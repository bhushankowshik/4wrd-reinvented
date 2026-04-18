"""Intake worker — polls Mock CTTS every 15s, validates,
writes to incident + chain. Leader election via file lock.
E6a §3.9 + E5 §2.1.
"""
from __future__ import annotations

import json
import signal
import time
import uuid
from datetime import datetime, timedelta, timezone
from uuid import UUID

import httpx
from filelock import FileLock, Timeout
from pydantic import ValidationError
from sqlalchemy import text

from services.chain_write.client import ChainWriteClient
from services.common.canonical import content_hash
from services.common.db import data_session
from services.common.settings import get_settings
from services.common.telemetry import (
    INTAKE_INGESTED,
    VALIDATION_FAILURES,
    configure_logging,
    log,
)
from services.intake.schemas import IncidentIn
from services.model_backend import get_model_backend
from services.secret_scanner.scan import scan as secret_scan


LEADER_LOCK_PATH = "/tmp/noc-intake.lock"


configure_logging()


def _emit_validation_failure(
    *,
    stage: str,
    rule_id: str,
    subject_ref: str | None,
    severity: str,
    details: dict,
    chain: ChainWriteClient,
) -> None:
    VALIDATION_FAILURES.labels(stage=stage, rule_id=rule_id, severity=severity).inc()
    failure_id = uuid.uuid4()
    ch_resp = chain.emit(
        entry_type="validation_failure",
        actor_id="intake",
        actor_role="service_account",
        payload_ref={
            "failure_id": str(failure_id),
            "stage": stage,
            "rule_id": rule_id,
            "severity": severity,
            "subject_ref": subject_ref,
        },
    )
    try:
        with data_session() as s, s.begin():
            s.execute(
                text("""
                    INSERT INTO validation_failure (
                      failure_id, stage, subject_ref, rule_id,
                      rule_severity, details, failure_chain_id
                    ) VALUES (
                      :failure_id, :stage, :subject_ref, :rule_id,
                      :severity, CAST(:details AS JSONB), :chain_id
                    )
                """),
                {
                    "failure_id": str(failure_id),
                    "stage": stage,
                    "subject_ref": subject_ref,
                    "rule_id": rule_id,
                    "severity": severity,
                    "details": json.dumps(details, default=str),
                    "chain_id": ch_resp["chain_id"],
                },
            )
    except Exception as exc:  # noqa: BLE001
        log.warning("intake.validation_failure_write_error",
                    rule_id=rule_id, error=str(exc))


def _validate_required(raw: dict) -> tuple[bool, str | None]:
    """Apply INT-001..INT-006 at the raw-dict level."""
    required = ["ctts_incident_ref", "ctts_received_at", "affected_nodes",
                "symptom_text", "severity"]
    for k in required:
        if k not in raw or raw[k] in (None, "", []):
            return False, f"INT-002:{k}"
    sev = raw.get("severity")
    if sev not in {"P1", "P2", "P3", "P4", "P5"}:
        return False, "INT-003"
    if not isinstance(raw.get("affected_nodes"), list) or not raw["affected_nodes"]:
        return False, "INT-005"
    stxt = raw.get("symptom_text") or ""
    if not (1 <= len(stxt) <= 8192):
        return False, "INT-006"
    return True, None


