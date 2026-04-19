"""L3 — Specialisation config.

Per INPUT-001 §5 a specialisation is a focused context within a
domain (NOC Operations, Retail Banking Compliance, Governed Human-AI
Delivery Harness). The specialisation config carries regulatory
overlays, compliance framework references, and per-skill fidelity
criteria overrides.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ComplianceFramework:
    """Reference to a regulatory / compliance framework."""
    name: str
    authority: str
    scope: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SkillFidelityOverride:
    """Per-skill fidelity-criterion override.

    `extra_adversarial_axes` are appended to the Adversarial Agent's
    default axes for this skill. `required_sections` augment the
    Producing Agent's required output sections. `producing_suffix`
    appends additional guidance to the skill's producing system prompt.
    """
    skill_id: str
    extra_adversarial_axes: tuple[str, ...] = field(default_factory=tuple)
    required_sections: tuple[str, ...] = field(default_factory=tuple)
    producing_suffix: str | None = None


@dataclass(frozen=True)
class SpecialisationConfig:
    """L3 specialisation config."""
    name: str = "Governed Human-AI Delivery Harness"
    regulatory_overlay: str | None = None
    compliance_frameworks: tuple[ComplianceFramework, ...] = field(default_factory=tuple)
    skill_overrides: dict[str, SkillFidelityOverride] = field(default_factory=dict)


DEFAULT_SPECIALISATION = SpecialisationConfig()


# Pre-canned specialisation for the MAS-TRM-bound Singapore fintech
# scope called out in the task knowledge contribution. Consumers can
# opt in via engagement config.
MAS_TRM_SPECIALISATION = SpecialisationConfig(
    name="MAS-TRM-bound Singapore fintech SDLC",
    regulatory_overlay="MAS Technology Risk Management",
    compliance_frameworks=(
        ComplianceFramework(
            name="MAS TRM",
            authority="Monetary Authority of Singapore",
            scope=(
                "Technology Risk Governance and Oversight",
                "IT Project Management",
                "Software Application Development & Management",
                "IT Change Management",
                "IT Audit",
                "Access Control",
                "Cryptography",
            ),
        ),
    ),
    skill_overrides={
        "S1": SkillFidelityOverride(
            skill_id="S1",
            extra_adversarial_axes=("COMPLIANCE_SURFACE",),
            required_sections=("## MAS TRM domain mapping",),
            producing_suffix=(
                "This specialisation is MAS-TRM-bound. If the problem "
                "touches any MAS TRM domain (SDLC, change management, "
                "access control, cryptography, audit), name the domain "
                "explicitly under '## MAS TRM domain mapping'."
            ),
        ),
    },
)
