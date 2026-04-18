"""SOP ingestion pipeline — CLI entry point.

Usage:
  python -m services.sop_ingest.pipeline ingest PATH \
      --sop-id PROC-001 --sop-version v1 \
      --uploader pseudo-ad-001

  python -m services.sop_ingest.pipeline review INGEST_RUN_ID \
      --decision approved|rejected \
      --reviewer pseudo-au-001

Fulfils E6a §3.1 + E5 §2.6 + §5.5.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import click
from sqlalchemy import text

from services.chain_write.client import ChainWriteClient
from services.common.canonical import content_hash
from services.common.db import data_session
from services.common.telemetry import VALIDATION_FAILURES, configure_logging, log
from services.model_backend import get_model_backend
from services.secret_scanner.scan import scan as secret_scan
from services.sop_ingest.chunker import chunk_sections
from services.sop_ingest.parser import parse_sop


configure_logging()


def _emit_validation_failure(
    stage: str,
    rule_id: str,
    subject_ref: str,
    severity: str,
    details: dict,
    chain: ChainWriteClient,
) -> None:
    VALIDATION_FAILURES.labels(stage=stage, rule_id=rule_id, severity=severity).inc()
    failure_id = uuid.uuid4()
    ch = chain.emit(
        entry_type="validation_failure",
        actor_id="sop-ingest",
        actor_role="service_account",
        payload_ref={
            "failure_id": str(failure_id),
            "stage": stage,
            "rule_id": rule_id,
            "severity": severity,
            "subject_ref": subject_ref,
        },
    )
    with data_session() as s, s.begin():
        s.execute(
            text("""
                INSERT INTO validation_failure (
                  failure_id, stage, subject_ref, rule_id, rule_severity,
                  details, failure_chain_id
                )
                VALUES (:failure_id, :stage, :subject_ref, :rule_id,
                        :severity, CAST(:details AS JSONB), :chain_id)
            """),
            {
                "failure_id": str(failure_id),
                "stage": stage,
                "subject_ref": subject_ref,
                "rule_id": rule_id,
                "severity": severity,
                "details": json.dumps(details, default=str),
                "chain_id": ch["chain_id"],
            },
        )


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--sop-id", required=True)
@click.option("--sop-version", required=True)
@click.option("--uploader", required=True, help="Pseudonymous uploader ID")
def ingest(path: Path, sop_id: str, sop_version: str, uploader: str) -> None:
    """Parse, chunk, embed, and stage an SOP bundle.

    PATH may be a single file or a directory of files.
    """
    chain = ChainWriteClient()
    backend = get_model_backend()
    run_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    # Chain: sop_ingest_run_start
    chain.emit(
        entry_type="sop_ingest_run_start",
        actor_id=uploader,
        actor_role="admin",
        payload_ref={
            "ingest_run_id": str(run_id),
            "sop_id": sop_id,
            "sop_version": sop_version,
        },
    )

    files: list[Path] = (
        [path] if path.is_file()
        else sorted(
            f for f in path.rglob("*")
            if f.suffix.lower() in {".pdf", ".docx", ".md", ".txt"}
        )
    )
    if not files:
        _emit_validation_failure(
            stage="sop_ingest", rule_id="SOP-001",
            subject_ref=f"{sop_id}/{sop_version}", severity="reject",
            details={"path": str(path)}, chain=chain,
        )
        raise click.ClickException("no ingestible files found")

    all_sections = []
    for f in files:
        all_sections.extend(parse_sop(f))
    chunks = chunk_sections(all_sections)

    if not chunks:
        _emit_validation_failure(
            stage="sop_ingest", rule_id="SOP-005",
            subject_ref=f"{sop_id}/{sop_version}", severity="reject",
            details={"sections_parsed": len(all_sections)}, chain=chain,
        )
        raise click.ClickException("parsing produced 0 chunks")

    # Embed in batches.
    embeddings = backend.embed([c.text for c in chunks])

    # Run record.
    with data_session() as s, s.begin():
        s.execute(
            text("""
                INSERT INTO sop_ingest_run (
                  ingest_run_id, sop_id, sop_version, triggered_at,
                  triggered_by, source_count, chunk_count,
                  embedder_model_version, sme_review_state, ingest_chain_id
                ) VALUES (
                  :ingest_run_id, :sop_id, :sop_version, :triggered_at,
                  :triggered_by, :source_count, :chunk_count,
                  :embedder, 'pending', :chain_id
                )
            """),
            {
                "ingest_run_id": str(run_id),
                "sop_id": sop_id,
                "sop_version": sop_version,
                "triggered_at": now,
                "triggered_by": uploader,
                "source_count": len(files),
                "chunk_count": len(chunks),
                "embedder": backend.embedding_model(),
                "chain_id": str(uuid.uuid4()),
            },
        )

    # Chunk rows — all pending_review until SME approves.
    quarantined = 0
    with data_session() as s, s.begin():
        for c, emb in zip(chunks, embeddings):
            scan_result = secret_scan(c.text)
            if scan_result.max_severity in {"high", "medium"}:
                _emit_validation_failure(
                    stage="sop_ingest", rule_id="SOP-004",
                    subject_ref=f"{sop_id}/{sop_version}:{c.chunk_seq}",
                    severity="quarantine",
                    details={"matches": scan_result.as_dict()},
                    chain=chain,
                )
                quarantined += 1
                continue

            chunk_id = uuid.uuid4()
            body = {
                "sop_id": sop_id,
                "sop_version": sop_version,
                "section_path": c.section_path,
                "chunk_seq": c.chunk_seq,
                "text": c.text,
            }
            ch_bytes = content_hash(body)
            vec_lit = "[" + ",".join(f"{x:.6f}" for x in emb) + "]"
            s.execute(
                text("""
                    INSERT INTO sop_chunk (
                      chunk_id, sop_id, sop_version, section_path,
                      section_type, chunk_seq, text, embedding,
                      content_hash, ingest_at, source_uri, ingest_run_id,
                      lifecycle_state
                    )
                    VALUES (
                      :chunk_id, :sop_id, :sop_version, :section_path,
                      :section_type, :chunk_seq, :text,
                      CAST(:emb AS vector), :content_hash, :ingest_at,
                      :source_uri, :ingest_run_id, 'pending_review'
                    )
                    ON CONFLICT (sop_id, sop_version, chunk_seq) DO NOTHING
                """),
                {
                    "chunk_id": str(chunk_id),
                    "sop_id": sop_id,
                    "sop_version": sop_version,
                    "section_path": c.section_path,
                    "section_type": c.section_type,
                    "chunk_seq": c.chunk_seq,
                    "text": c.text,
                    "emb": vec_lit,
                    "content_hash": ch_bytes,
                    "ingest_at": now,
                    "source_uri": c.source_file,
                    "ingest_run_id": str(run_id),
                },
            )

    log.info(
        "sop_ingest.staged",
        sop_id=sop_id, sop_version=sop_version, chunks=len(chunks),
        quarantined=quarantined, ingest_run_id=str(run_id),
    )
    click.echo(
        f"ingest_run_id={run_id}  chunks={len(chunks)}  "
        f"quarantined={quarantined}  (pending SME review)"
    )


@cli.command()
@click.argument("ingest_run_id")
@click.option("--decision", type=click.Choice(["approved", "rejected"]), required=True)
@click.option("--reviewer", required=True, help="Pseudonymous SME ID")
def review(ingest_run_id: str, decision: str, reviewer: str) -> None:
    """Apply SME review to an ingest run (flips
    lifecycle_state or marks for purge)."""
    chain = ChainWriteClient()
    run_uuid = UUID(ingest_run_id)
    now = datetime.now(timezone.utc)
    chain.emit(
        entry_type="sop_ingest_sme_decision",
        actor_id=reviewer, actor_role="auditor",
        payload_ref={"ingest_run_id": str(run_uuid), "decision": decision},
    )

    with data_session() as s, s.begin():
        row = s.execute(
            text("""
                SELECT sop_id, sop_version FROM sop_ingest_run
                WHERE ingest_run_id = :rid
            """),
            {"rid": str(run_uuid)},
        ).mappings().first()
        if not row:
            raise click.ClickException(f"no ingest run {ingest_run_id}")
        sop_id, sop_version = row["sop_id"], row["sop_version"]

        s.execute(
            text("""
                UPDATE sop_ingest_run
                   SET sme_review_state = :d,
                       sme_reviewer_id = :r,
                       sme_reviewed_at = :ts,
                       activation_at = CASE WHEN :d='approved' THEN :ts ELSE activation_at END
                 WHERE ingest_run_id = :rid
            """),
            {"d": decision, "r": reviewer, "ts": now, "rid": str(run_uuid)},
        )

        if decision == "approved":
            # Flip this run's chunks to 'active'.
            s.execute(
                text("""
                    UPDATE sop_chunk SET lifecycle_state='active'
                    WHERE ingest_run_id = :rid
                      AND lifecycle_state='pending_review'
                """),
                {"rid": str(run_uuid)},
            )
            # Deprecate prior active chunks for same sop_id.
            s.execute(
                text("""
                    UPDATE sop_chunk
                       SET lifecycle_state='deprecation_window',
                           superseded_at=:ts
                     WHERE sop_id=:sop_id
                       AND sop_version <> :sop_version
                       AND lifecycle_state='active'
                """),
                {"ts": now, "sop_id": sop_id, "sop_version": sop_version},
            )
            chain.emit(
                entry_type="sop_version_activate", actor_id=reviewer,
                actor_role="auditor",
                payload_ref={"sop_id": sop_id, "sop_version": sop_version},
            )
            chain.emit(
                entry_type="sop_version_deprecate", actor_id=reviewer,
                actor_role="auditor",
                payload_ref={"sop_id": sop_id, "superseded_by": sop_version},
            )

    click.echo(f"run {ingest_run_id} → {decision}")


if __name__ == "__main__":
    cli()
