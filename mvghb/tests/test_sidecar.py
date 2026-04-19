"""Sidecar tests — challenge rendering is pure, no DB."""
from __future__ import annotations

from datetime import datetime, timezone

from mvghb.sidecar import render_challenge


def test_render_challenge_includes_receptor_and_signal():
    ch = render_challenge(
        receptor="adversarial_ai",
        signal="primary_derivation_intent_drift",
        issued_at=datetime(2026, 4, 19, 10, 0, 0, tzinfo=timezone.utc),
    )
    assert "adversarial_ai" in ch.prompt
    assert "primary_derivation_intent_drift" in ch.prompt
    assert "2026-04-19T10:00:00" in ch.prompt
    assert "Primary Derivation Intent" in ch.prompt
    assert "SEAM-1..5" in ch.prompt


def test_render_challenge_blocks_other_receptors_at_type_level():
    """Receptor literal type bounds the field; runtime accepts the three valid sources."""
    for receptor in ("human", "producing_ai", "adversarial_ai"):
        ch = render_challenge(receptor=receptor, signal="x")  # type: ignore[arg-type]
        assert receptor in ch.prompt
