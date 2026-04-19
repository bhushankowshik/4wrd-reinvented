"""Actor registry helpers — read/write mvghb_actor + mvghb_actor_head."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


# Wave 1 default actors. Bootstrap seeds these; ChainWriter rejects unknown actors.
DEFAULT_ACTORS: list[tuple[str, str, str]] = [
    # (actor_id, actor_role, ownership_tier)
    ("orchestrator",      "orchestrator",      "user"),
    ("producing_agent",   "producing_ai",      "user"),
    ("adversarial_agent", "adversarial_ai",    "user"),
    ("human",             "human_operator",    "user"),
]


@dataclass(frozen=True)
class ActorRecord:
    actor_id: str
    actor_role: str
    ownership_tier: str
    genesis_chain_id: UUID | None


@dataclass(frozen=True)
class HeadRecord:
    actor_id: str
    head_chain_id: UUID
    head_timestamp: datetime
    entry_count: int


def list_actors(s: Session) -> list[ActorRecord]:
    rows = s.execute(text("""
        SELECT actor_id, actor_role, ownership_tier, genesis_chain_id
          FROM mvghb_actor
         WHERE retired_at IS NULL
         ORDER BY actor_id
    """)).all()
    return [
        ActorRecord(
            actor_id=r[0], actor_role=r[1], ownership_tier=r[2],
            genesis_chain_id=r[3],
        ) for r in rows
    ]


def get_actor(s: Session, actor_id: str) -> ActorRecord | None:
    r = s.execute(text("""
        SELECT actor_id, actor_role, ownership_tier, genesis_chain_id
          FROM mvghb_actor
         WHERE actor_id = :a
    """), {"a": actor_id}).first()
    if not r:
        return None
    return ActorRecord(
        actor_id=r[0], actor_role=r[1], ownership_tier=r[2],
        genesis_chain_id=r[3],
    )


def upsert_actor(
    s: Session, *, actor_id: str, actor_role: str, ownership_tier: str = "user",
) -> None:
    s.execute(text("""
        INSERT INTO mvghb_actor (actor_id, actor_role, ownership_tier)
        VALUES (:a, :r, :t)
        ON CONFLICT (actor_id) DO UPDATE
          SET actor_role = EXCLUDED.actor_role,
              ownership_tier = EXCLUDED.ownership_tier
    """), {"a": actor_id, "r": actor_role, "t": ownership_tier})


def set_genesis(s: Session, *, actor_id: str, chain_id: UUID) -> None:
    s.execute(text("""
        UPDATE mvghb_actor SET genesis_chain_id = :c WHERE actor_id = :a
    """), {"c": str(chain_id), "a": actor_id})


def get_head(s: Session, actor_id: str) -> HeadRecord | None:
    r = s.execute(text("""
        SELECT actor_id, head_chain_id, head_timestamp, entry_count
          FROM mvghb_actor_head
         WHERE actor_id = :a
    """), {"a": actor_id}).first()
    if not r:
        return None
    return HeadRecord(
        actor_id=r[0], head_chain_id=r[1], head_timestamp=r[2], entry_count=r[3],
    )


def update_head(
    s: Session, *, actor_id: str, head_chain_id: UUID, head_timestamp: datetime,
) -> None:
    s.execute(text("""
        INSERT INTO mvghb_actor_head (actor_id, head_chain_id, head_timestamp, entry_count)
        VALUES (:a, :c, :t, 1)
        ON CONFLICT (actor_id) DO UPDATE
          SET head_chain_id = EXCLUDED.head_chain_id,
              head_timestamp = EXCLUDED.head_timestamp,
              entry_count = mvghb_actor_head.entry_count + 1
    """), {"a": actor_id, "c": str(head_chain_id), "t": head_timestamp})


def all_heads(s: Session) -> list[HeadRecord]:
    rows = s.execute(text("""
        SELECT actor_id, head_chain_id, head_timestamp, entry_count
          FROM mvghb_actor_head
         ORDER BY actor_id
    """)).all()
    return [
        HeadRecord(actor_id=r[0], head_chain_id=r[1],
                   head_timestamp=r[2], entry_count=r[3])
        for r in rows
    ]
