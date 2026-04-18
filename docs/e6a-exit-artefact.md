# E6a Exit Artefact — Build (Product)

**Date:** 2026-04-18
**Convergence State:** Exact (ratified)
**Cycle:** E6a — NOC product build under
  cycle-primitive governance
**Companion cycles:** E6b governance-layer
  wiring (opens after MVGH-β Wave 1 substrate
  live); E7 Test opens with this artefact
  as primary input; E8 Deployment opens when
  client OpenShift AI environment is accessible.
**Governance mode:** Partial governance —
  cycle-primitive discipline (DSC rows in
  §1 mapping carry PAR status until MVGH-β
  substrate is live; see E4 §1).
**Primary derivation inputs:**
  - docs/e6-cycle-1-verification.md (Docker
    Compose environment constraint)
  - docs/e5-exit-artefact.md (data model
    authoritative)
  - docs/e4-exit-artefact.md (security/
    compliance authoritative)
  - docs/e3-exit-artefact.md (architecture
    authoritative)
  - docs/e2-exit-artefact.md (FR/NFR/CI
    authoritative)

---

## 0. Scope and E6a/E6b split

E6a produces the NOC product (retrieval,
agent orchestration, Reviewer UI, intake,
SOP ingestion, write-back path, chain-write
integration hooks, observability, tests).
The product is built and tested locally on
a Docker Compose environment because the
client OpenShift AI environment is not
currently accessible.

E6b wires the governance substrate: it
swaps the Chain-Write stub body for the
MVGH-β-backed implementation, activates
the chain archival pipeline, and flips DSC
rows from PAR to active status. E6b opens
when MVGH-β Wave 1 substrate is live. E6a
delivers the product unchanged in interface
terms; E6b touches only the inside of
stable interface seams.

E8 deploys the E6a-built, E6b-wired product
to the client's OpenShift AI environment.
E8 scope contains all OpenShift-specific
configuration (Operators, Custom Resources,
Routes, platform RBAC, namespace manifests,
NetworkPolicy CRs, ArgoCD/GitOps wiring).

Out of E6a scope: OpenShift Operator
lifecycle, production GPU tuning, client
SSO federation, production Vault HA, Ceph
tuning, production CloudNativePG HA — all
deferred to E8.

---

## 1. Build plan — layers and milestones

### 1.1 Layer summary (revised for Docker Compose)

| L | Layer                               | Environment | Notes |
|---|-------------------------------------|-------------|-------|
| 0 | Dev platform prerequisites          | Docker Compose | Replaces OpenShift AI for E6a dev. See §7. |
| 1 | Data substrate                      | 2× Postgres + pgvector containers + MinIO + Vault-dev | See §3 |
| 2 | Chain-Write stub + allowlist        | Python service container | See §3.7 |
| 3 | Identity and RBAC scaffolding       | Dex OIDC + FastAPI middleware | See §3.11 |
| 4 | SOP ingestion pipeline              | Python workers + pgvector | See §3.1, §3.2 |
| 5 | Agent orchestrator (LangGraph)      | Python service + vLLM CPU | See §3.8, §3.9 |
| 6 | Reviewer UI (FastAPI + HTMX)        | Single Python stack | See §3.10 |
| 7 | Intake adapter (Kafka or file-drop) | Python worker + pydantic | See §3.12 |
| 8 | Write-back path (simulated CTTS)    | Python worker + staged approval | See §3.13 |
| 9 | Observability (Prometheus, Grafana) | Containers + OTEL SDK | See §3.14 |
| 10| Test harness                        | pytest + hypothesis + testcontainers | See §5 |

### 1.2 Milestones

| M  | Deliverable                                                       | Layers | Risk-weight |
|----|-------------------------------------------------------------------|--------|-------------|
| M0 | Docker Compose env up; smoke health on all containers             | 0      | Low          |
| M1 | Two Postgres clusters provisioned; schemas from E5 §1 materialised; pgvector extension verified | 1 | Med |
| M2 | Chain-Write stub emits to `governance_chain` per E5 §1.11 append-only trigger; entry_type allowlist loaded | 2 | Med |
| M3 | SOP ingestion: PDF→chunk→embedding→write path green for synthetic corpus from E5 §4 | 4 | High (retrieval quality gate) |
| M4 | Agent orchestrator: analyst→recommender chain returns structured recommendation for one seeded incident | 5 | High |
| M5 | Reviewer UI: render pending recommendation + SOP citations + accept/edit/reject flow | 6 | Med |
| M6 | Intake adapter: batched synthetic incident feed lands in `incident` table | 7 | Low |
| M7 | Write-back path: simulated CTTS submission records chain entry per E5 §2.5 | 8 | Med |
| M8 | Observability: Prometheus scrape green for all services; Grafana dashboard for p50/p95 per NFR-L.1 | 9 | Low |
| M9 | Unit + integration tests passing on CI (GitHub Actions); coverage baseline locked | 10 | Med |
| M10| Adversarial harness exercising OWASP LLM Top 10 (LLM01/02/06/08/09) per E4 §6 | 10 | High (safety gate) |
| M11| Benchmark suite: 5-min envelope from intake to recommendation on synthetic corpus reproducible | 10, 5 | High (NFR-L.1 gate) |

