# E5 — Data — Exit Artefact

## 0. Status and derivation

**Convergence state at exit:** Exact. Ratified.
**Primary derivation intent:** docs/e4-exit-artefact.md; docs/e3-exit-artefact.md; docs/e2-exit-artefact.md; docs/e5-knowledge-contribution.md; docs/e5-cycle-1-verification.md.
**Contributing cycles:** E5.1 Explorative (first-pass across 7 deliverables) → E5 Targeted → Exact (7 adjustments absorbed).

**Governance mode at this cycle:** **Partial governance.** Cycle primitives active; full-harness infrastructure activates progressively as MVGH-β setup completes (CARRY-FWD-4).

**DISCIPLINE-2 stance:** E5 does not make architectural selections. Those are E3-owned. E5 works within the ratified E3 architecture and E4 security posture, and completes the data layer.

---

## 1. Complete data model

### 1.1 Namespace/cluster assignment

| Cluster | Namespace | Tables |
|---|---|---|
| Incident-tier PG (pgvector) | `noc-data` | `incident`, `agent_output`, `recommendation`, `operator_decision`, `sop_chunk`, `sop_chunk_archive_index`, `sop_ingest_run`, `test_corpus`, `synthetic_corpus_artefact`, `problem`, `problem_incident_link`, `validation_failure` |
| Governance-tier PG | `noc-gov` | `governance_chain` (authoritative, E3 §4.2), `operator_identity_map`, `identity_map_access_log`, `chain_integrity_check_result`, `key_lifecycle_event` |
| Object storage | — | `sop_chunk_archive` bundles (7y), `governance_chain` partition archives, `synthetic_corpus_bundle` |

### 1.2 `incident` (noc-data)

```sql
CREATE TABLE incident (
  incident_id            UUID PRIMARY KEY,                       -- FR-A.2
  ctts_incident_ref      TEXT NOT NULL,                          -- originating CTTS ID
  ctts_received_at       TIMESTAMPTZ NOT NULL,                   -- CTTS reported time
  ingest_at              TIMESTAMPTZ NOT NULL DEFAULT now(),     -- FR-A.4 stamp
  reporting_source       TEXT,                                   -- CI-9 bound
  affected_nodes         JSONB NOT NULL,                         -- structured list
  symptom_text           TEXT NOT NULL,
  symptom_embedding      vector(768),                            -- Granite Embedding; OF-5.1 to confirm dim
  severity               TEXT CHECK (severity IN ('P1','P2','P3','P4','P5')),
  customer_hint          TEXT,                                   -- CI-9 optional
  correlation_hints      JSONB,                                  -- CI-9 per-client
  system_version         TEXT NOT NULL,                          -- FR-A.4
  sop_corpus_version     TEXT NOT NULL,                          -- FR-A.4 (pinned at intake)
  intake_chain_id        UUID NOT NULL,                          -- logical FK → governance_chain
  chain_id_committed_at  TIMESTAMPTZ,                            -- OF-5.6 — set when noc-gov commit observed
  intake_state           TEXT NOT NULL DEFAULT 'accepted'
                         CHECK (intake_state IN ('accepted','malformed_rejected')),
  content_hash           BYTEA NOT NULL,                         -- SHA-256 over canonical payload (OF-5.18)
  raw_payload_ref        TEXT,                                   -- object-storage URI for full payload
  UNIQUE (ctts_incident_ref)                                     -- IR-T.5 idempotency
) PARTITION BY RANGE (ingest_at);
```

**Indexes:** `(intake_chain_id)`, `(severity, ingest_at DESC)`, `(ingest_at DESC)` partition-local, HNSW on `symptom_embedding` for correlation search.
**Partitioning:** monthly partitions; hot = 12 months (E3 §4.7); aged → archive job.
**Logical FK:** `intake_chain_id` references `noc-gov.governance_chain(chain_id)`; cross-cluster enforcement per §1.18.

### 1.3 `agent_output` (noc-data)

```sql
CREATE TABLE agent_output (
  agent_output_id        UUID PRIMARY KEY,
  incident_id            UUID NOT NULL REFERENCES incident(incident_id),
  agent_kind             TEXT NOT NULL
                         CHECK (agent_kind IN ('diagnosis','correlation','sop','orchestrator')),
  invocation_seq         INT NOT NULL,
  started_at             TIMESTAMPTZ NOT NULL,
  completed_at           TIMESTAMPTZ,
  status                 TEXT NOT NULL
                         CHECK (status IN ('ok','timeout','error','unavailable',
                                           'insufficient_data','none_found','no_applicable_sop')),
  output_payload         JSONB NOT NULL,                         -- per-agent pydantic schema
  reasoning_trace        JSONB,                                  -- FR-B.2.2; LUKS2-at-rest via E4 §4
  model_version          TEXT NOT NULL,
  tokens_in              INT,
  tokens_out             INT,
  agent_output_chain_id  UUID NOT NULL,                          -- logical FK
  chain_id_committed_at  TIMESTAMPTZ,                            -- OF-5.6
  content_hash           BYTEA NOT NULL,                         -- canonicalisation OF-5.18
  UNIQUE (incident_id, agent_kind, invocation_seq)
) PARTITION BY RANGE (started_at);
```

**Indexes:** `(incident_id, agent_kind)`, `(completed_at)`, `(status)`.

### 1.4 `recommendation` (noc-data — Targeted adjustment #1: production_seq + relaxed uniqueness)

```sql
CREATE TABLE recommendation (
  recommendation_id       UUID PRIMARY KEY,
  incident_id             UUID NOT NULL REFERENCES incident(incident_id),
  production_seq          INT NOT NULL DEFAULT 1,                 -- Targeted #1
  produced_at             TIMESTAMPTZ NOT NULL,                   -- FR-C.1
  decision_class          TEXT
                          CHECK (decision_class IN ('REMOTE_RESOLUTION','FIELD_DISPATCH','UNAVAILABLE')),
  payload                 JSONB NOT NULL,                         -- FR-C.1 full contract
  diagnostic_summary      TEXT,
  correlation_summary     JSONB,
  sop_references          JSONB NOT NULL,                         -- [{sop_id, sop_version, chunk_ids[]}]
  per_agent_status        JSONB NOT NULL,
  system_version          TEXT NOT NULL,
  sop_corpus_version      TEXT NOT NULL,                          -- FR-A.4 pinned
  model_version           TEXT NOT NULL,
  production_state        TEXT NOT NULL
                          CHECK (production_state IN ('produced','timed_out','unavailable')),
  recommendation_chain_id UUID NOT NULL,                          -- logical FK
  chain_id_committed_at   TIMESTAMPTZ,                            -- OF-5.6
  content_hash            BYTEA NOT NULL,                         -- canonicalisation OF-5.18
  UNIQUE (incident_id, production_seq)                            -- Targeted #1 relaxation
) PARTITION BY RANGE (produced_at);
```

