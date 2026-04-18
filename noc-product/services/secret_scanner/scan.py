"""Secret-pattern scanner — E6a §2.4 / E5 §5.1 INT-008,
§5.5 SOP-004. Pattern file pinned at patterns.yaml.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml


Severity = Literal["low", "medium", "high"]


@dataclass
class ScanMatch:
    pattern_id: str
    severity: Severity
    position: int
    preview: str


@dataclass
class ScanResult:
    matches: list[ScanMatch]

    @property
    def max_severity(self) -> Severity | None:
        order = {"low": 1, "medium": 2, "high": 3}
        if not self.matches:
            return None
        return max((m.severity for m in self.matches), key=lambda s: order[s])

    def as_dict(self) -> list[dict[str, Any]]:
        return [
            {
                "pattern_id": m.pattern_id,
                "severity": m.severity,
                "position": m.position,
                "preview": m.preview,
            }
            for m in self.matches
        ]


@lru_cache(maxsize=1)
def _compiled_patterns() -> list[tuple[str, Severity, re.Pattern[str]]]:
    path = Path(__file__).parent / "patterns.yaml"
    data = yaml.safe_load(path.read_text())
    compiled: list[tuple[str, Severity, re.Pattern[str]]] = []
    for p in data.get("patterns", []):
        sev = p.get("severity", "medium")
        compiled.append((p["id"], sev, re.compile(p["regex"])))
    return compiled


def scan(text_blob: str) -> ScanResult:
    if not text_blob:
        return ScanResult(matches=[])
    out: list[ScanMatch] = []
    for pid, sev, rx in _compiled_patterns():
        for m in rx.finditer(text_blob):
            preview = text_blob[max(0, m.start() - 5): m.end() + 5][:60]
            # Redact middle of preview to avoid echoing the secret back.
            redacted = preview[:4] + "***" + preview[-4:]
            out.append(
                ScanMatch(pattern_id=pid, severity=sev, position=m.start(), preview=redacted)
            )
    return ScanResult(matches=out)
