"""Envelope canonical-bytes determinism — no DB."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from mvghb.chain_write.envelope import build_envelope, envelope_bytes


T = datetime(2026, 4, 18, 12, 0, 0, tzinfo=timezone.utc)
CID = UUID("11111111-1111-1111-1111-111111111111")
PREV = UUID("22222222-2222-2222-2222-222222222222")


def _env(payload: dict) -> dict:
    return build_envelope(
        chain_id=CID, prev_chain_id=PREV,
        entry_type="intake", actor_id="orchestrator",
        actor_role="orchestrator", ownership_tier="user",
        incident_id=None, payload_ref=payload,
        sop_versions_pinned=None, class_enum="NORMAL",
        timestamp=T, system_version="test", kek_id="abc",
    )


def test_envelope_bytes_stable_under_dict_reorder():
    a = _env({"a": 1, "b": 2, "c": 3})
    b = _env({"c": 3, "b": 2, "a": 1})
    assert envelope_bytes(a) == envelope_bytes(b)


def test_envelope_bytes_change_on_payload_change():
    a = _env({"a": 1})
    b = _env({"a": 2})
    assert envelope_bytes(a) != envelope_bytes(b)


def test_envelope_bytes_unicode_preserved():
    env = _env({"note": "テレコム NOC"})
    assert "テレコム" in envelope_bytes(env).decode("utf-8")


def test_envelope_includes_prev_chain_id():
    env = _env({"x": 1})
    assert env["prev_chain_id"] == str(PREV)
