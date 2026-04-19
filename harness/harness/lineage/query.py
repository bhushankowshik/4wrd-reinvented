"""Backwards lineage query — "what led to this artefact?"

Given a ref (file path / URL / chain_id), walk every `artefact_lineage`
chain entry that includes the ref in either its primary or incidental
lists. Return the cycle_ids + skill_ids that depended on it, sorted
newest first.

This is a Layer 2 projection: read-only, computed per request.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from sqlalchemy import text

from mvghb.common.db import gov_session


@dataclass(frozen=True)
class LineageCycle:
    cycle_id: str
    skill_id: str
    category: str  # "primary" | "incidental"
    chain_id: str
    timestamp: datetime


@dataclass(frozen=True)
class LineageWalk:
    query_ref: str
    rows: list[LineageCycle] = field(default_factory=list)

    def cycle_ids(self) -> list[str]:
        return list({r.cycle_id: None for r in self.rows}.keys())

    def render(self) -> str:
        lines = [f"# Lineage walk — {self.query_ref}"]
        if not self.rows:
            lines.append("(no cycle depends on this ref)")
            return "\n".join(lines)
        for r in self.rows:
            lines.append(
                f"- {r.timestamp.isoformat()}  {r.skill_id}  "
                f"{r.category:<10}  cycle={r.cycle_id}  "
                f"chain={r.chain_id[:8]}"
            )
        return "\n".join(lines)


LineageFetcher = Callable[[], list[dict[str, Any]]]


def _default_fetcher() -> list[dict[str, Any]]:
    """Read every artefact_lineage entry, newest first."""
    sql = text(
        """
        SELECT chain_id, timestamp, payload_ref
          FROM governance_chain
         WHERE entry_type = 'artefact_lineage'
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


def walk_backwards(
    *, ref: str, fetcher: LineageFetcher | None = None,
) -> LineageWalk:
    """Find every cycle whose lineage entry includes `ref`."""
    f = fetcher or _default_fetcher
    rows = f()
    hits: list[LineageCycle] = []
    for r in rows:
        payload = r["payload_ref"] or {}
        cycle_id = str(payload.get("cycle_id") or "")
        skill_id = str(payload.get("skill_id") or "")
        for category in ("primary", "incidental"):
            for entry in payload.get(category, []):
                if not isinstance(entry, dict):
                    continue
                if entry.get("ref") == ref:
                    hits.append(
                        LineageCycle(
                            cycle_id=cycle_id,
                            skill_id=skill_id,
                            category=category,
                            chain_id=r["chain_id"],
                            timestamp=r["timestamp"],
                        )
                    )
                    break  # one hit per category per entry
    return LineageWalk(query_ref=ref, rows=hits)
