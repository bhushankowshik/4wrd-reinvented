"""Skill registry — one per 4WRD reference skill (INPUT-001 §6)."""
from harness.skills.s1_problem_crystallisation import S1_SKILL

SKILLS = {
    "S1": S1_SKILL,
}


_PREDECESSORS_CACHE: dict[str, str | None] | None = None


def _build_predecessors() -> dict[str, str | None]:
    """Flat predecessor map spanning both sequences.

    Within each sequence the predecessor is the prior entry. E1 bridges from
    the tail of SOLUTIONING so Execution cycles can auto-derive their PDI
    from the last Solutioning exit artefact.

    Imported lazily because ``harness.orchestrator`` itself imports
    ``harness.skills`` (via ``intent_cycle``); doing it at module top-level
    creates a circular import.
    """
    from harness.orchestrator.skill_sequence import (
        EXECUTION_SEQUENCE,
        SOLUTIONING_SEQUENCE,
    )
    m: dict[str, str | None] = {}
    for sid in SOLUTIONING_SEQUENCE.skill_ids:
        m[sid] = SOLUTIONING_SEQUENCE.predecessor(sid)
    for sid in EXECUTION_SEQUENCE.skill_ids:
        pred = EXECUTION_SEQUENCE.predecessor(sid)
        if pred is None:
            pred = SOLUTIONING_SEQUENCE.skill_ids[-1]
        m[sid] = pred
    return m


def _predecessors() -> dict[str, str | None]:
    global _PREDECESSORS_CACHE
    if _PREDECESSORS_CACHE is None:
        _PREDECESSORS_CACHE = _build_predecessors()
    return _PREDECESSORS_CACHE


def predecessor_of(skill_id: str) -> str | None:
    """Return the predecessor skill id, or None for sequence starts / unknown."""
    return _predecessors().get(skill_id)


__all__ = ["S1_SKILL", "SKILLS", "predecessor_of"]
