"""Frame Change Sidecar integration — always-live alongside cycles.

Two paths per INPUT-001 §2.3:

1. **Session boundary scan** — at session start we reconstruct the
   shape of the last N chain entries and expose it to the
   orchestrator so the new direction can be compared against
   session context. Drift signals a potential frame invalidation
   before Moment 1 even runs.

2. **Secondary Sidecar Detector** — the Adversarial Agent's
   FRAME_CHANGE-axis challenges. `inspect_adversarial_output`
   reads the AdversarialOutput, and if any CRITICAL FRAME_CHANGE
   challenge is raised, we emit a `frame_change_detected` chain
   entry and return a decision for the orchestrator to pause the
   cycle and request new direction.

Both paths converge on `mvghb.sidecar.emit_frame_change` which is
the Wave 1 write surface for frame-change records.
"""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mvghb.sidecar import (
    SessionContext,
    detect_session_boundary,
    emit_frame_change,
)

from harness.agents.adversarial_agent import AdversarialOutput


@dataclass(frozen=True)
class BoundaryScanResult:
    context: SessionContext
    prior_entry_count: int
    likely_drift: bool
    drift_reason: str | None


@dataclass(frozen=True)
class SidecarDecision:
    """Outcome of running the sidecar against an adversarial output."""
    frame_change: bool
    reason: str | None
    chain_id: UUID | None


def run_session_boundary_scan(
    *,
    new_direction: str,
    window: int = 25,
) -> BoundaryScanResult:
    """Scan the last N chain entries and flag likely drift vs new direction.

    Drift heuristic (Wave 1): if the new direction names no topic
    present in the last N entries AND there are prior entries, we mark
    `likely_drift=True` so the orchestrator can ask the human whether
    to continue. Concrete quorum/mandatory-pause semantics are
    deferred to Wave 2 (AG9d activation).
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
    receptor: str = "adversarial_ai",
) -> SidecarDecision:
    """Map an AdversarialOutput to a SidecarDecision.

    If any CRITICAL FRAME_CHANGE challenge is present, write a
    `frame_change_detected` entry and signal the orchestrator to pause.
    """
    if not adv.frame_change_detected:
        return SidecarDecision(frame_change=False, reason=None, chain_id=None)

    # Compose the signal from the CRITICAL frame-change challenges.
    critical_frame = [
        c for c in adv.challenges
        if c.axis == "FRAME_CHANGE" and c.severity == "CRITICAL"
    ]
    signal = "; ".join(c.challenge for c in critical_frame)

    chain_id = emit_frame_change(
        receptor=receptor,  # type: ignore[arg-type]
        signal=signal,
    )
    return SidecarDecision(
        frame_change=True,
        reason=signal,
        chain_id=chain_id,
    )
