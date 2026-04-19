"""HKDF + HMAC primitive tests — pure unit, no DB."""
from __future__ import annotations

from uuid import UUID, uuid4

from mvghb.common.crypto import constant_time_eq, derive_entry_key, hmac_sha256


KEK_A = b"\x01" * 32
KEK_B = b"\x02" * 32
ENTRY_ID = UUID("12345678-1234-5678-1234-567812345678")


def test_hkdf_deterministic_same_kek_same_entry():
    k1 = derive_entry_key(KEK_A, ENTRY_ID)
    k2 = derive_entry_key(KEK_A, ENTRY_ID)
    assert k1 == k2
    assert len(k1) == 32


def test_hkdf_changes_on_kek_change():
    k1 = derive_entry_key(KEK_A, ENTRY_ID)
    k2 = derive_entry_key(KEK_B, ENTRY_ID)
    assert k1 != k2


def test_hkdf_changes_on_entry_change():
    k1 = derive_entry_key(KEK_A, ENTRY_ID)
    k2 = derive_entry_key(KEK_A, uuid4())
    assert k1 != k2


def test_hmac_roundtrip():
    key = derive_entry_key(KEK_A, ENTRY_ID)
    msg = b"hello mvghb"
    sig = hmac_sha256(key, msg)
    assert hmac_sha256(key, msg) == sig
    assert constant_time_eq(sig, hmac_sha256(key, msg))
    assert not constant_time_eq(sig, hmac_sha256(key, msg + b"!"))
