"""Frame Change Sidecar — always-live companion to the Intent Cycle.

Three paths per INPUT-001 §2.3 / §5 Sidecar:

  1. Session boundary scan  — run at session start to spot drift
     between new direction and recent chain shape.
  2. In-session Tier 2 detector — wraps mvghb's adversarial
     FRAME_CHANGE detector and writes `frame_change_detected`.
  3. External receptor         — six canonical sources that can
     inject `frame_change_signal` entries into the chain out of
     band (e.g. a stakeholder email, a regulator notice, a
     production incident). CLI: `harness sidecar signal ...`.

The chain carries two separate entry types so Layer 2 can tell
in-session vs out-of-band frame-change signals apart:

  frame_change_detected   — in-session / Tier 2 / adversarial AI
  frame_change_signal     — external receptor / out-of-band
"""
from harness.sidecar.detector import (
    BoundaryScanResult,
    SidecarDecision,
    Tier2Receptor,
    emit_frame_change_detected,
    inspect_adversarial_output,
    run_session_boundary_scan,
)
from harness.sidecar.receptor import (
    EXTERNAL_RECEPTORS,
    ExternalReceptor,
    ExternalSignalResult,
    emit_frame_change_signal,
    sidecar_group,
)

__all__ = [
    "BoundaryScanResult",
    "EXTERNAL_RECEPTORS",
    "ExternalReceptor",
    "ExternalSignalResult",
    "SidecarDecision",
    "Tier2Receptor",
    "emit_frame_change_detected",
    "emit_frame_change_signal",
    "inspect_adversarial_output",
    "run_session_boundary_scan",
    "sidecar_group",
]
