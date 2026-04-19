"""Registry — Layer 2 projection of tombstone entries.

Read-only. Tests inject a fake fetcher.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from sqlalchemy import text

from mvghb.common.db import gov_session


@dataclass(frozen=True)
class RetirementRecord:
    chain_id: str
    timestamp: datetime
    cycle_id: str
    skill_id: str | None
    reason: str
    successor_cycle_id: str | None
    retired_by: str
    artefact_path: str | None


TombstoneFetcher = Callable[[], list[dict[str, Any]]]


def _default_fetcher() -> list[dict[str, Any]]:
    sql = text(
        """
        SELECT chain_id, timestamp, payload_ref
          FROM governance_chain
         WHERE entry_type = 'tombstone'
         ORDER BY timestamp DESC
        """
    )
    with gov_session() as s:
        rows = s.execute(sql).mappings().all()
    return [
        {
            "chain_id": str(r["chain_id"]),
            "timestamp": r["timestamp"],
            "payload_ref": r["payload_ref"] or {},
        }
        for r in rows
    ]


def list_retirements(
    *, fetcher: TombstoneFetcher | None = None,
) -> list[RetirementRecord]:
    f = fetcher or _default_fetcher
    rows = f()
    out: list[RetirementRecord] = []
    for r in rows:
        p = r["payload_ref"] or {}
        out.append(
            RetirementRecord(
                chain_id=r["chain_id"],
                timestamp=r["timestamp"],
                cycle_id=str(p.get("cycle_id", "")),
                skill_id=(p.get("skill_id") or None),
                reason=str(p.get("reason", "")),
                successor_cycle_id=(p.get("successor_cycle_id") or None),
                retired_by=str(p.get("retired_by", "")),
                artefact_path=(p.get("artefact_path") or None),
            )
        )
    return out