**Uniqueness rationale (Targeted adjustment #1):** `UNIQUE(incident_id)` was too strict under FR-D.4 re-present-for-human-review semantics (CI-3). `production_seq` defaults to 1 and increments only if the platform config selects re-presentation after timeout, so the default path is harmless. The CI-3 dependency is preserved: if CI-3 resolves to escalate / hold / park without re-present, `production_seq` stays at 1 for every incident.

**Indexes:** `(incident_id, production_seq DESC)`, `(decision_class, produced_at DESC)`, `(production_state)`.

### 1.5 `operator_decision` (noc-data)

```sql
CREATE TABLE operator_decision (
  decision_id              UUID PRIMARY KEY,
  incident_id              UUID NOT NULL REFERENCES incident(incident_id),
  recommendation_id        UUID NOT NULL REFERENCES recommendation(recommendation_id),
  pseudonymous_operator_id TEXT NOT NULL,                         -- CI-5
  decision_at              TIMESTAMPTZ NOT NULL,
  decision_kind            TEXT NOT NULL
                           CHECK (decision_kind IN
                                  ('approved','rejected','overridden','timed_out','unavailable_fallback')),
  reason_code              TEXT,                                  -- CI-2 taxonomy
  reason_note              TEXT,
  override_action_class    TEXT,                                  -- FR-D.3
  override_action_detail   JSONB,
  ctts_writeback_state     TEXT NOT NULL DEFAULT 'pending'
                           CHECK (ctts_writeback_state IN ('pending','ok','retrying','failed')),
  ctts_writeback_at        TIMESTAMPTZ,
  correlation_token        UUID NOT NULL,                         -- FR-E.4 idempotency
  decision_chain_id        UUID NOT NULL,                         -- logical FK
  chain_id_committed_at    TIMESTAMPTZ,                           -- OF-5.6
  content_hash             BYTEA NOT NULL,                        -- canonicalisation OF-5.18
  UNIQUE (incident_id, recommendation_id),                        -- one terminal decision per recommendation
  UNIQUE (correlation_token)
) PARTITION BY RANGE (decision_at);
```

**Uniqueness note:** decision keyed to `(incident_id, recommendation_id)` to align with the relaxed recommendation uniqueness (Targeted #1). A re-presented incident has two recommendations and may have two terminal decisions.

**Indexes:** `(pseudonymous_operator_id, decision_at DESC)`, `(decision_kind, decision_at DESC)`, `(ctts_writeback_state)`.

### 1.6 `sop_chunk` (noc-data, pgvector — Targeted adjustment #2: pending_review added)

```sql
CREATE TABLE sop_chunk (
  chunk_id               UUID PRIMARY KEY,
  sop_id                 TEXT NOT NULL,
  sop_version            TEXT NOT NULL,
  section_path           TEXT NOT NULL,
  section_type           TEXT
                         CHECK (section_type IN ('remediation','reference','precondition',
                                                 'escalation','overview','other')),
  chunk_seq              INT NOT NULL,
  text                   TEXT NOT NULL,
  embedding              vector(768) NOT NULL,                   -- OF-5.1 dim to confirm
  content_hash           BYTEA NOT NULL,                         -- canonicalisation OF-5.18
  ingest_at              TIMESTAMPTZ NOT NULL,
  source_uri             TEXT NOT NULL,
  ingest_run_id          UUID NOT NULL REFERENCES sop_ingest_run(ingest_run_id),
  lifecycle_state        TEXT NOT NULL DEFAULT 'pending_review'
                         CHECK (lifecycle_state IN                              -- Targeted #2
                                ('pending_review','active','deprecation_window','archived')),
  superseded_at          TIMESTAMPTZ,
  archive_at             TIMESTAMPTZ,
  UNIQUE (sop_id, sop_version, chunk_seq)
);
```

**Lifecycle transitions (Targeted #2):** `pending_review` (post-ingest, pre-SME) → `active` (on SME approval) → `deprecation_window` (on supersession) → `archived` (post-90d). Enum now fully covers the four states; retrieval indexes scope to active + deprecation_window only.

**Indexes:** `(sop_id, sop_version)`, `(lifecycle_state)`, HNSW on `embedding` (cosine ops) WHERE `lifecycle_state IN ('active','deprecation_window')`.

### 1.7 `sop_chunk_archive_index` (noc-data)

Pointer table; raw archived chunks live in object storage.

```sql
CREATE TABLE sop_chunk_archive_index (
  chunk_id               UUID PRIMARY KEY,
  sop_id                 TEXT NOT NULL,
  sop_version            TEXT NOT NULL,
  section_path           TEXT NOT NULL,
  chunk_seq              INT NOT NULL,
  archive_uri            TEXT NOT NULL,                          -- object-storage URI (Compliance-locked)
  staging_verified_at    TIMESTAMPTZ NOT NULL,                   -- OF-4.9 staging gate
  archived_at            TIMESTAMPTZ NOT NULL,
  content_hash           BYTEA NOT NULL,
  retention_until        DATE NOT NULL                           -- 7y per E4 §7.3
);
```

**Indexes:** `(sop_id, sop_version)`, `(retention_until)`.

### 1.8 `sop_ingest_run` (noc-data)

```sql
CREATE TABLE sop_ingest_run (
  ingest_run_id          UUID PRIMARY KEY,
  sop_id                 TEXT NOT NULL,
  sop_version            TEXT NOT NULL,
  triggered_at           TIMESTAMPTZ NOT NULL,
  triggered_by           TEXT NOT NULL,                          -- pseudonymous uploader ID
  source_count           INT NOT NULL,
  chunk_count            INT NOT NULL,
  embedder_model_version TEXT NOT NULL,
  sme_review_state       TEXT NOT NULL DEFAULT 'pending'
                         CHECK (sme_review_state IN ('pending','approved','rejected')),
  sme_reviewer_id        TEXT,
  sme_reviewed_at        TIMESTAMPTZ,
  activation_at          TIMESTAMPTZ,
  ingest_chain_id        UUID NOT NULL,
  chain_id_committed_at  TIMESTAMPTZ                             -- OF-5.6
);
```

### 1.9 `operator_identity_map` (noc-gov — E3 §4.4 authoritative)

```sql
CREATE TABLE operator_identity_map (
  pseudonymous_id        TEXT PRIMARY KEY,                       -- ≥128-bit entropy opaque token
  sso_subject_id         TEXT NOT NULL,                          -- client IdP subject
  display_name           TEXT NOT NULL,                          -- audit-render only
  role                   TEXT NOT NULL
                         CHECK (role IN ('operator','supervisor','auditor','admin','sre')),
  created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  retired_at             TIMESTAMPTZ,
  issuance_chain_id      UUID NOT NULL,
  retirement_chain_id    UUID,
  UNIQUE (sso_subject_id)
);
```

**Access:** via `identity-audit-api` only. All reads recorded to `identity_map_access_log` + chain (OF-4.8 strengthened).

### 1.10 `identity_map_access_log` (noc-gov — OF-4.8 strengthened)

```sql
CREATE TABLE identity_map_access_log (
  access_id               UUID PRIMARY KEY,
  access_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
  requester_pseudo_id     TEXT NOT NULL,
  requester_role          TEXT NOT NULL,
  access_kind             TEXT NOT NULL
                          CHECK (access_kind IN ('single_record','bulk_read')),
  record_count            INT NOT NULL,
  joint_session_id        UUID,                                  -- bulk_read two-role gate
  counter_party_pseudo_id TEXT,
  counter_party_role      TEXT,
  justification           TEXT NOT NULL,
  access_chain_id         UUID NOT NULL,
  rate_limit_bucket       TEXT NOT NULL,
  anomaly_flag            BOOLEAN NOT NULL DEFAULT false         -- set by detection job
);
```

**Indexes:** `(requester_pseudo_id, access_at DESC)`, `(access_kind, access_at DESC)`, `(anomaly_flag) WHERE anomaly_flag = true`.

### 1.11 `governance_chain` (noc-gov — E3 §4.2 authoritative; E5 additive)

**Schema preserved verbatim from E3 §4.2.** E5 adds only:

- **Extended `entry_type` values (additive — column type unchanged):**
  - `key_rotation`, `key_revocation` (E4 §3.3)
  - `identity_map_access`, `identity_map_access_bulk_joint` (OF-4.8)
  - `sop_ingest_run_start`, `sop_ingest_sme_decision`, `sop_version_activate`, `sop_version_deprecate`, `sop_chunk_archive_move`
  - `validation_failure`
  - `partition_seal`
  - `staging_integrity_verified` (OF-4.9)
  - `ctts_writeback_outcome`
  - `problem_created`, `problem_linked`, `problem_closed` (OF-4.15)
  - `export_bundle_generated` (OF-4.12)
- **No column changes.** All new data lives inside `payload_ref` JSONB.
- **Enum validation NOT at DB level** (per E3 §4.2 extensibility). Allowlist enforced at Chain-Write Service via AG-3 validator (**OF-5.17**).

**Append-only enforcement:**
```sql
REVOKE UPDATE, DELETE ON governance_chain FROM PUBLIC;
CREATE OR REPLACE FUNCTION reject_mutation() RETURNS trigger AS $$
BEGIN RAISE EXCEPTION 'governance_chain is append-only'; END; $$ LANGUAGE plpgsql;
CREATE TRIGGER governance_chain_append_only
  BEFORE UPDATE OR DELETE ON governance_chain
  FOR EACH ROW EXECUTE FUNCTION reject_mutation();
```

**Partitioning:** monthly partitions on `timestamp`; sealed-manifest per partition at hot→warm boundary; archived partitions move via OF-4.9 staging path to object storage Compliance-locked bucket.

### 1.12 `test_corpus` + `synthetic_corpus_artefact` (noc-data)

```sql
CREATE TABLE test_corpus (
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
  sensitivity_class      TEXT NOT NULL DEFAULT 'restricted_internal',   -- OF-4.10
  generation_chain_id    UUID,
  created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  retired_at             TIMESTAMPTZ
);

CREATE TABLE synthetic_corpus_artefact (
  artefact_id             UUID PRIMARY KEY,
  generation_run_id       UUID NOT NULL,
  pattern_catalog_version TEXT NOT NULL,
  synthesis_model_name    TEXT NOT NULL,                          -- 'llama-3.x' family
  synthesis_model_version TEXT NOT NULL,
  k_anonymity_k           INT NOT NULL,                           -- OF-4.10 ≥5 primary guard
  generated_count         INT NOT NULL,
  sme_review_state        TEXT NOT NULL DEFAULT 'pending'
                          CHECK (sme_review_state IN ('pending','approved','rejected')),
  bundle_uri              TEXT NOT NULL,
  generation_chain_id     UUID NOT NULL,
  created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Indexes:** `test_corpus (corpus_version, origin)`, `(sensitivity_class)`; `synthetic_corpus_artefact (generation_run_id)`.
**Retention posture:** indefinite pending CI-7 resolution (**OF-5.16**); k-anonymity ≥5 is the primary guard for re-identification risk.

### 1.13 `validation_failure` (noc-data)

```sql
CREATE TABLE validation_failure (
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
  chain_id_committed_at  TIMESTAMPTZ                             -- OF-5.6
);
```

### 1.14 `problem` + `problem_incident_link` (noc-data — OF-4.15 minimal viable)

```sql
CREATE TABLE problem (
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
  chain_id_committed_at  TIMESTAMPTZ                             -- OF-5.6
);

CREATE TABLE problem_incident_link (
  problem_id             UUID NOT NULL REFERENCES problem(problem_id),
  incident_id            UUID NOT NULL REFERENCES incident(incident_id),
  link_kind              TEXT NOT NULL
                         CHECK (link_kind IN ('example','root_cause_instance','symptom_match')),
  linked_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  linked_by_pseudo_id    TEXT NOT NULL,
  link_chain_id          UUID NOT NULL,
  chain_id_committed_at  TIMESTAMPTZ,                            -- OF-5.6
  PRIMARY KEY (problem_id, incident_id)
);
```

**Indexes:** `problem (status)`, `problem_incident_link (incident_id)`.
**Version history (OF-5.19):** `problem_status_history` intentionally deferred to E6 as a scope-growth extension; current minimal-viable schema holds.

### 1.15 `key_lifecycle_event` (noc-gov)

Mirrors E4 §3.3 key-rotation / revocation flow as a queryable companion to chain entries (10y retention per E4 §7.3).

```sql
CREATE TABLE key_lifecycle_event (
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
  counter_party_pseudo_id TEXT,                                  -- two-role ops
  chain_id                UUID NOT NULL,
  retention_until         DATE NOT NULL                          -- 10y per E4 §7.3
);
```

### 1.16 `chain_integrity_check_result` (noc-gov)

```sql
CREATE TABLE chain_integrity_check_result (
  check_id               UUID PRIMARY KEY,
  checked_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  check_kind             TEXT NOT NULL
                         CHECK (check_kind IN ('daily_full_walk','wal_pg_agreement',
                                               'partition_seal','on_demand')),
  actor_chain_scope      TEXT,                                   -- per-actor chain ID or 'all'
  entries_verified       BIGINT NOT NULL,
  mismatch_count         INT NOT NULL,
  mismatch_detail        JSONB,
  outcome                TEXT NOT NULL
                         CHECK (outcome IN ('ok','mismatch','error')),
  result_chain_id        UUID NOT NULL
);
```

### 1.17 content_hash canonicalisation (OF-5.18 — Targeted adjustment #4)

Every `content_hash` column stores `SHA-256(canonical_bytes(payload))`. Canonical form:

1. JSON serialisation with **sorted keys** (lexicographic, UTF-8 codepoint order).
2. **No insignificant whitespace** (compact separators `,` `:`).
3. **UTF-8 byte encoding** (no BOM).
4. Applied to the payload content *before* any wrapper envelope (chain HMAC covers the envelope separately).

**Enforcement:** Chain-Write Service canonicalises inputs and computes both `content_hash` and the HMAC over the canonical byte stream. Incident-tier producers MUST call Chain-Write Service helpers rather than hashing independently. **OF-5.18 is an E6 implementation + test requirement.**

### 1.18 Cross-cluster foreign-key posture (OF-5.6 — Targeted adjustment #6)

Cross-cluster FKs (`*.chain_id` → `noc-gov.governance_chain.chain_id`) are **not enforced at DB level** (separate clusters). Enforcement:

1. **Synchronous handshake:** Chain-Write Service returns `chain_id` to the producer on WAL fsync success; producer writes the incident-tier row with that `chain_id` and leaves `chain_id_committed_at` NULL until the async PG commit is observed.
2. **Commit-observation updater:** a lightweight reconcile worker reads `governance_chain` for each unresolved `chain_id` referenced by incident-tier rows and fills `chain_id_committed_at` on observation.
3. **Daily WAL-PG agreement verifier** (E3 §6.5) confirms every incident-tier `chain_id` has a matching `governance_chain` row.
4. **Orphan-detection query** (Layer-2) flags any incident-tier row whose `chain_id` is unresolved after a configurable grace window (default 30 minutes). Flagged orphans are incident-grade events.
5. **Audit-export queries filter on `chain_id_committed_at IS NOT NULL`** by default to avoid exporting rows whose governance-side commit has not been observed.

**OF-5.6 continuation:** tightening the grace window and choosing between per-write vs daily verification is an **E6 decision**.

---

## 2. Data flow diagrams

Each flow: **trigger → data movement → format → granularity**.

### 2.1 Intake flow (FR-A.1–5)

```
CTTS  ──poll every 15s──▶  Intake Adapter (noc-prod)
                               │
                               ├─ schema-validate (CI-9 schema + §5 intake rules)
                               │  └─(fail)─▶ validation_failure row + chain entry
                               │             'ticket_rejected_malformed' + 'validation_failure'
                               │
                               ├─ compute content_hash (canonical per OF-5.18)
                               │
                               ├─ UPSERT incident(...) by ctts_incident_ref       [noc-data]
                               │
                               ├─ Chain-Write Service ──▶ WAL fsync + ACK returns chain_id
                               │                      └─▶ async PG commit        [noc-gov]
                               │     entry_type='intake';  AG-3 allowlist (OF-5.17)
                               │     payload_ref={incident_id, content_hash,
                               │                    system_version, sop_corpus_version}
                               │
                               ├─ UPDATE incident.intake_chain_id = chain_id
                               └─ reconcile worker later fills chain_id_committed_at
```

**Granularity:** per ticket. **Trigger:** CTTS state-marker advance. **Idempotency:** `UNIQUE(ctts_incident_ref)`.

### 2.2 Analysis flow (FR-B.1–4)

```
Agent Orchestrator (LangGraph)
  │  input: incident row (noc-data)
  │
  ├─ parallel fan-out
  │   ├─▶ Diagnosis Agent  ──(vLLM Granite Instruct)──▶ agent_output(agent_kind='diagnosis')
  │   └─▶ Correlation Agent ──(pgvector HNSW on incident.symptom_embedding +
  │                             structured filter on affected_nodes / customer_hint / time)──▶
  │                             agent_output(agent_kind='correlation')
  │
  ├─ sequential-on-diagnosis
  │   └─▶ SOP Agent ──(pgvector HNSW on sop_chunk.embedding filtered
  │                     lifecycle_state IN ('active','deprecation_window'),
  │                     top-k=10 → re-rank → top-3)──▶
  │                     agent_output(agent_kind='sop')
  │
  └─ merge → compose FR-C.1 payload
       └─ each agent_output row written to noc-data
       └─ one chain entry per agent_output via Chain-Write Service
         entry_type='agent_output' (AG-3 allowlist OF-5.17)
         payload_ref={agent_output_id, agent_kind, status, content_hash, model_version}
```

**Granularity:** per agent invocation. **Trigger:** intake commit. **Budget:** per E3 §2.4 ~95s steady.

### 2.3 Recommendation flow (FR-C.1)

```
Orchestrator merge
  │
  ├─ assemble FR-C.1 payload
  ├─ compute content_hash (canonical per OF-5.18)
  ├─ determine production_seq (default 1; incremented by re-present CronJob if CI-3 so configures)
  ├─ INSERT recommendation(...)                                  [noc-data]
  ├─ Chain-Write Service ──▶ WAL fsync + ACK
  │                      └─▶ async PG commit                    [noc-gov]
  │     entry_type='recommendation' (AG-3 allowlist OF-5.17)
  │     payload_ref={recommendation_id, production_seq, decision_class,
  │     content_hash, sop_references, per_agent_status, model_version}
  │     sop_versions_pinned: full {sop_id, sop_version, chunk_ids[]} list
  │
  └─ UPDATE recommendation.recommendation_chain_id
```

**Produced-upon:** WAL fsync success (E3 §4.5; NFR-R.4). **UNAVAILABLE path** (FR-D.5): `decision_class='UNAVAILABLE'`, `production_state='unavailable'`, chain entry `entry_type='unavailable'`.

### 2.4 Review flow (FR-D.1–6)

```
Reviewer (SSO-authenticated)  ──HTTPS──▶  Review API (FastAPI + HTMX)
     │
     │  Review API resolves SSO subject → pseudonymous_operator_id via
     │  identity-audit-api single-record read on noc-gov; writes
     │  identity_map_access_log (access_kind='single_record') + chain entry
     │  entry_type='identity_map_access'
     │
     ├─ GET /recommendations/pending → reads recommendation + incident    [noc-data]
     │
     └─ POST /decisions
          │
          ├─ §5 validation (reason_code ∈ CI-2; override schema)
          ├─ INSERT operator_decision(...)                                [noc-data]
          ├─ Chain-Write Service ──▶ WAL fsync + ACK
          │                       └─▶ async PG commit                    [noc-gov]
          │    entry_type='operator_decision' (AG-3 allowlist OF-5.17)
          │    actor_id=pseudonymous_operator_id
          │    payload_ref={decision_id, decision_kind, reason_code,
          │                 recommendation_id, production_seq, content_hash}
          │
          └─ trigger CTTS write-back job (§2.5)
```

**Timeout path (FR-D.4):** re-materialisation CronJob scans recommendations without a decision past configurable window; behaviour per CI-3 config:
- `escalate` / `hold` / `park` → writes `operator_decision` with `decision_kind='timed_out'` or `'unavailable_fallback'`; recommendation retains `production_seq=1`.
- `re-present` → produces a new recommendation row with `production_seq = prior + 1` and chain entry; notifies next reviewer.

### 2.5 Outcome-recording / CTTS write-back flow (FR-E.1–4)

```
CTTS-writeback worker (noc-prod, leader-elected)
  │  polls operator_decision WHERE ctts_writeback_state='pending'
  │
  ├─ PATCH/POST against CTTS with correlation_token + structured fields:
  │  {decision_kind, reason_code, override_action_class, decision_at,
  │   pseudonymous_operator_id}
  │    ├─(ok)──▶ UPDATE operator_decision SET ctts_writeback_state='ok',
  │    │                                      ctts_writeback_at=now()
  │    │        └─▶ Chain-Write Service entry_type='ctts_writeback_outcome'
  │    │              (AG-3 allowlist OF-5.17)
  │    │              payload_ref={decision_id, writeback_state='ok'}
  │    │
  │    ├─(transient)──▶ retry exponential 2s/4s/8s (per E3 §5.4)
  │    └─(persistent after budget)──▶ ctts_writeback_state='failed' + alert + chain entry
  │
  └─ idempotency via correlation_token (CTTS-side duplicate rejection)
```

### 2.6 SOP ingestion flow (see §3 for full pipeline)

```
Authorised uploader (admin/auditor) uploads Word/PDF bundle to source fileserver
  │
Kubeflow pipeline triggered (on-demand or nightly)
  │
  ├─ INSERT sop_ingest_run (sme_review_state='pending') + chain entry
  │   'sop_ingest_run_start' (AG-3 allowlist OF-5.17)
  ├─ parse → chunk → embed → stage (lifecycle_state='pending_review')   (§3)
  ├─ k-anonymity check (synthetic path) / secret-pattern scan (§5)
  │
  ├─ SME review → chain entry 'sop_ingest_sme_decision'
  │   ├─(approved)─▶ UPDATE sop_chunk.lifecycle_state='active' (new version);
  │   │              UPDATE prior-version sop_chunk.lifecycle_state='deprecation_window',
  │   │              superseded_at=now()
  │   │              chain 'sop_version_activate' + 'sop_version_deprecate'
  │   └─(rejected)─▶ UPDATE sop_chunk.lifecycle_state remains 'pending_review'
  │                  marked for purge after retention hold
  │
  └─ 90-day deprecation CronJob (E3 §3.2 + E4 §7.3)
      └─ flip 'deprecation_window' → 'archived' via OF-4.9 staging path:
         stage → integrity verify → Compliance-locked bucket → archive_index row
         chain 'staging_integrity_verified' → 'sop_chunk_archive_move'
```

### 2.7 Archival flow (chain hot → warm)

```
Monthly CronJob (noc-gov)
  │
  ├─ compute partition_seal (HMAC over sorted (chain_id, hmac_signature) tuples)
  ├─ write partition bundle → OF-4.9 staging bucket (no Object Lock)
  ├─ integrity verifier walks sealed-partition HMAC chain + manifest
  │    └─ chain_integrity_check_result(check_kind='partition_seal')
  ├─(ok)─▶ copy staging → Compliance-locked bucket; retention lock = 7y
  │        delete staging entry; chain entries 'staging_integrity_verified'
  │        + 'partition_seal' (AG-3 allowlist OF-5.17)
  │
  └─ hot partition detaches after retention_until elapses
```

---

## 3. SOP ingestion pipeline data design

### 3.1 Input formats

- **Word** (`.docx`): python-docx or Apache Tika; structure from heading styles + tables.
- **PDF** (`.pdf`): pypdf + layout-aware parser (Unstructured / pdfminer.six) for heading detection; OCR fallback on scanned PDFs. **Parser selection is OF-5.4 (E6).**

**Input bundle contract:**
```
uploads/<sop_id>/<sop_version>/
  ├─ manifest.json     { sop_id, sop_version, declared_source_count, uploader_pseudo_id, uploaded_at }
  ├─ sources/*.docx|.pdf
  └─ signature         (optional; uploader signs manifest)
```

### 3.2 Parsing output schema (intermediate)

```
ParsedSection {
  section_path:  str            # e.g. "2.3.1 > Remediation > Step 4"
  section_type:  str            # remediation|reference|precondition|escalation|overview|other
  raw_text:      str
  source_file:   str
  page_range:    [int, int]?
}
```

### 3.3 Chunking output schema

Structure-aware primary: one chunk per `ParsedSection` when `len(text) ≤ max_tokens`; else recursive split at paragraph → sentence preserving `section_path`. Target 500–1000 tokens, 100 overlap (E3 §3.2).

Chunk record written to `sop_chunk` with fields per §1.6. Initial `lifecycle_state='pending_review'` (Targeted #2); flips to `'active'` on SME approval.

### 3.4 Embedding schema

- Model: **Granite Embedding** (E3 §2.2).
- Dimension: `vector(768)` — **OF-5.1** to confirm at E6 against deployed model card.
- Generated at ingest; **re-embedding on model-version change** handled as new `sop_version` ingest (new row; preserves provenance).

### 3.5 Index schema

Primary retrieval: pgvector HNSW on `sop_chunk.embedding`.

```sql
CREATE INDEX sop_chunk_embedding_hnsw ON sop_chunk
  USING hnsw (embedding vector_cosine_ops)
  WHERE lifecycle_state IN ('active','deprecation_window');
```

- **Cosine distance** assumed typical for sentence-level embeddings; **OF-5.2** to confirm at E6 against Granite Embedding training objective.
- HNSW tuning (M, ef_construction, ef_search) is **OF-5.3** (E6 tune against latency target <5s per E3 §3.2).
- Rebuild triggered on bulk ingestion; incremental on single-SOP update.
- Retrieval re-ranks by `section_type` weight (remediation > precondition > reference > overview).

### 3.6 Version management

**States (Targeted #2 enum):**
- `pending_review` — post-ingest, awaiting SME.
- `active` — SME-approved, latest version.
- `deprecation_window` — superseded; retained 90d for in-flight reviews + audit reconstruction.
- `archived` — moved to object storage; pgvector row deleted; pointer in `sop_chunk_archive_index`.

**Version-pinning semantics** (E3 §4.3 preserved): `recommendation.sop_references` carries `{sop_id, sop_version, chunk_ids[]}`; resolution order at reconstruction: active → deprecation_window → archive pointer.

### 3.7 Archival trigger

CronJob (`sop-archive-job`) runs daily:
```
SELECT chunk_id FROM sop_chunk
WHERE lifecycle_state='deprecation_window'
  AND superseded_at < now() - interval '90 days';
```
Per match:
1. Bundle chunk metadata + text + embedding vector + content_hash into archive object.
2. Write to OF-4.9 staging bucket.
3. Integrity verifier: recompute content_hash (canonical per OF-5.18) + confirm match to chain entry.
4. On OK: copy staging → Compliance-locked bucket; INSERT `sop_chunk_archive_index`; DELETE `sop_chunk` row; chain entries `staging_integrity_verified` + `sop_chunk_archive_move`.
5. On failure: alert + leave in `deprecation_window`.

---

## 4. Synthetic test corpus data design

### 4.1 Corpus schema (§1.12)

Two tables: `test_corpus` (individual test incidents) and `synthetic_corpus_artefact` (generation-run-level provenance).

### 4.2 Ground-truth labelling structure

`test_corpus.ground_truth` JSONB schema:
```json
{
  "expected_decision_class": "REMOTE_RESOLUTION" | "FIELD_DISPATCH" | "UNAVAILABLE",
  "expected_sop_references": [{"sop_id": "...", "relevance": "primary"|"secondary"}],
  "expected_correlation_outcome": "none" | "related_found" | "cluster_member",
  "expected_diagnosis_hypothesis": "...",
  "acceptable_variance": {
    "decision_class": ["REMOTE_RESOLUTION"],
    "sop_id_overlap_min": 1
  },
  "rationale_text": "...",
  "labelled_at": "...",
  "labelled_by_pseudo_id": "..."
}
```

### 4.3 Versioning

- `test_corpus.corpus_version` = semver tag; each release is an immutable snapshot referenced by E7 test runs.
- Retirement: `retired_at` set; rows never deleted.
- Retention: indefinite pending CI-7 resolution (**OF-5.16** — Targeted #5 confirmed; k-anonymity ≥5 is primary guard).

### 4.4 Generation provenance chain records

Per synthetic run, `governance_chain` receives:
1. `test_corpus_generation` entry (E3 §4.2 canonical) with `payload_ref={artefact_id, generation_run_id, pattern_catalog_version, synthesis_model_version, k_anonymity_k, generated_count}`.
2. On SME review: `test_corpus_generation` with sub-kind `sme_decision` in payload.
3. Per-test-incident inserts: batch-recorded via the artefact entry; per-row chain entries only on subsequent *access* events.

**Provenance query** (Layer-2 view): `synthetic_corpus_artefact ⋈ governance_chain WHERE entry_type='test_corpus_generation'` → full lineage: pattern_catalog_version → synthesis_model_version → SME approval → chunk count.

### 4.5 Access control (OF-4.10)

Row-level: `sensitivity_class='restricted_internal'` + RBAC (E4 §5) → `sre` + `admin`; chain-recorded access. Bulk-export subject to a joint-session gate analogous to OF-4.8.

---

## 5. Data quality rules

Rules keyed by `rule_id`. Violations → `validation_failure` row + chain entry `validation_failure` (allowlist per OF-5.17).

### 5.1 Intake (FR-A.3)

| rule_id | Rule | Severity |
|---|---|---|
| INT-001 | CTTS payload JSON parses | reject |
| INT-002 | Required fields per CI-9 present (`incident_id`, `timestamp`, `affected_nodes`, `symptom`, `severity`) | reject |
| INT-003 | `severity` ∈ `{P1..P5}` | reject |
| INT-004 | `ingest_at − ctts_received_at ≤ 24h` | warn |
| INT-005 | `affected_nodes` non-empty array | reject |
| INT-006 | `symptom_text` length 1..8192 | reject |
| INT-007 | `ctts_incident_ref` not already accepted with different `content_hash` | quarantine (potential tamper) |
| INT-008 | No secret-pattern match on `symptom_text` (OF-5.7) | quarantine (mask + alert) |

**Malformed outcome (INT-001–003, 005–006):** `intake_state='malformed_rejected'`; no agent invocation; chain `ticket_rejected_malformed` + `validation_failure`.

### 5.2 Agent output

| rule_id | Rule | Severity |
|---|---|---|
| AGO-001 | `output_payload` conforms to per-agent pydantic schema | reject (recommendation degrades per FR-B.1.4) |
| AGO-002 | `status ∈ enum` | reject |
| AGO-003 | `completed_at ≥ started_at` | reject |
| AGO-004 | `tokens_in + tokens_out ≤ model_context_limit` | warn |
| AGO-005 | `reasoning_trace` size ≤ 64 KiB | warn + truncate-with-marker |

### 5.3 Recommendation (FR-C.1)

| rule_id | Rule | Severity |
|---|---|---|
| REC-001 | All required FR-C.1 fields present | reject |
| REC-002 | `decision_class ∈ {REMOTE_RESOLUTION, FIELD_DISPATCH, UNAVAILABLE}` | reject |
| REC-003 | `decision_class='REMOTE_RESOLUTION'` → non-empty `sop_references` | reject |
| REC-004 | Every `sop_references.chunk_ids[]` resolves to an active / deprecation_window / archive-indexed chunk | reject |
| REC-005 | `system_version` and `sop_corpus_version` match intake row | reject (provenance break) |
| REC-006 | `produced_at − incident.ingest_at ≤ 3 min` (NFR-L.1) | warn (SLA metric) |
| REC-007 | `production_seq` monotonically increasing per `incident_id` | reject |

### 5.4 Operator decision (FR-D)

| rule_id | Rule | Severity |
|---|---|---|
| DEC-001 | `pseudonymous_operator_id` resolves in `operator_identity_map` with `retired_at IS NULL` at `decision_at` | reject |
| DEC-002 | `decision_kind='rejected'` → `reason_code ∈ CI-2.reject_codes` | reject |
| DEC-003 | `decision_kind='overridden'` → `override_action_class` + `override_action_detail` present; `reason_code ∈ CI-2.override_codes` | reject |
| DEC-004 | RBAC: `operator`/`supervisor` only | reject |
| DEC-005 | One terminal `operator_decision` per `(incident_id, recommendation_id)` | reject (idempotency via `correlation_token`) |

### 5.5 SOP ingestion

| rule_id | Rule | Severity |
|---|---|---|
| SOP-001 | Manifest parses; `sop_id` + `sop_version` present | reject-run |
| SOP-002 | `sop_version` strictly greater than any prior `active`/`deprecation_window` version for same `sop_id` | reject-run |
| SOP-003 | Each chunk has non-empty `text`, computed `embedding`, `content_hash` | reject-chunk |
| SOP-004 | No secret-pattern match on chunk text (OF-5.7) | quarantine-chunk + SME review |
| SOP-005 | Chunk count > 0 | reject-run |
| SOP-006 | `source_file` accessible + SHA-256 matches declared manifest | reject-run |
| SOP-007 | SME review = `approved` before `lifecycle_state` flips to `active` | block activation |

### 5.6 Write-back (FR-E.1–4)

| rule_id | Rule | Severity |
|---|---|---|
| WB-001 | `correlation_token` unique | reject (idempotency) |
| WB-002 | CTTS 2xx response | retry-or-fail per E3 §5.4 |
| WB-003 | `ctts_writeback_state` transitions legal: `pending → retrying → ok/failed` | reject illegal |

### 5.7 Export / audit (OF-4.12)

| rule_id | Rule | Severity |
|---|---|---|
| EXP-001 | Requester role ∈ {`auditor`,`admin`} | reject |
| EXP-002 | Bundle signature verifies against Root KMS master | reject-on-consume |
| EXP-003 | Chain slice covers full requested time-range without gaps | warn (report gap) |

### 5.8 Failure recording protocol

Every failure writes:
1. `validation_failure` row (noc-data).
2. Chain entry `validation_failure` (AG-3 allowlist OF-5.17) with `payload_ref={failure_id, stage, rule_id, severity, subject_ref}`.
3. Alert on `severity='reject'` or `'quarantine'` (Alertmanager routing per CI-8).

**Chain-write-of-validation-failure exception:** if the chain write of a `validation_failure` entry itself errors, the failure falls back to OpenShift platform logs + Alertmanager (E3 §6.5). This preserves operational visibility without recursion.

---

## 6. OF-4.15 problem-management data model (MAS 7.8 partial)

Scope: **minimal viable** structure linking problems to incident corpus. Full workflow UI + root-cause tooling is E6. Honest posture per E4 §1.2 (7.8 = PAR).

### 6.1 Schema

`problem` + `problem_incident_link` per §1.14. Both tables emit chain entries on state transitions (`problem_created`, `problem_linked`, `problem_closed`; allowlist per OF-5.17).

### 6.2 Link kinds

- `example` — one of many similar incidents under the problem (trend grouping).
- `root_cause_instance` — confirmed instance caused by the identified root cause.
- `symptom_match` — incident exhibits the pattern pre-confirmation.

### 6.3 Trend linkage via Correlation-Agent evidence

Read-only join: `problem_incident_link ⋈ agent_output WHERE agent_kind='correlation'` surfaces past correlation-agent evidence relevant to a problem. Consumed by Layer-2 `incident_trends` view (E4 §7.1 row 7.8).

### 6.4 Out of E5 scope (handover to E6)

- Root-cause-analysis workflow (5-whys, fishbone templates) — E6 UI.
- Automated problem-detection from incident clustering — E6/E7.
- Problem-to-change-request linkage (MAS 7.5) — E6.
- Problem-SLA / due-dates — CI pending (client ops).
- **`problem_status_history` (OF-5.19 — Targeted #7):** deferred to E6; activates if MAS 7.8 scope grows beyond PAR.

---

## 7. Open items for E6

E5 items to build + bind at E6. Register uses OF-5.x to keep separate from inherited E4 register.

| OF-# | Item | E5 position | E6 scope |
|---|---|---|---|
| OF-5.1 | Embedding dimension + model-version lock | `vector(768)` assumed | Confirm + lock in deployment manifest; drift-detector on `embedder_model_version` |
| OF-5.2 | pgvector distance metric | Cosine assumed | Confirm against Granite Embedding training objective; add recall eval |
| OF-5.3 | HNSW tuning (M, ef_construction, ef_search) | Defaults | Tune to <5s retrieval target (E3 §3.2) |
| OF-5.4 | PDF parser selection (pdfminer / Unstructured / Tika) + OCR fallback | Flagged as selection | E6 selects + binds; E7 test coverage on scanned PDFs |
| OF-5.5 | Partition size + retention detach cadence | Monthly partitions assumed | E6 CronJob + `pg_partman` or equivalent |
| OF-5.6 | Cross-cluster `chain_id` orphan-detection + commit-observation tightening | 30-min grace; `chain_id_committed_at` added (Targeted #6) | E6 decide per-write vs daily verification trade-off + grace tightening |
| OF-5.7 | Secret-pattern regex register (INT-008, SOP-004) | Placeholder | E6 curate per CI-9 + CI-10; client-supplied when available |
| OF-5.8 | CI-2 reason-code taxonomy binding (DEC-002/003) | Flagged dependency | Client input CI-2; E6 enforce at Review API |
| OF-5.9 | Rate-limit + anomaly thresholds for OF-4.8 | Schema supports | E6 config + tuning with auditor role holder |
| OF-5.10 | Problem-mgmt workflow UI (OF-4.15 continuation) | Schema only | E6 UI + Layer-2 `incident_trends` dashboard |
| OF-5.11 | Test-corpus SME validation UI | Schema only | E6 reviewer surface for SME gate |
| OF-5.12 | Two-role joint-session implementation (OF-4.8 bulk reads) | Schema supports | E6 `identity-audit-api` endpoint + session protocol |
| OF-5.13 | Keep-alive daemon ∥ synthesis pipeline isolation | Granite endpoints covered; Llama cold-start batch path | E6 confirm batch does not share hot-path endpoint |
| OF-5.14 | Archive-bundle manifest + signature format (OF-4.12 sibling) | Referenced | E6 schema + signature-verification tooling |
| OF-5.15 | Row-level encryption for `operator_identity_map.display_name` | LUKS2 at-rest applies | E6 evaluate if threat model demands column-level too |
| OF-5.16 | Test-corpus retention review on CI-7 resolution | Targeted #5 confirmed; k-anon ≥5 primary guard | Re-examine at CI-7 resolve; E6 surfaces the trigger |
| **OF-5.17** | **Chain-Write Service `entry_type` allowlist enforcement (AG-3)** (Targeted #3) | Canonical allowlist listed §1.11 | **E6 implementation requirement**: AG-3 validator rejects unknown `entry_type`; allowlist in version-controlled schema; test covers rejection path |
| **OF-5.18** | **content_hash canonicalisation rule** (Targeted #4) | Sorted-keys JSON, compact, UTF-8, SHA-256 (§1.17) | **E6 implementation + test requirement**: Chain-Write Service applies canonicalisation before HMAC; property-based test across Unicode edge cases |
| **OF-5.19** | **`problem_status_history` as MAS 7.8 scope-growth extension** (Targeted #7) | Not built | E6 extension when/if MAS 7.8 moves beyond PAR |
| **CI-E5.1** | Granite Embedding dimension/version confirmation | Flagged | Resolved at E6 via model-card |
| **CI-E5.2** | Distance-metric appropriateness vs training objective | Flagged | Resolved at E6 via model-card |

---

## 8. Requirements coverage confirmation

| E2/E3/E4 obligation | E5 satisfaction |
|---|---|
| E3 §4.2 `governance_chain` preserved | §1.11 additive only; append-only trigger explicit; AG-3 allowlist (OF-5.17) |
| E3 §4.1 two-cluster split | §1.1 cluster/namespace assignment respected |
| E3 §4.3 SOP version-pinning | §1.6 + §3.6 lifecycle_state + `recommendation.sop_references` |
| E3 §4.4 identity map governance-tier-only | §1.9 + §1.10 |
| E3 §4.5 Chain-Write WAL semantics | §2 flows emit via Chain-Write Service; produced-on-WAL preserved |
| E4 §3 key hierarchy | §1.15 `key_lifecycle_event` mirrors chain |
| E4 §5 RBAC | Tables carry pseudonymous IDs only; access via identity-audit-api |
| E4 §7.3 per-class retention | §1.7 `retention_until`; §1.15 10y key ops; archive flows |
| E4 OF-4.8 strengthened | §1.10 access log + joint_session_id + rate_limit_bucket + anomaly_flag |
| E4 OF-4.9 staging bucket | §2.7 archival; `staging_verified_at` captured |
| E4 OF-4.10 synthetic sensitivity | §1.12 `sensitivity_class`; §4.5 access; OF-5.16 |
| E4 OF-4.15 problem mgmt | §1.14 + §6 minimal schema |
| FR-A..F coverage | §2 flows per stage |
| FR-D.4 re-present semantics | Targeted #1: `production_seq` + relaxed uniqueness |
| FR-F.1 version reconstruction | §3.6 lifecycle states + archive pointer |
| FR-E.4 idempotency | `correlation_token UNIQUE` |
| NFR-AU.4 single-query audit | Layer-2 view joinable by `incident_id` across all tables (E6 binds views) |

---

## 9. Flags and posture declarations

### 9.1 DISCIPLINE-2 preserved

No architectural selection at E5. Every schema and flow decision cites E3 architecture, E4 security posture, or an E2 requirement. Where a binding is required but not architectural (HNSW defaults, parser choice, distance metric), the decision is deferred to E6 with an OF-5.x item.

### 9.2 Governance mode: partial

DSC claims on data-flow governance apply to MVGH-β-active state (per E4 §1.0 bifurcation). During the interim, chain writes occur but full-harness enforcement is not all live.

### 9.3 Append-only invariant preserved

`governance_chain` receives no UPDATE or DELETE paths anywhere in §1–§6. DB trigger enforces; AG-3 allowlist (OF-5.17) enforces additionally at write-time.

### 9.4 Cross-cluster FK honesty

Logical references only; enforcement by protocol + `chain_id_committed_at` observation + daily verifier + orphan-detection. Tightening is **OF-5.6** (E6 decision).

### 9.5 Honesty bound reaffirmed (S6 §4.6)

- Schema-level controls that will be active at MVGH-β-active state are described as such; interim posture preserves the PAR framing from E4 §1.0.
- No claim that MAS TRM data-controls are pre-certified. Evidence is generated; institution files attestation.

### 9.6 Client-input dependencies still open

CI-1, CI-1a, CI-2, CI-3, CI-5, CI-6, CI-7, CI-8, CI-9, CI-10, CI-13, CI-14, CI-15, CI-16, CI-17, CI-18, CI-19, CI-20 inherited unchanged. **CI-3 has a specific E5 hook:** re-present-after-timeout selection activates `production_seq > 1` path.

### 9.7 No new carry-forwards, no new disciplines

---

## 10. E6 Build inheritance

E6 opens with this artefact as primary input.

**E6 inherits:**
1. **Full schema DDL** — 14 tables across `noc-data` + `noc-gov` + archive index; governance_chain additive-only + append-only trigger.
2. **7 data flows** — intake, analysis, recommendation, review, write-back, SOP ingestion, archival — each with Chain-Write Service integration + AG-3 allowlist.
3. **SOP ingestion pipeline** — parser choice (OF-5.4), HNSW tuning (OF-5.3), embedding lock (OF-5.1), distance metric confirmation (OF-5.2) all E6 bindings.
4. **Synthetic test corpus schema** — E7 consumes.
5. **Data quality rules register** — 7 stages × 30+ rules; E6 binds validation layer + allowlist enforcement.
6. **19 active OF-5.x items** (includes 4 new Targeted additions: OF-5.17, OF-5.18, OF-5.19; OF-5.6 continuation).
7. **CI-3 re-present hook** — `production_seq` field to be wired only if config selects re-present.
8. **Chain-write canonicalisation + allowlist** — Targeted adjustments #3 + #4 are E6 implementation mandates.

---

## 11. Carry-forwards and Disciplines

**Carry-forwards (4, inherited):**
- CARRY-FWD-1 — Need 13 partial technical-constraint readiness.
- CARRY-FWD-2 — Anthropic platform concentration (substrate only; product runs Granite on OpenShift AI).
- CARRY-FWD-3 — C4 capacity binding constraint.
- CARRY-FWD-4 — MVGH-β first governed delivery; partial-governance interim.

**No new carry-forwards introduced at E5.**

**Disciplines (3, inherited):**
- DISCIPLINE-1 — source-of-count tagging.
- DISCIPLINE-2 — constraint citations on every selection; E5 makes no architectural selection.
- DISCIPLINE-3 — qualitative classification cites criterion.

**No new disciplines introduced at E5.**

---

*End of E5 exit artefact.*
