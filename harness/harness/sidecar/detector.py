"""Tier 2 Frame Change Detector — extends `mvghb.sidecar` with harness
context and a richer boundary scan.

Wave 1 surfaces we keep:

  SessionContext, detect_session_boundary  — `mvghb.sidecar`
  emit_frame_change                         — `mvghb.sidecar`

What this module adds on top:

  BoundaryScanResult  — bundles the mvghb context with a drift flag
                         and the reasoning so the caller can log it.
  SidecarDecision     — outcome of running the detector against an
                         AdversarialOutput; carries `chain_id` when
                         a `frame_change_detected` entry is written.
  Tier2Receptor       — bounded to the INPUT-001 §5 Sidecar trio:
                         human, producing_ai, adversarial_ai.

The canonical external-receptor path (six sources) lives in
`harness.sidecar.receptor` and writes `frame_change_signal` entries
— not `frame_change_detected`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from mvghb.sidecar import (
    SessionContext,
    detect_session_boundary,
    emit_frame_change,
)

from harness.agents.adversarial_agent import AdversarialOutput


Tier2Receptor = Literal["human", "producing_ai", "adversarial_ai"]


@dataclass(frozen=True)
class BoundaryScanResult:
    """Output of `run_session_boundary_scan`."""
    context: SessionContext
    prior_entry_count: int
    likely_drift: bool
    drift_reason: str | None


@dataclass(frozen=True)
class SidecarDecision:
    """Outcome of the Tier 2 detector vs an AdversarialOutput."""
    frame_change: bool
    reason: str | None
    chain_id: UUID | None


def run_session_boundary_scan(
    *,
    new_direction: str,
    window: int = 25,
) -> BoundaryScanResult:
    """Scan the last N chain entries and flag likely drift.

    Drift heuristic (Wave 1): the new direction shares no payload
    topic with the last N entries AND there were prior entries. This
    surfaces a soft signal to the orchestrator — the human retains
    override; mandatory pause / quorum is deferred to Wave 2.
    """
    ctx = detect_session_boundary(window=window)
    prior_count = ctx.last_n_entries
    drift = False
    reason: str | None = None

    if prior_count > 0 and ctx.payload_topics:
        direction_lower = new_direction.lower()
        overlap = any(
            topic.lower() in direction_lower for topic in ctx.payload_topics
        )
        if not overlap:
            drift = True
            reason = (
                f"new direction shares no payload topic with the last "
                f"{prior_count} chain entries (topics sampled: "
                f"{ctx.payload_topics[:5]})"
            )

    return BoundaryScanResult(
        context=ctx,
        prior_entry_count=prior_count,
        likely_drift=drift,
        drift_reason=reason,
    )


def inspect_adversarial_output(
    adv: AdversarialOutput,
    *,
    receptor: Tier2Receptor = "adversarial_ai",
) -> SidecarDecision:
    """Run the Tier 2 detector against an AdversarialOutput.

    If any CRITICAL FRAME_CHANGE challenge is present, write a
    `frame_change_detected` entry and return the new chain_id.
    """
    if not adv.frame_change_detected:
        return SidecarDecision(frame_change=False, reason=None, chain_id=None)

    critical_frame = [
        c for c in adv.challenges
        if c.axis == "FRAME_CHANGE" and c.severity == "CRITICAL"
    ]
    signal = "; ".join(c.challenge for c in critical_frame)

    chain_id = emit_frame_change(receptor=receptor, signal=signal)
    return SidecarDecision(
        frame_change=True, reason=signal, chain_id=chain_id,
    )


def emit_frame_change_detected(
    *, receptor: Tier2Receptor, signal: str,
) -> UUID:
    """Write a Tier 2 `frame_change_detected` entry directly.

    Thin wrapper around `mvghb.sidecar.emit_frame_change` — provided
    for symmetry with the external `emit_frame_change_signal` path so
    callers can reach both from one import.
    """
    return emit_frame_change(receptor=receptor, signal=signal)
