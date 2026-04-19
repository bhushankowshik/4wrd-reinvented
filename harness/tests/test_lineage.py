"""Artefact lineage extraction + backwards-query tests."""
from __future__ import annotations

from datetime import datetime, timezone

from harness.lineage.query import walk_backwards
from harness.lineage.tracker import extract_lineage


def test_extract_lineage_splits_primary_and_incidental():
    lineage = extract_lineage(
        cycle_id="c-1",
        skill_id="S1",
        primary_derivation_intent=["docs/foundation/INPUT-001.md"],
        output_text=(
            "See src/foo.py and tests/test_foo.py for the fix. "
            "Reference https://example.com/rfc."
        ),
        reasoning_text=(
            "Lineage chain_id: abcdef12-3456-7890-abcd-ef1234567890"
        ),
        challenge_text="",
    )
    primary_refs = [e.ref for e in lineage.primary]
    incidental_refs = [e.ref for e in lineage.incidental]
    assert primary_refs == ["docs/foundation/INPUT-001.md"]
    assert "src/foo.py" in incidental_refs
    assert "tests/test_foo.py" in incidental_refs
    assert "https://example.com/rfc" in incidental_refs
    assert any(
        e.kind == "chain_id" and e.ref.startswith("abcdef12")
        for e in lineage.incidental
    )


def test_extract_lineage_dedupes_declared_primary_from_incidental():
    lineage = extract_lineage(
        cycle_id="c-1",
        skill_id="S1",
        primary_derivation_intent=["src/foo.py"],
        output_text="We reference src/foo.py in the output too.",
    )
    assert [e.ref for e in lineage.primary] == ["src/foo.py"]
    # Should not re-appear in incidental.
    assert all(e.ref != "src/foo.py" for e in lineage.incidental)


def test_walk_backwards_finds_cycles_depending_on_ref():
    now = datetime(2026, 4, 1, tzinfo=timezone.utc)

    def fetcher():
        return [
            {
                "chain_id": "a1",
                "timestamp": now,
                "payload_ref": {
                    "cycle_id": "c-1",
                    "skill_id": "S1",
                    "primary": [{"ref": "INPUT-001.md", "kind": "file"}],
                    "incidental": [{"ref": "src/foo.py", "kind": "file"}],
                },
            },
            {
                "chain_id": "a2",
                "timestamp": now,
                "payload_ref": {
                    "cycle_id": "c-2",
                    "skill_id": "S2",
                    "primary": [{"ref": "src/foo.py", "kind": "file"}],
                    "incidental": [],
                },
            },
        ]

    walk = walk_backwards(ref="src/foo.py", fetcher=fetcher)
    assert set(walk.cycle_ids()) == {"c-1", "c-2"}
    # c-2 names it primary; c-1 incidental.
    cats = {row.cycle_id: row.category for row in walk.rows}
    assert cats["c-2"] == "primary"
    assert cats["c-1"] == "incidental"


def test_walk_backwards_empty_when_no_hits():
    walk = walk_backwards(ref="not/there.md", fetcher=lambda: [])
    assert walk.rows == []
    assert "(no cycle" in walk.render()
