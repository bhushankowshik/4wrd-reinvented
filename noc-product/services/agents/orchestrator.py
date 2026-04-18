"""Orchestrator — LangGraph-style DAG implemented with
concurrent futures for clarity under Docker Compose dev.

Flow (E5 §2.2 + E6a §3.5):
  1. Diagnosis ∥ Correlation fanned out in parallel.
  2. SOP runs after Diagnosis completes (primary hypothesis
     is input).
  3. Merge node composes an FR-C.1 conformant
     RecommendationPayload.
  4. Each agent_output row persists; one chain entry per
     agent_output + one for the recommendation.
"""
from __future__ import annotations

import json
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import text

from services.agents.correlation import CorrelationAgent
from services.agents.diagnosis import DiagnosisAgent
from services.agents.schemas import (
    CorrelationInput,
    CorrelationOutput,
    DiagnosisInput,
    DiagnosisOutput,
    RecommendationPayload,
    SOPInput,
    SOPOutput,
)
from services.agents.sop import SOPAgent
from services.chain_write.client import ChainWriteClient
from services.common.canonical import content_hash
from services.common.db import data_session
from services.common.settings import get_settings
from services.common.telemetry import (
    AGENT_TIMEOUTS,
    RECOMMENDATION_DURATION,
    log,
)
from services.model_backend import get_model_backend


TOTAL_BUDGET_SEC = 180.0
PER_AGENT_TIMEOUT_SEC = 60.0


def _persist_agent_output(
    *,
    incident_id: UUID,
    agent_kind: str,
    invocation_seq: int,
    started_at: datetime,
    completed_at: datetime,
    status: str,
    output_payload: dict,
    reasoning_trace: str | None,
    model_version: str,
    tokens_in: int | None,
    tokens_out: int | None,
    agent_output_chain_id: UUID,
    content_hash_bytes: bytes,
) -> UUID:
    agent_output_id = uuid.uuid4()
    with data_session() as s, s.begin():
        s.execute(
            text("""
                INSERT INTO agent_output (
                  agent_output_id, incident_id, agent_kind, invocation_seq,
                  started_at, completed_at, status, output_payload,
                  reasoning_trace, model_version, tokens_in, tokens_out,
                  agent_output_chain_id, content_hash
                )
                VALUES (
                  :agent_output_id, :incident_id, :agent_kind, :invocation_seq,
                  :started_at, :completed_at, :status,
                  CAST(:output_payload AS JSONB),
                  CAST(:reasoning_trace AS JSONB),
                  :model_version, :tokens_in, :tokens_out,
                  :agent_output_chain_id, :content_hash
                )
            """),
            {
                "agent_output_id": str(agent_output_id),
                "incident_id": str(incident_id),
                "agent_kind": agent_kind,
                "invocation_seq": invocation_seq,
                "started_at": started_at,
                "completed_at": completed_at,
                "status": status,
                "output_payload": json.dumps(output_payload, default=str),
                "reasoning_trace": (
                    json.dumps({"trace": reasoning_trace})
                    if reasoning_trace else None
                ),
                "model_version": model_version,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "agent_output_chain_id": str(agent_output_chain_id),
                "content_hash": content_hash_bytes,
            },
        )
    return agent_output_id


