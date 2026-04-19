"""Skill sequence — declarative "what comes after what".

For the reference 4WRD domain we have two sequences:

  Solutioning  S1 → S2 → S3 → S4 → S5 → S6
  Execution    E1 → E2 → E3 → E4 → E5 → E6 → E7 → E8 → E9 → E10

A SkillSequence is a tuple of skill ids; the gate enforces ordering.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillSequence:
    name: str
    skill_ids: tuple[str, ...]

    def predecessor(self, skill_id: str) -> str | None:
        """Which skill must have cleared for `skill_id` to be gated open?"""
        if skill_id not in self.skill_ids:
            raise ValueError(
                f"skill_id {skill_id!r} not in sequence {self.name}: "
                f"{self.skill_ids}"
            )
        idx = self.skill_ids.index(skill_id)
        if idx == 0:
            return None
        return self.skill_ids[idx - 1]

    def successor(self, skill_id: str) -> str | None:
        if skill_id not in self.skill_ids:
            raise ValueError(
                f"skill_id {skill_id!r} not in sequence {self.name}"
            )
        idx = self.skill_ids.index(skill_id)
        if idx == len(self.skill_ids) - 1:
            return None
        return self.skill_ids[idx + 1]


SOLUTIONING_SEQUENCE = SkillSequence(
    name="solutioning",
    skill_ids=("S1", "S2", "S3", "S4", "S5", "S6"),
)

EXECUTION_SEQUENCE = SkillSequence(
    name="execution",
    skill_ids=("E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10"),
)
