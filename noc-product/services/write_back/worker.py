"""CTTS write-back worker — per E5 §2.5 + E6a §3.8.

Polls operator_decision where ctts_writeback_state='pending'
or 'retrying'; POSTs the decision to mock-ctts /writeback with
correlation_token for idempotency; updates the row accordingly
and emits ctts_writeback_outcome on every attempt.

At-least-once semantics. Retries: exponential backoff with
tenacity; marks state='failed' after max attempts for SRE
review. Leader election via filelock to allow multiple
replicas in compose.
"""
from __future__ import annotations

import signal
import sys
import time
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import httpx
from filelock import FileLock, Timeout
from sqlalchemy import text
from tenacity import (
    RetryError,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from services.chain_write.client import ChainWriteClient
from services.common.db import data_session
from services.common.settings import get_settings
from services.common.telemetry import (
    VALIDATION_FAILURES,
    configure_logging,
    log,
)
from prometheus_client import Counter, start_http_server


configure_logging()

WRITEBACK_ATTEMPTS = Counter(
    "noc_writeback_attempts_total",
    "CTTS write-back attempts",
    ["outcome"],
)

POLL_INTERVAL_SEC = 5.0
MAX_ATTEMPTS_BEFORE_FAIL = 5
LOCK_PATH = "/tmp/noc-writeback.lock"


_shutdown = False


def _graceful(_signum, _frame) -> None:
    global _shutdown
    _shutdown = True
    log.info("writeback.shutdown_requested")


def _due_decisions(limit: int = 10) -> list[dict[str, Any]]:
    with data_session() as s:
        rows = s.execute(
            text("""
                SELECT d.decision_id, d.decision_at, d.incident_id,
                       d.recommendation_id, d.decision_kind,
                       d.reason_code, d.override_action_class,
                       d.pseudonymous_operator_id, d.correlation_token,
                       d.ctts_writeback_state,
                       i.ctts_incident_ref
                  FROM operator_decision d
                  JOIN incident i
                    ON i.incident_id = d.incident_id
                 WHERE d.ctts_writeback_state IN ('pending','retrying')
                   AND d.decision_kind IN ('approved','overridden','rejected')
                 ORDER BY d.decision_at ASC
                 LIMIT :lim
                 FOR UPDATE SKIP LOCKED
            """),
            {"lim": limit},
        ).mappings().all()
        return [dict(r) for r in rows]


def _post_to_ctts(decision: dict) -> dict:
    s = get_settings()
    body = {
        "correlation_token": str(decision["correlation_token"]),
        "decision_kind": decision["decision_kind"],
        "reason_code": decision.get("reason_code"),
        "override_action_class": decision.get("override_action_class"),
        "pseudonymous_operator_id": decision["pseudonymous_operator_id"],
        "decision_at": decision["decision_at"].isoformat(),
    }
    resp = httpx.post(f"{s.mock_ctts_url}/writeback", json=body, timeout=10.0)
    resp.raise_for_status()
    return resp.json()


def _update_state(
    decision_id: UUID,
    decision_at: datetime,
    state: str,
    outcome_detail: dict | None,
) -> None:
    with data_session() as s, s.begin():
        s.execute(
            text("""
                UPDATE operator_decision
                   SET ctts_writeback_state = :state,
                       ctts_writeback_at    = :ts
                 WHERE decision_id = :did
                   AND decision_at = :dat
            """),
            {
                "state": state,
                "ts": datetime.now(timezone.utc),
                "did": str(decision_id),
                "dat": decision_at,
            },
        )


def _process_one(decision: dict, chain: ChainWriteClient) -> None:
    decision_id = decision["decision_id"]
    incident_id = decision["incident_id"]
    started = datetime.now(timezone.utc)
    try:
        for attempt in Retrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(min=0.5, max=4),
            retry=retry_if_exception_type(httpx.HTTPError),
            reraise=True,
        ):
            with attempt:
                result = _post_to_ctts(decision)
        status = result.get("status", "accepted")
        _update_state(decision_id, decision["decision_at"], "ok", result)
        WRITEBACK_ATTEMPTS.labels(outcome="ok").inc()
        chain.emit(
            entry_type="ctts_writeback_outcome",
            actor_id="write-back-worker",
            actor_role="service_account",
            payload_ref={
                "decision_id": str(decision_id),
                "correlation_token": str(decision["correlation_token"]),
                "ctts_status": status,
                "attempt_started_at": started.isoformat(),
                "duration_ms": int(
                    (datetime.now(timezone.utc) - started).total_seconds() * 1000
                ),
            },
            incident_id=UUID(str(incident_id)),
        )
        log.info(
            "writeback.ok",
            decision_id=str(decision_id),
            correlation_token=str(decision["correlation_token"]),
            ctts_status=status,
        )
    except RetryError as exc:
        log.warning("writeback.retry_exhausted", decision_id=str(decision_id), error=str(exc))
        _bump_failure(decision, chain, reason="retry_exhausted", exc=exc)
    except httpx.HTTPError as exc:
        log.warning("writeback.http_error", decision_id=str(decision_id), error=str(exc))
        _bump_failure(decision, chain, reason="http_error", exc=exc)


def _bump_failure(
    decision: dict, chain: ChainWriteClient, *, reason: str, exc: Exception
) -> None:
    # Attempt counter lives in a memory-only dict keyed by decision_id for the
    # dev stub — on restart we re-attempt; E8 hardens this into a db column.
    attempts = _attempt_map.get(str(decision["decision_id"]), 0) + 1
    _attempt_map[str(decision["decision_id"])] = attempts
    terminal = attempts >= MAX_ATTEMPTS_BEFORE_FAIL
    new_state = "failed" if terminal else "retrying"
    _update_state(
        decision["decision_id"], decision["decision_at"],
        new_state,
        {"attempts": attempts, "reason": reason, "error": str(exc)[:300]},
    )
    WRITEBACK_ATTEMPTS.labels(outcome=new_state).inc()
    chain.emit(
        entry_type="ctts_writeback_outcome",
        actor_id="write-back-worker",
        actor_role="service_account",
        payload_ref={
            "decision_id": str(decision["decision_id"]),
            "correlation_token": str(decision["correlation_token"]),
            "outcome": new_state,
            "attempts": attempts,
            "reason": reason,
        },
        incident_id=UUID(str(decision["incident_id"])),
    )
    if terminal:
        VALIDATION_FAILURES.labels(
            stage="writeback", rule_id="WB-001", severity="warn"
        ).inc()


_attempt_map: dict[str, int] = {}


def main() -> int:
    signal.signal(signal.SIGTERM, _graceful)
    signal.signal(signal.SIGINT, _graceful)
    start_http_server(9465)

    lock = FileLock(LOCK_PATH)
    try:
        lock.acquire(timeout=0)
    except Timeout:
        log.info("writeback.not_leader_exiting")
        return 0

    log.info("writeback.leader_acquired")
    chain = ChainWriteClient()

    try:
        while not _shutdown:
            due = _due_decisions()
            if not due:
                time.sleep(POLL_INTERVAL_SEC)
                continue
            log.info("writeback.tick", due=len(due))
            for d in due:
                if _shutdown:
                    break
                _process_one(d, chain)
    finally:
        lock.release()
        log.info("writeback.leader_released")
    return 0


if __name__ == "__main__":
    sys.exit(main())