Risk-weighted ordering: M3, M4, M10, M11
carry the highest delivery risk (retrieval
quality, LLM behaviour, latency envelope,
adversarial safety). Ordering front-loads
M1–M3 so that retrieval fidelity can be
iterated against before downstream layers
compound error.

### 1.3 Explicit non-goals for E6a

- Multi-tenancy (E3 §11.4 declares single-tenant).
- Production GPU tuning (E8).
- OpenShift RBAC mapping (E8; dev uses Dex).
- Production Vault HA and seal/unseal
  procedures (E8; dev uses Vault dev mode).
- CloudNativePG operator and backup
  orchestration (E8; dev uses bare
  Postgres containers + pgbasebackup target
  volume for local PITR rehearsal only).
- Real Ceph/S3 provisioning (E8; dev uses
  MinIO with S3-compatible API).
- External egress hardening — no external
  egress is required in dev either, so the
  control surface is equivalent (IR-O.4).

---

## 2. E6-owned binding decisions (ratified)

These seven bindings were enumerated in the
E6 opening prompt as decisions E6 owns rather
than inherits. They are now fixed for E6a.

### 2.1 PDF parser

**Decision:** `unstructured[pdf]` as primary
extractor; `pdfminer.six` fallback for pages
where unstructured returns empty; `tesseract`
(via `pytesseract`) for OCR of image-only
pages detected by page-has-no-text heuristic.

**Rationale:** Python-native (no JVM — rejects
Apache Tika), keeps single-Python-stack
discipline from E3 §5.2. Unstructured handles
layout-aware chunk boundaries for SOP
documents which typically contain tables,
numbered steps, and callouts. pdfminer
fallback covers unstructured's known gaps on
older PDFs. Tesseract is the minimum viable
OCR path for scanned SOPs; OF-6.14 tracks
dependency trim if Unstructured pulls too
much transitively.

**Interface:** `services/sop_ingest/parser.py`
exports `parse_pdf(path) -> list[RawChunk]`.
Parser choice is hidden behind this function;
E6 can swap later without touching downstream.

### 2.2 HNSW index tuning and distance metric

**Decision:**
- Extension: `pgvector` (pinned to ≥0.7.0).
- Index: HNSW.
- `M = 16`, `ef_construction = 128`,
  `ef_search = 64` (session-set for queries).
- Distance operator: cosine
  (`vector_cosine_ops`).
- Vector dimension: **768** (aligned to
  Granite Embedding base; OF-6.2 captures
  final model-card confirmation at E7).

**Rationale:** HNSW gives the recall/latency
envelope required by NFR-L.1 retrieval
sub-budget. M=16 and ef_construction=128 are
the pgvector community-recommended balance
for corpora in the 10³–10⁶ vector range.
ef_search=64 is tuned for p95 retrieval under
the 5-minute overall envelope; session-set
so that Reviewer UI "show more" queries can
raise it without re-indexing. Cosine matches
the Granite Embedding normalisation contract.

**Configuration:** `db/migrations/0040_hnsw.sql`.

### 2.3 Partition manager

**Decision:** `pg_partman` v5, `native`
partitioning mode, `partition_interval = 1 month`,
`retention = NULL` at the partman level
(retention is policy-driven per E4 §7;
partman does not drop). Pre-creates 3 future
partitions via `run_maintenance_proc()` on
daily schedule.

**Rationale:** E5 §1 declares monthly partitions
for `incident`, `recommendation`,
`governance_chain`, `audit_event`,
`sop_chunk_embedding`. Using pg_partman
(rather than hand-rolled DDL) removes a class
of "partition-not-pre-created" outages. Policy
retention stays explicit in SQL rather than
being delegated to the partition manager, so
DSC evidence stays legible.

**Configuration:** `db/extensions/pg_partman.sql`;
parent tables declared in migrations 0010–0035
per E5 §1.

### 2.4 Secret-pattern register

