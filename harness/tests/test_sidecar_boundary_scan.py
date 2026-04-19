"""Sidecar boundary-scan test.

`run_session_boundary_scan` should:
  - return a BoundaryScanResult wrapping the SessionContext
  - flag likely_drift=True when new_direction shares no topic with prior
    chain entries
  - flag likely_drift=False when there is topic overlap

`inspect_adversarial_output` should:
  - route a CRITICAL FRAME_CHANGE to `emit_frame_change`
  - ignore non-CRITICAL or non-FRAME_CHANGE challenges
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from harness.agents.adversarial_agent import AdversarialOutput, Challenge
from harness.sidecar_integration import (
    inspect_adversarial_output,
    run_session_boundary_scan,
)
from mvghb.sidecar import SessionContext


def _ctx(topics, n=5):
    return SessionContext(
        last_n_entries=n,
        actor_breakdown={"human": n},
        last_entry_types=["direction_capture"] * n,
        last_timestamp=datetime.now(timezone.utc),
        payload_topics=topics,
    )


def test_boundary_scan_no_prior_entries(monkeypatch):
    from harness import sidecar_integration as sc
    monkeypatch.setattr(
        sc, "detect_session_boundary",
        lambda window=25: _ctx(topics=[], n=0),
    )
    result = run_session_boundary_scan(new_direction="Crystallise something new.")
    assert result.prior_entry_count == 0
    assert result.likely_drift is False


def test_boundary_scan_detects_drift(monkeypatch):
    from harness import sidecar_integration as sc
    monkeypatch.setattr(
        sc, "detect_session_boundary",
        lambda window=25: _ctx(topics=["billing migration", "mas trm"]),
    )
    result = run_session_boundary_scan(
        new_direction="Refactor the logging subsystem completely.",
    )
    assert result.likely_drift is True
    assert "billing migration" in (result.drift_reason or "")


def test_boundary_scan_no_drift_on_topic_overlap(monkeypatch):
    from harness import sidecar_integration as sc
    monkeypatch.setattr(
        sc, "detect_session_boundary",
        lambda window=25: _ctx(topics=["billing migration", "mas trm"]),
    )
    result = run_session_boundary_scan(
        new_direction="Continue on the billing migration scope.",
    )
    assert result.likely_drift is False
    assert result.drift_reason is None


def test_inspect_adversarial_output_no_frame_change():
    adv = AdversarialOutput(
        challenges=[Challenge(
            axis="OUTPUT", severity="CRITICAL",
            challenge="missing scope", evidence="line 2",
        )],
        frame_change_detected=False, raw="{}",
    )
    decision = inspect_adversarial_output(adv)
    assert decision.frame_change is False
    assert decision.chain_id is None


def test_inspect_adversarial_output_emits_frame_change(monkeypatch):
    captured: dict = {}

    def fake_emit(*, receptor, signal, incident_id=None,
                  context=None, writer=None):
        captured["receptor"] = receptor
        captured["signal"] = signal
        return uuid4()

    from harness import sidecar_integration as sc
    monkeypatch.setattr(sc, "emit_frame_change", fake_emit)

    adv = AdversarialOutput(
        challenges=[
            Challenge(axis="FRAME_CHANGE", severity="CRITICAL",
                      challenge="PDI drift detected",
                      evidence="direction cites S4 but refs S1 scope"),
            Challenge(axis="OUTPUT", severity="MAJOR",
                      challenge="unrelated", evidence="x"),
        ],
        frame_change_detected=True, raw="{}",
    )
    decision = inspect_adversarial_output(adv)
    assert decision.frame_change is True
    assert decision.chain_id is not None
    assert captured["receptor"] == "adversarial_ai"
    assert "PDI drift detected" in captured["signal"]