class Orchestrator:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._backend = get_model_backend()
        self._chain = ChainWriteClient()
        self._diagnosis = DiagnosisAgent(timeout_sec=PER_AGENT_TIMEOUT_SEC)
        self._correlation = CorrelationAgent()
        self._sop = SOPAgent()

    def run(self, incident_row: dict[str, Any]) -> RecommendationPayload:
        with RECOMMENDATION_DURATION.time():
            return self._run_inner(incident_row)

    def _run_inner(self, incident_row: dict[str, Any]) -> RecommendationPayload:
        incident_id = UUID(str(incident_row["incident_id"]))
        started = datetime.now(timezone.utc)

        per_agent_status: dict[str, str] = {}

        # --- Parallel: diagnosis + correlation ---

        diag_input = DiagnosisInput(
            incident_id=incident_id,
            symptom_text=incident_row["symptom_text"],
            severity=incident_row.get("severity") or "P3",
            affected_nodes=incident_row.get("affected_nodes") or [],
            customer_hint=incident_row.get("customer_hint"),
            correlation_hints=incident_row.get("correlation_hints"),
        )
        symptom_vec = incident_row.get("symptom_embedding") or []
        corr_input = CorrelationInput(
            incident_id=incident_id,
            symptom_embedding=symptom_vec,
            affected_nodes=incident_row.get("affected_nodes") or [],
            customer_hint=incident_row.get("customer_hint"),
        )

        with ThreadPoolExecutor(max_workers=2) as ex:
            fut_diag = ex.submit(self._diagnosis.run, diag_input)
            fut_corr = ex.submit(self._correlation.run, corr_input)

            try:
                diag_output: DiagnosisOutput = fut_diag.result(
                    timeout=PER_AGENT_TIMEOUT_SEC
                )
            except FuturesTimeout:
                AGENT_TIMEOUTS.labels(agent_kind="diagnosis").inc()
                fut_diag.cancel()
                diag_output = DiagnosisOutput(
                    incident_id=incident_id,
                    extracted_symptoms=[],
                    hypotheses=[],
                    primary_hypothesis="",
                    reasoning_trace="",
                    model=self._backend.reasoning_model(),
                    status="timeout",
                )

            try:
                corr_output: CorrelationOutput = fut_corr.result(
                    timeout=PER_AGENT_TIMEOUT_SEC
                )
            except FuturesTimeout:
                AGENT_TIMEOUTS.labels(agent_kind="correlation").inc()
                fut_corr.cancel()
                corr_output = CorrelationOutput(
                    incident_id=incident_id,
                    outcome="none",
                    related=[],
                    status="timeout",
                )

        per_agent_status["diagnosis"] = diag_output.status
        per_agent_status["correlation"] = corr_output.status

        self._persist_and_emit(
            incident_id=incident_id,
            agent_kind="diagnosis",
            invocation_seq=1,
            started_at=started,
            output=diag_output,
            actor_role="service_account",
            actor_id="agent-diagnosis",
        )
        self._persist_and_emit(
            incident_id=incident_id,
            agent_kind="correlation",
            invocation_seq=1,
            started_at=started,
            output=corr_output,
            actor_role="service_account",
            actor_id="agent-correlation",
        )

        # --- Sequential-on-diagnosis: SOP ---

        sop_started = datetime.now(timezone.utc)
        if diag_output.status in {"ok", "insufficient_data"} and diag_output.primary_hypothesis:
            sop_input = SOPInput(
                incident_id=incident_id,
                primary_hypothesis=diag_output.primary_hypothesis,
                symptom_text=incident_row["symptom_text"],
                severity=incident_row.get("severity") or "P3",
            )
            try:
                sop_output = self._sop.run(sop_input)
            except Exception as exc:  # noqa: BLE001
                log.warning("orchestrator.sop_error", error=str(exc))
                sop_output = SOPOutput(
                    incident_id=incident_id,
                    references=[],
                    summary="",
                    status="error",
                )
        else:
            sop_output = SOPOutput(
                incident_id=incident_id,
                references=[],
                summary="No diagnosis hypothesis — SOP retrieval skipped.",
                status="no_applicable_sop",
            )

        per_agent_status["sop"] = sop_output.status
        self._persist_and_emit(
            incident_id=incident_id,
            agent_kind="sop",
            invocation_seq=1,
            started_at=sop_started,
            output=sop_output,
            actor_role="service_account",
            actor_id="agent-sop",
        )

        # --- Merge + FR-C.1 recommendation ---

        produced_at = datetime.now(timezone.utc)
        decision_class: str
        summary: str
        proposed_actions: list[str]

        any_agent_errored = any(
            s in {"error", "timeout"} for s in per_agent_status.values()
        )

        if diag_output.status in {"error", "timeout"} and sop_output.status in {
            "error", "timeout"
        }:
            decision_class = "UNAVAILABLE"
            summary = "Recommendation unavailable: diagnosis and SOP retrieval failed."
            proposed_actions = []
        elif sop_output.status == "ok" and sop_output.references:
            remediation_present = any(
                (r.section_type or "").lower() == "remediation"
                for r in sop_output.references
            )
            decision_class = (
                "REMOTE_RESOLUTION" if remediation_present else "FIELD_DISPATCH"
            )
            summary = sop_output.summary or diag_output.primary_hypothesis
            proposed_actions = [
                f"Apply {r.sop_id}@{r.sop_version} — {r.section_path}"
                for r in sop_output.references[:3]
            ]
        else:
            decision_class = "FIELD_DISPATCH"
            summary = (
                diag_output.primary_hypothesis
                or "Unable to produce confident remote-resolution guidance."
            )
            proposed_actions = ["Dispatch field engineer for on-site inspection."]

        confidence = 0.0
        if diag_output.hypotheses:
            confidence = max(h.confidence for h in diag_output.hypotheses)
        if any_agent_errored:
            confidence = min(confidence, 0.4)

        correlation_summary: dict | None = (
            {
                "outcome": corr_output.outcome,
                "related_count": len(corr_output.related),
                "top_related": [
                    {
                        "incident_id": str(r.incident_id),
                        "score": r.score,
                        "ctts_ref": r.ctts_ref,
                        "overlap_kind": r.overlap_kind,
                    }
                    for r in corr_output.related[:3]
                ],
            }
            if corr_output.status != "error" else None
        )

        payload = RecommendationPayload(
            incident_id=incident_id,
            decision_class=decision_class,  # type: ignore[arg-type]
            summary=summary,
            proposed_actions=proposed_actions,
            diagnostic_summary=diag_output.primary_hypothesis
            or diag_output.reasoning_trace[:300],
            correlation_summary=correlation_summary,
            sop_references=sop_output.references,
            confidence=confidence,
            per_agent_status=per_agent_status,
            produced_at=produced_at.isoformat(),
            system_version=self._settings.system_version,
            sop_corpus_version=self._settings.sop_corpus_version,
            model_version=self._backend.reasoning_model(),
            requires_supervisor_review=any_agent_errored
            or confidence < 0.5
            or decision_class == "UNAVAILABLE",
        )

        # Persist recommendation + chain emit.
        recommendation_id = uuid.uuid4()
        payload_dict = payload.model_dump(mode="json")
        ch_bytes = content_hash(payload_dict)
        sop_versions_pinned = [
            {"sop_id": r.sop_id, "sop_version": r.sop_version,
             "chunk_ids": [str(r.chunk_id)]}
            for r in sop_output.references
        ]

        chain_resp = self._chain.emit(
            entry_type="recommendation",
            actor_id="agent-orchestrator",
            actor_role="service_account",
            payload_ref={
                "recommendation_id": str(recommendation_id),
                "production_seq": 1,
                "decision_class": decision_class,
                "content_hash_hex": ch_bytes.hex(),
                "per_agent_status": per_agent_status,
                "model_version": self._backend.reasoning_model(),
            },
            sop_versions_pinned=sop_versions_pinned or None,
            incident_id=incident_id,
        )
        recommendation_chain_id = UUID(chain_resp["chain_id"])

        production_state = (
            "unavailable" if decision_class == "UNAVAILABLE"
            else ("timed_out" if "timeout" in per_agent_status.values() else "produced")
        )

        with data_session() as s, s.begin():
            s.execute(
                text("""
                    INSERT INTO recommendation (
                      recommendation_id, incident_id, production_seq,
                      produced_at, decision_class, payload,
                      diagnostic_summary, correlation_summary,
                      sop_references, per_agent_status,
                      system_version, sop_corpus_version, model_version,
                      production_state, recommendation_chain_id, content_hash
                    )
                    VALUES (
                      :recommendation_id, :incident_id, 1,
                      :produced_at, :decision_class, CAST(:payload AS JSONB),
                      :diagnostic_summary, CAST(:correlation_summary AS JSONB),
                      CAST(:sop_references AS JSONB),
                      CAST(:per_agent_status AS JSONB),
                      :system_version, :sop_corpus_version, :model_version,
                      :production_state, :recommendation_chain_id, :content_hash
                    )
                """),
                {
                    "recommendation_id": str(recommendation_id),
                    "incident_id": str(incident_id),
                    "produced_at": produced_at,
                    "decision_class": decision_class,
                    "payload": json.dumps(payload_dict, default=str),
                    "diagnostic_summary": payload.diagnostic_summary,
                    "correlation_summary": (
                        json.dumps(correlation_summary)
                        if correlation_summary is not None else None
                    ),
                    "sop_references": json.dumps(
                        [r.model_dump(mode="json") for r in sop_output.references]
                    ),
                    "per_agent_status": json.dumps(per_agent_status),
                    "system_version": self._settings.system_version,
                    "sop_corpus_version": self._settings.sop_corpus_version,
                    "model_version": self._backend.reasoning_model(),
                    "production_state": production_state,
                    "recommendation_chain_id": str(recommendation_chain_id),
                    "content_hash": ch_bytes,
                },
            )

        log.info(
            "orchestrator.recommendation_produced",
            incident_id=str(incident_id),
            recommendation_id=str(recommendation_id),
            decision_class=decision_class,
            confidence=confidence,
            per_agent_status=per_agent_status,
        )
        return payload

    def _persist_and_emit(
        self,
        *,
        incident_id: UUID,
        agent_kind: str,
        invocation_seq: int,
        started_at: datetime,
        output: Any,
        actor_role: str,
        actor_id: str,
    ) -> None:
        completed_at = datetime.now(timezone.utc)
        payload = output.model_dump(mode="json")
        ch_bytes = content_hash(payload)
        chain = self._chain.emit(
            entry_type="agent_output",
            actor_id=actor_id,
            actor_role=actor_role,
            payload_ref={
                "incident_id": str(incident_id),
                "agent_kind": agent_kind,
                "status": output.status,
                "content_hash_hex": ch_bytes.hex(),
                "model_version": getattr(output, "model", None)
                or self._backend.reasoning_model(),
            },
            incident_id=incident_id,
        )
        _persist_agent_output(
            incident_id=incident_id,
            agent_kind=agent_kind,
            invocation_seq=invocation_seq,
            started_at=started_at,
            completed_at=completed_at,
            status=output.status,
            output_payload=payload,
            reasoning_trace=getattr(output, "reasoning_trace", None),
            model_version=getattr(output, "model", None)
            or self._backend.reasoning_model(),
            tokens_in=None,
            tokens_out=None,
            agent_output_chain_id=UUID(chain["chain_id"]),
            content_hash_bytes=ch_bytes,
        )