**Decision:** Seed from `gitleaks` default rules
(MIT licence) + `detect-secrets` default
plugins. Materialised to
`services/secret_scanner/patterns.yaml` as a
pinned copy. Pattern engine uses `regex`
(Python) with recompilation guard; false-
positive calibration items logged against
OF-6.15 during E7.

**Rationale:** Two sources reduce pattern
coverage gaps (gitleaks is stronger on cloud
secrets; detect-secrets has a wider pluggable
entropy detector). Pinning the pattern file
removes non-determinism from CI. The scanner
runs on (a) SOP ingestion inputs and
(b) recommendation outputs before Reviewer
presentation — per E4 §6 LLM06 mitigation.

**Integration:** `services/secret_scanner/scan.py`
exports `scan(text) -> ScanResult` with
severity levels. Recommender pipeline calls
this before persisting `recommendation.body`.
A non-zero severity hit marks the
recommendation `requires_supervisor_review`
per E5 §1 `recommendation` schema.

### 2.5 Entry_type allowlist

**Decision:** `services/chain_write/allowlist.yaml`
enumerates the 23 entry_type values declared
in E5 §1.11. Chain-Write stub validates every
emit against this file at service start
(fail-fast on unknown entry_type) and per
call (defence-in-depth). The trigger on
`governance_chain` enforces the same
constraint at the DB layer.

**Rationale:** E4 §6 LLM08 (excessive agency)
is mitigated in part by bounding what an
agent-produced chain entry can claim. The
allowlist is the seam; adding a new
entry_type requires a migration and an
explicit allowlist edit, both reviewable.

### 2.6 Canonical JSON for HMAC payload

**Decision:**
```python
canonical = json.dumps(
    payload,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
).encode("utf-8")
```
Defined once at
`services/chain_write/canonical.py::canonicalise`.
All HMAC inputs route through this function.

**Rationale:** Deterministic byte encoding is
a precondition for chain verification. Key
choices: `sort_keys=True` removes
dict-ordering drift across Python versions;
`separators=(",",":")` removes whitespace
drift; `ensure_ascii=False` preserves
Unicode in SOP-derived payloads without
double-encoding (MAS TRM clause map includes
CJK-safe language handling as OF-4.x-adjacent
concern). UTF-8 is the byte form.

**Test:** `tests/chain_write/test_canonical.py`
pins golden vectors for re-order,
whitespace, and Unicode cases. Any future
change to this function is a chain-forking
change and must be accompanied by a
migration plan — flagged as OF-6.6.

### 2.7 Chain-Write stub interface

**Decision:** `services/chain_write/writer.py`
exposes:

```python
class ChainWriter:
    def emit(
        self,
        entry_type: str,
        actor_id: str,
        actor_role: str,
        incident_id: UUID | None,
        payload_ref: dict,
        sop_versions_pinned: list[dict] | None = None,
        class_enum: Literal["NORMAL","OVERRIDE"] = "NORMAL",
    ) -> ChainEmitResult: ...
```

The stub body performs local-WAL write +
async PG commit per E3 §4.5, with HMAC
computed using a Vault-dev-backed KEK. E6b
replaces the body only; the signature and
return type are frozen by E6a for E7 test
authoring stability.

---

## 3. Component specifications

### 3.1 SOP ingestion pipeline

`services/sop_ingest/` contains:
- `parser.py` — §2.1 above
- `chunker.py` — chunk by section heading
  with 512-token target and 64-token overlap;
  preserves `section_path` for citation
- `embedder.py` — batched calls to Granite
  Embedding via vLLM; retries per E3 §5.4
- `writer.py` — writes to `sop_chunk` and
  `sop_chunk_embedding` in noc-data; emits
  chain entries of type `sop_ingest` per E5
  §1.11 via ChainWriter.emit
- `lifecycle.py` — honours
  `sop_chunk.lifecycle_state` values from E5
  §1 Targeted absorption #2 (pending_review,
  active, deprecation_window, archived)

### 3.2 Retrieval service

`services/retrieval/` contains:
- `query.py` — embedding of query,
  top-k ANN search with HNSW (§2.2), post-
  filter for `lifecycle_state='active'`,
  re-rank via Granite Instruct if top-k
  cosine scores below threshold
- Returns `RetrievalResult` with
  `(sop_chunk_id, sop_version_id,
  section_path, score)` tuples that the
  agent orchestrator pins into
  `sop_versions_pinned` on the produced
  recommendation

### 3.3 Data substrate (local)

