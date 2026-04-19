"""Master Anchor — periodic commit of per-actor chain heads.

Per spec:
  - Anchor record = HMAC over sorted (actor_id, chain_head_id) pairs.
  - Stored in governance_chain with entry_type='master_anchor'.
  - Verifiable: given actor heads, recompute anchor HMAC and compare.

The anchor is itself a chain entry signed by the 'orchestrator' actor —
this gives us a single tamper-evident pointer that fixes the state of
every per-actor chain at a point in time. Wave 2 quorum will replace the
sole-orchestrator signer with multi-actor co-signing.

We use a fixed HKDF info string for the anchor key (anchor_key info =
b"mvghb-master-anchor-v1") rather than per-entry derivation, so that the
anchor HMAC is reproducible from KEK + heads alone — no need to look up
the per-entry key for the anchor's own chain entry. The chain entry
*also* gets a per-entry HMAC via ChainWriter; the anchor_hmac stored in
mvghb_master_anchor is the additional per-anchor HMAC over the head set.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from uuid import UUID, uuid4

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from sqlalchemy import text
from sqlalchemy.orm import Session

from mvghb.chain_write.writer import ChainWriter
from mvghb.common import actors as actor_reg
from mvghb.common.canonical import canonical_bytes
from mvghb.common.crypto import HKDF_LEN, hmac_sha256
from mvghb.common.db import gov_session
from mvghb.common.log import log
from mvghb.common.settings import get_settings


ANCHOR_HKDF_INFO = b"mvghb-master-anchor-v1"
ANCHOR_ACTOR_ID = "orchestrator"
ANCHOR_ACTOR_ROLE = "orchestrator"


@dataclass(frozen=True)
class AnchorResult:
    anchor_id: UUID
    anchor_chain_id: UUID
    anchor_hmac: bytes
    head_set: list[tuple[str, UUID]]
    anchored_at: datetime
    prev_anchor_id: UUID | None


def _anchor_key(kek: bytes) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=HKDF_LEN,
        salt=None,
        info=ANCHOR_HKDF_INFO,
    ).derive(kek)


def compute_anchor_hmac(
    kek: bytes, head_set: Iterable[tuple[str, UUID]],
) -> bytes:
    """Pure function — given KEK + heads, return the anchor HMAC.

    Used both by commit_anchor (to compute) and verify_anchor (to recompute).
    """
    sorted_pairs = sorted(
        ((actor_id, str(chain_id)) for actor_id, chain_id in head_set),
        key=lambda p: p[0],
    )
    body = canonical_bytes({"heads": sorted_pairs})
    return hmac_sha256(_anchor_key(kek), body)


def commit_anchor(
    *, writer: ChainWriter | None = None,
) -> AnchorResult | None:
    """Snapshot current heads, sign with the anchor key, write anchor entry.

    Returns None if there are no heads yet (nothing to anchor).
    """
    s_settings = get_settings()
    writer = writer or ChainWriter()

    with gov_session() as s:
        heads = actor_reg.all_heads(s)
        if not heads:
            log.info("mvghb.anchor.no_heads")
            return None
        head_set = [(h.actor_id, h.head_chain_id) for h in heads]

        prev_row = s.execute(text("""
            SELECT anchor_id FROM mvghb_master_anchor
             ORDER BY anchored_at DESC LIMIT 1
        """)).first()
        prev_anchor_id = prev_row[0] if prev_row else None

    anchor_hmac = compute_anchor_hmac(s_settings.kek, head_set)
    anchor_id = uuid4()

    # Emit the anchor as a chain entry under the orchestrator actor.
    emit = writer.emit(
        entry_type="master_anchor",
        actor_id=ANCHOR_ACTOR_ID,
        actor_role=ANCHOR_ACTOR_ROLE,
        incident_id=None,
        payload_ref={
            "anchor_id": str(anchor_id),
            "head_set": [{"actor_id": a, "chain_head_id": str(c)}
                         for a, c in sorted(head_set, key=lambda p: p[0])],
            "anchor_hmac_hex": anchor_hmac.hex(),
            "prev_anchor_id": str(prev_anchor_id) if prev_anchor_id else None,
            "actor_count": len(head_set),
        },
    )

    with gov_session() as s, s.begin():
        s.execute(text("""
            INSERT INTO mvghb_master_anchor
              (anchor_id, anchor_chain_id, actor_count, anchor_hmac, prev_anchor_id)
            VALUES
              (:aid, :cid, :n, :hmac, :prev)
        """), {
            "aid": str(anchor_id),
            "cid": str(emit.chain_id),
            "n": len(head_set),
            "hmac": anchor_hmac,
            "prev": str(prev_anchor_id) if prev_anchor_id else None,
        })

    log.info(
        "mvghb.anchor.committed",
        anchor_id=str(anchor_id),
        anchor_chain_id=str(emit.chain_id),
        actor_count=len(head_set),
    )
    return AnchorResult(
        anchor_id=anchor_id,
        anchor_chain_id=emit.chain_id,
        anchor_hmac=anchor_hmac,
        head_set=sorted(head_set, key=lambda p: p[0]),
        anchored_at=emit.timestamp,
        prev_anchor_id=prev_anchor_id,
    )


def verify_anchor(anchor_id: UUID) -> tuple[bool, str]:
    """Recompute the anchor HMAC from current state of mvghb_master_anchor.

    Returns (ok, detail). Detail is empty on success or describes the
    mismatch reason on failure.
    """
    s_settings = get_settings()
    with gov_session() as s:
        anchor_row = s.execute(text("""
            SELECT anchor_id, anchor_chain_id, anchor_hmac, actor_count
              FROM mvghb_master_anchor
             WHERE anchor_id = :a
        """), {"a": str(anchor_id)}).first()
        if not anchor_row:
            return False, f"anchor_id {anchor_id} not found"

        chain_row = s.execute(text("""
            SELECT payload_ref FROM governance_chain
             WHERE chain_id = :c AND entry_type = 'master_anchor'
             LIMIT 1
        """), {"c": str(anchor_row[1])}).first()
        if not chain_row:
            return False, "anchor chain entry missing in governance_chain"

        head_set = [
            (h["actor_id"], UUID(h["chain_head_id"]))
            for h in chain_row[0].get("head_set", [])
        ]

    recomputed = compute_anchor_hmac(s_settings.kek, head_set)
    if recomputed != bytes(anchor_row[2]):
        return False, "anchor HMAC mismatch"
    if len(head_set) != anchor_row[3]:
        return False, "actor_count mismatch"
    return True, ""


def run_periodic(*, interval_sec: int = 60) -> None:
    """Daemon entry — commit an anchor every interval_sec."""
    import time
    writer = ChainWriter()
    log.info("mvghb.anchor.daemon_start", interval_sec=interval_sec)
    while True:
        try:
            commit_anchor(writer=writer)
        except Exception as exc:  # noqa: BLE001
            log.warning("mvghb.anchor.commit_error", error=str(exc))
        time.sleep(interval_sec)
