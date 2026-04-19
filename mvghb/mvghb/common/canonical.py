"""Canonical JSON encoding — frozen by E6a §2.6.

Identical contract to noc-product/services/common/canonical.py so the
two systems agree on byte-level encoding. Any change is a chain-forking
event (OF-6.6).
"""
from __future__ import annotations

import json
from typing import Any


def canonical_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")
