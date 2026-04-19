"""L4 — Engagement config.

Per INPUT-001 §5, an engagement is the most specific layer: a given
client, project, and the active skills within it. This config layer
sits on top of the three earlier layers and can override any of
them for one concrete delivery.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EngagementConfig:
    """L4 engagement config."""
    client_name: str = "(internal)"
    project_id: str = "4wrd-self-build"
    # Skills activated for this engagement (subset of the skill_registry
    # from L2). Empty means "all skills in the registry".
    active_skills: tuple[str, ...] = ()
    # Additional custom overlays — free-form so operators can carry
    # engagement-specific guidance without changing the schema.
    custom_overlays: dict[str, str] = field(default_factory=dict)
    # Per-engagement primary derivation intent (file paths); acts as
    # an implicit floor for Moment 1 direction capture when the human
    # omits explicit PDI.
    primary_derivation_intent_floor: tuple[str, ...] = ()


DEFAULT_ENGAGEMENT = EngagementConfig()
