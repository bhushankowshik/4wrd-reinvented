"""Integrity verifier integration — including tamper detection."""
from __future__ import annotations

import os
import uuid
from pathlib import Path

import pytest
from sqlalchemy import text

from mvghb.chain_write.writer import ChainWriter
from mvghb.common.db import gov_session
from mvghb.integrity_verifier import verify_actor_chain


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


def _seed(actor_id: str, n: int = 3) -> list:
    writer = ChainWriter()
    rs = []
    for i in range(n):
        rs.append(writer.emit(
            entry_type="intake", actor_id=actor_id, actor_role="test_role",
            incident_id=None, payload_ref={"i": i},
        ))
    return rs


def test_verifier_clean_chain_passes():
    actor_id = f"verify_clean_{uuid.uuid4().hex[:6]}"
    _seed(actor_id, n=4)
    rep = verify_actor_chain(actor_id)
    assert rep.entries_checked == 4
    assert rep.ok, rep.mismatches


def test_verifier_detects_payload_tamper():
    """Mutating payload_ref outside ChainWriter must produce an HMAC mismatch."""
    actor_id = f"verify_tamper_{uuid.uuid4().hex[:6]}"
    rs = _seed(actor_id, n=3)
    target = rs[1].chain_id

    # The append-only trigger blocks UPDATE on governance_chain — we need to
    # bypass it to simulate tampering. Drop trigger, mutate, recreate.
    with gov_session() as s, s.begin():
        s.execute(text("DROP TRIGGER IF EXISTS governance_chain_append_only ON governance_chain"))
        s.execute(text("""
            UPDATE governance_chain
               SET payload_ref = CAST(:p AS JSONB)
             WHERE chain_id = :c
        """), {"p": '{"i": 999, "evil": true}', "c": str(target)})
        s.execute(text("""
            CREATE TRIGGER governance_chain_append_only
              BEFORE UPDATE OR DELETE ON governance_chain
              FOR EACH ROW EXECUTE FUNCTION reject_governance_chain_mutation()
        """))

    rep = verify_actor_chain(actor_id)
    assert not rep.ok
    kinds = {m.kind for m in rep.mismatches}
    assert "hmac" in kinds


def test_verifier_detects_prev_link_break():
    """Mutating prev_chain_id breaks linkage; verifier reports kind='prev_link'."""
    actor_id = f"verify_prevlink_{uuid.uuid4().hex[:6]}"
    rs = _seed(actor_id, n=3)
    target = rs[1].chain_id
    bogus = uuid.uuid4()

    with gov_session() as s, s.begin():
        s.execute(text("DROP TRIGGER IF EXISTS governance_chain_append_only ON governance_chain"))
        s.execute(text("""
            UPDATE governance_chain SET prev_chain_id = :p WHERE chain_id = :c
        """), {"p": str(bogus), "c": str(target)})
        s.execute(text("""
            CREATE TRIGGER governance_chain_append_only
              BEFORE UPDATE OR DELETE ON governance_chain
              FOR EACH ROW EXECUTE FUNCTION reject_governance_chain_mutation()
        """))

    rep = verify_actor_chain(actor_id)
    assert not rep.ok
    kinds = {m.kind for m in rep.mismatches}
    # prev_link mismatch + hmac mismatch (envelope changed)
    assert "prev_link" in kinds
