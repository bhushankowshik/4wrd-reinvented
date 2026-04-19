"""Chain entry sequence test.

The orchestrator writes chain entries in a specific order:

  direction_capture → production → adversarial_challenge
  → verification → cycle_close

With a loop on PARTIAL verification, the middle block repeats.
We pin the per-actor routing too — each moment goes to the right
actor_id.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from harness.agents.adversarial_agent import AdversarialOutput, Challenge
from harness.agents.producing_agent import ProducingOutput
from harness.intent_cycle import IntentCycle, Moment1Input, VerifierResponse
from harness.skills import SKILLS


class _StubProducing:
    def __init__(self, n: int) -> None:
        self._n = n

    def produce(self, package):  # noqa: ANN001
        return ProducingOutput(
            output=f"output-{self._n}",
            reasoning_trace=f"reasoning-{self._n}",
            raw=f"raw-{self._n}",
            model="claude-sonnet-4-6",
        )


class _StubAdversarial:
    def challenge(self, package):  # noqa: ANN001
        return AdversarialOutput(
            challenges=[Challenge(
                axis="OUTPUT", severity="MINOR",
                challenge="fine", evidence="none",
            )],
            frame_change_detected=False,
            raw="{}",
            model="claude-opus-4-6",
        )


class _StubEmit:
    def __init__(self) -> None:
        self.chain_id = uuid4()
        self.timestamp = datetime.now(timezone.utc)


class _RecordingWriter:
    def __init__(self) -> None:
        self.log: list[tuple[str, str]] = []

    def emit(
        self, entry_type, actor_id, actor_role, incident_id,
        payload_ref, sop_versions_pinned=None,
        class_enum="NORMAL", prev_chain_id=None,
    ):
        self.log.append((entry_type, actor_id))
        return _StubEmit()


def _wire_cycle(writer, artefact_dir: Path, monkeypatch):
    from harness import intent_cycle as ic
    from harness.sidecar_integration import BoundaryScanResult
    from mvghb.sidecar import SessionContext

    monkeypatch.setattr(
        ic, "run_session_boundary_scan",
        lambda new_direction, window=25: BoundaryScanResult(
            context=SessionContext(
                last_n_entries=0, actor_breakdown={}, last_entry_types=[],
                last_timestamp=None, payload_topics=[],
            ),
            prior_entry_count=0, likely_drift=False, drift_reason=None,
        ),
    )
    monkeypatch.setattr(ic, "commit_anchor", lambda writer=None: None)


def test_chain_sequence_single_iteration(tmp_path: Path, monkeypatch):
    writer = _RecordingWriter()
    _wire_cycle(writer, tmp_path, monkeypatch)

    cycle = IntentCycle(
        skill=SKILLS["S1"],
        verifier=lambda **kw: VerifierResponse(outcome="CONFIRMED"),
        producing_agent=_StubProducing(1),
        adversarial_agent=_StubAdversarial(),
        writer=writer,
        artefact_dir=tmp_path / "docs",
    )
    cycle.run(Moment1Input(
        convergence_state="Targeted",
        direction="sharpen",
        primary_derivation_intent=["INPUT-001"],
    ))
    assert writer.log == [
        ("direction_capture",    "human"),
        ("production",           "producing_agent"),
        ("adversarial_challenge","adversarial_agent"),
        ("verification",         "human"),
        ("cycle_close",          "orchestrator"),
    ]


def test_chain_sequence_with_partial_loop(tmp_path: Path, monkeypatch):
    writer = _RecordingWriter()
    _wire_cycle(writer, tmp_path, monkeypatch)

    state = {"call": 0}

    def verify(**kw):
        state["call"] += 1
        if state["call"] == 1:
            return VerifierResponse(
                outcome="PARTIAL", notes="",
                refined_direction="refined again",
            )
        return VerifierResponse(outcome="CONFIRMED")

    cycle = IntentCycle(
        skill=SKILLS["S1"],
        verifier=verify,
        producing_agent=_StubProducing(2),
        adversarial_agent=_StubAdversarial(),
        writer=writer,
        artefact_dir=tmp_path / "docs",
    )
    cycle.run(Moment1Input(
        convergence_state="Targeted",
        direction="sharpen",
        primary_derivation_intent=["INPUT-001"],
    ))
    # Expect: direction_capture, then 2x (production, adversarial_challenge,
    # verification), then cycle_close.
    got = [x[0] for x in writer.log]
    assert got == [
        "direction_capture",
        "production", "adversarial_challenge", "verification",
        "production", "adversarial_challenge", "verification",
        "cycle_close",
    ]


def test_cycle_does_not_close_without_confirmation(tmp_path: Path, monkeypatch):
    writer = _RecordingWriter()
    _wire_cycle(writer, tmp_path, monkeypatch)

    cycle = IntentCycle(
        skill=SKILLS["S1"],
        verifier=lambda **kw: VerifierResponse(
            outcome="REJECTED", notes="no",
            refined_direction="try again",
        ),
        producing_agent=_StubProducing(9),
        adversarial_agent=_StubAdversarial(),
        writer=writer,
        artefact_dir=tmp_path / "docs",
        max_iterations=2,
    )
    result = cycle.run(Moment1Input(
        convergence_state="Targeted",
        direction="sharpen",
        primary_derivation_intent=["INPUT-001"],
    ))
    assert result.artefact_path is None
    types = [x[0] for x in writer.log]
    assert "cycle_close" not in types
