"""Emit a `tombstone` chain entry — retire a cycle or artefact.

A tombstone is the ONLY permitted mechanism for saying "this prior
cycle is no longer load-bearing". Silent removal is prohibited.

Payload shape:

  {
    "cycle_id": <target cycle>,
    "skill_id": <target skill, optional>,
    "artefact_path": <str, optional>,
    "reason": <required, human-readable>,
    "successor_cycle_id": <optional — pointer to a later cycle>,
    "retired_at": <ISO-8601>,
    "retired_by": <actor id>
  }
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from mvghb.chain_write.writer import ChainWriter


@dataclass(frozen=True)
class TombstoneResult:
    chain_id: UUID
    timestamp: datetime
    cycle_id: str
    reason: str


def emit_tombstone(
    *,
    cycle_id: UUID | str,
    reason: str,
    skill_id: str | None = None,
    artefact_path: str | None = None,
    successor_cycle_id: UUID | str | None = None,
    retired_by: str = "human",
    writer: ChainWriter | None = None,
) -> TombstoneResult:
    """Write one `tombstone` chain entry. Returns the new chain_id."""
    if not reason.strip():
        raise ValueError("tombstone reason must be non-empty.")

    writer = writer or ChainWriter()
    payload: dict[str, Any] = {
        "cycle_id": str(cycle_id),
        "reason": reason.strip(),
        "retired_at": datetime.now(timezone.utc).isoformat(),
        "retired_by": retired_by,
    }
    if skill_id is not None:
        payload["skill_id"] = skill_id
    if artefact_path is not None:
        payload["artefact_path"] = artefact_path
    if successor_cycle_id is not None:
        payload["successor_cycle_id"] = str(successor_cycle_id)

    res = writer.emit(
        entry_type="tombstone",
        actor_id=retired_by,
        actor_role="human_operator",
        incident_id=None,
        payload_ref=payload,
    )
    return TombstoneResult(
        chain_id=res.chain_id,
        timestamp=res.timestamp,
        cycle_id=str(cycle_id),
        reason=reason.strip(),
    )
