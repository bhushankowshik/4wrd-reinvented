"""Mock CTTS — stands in for the real client ticketing
system during Docker Compose development. Stores incidents
in-memory, exposes an unresolved queue, accepts write-backs
with correlation-token idempotency.
"""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from prometheus_client import make_asgi_app
from pydantic import BaseModel


app = FastAPI(title="mock-ctts")
app.mount("/metrics", make_asgi_app())


class MockIncident(BaseModel):
    ctts_incident_ref: str
    ctts_received_at: datetime
    affected_nodes: list[dict]
    symptom_text: str
    severity: str
    customer_hint: str | None = None
    reporting_source: str | None = None
    correlation_hints: dict | None = None
    state_marker: str = "pending"


class WriteBack(BaseModel):
    correlation_token: UUID
    decision_kind: str
    reason_code: str | None = None
    override_action_class: str | None = None
    pseudonymous_operator_id: str
    decision_at: datetime


_lock = threading.Lock()
_incidents: dict[str, MockIncident] = {}
_writebacks: dict[UUID, WriteBack] = {}


# Seed a few fixture incidents on startup — so intake has
# something to poll immediately.
def _seed() -> None:
    seeds = [
        MockIncident(
            ctts_incident_ref="CTTS-ALPHA-0001",
            ctts_received_at=datetime.now(timezone.utc),
            affected_nodes=[{"node_id": "BTS-447", "site": "SG-NORTH"}],
            symptom_text=(
                "Node BTS-447 reporting intermittent packet loss on interface "
                "eth0, severity P2, affecting 3 customers in zone SG-NORTH"
            ),
            severity="P2",
            customer_hint="ENT-0042",
            reporting_source="network-monitoring",
        ),
        MockIncident(
            ctts_incident_ref="CTTS-ALPHA-0002",
            ctts_received_at=datetime.now(timezone.utc),
            affected_nodes=[
                {"node_id": "MSC-12", "site": "SG-EAST"},
                {"node_id": "MSC-13", "site": "SG-EAST"},
            ],
            symptom_text=(
                "MSC-12 and MSC-13 showing elevated call drop rate (>2%) "
                "beginning at 14:03 local; voice quality alarms raised."
            ),
            severity="P1",
            customer_hint=None,
            reporting_source="oss-alarm",
        ),
        MockIncident(
            ctts_incident_ref="CTTS-ALPHA-0003",
            ctts_received_at=datetime.now(timezone.utc),
            affected_nodes=[{"node_id": "OLT-SG-07", "site": "SG-WEST"}],
            symptom_text=(
                "OLT-SG-07 link down on uplink port 3; ONTs on sub-ring lost "
                "service. Previous similar outage resolved by firmware reset."
            ),
            severity="P2",
            customer_hint="SME-0117",
            reporting_source="manual",
        ),
    ]
    with _lock:
        for m in seeds:
            _incidents.setdefault(m.ctts_incident_ref, m)


_seed()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "incidents": str(len(_incidents))}


@app.get("/incidents/unresolved")
def unresolved() -> list[MockIncident]:
    with _lock:
        return [i for i in _incidents.values() if i.state_marker == "pending"]


@app.post("/incidents/{ref}/advance")
def advance(ref: str) -> dict[str, str]:
    with _lock:
        inc = _incidents.get(ref)
        if not inc:
            raise HTTPException(404, "unknown ref")
        inc.state_marker = "in_progress"
    return {"status": "advanced"}


@app.post("/writeback")
def writeback(wb: WriteBack) -> dict[str, Any]:
    with _lock:
        if wb.correlation_token in _writebacks:
            return {"status": "duplicate", "correlation_token": str(wb.correlation_token)}
        _writebacks[wb.correlation_token] = wb
    return {"status": "accepted", "correlation_token": str(wb.correlation_token)}


@app.get("/writebacks")
def list_writebacks() -> list[WriteBack]:
    with _lock:
        return list(_writebacks.values())


# Dev-only helper: post a new malformed incident to exercise
# the validation_failure path in intake.
class PostIncidentIn(BaseModel):
    payload: dict


@app.post("/admin/post_incident")
def post_incident(req: PostIncidentIn) -> dict[str, Any]:
    ref = req.payload.get("ctts_incident_ref", f"CTTS-GEN-{uuid4().hex[:8]}")
    try:
        inc = MockIncident(**{**req.payload, "ctts_incident_ref": ref,
                              "ctts_received_at": datetime.now(timezone.utc)})
        ok = True
    except Exception as exc:  # noqa: BLE001
        return {"status": "rejected_by_mock_ctts", "error": str(exc)}
    with _lock:
        _incidents[ref] = inc
    return {"status": "accepted", "ref": ref, "ok": ok}
