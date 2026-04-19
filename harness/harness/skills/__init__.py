"""Skill registry — one per 4WRD reference skill (INPUT-001 §6)."""
from harness.skills.s1_problem_crystallisation import S1_SKILL

SKILLS = {
    "S1": S1_SKILL,
}

__all__ = ["S1_SKILL", "SKILLS"]
