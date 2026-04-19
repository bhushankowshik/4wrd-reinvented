"""Backwards-compat shim — use `harness.sidecar.detector` directly.

The old `harness.sidecar_integration` module was a flat two-function
surface. The full Sidecar now lives in the `harness.sidecar` package;
this shim keeps old imports working and delegates to the package.
"""
from harness.sidecar.detector import (
    BoundaryScanResult,
    SidecarDecision,
    inspect_adversarial_output,
    run_session_boundary_scan,
)

__all__ = [
    "BoundaryScanResult",
    "SidecarDecision",
    "inspect_adversarial_output",
    "run_session_boundary_scan",
]
