"""Canonical JSON per E5 §1.17 / E6a §2.6.

Deterministic byte encoding for HMAC and content_hash.
ALL hash/HMAC inputs route through canonical_bytes.
"""
import hashlib
import json
from typing import Any


def canonical_bytes(payload: Any) -> bytes:
    """UTF-8 bytes of JSON with sorted keys, compact separators,
    no BOM, ensure_ascii=False. Numbers and nulls preserved
    as-is; floats stringified by json default behaviour.
    """
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def content_hash(payload: Any) -> bytes:
    """SHA-256 over canonical_bytes. Returns raw bytes."""
    return hashlib.sha256(canonical_bytes(payload)).digest()


def content_hash_hex(payload: Any) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()
