# E3 — Architecture — Exit Artefact

## 0. Status and derivation

**Convergence state at exit:** Exact. Ratified.
**Primary derivation intent:** docs/e2-exit-artefact.md; docs/e3-knowledge-contribution.md; docs/s6-solution-brief.md.
**Contributing cycles:** E3.1 Explorative (first-pass architecture across 7 deliverables + selections from E2-flagged E3-owned choices); E3 Targeted → Exact (9 adjustments absorbed).

**Governance mode at this cycle:** **Partial governance.** Cycle primitives active; full-harness infrastructure activates progressively as MVGH-β setup completes (per CARRY-FWD-4).

## 1. Architecture overview

```
                       CTTS (client's ticketing system)
                           ▲                ▲
                 REST poll │                │ REST write-back
                           │                │
  ┌────────────────────────┴────────────────┴──────────────────────────┐
  │                  NOC Incident Management Product                    │
  │                (RedHat OpenShift AI, on-prem, client network)       │
  │                                                                     │
  │  ┌──────────────────┐                                               │
  │  │ Intake Adapter   │─┐                                             │
  │  │ (CTTS REST poll) │ │                                             │
  │  └──────────────────┘ │                                             │
  │                       ▼                                             │
  │          ┌────────────────────────────┐                             │
  │          │  Agent Orchestrator        │  LangGraph                  │
  │          │  (graph-coordinated)       │  3-min sub-budget           │
  │          └────────────┬───────────────┘                             │
  │                       │                                             │
  │        ┌──────────────┼──────────────┐                              │
  │        ▼              ▼              ▼                              │
  │  ┌─────────┐    ┌───────────┐   ┌────────┐                          │
  │  │Diagnosis│    │Correlation│   │  SOP   │                          │
  │  │  Agent  │    │   Agent   │   │ Agent  │                          │
  │  └────┬────┘    └─────┬─────┘   └────┬───┘                          │
  │       │               │              │                              │
  │       ▼               ▼              ▼                              │
  │   ┌──────────────────────────────────────┐                          │
  │   │ Model Serving: IBM Granite (vLLM)    │                          │
  │   │ Embedding: Granite Embedding         │                          │
  │   └──────────────────────────────────────┘                          │
  │                                                                     │
  │   ┌─────────────────────┐    ┌──────────────────────┐               │
  │   │ INCIDENT-TIER PG    │    │ SOP Ingest Pipeline  │ (Kubeflow)    │
  │   │ • pgvector (SOP,    │◀───│ Word/PDF → chunk →   │               │
  │   │   symptoms)         │    │ embed → index        │               │
  │   │ • incidents,        │    └──────────────────────┘               │
  │   │   recommendations,  │                                           │
  │   │   operator_decisions│                                           │
  │   └──────────┬──────────┘                                           │
  │              │                                                      │
  │              ▼ (one-directional bridge)                             │
  │   ┌────────────────────────┐                                        │
  │   │ Chain-Write Service    │◀── local-disk WAL (sync)               │
  │   │ WAL→PG commit (async)  │                                        │
  │   └───────────┬────────────┘                                        │
  │               ▼                                                     │
  │   ┌─────────────────────────┐    ┌──────────────────────┐           │
  │   │ GOVERNANCE-TIER PG      │───▶│ Object Storage       │           │
  │   │ • governance_chain      │    │ Ceph / S3-compat     │           │
  │   │   (append-only, HMAC)   │    │ • SOP archive        │           │
  │   │ • operator_identity_map │    │ • Chain archival     │           │
  │   │   (access-restricted)   │    │ • 7-yr retention     │           │
  │   └─────────────────────────┘    └──────────────────────┘           │
  │                                                                     │
  │   ┌──────────────────┐         ┌───────────────────────────┐        │
  │   │ Reviewer UI      │◀───────▶│ Review API                │        │
  │   │ HTMX + FastAPI   │  SSO/   │ • present recommendation  │        │
  │   │ single Python    │  SAML   │ • capture decision        │        │
  │   │ stack            │         │ • write-back to CTTS      │        │
  │   └──────────────────┘         └───────────────────────────┘        │
  │                                                                     │
  │   ┌──────────────────────────────────────────────────────┐          │
  │   │ Observability: Prometheus + Grafana (OpenShift)      │          │
  │   └──────────────────────────────────────────────────────┘          │
  └─────────────────────────────────────────────────────────────────────┘

Developer-side (distinct process, not product runtime):
4WRD governance harness on Claude Agent SDK — cycle primitives,
chain substrate, adversarial challenge. Does not run on OpenShift AI.
```

**Data flow.** CTTS → Intake Adapter polls → (malformed → rejection chain entry, stop) → Agent Orchestrator → fan-out to Diagnosis / Correlation / SOP agents → model inference via Granite → fan-in at Orchestrator → recommendation → **Chain-Write Service WAL (sync) → recommendation produced** → async commit to governance-tier PG → Reviewer UI → operator decides → decision written to CTTS + chain.

**Runtime boundaries.** Everything inside the box lives on client-network OpenShift AI. External egress forbidden (IR-O.4). SSO/SAML is the only identity-plane external-to-product dependency.

---

## 2. Agent architecture

### 2.1 Orchestration framework

**Selection: LangGraph (Python)** for per-incident agent orchestration.

**Rationale (constraint-grounded):**
- **NFR-L.1 / 3-min sub-budget + FR-B.1.2**: LangGraph expresses sequential-vs-parallel-vs-hybrid as graph topology; parallelises Diagnosis + Correlation + SOP where context permits.
- **FR-B.1.4 graceful degradation**: conditional edges support "agent X unavailable" branches with partial-recommendation composition.
- **NFR-R.1 deterministic reconstruction**: state-checkpointing permits per-node output capture for chain recording.
- **IR-O.3 / IR-O.4**: library — runs entirely in-process on OpenShift AI; no external dependency.
- **FR-B.1.3 compose outputs**: merge nodes produce structured composition for FR-C.1 payload.

