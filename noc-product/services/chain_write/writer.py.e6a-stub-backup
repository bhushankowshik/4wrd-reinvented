"""Chain-Write stub per E6a §2.7.

E6a provides the stub body: local WAL fsync + async PG commit.
E6b swaps the body for the MVGH-β-backed implementation
without touching the ChainWriter interface.
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

from services.chain_write.allowlist import assert_known
from services.common.canonical import canonical_bytes, content_hash
from services.common.db import gov_session
from services.common.settings import get_settings
from services.common.telemetry import CHAIN_EMITS, CHAIN_WAL_BACKLOG, log


STUB_NAMESPACE_UUID = UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


@dataclass
class ChainEmitResult:
    chain_id: UUID
    wal_path: str
    committed: bool
    hmac_signature: bytes
    content_hash: bytes
    timestamp: datetime


def _canonical_envelope(
    *,
    entry_type: str,
    actor_id: str,
    actor_role: str,
    incident_id: UUID | None,
    payload_ref: dict,
    sop_versions_pinned: list[dict] | None,
    class_enum: str,
    timestamp_iso: str,
    system_version: str,
    prev_chain_id: UUID | None,
) -> bytes:
    return canonical_bytes({
        "entry_type": entry_type,
        "actor_id": actor_id,
        "actor_role": actor_role,
        "incident_id": str(incident_id) if incident_id else None,
        "payload_ref": payload_ref,
        "sop_versions_pinned": sop_versions_pinned,
        "class_enum": class_enum,
        "timestamp": timestamp_iso,
        "system_version": system_version,
        "prev_chain_id": str(prev_chain_id) if prev_chain_id else None,
    })


class ChainWriter:
    """Stub Chain-Write Service per E6a §2.7.

    Interface is frozen by E6a. Do not change signatures without
    bumping the canonical-payload contract (OF-6.6).
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._wal_dir = Path(self._settings.chain_write_wal_dir)
        self._wal_dir.mkdir(parents=True, exist_ok=True)

    def emit(
        self,
        entry_type: str,
        actor_id: str,
        actor_role: str,
        incident_id: UUID | None,
        payload_ref: dict,
        sop_versions_pinned: list[dict] | None = None,
        class_enum: Literal["NORMAL", "OVERRIDE"] = "NORMAL",
        prev_chain_id: UUID | None = None,
    ) -> ChainEmitResult:
        assert_known(entry_type)

        now = datetime.now(timezone.utc)
        ts_iso = now.isoformat()

        # Deterministic stub chain_id via UUIDv5 over canonical envelope
        # — no real HMAC in dev; E6b fills this in.
        envelope = _canonical_envelope(
            entry_type=entry_type,
            actor_id=actor_id,
            actor_role=actor_role,
            incident_id=incident_id,
            payload_ref=payload_ref,
            sop_versions_pinned=sop_versions_pinned,
            class_enum=class_enum,
            timestamp_iso=ts_iso,
            system_version=self._settings.system_version,
            prev_chain_id=prev_chain_id,
        )
        chain_id = uuid.uuid5(STUB_NAMESPACE_UUID, envelope.decode("utf-8", errors="replace"))

        # Stub "hmac" — SHA-256 of the canonical envelope bytes. NOT a
        # security claim; E6b replaces with Vault-backed HMAC.
        import hashlib
        stub_sig = hashlib.sha256(envelope).digest()

        # WAL with fsync, per E3 §4.5.
        wal_path = self._wal_dir / f"{now.strftime('%Y%m%dT%H%M%S%fZ')}-{chain_id}.json"
        tmp_path = wal_path.with_suffix(".json.tmp")
        envelope_record = {
            "chain_id": str(chain_id),
            "prev_chain_id": str(prev_chain_id) if prev_chain_id else None,
            "entry_type": entry_type,
            "actor_id": actor_id,
            "actor_role": actor_role,
            "incident_id": str(incident_id) if incident_id else None,
            "payload_ref": payload_ref,
            "sop_versions_pinned": sop_versions_pinned,
            "class_enum": class_enum,
            "timestamp": ts_iso,
            "system_version": self._settings.system_version,
            "hmac_signature_hex": stub_sig.hex(),
        }
        tmp_path.write_bytes(canonical_bytes(envelope_record))
        with open(tmp_path, "rb") as f:
            os.fsync(f.fileno())
        os.replace(tmp_path, wal_path)
        # Best-effort dir fsync — some filesystems ignore.
        try:
            fd = os.open(str(self._wal_dir), os.O_DIRECTORY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        except OSError:
            pass

        committed = False
        try:
            with gov_session() as s, s.begin():
                s.execute(
                    text("""
                        INSERT INTO governance_chain
                          (chain_id, prev_chain_id, hmac_signature, actor_id,
                           actor_role, entry_type, ownership_tier, incident_id,
                           payload_ref, sop_versions_pinned, timestamp,
                           system_version, class_enum)
                        VALUES
                          (:chain_id, :prev_chain_id, :sig, :actor_id,
                           :actor_role, :entry_type, 'user', :incident_id,
                           CAST(:payload_ref AS JSONB),
                           CAST(:sop_versions_pinned AS JSONB), :ts,
                           :system_version, :class_enum)
                    """),
                    {
                        "chain_id": str(chain_id),
                        "prev_chain_id": str(prev_chain_id) if prev_chain_id else None,
                        "sig": stub_sig,
                        "actor_id": actor_id,
                        "actor_role": actor_role,
                        "entry_type": entry_type,
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
            committed = True
            CHAIN_EMITS.labels(entry_type=entry_type, outcome="committed").inc()
        except Exception as exc:  # noqa: BLE001
            CHAIN_EMITS.labels(entry_type=entry_type, outcome="wal_only").inc()
            CHAIN_WAL_BACKLOG.inc()
            log.warning(
                "chain_write.pg_commit_failed",
                entry_type=entry_type,
                chain_id=str(chain_id),
                error=str(exc),
            )

        return ChainEmitResult(
            chain_id=chain_id,
            wal_path=str(wal_path),
            committed=committed,
            hmac_signature=stub_sig,
            content_hash=content_hash(payload_ref),
            timestamp=now,
        )
