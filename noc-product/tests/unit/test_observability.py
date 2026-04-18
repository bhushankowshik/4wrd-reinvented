"""M9 — static wiring tests: every service that exposes metrics
has a scrape target and every histogram/counter referenced by
alert expressions is declared in telemetry.py.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PROMETHEUS_YML = ROOT / "dev" / "prometheus" / "prometheus.yml"
ALERTS_YML = ROOT / "dev" / "prometheus" / "alerts.yml"
TELEMETRY_PY = ROOT / "services" / "common" / "telemetry.py"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def test_all_http_services_are_scraped():
    cfg = _load(PROMETHEUS_YML)
    jobs = {j["job_name"] for j in cfg["scrape_configs"]}
    expected = {
        "chain-write",
        "agents",
        "reviewer-ui",
        "identity-audit-api",
        "mock-ctts",
        "intake",
        "write-back",
    }
    missing = expected - jobs
    assert not missing, f"missing scrape jobs: {missing}"


_METRIC_RX = re.compile(r"noc_[a-z_]+")


def test_alert_metrics_are_declared():
    alerts_text = ALERTS_YML.read_text()
    tel_text = TELEMETRY_PY.read_text()
    referenced = {m for m in _METRIC_RX.findall(alerts_text)}
    # Strip suffix like _bucket / _total for histogram/counter namespace checks.
    base_referenced = {
        m.removesuffix("_bucket").removesuffix("_total")
        for m in referenced
    }
    # Metrics that live in worker-side modules (reviewer_ui, writeback).
    extra_decl_sources = [
        (ROOT / "services" / "reviewer_ui" / "app.py").read_text(),
        (ROOT / "services" / "write_back" / "worker.py").read_text(),
    ]
    declared_text = tel_text + "\n" + "\n".join(extra_decl_sources)
    declared = {
        m.removesuffix("_bucket").removesuffix("_total")
        for m in _METRIC_RX.findall(declared_text)
    }
    missing = base_referenced - declared
    assert not missing, (
        f"alert references undeclared metrics: {missing}"
    )


def test_recommendation_latency_alert_threshold_matches_nfr():
    alerts_text = ALERTS_YML.read_text()
    assert "RecommendationLatencyBreach" in alerts_text
    # NFR-L.1 indicative budget = 180s.
    assert "180" in alerts_text


def test_grafana_dashboards_provisioned():
    dashboards_dir = ROOT / "dev" / "grafana" / "dashboards"
    dashboards = list(dashboards_dir.glob("*.json"))
    titles = set()
    import json as _json
    for p in dashboards:
        titles.add(_json.loads(p.read_text()).get("title"))
    assert {"NOC Operational", "NOC Quality", "NOC Capacity"} <= titles
