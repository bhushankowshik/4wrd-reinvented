"""M7 — parser unit tests (markdown path, section classification)."""
from __future__ import annotations

from pathlib import Path

import pytest

from services.sop_ingest.parser import _guess_section_type, parse_sop


FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "sops"


def test_parse_markdown_returns_single_overview_section():
    sections = parse_sop(FIXTURES / "sop-remote-resolution-v1.md")
    assert len(sections) == 1
    only = sections[0]
    assert only.section_type == "overview"
    assert "Remote Resolution" in only.raw_text
    assert only.source_file == "sop-remote-resolution-v1.md"


def test_parse_unknown_suffix_returns_empty(tmp_path: Path):
    p = tmp_path / "note.bin"
    p.write_bytes(b"\x00\x01\x02")
    assert parse_sop(p) == []


@pytest.mark.parametrize(
    "heading,expected",
    [
        ("Remediation Actions", "remediation"),
        ("Action — Dispatch Initiation", "remediation"),
        ("Precondition", "precondition"),
        ("Escalation", "escalation"),
        ("References", "reference"),
        ("Overview", "overview"),
        ("Random Heading", "other"),
    ],
)
def test_guess_section_type(heading: str, expected: str):
    assert _guess_section_type(heading) == expected
