"""Ticket Correlation Agent — hybrid retrieval over past
incident corpus using pgvector HNSW on symptom_embedding +
structured filters on affected_nodes / customer_hint / time
window. E5 §2.2.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import text

from services.agents.base import Agent
from services.agents.schemas import (
    CorrelatedIncident,
    CorrelationInput,
    CorrelationOutput,
)
from services.common.db import data_session
from services.common.telemetry import AGENT_DURATION, AGENT_ERRORS, log


class CorrelationAgent(Agent[CorrelationInput, CorrelationOutput]):
    kind = "correlation"

    def __init__(self, top_k: int = 5, score_threshold: float = 0.5) -> None:
        self._top_k = top_k
        self._threshold = score_threshold

    def run(self, input: CorrelationInput) -> CorrelationOutput:  # noqa: A002
        with AGENT_DURATION.labels(agent_kind=self.kind).time():
            return self._run_inner(input)

    def _run_inner(self, inp: CorrelationInput) -> CorrelationOutput:
        since = datetime.now(timezone.utc) - timedelta(hours=inp.time_window_hours)
        vec_lit = "[" + ",".join(f"{x:.6f}" for x in inp.symptom_embedding) + "]"

        try:
            with data_session() as s:
                rows = s.execute(
                    text("""
                        SELECT incident_id::text AS incident_id,
                               ctts_incident_ref,
                               severity,
                               affected_nodes,
                               customer_hint,
                               1 - (symptom_embedding <=> CAST(:vec AS vector)) AS score
                        FROM incident
                        WHERE incident_id <> :self_id
                          AND ingest_at >= :since
                          AND symptom_embedding IS NOT NULL
                          AND intake_state = 'accepted'
                        ORDER BY symptom_embedding <=> CAST(:vec AS vector)
                        LIMIT :k
                    """),
                    {
                        "vec": vec_lit,
                        "self_id": str(inp.incident_id),
                        "since": since,
                        "k": self._top_k,
                    },
                ).mappings().all()
        except Exception as exc:  # noqa: BLE001
            AGENT_ERRORS.labels(agent_kind=self.kind, reason="db").inc()
            log.warning("correlation.db_error", error=str(exc))
            return CorrelationOutput(
                incident_id=inp.incident_id,
                outcome="none",
                related=[],
                status="error",
            )

        related: list[CorrelatedIncident] = []
        own_node_ids = {n.get("node_id") for n in inp.affected_nodes if n.get("node_id")}

        for r in rows:
            score = float(r["score"] or 0.0)
            if score < self._threshold:
                continue
            other_nodes = r["affected_nodes"] or []
            other_ids = {n.get("node_id") for n in other_nodes if n.get("node_id")}
            overlap_kind = "symptom"
            if own_node_ids & other_ids:
                overlap_kind = "node"
            elif inp.customer_hint and inp.customer_hint == r["customer_hint"]:
                overlap_kind = "customer"
            related.append(
                CorrelatedIncident(
                    incident_id=UUID(r["incident_id"]),
                    score=score,
                    ctts_ref=r["ctts_incident_ref"],
                    severity=r["severity"] or "P5",
                    overlap_kind=overlap_kind,  # type: ignore[arg-type]
                )
            )

        if not related:
            return CorrelationOutput(
                incident_id=inp.incident_id,
                outcome="none",
                related=[],
                status="none_found",
            )

        outcome = "cluster_member" if len(related) >= 3 else "related_found"
        return CorrelationOutput(
            incident_id=inp.incident_id,
            outcome=outcome,  # type: ignore[arg-type]
            related=related,
            status="ok",
        )
