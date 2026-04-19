"""Wave 1 entry_type allowlist.

Reuses the noc-product allowlist set + adds harness-internal types
(genesis, master_anchor, frame_change_detected, integrity_check_result).

Loaded fresh on each ChainWriter init — fail-fast on unknown entry_type.
"""
from __future__ import annotations

from pathlib import Path
import yaml


class UnknownEntryTypeError(ValueError):
    pass


# Harness-internal entry types added on top of the noc-product allowlist.
#
# The first group is MVGH-β Wave 1 internals (chain bootstrap, anchoring,
# sidecar interrupts, integrity scans). The second group is the Claude
# Agent SDK governed Intent Cycle — the atomic unit per INPUT-001 §2.1:
#   Moment 1 direction_capture → Moment 2 production + adversarial_challenge
#   → Moment 3 verification → Moment 4 cycle_close.
HARNESS_ENTRY_TYPES: set[str] = {
    "genesis",
    "master_anchor",
    "frame_change_detected",
    "integrity_check_result",
    # Intent Cycle moments (governed delivery harness).
    "direction_capture",
    "production",
    "adversarial_challenge",
    "verification",
    "cycle_close",
    # Infrastructure additions (INPUT-001 §§2.3, 2.4, 8; INPUT-002 §3).
    "research",             # Research Agent (Haiku tier) fact-gathering.
    "frame_change_signal",  # External sidecar receptor (six-source).
    "artefact_lineage",     # Primary + incidental references at Moment 4.
    "tombstone",            # Theory retirement (§8 — silent removal prohibited).
}


def _load_noc_product_allowlist() -> set[str]:
    """Load entry types from noc-product/services/chain_write/allowlist.yaml.

    Single source of truth for product entry types — harness re-validates
    against the same set so a real ChainWriter accepts every emit the
    stub accepted.
    """
    here = Path(__file__).resolve()
    candidates = [
        here.parents[3] / "noc-product" / "services" / "chain_write" / "allowlist.yaml",
        Path("/Users/bhushan/projects/4wrd-reinvented/noc-product/services/chain_write/allowlist.yaml"),
    ]
    for path in candidates:
        if path.is_file():
            data = yaml.safe_load(path.read_text())
            return set(data.get("allowed_entry_types", []))
    return set()


_ALLOWED: set[str] | None = None


def get_allowed() -> set[str]:
    global _ALLOWED
    if _ALLOWED is None:
        _ALLOWED = _load_noc_product_allowlist() | HARNESS_ENTRY_TYPES
    return _ALLOWED


def assert_known(entry_type: str) -> None:
    if entry_type not in get_allowed():
        raise UnknownEntryTypeError(
            f"entry_type '{entry_type}' not in allowlist "
            f"(size={len(get_allowed())})"
        )


def reset_for_test() -> None:
    global _ALLOWED
    _ALLOWED = None
