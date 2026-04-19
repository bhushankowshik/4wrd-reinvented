"""Master anchor integration tests."""
from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest
from sqlalchemy import text

from mvghb.chain_write.writer import ChainWriter
from mvghb.common.crypto import constant_time_eq
from mvghb.common.db import gov_session
from mvghb.common.settings import get_settings
from mvghb.master_anchor import commit_anchor, compute_anchor_hmac, verify_anchor


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


def test_anchor_commits_and_verifies():
    writer = ChainWriter()
    # Write a couple of entries so heads exist.
    actor_id = f"anchor_test_{uuid.uuid4().hex[:6]}"
    writer.emit(entry_type="intake", actor_id=actor_id,
                actor_role="test", incident_id=None, payload_ref={"i": 1})
    writer.emit(entry_type="intake", actor_id=actor_id,
                actor_role="test", incident_id=None, payload_ref={"i": 2})

    res = commit_anchor(writer=writer)
    assert res is not None
    assert len(res.head_set) >= 1

    ok, detail = verify_anchor(res.anchor_id)
    assert ok, detail


def test_anchor_hmac_is_pure_function_of_kek_and_heads():
    settings = get_settings()
    heads = [
        ("aA", uuid.UUID("00000000-0000-0000-0000-000000000001")),
        ("aB", uuid.UUID("00000000-0000-0000-0000-000000000002")),
    ]
    h1 = compute_anchor_hmac(settings.kek, heads)
    h2 = compute_anchor_hmac(settings.kek, list(reversed(heads)))
    assert h1 == h2  # sorted internally
    h3 = compute_anchor_hmac(settings.kek, heads + [
        ("aC", uuid.UUID("00000000-0000-0000-0000-000000000003")),
    ])
    assert h3 != h1


def test_anchor_verify_fails_after_db_tamper():
    """If someone writes a different anchor_hmac into the index row,
    verify_anchor must return ok=False."""
    writer = ChainWriter()
    actor_id = f"anchor_tamper_{uuid.uuid4().hex[:6]}"
    writer.emit(entry_type="intake", actor_id=actor_id,
                actor_role="test", incident_id=None, payload_ref={"x": 1})
    res = commit_anchor(writer=writer)
    assert res is not None

    with gov_session() as s, s.begin():
        s.execute(text("""
            UPDATE mvghb_master_anchor SET anchor_hmac = :h WHERE anchor_id = :a
        """), {"h": b"\x00" * 32, "a": str(res.anchor_id)})

    ok, detail = verify_anchor(res.anchor_id)
    assert not ok
    assert "mismatch" in detail
