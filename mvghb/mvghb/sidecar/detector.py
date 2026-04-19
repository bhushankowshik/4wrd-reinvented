"""Frame Change Sidecar Detector — in-session Tier 2 interrupt.

Two paths:

1. **Session-boundary scan** — `detect_session_boundary(window=N)` reads
   the last N chain entries to reconstruct session context. Surfaces a
   structured SessionContext that callers can compare against new
   direction received at session start. If the new direction
   contradicts session context, the caller should `emit_frame_change`
   with reason='session_boundary_mismatch'.

2. **In-session interrupt** — `render_challenge(receptor, signal)`
   produces a structured adversarial challenge prompt. Receptor sources
   are bounded by S5 §2.1 to {human, producing AI, adversarial AI}.

Both paths converge on `emit_frame_change` which writes a
'frame_change_detected' chain entry under the 'adversarial_agent'
actor (the receptor is recorded in payload).

This is deliberately small — the Sidecar's job in Wave 1 is to give us
a chain entry that says "frame change was claimed". Wave 2 will add
quorum decisioning over whether the claim is upheld.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID

from sqlalchemy import text

from mvghb.chain_write.writer import ChainWriter
from mvghb.common.db import gov_session
from mvghb.common.log import log


Receptor = Literal["human", "producing_ai", "adversarial_ai"]


@dataclass(frozen=True)
class SessionContext:
    """Reconstruction of recent session direction from chain entries."""
    last_n_entries: int
    actor_breakdown: dict[str, int]  # actor_id -> entry count
    last_entry_types: list[str]
    last_timestamp: datetime | None
    payload_topics: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SidecarChallenge:
    """Structured adversarial challenge prompt — Tier 2 interrupt."""
    receptor: Receptor
    signal: str
    prompt: str


# ----- Session boundary scan -----

def detect_session_boundary(*, window: int = 25) -> SessionContext:
    """Read last N entries from governance_chain; reconstruct session shape."""
    with gov_session() as s:
        rows = s.execute(text("""
            SELECT actor_id, entry_type, timestamp, payload_ref
              FROM governance_chain
             ORDER BY timestamp DESC
             LIMIT :n
        """), {"n": window}).mappings().all()

    actors: dict[str, int] = {}
    types: list[str] = []
    last_ts: datetime | None = None
    topics: list[str] = []

    for r in rows:
        a = r["actor_id"] or "(none)"
        actors[a] = actors.get(a, 0) + 1
        types.append(r["entry_type"])
        if last_ts is None:
            last_ts = r["timestamp"]
        # Heuristic topic surface: small set of payload keys.
        payload = r["payload_ref"] or {}
        for key in ("entry_type", "subject", "topic", "incident_id", "ctts_incident_ref"):
            v = payload.get(key)
            if isinstance(v, str) and v not in topics:
                topics.append(v)
                if len(topics) >= 10:
                    break

    return SessionContext(
        last_n_entries=len(rows),
        actor_breakdown=actors,
        last_entry_types=list(reversed(types)),  # chronological
        last_timestamp=last_ts,
        payload_topics=topics,
    )


# ----- In-session interrupt template -----

CHALLENGE_TEMPLATE = """\
[Frame Change Sidecar — Tier 2 interrupt]
receptor      : {receptor}
signal        : {signal}
issued_at     : {issued_at}

The producing agent's current direction may have drifted from the
ratified scope. Before continuing, address each of the following:

1. State the current Primary Derivation Intent verbatim.
2. List the artefacts whose ratified scope this work modifies.
3. Identify which seam/invariant (SEAM-1..5) is closest to the
   change vector. If none, state that explicitly.
4. Give the failure-mode hypothesis the adversarial signal points at.

If you cannot answer (1)-(3) without inventing context, halt and
re-load Primary Derivation Intent before any further write.
"""


def render_challenge(
    *, receptor: Receptor, signal: str,
    issued_at: datetime | None = None,
) -> SidecarChallenge:
    ts = (issued_at or datetime.now(timezone.utc)).isoformat()
    prompt = CHALLENGE_TEMPLATE.format(
        receptor=receptor, signal=signal, issued_at=ts,
    )
    return SidecarChallenge(receptor=receptor, signal=signal, prompt=prompt)


# ----- Emit frame_change_detected chain entry -----

def emit_frame_change(
    *,
    receptor: Receptor,
    signal: str,
    incident_id: UUID | None = None,
    context: SessionContext | None = None,
    writer: ChainWriter | None = None,
) -> UUID:
    """Write a frame_change_detected entry to governance_chain.

    Returns the new chain_id.
    """
    writer = writer or ChainWriter()
    payload: dict[str, Any] = {
        "receptor": receptor,
        "signal": signal,
        "detected_at": datetime.now(timezone.utc).isoformat(),
    }
    if context is not None:
        payload["context"] = {
            "last_n_entries": context.last_n_entries,
            "actor_breakdown": context.actor_breakdown,
            "recent_types": context.last_entry_types[-10:],
            "topics": context.payload_topics,
        }
    res = writer.emit(
        entry_type="frame_change_detected",
        actor_id="adversarial_agent",
        actor_role="adversarial_ai",
        incident_id=incident_id,
        payload_ref=payload,
    )
    log.info("mvghb.sidecar.frame_change_emitted",
             receptor=receptor, chain_id=str(res.chain_id))
    return res.chain_id
