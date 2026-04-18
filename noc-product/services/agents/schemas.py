"""Pydantic schemas for agent I/O — per E5 §5.2 AGO-001
(output_payload conforms to per-agent schema).
"""
from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


# ---------- Diagnosis ----------

class DiagnosisInput(BaseModel):
    incident_id: UUID
    symptom_text: str
    severity: Literal["P1", "P2", "P3", "P4", "P5"]
    affected_nodes: list[dict]
    customer_hint: str | None = None
    correlation_hints: dict | None = None


class DiagnosisHypothesis(BaseModel):
    hypothesis: str
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_signals: list[str] = Field(default_factory=list)


class DiagnosisOutput(BaseModel):
    incident_id: UUID
    extracted_symptoms: list[str]
    hypotheses: list[DiagnosisHypothesis]
    primary_hypothesis: str
    reasoning_trace: str
    model: str
    status: Literal["ok", "insufficient_data", "timeout", "error"] = "ok"


# ---------- Correlation ----------

class CorrelationInput(BaseModel):
    incident_id: UUID
    symptom_embedding: list[float]
    affected_nodes: list[dict]
    customer_hint: str | None = None
    time_window_hours: int = 24


class CorrelatedIncident(BaseModel):
    incident_id: UUID
    score: float
    ctts_ref: str
    severity: str
    overlap_kind: Literal["symptom", "node", "customer", "cluster"]


class CorrelationOutput(BaseModel):
    incident_id: UUID
    outcome: Literal["none", "related_found", "cluster_member"]
    related: list[CorrelatedIncident]
    status: Literal["ok", "none_found", "timeout", "error"] = "ok"


# ---------- SOP ----------

class SOPInput(BaseModel):
    incident_id: UUID
    primary_hypothesis: str
    symptom_text: str
    severity: str


class SOPChunkRef(BaseModel):
    sop_id: str
    sop_version: str
    chunk_id: UUID
    section_path: str
    section_type: str | None
    score: float
    excerpt: str


class SOPOutput(BaseModel):
    incident_id: UUID
    references: list[SOPChunkRef]
    summary: str
    status: Literal["ok", "no_applicable_sop", "timeout", "error"] = "ok"


# ---------- Recommendation (FR-C.1) ----------

class RecommendationPayload(BaseModel):
    """FR-C.1 conformant payload body — nested under
    recommendation.payload JSONB column."""
    incident_id: UUID
    decision_class: Literal["REMOTE_RESOLUTION", "FIELD_DISPATCH", "UNAVAILABLE"]
    summary: str
    proposed_actions: list[str]
    diagnostic_summary: str
    correlation_summary: dict | None
    sop_references: list[SOPChunkRef]
    confidence: float = Field(ge=0.0, le=1.0)
    per_agent_status: dict[str, str]
    produced_at: str
    system_version: str
    sop_corpus_version: str
    model_version: str
    requires_supervisor_review: bool = False
