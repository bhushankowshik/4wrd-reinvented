-- noc-gov cluster — initial schema from E5 §1 + E3 §4.2 authoritative.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- ---------- governance_chain (E3 §4.2 authoritative, partitioned monthly on timestamp) ----------

CREATE TABLE IF NOT EXISTS governance_chain (
  chain_id             UUID NOT NULL,
  prev_chain_id        UUID,
  hmac_signature       BYTEA NOT NULL,
  actor_id             TEXT,
  actor_role           TEXT,
  entry_type           TEXT NOT NULL,
  ownership_tier       TEXT NOT NULL DEFAULT 'user',
  incident_id          UUID,
  payload_ref          JSONB,
  sop_versions_pinned  JSONB,
  timestamp            TIMESTAMPTZ NOT NULL DEFAULT now(),
  system_version       TEXT,
  model_version        TEXT,
  class_enum           TEXT NOT NULL DEFAULT 'NORMAL'
                       CHECK (class_enum IN ('NORMAL','OVERRIDE')),
  PRIMARY KEY (chain_id, timestamp)
) PARTITION BY RANGE (timestamp);

CREATE INDEX IF NOT EXISTS governance_chain_actor_idx
  ON governance_chain(actor_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS governance_chain_entry_type_idx
  ON governance_chain(entry_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS governance_chain_incident_idx
  ON governance_chain(incident_id) WHERE incident_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS governance_chain_prev_idx
  ON governance_chain(prev_chain_id);

-- Append-only enforcement (E5 §1.11 + E3 §4.2).
REVOKE UPDATE, DELETE ON governance_chain FROM PUBLIC;

CREATE OR REPLACE FUNCTION reject_governance_chain_mutation() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'governance_chain is append-only (UPDATE/DELETE rejected)';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS governance_chain_append_only ON governance_chain;
CREATE TRIGGER governance_chain_append_only
  BEFORE UPDATE OR DELETE ON governance_chain
  FOR EACH ROW EXECUTE FUNCTION reject_governance_chain_mutation();

-- ---------- operator_identity_map (E5 §1.9) ----------

CREATE TABLE IF NOT EXISTS operator_identity_map (
  pseudonymous_id        TEXT PRIMARY KEY,
  sso_subject_id         TEXT NOT NULL,
  display_name           TEXT NOT NULL,
  role                   TEXT NOT NULL
                         CHECK (role IN ('operator','supervisor','auditor','admin','sre')),
  created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  retired_at             TIMESTAMPTZ,
  issuance_chain_id      UUID NOT NULL,
  retirement_chain_id    UUID,
  UNIQUE (sso_subject_id)
);

-- ---------- identity_map_access_log (E5 §1.10) ----------

CREATE TABLE IF NOT EXISTS identity_map_access_log (
  access_id               UUID PRIMARY KEY,
  access_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
  requester_pseudo_id     TEXT NOT NULL,
  requester_role          TEXT NOT NULL,
  access_kind             TEXT NOT NULL
                          CHECK (access_kind IN ('single_record','bulk_read')),
  record_count            INT  NOT NULL,
  joint_session_id        UUID,
  counter_party_pseudo_id TEXT,
  counter_party_role      TEXT,
  justification           TEXT NOT NULL,
  access_chain_id         UUID NOT NULL,
  rate_limit_bucket       TEXT NOT NULL,
  anomaly_flag            BOOLEAN NOT NULL DEFAULT false
);
CREATE INDEX IF NOT EXISTS identity_map_access_log_req_idx
  ON identity_map_access_log(requester_pseudo_id, access_at DESC);
CREATE INDEX IF NOT EXISTS identity_map_access_log_kind_idx
  ON identity_map_access_log(access_kind, access_at DESC);
CREATE INDEX IF NOT EXISTS identity_map_access_log_anomaly_idx
  ON identity_map_access_log(anomaly_flag) WHERE anomaly_flag = true;

-- ---------- chain_integrity_check_result (E5 §1.16) ----------

CREATE TABLE IF NOT EXISTS chain_integrity_check_result (
  check_id               UUID PRIMARY KEY,
  checked_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  check_kind             TEXT NOT NULL
                         CHECK (check_kind IN ('daily_full_walk','wal_pg_agreement',
                                               'partition_seal','on_demand')),
  actor_chain_scope      TEXT,
  entries_verified       BIGINT NOT NULL,
  mismatch_count         INT NOT NULL,
  mismatch_detail        JSONB,
  outcome                TEXT NOT NULL
                         CHECK (outcome IN ('ok','mismatch','error')),
  result_chain_id        UUID NOT NULL
);

-- ---------- key_lifecycle_event (E5 §1.15) ----------

CREATE TABLE IF NOT EXISTS key_lifecycle_event (
  event_id                UUID PRIMARY KEY,
  event_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
  key_id                  TEXT NOT NULL,
  key_class               TEXT NOT NULL
                          CHECK (key_class IN ('root_master','chain_kek','data_kek','data_dek',
                                               'service_account','tls_cert','ctts_sa')),
  event_kind              TEXT NOT NULL
                          CHECK (event_kind IN ('generate','rotate','revoke','destroy','custody_attest')),
  rationale               TEXT,
  actor_pseudo_id         TEXT NOT NULL,
  counter_party_pseudo_id TEXT,
  chain_id                UUID NOT NULL,
  retention_until         DATE NOT NULL
);
