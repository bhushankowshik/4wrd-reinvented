-- noc-data cluster — initial schema from E5 §1.
-- Partitioning: monthly partitions, created ahead of time in 0002.
-- Cross-cluster FKs to noc-gov.governance_chain are logical only,
-- per E5 §1.18 reconcile protocol.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- ---------- sop_ingest_run (E5 §1.8) ----------

CREATE TABLE IF NOT EXISTS sop_ingest_run (
  ingest_run_id          UUID PRIMARY KEY,
  sop_id                 TEXT NOT NULL,
  sop_version            TEXT NOT NULL,
  triggered_at           TIMESTAMPTZ NOT NULL,
  triggered_by           TEXT NOT NULL,
  source_count           INT  NOT NULL,
  chunk_count            INT  NOT NULL,
  embedder_model_version TEXT NOT NULL,
  sme_review_state       TEXT NOT NULL DEFAULT 'pending'
                         CHECK (sme_review_state IN ('pending','approved','rejected')),
  sme_reviewer_id        TEXT,
  sme_reviewed_at        TIMESTAMPTZ,
  activation_at          TIMESTAMPTZ,
  ingest_chain_id        UUID NOT NULL,
  chain_id_committed_at  TIMESTAMPTZ
);

-- ---------- sop_chunk (E5 §1.6) ----------

CREATE TABLE IF NOT EXISTS sop_chunk (
  chunk_id               UUID PRIMARY KEY,
  sop_id                 TEXT NOT NULL,
  sop_version            TEXT NOT NULL,
  section_path           TEXT NOT NULL,
  section_type           TEXT
                         CHECK (section_type IN ('remediation','reference','precondition',
                                                 'escalation','overview','other')),
  chunk_seq              INT  NOT NULL,
  text                   TEXT NOT NULL,
  embedding              vector(768) NOT NULL,
  content_hash           BYTEA NOT NULL,
  ingest_at              TIMESTAMPTZ NOT NULL,
  source_uri             TEXT NOT NULL,
  ingest_run_id          UUID NOT NULL REFERENCES sop_ingest_run(ingest_run_id),
  lifecycle_state        TEXT NOT NULL DEFAULT 'pending_review'
                         CHECK (lifecycle_state IN
                                ('pending_review','active','deprecation_window','archived')),
  superseded_at          TIMESTAMPTZ,
  archive_at             TIMESTAMPTZ,
  UNIQUE (sop_id, sop_version, chunk_seq)
);

CREATE INDEX IF NOT EXISTS sop_chunk_sop_version_idx ON sop_chunk(sop_id, sop_version);
CREATE INDEX IF NOT EXISTS sop_chunk_lifecycle_idx   ON sop_chunk(lifecycle_state);
CREATE INDEX IF NOT EXISTS sop_chunk_embedding_hnsw  ON sop_chunk
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 128)
  WHERE lifecycle_state IN ('active','deprecation_window');

-- ---------- sop_chunk_archive_index (E5 §1.7) ----------

CREATE TABLE IF NOT EXISTS sop_chunk_archive_index (
  chunk_id               UUID PRIMARY KEY,
  sop_id                 TEXT NOT NULL,
  sop_version            TEXT NOT NULL,
  section_path           TEXT NOT NULL,
  chunk_seq              INT  NOT NULL,
  archive_uri            TEXT NOT NULL,
  staging_verified_at    TIMESTAMPTZ NOT NULL,
  archived_at            TIMESTAMPTZ NOT NULL,
  content_hash           BYTEA NOT NULL,
  retention_until        DATE NOT NULL
);
CREATE INDEX IF NOT EXISTS sop_chunk_archive_index_ver  ON sop_chunk_archive_index(sop_id, sop_version);
CREATE INDEX IF NOT EXISTS sop_chunk_archive_index_ret  ON sop_chunk_archive_index(retention_until);

-- ---------- incident (E5 §1.2, partitioned by ingest_at) ----------

CREATE TABLE IF NOT EXISTS incident (
  incident_id            UUID NOT NULL,
  ctts_incident_ref      TEXT NOT NULL,
  ctts_received_at       TIMESTAMPTZ NOT NULL,
  ingest_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  reporting_source       TEXT,
  affected_nodes         JSONB NOT NULL,
  symptom_text           TEXT NOT NULL,
  symptom_embedding      vector(768),
  severity               TEXT CHECK (severity IN ('P1','P2','P3','P4','P5')),
  customer_hint          TEXT,
  correlation_hints      JSONB,
  system_version         TEXT NOT NULL,
  sop_corpus_version     TEXT NOT NULL,
  intake_chain_id        UUID NOT NULL,
  chain_id_committed_at  TIMESTAMPTZ,
  intake_state           TEXT NOT NULL DEFAULT 'accepted'
                         CHECK (intake_state IN ('accepted','malformed_rejected')),
  content_hash           BYTEA NOT NULL,
  raw_payload_ref        TEXT,
  PRIMARY KEY (incident_id, ingest_at),
  UNIQUE (ctts_incident_ref, ingest_at)
) PARTITION BY RANGE (ingest_at);