Two Postgres 16 containers — `noc-data` and
`noc-gov` — each with pgvector and
pg_partman extensions. Schemas from E5 §1
applied via Alembic migrations under
`db/migrations/`. MinIO container exposes
an S3-compatible endpoint for archive
writes; archive bucket is created but
Object Lock Compliance mode is **E8 scope**
(MinIO supports it; E6a leaves
`object_lock_enabled=false` in dev to keep
test cycles fast — OF-6.7 tracks the E8
flip). Cross-cluster reconcile worker from
E5 §1.18 runs as a separate container.

### 3.4 Chain-Write stub

Described in §2.5–2.7. Runs as
`services/chain_write/` container. Local
WAL is a bind-mounted volume to survive
container restarts. Async PG commit target
is noc-gov.

### 3.5 Agent orchestration

`services/agents/` contains:
- `orchestrator.py` — LangGraph DAG with
  Analyst node, Recommender node, Safety
  node (OWASP LLM01/02 checks), Emit node
- `prompts/` — prompts versioned under git;
  prompt_id + version recorded on every
  agent step chain entry
- `safety/` — input scrubber (prompt
  injection patterns per E4 §6 LLM01) and
  output validator (schema validation +
  secret scanner §2.4)
- `state.py` — LangGraph state type that
  includes `citation_required: bool=True`
  so that Recommender node rejects any
  recommendation not backed by
  `sop_chunk_id` references (LLM09
  overreliance mitigation)

### 3.6 vLLM inference (dev)

CPU-only vLLM container in Docker Compose
using `granite-3.1-8b-instruct` at reduced
context for dev OR `ollama` with a
Granite-compatible quantised model if vLLM
CPU performance is insufficient for
iterative work. Inference latency in dev is
not NFR-L.1-binding — the 5-minute envelope
is validated at E8 on GPU hardware. Dev
benchmarks report CPU numbers with a
"dev-only" tag to keep client expectations
clear. OF-6.9 tracks the Ollama fallback
decision gate.

### 3.7 Reviewer UI

`services/reviewer_ui/` — FastAPI +
Jinja2 templates + HTMX fragments + htmx-ext
server-sent events for long-running agent
runs. Single Python process. Templates
render `recommendation.body` with citation
chips linking to `sop_chunk.section_path`
per FR-D.2. Accept/Edit/Reject actions
correspond to E5 §2.4 transitions and each
emit a chain entry via ChainWriter.

### 3.8 Identity and RBAC

Dex container serves OIDC in dev. FastAPI
middleware (`services/common/auth.py`)
validates id_tokens from Dex and maps
claim `role` to the 5-role RBAC from E4 §5.
Two-role gates (auditor + admin for bulk
reads of `operator_identity_map` per E4
§4 OF-4.8) are enforced in middleware,
tested by the adversarial harness. OF-6.17
tracks middleware path-gating hardening
(raised by adversarial challenge on the
Explorative pass).

### 3.9 Intake adapter

`services/intake/` consumes either a Kafka
topic (if a local Kafka is brought up in
Docker Compose) or a file-drop directory
(default dev mode). Pydantic model
`IncidentIn` validates payload shape and
writes to `incident` table. Intake-to-
orchestrator recovery sweep runs every N
seconds to pick up incidents where
orchestrator never acknowledged — closes
OF-6.16.

### 3.10 Write-back (simulated CTTS)

`services/write_back/` — staged approval
queue. On supervisor accept in Reviewer UI,
the accepted recommendation lands in the
queue; a simulated CTTS client logs the
intended call and emits a chain entry of
type `cts_submit` per E5 §1.11. Real CTTS
integration is an E8 concern (client
credentials, endpoint, service-account
rotation per OF-4.6).

### 3.11 Observability

Prometheus, Grafana, OTEL collector, Loki
for logs — standard container set. Python
services use OTEL SDK auto-instrumentation
+ manual spans around retrieval, agent
steps, and chain-write calls. Dashboards
ship as JSON under `deploy/observability/`
— dashboards are dev/prod-neutral; only the
Grafana data-source URLs differ, which the
E8 overlay supplies.

---

## 4. OF-5.x resolution

E5 §7 carried 19 OF items. E6a resolves
13 at implementation; 6 defer to E6b, E7,
or E8.

