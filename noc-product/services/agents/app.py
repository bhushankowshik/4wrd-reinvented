"""Agents service HTTP surface.

POST /runs   — synchronously orchestrate agents for one
               incident row and return the produced
               RecommendationPayload. Intake worker calls this.
GET  /health — backend + DB probes.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import FastAPI, HTTPException
from prometheus_client import make_asgi_app
from pydantic import BaseModel
from sqlalchemy import text

from services.agents.orchestrator import Orchestrator
from services.agents.schemas import RecommendationPayload
from services.common.db import data_session
from services.common.settings import get_settings
from services.common.telemetry import configure_logging, log
from services.model_backend import get_model_backend


configure_logging()
_orchestrator: Orchestrator | None = None


@asynccontextmanager
async def _lifespan(app: FastAPI):  # noqa: ARG001
    global _orchestrator
    _orchestrator = Orchestrator()
    # Keep-alive daemon: pings Ollama every N seconds.
    task = asyncio.create_task(_keepalive_loop())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


async def _keepalive_loop() -> None:
    s = get_settings()
    backend = get_model_backend()
    interval = max(30, int(s.ollama_keepalive_sec))
    while True:
        try:
            health = backend.health()
            log.info("model_backend.keepalive", **health)
        except Exception as exc:  # noqa: BLE001
            log.warning("model_backend.keepalive_error", error=str(exc))
        await asyncio.sleep(interval)


app = FastAPI(title="agents", lifespan=_lifespan)
app.mount("/metrics", make_asgi_app())


class RunRequest(BaseModel):
    incident_id: UUID


@app.get("/healthz")
def healthz() -> dict[str, Any]:
    backend = get_model_backend()
    return {"status": "ok", "model_backend": backend.health()}


@app.post("/runs", response_model=RecommendationPayload)
def run_one(req: RunRequest) -> RecommendationPayload:
    assert _orchestrator is not None
    with data_session() as s:
        row = s.execute(
            text("""
                SELECT incident_id::text AS incident_id,
                       symptom_text, severity, affected_nodes,
                       customer_hint, correlation_hints,
                       symptom_embedding::text AS symptom_embedding
                FROM incident
                WHERE incident_id = :iid
                  AND intake_state = 'accepted'
                ORDER BY ingest_at DESC
                LIMIT 1
            """),
            {"iid": str(req.incident_id)},
        ).mappings().first()
    if not row:
        raise HTTPException(404, detail="incident not found")

    record: dict[str, Any] = dict(row)
    # pgvector text form: "[0.1,0.2,...]". Cheap parse.
    raw = record.pop("symptom_embedding", None)
    if raw and raw.startswith("["):
        record["symptom_embedding"] = [float(x) for x in raw.strip("[]").split(",") if x]
    else:
        record["symptom_embedding"] = []

    return _orchestrator.run(record)