**Lock-in mitigation (per Targeted adjustment #6):** Framework churn risk is accepted **with explicit mitigation** — agent-interface contracts (input/output state schemas) are mandated as an **E6 implementation requirement**. Each agent is expressed as a thin adapter over a framework-agnostic `AgentInterface`:

```
AgentInterface:
  input:  AgentStateInput   (pydantic schema; per-agent)
  output: AgentStateOutput  (pydantic schema; per-agent)
  invoke(input) → output
```

LangGraph nodes are thin wrappers invoking the `AgentInterface`. A future framework swap replaces the wrappers, not the agent logic. E6 shall enforce this separation in PR review / module boundary discipline.

**Alternatives considered:**
- **LlamaIndex Agents**: repurposed for RAG primitives in the SOP pipeline (§3.2), not orchestration.
- **OpenShift AI Pipelines (Kubeflow)**: batch semantics, pod-per-step incompatible with NFR-L.1. Used for SOP ingestion batch jobs + synthetic-gen, not per-incident orchestration.
- **Custom Python asyncio**: rejected — re-implementation cost, loss of standard observability integration.

### 2.2 Model selection

**Selection: IBM Granite 3.x Instruct** as primary reasoning model; **Granite Embedding** for vector embeddings.

**Rationale (constraint-grounded):**
- **IR-O.1 / IR-O.3**: Granite is first-party RedHat/IBM-supported on OpenShift AI; validated serving path via vLLM.
- **IR-O.4**: weights ship on-prem; inference fully local.
- **NFR-L.1**: Granite 3 Instruct at 8B / 34B-class provides sufficient reasoning within budget on GPU-class nodes; E8 sizes.
- **Stack coherence**: single model family — one inference runtime, one tokenizer, same embedding model simplifies SOP RAG pipeline.

**Fallback candidates:** Llama 3.x (primary fallback) and Mistral (secondary) — both self-hostable on OpenShift AI, compatible with vLLM, invoked only if Granite capability insufficient per E7 quality testing.

**Synthesis model (separate from production inference):** **Llama 3.x** for synthetic test-incident generation (§7). Cross-family separation reduces systematic-bias coupling between synthesis and production inference; P4 credibility strengthened (Targeted adjustment #5).

**Model-serving runtime:** **vLLM on OpenShift AI Model Serving** — high-throughput inference, continuous batching, OpenShift AI-supported.

### 2.3 Per-agent architecture

Each agent is a LangGraph node wrapping an `AgentInterface` implementation (§2.1 mitigation).

**Agent Orchestrator (product) — LangGraph root.**
- Input: normalised incident payload (§3.1).
- Plan: **parallel-fan-out Diagnosis + Correlation; SOP sequential-on-Diagnosis** (SOP retrieval informed by diagnostic hypothesis); Orchestrator merge + conditional degradation branch on any-agent-failure.
- Output: FR-C.1 recommendation payload.
- Timeout: 3-min total sub-budget; per-agent timeout 60s.

**Diagnosis Agent.**
- Input: incident payload; sub-scope: symptoms + affected-nodes + severity.
- Prompt-chain: (i) extract observable symptoms; (ii) hypothesise fault; (iii) rank; (iv) produce reasoning trace.
- Model: Granite Instruct.
- Output: ranked hypotheses + reasoning trace + `insufficient_data` flag (FR-B.2.3).

**Ticket Correlation Agent.**
- Input: incident payload + correlation-window parameters (CI-17).
- Retrieval: hybrid query on `incident` table — structured filter (time-window, affected-node, customer) + pgvector similarity on symptom-embedding.
- Prompt: synthesise related-ticket evidence.
- Output: correlation evidence + `none_found` flag (FR-B.3.4).

**SOP Agent.**
- Input: incident payload + Diagnosis fault hypothesis.
- Retrieval: RAG over SOP index (§3.2) — top-k chunks with metadata.
- Prompt: extract remediation guidance from retrieved chunks.
- Output: remediation guidance + SOP references + `no_applicable_sop` flag (FR-B.4.4).

**Composition at Orchestrator merge:**
- Decision class (REMOTE_RESOLUTION vs FIELD_DISPATCH) inferred from SOP remediation type + severity + correlation pattern; CI-1 taxonomy-pending (fallback: structurally-complete recommendation only).
- Payload assembled per FR-C.1.
- Chain entry via Chain-Write Service WAL (§4.5).

### 2.4 Coordination timing budget

**Steady-state (warm path):**

| Step | Budget | Rationale |
|---|---|---|
| Intake normalisation | 5s | structured parse; no LLM |
| Diagnosis (~3 LLM calls) | 45s | ranked hypotheses + reasoning |
| Correlation (retrieval + 1 LLM call) | 30s | hybrid retrieval + synthesis |
| SOP (retrieval + 1 LLM call) | 30s | RAG retrieval + extraction |
| Composition + WAL write | 15s | merge + WAL-sync |
| **Parallel: Diagnosis ∥ Correlation → SOP-seq-on-Diagnosis** | **~75s max** | |
| **Steady-state worst case** | **~95s** | under 3-min (180s) budget |

**Cold-start path (per Targeted adjustment #2):**

| Step | Cold overhead | Note |
|---|---|---|
| vLLM model load (first invocation after restart) | +25s | model into GPU memory |
| First-token latency on cold model | +10s | KV-cache cold |
| PG connection-pool warm-up | +3s | pool initialisation |
| Embedding model cold-start | +2s | small model |
| **Cold-start overhead total** | **~40s** | one-time after service restart |
| **Cold-start worst case (95 + 40)** | **~135s** | still under 180s budget |

**Headroom:** ~45s under worst-case cold-start budget.

**Keep-alive mitigation (E6 implementation mandate):**
- **Keep-alive ping job** scheduled every 60s hitting Granite Instruct + Granite Embedding endpoints with a trivial prompt, maintaining warm KV-cache and avoiding model-unload under idle.
- **PG connection pool** held open with min-pool-size > 0.
- **Intended outcome:** cold-start path applies only to service-restart / deploy-rollout windows; normal operation stays in steady-state ~95s envelope.
- **E6 shall implement the keep-alive daemon as part of service deployment** (explicit handover to E6).

---

## 3. Integration architecture

### 3.1 CTTS REST API polling (incl. FR-A.3 per Targeted adjustment #8)

- **Poll interval: 15 seconds.** Rationale: intake-latency <10% of 3-min sub-budget; 15s provides 12s worst-case delay at acceptable CTTS load.
- **State marker:** last-seen-incident-modified-timestamp in incident-tier PG; persisted across restarts.
- **Concurrency:** single active replica (leader-elected via lease) + 1 standby; failover window < 30s (E6 implements; validates against CTTS intake tolerance).
- **Deduplication:** incident-ID-keyed upsert; IR-T.5 idempotency.
- **Auth:** CTTS service-account token in OpenShift Secret; rotation E4-owned.
- **Error handling (polling):** on CTTS unreachable, retry 3× exponential (2s/4s/8s) then alert (NFR-O.4); no block on intake — late arrivals surface on next successful poll.
- **Malformed-ticket handling (FR-A.3):** malformed intake payloads **do not queue for agents**. On schema-validation failure, Intake Adapter:
  1. Emits a `ticket_rejected_malformed` governance chain entry with incident-ID, arrival time, validation-error summary.
  2. Acknowledges CTTS read (state marker advances) so the malformed ticket does not re-poll infinitely.
  3. Alerts ops (NFR-O.4).
  4. **Does not invoke agents** — the 3-min sub-budget is not consumed on garbage input.
- **Write-back:** REST PATCH/POST against originating incident-ID on decision; idempotent (FR-E.4) via product-side correlation-token + retry-on-transient (3× exponential).

### 3.2 SOP/KB RAG pipeline

**Ingestion (Kubeflow on OpenShift AI Pipelines):**

```
Word/PDF sources → document parsing (Apache Tika or equivalent)
  → structure-aware chunking (recursive fallback)
  → metadata extraction → embedding (Granite Embedding)
  → pgvector upsert + archive to Object Storage
```

- **Chunking:** structure-aware primary (section/subsection/procedure-step boundaries); recursive character splitter fallback (~500–1000 tokens, ~100 overlap).
- **Metadata per chunk:** `{sop_id, sop_version, section_path, chunk_seq, ingest_timestamp, source_uri, content_hash}`.
- **Embedding:** Granite Embedding in-cluster (IR-O.4).
- **Index:** pgvector in incident-tier PG (§4).
- **Cadence:** nightly full reconcile + on-demand incremental (CI-13 informs).
- **Versioning and deprecation (per Targeted adjustment #9):**
  - New SOP version creates new chunk set with `sop_version` bumped.
  - **Deprecation window: 90 days after version supersession.** During the window, superseded version's chunks remain queryable (for in-flight reviews citing the older version; for audit reconstruction).
  - **After 90 days:** chunks moved to `sop_chunk_archive` in object storage; reconstruction via archive retrieval (FR-F.1).
  - **Deprecation window is configurable** (default 90d); override via platform configuration.
  - **E8 operationalises the archive-move job** (scheduled CronJob + integrity verification).

**Retrieval (per-incident by SOP Agent):**
- Query embedding via Granite Embedding on {fault hypothesis + symptoms}.
- Top-k (k≈10) vector similarity on **active + in-deprecation-window** chunks; re-rank by section-type (remediation > reference).
- Return top-3 chunks with full metadata.
- Latency target: <5s (within 30s SOP budget).

### 3.3 Reviewer UI architecture (per Targeted adjustment #4)

**Selection: FastAPI + HTMX — single Python stack.**

**Rationale:**
- **CI-11** separate app — satisfied by dedicated Review API + UI.
- **Stack-surface reduction (§6 role-compression)** — drops JavaScript/TypeScript build chain + React ecosystem; single Python codebase for API + UI renders.
- **Operational simplicity** — HTMX is static JS via CDN-equivalent (served locally per IR-O.4); no frontend build pipeline; server-rendered HTML with attribute-driven interactivity.
- **Solo-orchestrator maintainability** — fewer languages, fewer toolchains, fewer dependency graphs to track.

**Structure:**
- **FastAPI backend** serves both JSON API (for scripted/audit access) and HTML views (Jinja2 templates + HTMX attributes).
- **HTMX interactivity** for: approve/reject/override forms; incident-detail expansion; reason-code pickers; live-polling of pending-queue.
- **Static assets** (CSS, HTMX, minimal JS) served via NGINX sidecar or FastAPI static-files mount.
- **Auth:** OIDC/SAML via client SSO provider; session cookie + CSRF token.

**UI features (scoped to FR-D.1–5):**
- Recommendation list (pending review) with live refresh.
- Recommendation detail: decision class, diagnostic summary, correlation evidence, SOP references + version + chunk excerpts, per-agent confidence/status.
- Action panel: approve / reject-with-reason / override-with-action.
- Reason-code picker (CI-2 taxonomy-driven).
- Timeout banner + FR-D.5 "recommendation unavailable" explicit state.
- **No outbound-action controls** (FR-D.6 enforced at API level).

**Operator-identity pseudonymisation:** SSO token carries real identity; Review API maps to `pseudonymous_operator_id` via governance-tier `operator_identity_map` before writing to chain (§6).

### 3.4 Alternative architectures considered

- **Reviewer UI inline in CTTS:** CI-11 resolves against this — separate app.
- **Push-based CTTS webhook:** CI-9 resolves to polling.
- **Milvus / Weaviate vector DB:** thousands-of-SOPs scale + low query-volume does not warrant separate vector store; pgvector in incident-tier PG minimises operational surface.
- **React + TypeScript + FastAPI:** dropped per Targeted adjustment #4 — stack-surface reduction priority.

---

## 4. Data architecture

### 4.1 Two-cluster PostgreSQL split (per Targeted adjustment #1)

**Incident-tier PG cluster** (`noc-data` namespace):
- `incident` — live + historical tickets.
- `recommendation` — produced recommendations (denormalised view of governance data).
- `operator_decision` — product-side decision cache for UI and write-back semantics.
- `agent_output` — per-agent output records.
- `sop_chunk` (pgvector) — active + in-deprecation-window chunks + `symptom_embedding` vectors.
- `sop_chunk_archive_index` — pointers into object-storage archive.

**Governance-tier PG cluster** (`noc-gov` namespace, **separate physical cluster**):
- `governance_chain` — append-only, HMAC-signed entries (Layer-1 records).
- `operator_identity_map` — SSO subject ↔ pseudonymous ID mapping; access-restricted (admin + audit role only).

**Chain-Write Service — one-directional bridge:**
- Source: incident-tier producers (Intake Adapter, Orchestrator, Review API).
- Path: **local-disk WAL (synchronous) → async commit into governance-tier PG**.
- **Recommendation is considered produced upon WAL-sync success** (NFR-R.4 preserved on a faster-substrate); PG commit follows asynchronously.
- **No return path from governance-tier back to incident-tier.** One-directional.
- **Failure modes:**
  - WAL-write failure: production failure — recommendation not produced.
  - WAL-to-PG commit failure (transient): retry with exponential backoff; alert on persistent failure.
  - Chain-integrity verification (§6.5) confirms WAL and PG agree; mismatches are incident-grade events.

**Rationale for split:**
- **Blast-radius isolation** — incident-tier outage does not corrupt governance chain; governance-tier outage does not halt recommendation production beyond WAL window.
- **Access-control tiering** — DB-admin on incident-tier does not by itself expose `operator_identity_map`; separation of duties for MAS TRM Access Control evidence.
- **Integrity separation** — governance-tier is append-only-enforced at DB + object-lock-enforced on archive; incident-tier has normal CRUD.
- **Pseudonymity strength** — compromising one cluster does not compromise both sides of the pseudonymous-identity mapping.

### 4.2 Governance chain data model (Layer-1 entries; governance-tier PG)

```
governance_chain (
  chain_id            UUID primary key,
  prev_chain_id       UUID,                       -- chain linkage (per-actor)
  hmac_signature      BYTEA NOT NULL,             -- per-entry HMAC
  actor_id            TEXT,                       -- pseudonymous (operator) or service-account
  actor_role          TEXT,                       -- role enum
  entry_type          TEXT,                       -- intake / ticket_rejected_malformed /
                                                  --   agent_output / recommendation /
                                                  --   operator_decision / sop_reference /
                                                  --   unavailable / test_corpus_generation /
                                                  --   adversarial_challenge (dev-side) / etc.
  ownership_tier      TEXT,                       -- SEAM-5; always user-tier here
  incident_id         UUID,                       -- denormalised for indexing (not PII here)
  payload_ref         JSONB,                      -- IDs + metadata only; full payload in
                                                  -- incident-tier / object storage
  sop_versions_pinned JSONB,                      -- [{sop_id, sop_version, chunk_ids}]
  timestamp           TIMESTAMPTZ NOT NULL,
  system_version      TEXT,
  model_version       TEXT,
  class_enum          TEXT CHECK(class_enum IN ('NORMAL','OVERRIDE'))  -- AG-3 policy
)
```

- **Append-only enforced by DB policy** (no UPDATE, no DELETE on `governance_chain`).
- **HMAC chain**: per-actor chain anchored to master anchor (master anchor lives at 4WRD-substrate level Claude Agent SDK-side for dev chain; product-side for operator/service-account chains).
- **Key management E4-owned** (T12 deferred).
- **AG-3 policy:** `class_enum='OVERRIDE'` produces rejection-event node in MVGH-active mode (S6 §6 Constraint 12).
- **AG-7 binding:** `actor_id` + `actor_role` validated at insert; cross-tier writes rejected (SEAM-5).

**Canonical entry types (not exhaustive):**

| entry_type | Emitted by | Triggers |
|---|---|---|
| `intake` | Intake Adapter | valid ticket received |
| `ticket_rejected_malformed` | Intake Adapter | FR-A.3 schema-failure |
| `agent_output` | per agent (Orchestrator proxy) | per agent invocation |
| `recommendation` | Orchestrator | FR-C.1 produced |
| `operator_decision` | Review API | FR-D.1/2/3/4 |
| `unavailable` | Orchestrator | FR-D.5 |
| `sop_reference` | SOP Agent | per retrieval (embedded in `recommendation` payload_ref) |
| `test_corpus_generation` | Synthetic gen pipeline | per generation run |
| `chain_integrity_check` | Integrity verifier job | per scheduled run |

### 4.3 SOP version-pinning mechanism

**Reference-by-version-ID with guaranteed archival** (FR-F.1 E3 resolution).

- Active + deprecation-window chunks in pgvector index are version-tagged.
- Retrieval returns `{sop_id, sop_version, chunk_id}` references.
- Recommendation chain entry records full reference set in `sop_versions_pinned`.
- On SOP update: old version enters 90-day deprecation window (§3.2 Targeted adjustment #9); after 90d, chunks move to `sop_chunk_archive` in object storage; `sop_chunk_archive_index` (incident-tier) carries pointers.
- Reconstruction (FR-F.1): join `governance_chain.sop_versions_pinned` with active-chunk table OR archive-index → retrieve from object storage.

### 4.4 Operator-identity mapping (governance-tier PG)

- **`operator_identity_map`** — separate table, separate cluster, access-restricted.
- **Schema:** `{pseudonymous_id, sso_subject_id, display_name, role, created_at, retired_at}`.
- **Write:** on first-login via SSO, Review API issues pseudonymous ID + stores mapping (via Chain-Write Service's privileged path or a dedicated identity-issuance RPC; final mechanism E4-owned).
- **Read:** only via audit-API with named access-control role.
- **Chain records reference `pseudonymous_id` only** (CI-5).

### 4.5 Chain-Write Service WAL semantics (per Targeted adjustment #3)

```
Producer (Orchestrator / Intake / Review API)
  │
  │  chain entry (Layer-1 payload)
  ▼
Chain-Write Service
  │
  ├─ 1. HMAC sign
  │
  ├─ 2. Append to local-disk WAL (fsync)
  │      └─ ON SUCCESS → ACK to producer
  │         └─ Producer treats recommendation as "produced"
  │
  └─ 3. Async commit to governance-tier PG
         └─ Retry on transient failure (exponential backoff)
         └─ Alert on persistent failure + WAL-backlog monitoring
```

- **WAL durability:** fsync on every entry; WAL survives service crash.
- **Recovery:** on restart, Chain-Write Service replays unacked WAL entries to governance-tier PG.
- **Ordering:** per-actor WAL preserves per-actor chain order; master-anchor ordering is a periodic reconcile (M9c-7 compatible).
- **Failure semantics:**
  - **Producer → Chain-Write WAL fsync fail** = recommendation not produced (NFR-R.4 preserved on WAL substrate, same guarantee as prior spec; just on a faster medium).
  - **WAL → PG commit backlog** = degraded-governance warning but production continues; observability alert (NFR-O.4).
  - **WAL → PG commit persistent failure** = chain-integrity-at-risk; Orchestrator stops producing new recommendations until resolved (fail-safe).

**Rationale:** preserves NFR-R.4 "synchronous chain write" semantics while decoupling PG availability from the 3-min sub-budget hot path. Under brief PG pause (seconds), production is unaffected; under extended PG failure, fail-safe triggers.

### 4.6 Data inventory summary

| Data class | Cluster / store | Retention |
|---|---|---|
| Incident payload (live) | Incident-tier PG | 7 years (CI-7); archive after hot window |
| Agent outputs | Incident-tier PG | 7 years |
| Recommendation | Incident-tier PG | 7 years |
| Operator decision | Incident-tier PG | 7 years |
| SOP chunks (active + deprecation-window) | Incident-tier PG (pgvector) | while active + 90d |
| SOP chunks (archived) | Object storage | 7 years |
| `governance_chain` | Governance-tier PG | 7 years; tiered to object storage after hot window |
| `operator_identity_map` | Governance-tier PG | 7 years |
| Chain-Write WAL | Local disk (per Chain-Write replica) | retention = until PG-commit; short |
| Prometheus metrics | OpenShift monitoring | 15 days hot + long-term policy E8 |
| Alerts | Alertmanager | per alert-system |
| Synthetic test corpus | Object storage + test registry (incident-tier) | indefinite; versioned |

### 4.7 Retention and archival

- **Hot (PG):** rolling 12 months of incidents, chain entries, agent outputs, decisions.
- **Warm (object storage):** 12 months → 7 years archival; compressed, indexed by incident-ID + chain-ID.
- **Archival job:** nightly CronJob moves aged partitions; chain-integrity verification runs on each move.
- **Partition seal:** sealed manifest captures chain head for tamper-evidence at hot→warm boundary.

---

## 5. Infrastructure architecture

### 5.1 OpenShift AI deployment topology

**Namespaces (4, updated for governance-tier split):**
- `noc-prod` — Intake Adapter, Agent Orchestrator, Review API, Reviewer UI, Chain-Write Service.
- `noc-data` — **Incident-tier PG** (CloudNativePG), object-storage accessor service, ingestion pipelines.
- `noc-gov` — **Governance-tier PG** (CloudNativePG, separate cluster), identity-issuance RPC.
- `noc-model` — vLLM (Granite Instruct + Granite Embedding).

**Services:**

| Service | Namespace | Type | Replicas | Resource class |
|---|---|---|---|---|
| Intake Adapter | noc-prod | Deployment (leader-elected) | 2 (1 active + 1 standby) | Small CPU |
| Agent Orchestrator | noc-prod | Deployment (stateless) | 3 (HPA) | Medium CPU |
| Review API + UI (FastAPI + HTMX) | noc-prod | Deployment (stateless) | 2 (HPA) | Small CPU |
| Chain-Write Service | noc-prod | Deployment (stateful — WAL on PVC) | 2 (active-active or active-passive; E6 decides) | Small CPU + small PVC |
| vLLM (Granite Instruct) | noc-model | ModelServing CR | 2 (per adversarial challenge 3; availability-motivated) | GPU node (L40S / H100-class; E8) |
| vLLM (Granite Embedding) | noc-model | ModelServing CR | 1 | GPU node (smaller) |
| Incident-tier PG (pgvector) | noc-data | CloudNativePG cluster | 1 primary + 2 replicas | Memory-optimised |
| Governance-tier PG | noc-gov | CloudNativePG cluster | 1 primary + 2 replicas | Memory-optimised; smaller footprint |
| SOP Ingestion Pipeline | noc-data | Kubeflow Pipeline | on-demand | CPU + GPU worker |
| Synthetic-gen Pipeline | noc-data | Kubeflow Pipeline | on-demand | GPU worker (Llama serving) |
| Keep-alive daemon | noc-prod | CronJob (every 60s) | 1 | Trivial |
| Prometheus / Grafana / Alertmanager | openshift-monitoring | OpenShift built-in | N/A | platform-tier |

**Routing / ingress:**
- Reviewer UI + Review API exposed via OpenShift Route with TLS; SSO/SAML in front.
- Intake Adapter egresses to CTTS inside client network only (IR-O.4).
- All inter-service traffic inside cluster; NetworkPolicies enforce declared flows.

**Storage classes:**
- Block (RWO) for PG volumes (both clusters) + Chain-Write WAL PVC.
- Object storage (S3-compatible / Ceph) for SOP archive, chain archival, synthetic corpus.

### 5.2 Observability wiring (Prometheus + Grafana)

- **Scrape targets:** all services expose `/metrics` (FastAPI via `prometheus-fastapi-instrumentator`; LangGraph via custom middleware; vLLM native endpoint; PG via exporter; Chain-Write Service custom).
- **Dashboards:**
  - **Operational:** per-stage latency histograms (NFR-L.4), error rates, throughput, agent-unavailable rate, approval/reject/override ratios, WAL-to-PG backlog.
  - **Proof:** adversarial-catch rate, provenance-query success rate, rework rate (GR-S.1–3).
  - **Capacity:** GPU utilisation, PG pool saturation, vLLM queue depth, keep-alive latency trend (cold-start-risk indicator).
- **Alerts:** production-sub-budget latency breach, persistent timeout, WAL→PG backlog threshold, chain-integrity-check failure, retrieval-system unavailability, keep-alive ping failure (cold-start risk). Routing **CI-8 pending**.

### 5.3 7-year retention storage tier

- **Object storage (Ceph on-prem or S3-compatible):** primary long-term store.
- **Partition scheme:** year + month; immutability lock on seal (MAS TRM IT Audit).
- **Chain-integrity on archive:** HMAC verification before archive write; sealed-partition manifest records chain head at seal.
- **Retrieval path:** audit-API service mounts read-only for reconstruction (FR-F.1 / FR-F.2).
- **Encryption at rest / key management: E4-owned.**

### 5.4 Retry policy numerics

| Call class | Timeout | Retries | Backoff | Total budget |
|---|---|---|---|---|
| Model inference (vLLM) | 30s | 2 | exponential 2s/4s | ~40s |
| Retrieval (pgvector / structured) | 5s | 1 | 500ms | ~6s |
| CTTS poll | 10s | 3 | exponential 2s/4s/8s | ~24s then alert |
| CTTS write-back | 10s | 3 | exponential 2s/4s/8s | ~24s then alert |
| Chain-Write WAL fsync | 2s | 0 | — | 2s then production-fail |
| WAL → governance-PG commit (async) | 5s | N (exponential) | up to 60s/retry cap | alert on persistent backlog |

---

## 6. Security architecture (outline — E4 hardens)

### 6.1 Identity and access

- **Operator identity: SSO/SAML** via client IdP. Review API validates SAML per request (session TTL client-policy; sensible default 8h sliding — E4 confirms).
- **Pseudonymous chain identity (CI-5):** SSO subject → pseudonymous `operator_id` via `operator_identity_map` (governance-tier PG); chain records pseudonymous ID only.
- **Service-account identities:** per-service chain actor; each has per-actor chain per AG-7.
- **AG-7 binding at insert:** actor + role-class validated.

### 6.2 Authorisation

- **RBAC (Kubernetes-native)** for platform operations on namespaces + resources; **governance-tier namespace RBAC strictly tighter** than incident-tier (named principle — DB-admin on `noc-data` does not grant access to `noc-gov`).
- **Application RBAC in Review API:** roles = `operator`, `supervisor`, `auditor`, `admin` (indicative; **E4 finalises**).
- **Audit role** has read-only access to `operator_identity_map`; no write.

### 6.3 Credential management

- **OpenShift Secrets** for CTTS service-account, DB credentials (both clusters), HMAC keys, SSO signing cert.
- **Rotation E4-owned** (T12 deferred).
- **No credentials in code, config, or chain entries.**

### 6.4 Network

- **NetworkPolicies** restrict cross-namespace flows to declared paths. Specifically:
  - `noc-prod` → `noc-data` (read/write), `noc-model` (read), `noc-gov` (Chain-Write egress **only**, no direct reads).
  - `noc-gov` isolated from incident-tier direct access; audit-API is the only read path.
- **Egress:** default-deny; allow-list covers only CTTS (internal), SSO IdP (internal), SOP source fileserver (internal). **Zero external-to-client-network egress.** IR-O.4 enforced at NetworkPolicy level + runtime egress monitoring.

### 6.5 Chain integrity

- **Per-entry HMAC** covers payload + `prev_chain_id`.
- **Chain-integrity verifier** (scheduled CronJob) walks chain daily, re-computes HMACs, alerts on mismatch.
- **Sealed-partition manifest** at archive time captures chain head for tamper-evidence across hot→warm boundary.
- **WAL-PG agreement verifier** confirms Chain-Write WAL and governance-PG contain the same entries for each actor chain (§4.5).
- **GR-E.7 chain-integrity evidence** producible once C2 custom-light is online at the 4WRD-substrate level; until then, chain-integrity-evidence-not-yet-applicable per E2 §5.2.

### 6.6 Data-at-rest / data-in-transit

- **TLS** on all service-to-service and intra-network traffic.
- **Encryption at rest on PG (both clusters), object storage, model-cache, WAL volumes** — **E4-owned** binding of mechanism + key hierarchy.

### 6.7 Synthetic test corpus access

- Access-restricted; governance chain records `test_corpus_generation` + test-run events; P4 evaluation outputs are chain-recorded.

---

## 7. Synthetic test-incident generation (CI-12 resolution)

**Approach: pattern-grounded cross-family LLM synthesis with SME validation.**

```
Historical incidents (source)
  → feature extraction (symptom types, node patterns, 
                         severity distribution, outcome labels)
  → pattern catalog (anonymised feature vectors)
  → synthesis (Llama 3.x — cross-family for bias reduction)
    • input: pattern + target outcome + novelty parameter
    • output: synthetic incident payload conforming to CTTS schema
  → SME validation pass (accept / reject / edit)
  → test_incident table with ground-truth labels
```

**Per Targeted adjustment #5:** synthesis uses **Llama 3.x** (cross-family); production inference uses **Granite Instruct**. Separate model families reduce systematic-bias coupling; P4 credibility strengthened — synthetic test set does not inherit the production model's blind spots.

- **Pattern catalog** from historical incidents — anonymised feature vectors.
- **Synthesis pipeline** on OpenShift AI Pipelines (Kubeflow) — batch; offline from per-incident path.
- **Target size:** 100–500 initial; iterative expansion per E7 test plan.
- **Ground-truth labelling:** historical outcomes + SME validation.
- **Chain-record:** `test_corpus_generation` entries for provenance.

Note: E7 owns the test plan; E3 defines the architecture surface.

---

## 8. Replay semantics for evaluation

- **Mode A — Recorded-output replay** (audit verification): fetch past recommendation + decision from chain; regenerate audit report; verify chain-integrity. Primary governance replay (FR-F.2).
- **Mode B — Live re-inference** (quality regression + CI-12 evaluation): run agent stack against test incident with current model + current SOP index; produce fresh recommendation; compare to ground-truth / past recommendation. Synthetic test corpus goes through Mode B.

Both chain-record their runs for provenance.

---

## 9. Open items for E4

| # | Item | E3 position | E4 scope |
|---|---|---|---|
| OF-4.1 | HMAC key management + rotation (T12) | Keys in OpenShift Secret | Key hierarchy; rotation cadence; revocation |
| OF-4.2 | Encryption at rest (both PG clusters + object storage + model-cache + WAL volumes) | Required; mechanism unspecified | Select mechanism; key source |
| OF-4.3 | MAS TRM control-number-level mapping | Domain-level evidence producible | Clauses → evidence mapping |
| OF-4.4 | CI-7 retention refinement under IMDA / sectoral framework | 7-year anchor | Exact retention per data class |
| OF-4.5 | Application RBAC roles + policies | Indicative | Client-approved RBAC matrix |
| OF-4.6 | CTTS service-account rotation | Stored in Secret | Rotation automation |
| OF-4.7 | SSO/SAML hardening (assertion validation depth, replay protection, TTL default) | OIDC/SAML in Review API; 8h sliding default proposed | Full hardening per client IdP posture |
| OF-4.8 | `operator_identity_map` access control + audit | Access-restricted, audit-role read | Formal policy + audit-log of admin reads |
| OF-4.9 | Chain archival immutability mechanism | Partition-seal manifest | Object-lock / WORM selection |
| OF-4.10 | Synthetic test corpus sensitivity classification | Chain-recorded generation | Classification + handling policy |
| OF-4.11 | Penetration testing + threat-modelling | Not in E3 | E4 / E7 |
| OF-4.12 | Audit-evidence packaging format for regulator | Layer-2 views exportable | Client-accepted packaging |
| OF-4.13 | WAL disk-encryption + WAL-PG agreement verifier hardening | WAL on PVC; verifier scheduled | Encryption + tamper-evidence |
| OF-4.14 | Identity-issuance RPC hardening (cross-cluster path for first-login pseudonymous-ID creation) | Privileged path named | Mechanism + threat model |

---

## 10. Requirements coverage matrix (spot-check)

| E2 requirement | E3 satisfaction |
|---|---|
| FR-A.1–5 intake (incl. malformed rejection) | §3.1 polling + FR-A.3 rejection-chain-entry |
| FR-B.1–4 agents | §2.3 per-agent; LangGraph orchestration |
| FR-C.1 structured recommendation | §2.3 Orchestrator merge composition |
| FR-D.1–6 human review | §3.3 FastAPI+HTMX UI + FR-D.6 API-level enforcement |
| FR-E.1–4 outcome recording | §3.1 write-back + §4.2 chain |
| FR-F.1–4 post-hoc audit | §4.3 version-pinning + §5.3 archival + Mode-A (§8) |
| NFR-L.1 3-min sub-budget (steady-state) | §2.4 ~95s steady-state |
| NFR-L.1 cold-start | §2.4 ~135s cold-start; keep-alive mitigation (E6) |
| NFR-A.1–4 availability | §5.1 HPA + 2× vLLM Instruct + leader-election |
| NFR-R.1 deterministic reconstruction | §2.1 state-checkpointing + §4.2 chain |
| NFR-R.3 retry with budget | §5.4 concrete numerics |
| NFR-R.4 sync chain write | §4.5 WAL-sync preserves semantics |
| NFR-AU.1–5 auditability | §4.2 chain model + §5.3 archival |
| NFR-O.1–4 observability | §5.2 Prometheus + Grafana + WAL-backlog + keep-alive metrics |
| IR-T.1–5 CTTS | §3.1 polling + idempotent write-back |
| IR-S.1–5 SOP/KB (incl. 90d deprecation) | §3.2 RAG + §4.3 version-pinning |
| IR-O.1–6 OpenShift AI + egress | §5.1 topology + §6.4 no external egress |
| GR-E.1–7 governance evidence | §4.2 chain + §6.5 integrity + GR-E.7 C2-conditioned |

---

## 11. Flags and posture declarations

### 11.1 DISCIPLINE-2 preserved

Every architecture selection cites the constraint it satisfies. No preference-based choice.

### 11.2 Governance mode: partial

Cycle-primitive discipline active on this cycle. MVGH-β Wave-1 elements activate in parallel with this delivery's E6 build phase; progressive coverage through E4+ per E2 §5.6.

### 11.3 4WRD substrate vs NOC product runtime — separate systems

4WRD runs on Claude Agent SDK (developer-side). NOC product runs on OpenShift AI. No runtime coupling. IR-O.6 restated.

### 11.4 Single-tenant declaration (per Targeted adjustment #7)

**This E3 architecture is explicitly single-tenant.** `ownership_tier` column (SEAM-5) is in place but single-valued (user-tier) for this delivery. **Multi-tenant operation is not a configuration toggle** — it requires:
- Dedicated S-cycle to evaluate tenant-isolation model (data partitioning, model-serving tenancy, identity-plane separation, chain-tenancy, SOP-corpus multi-tenancy).
- Architectural change across namespaces, PG clusters, NetworkPolicies, chain data model.
- Regulatory re-assessment (cross-tenant MAS TRM implications).

E3 does not preserve a multi-tenant activation path in this artefact; multi-tenant is a **future S-cycle + new E-cycle pair**, not a deferred-item with schema-gated activation.

### 11.5 Framework lock-in mitigation (per Targeted adjustment #6)

LangGraph chosen with explicit mitigation: `AgentInterface` contracts (§2.1) mandated as E6 requirement. Framework-swap cost bounded to wrapper-replacement, not agent-logic rewrite.

### 11.6 Cold-start discipline (per Targeted adjustment #2)

Keep-alive ping daemon is an **E6 implementation mandate**, not an optional optimisation. Absence breaches NFR-L.1 on service restart; observability includes keep-alive ping metric to detect regression.

### 11.7 Client-input dependencies still open

CI-1, CI-1a, CI-2, CI-3, CI-4, CI-6 (retention refinement), CI-8, CI-13, CI-14, CI-15, CI-16, CI-17, CI-18, CI-19, CI-20. Not blocking E3 Exact; gate E4–E9 per E2 §7.

---

## 12. E4 Security and Compliance inheritance

E4 opens with this artefact as primary input.

**E4 inherits:**
1. **Architecture as stated in §§1–8** — 4 namespaces, 2 PG clusters, Chain-Write Service WAL, Granite + vLLM, LangGraph orchestration with `AgentInterface` mitigation, FastAPI+HTMX reviewer UI, SSO/SAML with pseudonymous chain mapping.
2. **14 open items (§9 OF-4.1 through OF-4.14)** — explicit handover for hardening.
3. **Governance-tier / incident-tier split** (§4.1) — MAS TRM Access Control evidence surface.
4. **Chain data model** (§4.2) + **version-pinning mechanism** (§4.3) — for Change Management + IT Audit domains.
5. **Network isolation posture** (§6.4) — NetworkPolicies for Access Control + egress-denial evidence.
6. **Encryption-at-rest obligation** (§6.6) — E4 binds mechanisms.
7. **Key management obligation** (§6.3 / OF-4.1) — HMAC chain keys + rotation.
8. **Audit-API and Layer-2 views** — evidence-export surface for Regulator consumer.

**E4 shall produce:**
- MAS TRM control-number-level mapping to domain-level evidence (S5 §5.3 honesty bound).
- Hardened RBAC matrix (OF-4.5).
- SSO/SAML hardening and TTL defaults (OF-4.7).
- Encryption scheme (OF-4.2).
- Key lifecycle (OF-4.1).
- Retention refinement per data class (OF-4.4).
- Threat model + pen-testing plan (OF-4.11).
- Audit-evidence packaging format (OF-4.12).

---

## 13. Carry-forwards and Disciplines

**Carry-forwards (4, inherited):**
- CARRY-FWD-1 — Need 13 partial technical-constraint readiness.
- CARRY-FWD-2 — Anthropic platform concentration (4WRD substrate only; NOC product runs Granite on OpenShift AI — not triggered at product layer).
- CARRY-FWD-3 — C4 capacity binding constraint.
- CARRY-FWD-4 — MVGH-β first governed delivery; progressive governance.

**No new carry-forwards introduced at E3.**

**Disciplines (3, inherited):**
- DISCIPLINE-1 — source-of-count tagging.
- DISCIPLINE-2 — convergence-state transition preferences not expressed by AI; E3 made selections per mandate, each constraint-cited.
- DISCIPLINE-3 — qualitative classification cites criterion.

**No new disciplines introduced at E3.**

---

*End of E3 exit artefact.*