| OF | Title | E6a treatment |
|----|------|----------------|
| OF-5.1  | PDF parser library selection | **Resolved** — §2.1 |
| OF-5.2  | HNSW tuning values | **Resolved** — §2.2 |
| OF-5.3  | Distance metric + embedding dim | **Resolved** — §2.2 |
| OF-5.4  | Partition manager tool | **Resolved** — §2.3 |
| OF-5.5  | Secret-pattern register seed | **Resolved** — §2.4 |
| OF-5.6  | Entry_type allowlist location | **Resolved** — §2.5 |
| OF-5.7  | Canonical JSON spec | **Resolved** — §2.6 |
| OF-5.8  | ChainWriter interface shape | **Resolved** — §2.7 |
| OF-5.9  | sop_chunk lifecycle_state enum | **Resolved** — materialised from E5 §1 T#2 |
| OF-5.10 | recommendation.production_seq semantics | **Resolved** — schema + orchestrator obey E5 §1 T#1 |
| OF-5.11 | content_hash canonicalisation | **Resolved** — §2.6 shared with HMAC |
| OF-5.12 | Cross-cluster FK reconcile worker | **Resolved** — §3.3 |
| OF-5.13 | Append-only trigger on governance_chain | **Resolved** — migration in 0050 |
| OF-5.14 | Archive bucket Object Lock flip | **Deferred to E8** — OF-6.7 |
| OF-5.15 | Chain archival pipeline | **Deferred to E6b** |
| OF-5.16 | Synthetic corpus retention review on CI-7 | **Deferred to E7** — ties to MAS TRM retention clauses, E7 test plan will exercise |
| OF-5.17 | IMDA sectoral retention refinement | **Deferred to E8** — client legal sign-off gate from E4 T#8 |
| OF-5.18 | Cross-version content_hash migration plan | **Deferred to E6b** — OF-6.6 |
| OF-5.19 | Intake dedup window calibration | **Deferred to E7** — adversarial harness will surface data |

---

## 5. Test strategy

### 5.1 Unit

pytest across every service module. Focus
on parser boundary cases, chunker
deterministic output on canonical inputs,
canonical JSON golden vectors, ChainWriter
emit validation, allowlist fail-fast,
secret scanner true-positive set.

### 5.2 Integration

testcontainers (Python) brings up Postgres,
MinIO, Vault-dev, Dex, vLLM CPU, services.
Tests exercise: SOP ingest end-to-end for
the synthetic corpus from E5 §4; incident
intake → orchestrator → recommendation →
reviewer accept → write-back; chain
verification walk on
`prev_chain_id` linkage per E4 §3.

### 5.3 Adversarial

`tests/adversarial/` maps directly to E4
§6 OWASP LLM Top 10 supplement:
- `test_llm01_prompt_injection.py` —
  injection attempts through SOP content,
  through intake payload, through
  Reviewer edit comments
- `test_llm02_insecure_output.py` — HTML
  injection in recommendation body
  rendering
- `test_llm06_sensitive_info.py` — secret
  scanner coverage against a fixture of
  leaked-credential patterns
- `test_llm08_excessive_agency.py` —
  attempt to emit chain entries with
  disallowed `entry_type`; attempt to
  bypass FR-D.6 human-review gate by
  direct CTTS call path (must fail —
  write-back is structurally gated)
- `test_llm09_overreliance.py` —
  recommendation without citation must be
  blocked by §3.5 state rule

### 5.4 Benchmark

`tests/benchmarks/` measures retrieval p95,
agent-step latency, end-to-end intake-to-
recommendation envelope. CPU numbers are
reported with `dev-only` tag; thresholds
log as warnings not failures in dev.
Thresholds become hard gates at E8 on GPU.
Two-role gate tests exercise the middleware
(per §3.8).

### 5.5 Chain-verification

`tests/chain/test_linkage.py` walks
`governance_chain` by `prev_chain_id` and
verifies HMAC per entry. Run after every
integration test; run as a dedicated
nightly job in CI.

---

## 6. E6b handoff surface (CWP — chain-write points)

E6b rewrites only the inside of ChainWriter.
E6a commits to 16 integration points that
must each already be calling
`ChainWriter.emit`. E6b's job is to make
the emit durable against MVGH-β.

