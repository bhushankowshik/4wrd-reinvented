"""Layer 3 context package builder.

Per INPUT-001 §2.2, Layer 3 context packages are generated fresh before
each agent invocation from Layer 1 (governance_chain) entries written
since the last generation. This module produces two shapes:

- **ProducingContextPackage** — direction + knowledge contribution +
  summarised prior chain entries for this skill. Goes to the Sonnet 4.6
  Producing Agent.

- **ChallengeContextPackage** — output + reasoning trace + direction
  only. Goes to the Opus 4.6 Adversarial Agent. Deliberately narrow —
  the Adversarial Agent challenges this cycle's production, not all
  of history.

Token-budget shape is controlled by `max_prior_entries` and a small
character budget per entry summary. Knowledge contribution: INPUT-001
§2.1 says this is only required in the Explorative convergence state.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from sqlalchemy import text

from mvghb.common.db import gov_session


ConvergenceState = Literal["Explorative", "Targeted", "Exact"]

# Conservative per-entry summary cap — keeps the package well under
# the 50k-token budget from the task knowledge contribution even when
# max_prior_entries is raised. 2000 chars ≈ 500 tokens.
_ENTRY_SUMMARY_CHAR_CAP = 2000


@dataclass(frozen=True)
class PriorEntrySummary:
    chain_id: str
    entry_type: str
    actor_id: str
    timestamp: str
    summary: str


@dataclass(frozen=True)
class ProducingContextPackage:
    skill_id: str
    convergence_state: ConvergenceState
    direction: str
    knowledge_contribution: str | None
    prior_entries: list[PriorEntrySummary] = field(default_factory=list)
    primary_derivation_intent: list[str] = field(default_factory=list)

    def render(self) -> str:
        """Render as the user-message text for the Producing Agent."""
        parts: list[str] = []
        parts.append(f"# Skill: {self.skill_id}")
        parts.append(f"# Convergence state: {self.convergence_state}")
        parts.append("")
        parts.append("## Direction")
        parts.append(self.direction.strip())
        parts.append("")
        if self.knowledge_contribution:
            parts.append("## Knowledge contribution")
            parts.append(self.knowledge_contribution.strip())
            parts.append("")
        if self.primary_derivation_intent:
            parts.append("## Primary derivation intent")
            for ref in self.primary_derivation_intent:
                parts.append(f"- {ref}")
            parts.append("")
        if self.prior_entries:
            parts.append(f"## Prior chain entries ({len(self.prior_entries)})")
            for e in self.prior_entries:
                parts.append(
                    f"- [{e.timestamp}] {e.entry_type} by {e.actor_id} "
                    f"(chain_id={e.chain_id[:8]}): {e.summary}"
                )
            parts.append("")
        parts.append("Produce now. Do not block for more context.")
        return "\n".join(parts)


@dataclass(frozen=True)
class ChallengeContextPackage:
    skill_id: str
    convergence_state: ConvergenceState
    direction: str
    producing_output: str
    reasoning_trace: str

    def render(self) -> str:
        return (
            f"# Skill: {self.skill_id}\n"
            f"# Convergence state: {self.convergence_state}\n"
            f"\n"
            f"## Direction (from the human)\n"
            f"{self.direction.strip()}\n"
            f"\n"
            f"## Producing Agent output\n"
            f"{self.producing_output.strip()}\n"
            f"\n"
            f"## Producing Agent reasoning trace\n"
            f"{self.reasoning_trace.strip()}\n"
            f"\n"
            f"Challenge now. Be specific, cite evidence, assign severity."
        )


# ---- Builders ----


def _summarise_payload(payload: dict[str, Any]) -> str:
    """Compact payload to a one-line summary for context."""
    if not isinstance(payload, dict):
        return str(payload)[:_ENTRY_SUMMARY_CHAR_CAP]
    # Prefer the highest-signal keys.
    for key in ("direction", "crystallised", "output_excerpt",
                "verification_outcome", "subject", "summary"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()[:_ENTRY_SUMMARY_CHAR_CAP]
    # Fall back to the keys + a preview.
    keys = ",".join(sorted(payload.keys()))
    return f"keys={keys}"[:_ENTRY_SUMMARY_CHAR_CAP]


def _fetch_prior_entries(
    *, skill_id: str, max_prior_entries: int,
) -> list[PriorEntrySummary]:
    """Read the most recent chain entries for this skill, chronological order.

    Skill scoping is best-effort — we filter by payload_ref->>skill_id when
    present, else fall back to entries tagged with harness cycle entry_types.
    """
    with gov_session() as s:
        rows = s.execute(
            text(
                """
                SELECT chain_id, entry_type, actor_id, timestamp, payload_ref
                  FROM governance_chain
                 WHERE entry_type IN (
                     'direction_capture', 'production',
                     'adversarial_challenge', 'verification',
                     'cycle_close', 'frame_change_detected'
                 )
                   AND (
                     payload_ref->>'skill_id' = :skill
                     OR payload_ref->>'skill_id' IS NULL
                   )
                 ORDER BY timestamp DESC
                 LIMIT :n
                """
            ),
            {"skill": skill_id, "n": max_prior_entries},
        ).mappings().all()

    # Chronological order for the agent's reading.
    rows = list(reversed(rows))
    out: list[PriorEntrySummary] = []
    for r in rows:
        out.append(
            PriorEntrySummary(
                chain_id=str(r["chain_id"]),
                entry_type=r["entry_type"],
                actor_id=r["actor_id"],
                timestamp=r["timestamp"].isoformat() if r["timestamp"] else "",
                summary=_summarise_payload(r["payload_ref"] or {}),
            )
        )
    return out


def build_producing_package(
    *,
    skill_id: str,
    convergence_state: ConvergenceState,
    direction: str,
    knowledge_contribution: str | None,
    primary_derivation_intent: list[str] | None = None,
    max_prior_entries: int = 5,
) -> ProducingContextPackage:
    """Build the Producing Agent's context package.

    Reads the last N chain entries for this skill from governance_chain.
    """
    if convergence_state == "Explorative" and not knowledge_contribution:
        raise ValueError(
            "Knowledge contribution is required in Explorative state "
            "per INPUT-001 §2.1 / §3."
        )
    prior = _fetch_prior_entries(
        skill_id=skill_id, max_prior_entries=max_prior_entries,
    )
    return ProducingContextPackage(
        skill_id=skill_id,
        convergence_state=convergence_state,
        direction=direction,
        knowledge_contribution=knowledge_contribution,
        prior_entries=prior,
        primary_derivation_intent=primary_derivation_intent or [],
    )


def build_challenge_package(
    *,
    skill_id: str,
    convergence_state: ConvergenceState,
    direction: str,
    producing_output: str,
    reasoning_trace: str,
) -> ChallengeContextPackage:
    """Build the Adversarial Agent's narrow challenge package."""
    return ChallengeContextPackage(
        skill_id=skill_id,
        convergence_state=convergence_state,
        direction=direction,
        producing_output=producing_output,
        reasoning_trace=reasoning_trace,
    )
