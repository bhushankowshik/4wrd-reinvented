"""Identity-Audit API — per E5 §1.9/§1.10 + E6a §2.2.

Dev stub: forward resolution plus break-glass reverse lookup
backed by governance_chain + identity_map_access_log.

  POST /resolve  — map OIDC {issuer, sub, display_name, role}
                   to a deterministic pseudonymous_id;
                   creates the operator_identity_map row on
                   first sight and emits a governance_chain
                   issuance entry.
  POST /reverse  — break-glass audit lookup — requires an
                   'auditor' role hint from the caller,
                   appends to identity_map_access_log.

Hardening (two-person joint session, formal rate limit,
anomaly detection) is deferred to E8.
"""
from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, Header, HTTPException
from prometheus_client import Counter, make_asgi_app
from pydantic import BaseModel
from sqlalchemy import text

from services.chain_write.client import ChainWriteClient
from services.common.db import gov_session
from services.common.telemetry import configure_logging, log


configure_logging()

app = FastAPI(title="identity-audit-api")
app.mount("/metrics", make_asgi_app())


IDENTITY_MAP_REVERSE = Counter(
    "noc_identity_map_reverse_lookups_total",
    "Break-glass reverse lookups on the identity map",
    ["actor_role", "outcome"],
)
IDENTITY_MAP_RESOLVE = Counter(
    "noc_identity_map_resolutions_total",
    "Forward resolutions {issuer,sub}->pseudonymous_id",
    ["issuer", "outcome"],
)


_PSEUDO_SALT = os.environ.get(
    "IDENTITY_PSEUDO_SALT", "dev-pseudo-salt-change-me"
).encode()

_chain = ChainWriteClient()


def _pseudo_id(issuer: str, sub: str) -> str:
    h = hashlib.sha256(_PSEUDO_SALT + f"{issuer}|{sub}".encode()).hexdigest()
    return f"pseudo-{h[:20]}"


class ResolveIn(BaseModel):
    issuer: str
    sub: str
    display_name: str
    role: str = "operator"


class ResolveOut(BaseModel):
    pseudonymous_id: str
    role: str
    display_name: str
    created_at: datetime
    created: bool


class ReverseIn(BaseModel):
    pseudonymous_id: str
    justification: str


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/resolve", response_model=ResolveOut)
def resolve(req: ResolveIn) -> ResolveOut:
    if req.role not in {"operator", "supervisor", "auditor", "admin", "sre"}:
        raise HTTPException(400, f"invalid role: {req.role}")
    pid = _pseudo_id(req.issuer, req.sub)
    now = datetime.now(timezone.utc)
    sso_subject = f"{req.issuer}|{req.sub}"
    created = False

    with gov_session() as s, s.begin():
        row = s.execute(
            text("""
                SELECT pseudonymous_id, display_name, role, created_at
                  FROM operator_identity_map
                 WHERE pseudonymous_id = :pid
            """),
            {"pid": pid},
        ).mappings().first()

        if not row:
            chain = _chain.emit(
                entry_type="identity_issuance",
                actor_id="identity-audit-api",
                actor_role="service_account",
                payload_ref={
                    "pseudonymous_id": pid,
                    "issuer": req.issuer,
                    "role": req.role,
                },
            )
            s.execute(
                text("""
                    INSERT INTO operator_identity_map
                      (pseudonymous_id, sso_subject_id,
                       display_name, role, created_at,
                       issuance_chain_id)
                    VALUES
                      (:pid, :sso, :name, :role, :now, :chain_id)
                """),
                {
                    "pid": pid,
                    "sso": sso_subject,
                    "name": req.display_name,
                    "role": req.role,
                    "now": now,
                    "chain_id": chain["chain_id"],
                },
            )
            created = True
            created_at = now
            display_name = req.display_name
            role = req.role
        else:
            created_at = row["created_at"]
            display_name = row["display_name"]
            role = row["role"]

    IDENTITY_MAP_RESOLVE.labels(
        issuer=req.issuer, outcome="created" if created else "existing"
    ).inc()
    return ResolveOut(
        pseudonymous_id=pid,
        role=role,
        display_name=display_name,
        created_at=created_at,
        created=created,
    )


@app.post("/reverse")
def reverse(
    req: ReverseIn,
    x_actor_role: str = Header(default=""),
    x_actor_id: str = Header(default=""),
) -> dict:
    if x_actor_role != "auditor":
        IDENTITY_MAP_REVERSE.labels(
            actor_role=x_actor_role or "none", outcome="forbidden"
        ).inc()
        raise HTTPException(403, "auditor role required for reverse lookup")
    access_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    chain = _chain.emit(
        entry_type="identity_map_access",
        actor_id=x_actor_id or "unknown",
        actor_role=x_actor_role,
        payload_ref={
            "access_id": str(access_id),
            "subject": req.pseudonymous_id,
            "justification": req.justification,
        },
    )
    with gov_session() as s, s.begin():
        row = s.execute(
            text("""
                SELECT sso_subject_id, display_name, role, created_at
                  FROM operator_identity_map
                 WHERE pseudonymous_id = :pid
            """),
            {"pid": req.pseudonymous_id},
        ).mappings().first()
        s.execute(
            text("""
                INSERT INTO identity_map_access_log
                  (access_id, access_at, requester_pseudo_id,
                   requester_role, access_kind, record_count,
                   justification, access_chain_id,
                   rate_limit_bucket)
                VALUES
                  (:aid, :now, :accessor, :role,
                   'single_record', 1, :reason,
                   :chain_id, 'default')
            """),
            {
                "aid": str(access_id),
                "now": now,
                "accessor": x_actor_id or "unknown",
                "role": x_actor_role,
                "reason": req.justification,
                "chain_id": chain["chain_id"],
            },
        )
    IDENTITY_MAP_REVERSE.labels(
        actor_role=x_actor_role,
        outcome="served" if row else "not_found",
    ).inc()
    log.warning(
        "identity_audit.reverse_lookup",
        access_id=str(access_id),
        accessor=x_actor_id,
        subject=req.pseudonymous_id,
    )
    if not row:
        raise HTTPException(404, "pseudonymous_id unknown")
    return {
        "access_id": str(access_id),
        "pseudonymous_id": req.pseudonymous_id,
        "sso_subject_id": row["sso_subject_id"],
        "display_name": row["display_name"],
        "role": row["role"],
        "created_at": row["created_at"].isoformat(),
    }
