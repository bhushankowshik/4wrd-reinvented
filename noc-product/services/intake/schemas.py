"""Intake pydantic schemas. E5 §5.1 INT-rules enforce shape."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class IncidentIn(BaseModel):
    ctts_incident_ref: str = Field(min_length=1)
    ctts_received_at: datetime
    affected_nodes: list[dict]
    symptom_text: str = Field(min_length=1, max_length=8192)
    severity: Literal["P1", "P2", "P3", "P4", "P5"]
    customer_hint: str | None = None
    reporting_source: str | None = None
    correlation_hints: dict | None = None

    @field_validator("affected_nodes")
    @classmethod
    def _non_empty(cls, v: list[dict]) -> list[dict]:
        if not v:
            raise ValueError("affected_nodes must be non-empty")
        return v
