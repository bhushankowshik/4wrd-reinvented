-- MVGH-β Wave 1 — additive schema on noc-gov.
-- Reuses governance_chain (already created by noc-product migration 0001).
-- Adds: actor registry, head pointer, anchor index.

-- Actor registry — one row per chain-bearing actor.
CREATE TABLE IF NOT EXISTS mvghb_actor (
  actor_id          TEXT PRIMARY KEY,
  actor_role        TEXT NOT NULL,
  ownership_tier    TEXT NOT NULL DEFAULT 'user',
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  genesis_chain_id  UUID,
  retired_at        TIMESTAMPTZ
);

-- Per-actor chain head — fast lookup of last chain_id without scanning the partitioned table.
-- Updated on every emit; one row per actor.
CREATE TABLE IF NOT EXISTS mvghb_actor_head (
  actor_id        TEXT PRIMARY KEY REFERENCES mvghb_actor(actor_id),
  head_chain_id   UUID NOT NULL,
  head_timestamp  TIMESTAMPTZ NOT NULL,
  entry_count     BIGINT NOT NULL DEFAULT 0
);

-- Master anchor index — convenience pointer; the authoritative anchor record
-- lives in governance_chain with entry_type='master_anchor'.
CREATE TABLE IF NOT EXISTS mvghb_master_anchor (
  anchor_id           UUID PRIMARY KEY,
  anchored_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  anchor_chain_id     UUID NOT NULL,
  actor_count         INT NOT NULL,
  anchor_hmac         BYTEA NOT NULL,
  prev_anchor_id      UUID
);

CREATE INDEX IF NOT EXISTS mvghb_master_anchor_time_idx
  ON mvghb_master_anchor(anchored_at DESC);
