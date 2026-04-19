"""Theory Retirement — tombstone a superseded cycle / artefact.

Per INPUT-001 §8, nothing on the chain is silently removed. When a
cycle is retired, we write a `tombstone` chain entry that names the
target cycle_id / artefact_path, the reason, and the successor (if
any). The tombstone is permanent — it does not delete the original
chain rows; it annotates them.

Three surfaces:

  tombstone    — emit a `tombstone` chain entry
  registry     — Layer 2 list of active tombstones
  cli          — `harness retire --cycle-id ... --reason ... [--successor ...]`
"""
from harness.retirement.registry import (
    RetirementRecord,
    list_retirements,
)
from harness.retirement.tombstone import (
    TombstoneResult,
    emit_tombstone,
)

__all__ = [
    "RetirementRecord",
    "TombstoneResult",
    "emit_tombstone",
    "list_retirements",
]
