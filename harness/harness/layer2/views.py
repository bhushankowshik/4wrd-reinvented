"""Layer 2 derived views.

Read-only projections computed from governance_chain entries. All three
views share a small entry-fetch helper so behaviour stays consistent:

  `_fetch_cycle_entries(skill_id, since, until, limit)`

Per INPUT-001 §2.2 Layer 2 is computed fresh per request, not cached.

All views are designed to be callable with or without a live database:
tests inject a fake `fetcher` callable that returns canonical rows.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Iterable

from sqlalchemy import text

from mvghb.common.db import gov_session


# ---- Types ----


@dataclass(frozen=True)
class ChainEntryRow:
    """Canonical row shape used by all views."""
    chain_id: str
    entry_type: str
    actor_id: str
    timestamp: datetime
    payload_ref: dict[str, Any]


@dataclass(frozen=True)
class CycleSummary:
    """One cycle's compact summary — used by operator_view."""
    cycle_id: str
    skill_id: str
    direction: str | None
    convergence_state: str | None
    output_excerpt: str | None
    verification_outcome: str | None
    adversarial_challenge_count: int
    iteration_count: int
    opened_at: datetime | None
    closed_at: datetime | None
    closed_at_exact: bool


@dataclass(frozen=True)
class OperatorView:
    skill_id: str
    cycles: list[CycleSummary]


@dataclass(frozen=True)
class AuditView:
    skill_id: str
    since: datetime | None
    until: datetime | None
    rows: list[ChainEntryRow]


@dataclass(frozen=True)
class SkillFrame:
    """Where a skill was left — session replay per-skill."""
    skill_id: str
    last_cycle_id: str | None
    last_convergence_state: str | None
    last_outcome: str | None
    last_direction: str | None
    last_closed_at_exact: bool
    last_artefact_path: str | None
    unresolved_partial: bool
    last_activity_at: datetime | None


@dataclass(frozen=True)
class SessionReplayView:
    generated_at: datetime
    skill_frames: list[SkillFrame]

    def render(self) -> str:
        lines: list[str] = [
            "# Session replay — where did I leave off",
            f"_generated at {self.generated_at.isoformat()}_",
            "",
        ]
        if not self.skill_frames:
            lines.append("(no governed cycles on the chain yet)")
            return "\n".join(lines)
        for f in self.skill_frames:
            lines.append(f"## {f.skill_id}")
            lines.append(f"- last cycle: {f.last_cycle_id or '(none)'}")
            lines.append(f"- convergence state at last cycle: "
                         f"{f.last_convergence_state or '(none)'}")
            lines.append(f"- verification outcome: {f.last_outcome or '(none)'}")
            lines.append(
                f"- closed at Exact: {'yes' if f.last_closed_at_exact else 'no'}"
            )
            lines.append(
                f"- unresolved PARTIAL: "
                f"{'yes' if f.unresolved_partial else 'no'}"
            )
            if f.last_artefact_path:
                lines.append(f"- last artefact: {f.last_artefact_path}")
            if f.last_direction:
                lines.append(f"- last direction: {f.last_direction}")
            if f.last_activity_at:
                lines.append(
                    f"- last activity: {f.last_activity_at.isoformat()}"
                )
            lines.append("")
        return "\n".join(lines)


# ---- Fetch ----


# Entry types that belong to a governed cycle.
_CYCLE_ENTRY_TYPES = (
    "direction_capture",
    "production",
    "adversarial_challenge",
    "verification",
    "cycle_close",
    "research",
    "artefact_lineage",
    "frame_change_detected",
    "frame_change_signal",
    "tombstone",
)


Fetcher = Callable[..., list[ChainEntryRow]]


def _default_fetcher(
    *,
    skill_id: str | None,
    since: datetime | None,
    until: datetime | None,
    limit: int,
) -> list[ChainEntryRow]:
    """Default fetcher — reads governance_chain via mvghb's gov_session."""
    clauses = ["entry_type = ANY(:types)"]
    params: dict[str, Any] = {
        "types": list(_CYCLE_ENTRY_TYPES),
        "limit": limit,
    }
    if skill_id is not None:
        clauses.append("payload_ref->>'skill_id' = :skill")
        params["skill"] = skill_id
    if since is not None:
        clauses.append("timestamp >= :since")
        params["since"] = since
    if until is not None:
        clauses.append("timestamp < :until")
        params["until"] = until
    where = " AND ".join(clauses)

    sql = text(
        f"""
        SELECT chain_id, entry_type, actor_id, timestamp, payload_ref
          FROM governance_chain
         WHERE {where}
         ORDER BY timestamp ASC
         LIMIT :limit
        """
    )
    with gov_session() as s:
        rows = s.execute(sql, params).mappings().all()

    out: list[ChainEntryRow] = []
    for r in rows:
        payload = r["payload_ref"] or {}
        if not isinstance(payload, dict):
            payload = {"_raw": payload}
        out.append(
            ChainEntryRow(
                chain_id=str(r["chain_id"]),
                entry_type=r["entry_type"],
                actor_id=r["actor_id"],
                timestamp=r["timestamp"],
                payload_ref=payload,
            )
        )
    return out


# ---- View computation ----


