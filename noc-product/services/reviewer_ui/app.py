"""Reviewer UI — FastAPI + Jinja2 + HTMX.

Flow:
  1. /login/start  — OIDC Authorization Code + PKCE redirect
  2. /auth/callback — exchange code, resolve pseudonymous id
                      via identity-audit-api, issue session
  3. /queue         — list produced recommendations with no
                      operator_decision yet
  4. /recommendation/{id} — detail + approve / reject / override
  5. /admin/        — role-gated (admin|auditor) — OF-6.17 path gate

Session via signed cookie (sliding 8h, absolute 12h).
CSRF via double-submit cookie. HTMX is used opportunistically
for action forms so successful POSTs hx-swap the body with a
server-rendered redirect fragment.
"""
from __future__ import annotations

import json
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx
from fastapi import (
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Request,
    Response,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from prometheus_client import Counter, make_asgi_app
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware

from services.chain_write.client import ChainWriteClient
from services.common.canonical import content_hash
from services.common.db import data_session
from services.common.settings import get_settings
from services.common.telemetry import configure_logging, log
from services.reviewer_ui import oidc
from services.reviewer_ui.session import (
    clear_session,
    issue_session,
    read_session,
    refresh_session,
    verify_csrf,
)


configure_logging()

_templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(_templates_dir))

app = FastAPI(title="noc-reviewer-ui")
app.mount("/metrics", make_asgi_app())


DECISION_COUNTER = Counter(
    "noc_operator_decisions_total",
    "Operator decisions recorded",
    ["kind"],
)


# In-memory per-process PKCE / state store. In prod this is
# backed by Redis or similar; for E6a dev a restart just
# invalidates in-flight logins.
_pending_logins: dict[str, dict[str, Any]] = {}


# ---------- Middleware: refresh session + gate admin path ----------

class RefreshAndAdminGateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session = read_session(request)
        request.state.session = session

        # OF-6.17 — hard gate on /admin/ prefix.
        if request.url.path.startswith("/admin/"):
            if not session:
                return RedirectResponse("/login", status_code=303)
            if session.get("role") not in {"admin", "auditor"}:
                return Response("forbidden", status_code=403)

        response: Response = await call_next(request)
        if session:
            refresh_session(response, dict(session))
        return response


app.add_middleware(RefreshAndAdminGateMiddleware)


def require_session(request: Request) -> dict:
    session = getattr(request.state, "session", None)
    if not session:
        raise HTTPException(303, "redirect", headers={"Location": "/login"})
    return session


# ---------- Health ----------

@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


# ---------- Auth ----------

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    if getattr(request.state, "session", None):
        return RedirectResponse("/queue", status_code=303)
    return RedirectResponse("/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login(request: Request, error: str | None = None):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "session": None, "active": None, "error": error},
    )


@app.get("/login/start")
def login_start() -> RedirectResponse:
    state = secrets.token_urlsafe(24)
    verifier, challenge = oidc.make_pkce()
    _pending_logins[state] = {
        "verifier": verifier,
        "created_at": datetime.now(timezone.utc),
    }
    url = oidc.build_authorize_url(state, challenge)
    return RedirectResponse(url, status_code=303)


@app.get("/auth/callback")
def auth_callback(code: str, state: str) -> RedirectResponse:
    ctx = _pending_logins.pop(state, None)
    if not ctx:
        return RedirectResponse("/login?error=unknown_state", status_code=303)
    tok = oidc.exchange_code(code, ctx["verifier"])
    id_token = tok.get("id_token")
    if not id_token:
        return RedirectResponse("/login?error=no_id_token", status_code=303)
    claims = oidc.decode_id_token_unverified(id_token)

    # Map to pseudonymous operator id via identity-audit-api.
    s = get_settings()
    display = claims.get("name") or claims.get("email") or claims.get("sub", "unknown")
    role = "operator"
    groups = claims.get("groups") or []
    if isinstance(groups, list) and groups:
        for preferred in ("admin", "auditor", "supervisor", "sre"):
            if preferred in groups:
                role = preferred
                break
    if role == "operator":
        # Dev fallback when Dex doesn't emit group claims — derive from
        # the local-part of the email, matching the seeded static users.
        local = (claims.get("email") or "").split("@")[0].lower()
        if local in {"admin", "auditor", "supervisor", "sre", "operator"}:
            role = local

    resp = httpx.post(
        "http://identity-audit-api:7005/resolve",
        json={
            "issuer": claims.get("iss") or s.oidc_issuer,
            "sub": claims.get("sub", "unknown"),
            "display_name": display,
            "role": role,
        },
        timeout=10.0,
    )
    resp.raise_for_status()
    body = resp.json()

    rr = RedirectResponse("/queue", status_code=303)
    issue_session(
        rr,
        {
            "pseudonymous_id": body["pseudonymous_id"],
            "display_name": body["display_name"],
            "role": body["role"],
        },
    )
    log.info(
        "reviewer_ui.login_success",
        pseudonymous_id=body["pseudonymous_id"],
        role=body["role"],
    )
    return rr


