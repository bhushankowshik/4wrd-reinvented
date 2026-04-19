"""Chain integrity verifier.

For each actor, walks the chain in chain order:
  1. Recompute the per-entry HMAC from canonical envelope + HKDF(KEK, chain_id).
  2. Verify prev_chain_id linkage (each entry's prev_chain_id == previous entry's chain_id).
Reports every mismatch with kind tag and identifying chain_id.

Walk strategy: pull entries by (actor_id) ordered by timestamp ASC. The
governance_chain primary key is (chain_id, timestamp), and we track
prev_chain_id explicitly, so timestamp-order is fine for verification —
linkage check catches reorder.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from mvghb.chain_write.envelope import build_envelope, envelope_bytes
from mvghb.common import actors as actor_reg
from mvghb.common.crypto import constant_time_eq, derive_entry_key, hmac_sha256
from mvghb.common.db import gov_session
from mvghb.common.log import log
from mvghb.common.settings import get_settings


@dataclass(frozen=True)
class Mismatch:
    chain_id: UUID
    actor_id: str
    kind: str         # 'hmac' | 'prev_link' | 'envelope_decode'
    detail: str


@dataclass
class VerifyReport:
    actor_id: str | None
    entries_checked: int = 0
    mismatches: list[Mismatch] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.mismatches


def _fetch_actor_entries(s: Session, actor_id: str) -> list[dict]:
    rows = s.execute(text("""
        SELECT chain_id, prev_chain_id, hmac_signature, actor_id, actor_role,
               entry_type, ownership_tier, incident_id, payload_ref,
               sop_versions_pinned, timestamp, system_version, class_enum
          FROM governance_chain
         WHERE actor_id = :a
         ORDER BY timestamp ASC
    """), {"a": actor_id}).mappings().all()
    return [dict(r) for r in rows]


def _verify_entry(row: dict, kek: bytes, kek_id: str) -> Mismatch | None:
    chain_id = row["chain_id"] if isinstance(row["chain_id"], UUID) else UUID(row["chain_id"])
    incident_id = row["incident_id"]
    if isinstance(incident_id, str):
        incident_id = UUID(incident_id)
    prev_id = row["prev_chain_id"]
    if isinstance(prev_id, str):
        prev_id = UUID(prev_id)

    envelope = build_envelope(
        chain_id=chain_id,
        prev_chain_id=prev_id,
        entry_type=row["entry_type"],
        actor_id=row["actor_id"],
        actor_role=row["actor_role"],
        ownership_tier=row["ownership_tier"],
        incident_id=incident_id,
        payload_ref=row["payload_ref"] or {},
        sop_versions_pinned=row["sop_versions_pinned"],
        class_enum=row["class_enum"],
        timestamp=row["timestamp"],
        system_version=row["system_version"],
        kek_id=kek_id,
    )
    per_key = derive_entry_key(kek, chain_id)
    expected = hmac_sha256(per_key, envelope_bytes(envelope))
    actual = bytes(row["hmac_signature"])

    if not constant_time_eq(expected, actual):
        return Mismatch(
            chain_id=chain_id,
            actor_id=row["actor_id"],
            kind="hmac",
            detail=f"expected={expected.hex()[:16]}... actual={actual.hex()[:16]}...",
        )
    return None


def verify_actor_chain(actor_id: str) -> VerifyReport:
    settings = get_settings()
    report = VerifyReport(actor_id=actor_id)

    with gov_session() as s:
        rows = _fetch_actor_entries(s, actor_id)

    expected_prev: UUID | None = None
    for row in rows:
        chain_id = (row["chain_id"] if isinstance(row["chain_id"], UUID)
                    else UUID(row["chain_id"]))
        prev_in_row = row["prev_chain_id"]
        if isinstance(prev_in_row, str):
            prev_in_row = UUID(prev_in_row)

        if prev_in_row != expected_prev:
            report.mismatches.append(Mismatch(
                chain_id=chain_id,
                actor_id=actor_id,
                kind="prev_link",
                detail=f"expected_prev={expected_prev} actual_prev={prev_in_row}",
            ))

        m = _verify_entry(row, settings.kek, settings.kek_id)
        if m is not None:
            report.mismatches.append(m)

        expected_prev = chain_id
        report.entries_checked += 1

    log.info(
        "mvghb.verify.actor_done",
        actor_id=actor_id,
        entries=report.entries_checked,
        mismatches=len(report.mismatches),
    )
    return report


def verify_all_chains() -> list[VerifyReport]:
    with gov_session() as s:
        actors = actor_reg.list_actors(s)
    return [verify_actor_chain(a.actor_id) for a in actors]