| CWP | Point                                                      | Call site                                | entry_type           |
|-----|------------------------------------------------------------|------------------------------------------|----------------------|
| CWP-1  | Incident created                                        | `services/intake/write.py`               | `incident_created`   |
| CWP-2  | Orchestrator run started                                | `services/agents/orchestrator.py`        | `agent_run_start`    |
| CWP-3  | Analyst step completed                                  | orchestrator analyst node                | `analyst_step`       |
| CWP-4  | Retrieval executed                                      | `services/retrieval/query.py`            | `retrieval`          |
| CWP-5  | Recommender step completed                              | orchestrator recommender node            | `recommender_step`   |
| CWP-6  | Safety gate outcome                                     | orchestrator safety node                 | `safety_check`       |
| CWP-7  | Recommendation produced                                 | orchestrator emit node                   | `recommendation_produced` |
| CWP-8  | Reviewer opened recommendation                          | `services/reviewer_ui/routes.py`         | `review_opened`      |
| CWP-9  | Reviewer accepted                                       | reviewer action handler                  | `review_accept`      |
| CWP-10 | Reviewer edited                                         | reviewer action handler                  | `review_edit`        |
| CWP-11 | Reviewer rejected                                       | reviewer action handler                  | `review_reject`      |
| CWP-12 | CTTS submission (simulated in E6a)                      | `services/write_back/submit.py`          | `cts_submit`         |
| CWP-13 | SOP ingested (version promoted to active)               | `services/sop_ingest/lifecycle.py`       | `sop_activated`      |
| CWP-14 | SOP deprecated                                          | lifecycle worker                          | `sop_deprecated`     |
| CWP-15 | KEK rotated (dev-only event in E6a; real in E6b)        | Vault webhook handler                    | `kek_rotated`        |
| CWP-16 | Two-role-gated bulk read                                | `services/common/auth.py` middleware     | `operator_identity_read_bulk` |

Each CWP site has a targeted integration
test asserting that ChainWriter.emit was
called with the right `entry_type`. E7 runs
those tests; E6b doesn't need to add new
call sites.

---

## 7. Docker Compose environment (Layer 0 revised)

Replaces OpenShift AI prerequisites for E6a
dev. Target file:
`dev/docker-compose.yaml`.

### 7.1 Services

| Service         | Image                            | Port    | Purpose                         |
|-----------------|----------------------------------|---------|---------------------------------|
| noc-data        | postgres:16 + pgvector + partman | 5433    | Incident-tier DB                |
| noc-gov         | postgres:16 + partman            | 5434    | Governance-tier DB              |
| minio           | minio/minio                      | 9000/9001 | S3-compatible archive        |
| vault-dev       | hashicorp/vault:latest (dev mode)| 8200    | KEK storage (dev root token)    |
| dex             | ghcr.io/dexidp/dex               | 5556    | Mock OIDC provider              |
| vllm            | vllm-cpu (custom image)          | 8000    | CPU inference (Granite)         |
| chain-write     | local build                      | 7001    | Chain-Write stub service        |
| sop-ingest      | local build                      | —       | Worker (no port)                |
| agents          | local build                      | 7002    | LangGraph orchestrator          |
| reviewer-ui     | local build                      | 8080    | FastAPI + HTMX                  |
| intake          | local build                      | 7003    | File-drop or Kafka consumer     |
| write-back      | local build                      | 7004    | Simulated CTTS                  |
| prometheus      | prom/prometheus                  | 9090    | Metrics                         |
| grafana         | grafana/grafana                  | 3000    | Dashboards                      |
| otel-collector  | otel/opentelemetry-collector     | 4317    | Traces                          |
| loki            | grafana/loki                     | 3100    | Logs                            |

Optional (off by default):
- kafka (bitnami/kafka) — intake upgrade path
- zookeeper (bitnami/zookeeper) — if kafka enabled

### 7.2 Networks

Three Docker networks approximate the E3
§5.1 namespace split:
- `noc-data-net` — noc-data + sop-ingest +
  agents + retrieval + reviewer-ui +
  intake + write-back
- `noc-gov-net` — noc-gov + chain-write +
  vault-dev + minio
- `noc-obs-net` — prometheus + grafana +
  otel-collector + loki (services join this
  net in addition to their tier net)

No container joins both noc-data-net and
noc-gov-net directly except chain-write
(to reach noc-gov) and the cross-cluster
reconcile worker (read-only on both). This
mirrors the E3 NetworkPolicy intent. The
mapping to real NetworkPolicy CRs lives in
E8.

### 7.3 Volumes

Named Docker volumes for Postgres data
(two), MinIO data, Vault file backend
(dev), chain-write local WAL, and Grafana
state. All under `dev/volumes/` via bind
where developer persistence is useful.

### 7.4 Dev secret bootstrap

`dev/bootstrap.sh` does:
1. Wait for Vault-dev ready
2. Write dev KEK under
   `secret/noc-gov/kek/current`
3. Create Dex OIDC client + seed 5 test
   users (one per RBAC role)
4. Create MinIO buckets: `noc-archive`,
   `noc-staging` (matches OF-4.9 staging
   bucket pattern from E4; staging ↔
   locked flip itself is deferred to E8)
5. Apply Alembic migrations to both
   Postgres clusters
6. Load entry_type allowlist into
   chain-write container

