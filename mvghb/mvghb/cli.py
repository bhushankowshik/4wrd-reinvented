"""mvghb CLI — bootstrap, anchor, verify, sidecar."""
from __future__ import annotations

import json
import sys
from uuid import UUID

import click


@click.group()
def main() -> None:
    """MVGH-β Wave 1 governance harness CLI."""


# ----- bootstrap -----

@main.group()
def bootstrap() -> None:
    """Bootstrap the harness (first-run init)."""


@bootstrap.command("init")
@click.option("--gov-dsn", default=None, help="noc-gov DSN. Defaults to env or localhost.")
def bootstrap_init(gov_dsn: str | None) -> None:
    """Generate KEK, apply schema, seed actors, mint genesis + first anchor."""
    from mvghb.bootstrap import init_first_run
    result = init_first_run(gov_dsn=gov_dsn)
    click.echo(json.dumps(result, indent=2))


# ----- anchor -----

@main.group()
def anchor() -> None:
    """Master anchor commands."""


@anchor.command("commit")
def anchor_commit() -> None:
    from mvghb.master_anchor import commit_anchor
    res = commit_anchor()
    if res is None:
        click.echo("(no heads — nothing anchored)")
        return
    click.echo(json.dumps({
        "anchor_id": str(res.anchor_id),
        "anchor_chain_id": str(res.anchor_chain_id),
        "anchor_hmac_hex": res.anchor_hmac.hex(),
        "actor_count": len(res.head_set),
        "anchored_at": res.anchored_at.isoformat(),
    }, indent=2))


@anchor.command("verify")
@click.argument("anchor_id")
def anchor_verify(anchor_id: str) -> None:
    from mvghb.master_anchor import verify_anchor
    ok, detail = verify_anchor(UUID(anchor_id))
    click.echo(json.dumps({"ok": ok, "detail": detail}, indent=2))
    sys.exit(0 if ok else 1)


@anchor.command("daemon")
@click.option("--interval", default=60, type=int)
def anchor_daemon(interval: int) -> None:
    from mvghb.master_anchor.anchor import run_periodic
    run_periodic(interval_sec=interval)


# ----- verify -----

@main.command("verify")
@click.option("--actor", default=None, help="Single actor; default = all.")
def verify(actor: str | None) -> None:
    from mvghb.integrity_verifier import verify_actor_chain, verify_all_chains
    reports = [verify_actor_chain(actor)] if actor else verify_all_chains()
    out = {
        "actors_checked": len(reports),
        "total_entries": sum(r.entries_checked for r in reports),
        "total_mismatches": sum(len(r.mismatches) for r in reports),
        "reports": [
            {
                "actor_id": r.actor_id,
                "entries_checked": r.entries_checked,
                "ok": r.ok,
                "mismatches": [
                    {"chain_id": str(m.chain_id), "kind": m.kind, "detail": m.detail}
                    for m in r.mismatches
                ],
            }
            for r in reports
        ],
    }
    click.echo(json.dumps(out, indent=2))
    sys.exit(0 if out["total_mismatches"] == 0 else 1)


# ----- sidecar -----

@main.group()
def sidecar() -> None:
    """Frame Change Sidecar Detector commands."""


@sidecar.command("scan")
@click.option("--window", default=25, type=int)
def sidecar_scan(window: int) -> None:
    from mvghb.sidecar import detect_session_boundary
    ctx = detect_session_boundary(window=window)
    click.echo(json.dumps({
        "last_n_entries": ctx.last_n_entries,
        "actor_breakdown": ctx.actor_breakdown,
        "recent_types": ctx.last_entry_types,
        "topics": ctx.payload_topics,
        "last_timestamp": ctx.last_timestamp.isoformat() if ctx.last_timestamp else None,
    }, indent=2))


@sidecar.command("challenge")
@click.option("--receptor", type=click.Choice(["human", "producing_ai", "adversarial_ai"]),
              required=True)
@click.option("--signal", required=True)
def sidecar_challenge(receptor: str, signal: str) -> None:
    from mvghb.sidecar import render_challenge
    ch = render_challenge(receptor=receptor, signal=signal)
    click.echo(ch.prompt)


@sidecar.command("emit")
@click.option("--receptor", type=click.Choice(["human", "producing_ai", "adversarial_ai"]),
              required=True)
@click.option("--signal", required=True)
def sidecar_emit(receptor: str, signal: str) -> None:
    from mvghb.sidecar import emit_frame_change, detect_session_boundary
    ctx = detect_session_boundary()
    cid = emit_frame_change(receptor=receptor, signal=signal, context=ctx)
    click.echo(json.dumps({"chain_id": str(cid)}, indent=2))


if __name__ == "__main__":
    main()
