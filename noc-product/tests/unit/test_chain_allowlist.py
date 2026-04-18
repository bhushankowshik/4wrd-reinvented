"""M10 — AG-3 entry_type allowlist gate (E3 §4.2)."""
from __future__ import annotations

import pytest

from services.chain_write.allowlist import (
    UnknownEntryTypeError,
    assert_known,
    load_allowlist,
)


EXPECTED_CORE = {
    "intake",
    "ticket_rejected_malformed",
    "agent_output",
    "recommendation",
    "operator_decision",
    "unavailable",
    "sop_reference",
    "validation_failure",
    "ctts_writeback_outcome",
    "sop_ingest_run_start",
    "sop_version_activate",
    "sop_version_deprecate",
    "identity_map_access",
}


def test_allowlist_contains_canonical_types():
    allowed = load_allowlist()
    missing = EXPECTED_CORE - allowed
    assert not missing, f"missing entry types: {missing}"


def test_assert_known_passes_for_known_types():
    for t in EXPECTED_CORE:
        assert_known(t)  # no raise


def test_assert_known_rejects_unknown_type():
    with pytest.raises(UnknownEntryTypeError):
        assert_known("not_a_real_entry_type")


def test_identity_issuance_allowed():
    # Added in M8 — operator_identity_map row creation.
    assert_known("identity_issuance")
