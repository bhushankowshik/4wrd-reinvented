"""M10 — intake INT-001..INT-008 quality gate tests."""
from __future__ import annotations

from datetime import datetime, timezone

from services.intake.schemas import IncidentIn
from services.intake.worker import _validate_required


def _base() -> dict:
    return {
        "ctts_incident_ref": "CTTS-TEST-0001",
        "ctts_received_at": datetime.now(timezone.utc).isoformat(),
        "affected_nodes": [{"node_id": "BTS-447", "site": "SG-NORTH"}],
        "symptom_text": "Node packet loss on eth0",
        "severity": "P2",
        "reporting_source": "network-monitoring",
    }


def test_int_positive_valid_incident():
    ok, rule = _validate_required(_base())
    assert ok and rule is None


def test_int_002_missing_required_field():
    raw = _base()
    del raw["symptom_text"]
    ok, rule = _validate_required(raw)
    assert not ok and rule.startswith("INT-002")


def test_int_003_bad_severity():
    raw = _base()
    raw["severity"] = "P9"
    ok, rule = _validate_required(raw)
    assert not ok and rule == "INT-003"


def test_int_005_empty_affected_nodes():
    raw = _base()
    raw["affected_nodes"] = []
    ok, rule = _validate_required(raw)
    assert not ok and rule in {"INT-002:affected_nodes", "INT-005"}


def test_int_006_symptom_text_too_long():
    raw = _base()
    raw["symptom_text"] = "x" * 8193
    ok, rule = _validate_required(raw)
    assert not ok and rule == "INT-006"


def test_int_006_symptom_text_empty():
    raw = _base()
    raw["symptom_text"] = ""
    ok, rule = _validate_required(raw)
    assert not ok


def test_pydantic_schema_accepts_valid_payload():
    inc = IncidentIn(**_base())
    assert inc.severity == "P2"
    assert inc.ctts_incident_ref == "CTTS-TEST-0001"


def test_pydantic_schema_rejects_empty_affected_nodes():
    import pytest
    from pydantic import ValidationError

    raw = _base()
    raw["affected_nodes"] = []
    with pytest.raises(ValidationError):
        IncidentIn(**raw)