def _process_one(raw: dict, chain: ChainWriteClient) -> None:
    ref = raw.get("ctts_incident_ref") or ""
    ok, rule = _validate_required(raw)
    if not ok:
        _emit_validation_failure(
            stage="intake",
            rule_id=rule or "INT-000",
            subject_ref=ref,
            severity="reject",
            details=raw,
            chain=chain,
        )
        # Also emit ticket_rejected_malformed chain entry.
        chain.emit(
            entry_type="ticket_rejected_malformed",
            actor_id="intake",
            actor_role="service_account",
            payload_ref={"ctts_incident_ref": ref, "rule_id": rule or "INT-000"},
        )
        return

    try:
        inc = IncidentIn(**raw)
    except ValidationError as exc:
        _emit_validation_failure(
            stage="intake", rule_id="INT-000",
            subject_ref=ref, severity="reject",
            details={"raw": raw, "errors": exc.errors()},
            chain=chain,
        )
        chain.emit(
            entry_type="ticket_rejected_malformed",
            actor_id="intake",
            actor_role="service_account",
            payload_ref={"ctts_incident_ref": ref, "rule_id": "INT-000"},
        )
        return

    # INT-008 — secret scan on symptom_text.
    scan_result = secret_scan(inc.symptom_text)
    if scan_result.max_severity == "high":
        _emit_validation_failure(
            stage="intake", rule_id="INT-008",
            subject_ref=ref, severity="quarantine",
            details={"matches": scan_result.matches},
            chain=chain,
        )
        return

    # Embed symptom.
    backend = get_model_backend()
    try:
        emb = backend.embed([inc.symptom_text])[0]
    except Exception as exc:  # noqa: BLE001
        log.warning("intake.embed_error", ref=ref, error=str(exc))
        emb = []

    incident_id = uuid.uuid4()
    ingest_at = datetime.now(timezone.utc)
    s = get_settings()

    payload_ref = {
        "incident_id": str(incident_id),
        "ctts_incident_ref": ref,
        "system_version": s.system_version,
        "sop_corpus_version": s.sop_corpus_version,
    }
    ch_bytes = content_hash(payload_ref)

    ch_resp = chain.emit(
        entry_type="intake",
        actor_id="intake",
        actor_role="service_account",
        payload_ref={**payload_ref, "content_hash_hex": ch_bytes.hex()},
        incident_id=incident_id,
    )
    intake_chain_id = UUID(ch_resp["chain_id"])
    vec_lit = "[" + ",".join(f"{x:.6f}" for x in emb) + "]" if emb else None

    try:
        with data_session() as sess, sess.begin():
            sess.execute(
                text("""
                    INSERT INTO incident (
                      incident_id, ctts_incident_ref, ctts_received_at,
                      ingest_at, reporting_source, affected_nodes,
                      symptom_text, symptom_embedding, severity,
                      customer_hint, correlation_hints, system_version,
                      sop_corpus_version, intake_chain_id, content_hash,
                      intake_state, raw_payload_ref
                    )
                    VALUES (
                      :incident_id, :ref, :ctts_received_at,
                      :ingest_at, :reporting_source,
                      CAST(:affected_nodes AS JSONB),
                      :symptom_text,
                      CAST(:emb AS vector),
                      :severity, :customer_hint,
                      CAST(:correlation_hints AS JSONB),
                      :system_version, :sop_corpus_version,
                      :intake_chain_id, :content_hash,
                      'accepted', :raw_payload_ref
                    )
                    ON CONFLICT DO NOTHING
                """),
                {
                    "incident_id": str(incident_id),
                    "ref": ref,
                    "ctts_received_at": inc.ctts_received_at,
                    "ingest_at": ingest_at,
                    "reporting_source": inc.reporting_source,
                    "affected_nodes": json.dumps(inc.affected_nodes),
                    "symptom_text": inc.symptom_text,
                    "emb": vec_lit,
                    "severity": inc.severity,
                    "customer_hint": inc.customer_hint,
                    "correlation_hints": json.dumps(inc.correlation_hints) if inc.correlation_hints else None,
                    "system_version": s.system_version,
                    "sop_corpus_version": s.sop_corpus_version,
                    "intake_chain_id": str(intake_chain_id),
                    "content_hash": ch_bytes,
                    "raw_payload_ref": None,
                },
            )
    except Exception as exc:  # noqa: BLE001
        log.error("intake.insert_error", ref=ref, error=str(exc))
        return

    INTAKE_INGESTED.labels(reporting_source=inc.reporting_source or "unknown").inc()

    # Advance CTTS state marker + enqueue orchestrator run.
    try:
        httpx.post(f"{s.mock_ctts_url}/incidents/{ref}/advance", timeout=5).raise_for_status()
    except Exception as exc:  # noqa: BLE001
        log.warning("intake.advance_state_error", ref=ref, error=str(exc))

    # Orchestrator enqueue — synchronous in dev.
    try:
        httpx.post(
            "http://agents:7002/runs",
            json={"incident_id": str(incident_id)},
            timeout=240,
        ).raise_for_status()
    except Exception as exc:  # noqa: BLE001
        log.warning("intake.orchestrator_error", ref=ref, error=str(exc))


def _recovery_sweep(chain: ChainWriteClient) -> None:
    """OF-6.16 — pick up any accepted incident that lacks a
    recommendation (prior orchestrator run lost). Best-effort."""
    try:
        with data_session() as sess:
            rows = sess.execute(
                text("""
                    SELECT i.incident_id::text AS incident_id
                    FROM incident i
                    LEFT JOIN recommendation r
                      ON r.incident_id = i.incident_id
                    WHERE i.intake_state = 'accepted'
                      AND r.recommendation_id IS NULL
                      AND i.ingest_at > now() - interval '24 hours'
                    LIMIT 50
                """)
            ).mappings().all()
    except Exception as exc:  # noqa: BLE001
        log.warning("intake.recovery_sweep_error", error=str(exc))
        return

    for r in rows:
        try:
            httpx.post(
                "http://agents:7002/runs",
                json={"incident_id": r["incident_id"]},
                timeout=240,
            ).raise_for_status()
            log.info("intake.recovery_sweep_enqueued", incident_id=r["incident_id"])
        except Exception as exc:  # noqa: BLE001
            log.warning(
                "intake.recovery_sweep_enqueue_error",
                incident_id=r["incident_id"],
                error=str(exc),
            )


def _poll_cycle(chain: ChainWriteClient) -> None:
    s = get_settings()
    try:
        r = httpx.get(f"{s.mock_ctts_url}/incidents/unresolved", timeout=10)
        r.raise_for_status()
        items = r.json()
    except Exception as exc:  # noqa: BLE001
        log.warning("intake.poll_error", error=str(exc))
        return
    for raw in items:
        _process_one(raw, chain)


def main() -> None:
    from prometheus_client import start_http_server

    s = get_settings()
    chain = ChainWriteClient()
    stop = {"flag": False}

    # Expose worker metrics for Prometheus scrape.
    start_http_server(9464)

    def _sig(_signum, _frame):  # noqa: ANN001
        stop["flag"] = True

    signal.signal(signal.SIGTERM, _sig)
    signal.signal(signal.SIGINT, _sig)

    try:
        with FileLock(LEADER_LOCK_PATH, timeout=1):
            log.info("intake.leader_acquired")
            _recovery_sweep(chain)
            while not stop["flag"]:
                _poll_cycle(chain)
                for _ in range(max(1, s.ctts_poll_interval_sec)):
                    if stop["flag"]:
                        break
                    time.sleep(1)
    except Timeout:
        log.info("intake.leader_not_available — sleeping")
        while not stop["flag"]:
            time.sleep(5)


if __name__ == "__main__":
    main()
