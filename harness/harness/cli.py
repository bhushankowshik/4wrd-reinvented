"""Harness CLI — run a governed Intent Cycle.

Usage (with uv):

    uv run harness run \\
        --skill S1 \\
        --convergence Explorative \\
        --direction "Crystallise the problem..." \\
        --knowledge "Context is ..." \\
        --pdi docs/foundation/INPUT-001-foundation-v4.md

Interactive mode: after Moment 2 the CLI prints the Producing Agent
output, reasoning trace, and adversarial challenges, and waits for
the human verifier to type CONFIRMED / PARTIAL / REJECTED plus notes.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from uuid import UUID

import click

from harness.agents.adversarial_agent import AdversarialOutput
from harness.agents.producing_agent import ProducingOutput
from harness.intent_cycle import (
    IntentCycle,
    Moment1Input,
    VerifierResponse,
)
from harness.layer2.cli import layer2_group
from harness.orchestrator.gate import gate_is_open
from harness.orchestrator.skill_sequence import (
    EXECUTION_SEQUENCE,
    SOLUTIONING_SEQUENCE,
    SkillSequence,
)
from harness.retirement.cli import retire_group
from harness.sidecar.receptor import sidecar_group
from harness.skills import SKILLS


def _interactive_verifier(
    *,
    producing: ProducingOutput,
    adversarial: AdversarialOutput,
    cycle_id: UUID,
    iteration: int,
) -> VerifierResponse:
    click.secho(
        f"\n==================== Moment 3 — Human Verifies ====================",
        fg="cyan", bold=True,
    )
    click.secho(f"cycle_id: {cycle_id}  iteration: {iteration}", fg="cyan")
    click.secho("\n--- Producing Agent output ---", fg="green", bold=True)
    click.echo(producing.output)
    click.secho("\n--- Producing Agent reasoning trace ---", fg="green", bold=True)
    click.echo(producing.reasoning_trace)
    click.secho("\n--- Adversarial challenges ---", fg="red", bold=True)
    click.echo(adversarial.render())
    if adversarial.frame_change_detected:
        click.secho(
            "\n[!] Adversarial agent raised a CRITICAL FRAME_CHANGE signal.",
            fg="yellow", bold=True,
        )

    click.secho(
        "\nVerdict options: CONFIRMED | PARTIAL | REJECTED",
        fg="cyan",
    )
    outcome = _ask_outcome()
    click.echo("Verification notes (optional): ", nl=False)
    sys.stdout.flush()
    notes = sys.stdin.readline().strip()
    refined: str | None = None
    if outcome != "CONFIRMED":
        click.echo("Refined direction for next iteration: ", nl=False)
        sys.stdout.flush()
        refined = sys.stdin.readline().strip()
        if not refined:
            click.secho(
                "Refined direction required for PARTIAL/REJECTED. "
                "Treating as CONFIRMED instead.",
                fg="yellow",
            )
            outcome = "CONFIRMED"
    return VerifierResponse(
        outcome=outcome, notes=notes, refined_direction=refined,
        verifier_actor_id="human",
    )


def _ask_outcome() -> str:
    import sys
    while True:
        click.echo("Outcome: ", nl=False)
        sys.stdout.flush()
        raw = sys.stdin.readline().strip().upper()
        if raw in ("CONFIRMED", "PARTIAL", "REJECTED"):
            return raw
        click.secho(
            "Must be one of CONFIRMED / PARTIAL / REJECTED.", fg="yellow",
        )


@click.group()
def main() -> None:
    """4WRD Claude Agent SDK governed delivery harness."""


@main.command("run")
@click.option("--skill", required=True, type=click.Choice(sorted(SKILLS.keys())))
@click.option(
    "--convergence",
    required=True,
    type=click.Choice(["Explorative", "Targeted", "Exact"]),
)
@click.option("--direction", required=True, help="The human direction for Moment 1.")
@click.option("--knowledge", default=None, help="Knowledge contribution (Explorative only).")
@click.option(
    "--pdi", "pdi_refs", multiple=True,
    help="Primary derivation intent reference (repeatable).",
)
@click.option(
    "--artefact-dir", default="docs",
    type=click.Path(file_okay=False, path_type=Path),
    help="Where to write the exit artefact.",
)
@click.option(
    "--max-iterations", default=3, type=int,
    help="Max Moment 2/3 loops on PARTIAL/REJECTED verification.",
)
@click.option(
    "--stream/--no-stream", default=True,
    help="Stream agent tokens to stderr as they arrive.",
)
def run(
    skill: str,
    convergence: str,
    direction: str,
    knowledge: str | None,
    pdi_refs: tuple[str, ...],
    artefact_dir: Path,
    max_iterations: int,
    stream: bool,
) -> None:
    """Run one governed Intent Cycle end-to-end."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise click.ClickException(
            "ANTHROPIC_API_KEY is not set — export it or add to .env.",
        )

    skill_def = SKILLS[skill]
    stream_to = sys.stderr if stream else None
    cycle = IntentCycle(
        skill=skill_def,
        verifier=_interactive_verifier,
        artefact_dir=artefact_dir,
        max_iterations=max_iterations,
        stream_agents_to=stream_to,
    )
    moment1 = Moment1Input(
        convergence_state=convergence,  # type: ignore[arg-type]
        direction=direction,
        knowledge_contribution=knowledge,
        primary_derivation_intent=list(pdi_refs),
    )

    click.secho(f"\n>>> Starting Intent Cycle for skill {skill}", fg="cyan", bold=True)
    result = cycle.run(moment1)

    click.secho("\n==================== Cycle summary ====================",
                fg="cyan", bold=True)
    click.echo(f"cycle_id:                 {result.cycle_id}")
    click.echo(f"iterations:               {result.iterations}")
    click.echo(f"convergence at exit:      {result.convergence_state_at_exit}")
    click.echo(f"chain entries written:    {len(result.chain_records)}")
    if result.artefact_path:
        click.secho(f"exit artefact:            {result.artefact_path}",
                    fg="green")
    else:
        click.secho("exit artefact:            (none — did not converge)",
                    fg="yellow")
    if result.anchor_chain_id:
        click.secho(f"master anchor chain_id:   {result.anchor_chain_id}",
                    fg="green")
    if result.frame_change and result.frame_change.frame_change:
        click.secho(
            f"frame change recorded:    chain_id={result.frame_change.chain_id}",
            fg="yellow",
        )


