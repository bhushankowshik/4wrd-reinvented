"""Test-time defaults so unit tests can run without a live
Docker Compose stack. Integration + chain tests that touch
Postgres gate themselves on env NOC_LIVE_DB=1.
"""
from __future__ import annotations

import os

# Default to a filesystem-only WAL so ChainWriter can
# initialize without hitting /var/wal.
os.environ.setdefault("CHAIN_WRITE_WAL_DIR", "/tmp/noc-test-wal")
os.environ.setdefault("SESSION_SECRET", "dev-test-secret-do-not-use-in-prod")
os.environ.setdefault("NOC_DATA_DSN", "postgresql+psycopg://noc:noc@localhost:5433/noc_data")
os.environ.setdefault("NOC_GOV_DSN", "postgresql+psycopg://noc:noc@localhost:5434/noc_gov")