@app.get("/logout")
def logout():
    rr = RedirectResponse("/login", status_code=303)
    clear_session(rr)
    return rr


# ---------- Queue ----------

def _fetch_pending(session: dict, limit: int = 50) -> list[dict]:
    sql = text("""
        SELECT r.recommendation_id, r.incident_id, r.produced_at,
               r.decision_class, r.payload, r.sop_references,
               i.ctts_incident_ref, i.severity, i.symptom_text,
               i.affected_nodes
          FROM recommendation r
          JOIN incident i
            ON i.incident_id = r.incident_id
         WHERE r.production_state = 'produced'
           AND NOT EXISTS (
             SELECT 1 FROM operator_decision d
              WHERE d.recommendation_id = r.recommendation_id
           )
         ORDER BY
           CASE i.severity
             WHEN 'P1' THEN 1 WHEN 'P2' THEN 2 WHEN 'P3' THEN 3
             WHEN 'P4' THEN 4 ELSE 5 END,
           r.produced_at DESC
         LIMIT :lim
    """)
    with data_session() as s:
        rows = s.execute(sql, {"lim": limit}).mappings().all()
    out: list[dict] = []
    for row in rows:
        payload = row["payload"]
        if isinstance(payload, str):
            payload = json.loads(payload)
        out.append(
            {
                "recommendation_id": str(row["recommendation_id"]),
                "incident_id": str(row["incident_id"]),
                "ctts_incident_ref": row["ctts_incident_ref"],
                "severity": row["severity"],
                "symptom_text": row["symptom_text"] or "",
                "decision_class": row["decision_class"],
                "confidence": payload.get("confidence", 0.0),
                "produced_at_display": row["produced_at"].strftime("%Y-%m-%d %H:%M"),
                "sop_count": len(row["sop_references"] or []),
            }
        )
    return out


@app.get("/queue", response_class=HTMLResponse)
def queue(request: Request):
    session = require_session(request)
    rows = _fetch_pending(session)
    return templates.TemplateResponse(
        "queue.html",
        {
            "request": request, "session": session, "active": "queue",
            "rows": rows, "flash": None,
        },
    )


# ---------- Recommendation detail ----------