def _group_by_cycle(rows: Iterable[ChainEntryRow]) -> dict[str, list[ChainEntryRow]]:
    buckets: dict[str, list[ChainEntryRow]] = defaultdict(list)
    for r in rows:
        cid = r.payload_ref.get("cycle_id")
        if not isinstance(cid, str):
            continue
        buckets[cid].append(r)
    # Preserve chronological order within each cycle.
    for cid in buckets:
        buckets[cid].sort(key=lambda r: r.timestamp)
    return buckets


def _summarise_cycle(rows: list[ChainEntryRow]) -> CycleSummary:
    cycle_id = rows[0].payload_ref.get("cycle_id", "")
    skill_id = rows[0].payload_ref.get("skill_id", "")

    direction: str | None = None
    convergence: str | None = None
    output_excerpt: str | None = None
    outcome: str | None = None
    challenge_count = 0
    iteration_count = 0
    opened_at = rows[0].timestamp
    closed_at: datetime | None = None
    closed_at_exact = False

    for r in rows:
        p = r.payload_ref
        if r.entry_type == "direction_capture":
            direction = p.get("direction")
            convergence = p.get("convergence_state")
        elif r.entry_type == "production":
            output_excerpt = p.get("output_excerpt")
            try:
                iteration_count = max(iteration_count, int(p.get("iteration", 0)))
            except (TypeError, ValueError):
                pass
        elif r.entry_type == "adversarial_challenge":
            challenges = p.get("challenges") or []
            challenge_count += len(challenges) if isinstance(challenges, list) else 0
        elif r.entry_type == "verification":
            outcome = p.get("verification_outcome")
        elif r.entry_type == "cycle_close":
            closed_at = r.timestamp
            exit_state = p.get("convergence_state_at_exit")
            closed_at_exact = exit_state == "Exact"
    return CycleSummary(
        cycle_id=str(cycle_id),
        skill_id=str(skill_id),
        direction=direction,
        convergence_state=convergence,
        output_excerpt=output_excerpt,
        verification_outcome=outcome,
        adversarial_challenge_count=challenge_count,
        iteration_count=iteration_count,
        opened_at=opened_at,
        closed_at=closed_at,
        closed_at_exact=closed_at_exact,
    )


# ---- Public views ----


def operator_view(
    *,
    skill_id: str,
    last_n_cycles: int = 5,
    fetcher: Fetcher | None = None,
) -> OperatorView:
    """Last N cycles for a skill: direction, output excerpt, outcome, challenges."""
    f = fetcher or _default_fetcher
    rows = f(skill_id=skill_id, since=None, until=None, limit=500)
    buckets = _group_by_cycle(rows)
    summaries = sorted(
        (_summarise_cycle(rs) for rs in buckets.values()),
        key=lambda c: (c.opened_at or datetime.min.replace(tzinfo=timezone.utc)),
        reverse=True,
    )
    return OperatorView(
        skill_id=skill_id, cycles=summaries[:last_n_cycles],
    )


def audit_view(
    *,
    skill_id: str,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = 2000,
    fetcher: Fetcher | None = None,
) -> AuditView:
    """Full chain slice for a skill + date range — every entry type."""
    f = fetcher or _default_fetcher
    rows = f(skill_id=skill_id, since=since, until=until, limit=limit)
    return AuditView(skill_id=skill_id, since=since, until=until, rows=rows)


def session_replay_view(
    *,
    fetcher: Fetcher | None = None,
) -> SessionReplayView:
    """Cold-start view — last cycle per skill with the operator-relevant state."""
    f = fetcher or _default_fetcher
    rows = f(skill_id=None, since=None, until=None, limit=5000)

    per_skill: dict[str, list[ChainEntryRow]] = defaultdict(list)
    for r in rows:
        sid = r.payload_ref.get("skill_id")
        if isinstance(sid, str):
            per_skill[sid].append(r)

    frames: list[SkillFrame] = []
    for sid, rs in sorted(per_skill.items()):
        buckets = _group_by_cycle(rs)
        if not buckets:
            continue
        # Pick the latest-opened cycle.
        summaries = [_summarise_cycle(bucket) for bucket in buckets.values()]
        summaries.sort(
            key=lambda c: (c.opened_at or datetime.min.replace(tzinfo=timezone.utc)),
            reverse=True,
        )
        last = summaries[0]
        # Detect any unresolved PARTIAL in this skill's recent history.
        unresolved_partial = any(
            c.verification_outcome == "PARTIAL" and not c.closed_at_exact
            for c in summaries[:5]
        )
        # Last artefact path — look up in the latest cycle_close entry.
        last_artefact: str | None = None
        for r in reversed(buckets[last.cycle_id]):
            if r.entry_type == "cycle_close":
                val = r.payload_ref.get("artefact_path")
                if isinstance(val, str):
                    last_artefact = val
                break
        frames.append(
            SkillFrame(
                skill_id=sid,
                last_cycle_id=last.cycle_id,
                last_convergence_state=last.convergence_state,
                last_outcome=last.verification_outcome,
                last_direction=last.direction,
                last_closed_at_exact=last.closed_at_exact,
                last_artefact_path=last_artefact,
                unresolved_partial=unresolved_partial,
                last_activity_at=last.closed_at or last.opened_at,
            )
        )
    return SessionReplayView(
        generated_at=datetime.now(timezone.utc),
        skill_frames=frames,
    )
