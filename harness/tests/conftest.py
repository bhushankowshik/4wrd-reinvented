"""Harness test defaults — match the mvghb conftest environment."""
from __future__ import annotations

import base64
import os

# Match mvghb/tests/conftest.py so real ChainWriter works in tests.
os.environ.setdefault(
    "MVGHB_KEK",
    base64.b64encode(b"\x01" * 32).decode("ascii"),
)
os.environ.setdefault("MVGHB_WAL_DIR", "/tmp/mvghb-test-wal")
os.environ.setdefault(
    "MVGHB_GOV_DSN",
    "postgresql+psycopg://noc:noc@localhost:5434/noc_gov",
)
# Agents will not actually be called in unit tests (they are mocked),
# so we stub an API key so the anthropic client constructor doesn't
# complain.
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-stub")