def _fetch_recommendation(rid: UUID) -> dict | None:
    sql = text("""
        SELECT r.recommendation_id, r.incident_id, r.produced_at,
               r.decision_class, r.payload, r.sop_references,
               r.per_agent_status, r.correlation_summary,
               r.diagnostic_summary,
               i.ctts_incident_ref, i.severity, i.symptom_text,
               i.affected_nodes, i.reporting_source
          FROM recommendation r
          JOIN incident i ON i.incident_id = r.incident_id
         WHERE r.recommendation_id = :rid
         ORDER BY r.produced_at DESC
         LIMIT 1
    """)
    with data_session() as s:
        row = s.execute(sql, {"rid": str(rid)}).mappings().first()
        if not row:
            return None
        decision = s.execute(
            text("""
                SELECT decision_kind, reason_code, reason_note,
                       override_action_class, pseudonymous_operator_id,
                       decision_at, ctts_writeback_state
                  FROM operator_decision
                 WHERE recommendation_id = :rid
                 ORDER BY decision_at DESC LIMIT 1
            """),
            {"rid": str(rid)},
        ).mappings().first()
    payload = row["payload"]
    if isinstance(payload, str):
        payload = json.loads(payload)
    rec = {
        "recommendation_id": str(row["recommendation_id"]),
        "incident_id": str(row["incident_id"]),
        "ctts_incident_ref": row["ctts_incident_ref"],
        "severity": row["severity"],
        "symptom_text": row["symptom_text"] or "",
        "affected_nodes": row["affected_nodes"] or [],
        "reporting_source": row["reporting_source"],
        "decision_class": row["decision_class"],
        "summary": payload.get("summary", ""),
        "proposed_actions": payload.get("proposed_actions", []),
        "diagnostic_summary": row["diagnostic_summary"],
        "correlation_summary": row["correlation_summary"],
        "sop_references": row["sop_references"] or [],
        "per_agent_status": row["per_agent_status"] or {},
        "confidence": payload.get("confidence", 0.0),
        "requires_supervisor_review": payload.get("requires_supervisor_review", False),
        "decided": dict(decision) if decision else None,
    }
    if rec["decided"]:
        rec["decided"]["decision_at"] = rec["decided"]["decision_at"].isoformat()
    return rec


@app.get("/recommendation/{rid}", response_class=HTMLResponse)
def recommendation_detail(rid: UUID, request: Request):
    session = require_session(request)
    rec = _fetch_recommendation(rid)
    if not rec:
        raise HTTPException(404, "recommendation not found")
    csrf = request.cookies.get("noc_rev_csrf") or ""
    return templates.TemplateResponse(
        "recommendation.html",
        {
            "request": request, "session": session, "active": "queue",
            "rec": rec, "csrf": csrf, "flash": None,
        },
    )


# ---------- Decision actions ----------

def _record_decision(
    *,
    recommendation_id: UUID,
    decision_kind: str,
    reason_code: str | None,
    reason_note: str | None,
    override_action_class: str | None,
    session: dict,
) -> UUID:
    now = datetime.now(timezone.utc)
    decision_id = uuid.uuid4()
    correlation_token = uuid.uuid4()

    # Load parent recommendation for incident_id + class enum.
    with data_session() as s:
        row = s.execute(
            text("""
                SELECT incident_id, decision_class
                  FROM recommendation
                 WHERE recommendation_id = :rid
                 ORDER BY produced_at DESC LIMIT 1
            """),
            {"rid": str(recommendation_id)},
        ).mappings().first()
    if not row:
        raise HTTPException(404, "recommendation not found")
    incident_id = row["incident_id"]
    recommended_class = row["decision_class"]

    class_enum = "OVERRIDE" if decision_kind == "overridden" else "NORMAL"

    chain = ChainWriteClient()
    payload_ref = {
        "decision_id": str(decision_id),
        "recommendation_id": str(recommendation_id),
        "decision_kind": decision_kind,
        "reason_code": reason_code,
        "override_action_class": override_action_class,
        "recommended_class": recommended_class,
    }
    ch = chain.emit(
        entry_type="operator_decision",
        actor_id=session["pseudonymous_id"],
        actor_role=session["role"],
        payload_ref=payload_ref,
        incident_id=UUID(str(incident_id)),
        class_enum=class_enum,  # type: ignore[arg-type]
    )

    content_hash_bytes = content_hash(payload_ref)

    with data_session() as s, s.begin():
        s.execute(
            text("""
                INSERT INTO operator_decision (
                  decision_id, incident_id, recommendation_id,
                  pseudonymous_operator_id, decision_at, decision_kind,
                  reason_code, reason_note, override_action_class,
                  correlation_token, decision_chain_id,
                  content_hash, ctts_writeback_state
                ) VALUES (
                  :did, :iid, :rid, :op, :now, :kind,
                  :rcode, :rnote, :oclass, :ctok, :chain_id,
                  :chash,
                  CASE WHEN :kind = 'rejected' THEN 'ok' ELSE 'pending' END
                )
            """),
            {
                "did": str(decision_id),
                "iid": str(incident_id),
                "rid": str(recommendation_id),
                "op": session["pseudonymous_id"],
                "now": now,
                "kind": decision_kind,
                "rcode": reason_code,
                "rnote": reason_note,
                "oclass": override_action_class,
                "ctok": str(correlation_token),
                "chain_id": ch["chain_id"],
                "chash": content_hash_bytes,
            },
        )

    DECISION_COUNTER.labels(kind=decision_kind).inc()
    log.info(
        "reviewer_ui.decision_recorded",
        decision_id=str(decision_id),
        recommendation_id=str(recommendation_id),
        kind=decision_kind,
        pseudonymous_id=session["pseudonymous_id"],
    )
    return decision_id


