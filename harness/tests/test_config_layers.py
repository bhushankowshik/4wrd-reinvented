"""Config layer merge tests.

L1 harness base ← L2 domain ← L3 specialisation ← L4 engagement.

Assertions:
  - With no overrides, `effective_skills` equals the domain registry.
  - L3 `skill_overrides` decorate the producing_system_prompt AND the
    adversarial_system_prompt in place.
  - L4 `active_skills` narrows the registry; non-listed skills drop.
  - `HarnessConfig.skill()` raises KeyError for inactive skills and
    returns the decorated copy for active ones.
"""
from __future__ import annotations

from harness.config.domain_config import DomainConfig, DEFAULT_DOMAIN
from harness.config.engagement_config import EngagementConfig
from harness.config.loader import load_config
from harness.config.specialisation_config import (
    SkillFidelityOverride,
    SpecialisationConfig,
)
from harness.skills import SKILLS


def test_defaults_pass_through_all_skills():
    cfg = load_config()
    assert set(cfg.effective_skills) == set(SKILLS)
    # prompt is untouched.
    assert (
        cfg.skill("S1").producing_system_prompt
        == SKILLS["S1"].producing_system_prompt
    )


def test_l3_override_decorates_prompts():
    override = SkillFidelityOverride(
        skill_id="S1",
        producing_suffix="EXTRA PRODUCING RULE.",
        required_sections=("## Compliance attestation",),
        extra_adversarial_axes=("COMPLIANCE_SURFACE",),
    )
    spec = SpecialisationConfig(
        name="test-spec",
        skill_overrides={"S1": override},
    )
    cfg = load_config(specialisation=spec)
    decorated = cfg.skill("S1")
    assert "EXTRA PRODUCING RULE." in decorated.producing_system_prompt
    assert "## Compliance attestation" in decorated.producing_system_prompt
    assert "COMPLIANCE_SURFACE" in decorated.adversarial_system_prompt
    # Untouched by L3 means the base skill's prompt still equals the
    # pre-decoration text.
    assert (
        SKILLS["S1"].producing_system_prompt
        != decorated.producing_system_prompt
    )


def test_l4_narrows_active_skills():
    engagement = EngagementConfig(
        client_name="ACME", project_id="acme-1",
        active_skills=("S1",),
    )
    cfg = load_config(engagement=engagement)
    assert set(cfg.effective_skills) == {"S1"}
    assert cfg.is_active("S1") is True


def test_inactive_skill_raises():
    import pytest

    engagement = EngagementConfig(
        client_name="ACME", project_id="acme-1",
        active_skills=("S1",),
    )
    # Poison the registry so we know S9 was never known.
    cfg = load_config(engagement=engagement)
    assert cfg.is_active("S9") is False
    with pytest.raises(KeyError):
        cfg.skill("S9")


def test_l3_plus_l4_compose_in_order():
    """L3 decoration runs BEFORE L4 narrowing."""
    override = SkillFidelityOverride(
        skill_id="S1",
        producing_suffix="SPEC SUFFIX.",
    )
    spec = SpecialisationConfig(
        name="s", skill_overrides={"S1": override},
    )
    engagement = EngagementConfig(
        client_name="ACME", project_id="acme-1",
        active_skills=("S1",),
    )
    cfg = load_config(specialisation=spec, engagement=engagement)
    assert set(cfg.effective_skills) == {"S1"}
    assert "SPEC SUFFIX." in cfg.skill("S1").producing_system_prompt