CREATE INDEX IF NOT EXISTS incident_intake_chain_idx ON incident(intake_chain_id);
CREATE INDEX IF NOT EXISTS incident_severity_idx     ON incident(severity, ingest_at DESC);
CREATE INDEX IF NOT EXISTS incident_ingest_idx       ON incident(ingest_at DESC);
CREATE INDEX IF NOT EXISTS incident_symptom_hnsw     ON incident
  USING hnsw (symptom_embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 128);

-- ---------- agent_output (E5 §1.3, partitioned by started_at) ----------

CREATE TABLE IF NOT EXISTS agent_output (
  agent_output_id        UUID NOT NULL,
  incident_id            UUID NOT NULL,
  agent_kind             TEXT NOT NULL
                         CHECK (agent_kind IN ('diagnosis','correlation','sop','orchestrator')),
  invocation_seq         INT  NOT NULL,
  started_at             TIMESTAMPTZ NOT NULL,
  completed_at           TIMESTAMPTZ,
  status                 TEXT NOT NULL
                         CHECK (status IN ('ok','timeout','error','unavailable',
                                           'insufficient_data','none_found','no_applicable_sop')),
  output_payload         JSONB NOT NULL,
  reasoning_trace        JSONB,
  model_version          TEXT NOT NULL,
  tokens_in              INT,
  tokens_out             INT,
  agent_output_chain_id  UUID NOT NULL,
  chain_id_committed_at  TIMESTAMPTZ,
  content_hash           BYTEA NOT NULL,
  PRIMARY KEY (agent_output_id, started_at),
  UNIQUE (incident_id, agent_kind, invocation_seq, started_at)
) PARTITION BY RANGE (started_at);

CREATE INDEX IF NOT EXISTS agent_output_incident_idx ON agent_output(incident_id, agent_kind);
CREATE INDEX IF NOT EXISTS agent_output_completed_idx ON agent_output(completed_at);
CREATE INDEX IF NOT EXISTS agent_output_status_idx   ON agent_output(status);

-- ---------- recommendation (E5 §1.4, partitioned by produced_at) ----------

CREATE TABLE IF NOT EXISTS recommendation (
  recommendation_id       UUID NOT NULL,
  incident_id             UUID NOT NULL,
  production_seq          INT  NOT NULL DEFAULT 1,
  produced_at             TIMESTAMPTZ NOT NULL,
  decision_class          TEXT
                          CHECK (decision_class IN ('REMOTE_RESOLUTION','FIELD_DISPATCH','UNAVAILABLE')),
  payload                 JSONB NOT NULL,
  diagnostic_summary      TEXT,
  correlation_summary     JSONB,
  sop_references          JSONB NOT NULL,
  per_agent_status        JSONB NOT NULL,
  system_version          TEXT NOT NULL,
  sop_corpus_version      TEXT NOT NULL,
  model_version           TEXT NOT NULL,
  production_state        TEXT NOT NULL
                          CHECK (production_state IN ('produced','timed_out','unavailable')),
  recommendation_chain_id UUID NOT NULL,
  chain_id_committed_at   TIMESTAMPTZ,
  content_hash            BYTEA NOT NULL,
  PRIMARY KEY (recommendation_id, produced_at),
  UNIQUE (incident_id, production_seq, produced_at)
) PARTITION BY RANGE (produced_at);

CREATE INDEX IF NOT EXISTS recommendation_incident_seq_idx
  ON recommendation(incident_id, production_seq DESC);
CREATE INDEX IF NOT EXISTS recommendation_decision_idx
  ON recommendation(decision_class, produced_at DESC);
CREATE INDEX IF NOT EXISTS recommendation_prodstate_idx
  ON recommendation(production_state);

-- ---------- operator_decision (E5 §1.5, partitioned by decision_at) ----------

CREATE TABLE IF NOT EXISTS operator_decision (
  decision_id              UUID NOT NULL,
  incident_id              UUID NOT NULL,
  recommendation_id        UUID NOT NULL,
  pseudonymous_operator_id TEXT NOT NULL,
  decision_at              TIMESTAMPTZ NOT NULL,
  decision_kind            TEXT NOT NULL
                           CHECK (decision_kind IN
                                  ('approved','rejected','overridden','timed_out','unavailable_fallback')),
  reason_code              TEXT,
  reason_note              TEXT,
  override_action_class    TEXT,
  override_action_detail   JSONB,
  ctts_writeback_state     TEXT NOT NULL DEFAULT 'pending'
                           CHECK (ctts_writeback_state IN ('pending','ok','retrying','failed')),
  ctts_writeback_at        TIMESTAMPTZ,
  correlation_token        UUID NOT NULL,
  decision_chain_id        UUID NOT NULL,
  chain_id_committed_at    TIMESTAMPTZ,
  content_hash             BYTEA NOT NULL,
  PRIMARY KEY (decision_id, decision_at),
  UNIQUE (incident_id, recommendation_id, decision_at),
  UNIQUE (correlation_token, decision_at)
) PARTITION BY RANGE (decision_at);

