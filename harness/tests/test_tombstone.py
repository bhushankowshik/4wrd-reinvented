"""Tombstone round-trip — emit + list."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from harness.retirement.registry import list_retirements
from harness.retirement.tombstone import emit_tombstone


class FakeEmit:
    def __init__(self) -> None:
        self.chain_id = uuid4()
        self.timestamp = datetime.now(timezone.utc)


class FakeWriter:
    def __init__(self) -> None:
        self.emitted: list[dict] = []

    def emit(self, *, entry_type, actor_id, actor_role, incident_id,
             payload_ref, sop_versions_pinned=None,
             class_enum="NORMAL", prev_chain_id=None):
        self.emitted.append(
            {"entry_type": entry_type, "actor_id": actor_id,
             "payload": payload_ref}
        )
        return FakeEmit()


def test_emit_tombstone_writes_chain_entry():
    writer = FakeWriter()
    cycle_id = uuid4()
    result = emit_tombstone(
        cycle_id=cycle_id,
        reason="Replaced by c-2 after MAS Notice 656",
        skill_id="S3",
        successor_cycle_id=uuid4(),
        writer=writer,
    )
    assert len(writer.emitted) == 1
    emitted = writer.emitted[0]
    assert emitted["entry_type"] == "tombstone"
    assert emitted["payload"]["cycle_id"] == str(cycle_id)
    assert emitted["payload"]["skill_id"] == "S3"
    assert "successor_cycle_id" in emitted["payload"]
    assert result.reason == "Replaced by c-2 after MAS Notice 656"


def test_list_retirements_parses_fetcher_rows():
    now = datetime.now(timezone.utc)

    def fetcher():
        return [
            {
                "chain_id": "abc",
                "timestamp": now,
                "payload_ref": {
                    "cycle_id": "c-1",
                    "skill_id": "S1",
                    "reason": "superseded",
                    "retired_by": "human",
                    "successor_cycle_id": "c-2",
                    "artefact_path": "docs/c-1.md",
                },
            }
        ]

    records = list_retirements(fetcher=fetcher)
    assert len(records) == 1
    r = records[0]
    assert r.cycle_id == "c-1"
    assert r.skill_id == "S1"
    assert r.successor_cycle_id == "c-2"
    assert r.artefact_path == "docs/c-1.md"


def test_tombstone_requires_non_empty_reason():
    import pytest
    writer = FakeWriter()
    with pytest.raises(ValueError):
        emit_tombstone(cycle_id=uuid4(), reason="  ", writer=writer)
