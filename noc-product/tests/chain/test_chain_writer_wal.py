"""M10 — chain-writer WAL + canonical envelope tests (no DB needed).

Uses a tmp WAL dir and monkeypatches gov_session so the PG commit
returns failure-by-design, letting us validate that WAL persistence
is authoritative and governance_chain commit is best-effort.
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import pytest

from services.common.canonical import canonical_bytes, content_hash
from services.chain_write import writer as cw


@pytest.fixture
def wal_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(
        cw, "get_settings", lambda: type("S", (), {
            "chain_write_wal_dir": str(tmp_path),
            "system_version": "test-version",
        })()
    )
    return tmp_path


@pytest.fixture
def no_pg(monkeypatch):
    @contextmanager
    def _raises():
        raise RuntimeError("pg unavailable (test)")
        yield None
    monkeypatch.setattr(cw, "gov_session", _raises)


def test_emit_writes_wal_even_if_pg_fails(wal_tmp, no_pg):
    w = cw.ChainWriter()
    incident_id = uuid4()
    result = w.emit(
        entry_type="intake",
        actor_id="test-actor",
        actor_role="service_account",
        incident_id=incident_id,
        payload_ref={"k": "v", "incident_id": str(incident_id)},
    )
    assert result.committed is False
    wal_files = list(Path(wal_tmp).glob("*.json"))
    assert len(wal_files) == 1
    body = json.loads(wal_files[0].read_bytes())
    assert body["chain_id"] == str(result.chain_id)
    assert body["entry_type"] == "intake"
    assert body["hmac_signature_hex"] == result.hmac_signature.hex()


def test_unknown_entry_type_rejected(wal_tmp):
    from services.chain_write.allowlist import UnknownEntryTypeError

    w = cw.ChainWriter()
    with pytest.raises(UnknownEntryTypeError):
        w.emit(
            entry_type="not_allowed_x",
            actor_id="x", actor_role="x",
            incident_id=None, payload_ref={},
        )


def test_chain_id_is_deterministic_over_envelope(wal_tmp, no_pg, monkeypatch):
    """Same envelope → same chain_id (pure UUIDv5 over canonical bytes)."""
    import uuid
    from datetime import datetime, timezone

    # Freeze time so envelopes are identical.
    fixed = datetime(2026, 4, 18, 10, 0, 0, tzinfo=timezone.utc)

    class _Clock:
        @staticmethod
        def now(_tz=None):
            return fixed

    monkeypatch.setattr(cw, "datetime", _Clock)

    w = cw.ChainWriter()
    incident_id = uuid4()
    args = dict(
        entry_type="intake",
        actor_id="a",
        actor_role="service_account",
        incident_id=incident_id,
        payload_ref={"k": "v"},
    )
    r1 = w.emit(**args)
    # Second emit with identical timestamp frozen → identical UUIDv5.
    r2 = w.emit(**args)
    assert r1.chain_id == r2.chain_id
