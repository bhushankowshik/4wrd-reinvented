"""Dex OIDC integration — Authorization Code + PKCE.

Dev notes: skip_well_known in dev pointed at Dex container;
discovery via issuer/.well-known/openid-configuration.
"""
from __future__ import annotations

import base64
import hashlib
import secrets
import time
from typing import Any

import httpx
from fastapi import HTTPException

from services.common.settings import get_settings


_discovery_cache: dict[str, Any] = {}


def _discover(issuer: str) -> dict[str, Any]:
    if "doc" in _discovery_cache and _discovery_cache.get("issuer") == issuer:
        return _discovery_cache["doc"]
    resp = httpx.get(f"{issuer.rstrip('/')}/.well-known/openid-configuration",
                     timeout=5.0)
    resp.raise_for_status()
    _discovery_cache["issuer"] = issuer
    _discovery_cache["doc"] = resp.json()
    return _discovery_cache["doc"]


def make_pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()
    return verifier, challenge


def build_authorize_url(state: str, code_challenge: str) -> str:
    s = get_settings()
    doc = _discover(s.oidc_issuer)
    from urllib.parse import urlencode
    qs = urlencode({
        "response_type": "code",
        "client_id": s.oidc_client_id,
        "redirect_uri": s.oidc_redirect_uri,
        "scope": "openid profile email groups",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    })
    return f"{doc['authorization_endpoint']}?{qs}"


def exchange_code(code: str, verifier: str) -> dict[str, Any]:
    s = get_settings()
    doc = _discover(s.oidc_issuer)
    resp = httpx.post(
        doc["token_endpoint"],
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": s.oidc_redirect_uri,
            "client_id": s.oidc_client_id,
            "client_secret": s.oidc_client_secret,
            "code_verifier": verifier,
        },
        timeout=10.0,
    )
    if resp.status_code >= 400:
        raise HTTPException(401, f"token exchange failed: {resp.text}")
    return resp.json()


def decode_id_token_unverified(id_token: str) -> dict[str, Any]:
    """Dev-only decode: split JWT, base64url-decode claims.

    Real signature verification (JWKS fetch, aud/iss checks)
    is deferred to E8 hardening.
    """
    import json as _json
    parts = id_token.split(".")
    if len(parts) != 3:
        raise HTTPException(400, "malformed id_token")
    pad = "=" * (-len(parts[1]) % 4)
    claims = _json.loads(base64.urlsafe_b64decode(parts[1] + pad))
    now = int(time.time())
    if claims.get("exp") and claims["exp"] < now:
        raise HTTPException(401, "id_token expired")
    return claims
