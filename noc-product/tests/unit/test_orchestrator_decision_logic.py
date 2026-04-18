"""M10 — orchestrator decision-class selection logic (REC-rules).

Exercises the pure merge logic that maps per-agent outputs
to a RecommendationPayload.decision_class. The persistence
and chain-emit paths are covered separately under tests/chain.
"""
from __future__ import annotations

from uuid import uuid4

from services.agents.schemas import (
    CorrelationOutput,
    DiagnosisHypothesis,
    DiagnosisOutput,
    SOPChunkRef,
    SOPOutput,
)


def _diag_ok(primary: str = "intermittent optical transceiver fault") -> DiagnosisOutput:
    return DiagnosisOutput(
        incident_id=uuid4(),
        extracted_symptoms=["packet loss", "eth0"],
        hypotheses=[DiagnosisHypothesis(hypothesis=primary, confidence=0.72)],
        primary_hypothesis=primary,
        reasoning_trace="dev trace",
        model="llama3.2:3b",
        status="ok",
    )


def _sop_with_remediation() -> SOPOutput:
    return SOPOutput(
        incident_id=uuid4(),
        references=[
            SOPChunkRef(
                sop_id="PROC-RR-001", sop_version="v1", chunk_id=uuid4(),
                section_path="Remediation Actions", section_type="remediation",
                score=0.81, excerpt="Issue an interface shut / no shut sequence...",
            )
        ],
        summary="Apply interface soft reset remediation",
        status="ok",
    )


def _sop_reference_only() -> SOPOutput:
    return SOPOutput(
        incident_id=uuid4(),
        references=[
            SOPChunkRef(
                sop_id="PROC-FD-001", sop_version="v1", chunk_id=uuid4(),
                section_path="References", section_type="reference",
                score=0.65, excerpt="See field-dispatch procedures",
            )
        ],
        summary="Field-dispatch applicable",
        status="ok",
    )


def _corr_none() -> CorrelationOutput:
    return CorrelationOutput(
        incident_id=uuid4(), outcome="none", related=[], status="none_found",
    )


def _derive_decision(diag: DiagnosisOutput, sop: SOPOutput, corr: CorrelationOutput) -> str:
    """Replicates the pure decision-class logic from Orchestrator._run_inner
    so we can unit-test it without live DB/chain."""
    if diag.status in {"error", "timeout"} and sop.status in {"error", "timeout"}:
        return "UNAVAILABLE"
    if sop.status == "ok" and sop.references:
        remediation_present = any(
            (r.section_type or "").lower() == "remediation"
            for r in sop.references
        )
        return "REMOTE_RESOLUTION" if remediation_present else "FIELD_DISPATCH"
    return "FIELD_DISPATCH"


def test_remote_resolution_when_sop_has_remediation():
    assert _derive_decision(
        _diag_ok(), _sop_with_remediation(), _corr_none()
    ) == "REMOTE_RESOLUTION"


def test_field_dispatch_when_sop_has_no_remediation_section():
    assert _derive_decision(
        _diag_ok(), _sop_reference_only(), _corr_none()
    ) == "FIELD_DISPATCH"


def test_unavailable_when_both_diagnosis_and_sop_fail():
    d = DiagnosisOutput(
        incident_id=uuid4(), extracted_symptoms=[], hypotheses=[],
        primary_hypothesis="", reasoning_trace="", model="llama3.2:3b",
        status="timeout",
    )
    s = SOPOutput(incident_id=uuid4(), references=[], summary="", status="error")
    assert _derive_decision(d, s, _corr_none()) == "UNAVAILABLE"


def test_field_dispatch_default_when_no_sop_retrieved():
    s = SOPOutput(
        incident_id=uuid4(), references=[], summary="", status="no_applicable_sop"
    )
    assert _derive_decision(_diag_ok(), s, _corr_none()) == "FIELD_DISPATCH"
