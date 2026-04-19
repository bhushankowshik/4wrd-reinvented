"""Context package builder unit tests — Explorative requires knowledge,
renderers include the expected fields, builder returns the right shape.

DB access is patched so these tests do not need noc-gov running.
"""
from __future__ import annotations

import pytest

from harness.context_package import (
    PriorEntrySummary,
    build_challenge_package,
    build_producing_package,
)


@pytest.fixture()
def no_db_prior(monkeypatch):
    from harness import context_package as cp
    monkeypatch.setattr(
        cp, "_fetch_prior_entries",
        lambda *, skill_id, max_prior_entries: [],
    )


def test_build_producing_package_explorative_requires_knowledge(no_db_prior):
    with pytest.raises(ValueError):
        build_producing_package(
            skill_id="S1",
            convergence_state="Explorative",
            direction="Hello",
            knowledge_contribution=None,
        )


def test_build_producing_package_renders_direction_and_knowledge(no_db_prior):
    pkg = build_producing_package(
        skill_id="S1",
        convergence_state="Explorative",
        direction="Crystallise the problem.",
        knowledge_contribution="Context: X, Y, Z.",
        primary_derivation_intent=["INPUT-001", "docs/s4-exit-artefact.md"],
    )
    txt = pkg.render()
    assert "Skill: S1" in txt
    assert "Explorative" in txt
    assert "Crystallise the problem." in txt
    assert "Context: X, Y, Z." in txt
    assert "INPUT-001" in txt
    assert "docs/s4-exit-artefact.md" in txt
    assert "Produce now" in txt


def test_build_producing_package_includes_prior_entries(monkeypatch):
    from harness import context_package as cp

    prior = [
        PriorEntrySummary(
            chain_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            entry_type="direction_capture",
            actor_id="human",
            timestamp="2026-04-19T09:00:00+00:00",
            summary="previous direction",
        ),
    ]
    monkeypatch.setattr(
        cp, "_fetch_prior_entries",
        lambda *, skill_id, max_prior_entries: prior,
    )
    pkg = build_producing_package(
        skill_id="S1",
        convergence_state="Targeted",
        direction="Sharpen.",
        knowledge_contribution=None,
    )
    assert len(pkg.prior_entries) == 1
    rendered = pkg.render()
    assert "direction_capture by human" in rendered
    assert "previous direction" in rendered


def test_build_challenge_package_is_narrow():
    pkg = build_challenge_package(
        skill_id="S1",
        convergence_state="Explorative",
        direction="Do the thing.",
        producing_output="OUTPUT BODY",
        reasoning_trace="1. because",
    )
    txt = pkg.render()
    assert "Do the thing." in txt
    assert "OUTPUT BODY" in txt
    assert "1. because" in txt
    # No knowledge contribution, no prior entries — kept narrow.
    assert "Knowledge contribution" not in txt
    assert "Prior chain entries" not in txt
