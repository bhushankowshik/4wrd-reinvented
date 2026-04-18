"""SOP Agent — RAG over sop_chunk using pgvector HNSW
filtered to active + deprecation_window chunks. Top-k → re-rank
by section_type weight → top-3. E5 §2.2, §3.5.
"""
from __future__ import annotations

import json
from uuid import UUID

from sqlalchemy import text

from services.agents.base import Agent
from services.agents.schemas import SOPChunkRef, SOPInput, SOPOutput
from services.common.db import data_session
from services.common.telemetry import AGENT_DURATION, AGENT_ERRORS, log
from services.model_backend import ChatMessage, get_model_backend


_SECTION_WEIGHT = {
    "remediation": 1.0,
    "precondition": 0.8,
    "escalation": 0.7,
    "reference": 0.5,
    "overview": 0.3,
    "other": 0.4,
    None: 0.4,
}


_SUMMARY_SYSTEM = """You are a Telco NOC SOP retrieval assistant. Given a \
diagnosis hypothesis and the top-3 retrieved SOP excerpts, produce a SHORT \
(<= 400 chars) summary of which SOP applies and the first concrete steps to \
take. Do not invent new steps — cite only content present in the excerpts. \
Respond in plain prose, no JSON, no markdown."""


class SOPAgent(Agent[SOPInput, SOPOutput]):
    kind = "sop"

    def __init__(self, top_k: int = 10, top_n: int = 3) -> None:
        self._top_k = top_k
        self._top_n = top_n
        self._backend = get_model_backend()

    def run(self, input: SOPInput) -> SOPOutput:  # noqa: A002
        with AGENT_DURATION.labels(agent_kind=self.kind).time():
            return self._run_inner(input)

    def _run_inner(self, inp: SOPInput) -> SOPOutput:
        query = f"{inp.primary_hypothesis}\n\n{inp.symptom_text}"
        try:
            embedding = self._backend.embed([query])[0]
        except Exception as exc:  # noqa: BLE001
            AGENT_ERRORS.labels(agent_kind=self.kind, reason="embed").inc()
            log.warning("sop.embed_error", error=str(exc))
            return SOPOutput(
                incident_id=inp.incident_id,
                references=[],
                summary="",
                status="error",
            )
        vec_lit = "[" + ",".join(f"{x:.6f}" for x in embedding) + "]"

        try:
            with data_session() as s:
                rows = s.execute(
                    text("""
                        SELECT chunk_id::text AS chunk_id,
                               sop_id, sop_version, section_path, section_type,
                               substr(text, 1, 600) AS excerpt,
                               1 - (embedding <=> CAST(:vec AS vector)) AS score
                        FROM sop_chunk
                        WHERE lifecycle_state IN ('active','deprecation_window')
                        ORDER BY embedding <=> CAST(:vec AS vector)
                        LIMIT :k
                    """),
                    {"vec": vec_lit, "k": self._top_k},
                ).mappings().all()
        except Exception as exc:  # noqa: BLE001
            AGENT_ERRORS.labels(agent_kind=self.kind, reason="db").inc()
            log.warning("sop.db_error", error=str(exc))
            return SOPOutput(
                incident_id=inp.incident_id,
                references=[],
                summary="",
                status="error",
            )

        if not rows:
            return SOPOutput(
                incident_id=inp.incident_id,
                references=[],
                summary="No applicable SOP found.",
                status="no_applicable_sop",
            )

        scored = [
            (
                float(r["score"] or 0.0) * _SECTION_WEIGHT.get(r["section_type"], 0.4),
                r,
            )
            for r in rows
        ]
        scored.sort(key=lambda t: t[0], reverse=True)
        top = scored[: self._top_n]

        refs = [
            SOPChunkRef(
                sop_id=r["sop_id"],
                sop_version=r["sop_version"],
                chunk_id=UUID(r["chunk_id"]),
                section_path=r["section_path"],
                section_type=r["section_type"],
                score=float(adj_score),
                excerpt=r["excerpt"],
            )
            for adj_score, r in top
        ]

        excerpts_block = "\n\n".join(
            f"[{i + 1}] {r.section_path}\n{r.excerpt}"
            for i, r in enumerate(refs)
        )
        try:
            summary_resp = self._backend.chat(
                [
                    ChatMessage(role="system", content=_SUMMARY_SYSTEM),
                    ChatMessage(
                        role="user",
                        content=(
                            f"Hypothesis: {inp.primary_hypothesis}\n"
                            f"Severity: {inp.severity}\n\n"
                            f"Retrieved excerpts:\n{excerpts_block}"
                        ),
                    ),
                ],
                temperature=0.1,
            )
            summary = summary_resp.content.strip()[:600]
        except Exception as exc:  # noqa: BLE001
            AGENT_ERRORS.labels(agent_kind=self.kind, reason="summary").inc()
            log.warning("sop.summary_error", error=str(exc))
            summary = f"Top SOP: {refs[0].sop_id}@{refs[0].sop_version} ({refs[0].section_path})"

        return SOPOutput(
            incident_id=inp.incident_id,
            references=refs,
            summary=summary,
            status="ok",
        )
