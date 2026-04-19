"""Layer 2 derived view tests — with injected fetchers."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from harness.layer2.views import (
    ChainEntryRow,
    operator_view,
    session_replay_view,
)


T0 = datetime(2026, 4, 1, tzinfo=timezone.utc)


def _row(*, entry_type, actor, cycle, skill, payload=None, offset=0):
    base = {"cycle_id": cycle, "skill_id": skill}
    if payload:
        base.update(payload)
    return ChainEntryRow(
        chain_id=f"{entry_type}-{cycle}-{offset}",
        entry_type=entry_type,
        actor_id=actor,
        timestamp=T0 + timedelta(minutes=offset),
        payload_ref=base,
    )


def _make_cycle(*, skill, cycle, outcome, exit_state, start_min=0):
    """One full cycle's worth of rows."""
    return [
        _row(entry_type="direction_capture", actor="human", cycle=cycle,
             skill=skill, payload={"direction": "go", "convergence_state": "Targeted"},
             offset=start_min),
        _row(entry_type="production", actor="producing_agent", cycle=cycle,
             skill=skill, payload={"output_excerpt": "body", "iteration": 1},
             offset=start_min + 1),
        _row(entry_type="adversarial_challenge", actor="adversarial_agent",
             cycle=cycle, skill=skill,
             payload={"challenges": [{"axis": "X", "severity": "MINOR"}]},
             offset=start_min + 2),
        _row(entry_type="verification", actor="human", cycle=cycle, skill=skill,
             payload={"verification_outcome": outcome}, offset=start_min + 3),
        _row(entry_type="cycle_close", actor="orchestrator", cycle=cycle,
             skill=skill,
             payload={
                 "convergence_state_at_exit": exit_state,
                 "artefact_path": f"docs/{cycle}.md",
             },
             offset=start_min + 4),
    ]


def test_operator_view_orders_cycles_newest_first():
    rows = []
    rows += _make_cycle(skill="S1", cycle="c1", outcome="CONFIRMED",
                        exit_state="Exact", start_min=0)
    rows += _make_cycle(skill="S1", cycle="c2", outcome="CONFIRMED",
                        exit_state="Exact", start_min=100)

    def fetcher(**kwargs):
        return rows

    view = operator_view(skill_id="S1", fetcher=fetcher)
    assert [c.cycle_id for c in view.cycles] == ["c2", "c1"]
    assert view.cycles[0].closed_at_exact is True
    assert view.cycles[0].verification_outcome == "CONFIRMED"
    assert view.cycles[0].output_excerpt == "body"


def test_operator_view_last_n_cap():
    rows = []
    for i in range(5):
        rows += _make_cycle(
            skill="S1", cycle=f"c{i}", outcome="CONFIRMED",
            exit_state="Exact", start_min=i * 10,
        )

    def fetcher(**kwargs):
        return rows

    view = operator_view(skill_id="S1", last_n_cycles=3, fetcher=fetcher)
    assert len(view.cycles) == 3


def test_session_replay_one_frame_per_skill_unresolved_partial():
    rows = []
    # S1 — one PARTIAL at Targeted.
    rows += _make_cycle(skill="S1", cycle="c1", outcome="PARTIAL",
                        exit_state="Targeted", start_min=0)
    # S2 — one CONFIRMED at Exact.
    rows += _make_cycle(skill="S2", cycle="c2", outcome="CONFIRMED",
                        exit_state="Exact", start_min=50)

    def fetcher(**kwargs):
        return rows

    view = session_replay_view(fetcher=fetcher)
    frames = {f.skill_id: f for f in view.skill_frames}
    assert set(frames) == {"S1", "S2"}

    s1 = frames["S1"]
    assert s1.last_outcome == "PARTIAL"
    assert s1.last_closed_at_exact is False
    assert s1.unresolved_partial is True
    assert s1.last_artefact_path == "docs/c1.md"

    s2 = frames["S2"]
    assert s2.last_outcome == "CONFIRMED"
    assert s2.last_closed_at_exact is True
    assert s2.unresolved_partial is False


def test_session_replay_render_markdown():
    rows = _make_cycle(skill="S1", cycle="c1", outcome="CONFIRMED",
                       exit_state="Exact")
    view = session_replay_view(fetcher=lambda **kw: rows)
    md = view.render()
    assert "Session replay" in md
    assert "S1" in md
    assert "closed at Exact: yes" in md