This script is **dev-only**. The
equivalent for E8 is a GitOps-driven
sealed-secret + Vault HA bootstrap, which
lives under `deploy/`.

### 7.5 GPU handling

vLLM container is pinned to CPU build in
dev; no CUDA runtime assumed. The vLLM
image tag is parameterised via
`VLLM_IMAGE` environment variable so E8
can override with a CUDA image without a
code change. OF-6.9 tracks the Ollama
fallback gate if vLLM CPU throughput is
insufficient for M11 iteration loops.

---

## 8. Deployment strategy: dev vs E8

### 8.1 Repo layout

```
/                          — application code
  services/                — Python services (§3)
  db/migrations/           — Alembic
  tests/                   — pytest tree (§5)
  dev/                     — Docker Compose env
    docker-compose.yaml
    bootstrap.sh
    volumes/
  deploy/                  — E8 ONLY — unbuilt in E6a
    openshift/
      operators/           — CNPG, pgvector, etc.
      customresources/     — PostgresCluster, etc.
      routes/              — Ingress/Route manifests
      networkpolicies/     — real NP CRs
      rbac/                — ClusterRoles, RoleBindings
      argocd/              — ApplicationSets
    observability/         — Grafana dashboards (dev/prod neutral)
```

### 8.2 What's unbuilt in E6a but scaffolded

`deploy/` exists with READMEs and stub
manifests where needed to capture design
intent — but nothing under `deploy/` is
built, linted, or tested in E6a CI. That
is explicit: E8 owns its own CI gate and
lint pass (ArgoCD/kustomize validation).

### 8.3 E8 responsibility list (not E6a)

- All OpenShift CRs and Operator wiring
- Real Vault HA + auto-unseal
- Real CNPG cluster with backups
- Ceph/S3 provisioning + Object Lock
  Compliance flip (closes OF-5.14,
  OF-6.7)
- Production NetworkPolicy mapping
- SSO federation to client IdP
- GPU node selector + tolerations for
  vLLM deployment
- Image signing + admission policy
- GitOps promotion pipeline

---

## 9. Open items for E7

Thirteen items carried forward from E6a
for E7 Test and beyond.

| OF     | Title                                              | Owner / target cycle |
|--------|----------------------------------------------------|----------------------|
| OF-6.1 | Benchmark thresholds (CPU dev vs GPU E8)           | E7; hardens at E8    |
| OF-6.2 | Granite Embedding model-card confirmation of dim=768 | E7 |
| OF-6.3 | Prompt-version frozen set for M10 adversarial pass | E7 |
| OF-6.4 | Retrieval recall@k on synthetic corpus + threshold | E7 |
| OF-6.5 | Reviewer UI accessibility baseline (WCAG AA)       | E7 |
| OF-6.6 | Canonical JSON migration plan for any future change| E6b                  |
| OF-6.7 | Object Lock Compliance flip on archive bucket      | E8                   |
| OF-6.8 | Chain archival pipeline cutover                    | E6b                  |
| OF-6.9 | vLLM CPU vs Ollama fallback decision gate          | E7                   |
| OF-6.10| Cross-cluster reconcile worker SLO                 | E7                   |
| OF-6.11| Observability red-line alerts set                  | E7                   |
| OF-6.12| CI matrix (Python versions, pg versions)           | E7                   |
| OF-6.13| Stub-ID namespace for dev-only chain entries       | E6b                  |
| OF-6.14| Unstructured dependency trim                       | E7                   |
| OF-6.15| Secret-pattern false-positive calibration          | E7                   |
| OF-6.16| Intake-to-orchestrator recovery sweep interval     | E7                   |
| OF-6.17| Middleware path-gating hardening                   | E7                   |
| OF-6.18| FR-D.4 re-present integration test                 | E7                   |

---

## 10. Traceability

### 10.1 To E2 FR/NFR/CI

- FR-A (intake): §3.9
- FR-B (analysis): §3.5 Analyst node
- FR-C (recommendation): §3.5 Recommender
  node + §3.7 Reviewer render
- FR-D (review): §3.7, §5.3 LLM09
- FR-D.4 (re-present): OF-6.18 + §3.7
- FR-D.6 (human-review gate): §3.10
  structurally gated; §5.3 LLM08 verifies
- FR-E (write-back): §3.10
- FR-F (SOP ingestion): §3.1, §3.2, §3.3
- NFR-L.1 (5-min envelope): M11, §5.4;
  dev = CPU reported, hardens at E8
- CI-1..CI-20: resolved where applicable
  in E2/E3/E4/E5; residuals carry forward
  in OF-5/OF-6 series

### 10.2 To E3 architecture

