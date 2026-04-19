"""Intent Cycle unit test with mocked agents.

Exercises the four moments end-to-end without calling Anthropic or the
real database — fake writer + fake agents + in-memory verifier. This
test pins the sequence (direction → production → adversarial →
verification → close) and the loop-on-PARTIAL behaviour.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest

from harness.agents.adversarial_agent import (
    AdversarialAgent,
    AdversarialOutput,
    Challenge,
)
from harness.agents.producing_agent import ProducingAgent, ProducingOutput
from harness.intent_cycle import (
    IntentCycle,
    Moment1Input,
    VerifierResponse,
)
from harness.skills import SKILLS


# ---- Fakes ----


class FakeProducingAgent:
    def __init__(self, outputs: list[str]) -> None:
        self._outputs = list(outputs)

    def produce(self, package) -> ProducingOutput:  # noqa: ANN001
        body = self._outputs.pop(0)
        return ProducingOutput(
            output=body,
            reasoning_trace="1. mocked\n2. mocked",
            raw=body,
            model="claude-sonnet-4-6",
        )


class FakeAdversarialAgent:
    def __init__(self, challenges_per_call: list[list[Challenge]]) -> None:
        self._cs = list(challenges_per_call)

    def challenge(self, package) -> AdversarialOutput:  # noqa: ANN001
        challenges = self._cs.pop(0)
        fc = any(
            c.axis == "FRAME_CHANGE" and c.severity == "CRITICAL"
            for c in challenges
        )
        return AdversarialOutput(
            challenges=challenges,
            frame_change_detected=fc,
            raw="{}",
            model="claude-opus-4-6",
        )


class FakeChainEmitResult:
    def __init__(self) -> None:
        self.chain_id = uuid4()
        self.timestamp = datetime.now(timezone.utc)


@dataclass
class EmittedEntry:
    entry_type: str
    actor_id: str
    actor_role: str
    payload_ref: dict[str, Any]


class FakeChainWriter:
    def __init__(self) -> None:
        self.emitted: list[EmittedEntry] = []

    def emit(
        self,
        entry_type,
        actor_id,
        actor_role,
        incident_id,
        payload_ref,
        sop_versions_pinned=None,
        class_enum="NORMAL",
        prev_chain_id=None,
    ):
        self.emitted.append(
            EmittedEntry(
                entry_type=entry_type,
                actor_id=actor_id,
                actor_role=actor_role,
                payload_ref=payload_ref,
            )
        )
        return FakeChainEmitResult()


@pytest.fixture()
def fake_writer():
    return FakeChainWriter()


@pytest.fixture()
def tmp_artefact_dir(tmp_path: Path) -> Path:
    return tmp_path / "docs"


class FakeResearchAgent:
    def gather(self, *, direction, primary_derivation_intent, knowledge_contribution):  # noqa: ANN001
        from harness.agents.research_agent import ResearchOutput
        return ResearchOutput(
            findings=["(fake)"], sources=list(primary_derivation_intent),
            raw="", invoked=True, model="fake-haiku",
        )


def _build_cycle(
    producing,
    adversarial,
    verifier,
    writer,
    artefact_dir: Path,
    max_iterations: int = 3,
    monkeypatch: pytest.MonkeyPatch | None = None,
):
    # Neutralise the sidecar scan + anchor commit — we only test
    # the orchestrator's moment sequencing here.
    from harness import intent_cycle as ic_mod

    if monkeypatch is not None:
        monkeypatch.setattr(
            ic_mod, "run_session_boundary_scan",
            lambda new_direction, window=25: _empty_scan(),
        )
        monkeypatch.setattr(ic_mod, "commit_anchor", lambda writer=None: None)
        # Force the Research Agent invocation path to return no findings
        # so tests don't hit the Anthropic API.
        monkeypatch.setattr(
            ic_mod, "should_invoke_research",
            lambda convergence_state, primary_derivation_intent: False,
        )

    return IntentCycle(
        skill=SKILLS["S1"],
        verifier=verifier,
        producing_agent=producing,
        adversarial_agent=adversarial,
        research_agent=FakeResearchAgent(),
        writer=writer,
        artefact_dir=artefact_dir,
        max_iterations=max_iterations,
    )


def _empty_scan():
    from harness.sidecar_integration import BoundaryScanResult
    from mvghb.sidecar import SessionContext
    return BoundaryScanResult(
        context=SessionContext(
            last_n_entries=0, actor_breakdown={}, last_entry_types=[],
            last_timestamp=None, payload_topics=[],
        ),
        prior_entry_count=0,
        likely_drift=False,
        drift_reason=None,
    )


# ---- Tests ----


def test_intent_cycle_converges_on_first_iteration(
    fake_writer, tmp_artefact_dir, monkeypatch,
):
    producing = FakeProducingAgent(outputs=["# Problem\ncrystal"])
    adversarial = FakeAdversarialAgent(challenges_per_call=[[
        Challenge(axis="OUTPUT", severity="MINOR",
                  challenge="trivial", evidence="none"),
    ]])

    def verifier(*, producing, adversarial, cycle_id, iteration):
        return VerifierResponse(outcome="CONFIRMED", notes="looks good")

    cycle = _build_cycle(
        producing, adversarial, verifier, fake_writer,
        tmp_artefact_dir, monkeypatch=monkeypatch,
    )

    result = cycle.run(Moment1Input(
        convergence_state="Explorative",
        direction="Crystallise test problem.",
        knowledge_contribution="Context: unit test.",
        primary_derivation_intent=["INPUT-001"],
    ))

    assert result.iterations == 1
    assert result.artefact_path is not None
    assert result.artefact_path.exists()
    # Sequence: direction_capture → production → adversarial_challenge
    # → verification → cycle_close
    entry_types = [e.entry_type for e in fake_writer.emitted]
    assert entry_types == [
        "direction_capture",
        "production",
        "adversarial_challenge",
        "verification",
        "artefact_lineage",
        "cycle_close",
    ]


def test_intent_cycle_loops_on_partial_verification(
    fake_writer, tmp_artefact_dir, monkeypatch,
):
    producing = FakeProducingAgent(
        outputs=["# draft 1", "# draft 2 (refined)"]
    )
    adversarial = FakeAdversarialAgent(challenges_per_call=[
        [Challenge(axis="REASONING", severity="MAJOR",
                   challenge="loose", evidence="line 2")],
        [Challenge(axis="OUTPUT", severity="MINOR",
                   challenge="fine", evidence="—")],
    ])

    state = {"call": 0}

    def verifier(*, producing, adversarial, cycle_id, iteration):
        state["call"] += 1
        if state["call"] == 1:
            return VerifierResponse(
                outcome="PARTIAL",
                notes="tighten step 2",
                refined_direction="Refined: narrow the scope.",
            )
        return VerifierResponse(outcome="CONFIRMED", notes="done")

    cycle = _build_cycle(
        producing, adversarial, verifier, fake_writer,
        tmp_artefact_dir, monkeypatch=monkeypatch,
    )

    result = cycle.run(Moment1Input(
        convergence_state="Targeted",
        direction="Sharpen the scope.",
        primary_derivation_intent=["INPUT-001"],
    ))

    assert result.iterations == 2
    # Two productions, two adversarial challenges, two verifications.
    entry_types = [e.entry_type for e in fake_writer.emitted]
    assert entry_types.count("production") == 2
    assert entry_types.count("adversarial_challenge") == 2
    assert entry_types.count("verification") == 2
    assert entry_types.count("cycle_close") == 1
    assert entry_types.count("artefact_lineage") == 1
    # Iteration counter must correctly increment across the PARTIAL loop:
    prod_iters = [
        e.payload_ref["iteration"] for e in fake_writer.emitted
        if e.entry_type == "production"
    ]
    assert prod_iters == [1, 2]
    verif_iters = [
        e.payload_ref["iteration"] for e in fake_writer.emitted
        if e.entry_type == "verification"
    ]
    assert verif_iters == [1, 2]


def test_intent_cycle_rejects_invalid_convergence_state():
    with pytest.raises(ValueError):
        Moment1Input(
            convergence_state="Bogus",  # type: ignore[arg-type]
            direction="x",
            primary_derivation_intent=[],
        )


def test_intent_cycle_requires_knowledge_in_explorative():
    with pytest.raises(ValueError):
        Moment1Input(
            convergence_state="Explorative",
            direction="x",
            knowledge_contribution=None,
            primary_derivation_intent=[],
        )
