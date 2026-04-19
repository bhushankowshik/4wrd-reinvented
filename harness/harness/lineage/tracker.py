"""Artefact Lineage tracker — extract + emit `artefact_lineage`.

At Moment 4, the orchestrator writes a structured lineage entry that
lists both the primary refs (declared in Moment 1) and the incidental
refs (discovered inside the produced output, reasoning trace, and
adversarial challenges). Layer 2 can then answer "what artefacts led
to this artefact?" without parsing markdown at query time.

Regex surfaces:

  file paths  — POSIX paths under project root, optionally with
                 line ranges (e.g. `src/foo.py:42`)
  URLs        — http / https
  chain ids   — 8-4-4-4-12 hex UUIDs (links to other chain entries)
  cycle ids   — same shape but namespaced by the caller when known
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable
from uuid import UUID

from mvghb.chain_write.writer import ChainEmitResult, ChainWriter


# Path heuristic: starts with a letter / `_` / `.`, contains at
# least one `/`, with typical source file extensions.
_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_/])"
    r"([a-zA-Z_.][\w./-]*?"
    r"\.(?:py|md|json|yaml|yml|toml|sql|rs|go|ts|tsx|js|jsx|proto|sh))"
    r"(?:[:\s]|$)"
)
_URL_RE = re.compile(r"https?://[^\s)>\]]+")
_UUID_RE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class LineageEntry:
    """One extracted reference."""
    ref: str
    kind: str  # "file" | "url" | "chain_id"


@dataclass(frozen=True)
class ArtefactLineage:
    """Composite lineage for one cycle."""
    cycle_id: str
    skill_id: str
    primary: list[LineageEntry] = field(default_factory=list)
    incidental: list[LineageEntry] = field(default_factory=list)

    def all_refs(self) -> list[str]:
        return [e.ref for e in self.primary] + [e.ref for e in self.incidental]

    def to_payload(self) -> dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "skill_id": self.skill_id,
            "primary": [
                {"ref": e.ref, "kind": e.kind} for e in self.primary
            ],
            "incidental": [
                {"ref": e.ref, "kind": e.kind} for e in self.incidental
            ],
            "counts": {
                "primary": len(self.primary),
                "incidental": len(self.incidental),
            },
        }


def _scan(text: str) -> list[LineageEntry]:
    found: list[LineageEntry] = []
    seen: set[str] = set()

    def _add(ref: str, kind: str) -> None:
        key = f"{kind}:{ref}"
        if key in seen:
            return
        seen.add(key)
        found.append(LineageEntry(ref=ref, kind=kind))

    for m in _PATH_RE.finditer(text):
        _add(m.group(1), "file")
    for m in _URL_RE.finditer(text):
        # Strip trailing punctuation that regex greedy might have grabbed.
        ref = m.group(0).rstrip(".,;:)")
        _add(ref, "url")
    for m in _UUID_RE.finditer(text):
        _add(m.group(0).lower(), "chain_id")
    return found


def extract_lineage(
    *,
    cycle_id: UUID | str,
    skill_id: str,
    primary_derivation_intent: Iterable[str],
    output_text: str = "",
    reasoning_text: str = "",
    challenge_text: str = "",
) -> ArtefactLineage:
    """Extract primary + incidental lineage entries for a cycle.

    Primary: every non-empty entry in `primary_derivation_intent`,
    classified by shape (url vs file vs chain_id). Duplicates are
    preserved in declaration order.

    Incidental: refs scanned out of output_text / reasoning_text /
    challenge_text, minus anything already declared primary.
    """
    primary: list[LineageEntry] = []
    primary_refs: set[str] = set()
    for raw in primary_derivation_intent:
        ref = raw.strip()
        if not ref:
            continue
        kind = (
            "url" if ref.startswith(("http://", "https://"))
            else "chain_id" if _UUID_RE.fullmatch(ref)
            else "file"
        )
        if ref in primary_refs:
            continue
        primary_refs.add(ref)
        primary.append(LineageEntry(ref=ref, kind=kind))

    incidental: list[LineageEntry] = []
    for blob in (output_text, reasoning_text, challenge_text):
        if not blob:
            continue
        for entry in _scan(blob):
            if entry.ref in primary_refs:
                continue
            # de-dupe against already-added incidental
            if any(e.ref == entry.ref for e in incidental):
                continue
            incidental.append(entry)

    return ArtefactLineage(
        cycle_id=str(cycle_id),
        skill_id=skill_id,
        primary=primary,
        incidental=incidental,
    )


def emit_artefact_lineage(
    lineage: ArtefactLineage,
    *,
    actor_id: str = "orchestrator",
    actor_role: str = "orchestrator",
    writer: ChainWriter | None = None,
) -> ChainEmitResult:
    """Write the lineage as a single `artefact_lineage` chain entry."""
    writer = writer or ChainWriter()
    return writer.emit(
        entry_type="artefact_lineage",
        actor_id=actor_id,
        actor_role=actor_role,
        incident_id=None,
        payload_ref=lineage.to_payload(),
    )
