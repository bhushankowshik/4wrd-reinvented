"""Diagnosis Agent — symptom extraction → hypothesis ranking
→ reasoning trace (E2 FR-B.1 / E5 §2.2).
"""
from __future__ import annotations

import json
import re

from pydantic import ValidationError

from services.agents.base import Agent
from services.agents.schemas import (
    DiagnosisHypothesis,
    DiagnosisInput,
    DiagnosisOutput,
)
from services.common.telemetry import AGENT_DURATION, AGENT_ERRORS, log
from services.model_backend import ChatMessage, get_model_backend


_SYSTEM_PROMPT = """You are a Telco NOC diagnosis assistant. Given an incident \
description, extract observable symptoms, produce 2-4 ranked hypotheses with a \
confidence score between 0 and 1, and identify the primary hypothesis.

Respond with STRICT JSON ONLY in this shape — no prose outside the JSON:
{
  "extracted_symptoms": ["..."],
  "hypotheses": [
    {"hypothesis": "...", "confidence": 0.0-1.0, "supporting_signals": ["..."]}
  ],
  "primary_hypothesis": "...",
  "reasoning_trace": "one short paragraph, <= 400 chars"
}
"""


def _extract_json(text: str) -> dict | None:
    """Tolerant JSON extraction — small models sometimes
    wrap output in prose or code fences."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Strip code fences.
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # First-brace to last-brace fallback.
    lb = text.find("{")
    rb = text.rfind("}")
    if lb >= 0 and rb > lb:
        try:
            return json.loads(text[lb:rb + 1])
        except json.JSONDecodeError:
            return None
    return None


class DiagnosisAgent(Agent[DiagnosisInput, DiagnosisOutput]):
    kind = "diagnosis"

    def __init__(self, timeout_sec: float = 60.0) -> None:
        self._backend = get_model_backend()
        self._timeout = timeout_sec

    def run(self, input: DiagnosisInput) -> DiagnosisOutput:  # noqa: A002
        with AGENT_DURATION.labels(agent_kind=self.kind).time():
            return self._run_inner(input)

    def _run_inner(self, inp: DiagnosisInput) -> DiagnosisOutput:
        user_prompt = {
            "symptom_text": inp.symptom_text,
            "severity": inp.severity,
            "affected_nodes": inp.affected_nodes,
            "customer_hint": inp.customer_hint,
            "correlation_hints": inp.correlation_hints,
        }
        try:
            resp = self._backend.chat(
                [
                    ChatMessage(role="system", content=_SYSTEM_PROMPT),
                    ChatMessage(role="user", content=json.dumps(user_prompt)),
                ],
                temperature=0.1,
                timeout_sec=self._timeout,
            )
        except Exception as exc:  # noqa: BLE001
            AGENT_ERRORS.labels(agent_kind=self.kind, reason="backend").inc()
            log.warning("diagnosis.backend_error", error=str(exc))
            return DiagnosisOutput(
                incident_id=inp.incident_id,
                extracted_symptoms=[],
                hypotheses=[],
                primary_hypothesis="",
                reasoning_trace=f"backend error: {exc}",
                model=self._backend.reasoning_model(),
                status="error",
            )

        data = _extract_json(resp.content)
        if not data:
            AGENT_ERRORS.labels(agent_kind=self.kind, reason="parse").inc()
            return DiagnosisOutput(
                incident_id=inp.incident_id,
                extracted_symptoms=[inp.symptom_text[:200]],
                hypotheses=[],
                primary_hypothesis="",
                reasoning_trace=(
                    "model response did not parse as JSON; returning degraded output"
                ),
                model=resp.model,
                status="insufficient_data",
            )

        try:
            hypotheses = [
                DiagnosisHypothesis(**h) for h in (data.get("hypotheses") or [])
            ]
        except ValidationError:
            hypotheses = []

        primary_raw = data.get("primary_hypothesis")
        if isinstance(primary_raw, dict):
            primary_raw = primary_raw.get("hypothesis") or ""
        primary = primary_raw or (hypotheses[0].hypothesis if hypotheses else "")
        primary = str(primary)

        return DiagnosisOutput(
            incident_id=inp.incident_id,
            extracted_symptoms=list(data.get("extracted_symptoms") or []),
            hypotheses=hypotheses,
            primary_hypothesis=primary,
            reasoning_trace=str(data.get("reasoning_trace") or "")[:4000],
            model=resp.model,
            status="ok" if (primary and hypotheses) else "insufficient_data",
        )
