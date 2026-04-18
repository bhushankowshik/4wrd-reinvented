import logging
import structlog
from prometheus_client import Counter, Histogram, Gauge


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ]
    )


log = structlog.get_logger()


# Prometheus metrics — per E6a §3.14 and §5.4 benchmarks.
RECOMMENDATION_DURATION = Histogram(
    "noc_recommendation_duration_seconds",
    "End-to-end recommendation production latency",
    buckets=(1, 5, 15, 30, 60, 90, 120, 180, 300, 600),
)
AGENT_DURATION = Histogram(
    "noc_agent_duration_seconds",
    "Agent invocation duration",
    ["agent_kind"],
    buckets=(0.5, 1, 2, 5, 10, 30, 60, 120),
)
AGENT_TIMEOUTS = Counter(
    "noc_agent_timeouts_total",
    "Agent invocations that hit their timeout",
    ["agent_kind"],
)
AGENT_ERRORS = Counter(
    "noc_agent_errors_total",
    "Agent invocations that errored",
    ["agent_kind", "reason"],
)
CHAIN_EMITS = Counter(
    "noc_chain_emits_total",
    "Chain-Write Service emit calls",
    ["entry_type", "outcome"],
)
CHAIN_WAL_BACKLOG = Gauge(
    "noc_chain_write_wal_backlog",
    "Chain-Write WAL entries awaiting PG commit",
)
VALIDATION_FAILURES = Counter(
    "noc_validation_failures_total",
    "Data validation rule violations",
    ["stage", "rule_id", "severity"],
)
INTAKE_INGESTED = Counter(
    "noc_intake_ingested_total",
    "Incidents successfully ingested",
    ["reporting_source"],
)
MODEL_CALLS = Counter(
    "noc_model_calls_total",
    "Model backend calls",
    ["kind", "model", "outcome"],
)
