"""Multi-skill orchestration — chain of Intent Cycles under gate discipline.

Two moving parts:

  skill_sequence  — the ordered list that governs "what's next" (e.g.
                    the Solutioning pipeline S1→S2→…→S6). Declarative.
  gate            — chain-enforced predicate "has skill X closed at
                    Exact?". Returns a reason the human can read.
  runner          — drives one skill at a time, only starting skill
                    N+1 if the gate for skill N is open.

Gate discipline is NEVER derived from an in-process flag — it is a
SQL query over the governance_chain. If someone reverts a cycle_close
entry or rolls the DB back, the gate reflects reality.
"""
from harness.orchestrator.gate import (
    GateResult,
    gate_is_open,
    latest_close_at_exact,
)
from harness.orchestrator.skill_sequence import SkillSequence
from harness.orchestrator.runner import (
    SkillStep,
    SequenceResult,
    SequenceRunner,
)

__all__ = [
    "GateResult",
    "SequenceResult",
    "SequenceRunner",
    "SkillSequence",
    "SkillStep",
    "gate_is_open",
    "latest_close_at_exact",
]
