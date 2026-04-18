"""M7 — secret scanner unit tests (SOP-004 quarantine path)."""
from __future__ import annotations

from services.secret_scanner.scan import scan


def test_empty_text_yields_no_matches():
    r = scan("")
    assert r.matches == []
    assert r.max_severity is None


def test_clean_sop_text_has_no_matches():
    r = scan(
        "Inspect alarm state. Pull interface counters. Escalate per the "
        "Escalation section if remediation fails."
    )
    assert r.matches == []


def test_aws_access_key_triggers_high():
    r = scan("export creds: AKIAABCDEFGHIJKLMNOP and others")
    assert r.max_severity == "high"
    assert any(m.pattern_id == "aws-access-key-id" for m in r.matches)


def test_private_key_triggers_high():
    r = scan("config snippet:\n-----BEGIN RSA PRIVATE KEY-----\nMIIB...")
    assert r.max_severity == "high"


def test_jwt_triggers_medium():
    jwt = (
        "eyJhbGciOiJIUzI1NiJ9."
        "eyJzdWIiOiJ0ZXN0In0."
        "abcdefghabcdefgh"
    )
    r = scan(f"token={jwt}")
    assert r.max_severity in {"medium", "high"}


def test_quarantine_threshold_is_medium_or_high():
    # Mirrors pipeline.py guard: matches in {high, medium} quarantine.
    jwt = (
        "eyJhbGciOiJIUzI1NiJ9."
        "eyJzdWIiOiJ0ZXN0In0."
        "abcdefghabcdefgh"
    )
    for text in [
        "AKIAABCDEFGHIJKLMNOP",
        f"token={jwt}",
        "-----BEGIN PRIVATE KEY-----",
    ]:
        sev = scan(text).max_severity
        assert sev in {"medium", "high"}, f"{text!r} → {sev}"


def test_preview_is_redacted():
    r = scan("leaked = AKIAABCDEFGHIJKLMNOP done")
    assert r.matches
    for m in r.matches:
        assert "***" in m.preview