@app.post("/recommendation/{rid}/approve")
def approve(
    rid: UUID,
    request: Request,
    csrf: str = Form(...),
):
    session = require_session(request)
    if not verify_csrf(request, csrf):
        raise HTTPException(403, "csrf mismatch")
    _record_decision(
        recommendation_id=rid, decision_kind="approved",
        reason_code=None, reason_note=None,
        override_action_class=None, session=session,
    )
    return RedirectResponse(f"/recommendation/{rid}", status_code=303)


@app.post("/recommendation/{rid}/reject")
def reject(
    rid: UUID,
    request: Request,
    csrf: str = Form(...),
    reason_code: str = Form(...),
    reason_note: str | None = Form(default=None),
):
    session = require_session(request)
    if not verify_csrf(request, csrf):
        raise HTTPException(403, "csrf mismatch")
    if not reason_code:
        raise HTTPException(400, "reason_code required")
    _record_decision(
        recommendation_id=rid, decision_kind="rejected",
        reason_code=reason_code, reason_note=reason_note,
        override_action_class=None, session=session,
    )
    return RedirectResponse(f"/recommendation/{rid}", status_code=303)


@app.post("/recommendation/{rid}/override")
def override(
    rid: UUID,
    request: Request,
    csrf: str = Form(...),
    override_action_class: str = Form(...),
    reason_note: str = Form(...),
):
    session = require_session(request)
    if not verify_csrf(request, csrf):
        raise HTTPException(403, "csrf mismatch")
    _record_decision(
        recommendation_id=rid, decision_kind="overridden",
        reason_code="operator_override", reason_note=reason_note,
        override_action_class=override_action_class, session=session,
    )
    return RedirectResponse(f"/recommendation/{rid}", status_code=303)


# ---------- Admin ----------

@app.get("/admin/", response_class=HTMLResponse)
def admin_home(request: Request):
    session = require_session(request)
    with data_session() as s:
        failures = s.execute(
            text("""
                SELECT detected_at, stage, rule_id, rule_severity, subject_ref
                  FROM validation_failure
                 ORDER BY detected_at DESC LIMIT 50
            """)
        ).mappings().all()
    wal_dir = Path(get_settings().chain_write_wal_dir)
    backlog = 0
    if wal_dir.exists():
        backlog = sum(1 for _ in wal_dir.glob("*.jsonl"))
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request, "session": session, "active": "admin",
            "chain_health": {"wal_backlog": backlog, "drift_sec": None},
            "validation_failures": [dict(v) for v in failures],
        },
    )


# ---------- History (read-only) ----------

@app.get("/history", response_class=HTMLResponse)
def history(request: Request):
    session = require_session(request)
    with data_session() as s:
        raw = s.execute(
            text("""
                SELECT d.decision_id, d.decision_kind, d.decision_at,
                       d.pseudonymous_operator_id, d.ctts_writeback_state,
                       r.recommendation_id, r.decision_class,
                       i.ctts_incident_ref, i.severity
                  FROM operator_decision d
                  JOIN recommendation r
                    ON r.recommendation_id = d.recommendation_id
                  JOIN incident i
                    ON i.incident_id = d.incident_id
                 ORDER BY d.decision_at DESC
                 LIMIT 50
            """)
        ).mappings().all()
    rows = [
        {
            **dict(r),
            "decision_at_display": r["decision_at"].strftime("%Y-%m-%d %H:%M"),
            "recommendation_id": str(r["recommendation_id"]),
        }
        for r in raw
    ]
    return templates.TemplateResponse(
        "history.html",
        {"request": request, "session": session, "active": "history", "rows": rows},
    )
