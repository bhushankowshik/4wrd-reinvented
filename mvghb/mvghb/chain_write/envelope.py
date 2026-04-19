"""Canonical envelope for HMAC.

The HMAC input is canonical_bytes(envelope_dict). The envelope is the
complete, deterministic representation of the entry. Any field that is
included in the chain MUST be in the envelope.

The envelope key set is frozen at v1; adding a field requires a v2
schema migration with a flag day (OF-6.6).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from mvghb.common.canonical import canonical_bytes


ENVELOPE_VERSION = "mvghb-env-v1"


def build_envelope(
    *,
    chain_id: UUID,
    prev_chain_id: UUID | None,
    entry_type: str,
    actor_id: str,
    actor_role: str,
    ownership_tier: str,
    incident_id: UUID | None,
    payload_ref: dict[str, Any],
    sop_versions_pinned: list[dict[str, Any]] | None,
    class_enum: str,
    timestamp: datetime,
    system_version: str,
    kek_id: str,
) -> dict[str, Any]:
    return {
        "envelope_version": ENVELOPE_VERSION,
        "chain_id": str(chain_id),
        "prev_chain_id": str(prev_chain_id) if prev_chain_id else None,
        "entry_type": entry_type,
        "actor_id": actor_id,
        "actor_role": actor_role,
        "ownership_tier": ownership_tier,
        "incident_id": str(incident_id) if incident_id else None,
        "payload_ref": payload_ref,
        "sop_versions_pinned": sop_versions_pinned,
        "class_enum": class_enum,
        "timestamp": timestamp.isoformat(),
        "system_version": system_version,
        "kek_id": kek_id,
    }


def envelope_bytes(env: dict[str, Any]) -> bytes:
    return canonical_bytes(env)
