"""External sidecar receptor — the six sources + frame_change_signal."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from harness.sidecar.receptor import (
    EXTERNAL_RECEPTORS,
    emit_frame_change_signal,
)


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


def test_six_receptors_are_registered():
    assert set(EXTERNAL_RECEPTORS) == {
        "upstream_contract",
        "regulatory",
        "ops_incident",
        "market",
        "research",
        "stakeholder",
    }


def test_emit_frame_change_signal_writes_entry():
    writer = FakeWriter()
    result = emit_frame_change_signal(
        receptor="regulatory",
        signal="MAS Notice 656 — repaper all TRM skills",
        skill_id="S3",
        evidence_ref="https://www.mas.gov.sg/notices/656",
        writer=writer,
    )
    assert len(writer.emitted) == 1
    emitted = writer.emitted[0]
    assert emitted["entry_type"] == "frame_change_signal"
    payload = emitted["payload"]
    assert payload["receptor"] == "regulatory"
    assert payload["evidence_ref"] == "https://www.mas.gov.sg/notices/656"
    assert payload["skill_id"] == "S3"
    assert result.receptor == "regulatory"


def test_unknown_receptor_rejected():
    writer = FakeWriter()
    with pytest.raises(ValueError):
        emit_frame_change_signal(
            receptor="weather",  # type: ignore[arg-type]
            signal="stormy",
            writer=writer,
        )


def test_empty_signal_rejected():
    writer = FakeWriter()
    with pytest.raises(ValueError):
        emit_frame_change_signal(
            receptor="regulatory", signal="  ", writer=writer,
        )