@main.command("list-skills")
def list_skills() -> None:
    """List available skill IDs."""
    for skill_id, skill in sorted(SKILLS.items()):
        click.echo(f"{skill_id}  {skill.name}")


def _pick_sequence(skill_id: str) -> SkillSequence:
    if skill_id.startswith("S"):
        return SOLUTIONING_SEQUENCE
    if skill_id.startswith("E"):
        return EXECUTION_SEQUENCE
    raise click.ClickException(
        f"skill {skill_id!r} does not belong to the S-prefix solutioning "
        f"sequence or the E-prefix execution sequence."
    )


@main.command("gate")
@click.option("--skill", required=True, help="Skill id, e.g. S2 / E4.")
def gate_cmd(skill: str) -> None:
    """Check the gate for a skill — chain-enforced via cycle_close at Exact."""
    sequence = _pick_sequence(skill)
    result = gate_is_open(skill_id=skill, sequence=sequence)
    if result.open:
        click.secho(f"[OPEN]   {result.reason}", fg="green", bold=True)
    else:
        click.secho(f"[BLOCKED] {result.reason}", fg="red", bold=True)
        if result.blocking_skill_id:
            click.echo(f"blocking predecessor: {result.blocking_skill_id}")


main.add_command(layer2_group)
main.add_command(sidecar_group)
main.add_command(retire_group)


if __name__ == "__main__":  # pragma: no cover
    main()
