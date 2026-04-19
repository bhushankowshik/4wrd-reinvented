"""Crypto primitives — HKDF derivation + HMAC-SHA256.

Per spec:
  HKDF(algorithm=SHA256, length=32, salt=None, info=entry_id.bytes)
"""
from __future__ import annotations

import hmac
import hashlib
from uuid import UUID

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


HKDF_LEN = 32


def derive_entry_key(kek: bytes, entry_id: UUID) -> bytes:
    """HKDF-SHA256 derive a per-entry signing key from the KEK.

    Deterministic: same (kek, entry_id) → same key.
    """
    return HKDF(
        algorithm=hashes.SHA256(),
        length=HKDF_LEN,
        salt=None,
        info=entry_id.bytes,
    ).derive(kek)


def hmac_sha256(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()


def constant_time_eq(a: bytes, b: bytes) -> bool:
    return hmac.compare_digest(a, b)