CREATE INDEX IF NOT EXISTS operator_decision_op_idx
  ON operator_decision(pseudonymous_operator_id, decision_at DESC);
CREATE INDEX IF NOT EXISTS operator_decision_kind_idx
  ON operator_decision(decision_kind, decision_at DESC);
CREATE INDEX IF NOT EXISTS operator_decision_writeback_idx
  ON operator_decision(ctts_writeback_state);

-- ---------- test_corpus + synthetic_corpus_artefact (E5 §1.12) ----------

CREATE TABLE IF NOT EXISTS synthetic_corpus_artefact (
  artefact_id             UUID PRIMARY KEY,
  generation_run_id       UUID NOT NULL,
  pattern_catalog_version TEXT NOT NULL,
  synthesis_model_name    TEXT NOT NULL,
  synthesis_model_version TEXT NOT NULL,
  k_anonymity_k           INT  NOT NULL,
  generated_count         INT  NOT NULL,
  sme_review_state        TEXT NOT NULL DEFAULT 'pending'
                          CHECK (sme_review_state IN ('pending','approved','rejected')),
  bundle_uri              TEXT NOT NULL,
  generation_chain_id     UUID NOT NULL,
  created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS synthetic_corpus_artefact_run_idx ON synthetic_corpus_artefact(generation_run_id);

CREATE TABLE IF NOT EXISTS test_corpus (
  test_incident_id       UUID PRIMARY KEY,
  corpus_version         TEXT NOT NULL,
  origin                 TEXT NOT NULL
                         CHECK (origin IN ('historical','synthetic','sme_authored')),
  source_incident_ref    TEXT,
  synthetic_artefact_id  UUID REFERENCES synthetic_corpus_artefact(artefact_id),
  payload                JSONB NOT NULL,
  ground_truth           JSONB NOT NULL,
  ground_truth_source    TEXT NOT NULL
                         CHECK (ground_truth_source IN ('historical_outcome','sme_labelled','both')),
  sme_validator_id       TEXT,
  sme_validated_at       TIMESTAMPTZ,
  sensitivity_class      TEXT NOT NULL DEFAULT 'restricted_internal',
  generation_chain_id    UUID,
  created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  retired_at             TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS test_corpus_version_idx ON test_corpus(corpus_version, origin);
CREATE INDEX IF NOT EXISTS test_corpus_sens_idx    ON test_corpus(sensitivity_class);

-- ---------- validation_failure (E5 §1.13) ----------

CREATE TABLE IF NOT EXISTS validation_failure (
  failure_id             UUID PRIMARY KEY,
  detected_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  stage                  TEXT NOT NULL
                         CHECK (stage IN ('intake','agent_output','recommendation',
                                          'decision','sop_ingest','writeback','export')),
  subject_ref            TEXT,
  rule_id                TEXT NOT NULL,
  rule_severity          TEXT NOT NULL
                         CHECK (rule_severity IN ('reject','quarantine','warn')),
  details                JSONB NOT NULL,
  failure_chain_id       UUID NOT NULL,
  chain_id_committed_at  TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS validation_failure_stage_idx ON validation_failure(stage, detected_at DESC);
CREATE INDEX IF NOT EXISTS validation_failure_rule_idx  ON validation_failure(rule_id);

-- ---------- problem + problem_incident_link (E5 §1.14) ----------

CREATE TABLE IF NOT EXISTS problem (
  problem_id             UUID PRIMARY KEY,
  created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by_pseudo_id   TEXT NOT NULL,
  status                 TEXT NOT NULL DEFAULT 'open'
                         CHECK (status IN ('open','investigating','root_caused','closed')),
  title                  TEXT NOT NULL,
  summary                TEXT,
  root_cause_hypothesis  TEXT,
  root_cause_confirmed_at TIMESTAMPTZ,
  closed_at              TIMESTAMPTZ,
  problem_chain_id       UUID NOT NULL,
  chain_id_committed_at  TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS problem_status_idx ON problem(status);

CREATE TABLE IF NOT EXISTS problem_incident_link (
  problem_id             UUID NOT NULL REFERENCES problem(problem_id),
  incident_id            UUID NOT NULL,
  link_kind              TEXT NOT NULL
                         CHECK (link_kind IN ('example','root_cause_instance','symptom_match')),
  linked_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  linked_by_pseudo_id    TEXT NOT NULL,
  link_chain_id          UUID NOT NULL,
  chain_id_committed_at  TIMESTAMPTZ,
  PRIMARY KEY (problem_id, incident_id)
);
CREATE INDEX IF NOT EXISTS problem_incident_link_inc_idx ON problem_incident_link(incident_id);
