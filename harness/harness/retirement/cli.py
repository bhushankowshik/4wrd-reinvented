"""Retire CLI — `harness retire` subcommand.

    harness retire write \\
        --cycle-id UUID \\
        --reason "Superseded by cycle X after MAS Notice 656"

    harness retire list
"""
from __future__ import annotations

import click

from harness.retirement.registry import list_retirements
from harness.retirement.tombstone import emit_tombstone


@click.group("retire")
def retire_group() -> None:
    """Theory retirement — tombstone entries and the registry."""


@retire_group.command("write")
@click.option("--cycle-id", required=True, help="The cycle to retire.")
@click.option("--reason", required=True, help="Why this cycle is retired.")
@click.option("--skill", "skill_id", default=None)
@click.option("--artefact-path", default=None)
@click.option("--successor", default=None, help="Cycle id that replaces this.")
@click.option("--retired-by", default="human")
def write_cmd(
    cycle_id: str,
    reason: str,
    skill_id: str | None,
    artefact_path: str | None,
    successor: str | None,
    retired_by: str,
) -> None:
    """Write one tombstone chain entry."""
    result = emit_tombstone(
        cycle_id=cycle_id,
        reason=reason,
        skill_id=skill_id,
        artefact_path=artefact_path,
        successor_cycle_id=successor,
        retired_by=retired_by,
    )
    click.secho("tombstone emitted", fg="green", bold=True)
    click.echo(f"  chain_id:   {result.chain_id}")
    click.echo(f"  timestamp:  {result.timestamp.isoformat()}")
    click.echo(f"  cycle_id:   {result.cycle_id}")
    click.echo(f"  reason:     {result.reason}")


@retire_group.command("list")
def list_cmd() -> None:
    """List every active tombstone on the chain (newest first)."""
    records = list_retirements()
    click.secho(f"# Retirements — {len(records)} tombstones", fg="cyan", bold=True)
    if not records:
        click.echo("(no tombstones yet)")
        return
    for r in records:
        click.echo(
            f"{r.timestamp.isoformat()}  cycle={r.cycle_id}  "
            f"skill={r.skill_id or '-'}  "
            f"successor={r.successor_cycle_id or '-'}"
        )
        click.echo(f"  reason:     {r.reason}")
        click.echo(f"  retired_by: {r.retired_by}")


if __name__ == "__main__":  # pragma: no cover
    retire_group()
