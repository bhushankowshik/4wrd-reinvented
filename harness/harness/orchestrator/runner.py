"""SequenceRunner — drive a skill sequence through governed cycles.

Given a SkillSequence and an `IntentCycle` factory, run each skill's
cycle in order, but ONLY if the gate for that skill is open (chain-
enforced via `gate_is_open`). If any skill's gate is closed, the
runner stops and surfaces the reason.

This is deliberately simple: the runner does not loop retries or
escalate — the human decides whether to open the gate manually (by
re-running the preceding skill to Exact) or skip.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from harness.intent_cycle import CycleResult, IntentCycle, Moment1Input
from harness.orchestrator.gate import GateResult, gate_is_open
from harness.orchestrator.skill_sequence import SkillSequence


@dataclass(frozen=True)
class SkillStep:
    """One slot in a SequenceRunner plan."""
    skill_id: str
    moment1: Moment1Input


@dataclass(frozen=True)
class SequenceResult:
    sequence_name: str
    completed: list[tuple[str, CycleResult]] = field(default_factory=list)
    blocked_at: tuple[str, GateResult] | None = None


IntentCycleFactory = Callable[[str], IntentCycle]


class SequenceRunner:
    """Run a sequence of skills, one Intent Cycle each, gate-enforced."""

    def __init__(
        self,
        *,
        sequence: SkillSequence,
        intent_cycle_factory: IntentCycleFactory,
    ) -> None:
        self._sequence = sequence
        self._factory = intent_cycle_factory

    def run(self, steps: list[SkillStep]) -> SequenceResult:
        completed: list[tuple[str, CycleResult]] = []
        for step in steps:
            gate = gate_is_open(
                skill_id=step.skill_id, sequence=self._sequence,
            )
            if not gate.open:
                return SequenceResult(
                    sequence_name=self._sequence.name,
                    completed=completed,
                    blocked_at=(step.skill_id, gate),
                )
            cycle = self._factory(step.skill_id)
            result = cycle.run(step.moment1)
            completed.append((step.skill_id, result))
        return SequenceResult(
            sequence_name=self._sequence.name,
            completed=completed,
            blocked_at=None,
        )
