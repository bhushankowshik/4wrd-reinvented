"""Gate discipline — chain-enforced predicates over governance_chain.

The single rule:

  skill N+1 can start only if skill N has at least one cycle_close
  entry whose payload_ref.convergence_state_at_exit == "Exact"
  AND is not superseded by a later tombstone entry.

This module provides two primitives:

  latest_close_at_exact(skill_id)  — fetch the newest qualifying
                                      cycle_close row for a skill;
                                      returns None if none exists.
  gate_is_open(skill_id, sequence) — True iff every predecessor in
                                      the sequence has a qualifying
                                      cycle_close. Carries a reason.

Both go through a fetcher callable so tests can inject a fake.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from sqlalchemy import text

from mvghb.common.db import gov_session

from harness.orchestrator.skill_sequence import SkillSequence


@dataclass(frozen=True)
class GateResult:
    skill_id: str
    open: bool
    reason: str
    blocking_skill_id: str | None = None


CloseFetcher = Callable[[str], dict[str, Any] | None]


def _default_close_fetcher(skill_id: str) -> dict[str, Any] | None:
    """Return the newest non-tombstoned cycle_close at Exact for a skill."""
    sql = text(
        """
        SELECT c.chain_id, c.timestamp, c.payload_ref
          FROM governance_chain c
         WHERE c.entry_type = 'cycle_close'
           AND c.payload_ref->>'skill_id' = :skill
           AND c.payload_ref->>'convergence_state_at_exit' = 'Exact'
           AND NOT EXISTS (
                 SELECT 1 FROM governance_chain t
                  WHERE t.entry_type = 'tombstone'
                    AND t.payload_ref->>'cycle_id' = c.payload_ref->>'cycle_id'
                    AND t.timestamp > c.timestamp
               )
         ORDER BY c.timestamp DESC
         LIMIT 1
        """
    )
    with gov_session() as s:
        row = s.execute(sql, {"skill": skill_id}).mappings().first()
    if row is None:
        return None
    return {
        "chain_id": str(row["chain_id"]),
        "timestamp": row["timestamp"],
        "payload_ref": row["payload_ref"] or {},
    }


def latest_close_at_exact(
    skill_id: str, *, fetcher: CloseFetcher | None = None,
) -> dict[str, Any] | None:
    f = fetcher or _default_close_fetcher
    return f(skill_id)


def gate_is_open(
    *,
    skill_id: str,
    sequence: SkillSequence,
    fetcher: CloseFetcher | None = None,
) -> GateResult:
    """Is `skill_id` allowed to start, given the sequence gate rule?"""
    predecessor = sequence.predecessor(skill_id)
    if predecessor is None:
        return GateResult(
            skill_id=skill_id, open=True,
            reason=f"{skill_id} is the first skill in sequence "
                   f"{sequence.name}; no predecessor to clear.",
        )
    row = latest_close_at_exact(predecessor, fetcher=fetcher)
    if row is None:
        return GateResult(
            skill_id=skill_id,
            open=False,
            blocking_skill_id=predecessor,
            reason=(
                f"{skill_id} is blocked — its predecessor {predecessor} "
                f"has no cycle_close at Exact on the chain. "
                f"Close {predecessor} at Exact before starting {skill_id}."
            ),
        )
    ts: datetime = row["timestamp"]
    cycle_id = row["payload_ref"].get("cycle_id")
    return GateResult(
        skill_id=skill_id,
        open=True,
        blocking_skill_id=None,
        reason=(
            f"{skill_id} is open — {predecessor} closed at Exact at "
            f"{ts.isoformat()} (cycle {cycle_id})."
        ),
    )
