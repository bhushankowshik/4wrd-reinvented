"""Minimal structured logging — no external collector dependency."""
from __future__ import annotations

import structlog


def configure() -> None:
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO+
    )


configure()
log = structlog.get_logger("mvghb")
