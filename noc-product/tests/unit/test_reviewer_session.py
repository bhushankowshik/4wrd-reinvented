"""M8 — Reviewer UI session + CSRF unit tests."""
from __future__ import annotations

import time

from fastapi import Request, Response

from services.reviewer_ui.session import (
    CSRF_COOKIE,
    SESSION_COOKIE,
    issue_session,
    read_session,
    verify_csrf,
)


def _req_with_cookies(cookies: dict[str, str]) -> Request:
    scope = {
        "type": "http",
        "headers": [
            (b"cookie", b"; ".join(
                f"{k}={v}".encode() for k, v in cookies.items()
            ))
        ],
        "method": "GET",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
    }
    return Request(scope)


def test_issue_then_read_roundtrip():
    resp = Response()
    csrf = issue_session(
        resp,
        {"pseudonymous_id": "pseudo-test-01", "display_name": "A", "role": "operator"},
    )
    assert csrf

    # Extract cookies from Set-Cookie headers.
    cookies: dict[str, str] = {}
    for _, header in resp.raw_headers:
        # No-op here; use resp.headers.getlist equivalent.
        pass
    # Simpler: use the response's known cookies via multidict.
    for k, v in resp.headers.items():
        if k.lower() == "set-cookie":
            name = v.split("=", 1)[0]
            val = v.split("=", 1)[1].split(";", 1)[0]
            cookies[name] = val

    assert SESSION_COOKIE in cookies
    assert CSRF_COOKIE in cookies

    req = _req_with_cookies(cookies)
    body = read_session(req)
    assert body is not None
    assert body["pseudonymous_id"] == "pseudo-test-01"
    assert body["role"] == "operator"


def test_tampered_session_rejected():
    resp = Response()
    issue_session(
        resp, {"pseudonymous_id": "x", "display_name": "y", "role": "operator"}
    )
    cookies: dict[str, str] = {}
    for k, v in resp.headers.items():
        if k.lower() == "set-cookie":
            name, rest = v.split("=", 1)
            cookies[name] = rest.split(";", 1)[0]
    # Flip one byte of the session cookie.
    tampered = cookies[SESSION_COOKIE][:-3] + "AAA"
    cookies[SESSION_COOKIE] = tampered
    req = _req_with_cookies(cookies)
    assert read_session(req) is None


def test_csrf_mismatch_rejected():
    req = _req_with_cookies({CSRF_COOKIE: "abc123"})
    assert verify_csrf(req, "abc123") is True
    assert verify_csrf(req, "different") is False
    assert verify_csrf(req, None) is False


def test_csrf_missing_cookie_rejected():
    req = _req_with_cookies({})
    assert verify_csrf(req, "whatever") is False
