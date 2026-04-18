"""M7 — chunker unit tests."""
from __future__ import annotations

import tiktoken

from services.sop_ingest.chunker import (
    _TARGET_MAX,
    _split_paragraphs,
    _split_sentences,
    chunk_sections,
)
from services.sop_ingest.parser import ParsedSection


def _enc():
    return tiktoken.get_encoding("cl100k_base")


def test_split_paragraphs_strips_blank_lines():
    blob = "First para.\n\n  \n\nSecond para spans\ntwo lines."
    assert _split_paragraphs(blob) == [
        "First para.",
        "Second para spans\ntwo lines.",
    ]


def test_split_sentences_handles_trailing_punctuation():
    blob = "One. Two! Three? Four."
    assert _split_sentences(blob) == ["One.", "Two!", "Three?", "Four."]


def test_short_section_becomes_single_chunk():
    sections = [
        ParsedSection(
            section_path="Intro",
            section_type="overview",
            raw_text="A very brief section with under one hundred tokens.",
            source_file="a.md",
        )
    ]
    chunks = chunk_sections(sections)
    assert len(chunks) == 1
    assert chunks[0].chunk_seq == 1
    assert chunks[0].section_path == "Intro"


def test_long_section_splits_with_overlap():
    enc = _enc()
    # ~4000 tokens worth of repetitive paragraph structure.
    paragraph = (
        "This is a routine operational paragraph describing a standard "
        "network diagnostic procedure used by tier-two engineers working on "
        "access-layer packet loss remediation and associated verification "
        "steps that must be followed in order before escalation. "
    )
    blob = "\n\n".join([paragraph] * 60)
    sections = [
        ParsedSection(
            section_path="Big",
            section_type="remediation",
            raw_text=blob,
            source_file="big.md",
        )
    ]
    chunks = chunk_sections(sections)
    assert len(chunks) > 1
    for c in chunks:
        assert len(enc.encode(c.text)) <= _TARGET_MAX + 50
    # Sequence is monotonically increasing from 1.
    assert [c.chunk_seq for c in chunks] == list(range(1, len(chunks) + 1))


def test_fixture_sop_produces_multiple_chunks():
    """50-page equivalent proxy — concatenate both fixture SOPs x5."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "fixtures" / "sops"
    big = ""
    for f in sorted(root.glob("*.md")):
        big += f.read_text() * 5
    sections = [
        ParsedSection(
            section_path="Concat",
            section_type="overview",
            raw_text=big,
            source_file="concat.md",
        )
    ]
    chunks = chunk_sections(sections)
    assert len(chunks) >= 5
