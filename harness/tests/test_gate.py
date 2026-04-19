"""Gate discipline tests — chain-enforced predecessor close-at-Exact."""
from __future__ import annotations

from datetime import datetime, timezone

from harness.orchestrator.gate import gate_is_open
from harness.orchestrator.skill_sequence import SOLUTIONING_SEQUENCE


def test_gate_blocked_when_predecessor_has_no_close():
    """S2 must be blocked when S1 has no cycle_close at Exact."""
    result = gate_is_open(
        skill_id="S2",
        sequence=SOLUTIONING_SEQUENCE,
        fetcher=lambda skill_id: None,
    )
    assert result.open is False
    assert result.blocking_skill_id == "S1"
    assert "blocked" in result.reason.lower()


def test_gate_open_when_predecessor_closed_at_exact():
    fetched = {
        "chain_id": "abc",
        "timestamp": datetime(2026, 4, 1, tzinfo=timezone.utc),
        "payload_ref": {
            "cycle_id": "c-1",
            "skill_id": "S1",
            "convergence_state_at_exit": "Exact",
        },
    }
    result = gate_is_open(
        skill_id="S2",
        sequence=SOLUTIONING_SEQUENCE,
        fetcher=lambda skill_id: fetched if skill_id == "S1" else None,
    )
    assert result.open is True
    assert result.blocking_skill_id is None
    assert "closed at Exact" in result.reason


def test_gate_first_skill_is_always_open():
    """S1 has no predecessor — gate is open."""
    result = gate_is_open(
        skill_id="S1",
        sequence=SOLUTIONING_SEQUENCE,
        fetcher=lambda skill_id: None,
    )
    assert result.open is True
    assert result.blocking_skill_id is None
