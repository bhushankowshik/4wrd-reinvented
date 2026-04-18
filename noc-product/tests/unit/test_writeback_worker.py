"""M8 — write-back worker unit tests (idempotency + failure handling)."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import httpx
import pytest

from services.write_back import worker as wb


def _decision() -> dict:
    return {
        "decision_id": uuid4(),
        "decision_at": datetime.now(timezone.utc),
        "incident_id": uuid4(),
        "recommendation_id": uuid4(),
        "decision_kind": "approved",
        "reason_code": None,
        "override_action_class": None,
        "pseudonymous_operator_id": "pseudo-test-001",
        "correlation_token": uuid4(),
        "ctts_writeback_state": "pending",
        "ctts_incident_ref": "CTTS-TEST-0001",
    }


def test_post_to_ctts_builds_expected_body():
    dec = _decision()
    with patch.object(wb.httpx, "post") as m:
        m.return_value = MagicMock(
            status_code=200, json=lambda: {"status": "accepted"}
        )
        m.return_value.raise_for_status = lambda: None
        out = wb._post_to_ctts(dec)
        assert out == {"status": "accepted"}
        call_body = m.call_args.kwargs["json"]
        assert call_body["correlation_token"] == str(dec["correlation_token"])
        assert call_body["decision_kind"] == "approved"
        assert call_body["pseudonymous_operator_id"] == "pseudo-test-001"


def test_process_one_records_ok_on_success():
    dec = _decision()
    chain = MagicMock()

    with (
        patch.object(wb, "_post_to_ctts", return_value={"status": "accepted"}),
        patch.object(wb, "_update_state") as upd,
    ):
        wb._process_one(dec, chain)

    upd.assert_called_once()
    _, args, kwargs = upd.mock_calls[0]
    # _update_state(decision_id, decision_at, state, outcome_detail)
    assert args[2] == "ok"
    chain.emit.assert_called_once()
    assert (
        chain.emit.call_args.kwargs["entry_type"] == "ctts_writeback_outcome"
    )


def test_process_one_bumps_failure_on_http_error():
    dec = _decision()
    chain = MagicMock()
    wb._attempt_map.clear()

    def fail(*_a, **_k):
        raise httpx.ConnectError("boom")

    with (
        patch.object(wb, "_post_to_ctts", side_effect=fail),
        patch.object(wb, "_update_state") as upd,
    ):
        wb._process_one(dec, chain)

    # Once attempt is counted in the map.
    assert wb._attempt_map[str(dec["decision_id"])] == 1
    # State must be 'retrying' (not yet terminal).
    assert upd.call_args.args[2] == "retrying"


def test_process_one_terminal_after_max_attempts():
    dec = _decision()
    chain = MagicMock()
    wb._attempt_map.clear()
    wb._attempt_map[str(dec["decision_id"])] = wb.MAX_ATTEMPTS_BEFORE_FAIL - 1

    with (
        patch.object(wb, "_post_to_ctts", side_effect=httpx.ConnectError("x")),
        patch.object(wb, "_update_state") as upd,
    ):
        wb._process_one(dec, chain)

    assert upd.call_args.args[2] == "failed"
