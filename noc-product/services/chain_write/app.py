"""HTTP surface for Chain-Write stub.

Exposed for services that call it over HTTP (reviewer-ui,
intake, agents, write-back). Services may also import
`ChainWriter` directly — both paths share the same object.
"""
from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from fastapi import FastAPI, HTTPException
from prometheus_client import make_asgi_app
from pydantic import BaseModel, Field

from services.chain_write.allowlist import UnknownEntryTypeError, load_allowlist
from services.chain_write.writer import ChainWriter
from services.common.telemetry import configure_logging, log


configure_logging()
_writer = ChainWriter()
load_allowlist()  # fail-fast at startup

app = FastAPI(title="chain-write stub")
app.mount("/metrics", make_asgi_app())


class EmitRequest(BaseModel):
    entry_type: str
    actor_id: str
    actor_role: str
    incident_id: UUID | None = None
    payload_ref: dict[str, Any]
    sop_versions_pinned: list[dict[str, Any]] | None = None
    class_enum: Literal["NORMAL", "OVERRIDE"] = "NORMAL"
    prev_chain_id: UUID | None = None


class EmitResponse(BaseModel):
    chain_id: UUID
    committed: bool
    wal_path: str
    timestamp: str
    hmac_signature_hex: str
    content_hash_hex: str


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "allowlist_size": str(len(load_allowlist()))}


@app.post("/emit", response_model=EmitResponse)
def emit(req: EmitRequest) -> EmitResponse:
    try:
        result = _writer.emit(
            entry_type=req.entry_type,
            actor_id=req.actor_id,
            actor_role=req.actor_role,
            incident_id=req.incident_id,
            payload_ref=req.payload_ref,
            sop_versions_pinned=req.sop_versions_pinned,
            class_enum=req.class_enum,
            prev_chain_id=req.prev_chain_id,
        )
    except UnknownEntryTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return EmitResponse(
        chain_id=result.chain_id,
        committed=result.committed,
        wal_path=result.wal_path,
        timestamp=result.timestamp.isoformat(),
        hmac_signature_hex=result.hmac_signature.hex(),
        content_hash_hex=result.content_hash.hex(),
    )
