"""Layer 2 CLI — operator / audit / replay views over governance_chain.

Usage:

    harness layer2 operator --skill S1 [--last-n 5]
    harness layer2 audit    --skill S1 [--since ISO] [--until ISO] [--limit N]
    harness layer2 replay

All three views are read-only projections. They call `operator_view`,
`audit_view`, and `session_replay_view` directly — no caching.
"""
from __future__ import annotations

import json
from datetime import datetime

import click

from harness.layer2.views import (
    audit_view,
    operator_view,
    session_replay_view,
)


def _iso(dt: datetime | None) -> str:
    return dt.isoformat() if dt else "(none)"


@click.group("layer2")
def layer2_group() -> None:
    """Layer 2 derived views over governance_chain."""


@layer2_group.command("operator")
@click.option("--skill", required=True, help="Skill id, e.g. S1.")
@click.option("--last-n", default=5, type=int, show_default=True)
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of text.")
def operator_cmd(skill: str, last_n: int, as_json: bool) -> None:
    """Last N cycles for a skill."""
    view = operator_view(skill_id=skill, last_n_cycles=last_n)
    if as_json:
        click.echo(json.dumps({
            "skill_id": view.skill_id,
            "cycles": [
                {
                    "cycle_id": c.cycle_id,
                    "direction": c.direction,
                    "convergence_state": c.convergence_state,
                    "verification_outcome": c.verification_outcome,
                    "iterations": c.iteration_count,
                    "challenges": c.adversarial_challenge_count,
                    "opened_at": _iso(c.opened_at),
                    "closed_at": _iso(c.closed_at),
                    "closed_at_exact": c.closed_at_exact,
                    "output_excerpt": c.output_excerpt,
                }
                for c in view.cycles
            ],
        }, indent=2))
        return

    click.secho(f"# Operator view — {view.skill_id}", fg="cyan", bold=True)
    if not view.cycles:
        click.echo("(no cycles on the chain yet)")
        return
    for c in view.cycles:
        click.secho(f"\n## cycle {c.cycle_id}", fg="green", bold=True)
        click.echo(f"- opened:             {_iso(c.opened_at)}")
        click.echo(f"- closed:             {_iso(c.closed_at)}  "
                   f"(Exact: {'yes' if c.closed_at_exact else 'no'})")
        click.echo(f"- convergence state:  {c.convergence_state or '(none)'}")
        click.echo(f"- direction:          {c.direction or '(none)'}")
        click.echo(f"- verification:       {c.verification_outcome or '(none)'}")
        click.echo(f"- iterations:         {c.iteration_count}")
        click.echo(f"- challenges raised:  {c.adversarial_challenge_count}")
        if c.output_excerpt:
            click.echo("- output excerpt:")
            for line in c.output_excerpt.splitlines()[:6]:
                click.echo(f"    {line}")


@layer2_group.command("audit")
@click.option("--skill", required=True)
@click.option("--since", default=None, help="ISO 8601 inclusive lower bound.")
@click.option("--until", default=None, help="ISO 8601 exclusive upper bound.")
@click.option("--limit", default=2000, type=int, show_default=True)
@click.option("--json", "as_json", is_flag=True)
def audit_cmd(
    skill: str, since: str | None, until: str | None, limit: int, as_json: bool,
) -> None:
    """Full chain slice for a skill + date range."""
    since_dt = datetime.fromisoformat(since) if since else None
    until_dt = datetime.fromisoformat(until) if until else None
    view = audit_view(
        skill_id=skill, since=since_dt, until=until_dt, limit=limit,
    )
    if as_json:
        click.echo(json.dumps({
            "skill_id": view.skill_id,
            "since": _iso(view.since),
            "until": _iso(view.until),
            "row_count": len(view.rows),
            "rows": [
                {
                    "chain_id": r.chain_id,
                    "entry_type": r.entry_type,
                    "actor_id": r.actor_id,
                    "timestamp": r.timestamp.isoformat(),
                    "cycle_id": r.payload_ref.get("cycle_id"),
                    "iteration": r.payload_ref.get("iteration"),
                }
                for r in view.rows
            ],
        }, indent=2))
        return

    click.secho(
        f"# Audit view — {view.skill_id}  "
        f"({_iso(view.since)} → {_iso(view.until)})",
        fg="cyan", bold=True,
    )
    click.echo(f"rows: {len(view.rows)}")
    for r in view.rows:
        click.echo(
            f"{r.timestamp.isoformat()}  "
            f"{r.entry_type:<25}  {r.actor_id:<20}  "
            f"cycle={r.payload_ref.get('cycle_id', '-')}  "
            f"chain={r.chain_id[:8]}"
        )


@layer2_group.command("replay")
@click.option("--json", "as_json", is_flag=True)
def replay_cmd(as_json: bool) -> None:
    """Cold-start session replay — where did I leave off, per skill."""
    view = session_replay_view()
    if as_json:
        click.echo(json.dumps({
            "generated_at": view.generated_at.isoformat(),
            "skill_frames": [
                {
                    "skill_id": f.skill_id,
                    "last_cycle_id": f.last_cycle_id,
                    "last_convergence_state": f.last_convergence_state,
                    "last_outcome": f.last_outcome,
                    "last_direction": f.last_direction,
                    "last_closed_at_exact": f.last_closed_at_exact,
                    "last_artefact_path": f.last_artefact_path,
                    "unresolved_partial": f.unresolved_partial,
                    "last_activity_at": _iso(f.last_activity_at),
                }
                for f in view.skill_frames
            ],
        }, indent=2))
        return
    click.echo(view.render())


if __name__ == "__main__":  # pragma: no cover
    layer2_group()
