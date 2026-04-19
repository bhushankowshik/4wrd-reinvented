"""ChainWriter integration tests against the live noc-gov DB.

Skipped unless MVGHB_LIVE_DB=1. Apply schema once via a session-scoped
fixture; each test uses unique actor_ids to avoid cross-test interference.
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest
from sqlalchemy import text

from mvghb.chain_write.envelope import build_envelope, envelope_bytes
from mvghb.chain_write.writer import ChainWriter
from mvghb.common import actors as actor_reg
from mvghb.common.crypto import constant_time_eq, derive_entry_key, hmac_sha256
from mvghb.common.db import gov_session
from mvghb.common.settings import get_settings


pytestmark = pytest.mark.skipif(
    os.environ.get("MVGHB_LIVE_DB") != "1",
    reason="set MVGHB_LIVE_DB=1 to run live-DB tests",
)


@pytest.fixture(scope="session", autouse=True)
def _apply_schema():
    from mvghb.common.sql_apply import apply_sql_file
    sql_path = Path(__file__).resolve().parents[1] / "db" / "0001_mvghb.sql"
    with gov_session() as s, s.begin():
        apply_sql_file(s, sql_path)


def _new_actor() -> tuple[str, str]:
    suffix = uuid.uuid4().hex[:8]
    return f"test_actor_{suffix}", "test_role"


def test_emit_signs_and_inserts():
    writer = ChainWriter()
    actor_id, role = _new_actor()
    res = writer.emit(
        entry_type="intake",
        actor_id=actor_id, actor_role=role,
        incident_id=None, payload_ref={"k": "v"},
    )
    assert res.committed is True
    assert res.prev_chain_id is None  # genesis emit for this actor
    assert len(res.hmac_signature) == 32

    with gov_session() as s:
        row = s.execute(text("""
            SELECT chain_id, hmac_signature, actor_id, prev_chain_id
              FROM governance_chain WHERE chain_id = :c
        """), {"c": str(res.chain_id)}).first()
    assert row is not None
    assert row[2] == actor_id
    assert bytes(row[1]) == res.hmac_signature
    assert row[3] is None


def test_prev_chain_id_links_correctly():
    writer = ChainWriter()
    actor_id, role = _new_actor()
    r1 = writer.emit(entry_type="intake", actor_id=actor_id,
                     actor_role=role, incident_id=None, payload_ref={"step": 1})
    r2 = writer.emit(entry_type="intake", actor_id=actor_id,
                     actor_role=role, incident_id=None, payload_ref={"step": 2})
    r3 = writer.emit(entry_type="intake", actor_id=actor_id,
                     actor_role=role, incident_id=None, payload_ref={"step": 3})

    assert r1.prev_chain_id is None
    assert r2.prev_chain_id == r1.chain_id
    assert r3.prev_chain_id == r2.chain_id

    with gov_session() as s:
        head = actor_reg.get_head(s, actor_id)
    assert head.head_chain_id == r3.chain_id
    assert head.entry_count == 3


def test_signing_roundtrip_recompute_matches_stored():
    """Recompute the HMAC from envelope bytes and confirm it matches what's in PG."""
    writer = ChainWriter()
    actor_id, role = _new_actor()
    res = writer.emit(
        entry_type="intake", actor_id=actor_id, actor_role=role,
        incident_id=None, payload_ref={"hello": "world"},
    )
    settings = get_settings()
    with gov_session() as s:
        row = s.execute(text("""
            SELECT chain_id, prev_chain_id, hmac_signature, actor_id, actor_role,
                   entry_type, ownership_tier, incident_id, payload_ref,
                   sop_versions_pinned, timestamp, system_version, class_enum
              FROM governance_chain WHERE chain_id = :c
        """), {"c": str(res.chain_id)}).mappings().first()
    env = build_envelope(
        chain_id=row["chain_id"] if isinstance(row["chain_id"], uuid.UUID) else uuid.UUID(row["chain_id"]),
        prev_chain_id=row["prev_chain_id"],
        entry_type=row["entry_type"], actor_id=row["actor_id"],
        actor_role=row["actor_role"], ownership_tier=row["ownership_tier"],
        incident_id=row["incident_id"], payload_ref=row["payload_ref"],
        sop_versions_pinned=row["sop_versions_pinned"],
        class_enum=row["class_enum"], timestamp=row["timestamp"],
        system_version=row["system_version"], kek_id=settings.kek_id,
    )
    chain_id_uuid = row["chain_id"] if isinstance(row["chain_id"], uuid.UUID) else uuid.UUID(row["chain_id"])
    per_key = derive_entry_key(settings.kek, chain_id_uuid)
    expected = hmac_sha256(per_key, envelope_bytes(env))
    assert constant_time_eq(expected, bytes(row["hmac_signature"]))


def test_unknown_actor_role_auto_registers():
    writer = ChainWriter()
    actor_id, role = _new_actor()
    writer.emit(entry_type="intake", actor_id=actor_id,
                actor_role=role, incident_id=None, payload_ref={})
    with gov_session() as s:
        a = actor_reg.get_actor(s, actor_id)
    assert a is not None
    assert a.actor_role == role
