"""Real ChainWriter — MVGH-β Wave 1, deployed into noc-product.

This module is installed by `mvghb/activate_e6b.sh` as a drop-in
replacement for `services/chain_write/writer.py` (the E6a stub).

Interface (emit signature + ChainEmitResult) is frozen by E6a §2.7.
The body is the MVGH-β real implementation:

  - chain_id is real UUIDv4 (stub used deterministic UUIDv5).
  - hmac_signature is real HMAC-SHA256 with an HKDF-derived
    per-entry key (stub used SHA-256 over the envelope).
  - prev_chain_id is auto-resolved from mvghb_actor_head when the
    caller did not pin one — per-actor chains.
  - Unknown actors are auto-registered in mvghb_actor on first emit.

Self-contained: depends only on noc-product's `services.common.*`
and `cryptography` (already in uv.lock). Reads MVGHB_KEK from env.
"""
from __future__ import annotations

import base64
import hashlib
import hmac as _hmac
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from uuid import UUID

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from sqlalchemy import text

from services.chain_write.allowlist import assert_known
from services.common.canonical import canonical_bytes, content_hash
from services.common.db import gov_session
from services.common.settings import get_settings
from services.common.telemetry import CHAIN_EMITS, CHAIN_WAL_BACKLOG, log


ENVELOPE_VERSION = "mvghb-env-v1"
HARNESS_ENTRY_TYPES = {
    "genesis", "master_anchor", "frame_change_detected", "integrity_check_result",
}


# ---------------- KEK + crypto primitives ----------------


def _load_kek() -> bytes:
    raw_b64 = os.environ.get("MVGHB_KEK")
    if not raw_b64:
        raise RuntimeError(
            "MVGHB_KEK env var not set. Run `mvghb bootstrap init` in the "
            "mvghb package or copy the value into noc-product/.env."
        )
    kek = base64.b64decode(raw_b64, validate=True)
    if len(kek) != 32:
        raise RuntimeError(f"MVGHB_KEK decoded length {len(kek)} != 32")
    return kek


def _kek_id(kek: bytes) -> str:
    return hashlib.sha256(kek).hexdigest()[:16]


def _derive_entry_key(kek: bytes, entry_id: UUID) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(), length=32, salt=None, info=entry_id.bytes,
    ).derive(kek)


def _hmac_sha256(key: bytes, data: bytes) -> bytes:
    return _hmac.new(key, data, hashlib.sha256).digest()


# ---------------- Envelope ----------------


def _build_envelope(
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


# ---------------- Actor registry + head ----------------


def _get_or_create_actor(s, actor_id: str, actor_role: str) -> tuple[str, str]:
    row = s.execute(
        text("""SELECT actor_role, ownership_tier FROM mvghb_actor
                WHERE actor_id = :a"""), {"a": actor_id},
    ).first()
    if row is not None:
        return row[0], row[1]
    s.execute(
        text("""INSERT INTO mvghb_actor (actor_id, actor_role, ownership_tier)
                VALUES (:a, :r, 'user')
                ON CONFLICT (actor_id) DO NOTHING"""),
        {"a": actor_id, "r": actor_role},
    )
    return actor_role, "user"


def _get_head(s, actor_id: str) -> UUID | None:
    row = s.execute(
        text("SELECT head_chain_id FROM mvghb_actor_head WHERE actor_id = :a"),
        {"a": actor_id},
    ).first()
    return row[0] if row else None


def _update_head(s, *, actor_id: str, head_chain_id: UUID, ts: datetime) -> None:
    s.execute(
        text("""
            INSERT INTO mvghb_actor_head
              (actor_id, head_chain_id, head_timestamp, entry_count)
            VALUES (:a, :c, :t, 1)
            ON CONFLICT (actor_id) DO UPDATE
              SET head_chain_id = EXCLUDED.head_chain_id,
                  head_timestamp = EXCLUDED.head_timestamp,
                  entry_count = mvghb_actor_head.entry_count + 1
        """),
        {"a": actor_id, "c": str(head_chain_id), "t": ts},
    )


# ---------------- Public interface (E6a §2.7 frozen) ----------------


@dataclass
class ChainEmitResult:
    chain_id: UUID
    wal_path: str
    committed: bool
    hmac_signature: bytes
    content_hash: bytes
    timestamp: datetime


class ChainWriter:
    """Real Chain-Write Service per MVGH-β Wave 1.

    Interface identical to the E6a stub. Body: HKDF-derived per-entry
    HMAC-SHA256 over the canonical envelope, plus per-actor chain
    linkage via mvghb_actor_head.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._wal_dir = Path(self._settings.chain_write_wal_dir)
        self._wal_dir.mkdir(parents=True, exist_ok=True)
        self._kek = _load_kek()
        self._kek_id = _kek_id(self._kek)
        log.info(
            "chain_write.mvghb_activated",
            kek_id=self._kek_id, wal_dir=str(self._wal_dir),
        )

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
        if entry_type not in HARNESS_ENTRY_TYPES:
            assert_known(entry_type)

        now = datetime.now(timezone.utc)
        chain_id = uuid.uuid4()

        committed = False
        wal_path: Path | None = None
        sig = b""

        try:
            with gov_session() as s, s.begin():
                role, tier = _get_or_create_actor(s, actor_id, actor_role)
                if prev_chain_id is None:
                    prev_chain_id = _get_head(s, actor_id)

                envelope = _build_envelope(
                    chain_id=chain_id,
                    prev_chain_id=prev_chain_id,
                    entry_type=entry_type,
                    actor_id=actor_id,
                    actor_role=role,
                    ownership_tier=tier,
                    incident_id=incident_id,
                    payload_ref=payload_ref,
                    sop_versions_pinned=sop_versions_pinned,
                    class_enum=class_enum,
                    timestamp=now,
                    system_version=self._settings.system_version,
                    kek_id=self._kek_id,
                )
                env_bytes = canonical_bytes(envelope)
                per_entry_key = _derive_entry_key(self._kek, chain_id)
                sig = _hmac_sha256(per_entry_key, env_bytes)

                wal_path = self._wal_write(envelope, sig, now, chain_id)

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
                        "actor_role": role,
                        "entry_type": entry_type,
                        "tier": tier,
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
                _update_head(s, actor_id=actor_id, head_chain_id=chain_id, ts=now)
            committed = True
            CHAIN_EMITS.labels(entry_type=entry_type, outcome="committed").inc()
        except Exception as exc:  # noqa: BLE001
            CHAIN_EMITS.labels(entry_type=entry_type, outcome="wal_only").inc()
            CHAIN_WAL_BACKLOG.inc()
            log.warning(
                "chain_write.pg_commit_failed",
                entry_type=entry_type, chain_id=str(chain_id), error=str(exc),
            )

        return ChainEmitResult(
            chain_id=chain_id,
            wal_path=str(wal_path) if wal_path else "",
            committed=committed,
            hmac_signature=sig,
            content_hash=content_hash(payload_ref),
            timestamp=now,
        )

    # ---------------- WAL (M9c-2 write-through) ----------------

    def _wal_write(
        self, envelope: dict, sig: bytes, ts: datetime, chain_id: UUID,
    ) -> Path:
        wal_path = self._wal_dir / f"{ts.strftime('%Y%m%dT%H%M%S%fZ')}-{chain_id}.json"
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
        return wal_path
