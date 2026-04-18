"""Signed-cookie session for the Reviewer UI.

Sliding timeout 8h, absolute timeout 12h (E6a §3.7).
Cookie signed with itsdangerous TimestampSigner; contents
are JSON with the operator's pseudonymous_id, display_name,
role, issued_at, and last_activity_at.
"""
from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from typing import Any

from fastapi import Request, Response
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from services.common.settings import get_settings


SESSION_COOKIE = "noc_rev_session"
CSRF_COOKIE = "noc_rev_csrf"


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(
        get_settings().session_secret, salt="noc-reviewer-session"
    )


def issue_session(resp: Response, payload: dict[str, Any]) -> str:
    now = datetime.now(timezone.utc).isoformat()
    body = {**payload, "issued_at": now, "last_activity_at": now}
    token = _serializer().dumps(body)
    resp.set_cookie(
        SESSION_COOKIE, token, httponly=True, samesite="lax",
        secure=False, max_age=get_settings().session_absolute_hours * 3600,
    )
    csrf = secrets.token_urlsafe(24)
    resp.set_cookie(
        CSRF_COOKIE, csrf, httponly=False, samesite="lax",
        secure=False, max_age=get_settings().session_absolute_hours * 3600,
    )
    return csrf


def clear_session(resp: Response) -> None:
    resp.delete_cookie(SESSION_COOKIE)
    resp.delete_cookie(CSRF_COOKIE)


def read_session(req: Request) -> dict[str, Any] | None:
    tok = req.cookies.get(SESSION_COOKIE)
    if not tok:
        return None
    s = get_settings()
    try:
        body = _serializer().loads(
            tok, max_age=s.session_sliding_hours * 3600
        )
    except (BadSignature, SignatureExpired):
        return None
    # Absolute cap — if body.issued_at is older than absolute_hours, reject.
    try:
        issued = datetime.fromisoformat(body["issued_at"])
    except Exception:
        return None
    age = (datetime.now(timezone.utc) - issued).total_seconds()
    if age > s.session_absolute_hours * 3600:
        return None
    return body


def refresh_session(resp: Response, body: dict[str, Any]) -> None:
    body["last_activity_at"] = datetime.now(timezone.utc).isoformat()
    tok = _serializer().dumps(body)
    resp.set_cookie(
        SESSION_COOKIE, tok, httponly=True, samesite="lax",
        secure=False, max_age=get_settings().session_absolute_hours * 3600,
    )


def verify_csrf(req: Request, form_token: str | None) -> bool:
    cookie_token = req.cookies.get(CSRF_COOKIE)
    if not cookie_token or not form_token:
        return False
    return secrets.compare_digest(cookie_token, form_token)