- Two-cluster posture: §3.3, §7.1, §7.2
- Chain-Write WAL semantics: §3.4, §2.7
- Single Python stack: §§2.1, 3.7
- NetworkPolicy default-deny: §7.2 (dev
  proxy), E8 for prod
- IR-O.4 no external egress: §0 non-goals
  note

### 10.3 To E4 security/compliance

- MAS TRM mapping: inherited; DSC rows
  remain PAR in E6a (partial governance)
- OWASP LLM Top 10: §5.3 adversarial
  tests map 1:1 to LLM01/02/06/08/09
- KEK hierarchy: §3.4 chain-write uses
  Vault-dev-backed KEK (root → KEK →
  per-entry HMAC); real root in Vault HA
  at E8
- Two-role gate: §3.8, CWP-16
- Retention: enforced via pg_partman +
  policy SQL per E4 §7; retention flip on
  client legal sign-off (OF-4.4 / OF-5.17)
  is E8
- Staging bucket OF-4.9: §7.4 MinIO
  bucket created; flip is E8

### 10.4 To E5 data model

- All schemas in E5 §1 materialised as
  Alembic migrations 0010–0050
- E5 §1.11 append-only trigger on
  governance_chain: migration 0050
- E5 §1.17 content_hash canonicalisation:
  §2.6 (shared canonical function with
  HMAC)
- E5 §1.18 cross-cluster reconcile
  worker: §3.3
- E5 §2.5 write-back chain entry:
  CWP-12
- E5 §4 synthetic corpus: M3 ingestion
  fixture

---

## 11. Absorbed verification adjustments

The E6 cycle-1 verification file
(`docs/e6-cycle-1-verification.md`)
records a single high-level decision:
replace the OpenShift AI-dependent Layer 0
with Docker Compose for E6a development;
defer OpenShift-specific concerns to E8.
The E6a Targeted direction message
enumerated seven concrete implementation
adjustments stemming from that decision.
All seven are absorbed as follows.

1. **Layer 0 environment swap** —
   OpenShift AI platform prerequisites
   replaced by Docker Compose (§1.1, §7).

2. **Inference path swap** — GPU-backed
   vLLM on OpenShift AI → CPU-only vLLM
   (with Ollama fallback per OF-6.9) in
   Docker Compose for dev; GPU validated
   at E8 on client hardware (§3.6, §7.5).

3. **Storage substrate swap** — Ceph /
   client S3 → MinIO in Docker Compose
   for S3-compatible archive; Object Lock
   flip remains E8 (§3.3, §7.1, §7.4).

4. **Secrets substrate swap** — Vault HA
   → Vault dev mode in Docker Compose;
   real root key management is E8 (§3.4,
   §7.1, §7.4).

5. **Database substrate swap** —
   CloudNativePG on OpenShift → two bare
   Postgres 16 containers (incident-tier,
   governance-tier) with pgvector +
   pg_partman; operator lifecycle is E8
   (§3.3, §7.1, §1.3 non-goals).

6. **Identity substrate swap** — client
   SSO/SAML → Dex mock OIDC provider in
   Docker Compose; federation to client
   IdP is E8 (§3.8, §7.1, §7.4).

7. **Isolation substrate swap** —
   OpenShift NetworkPolicy CRs → Docker
   Compose network segmentation (three
   networks mirroring the E3 namespace
   split); real NetworkPolicy manifests
   live in `deploy/openshift/networkpolicies/`
   and are unbuilt in E6a (§7.2, §8.1,
   §8.3).

Cross-cutting consequence: everything
OpenShift-specific is isolated under
`deploy/` and is explicitly E8 scope.
E6a CI does not build, lint, or validate
`deploy/` contents.

---

## 12. Convergence statement

E6a advances to Exact.

All E6-owned bindings are resolved (§2,
seven decisions). The build plan is
actionable (§1, M0–M11). Every chain-
write integration point required by E6b
is named and pinned to a call site (§6,
CWP-1..16). Test strategy covers unit,
integration, adversarial (mapped to E4
§6 LLM Top 10), benchmark, and chain
verification (§5). The dev/prod split
is disciplined: OpenShift-specific
concerns are isolated under `deploy/`
and unbuilt in E6a (§8).

E7 Test opens with this artefact as
primary input. MVGH-β Wave 1 substrate
setup continues as a parallel workstream;
E6b opens when that substrate is live and
swaps the body of `ChainWriter.emit`
without touching any call site. E8
Deployment opens when the client
OpenShift AI environment is accessible
and promotes the E6a-built, E6b-wired
product to production.

---

**Exit-artefact status:** Ratified.
