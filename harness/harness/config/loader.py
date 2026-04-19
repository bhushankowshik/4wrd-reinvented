"""Config loader — stack L1 → L2 → L3 → L4 and return one `HarnessConfig`.

Layer override policy (INPUT-001 §5):

  Base          L1 harness     — chain + models + budgets + rules
  Override      L2 domain      — skill registry + methodology
  Override      L3 specialisation — regulatory overlay + skill fidelity overrides
  Override      L4 engagement  — client/project + active skills + custom overlays

Conflicts: a later layer's value wins. L3 `skill_overrides` decorate L2 skills
in-place (producing_suffix appended, extra adversarial axes recorded in
metadata). L4 `active_skills` narrows the L2 registry.

This loader is declarative: callers build the four layer objects and the
loader composes them. No filesystem reads — layer construction is the caller's
concern so tests can inject any combination.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

from harness.config.domain_config import DEFAULT_DOMAIN, DomainConfig
from harness.config.engagement_config import (
    DEFAULT_ENGAGEMENT,
    EngagementConfig,
)
from harness.config.harness_config import (
    DEFAULT_HARNESS_CORE,
    HarnessCoreConfig,
)
from harness.config.specialisation_config import (
    DEFAULT_SPECIALISATION,
    SkillFidelityOverride,
    SpecialisationConfig,
)
from harness.skills.s1_problem_crystallisation import Skill


@dataclass(frozen=True)
class HarnessConfig:
    """Composed, frozen config after all four layers merge."""
    harness: HarnessCoreConfig
    domain: DomainConfig
    specialisation: SpecialisationConfig
    engagement: EngagementConfig
    # Effective skill registry after L3 decoration + L4 narrowing.
    effective_skills: dict[str, Skill] = field(default_factory=dict)

    def skill(self, skill_id: str) -> Skill:
        try:
            return self.effective_skills[skill_id]
        except KeyError as exc:
            raise KeyError(
                f"skill_id {skill_id!r} is not active in this engagement. "
                f"Active: {sorted(self.effective_skills.keys())}"
            ) from exc

    def is_active(self, skill_id: str) -> bool:
        return skill_id in self.effective_skills


def _apply_skill_override(skill: Skill, override: SkillFidelityOverride) -> Skill:
    """Decorate a Skill with L3 fidelity overrides."""
    producing = skill.producing_system_prompt
    if override.producing_suffix:
        producing = producing.rstrip() + "\n\n" + override.producing_suffix.strip()
    if override.required_sections:
        sections_note = (
            "\n\nAdditional required sections for this specialisation:\n"
            + "\n".join(f"  - {s}" for s in override.required_sections)
        )
        producing = producing.rstrip() + sections_note

    adversarial = skill.adversarial_system_prompt
    if override.extra_adversarial_axes:
        axes = ", ".join(override.extra_adversarial_axes)
        adversarial = (
            adversarial.rstrip()
            + f"\n\nAdditional challenge axes for this specialisation: {axes}."
        )

    return Skill(
        skill_id=skill.skill_id,
        name=skill.name,
        producing_system_prompt=producing,
        adversarial_system_prompt=adversarial,
        exit_artefact_template=skill.exit_artefact_template,
    )


def _compute_effective_skills(
    *,
    domain: DomainConfig,
    specialisation: SpecialisationConfig,
    engagement: EngagementConfig,
) -> dict[str, Skill]:
    registry = dict(domain.skill_registry)
    # L3 decoration.
    for skill_id, override in specialisation.skill_overrides.items():
        if skill_id in registry:
            registry[skill_id] = _apply_skill_override(registry[skill_id], override)
    # L4 narrowing.
    if engagement.active_skills:
        registry = {
            sid: s for sid, s in registry.items() if sid in engagement.active_skills
        }
    return registry


def load_config(
    *,
    harness: HarnessCoreConfig | None = None,
    domain: DomainConfig | None = None,
    specialisation: SpecialisationConfig | None = None,
    engagement: EngagementConfig | None = None,
) -> HarnessConfig:
    """Compose the four layers into one `HarnessConfig`.

    Omitted layers fall back to the module-level defaults. Any layer
    can be passed as a custom instance; the later-wins override policy
    is already baked into dataclass field defaults + `replace()` —
    callers pre-build the layer they want before handing it in.
    """
    h = harness or DEFAULT_HARNESS_CORE
    d = domain or DEFAULT_DOMAIN
    s = specialisation or DEFAULT_SPECIALISATION
    e = engagement or DEFAULT_ENGAGEMENT
    effective = _compute_effective_skills(domain=d, specialisation=s, engagement=e)
    return HarnessConfig(
        harness=h, domain=d, specialisation=s, engagement=e,
        effective_skills=effective,
    )
