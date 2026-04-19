"""Artefact Lineage — primary / incidental ref extraction + backwards query.

Chain entry type: `artefact_lineage`. Emitted at Moment 4 alongside
`cycle_close` so the chain carries the structured lineage AS DATA,
not only inside the artefact markdown.

Two categories (INPUT-001 §6.3):

  primary     — named in Moment 1 primary_derivation_intent
  incidental  — referenced inside produced output / reasoning /
                challenges but NOT in the Moment 1 declaration

Both are extracted via regex: file paths, URLs, chain_ids.
"""
from harness.lineage.tracker import (
    ArtefactLineage,
    LineageEntry,
    emit_artefact_lineage,
    extract_lineage,
)
from harness.lineage.query import (
    LineageWalk,
    walk_backwards,
)

__all__ = [
    "ArtefactLineage",
    "LineageEntry",
    "LineageWalk",
    "emit_artefact_lineage",
    "extract_lineage",
    "walk_backwards",
]
