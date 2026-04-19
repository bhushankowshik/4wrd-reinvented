"""Test-time defaults."""
from __future__ import annotations

import base64
import os
import secrets

# Stable test KEK so signing is reproducible across runs.
os.environ.setdefault(
    "MVGHB_KEK",
    base64.b64encode(b"\x01" * 32).decode("ascii"),
)
os.environ.setdefault("MVGHB_WAL_DIR", "/tmp/mvghb-test-wal")
os.environ.setdefault(
    "MVGHB_GOV_DSN",
    "postgresql+psycopg://noc:noc@localhost:5434/noc_gov",
)
