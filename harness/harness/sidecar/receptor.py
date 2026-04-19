"""External Frame Change Receptor — six canonical sources.

Per INPUT-001 §2.3 / §5 the Sidecar is always-live. Tier 2 covers
in-session signals (human / producing_ai / adversarial_ai) and writes
`frame_change_detected` entries. But frame change can also land from
OUTSIDE the cycle — a new regulator notice, a production incident, a
stakeholder email. That's what this receptor is for.

Six canonical external sources:

  upstream_contract   — an upstream API / schema / contract changed
  regulatory          — a new regulation / audit finding / compliance ask
  ops_incident        — a production incident or new severity event
  market              — a business / market / competitive shift
  research            — new research that invalidates prior assumption
  stakeholder         — an explicit external stakeholder ask

Each external signal lands on the chain as a `frame_change_signal`
entry (NOT `frame_change_detected`) so Layer 2 can distinguish
in-session from out-of-band signals.

CLI (wired as `harness sidecar`):

  harness sidecar signal \\
      --source regulatory \\
      --signal "MAS Notice 656 effective 2026-06-01; repaper all MAS TRM skills" \\
      [--skill S3] [--cycle-id UUID] [--evidence-ref URL]

Writes one chain entry via MVGH-β Wave 1 ChainWriter.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID

import click

from mvghb.chain_write.writer import ChainWriter


ExternalReceptor = Literal[
    "upstream_contract",
    "regulatory",
    "ops_incident",
    "market",
    "research",
    "stakeholder",
]


EXTERNAL_RECEPTORS: tuple[ExternalReceptor, ...] = (
    "upstream_contract",
    "regulatory",
    "ops_incident",
    "market",
    "research",
    "stakeholder",
)


@dataclass(frozen=True)
class ExternalSignalResult:
    chain_id: UUID
    timestamp: datetime
    receptor: ExternalReceptor
    signal: str


def emit_frame_change_signal(
    *,
    receptor: ExternalReceptor,
    signal: str,
    skill_id: str | None = None,
    cycle_id: UUID | str | None = None,
    evidence_ref: str | None = None,
    submitter_actor_id: str = "human",
    writer: ChainWriter | None = None,
) -> ExternalSignalResult:
    """Write a `frame_change_signal` entry to governance_chain."""
    if receptor not in EXTERNAL_RECEPTORS:
        raise ValueError(
            f"receptor must be one of {EXTERNAL_RECEPTORS}; got {receptor!r}"
        )
    if not signal.strip():
        raise ValueError("signal must be non-empty.")

    writer = writer or ChainWriter()
    payload: dict[str, Any] = {
        "receptor": receptor,
        "signal": signal,
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "submitter_actor_id": submitter_actor_id,
    }
    if skill_id is not None:
        payload["skill_id"] = skill_id
    if cycle_id is not None:
        payload["cycle_id"] = str(cycle_id)
    if evidence_ref is not None:
        payload["evidence_ref"] = evidence_ref

    res = writer.emit(
        entry_type="frame_change_signal",
        actor_id=submitter_actor_id,
        actor_role="human_operator",
        incident_id=None,
        payload_ref=payload,
    )
    return ExternalSignalResult(
        chain_id=res.chain_id,
        timestamp=res.timestamp,
        receptor=receptor,
        signal=signal,
    )


# ---- CLI ----


@click.group("sidecar")
def sidecar_group() -> None:
    """Frame Change Sidecar — external signal injection + scans."""


@sidecar_group.command("signal")
@click.option(
    "--source", "receptor", required=True,
    type=click.Choice(list(EXTERNAL_RECEPTORS)),
    help="Which external receptor is raising this signal.",
)
@click.option("--signal", "signal_text", required=True,
              help="One-line description of the frame change.")
@click.option("--skill", "skill_id", default=None,
              help="Skill id this signal should be attributed to (optional).")
@click.option("--cycle-id", default=None, help="Cycle id (optional).")
@click.option("--evidence-ref", default=None,
              help="URL / file path / ticket id backing the signal.")
@click.option("--submitter", default="human",
              help="Actor id of the human submitting this signal.")
def signal_cmd(
    receptor: str,
    signal_text: str,
    skill_id: str | None,
    cycle_id: str | None,
    evidence_ref: str | None,
    submitter: str,
) -> None:
    """Emit one `frame_change_signal` chain entry from an external receptor."""
    result = emit_frame_change_signal(
        receptor=receptor,  # type: ignore[arg-type]
        signal=signal_text,
        skill_id=skill_id,
        cycle_id=cycle_id,
        evidence_ref=evidence_ref,
        submitter_actor_id=submitter,
    )
    click.secho("frame_change_signal emitted", fg="green", bold=True)
    click.echo(f"  chain_id:   {result.chain_id}")
    click.echo(f"  timestamp:  {result.timestamp.isoformat()}")
    click.echo(f"  receptor:   {result.receptor}")
    click.echo(f"  signal:     {result.signal}")


@sidecar_group.command("scan")
@click.option("--direction", required=True,
              help="New direction to compare against the recent chain shape.")
@click.option("--window", default=25, type=int, show_default=True)
def scan_cmd(direction: str, window: int) -> None:
    """Run the session boundary scan and print the drift verdict."""
    from harness.sidecar.detector import run_session_boundary_scan

    result = run_session_boundary_scan(new_direction=direction, window=window)
    ctx = result.context
    click.secho(
        f"# Session boundary scan (last {ctx.last_n_entries} entries)",
        fg="cyan", bold=True,
    )
    click.echo(f"last entry types: {ctx.last_entry_types[-10:]}")
    click.echo(f"actor breakdown:  {ctx.actor_breakdown}")
    click.echo(f"topic sample:     {ctx.payload_topics[:10]}")
    if result.likely_drift:
        click.secho(f"\n[drift] {result.drift_reason}", fg="yellow", bold=True)
    else:
        click.secho("\nno drift signal (direction overlaps prior topics).",
                    fg="green")


if __name__ == "__main__":  # pragma: no cover
    sidecar_group()
