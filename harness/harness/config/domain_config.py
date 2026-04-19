"""L2 — Domain config.

Per INPUT-001 §5 a domain is a broad sector (Telecommunications,
Finance, Healthcare, Software Development Tooling). The domain
config carries the skill registry for that domain and the delivery
methodology expression in the orchestration layer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from harness.skills import SKILLS as _DEFAULT_SKILLS


@dataclass(frozen=True)
class DomainConfig:
    """L2 domain config."""
    name: str = "Software Development Tooling"
    methodology: str = "Hybrid"
    # Skill registry is a mapping skill_id → Skill record. Uses the
    # live registry by default; L3/L4 can swap or extend it.
    skill_registry: dict = field(default_factory=lambda: dict(_DEFAULT_SKILLS))
    # Default skill sequences within this domain — used by the
    # orchestrator for gate discipline.
    solutioning_sequence: tuple[str, ...] = (
        "S1", "S2", "S3", "S4", "S5", "S6",
    )
    execution_sequence: tuple[str, ...] = (
        "E1", "E2", "E3", "E4", "E5",
        "E6", "E7", "E8", "E9", "E10",
    )


DEFAULT_DOMAIN = DomainConfig()
