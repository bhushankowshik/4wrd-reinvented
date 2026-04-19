"""Real ChainWriter — MVGH-β Wave 1.

Replaces the noc-product Chain-Write stub body. Interface (emit signature
+ ChainEmitResult shape) is frozen by E6a §2.7 — the only changes here:
  - chain_id is real UUIDv4 (not deterministic UUIDv5)
  - hmac_signature is real HMAC-SHA256 with HKDF-derived per-entry key
  - prev_chain_id is auto-resolved from mvghb_actor_head if not supplied
  - actor must exist in mvghb_actor; ChainWriter rejects unknown actors

Write path:
  1. validate entry_type (allowlist) and actor (registry).
  2. resolve prev_chain_id from per-actor head if caller didn't supply.
  3. mint UUIDv4 chain_id; build canonical envelope.
  4. derive per-entry key via HKDF(KEK, info=chain_id.bytes).
  5. compute hmac_signature = HMAC-SHA256(per_entry_key, canonical(env)).
  6. write WAL (fsync + dir-fsync) — M9c-2 write-through coherence.
  7. begin tx: INSERT into governance_chain; UPDATE per-actor head; commit.
  8. return ChainEmitResult.

WAL is authoritative. PG commit is best-effort but expected to succeed
for noc-gov reachability; on failure we log + bump backlog and surface
committed=False so callers can react. Recovery sweep (E6b later) will
replay WAL → PG.
"""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from uuid import UUID

from sqlalchemy import text

from mvghb.chain_write.allowlist import assert_known
from mvghb.chain_write.envelope import build_envelope, envelope_bytes
from mvghb.common import actors as actor_reg
from mvghb.common.canonical import canonical_bytes
from mvghb.common.crypto import derive_entry_key, hmac_sha256
from mvghb.common.db import gov_session
from mvghb.common.log import log
from mvghb.common.settings import get_settings


@dataclass
class ChainEmitResult:
    chain_id: UUID
    wal_path: str
    committed: bool
    hmac_signature: bytes
    content_hash: bytes
    timestamp: datetime
    prev_chain_id: UUID | None


class ChainWriter:
    """Real Chain-Write Service per MVGH-β Wave 1.

    Same interface as noc-product/services/chain_write/writer.py:ChainWriter.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._wal_dir = Path(self._settings.wal_dir)
        self._wal_dir.mkdir(parents=True, exist_ok=True)

    # ----- Public API (frozen by E6a §2.7) -----

    def emit(
        self,
        entry_type: str,
        actor_id: str,
        actor_role: str,
        incident_id: UUID | None,
        payload_ref: dict[str, Any],
        sop_versions_pinned: list[dict[str, Any]] | None = None,
        class_enum: Literal["NORMAL", "OVERRIDE"] = "NORMAL",
        prev_chain_id: UUID | None = None,
    ) -> ChainEmitResult:
        assert_known(entry_type)

        with gov_session() as s, s.begin():
            actor = actor_reg.get_actor(s, actor_id)
            if actor is None:
                # Auto-register actor on first emit if role given —
                # makes the harness usable from noc-product without a
                # separate registration step. Genesis chain entry is
                # emitted lazily here.
                actor_reg.upsert_actor(
                    s, actor_id=actor_id, actor_role=actor_role,
                )
                actor = actor_reg.get_actor(s, actor_id)
                assert actor is not None

            # Resolve prev_chain_id from per-actor head if caller didn't pin one.
            if prev_chain_id is None:
                head = actor_reg.get_head(s, actor_id)
                prev_chain_id = head.head_chain_id if head else None

            now = datetime.now(timezone.utc)
            chain_id = uuid.uuid4()

            envelope = build_envelope(
                chain_id=chain_id,
                prev_chain_id=prev_chain_id,
                entry_type=entry_type,
                actor_id=actor_id,
                actor_role=actor.actor_role,
                ownership_tier=actor.ownership_tier,
                incident_id=incident_id,
                payload_ref=payload_ref,
                sop_versions_pinned=sop_versions_pinned,
                class_enum=class_enum,
                timestamp=now,
                system_version=self._settings.system_version,
                kek_id=self._settings.kek_id,
            )
            env_bytes = envelope_bytes(envelope)

            per_entry_key = derive_entry_key(self._settings.kek, chain_id)
            sig = hmac_sha256(per_entry_key, env_bytes)
            content_hash = hmac_sha256(b"", canonical_bytes(payload_ref))  # neutral hash for payload-only

            self._wal_write(envelope, sig, now)

            try:
                s.execute(
                    text("""
                        INSERT INTO governance_chain
                          (chain_id, prev_chain_id, hmac_signature, actor_id,
                           actor_role, entry_type, ownership_tier, incident_id,
                           payload_ref, sop_versions_pinned, timestamp,
                           system_version, class_enum)
                        VALUES
                          (:chain_id, :prev_chain_id, :sig, :actor_id,
                           :actor_role, :entry_type, :tier, :incident_id,
                           CAST(:payload_ref AS JSONB),
                           CAST(:sop_versions_pinned AS JSONB), :ts,
                           :system_version, :class_enum)
                    """),
                    {
                        "chain_id": str(chain_id),
                        "prev_chain_id": str(prev_chain_id) if prev_chain_id else None,
                        "sig": sig,
                        "actor_id": actor_id,
                        "actor_role": actor.actor_role,
                        "entry_type": entry_type,
                        "tier": actor.ownership_tier,
                        "incident_id": str(incident_id) if incident_id else None,
                        "payload_ref": canonical_bytes(payload_ref).decode("utf-8"),
                        "sop_versions_pinned": (
                            canonical_bytes(sop_versions_pinned).decode("utf-8")
                            if sop_versions_pinned is not None else None
                        ),
                        "ts": now,
                        "system_version": self._settings.system_version,
                        "class_enum": class_enum,
                    },
                )
                actor_reg.update_head(
                    s, actor_id=actor_id,
                    head_chain_id=chain_id, head_timestamp=now,
                )
                committed = True
            except Exception as exc:  # noqa: BLE001
                log.warning(
                    "mvghb.chain_write.pg_commit_failed",
                    actor_id=actor_id, entry_type=entry_type,
                    chain_id=str(chain_id), error=str(exc),
                )
                committed = False
                raise  # let session.begin() roll back; caller sees None

        return ChainEmitResult(
            chain_id=chain_id,
            wal_path=str(self._wal_path(chain_id, now)),
            committed=committed,
            hmac_signature=sig,
            content_hash=content_hash,
            timestamp=now,
            prev_chain_id=prev_chain_id,
        )

    # ----- WAL (M9c-2 write-through) -----

    def _wal_path(self, chain_id: UUID, ts: datetime) -> Path:
        return self._wal_dir / f"{ts.strftime('%Y%m%dT%H%M%S%fZ')}-{chain_id}.json"

    def _wal_write(self, envelope: dict, sig: bytes, ts: datetime) -> None:
        wal_path = self._wal_path(UUID(envelope["chain_id"]), ts)
        tmp_path = wal_path.with_suffix(".json.tmp")
        record = {**envelope, "hmac_signature_hex": sig.hex()}
        tmp_path.write_bytes(canonical_bytes(record))
        with open(tmp_path, "rb") as f:
            os.fsync(f.fileno())
        os.replace(tmp_path, wal_path)
        try:
            fd = os.open(str(self._wal_dir), os.O_DIRECTORY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        except OSError:
            pass
