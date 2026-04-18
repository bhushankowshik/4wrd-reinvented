# E2 — Requirements — Exit Artefact

## 0. Status and derivation

**Convergence state at exit:** Exact. Ratified.
**Primary derivation intent:** docs/e1-exit-artefact.md; docs/e2-knowledge-contribution.md; docs/s6-solution-brief.md.
**Contributing cycles:** E2.1 Explorative (first-pass requirements across 6 deliverables + governance-increment approach); E2 Targeted → Exact (11 adjustments absorbed; governance-increment quantified per-item with named missing inputs).

**Governance mode at this cycle:** **Partial governance.** Cycle primitives active on this cycle; full-harness infrastructure activates progressively as MVGH-β setup completes (per CARRY-FWD-4; see §5.6 progressive-governance framing).

## 1. Scope of this artefact

**In scope for E2:** functional + non-functional + integration + governance requirements; role-compression mapping instantiation; client-input open questions; **governance-increment quantification produced** (§8).

**Out of scope (E3 mandate; E4/E8 for others — flagged inline where requirements imply a choice):**
- Agent orchestration framework (LangGraph / LlamaIndex / OpenShift AI Pipelines / other) — **E3-owned**.
- Self-hosted model selection (Llama / Mistral / Granite / IBM-supported) — **E3-owned**.
- Retrieval pattern for SOP corpus (RAG / vector / keyword / hybrid) — **E3-owned within CI-10 constraints**.
- Correlation-search architecture (index / vector / graph) — **E3-owned**.
- Reviewer-UI host (separate app / ticketing-inline / dashboard) — **E3-owned, gated on CI-11**.
- OpenShift AI deployment topology (operators, pipelines, pod composition) — **E3 / E8-owned**.

Per DISCIPLINE-2, every requirement below that implies an architectural choice is stated as *requirement + flagged E3 choice*.

---

## 2. Functional requirements

Structured by **workflow stage × actor × agent role**. Grounded in the 4-agent decomposition from E1 §1.5.

### 2.1 Workflow stages

- **Stage A — Ticket intake.** Incident ticket becomes available.
- **Stage B — Analysis.** Diagnosis, Correlation, SOP agents analyse under Orchestrator coordination.
- **Stage C — Recommendation production.** Orchestrator composes structured recommendation.
- **Stage D — Human review gate.** NOC operator approves / rejects / overrides / times-out / handles system-unavailable.
- **Stage E — Outcome recording.** Human decision written back to ticketing system + governance chain.
- **Stage F — Post-hoc audit.** SOP-version reconstruction, test-incident-set evaluation, MAS TRM evidence extraction.

### 2.2 Actors

Incident (ticket); NOC operator (human reviewer); Agent Orchestrator (product); Diagnosis Agent; Ticket Correlation Agent; SOP Agent; Ticketing system; SOP/KB corpus.

### 2.3 Stage A — Ticket intake (FR-A)

- **FR-A.1** The system shall receive incident tickets from the ticketing system on trigger (push vs pull flagged **E3-owned**).
- **FR-A.2** The system shall parse the incident payload to named structural fields (incident ID, timestamp, reporting source, affected nodes / service elements, symptom description, severity, attached correlation hints). Field inventory bound to client ticketing schema — **CI-9**.
- **FR-A.3** The system shall validate intake payload against a declared schema and reject malformed tickets with explicit rejection record (not silent drop).
- **FR-A.4** The system shall stamp each accepted incident with a governance record marker: incident ID + arrival time + system version + SOP corpus version pinned at this moment.
- **FR-A.5** The system shall emit a Layer-1 chain entry on intake. Incident payload referenced by ID; full payload not stored in-chain.

### 2.4 Stage B — Analysis (FR-B)

**FR-B.1 — Agent Orchestrator (product)**
- **FR-B.1.1** Shall coordinate the three domain agents over a single incident within the 5-minute diagnosis budget (§3.1).
- **FR-B.1.2** Shall provide each domain agent with sufficient incident context; coordination pattern (sequential / parallel / hybrid; planner-worker / graph / supervisor) is **E3-owned**.
- **FR-B.1.3** Shall compose the three agent outputs into a single recommendation payload (FR-C.1).
- **FR-B.1.4** Shall degrade gracefully on partial agent failure: produce a recommendation with explicit "agent X unavailable" marker rather than fail silently.

**FR-B.2 — Diagnosis Agent**
- **FR-B.2.1** Shall produce a fault hypothesis (or ranked set) grounded in observable symptoms.
- **FR-B.2.2** Shall produce a reasoning trace linking symptoms to hypothesis.
- **FR-B.2.3** Shall flag "insufficient data" explicitly; no forced low-confidence guess.

**FR-B.3 — Ticket Correlation Agent**
- **FR-B.3.1** Shall search historical and open ticket corpus for related incidents.
- **FR-B.3.2** Shall return correlation evidence: related tickets, grounds (co-timing / shared-node / shared-symptom / shared-customer-impact), related-ticket outcomes.
- **FR-B.3.3** Shall operate within an explicit, auditable correlation window (lookback duration + live-ticket scope). Window numerics are **CI-17**; mechanism is **E3-owned**.
- **FR-B.3.4** Shall state "no significant correlations found" explicitly; silent emptiness prohibited.

**FR-B.4 — SOP Agent**
- **FR-B.4.1** Shall retrieve applicable SOPs for the incident class.
- **FR-B.4.2** Shall extract named remediation guidance: preconditions, steps, expected outcome, escalation criteria.
- **FR-B.4.3** Shall record SOP versions referenced (SOP version-pinning per E1 §2.1). **Retrieval pattern is E3-owned within the constraints that CI-10 (SOP/KB structure) surfaces.** Where the corpus is document-only with no machine-readable metadata, retrieval options are bounded by that reality; E3 selects within CI-10's envelope.
- **FR-B.4.4** Shall state "no applicable SOP found" explicitly; silent emptiness prohibited.

### 2.5 Stage C — Recommendation production (FR-C)

- **FR-C.1** Recommendation payload shall be structurally complete per declared contract. Required fields:
  - Incident ID (traced to intake).
  - Decision class: `REMOTE_RESOLUTION` | `FIELD_DISPATCH`.
  - For `REMOTE_RESOLUTION`: remediation steps (ordered), preconditions, expected outcome, escalation criteria, SOP references (ID + version).
  - For `FIELD_DISPATCH`: justification (named criteria), urgency class, diagnostic summary, SOP references where dispatch is SOP-directed.
  - Diagnostic summary.
  - Correlation summary (including explicit "none found" when applicable).
  - Per-agent confidence or status flag (incl. "agent unavailable").
  - Timestamp of production.
  - System version + SOP corpus version pinned at intake (FR-A.4).
- **FR-C.2** Recommendation shall be operator-reviewable: every decision element traces to at least one of {diagnostic reasoning, correlation evidence, SOP reference}.
- **FR-C.3** Taxonomy of "remote resolvable" vs "requires dispatch" is **CI-1**. System enforces structural completeness only until taxonomy resolved.
- **FR-C.4** Recommendation shall be produced within the production sub-budget (§3.1 NFR-L.1). Timeout shall emit a governance-chain record and either return best-effort-partial or null-with-cause — behaviour is **E3-owned**; the requirement is explicit timeout handling, not silent over-run.

### 2.6 Stage D — Human review gate (FR-D)

Per E1 §2.1 named error modes.

- **FR-D.1 — Approval path.** Operator approves. System records approval with operator identity + timestamp + optional comment. Triggers Stage E.
- **FR-D.2 — Reject path.** Operator rejects. Rejection-reason-code structurally captured from declared taxonomy — **CI-2**.
- **FR-D.3 — Override path.** Operator takes different action. Override-reason-code + chosen-action structurally captured (taxonomy shared with CI-2).
- **FR-D.4 — No-review / timeout path.** **There shall exist a configurable operating window; behaviour on expiry is client-configured (CI-3). There shall be no unbounded-pending state that survives system restart silently.** On restart, any recommendation past its window shall be explicitly re-materialised in the chain with its terminal state (pending-expired / re-presented / auto-escalated per config).
- **FR-D.5 — System-unavailable path.** On agent-system failure (orchestrator outage, sustained timeout, all domain agents unavailable), incident falls back to manual handling via the ticketing system without blocking. Fallback is graceful: ticket returned to operator with "recommendation unavailable" + cause; no silent queue dead-letter.
- **FR-D.6** No outbound action on any path. Stage D produces human-decided outcome only; execution is outside product scope (E1 §2.2). Human-review-gate authority non-waivable (E1 §5.3).

### 2.7 Stage E — Outcome recording (FR-E)

- **FR-E.1** System shall write operator decision back to ticketing system against the incident record (write-back contract **E3-owned**).
- **FR-E.2** System shall emit a Layer-1 chain entry capturing: recommendation-payload reference, operator identity (per **CI-5**), decision class (approved / rejected / overridden / timed-out / unavailable), decision time, reason code where applicable, SOP versions referenced.
- **FR-E.3** Outcome-chain entry shall link back to intake-chain entry (FR-A.5) and recommendation-production chain entry (FR-C), producing auditable per-incident trace.
- **FR-E.4** Ticketing-system write-back shall be idempotent: replay of same decision shall not produce duplicate outcome record.

### 2.8 Stage F — Post-hoc audit (FR-F)

- **FR-F.1** For any given past recommendation, system shall enable reconstruction of SOP versions live at recommendation time. Storage approach (snapshot vs reference-by-version-ID) **E3-owned**.
- **FR-F.2** System shall support audit query: "for incident X, produce full decision record — intake → agent outputs → recommendation → operator decision — with SOP versions." Layer-2 derived view; query interface **E3-owned**.
- **FR-F.3** System shall support test-incident-set evaluation (per E1 §4.2 / X4): replay or re-analyse curated set; produce recommendation-quality metrics against ground-truth. Replay semantics (live-model re-infer vs recorded-output replay) **E3-owned**.
- **FR-F.4** System shall support compliance evidence extraction: Layer-2 auditor view returning per-incident governance evidence.

---

## 3. Non-functional requirements

### 3.1 Latency (first-order — E1 §5.2)

- **NFR-L.1** Diagnosis window: **5 minutes wall-clock per incident, intake (FR-A.1) → operator decision-ready state**. The system production sub-budget (intake → recommendation made available for review, FR-C.1) shall be **≤3 minutes**, leaving ≥2 minutes of operator-cognition time within the overall 5-minute diagnosis envelope. **Client confirmation of the 5-minute envelope decomposition is CI-1a** — confirms whether the client's "5 min diagnosis" includes operator cognition or ends at recommendation-produced.
- **NFR-L.2** Latency budget is product-internal. Ticketing-system intake-trigger time and operator-review time are separate from the production sub-budget; operator-cognition is inside the overall envelope but outside the production sub-budget.
- **NFR-L.3** Sync invocation and sequential agent coordination are viable within the 3-minute production sub-budget (per knowledge contribution). Rules sync orchestration **in** as an E3 candidate; does not rule out async/parallel. Selection **E3-owned**.
- **NFR-L.4** System shall instrument per-stage latency (intake / diagnosis / correlation / SOP / compose / total) as observability metric (§3.5) and expose it in audit view (FR-F.2).

### 3.2 Availability

- **NFR-A.1** Availability during NOC operating hours. 24×7 vs business-hours posture is **CI-4**.
- **NFR-A.2** On system unavailability, ticketing-system path remains operational (FR-D.5).
- **NFR-A.3** Target availability SLA is client-specified (**CI-4**). E2 does not pre-set a number.
- **NFR-A.4** Planned-downtime windows (model updates, SOP refresh, governance maintenance) shall be pre-announced and coincident with lowest-volume periods (client-input for windowing).

### 3.3 Reliability

- **NFR-R.1** Recommendation production shall be **deterministically reconstructable**: given same intake + same SOP corpus version + same model version, the recommendation record shall be reconstructable via replay (FR-F.3). Model non-determinism is acceptable *if* reasoning-trace + output record is faithfully captured in the chain. Re-running the model is not required to yield byte-identical outputs; the record must be faithful.
- **NFR-R.2** Schema-validation errors on intake (FR-A.3), recommendation (FR-C.1), write-back (FR-E.1) shall produce explicit error records, not silent drops.
- **NFR-R.3** On transient failure, system shall implement bounded retry with explicit retry-budget; on exhaustion, FR-D.5 applies. Retry numerics **E3-owned**.
- **NFR-R.4** Governance-chain writes (FR-A.5, FR-C chain entry, FR-E.2) shall be synchronous with respect to decision record: recommendation is not "produced" until its chain entry is successfully recorded. Chain-write failure is a production failure.

### 3.4 Auditability

- **NFR-AU.1** Every recommendation, reviewer decision, SOP reference, agent output, and intake event shall be captured in a tamper-evident chain (Layer-1 per 4WRD Recording Mechanism).
- **NFR-AU.2** Chain shall be queryable per-incident, per-operator, per-time-range, per-SOP-version (Layer-2 derived views).
- **NFR-AU.3** SOP version pinning shall be preserved for the regulatory retention period — **CI-6**.
- **NFR-AU.4** Audit trail shall be sufficient to answer in one query per incident: (a) what was recommended, (b) on what evidence, (c) against which SOP version, (d) what operator decided, (e) with what reason.
- **NFR-AU.5** IMDA licensing / sectoral regulatory obligations are **CI-7**; retention + audit-access requirements confirmed before E4 hardens the surface.

### 3.5 Observability

- **NFR-O.1** Operational metrics: per-stage latency (NFR-L.4), error rates per stage, recommendation throughput, agent-unavailable rate, no-review/timeout rate, approval/reject/override ratios.
- **NFR-O.2** Proof metrics relevant to 4WRD governance (adversarial-catch-rate, provenance-query success rate, rework rate) instrumented at product boundary for MVGH-β proof. (Governance-side requirement — see §5.4.)
- **NFR-O.3** Logging + metrics destination (Prometheus / OpenShift monitoring / external) **E3-owned**.
- **NFR-O.4** Alerts on: recommendation-production latency breach, persistent timeout, chain-write failure, retrieval-system unavailability. Routing (operator / ops / both) **CI-8**.

---

## 4. Integration requirements

### 4.1 Ticketing system (read + write)

- **IR-T.1** System shall read incident payloads via ticketing system's supported interface. Push vs pull **E3-owned**; interface must be auditable (every read traceable to a ticketing-system event).
- **IR-T.2** System shall write outcomes back to the ticketing system against the originating incident (FR-E.1).
- **IR-T.3** Ticketing-system schema (fields, severity vocab, correlation hints) — **CI-9**.
- **IR-T.4** Authentication (service account, token lifecycle, rotation) **E3-owned** + **E4-owned hardening**; credentials must not be embedded in code or config snapshots.
- **IR-T.5** Integration idempotent: re-processing same incident ID yields one record, not duplicates.

### 4.2 SOP / KB (read-only)

- **IR-S.1** System shall read SOP content on query (FR-B.4).
- **IR-S.2** SOP content shall be versioned; system shall identify "SOP version live at time T" for any past T within retention (FR-F.1).
- **IR-S.3** SOP/KB structure (documents / hierarchical / RAG-ready / graph / multiple sources) — **CI-10**.
- **IR-S.4** Retrieval pattern **E3-owned within CI-10 constraints** (FR-B.4.3).
- **IR-S.5** SOP content curation is **out of scope** (E1 §2.2). System consumes only.

### 4.3 OpenShift AI platform constraints on integration

- **IR-O.1** Product shall be deployable on RedHat OpenShift AI on client-provided on-prem infrastructure.
- **IR-O.2** Self-hosted model serving shall use an OpenShift AI-supported inference runtime (**model selection E3-owned** — Llama / Mistral / Granite / IBM-supported candidates).
- **IR-O.3** Agent-orchestration layer shall deploy on OpenShift AI (**framework selection E3-owned**).
- **IR-O.4** **External API egress from the product runtime is forbidden.** Any E3 design requiring external egress (e.g., model licence-server callout, external retrieval dependency) shall be flagged explicitly and requires (a) client approval recorded against the design artefact and (b) a chain-recorded justification entry naming the egress target, purpose, and approving party. **No default-permissible external egress.**
- **IR-O.5** Storage, namespace, resource-quota, platform-identity follow OpenShift AI conventions; configuration **E3 / E8-owned**.
- **IR-O.6** 4WRD's own substrate (Claude Agent SDK) is **not** deployed on OpenShift AI. 4WRD governs the delivery process; NOC product is the runtime. No product-4WRD substrate coupling at runtime.

---

## 5. Governance requirements (MVGH-β)

Requirements on the **delivery process**, distinct from product requirements above.

### 5.1 Delivery process invariants

- **GR-D.1** Every E-skill cycle from E2 onward shall operate under cycle-primitive governance (Intent Cycle moments, convergence-state discipline, DISCIPLINE-1/2/3, primary derivation intent declaration, exit artefact ratification).
- **GR-D.2** As MVGH-β elements come online (S6 §3.1, 15 elements), subsequent cycles progressively operate under richer governance. E2 remains partial governance per CARRY-FWD-4 and §5.6 below.
- **GR-D.3** Every ratified exit artefact persisted under version control with `[E<n>]` commit prefix (continuing S1–S6 + E1 convention).
- **GR-D.4** Every ratified exit artefact shall declare: primary derivation intent, contributing cycles, open items, inheritance surface for next E-skill.

### 5.2 Evidence the governed delivery must produce

- **GR-E.1** Per-incident recommendation records with full agent-output + SOP-version + reviewer-decision trace (product outputs of NFR-AU.1–5 serve this).
- **GR-E.2** Per-cycle adversarial-challenge records: at minimum, one adversarial moment per Production moment per cycle, recorded in the cycle exit artefact.
- **GR-E.3** Per-cycle primary derivation intent + knowledge contribution record: captured in opening prompt + cycle verification; persisted alongside exit artefact.
- **GR-E.4** Rework events: 3-valued tracking (new / rework / rework-causal-attributed) for any work revisited after ratification. Advances conventional buffer-no-tracking (category 2) → explicit-tracking (category 3) per S6 §4.2.
- **GR-E.5** MAS TRM domain-level evidence (Technology Risk Governance, IT Project Management, SDLC, Change Management, IT Audit, Access Control, Cryptography) — generated at the governance layer, per domain. **Control-number-level mapping is E4 work.**
- **GR-E.6** SOP version-pinning evidence satisfies Change Management domain evidence (SOP change is a change-control event with auditable trace).
- **GR-E.7** Chain-integrity evidence: HMAC-chain verification pass per cycle exit. **Conditioned on C2 custom-light being online** — the C2 Wave-1 custom-light T10 path compensates the absent SDK ledger primitive; GR-E.7 evidence can only be produced once C2 is live. Until then, the cycle is explicitly "chain-integrity-evidence-not-yet-applicable" rather than "chain-integrity-evidence-missing".

### 5.3 Five primary proof metrics — instrumentation surface

| Metric | Measurement locus | Owner |
|---|---|---|
| ΔE — effort delta | Solo-elapsed-weeks × attention-intensity × 5d/w vs 163-pd baseline | E9 measures realised delta; E2 resolves governance-increment (§8) |
| ΔT — schedule delta | Calendar elapsed | E9 |
| ΔR — role compression | Role-mapping instantiation (§6) + RACI preservation audit | E9 |
| ΔRW — rework visibility | GR-E.4 3-valued tracking | E9 |
| ΔC — compliance readiness | **Generated continuously E2–E9 via GR-E.5 domain evidence + GR-E.6 SOP change-control; E4 adds control-number mapping; E9 packages for client** | E2–E9 generate; E4 maps; E9 packages |

Numeric thresholds are E2–E9-propagated, not pre-set here.

### 5.4 Secondary instrumentation (3-in-MVGH, 4-deferred per S6 §4.3)

- **GR-S.1** Provenance-query success rate — Layer-2 view level.
- **GR-S.2** Adversarial-catch rate — counted per cycle from adversarial-challenge records (GR-E.2).
- **GR-S.3** Rework rate — derived from GR-E.4.
- **GR-S.4** *(Deferred post-MVGH)* frame-change detection latency, theory-churn delta, time-to-crystallisation, artefacts-per-attention-week.

### 5.5 Methodology binding

- **GR-M.1** Methodology posture is **gate-based (Waterfall or Hybrid)** — aligns with MAS TRM expectation (S6 §2.5).
- **GR-M.2** E-skill boundaries (E2→E3→E4→…→E10) serve as gates. Each gate = ratified exit artefact + open-items transfer + client-facing gate review where applicable.
- **GR-M.3** Orchestration-layer numerics (gate frequencies, review cadences, hand-off intervals) flagged Orchestrator-level / E8+ — not bound at E2.

### 5.6 Governance mode — progressive framing (CARRY-FWD-4 tension resolved)

**No contradiction between CARRY-FWD-4 and the progressive-governance statement.** CARRY-FWD-4 says: *no prior substantial delivery was 4WRD-governed*. The MVGH-β delivery is the **first** governed delivery, and it operates under **progressively increasing** governance coverage as MVGH-β substrate elements come online within the delivery itself. "First fully governed" means the first time full-harness evidence can be produced — structurally achievable only once all MVGH-β elements are live.

| Cycle | Governance coverage |
|---|---|
| E1, E2 (now) | Cycle primitives + adversarial dialogue + version-controlled artefacts (partial) |
| E3 | As MVGH-β Wave 1 substrate comes online (A2 chains, B1 master anchor, B5 schema, C2 custom-light T10, Sidecar Detector) — partial → intermediate |
| E4 onwards | AG-7 identity binding + AG-2/AG-3 enforcement activating as Waves 2/3 come online — intermediate → full |
| E7 onwards | All MVGH-β 15 elements expected online; full-harness evidence producible on the NOC product build/test/deploy/ops phases |

**Evidence-claim bound:** each cycle's evidence-set is bounded by MVGH-β substrate live at that cycle's time. This is honest progressive governance, not a staged-contradiction.

---

## 6. Role-compression mapping — instantiated

Per S6 §5.2 template. **pd numerics are TBD pending CI-19.** Functional mapping stated explicitly against a conventional NOC delivery team.

[DISCIPLINE-3: mapping by function-performed, not title.]

| Conventional role | Functional responsibility | Baseline pd | 4WRD locus | MVGH pd |
|---|---|---|---|---|
| Business Analyst | Elicit NOC workflow; define incident taxonomy; capture decision contracts | TBD | Producing Agent + **Human Team** decision | TBD |
| Solution Architect | Multi-agent architecture; OpenShift AI topology; integration patterns | TBD | Producing + **Adversarial** + **Human Team** sign-off | TBD |
| AI/ML Engineer | Model selection, prompt engineering, retrieval-tuning, agent orchestration | TBD | Producing Agent (domain-specialised) | TBD |
| Data Engineer | SOP corpus ingestion, correlation pipelines, retention | TBD | Producing + **Human Team** for data-contract | TBD |
| Integration Engineer | Ticketing + SOP/KB adapters; API contracts; auth | TBD | Producing Agent | TBD |
| Backend / Platform Engineer | OpenShift AI deployment; pod/service config; scaling | TBD | Producing (E8) | TBD |
| Frontend Engineer | Reviewer UI if separate from ticketing | TBD | Producing (conditional on **CI-11**) | TBD |
| Security Engineer | Authn/authz, secret management, audit-chain security | TBD | **Adversarial** + **Human Team** + E4 hardening | TBD |
| Compliance / Audit Engineer | MAS TRM mapping, evidence-generation requirements | TBD | **Adversarial** + **Human Team** (evidence by-construction via governance layer) | TBD |
| QA / Test Engineer | Test-incident-set curation, quality evaluation, replay tests | TBD | Producing + **Adversarial** | TBD |
| Release / DevOps | OpenShift AI pipelines, CI/CD, promotion | TBD | **Orchestrator** + Producing | TBD |
| Project Manager | Delivery coordination, stakeholder reporting, risk register | TBD | **Orchestrator** | TBD |
| Technical Writer | Documentation, runbooks, handover | TBD | Producing (emergent from chain + exit artefacts) | TBD |
| NOC SME (consultant) | Domain input: incident classification, SOP interpretation, correlation heuristics | TBD | **Human Team** (client-side SME; not compressed) | TBD (client-side) |
| **Total** | | **163** | | **Envelope 78–141 indicative** (governance-increment per §8) |

**Compression mechanism (S6 §5.2):** AI personas absorb production-labour at near-zero marginal cost (INPUT-001 §7 Principle 2). Human Team retains decision-labour; Orchestrator retains coordination. 78–141 pd range reflects decision + coordination hours compressed to solo-founder attention; Producing / Adversarial hours off the pd ledger.

**RACI preservation:**
- **Accountable / Responsible-decider:** Human Team (solo orchestrator; client-accountable remains with client).
- **Consulted:** NOC SME (client-side), compliance, platform owner — retained, not compressed.
- **Informed:** stakeholders per client governance — retained.
- **Responsible-producer:** Producing Agent (per-skill / per-specialisation personas).
- **Adversarial review:** structurally mandatory per cycle moment; not role-assigned. Replaces "peer review" as a *role* with "peer review" as a *cycle primitive*.

### 6.1 ΔR proof-risk — named

**ΔR credibility is client-cooperation-gated.** The per-role pd breakdown of the 163-pd baseline (CI-19) is required for quantitative ΔR (conventional role pd vs MVGH role pd). If CI-19 is unresolved at E9:
- Functional mapping above stands as **weaker-form ΔR evidence** — shows the re-assignment of responsibilities to personas / Human Team / Orchestrator with RACI preserved.
- **Quantitative ΔR is not demonstrable** without the baseline per-role breakdown.
- Proof-credibility on ΔR rests on the load-bearing triad still being met by ΔC + ΔRW with ΔR in weaker-form if CI-19 remains unresolved.

E9 measurement plan must name whether weaker-form or quantitative ΔR is the evidence form, per CI-19 status at that time.

---

## 7. Open questions requiring client input

Agenda for requirements-gathering sessions. 21 items (20 from Explorative + CI-1a added, CI-11 elevated).

| # | Question | Blocks | Priority |
|---|---|---|---|
| CI-1 | Incident-classification taxonomy: "remote resolvable" vs "requires dispatch" criteria | E3 decision-output contract | High |
| **CI-1a** | **5-minute envelope decomposition: does "5 min diagnosis" end at recommendation-produced, or include operator-cognition time?** Confirms 3-min production sub-budget vs alternative split. | E3 orchestration budget | **High** |
| CI-2 | Rejection / override reason-code taxonomy | E3 UI + chain schema | High |
| CI-3 | No-review timeout behaviour: escalate / hold / page / park (configurable window mechanics) | E3 workflow + E8 | High |
| CI-4 | Availability posture: 24×7 vs business-hours; target SLA% | E3 / E8 | Medium |
| CI-5 | Operator identity in governance chain: named / pseudonymous / role-based | E3 + E4 access-control evidence | High |
| CI-6 | Audit-retention duration | E4 / E8 storage | Medium |
| CI-7 | IMDA / sectoral regulatory obligations | E4 compliance surface | High |
| CI-8 | Alert routing: operator / ops / both | E3 / E8 | Low |
| CI-9 | Ticketing-system schema: field inventory, severity vocab, correlation hints | E3 intake contract | High |
| CI-10 | SOP/KB structure: corpus type, access pattern, refresh cadence | E3 retrieval design (constrains FR-B.4.3) | **High** |
| **CI-11** | **Reviewer UI: inline in ticketing vs separate app vs dashboard. ELEVATED — major architecture fork; prerequisite for E3 FR-D scope; first client-input session priority.** | E3 FR-D scope + frontend-engineer role (§6) | **Top** |
| CI-12 | Test-incident-set: curation method, size, outcome-labelling, operator validation | E9 P4 measurement (see §10 escalation) | **High** |
| CI-13 | SOP change cadence: expected update rate + propagation SLA | E3 retrieval + audit | Medium |
| CI-14 | Emergency-override procedure documentation expectation | E3 + E4 | Medium |
| CI-15 | Operator onboarding model | E8 rollout | Medium |
| CI-16 | SLA contractual terms (MTTR, first-response) | E9 proof acceptance | Medium |
| CI-17 | Multi-incident correlation window (lookback duration, live-scope) | E3 correlation design | Medium |
| CI-18 | Recommendation-quality acceptance threshold | E9 acceptance | High |
| CI-19 | 163-pd baseline role-by-role breakdown | ΔR quantification; §6 numerics | High |
| **CI-20** | **(Reframed)** Share the governance-increment envelope (§8) with the offset-form (what the governance layer obviates). Client assesses **net value**, not line-item overhead acceptance. Question to client: does the net-value picture warrant MVGH-β over conventional delivery on this scope? | §8 proof credibility | High |

---

## 8. Governance-increment quantification

Per-item estimates with assumption bases. Where an item cannot be estimated without a named input, the missing input is named.

**Baseline framing:** 163-pd figure = core agent logic only, conventional delivery. MVGH-β adds, on top of core agent logic:

### 8.1 Per-item additive estimates (product-side integration only; MVGH-β substrate assumed already built)

| # | Increment item | Scope assumption | Estimate (pd) | Missing-input dependency |
|---|---|---|---|---|
| I1 | HMAC Layer-1 chain wiring at 4 product emission points (intake, recommendation, outcome, post-hoc) | Wrapper/adapter per emission; assumes Wave-1 A2/B1 libraries exist | **6–15** | None; bound to 4 emission points |
| I2 | B5 schema entries + additive-compatible policy for product emissions | 4–6 entry types (intake, agent-output, recommendation, operator-decision, SOP-reference, system-unavailable) | **3–8** | None |
| I3 | AG-2 pre-commit hook integration on product emissions | Wiring atop chain-emit moments; largely shared with I1 | **2–4** | None |
| I4 | AG-3 schema-validator chain invocation on governance writes | Validator-chain call integration | **2–4** | None |
| I5 | AG-7 identity binding on operator/reviewer records | Operator-identity field + binding to identity infrastructure | **2–5 (base)** / **+3–8 (if operator-identity policy complex)** | **CI-5** (operator identity policy) |
| I6 | SOP version-pinning chain records | Schema + capture at intake + capture at retrieval | **3–6** | **CI-10** (may shift if SOP corpus lacks version metadata) |
| I7 | Adversarial-challenge record emission per cycle moment | Development-process overhead; minimal product code | **0–2 (product-side)** | None |
| I8 | Layer-2 derived views (audit, observability) | View construction + query interface | **8–16** | **NFR-O.3** (observability destination E3-owned); **CI-11** (reviewer-UI host may share view surface) |
| I9 | MAS TRM domain-level evidence packaging | Chain extraction queries + packaging templates | **3–7** | **CI-7** (regulatory obligations may extend scope) |
| I10 | Test-incident-set integration wiring | Harness integration; only if product-side replay needed | **5–10** / **0 if entirely test-bench side** | **CI-12** (test-set provenance) + FR-F.3 E3 replay-semantics choice |

**Additive envelope:**
- **Low:** ~34 pd (tight scope, minimal complexity on each item).
- **Midpoint:** ~55 pd (central assumptions).
- **High:** ~75 pd (complex on I5 + full I10 + observability-heavy I8).

**Named missing inputs that would tighten the envelope:** CI-5, CI-10, CI-7, CI-11, CI-12, NFR-O.3 (E3 decision). Per the verification: these are named now; Targeted does not produce a false-precise single number without them.

### 8.2 Offset items (governance layer obviates conventional work)

| # | Conventional work obviated | Notional pd saved |
|---|---|---|
| O1 | End-of-project compliance remediation sprint (MAS-TRM-bound, back-loaded in baseline) | **10–20 pd** |
| O2 | Separate peer-review and architectural-review cycles (subsumed by adversarial-as-primitive) | **5–10 pd** |
| O3 | Separate audit-trail construction and documentation (chain is the audit trail) | **5–10 pd** |
| O4 | Separate change-management evidence construction (chain records + SOP version-pinning) | **3–5 pd** |

**Offset envelope:** **23–45 pd saved** (midpoint ~34 pd).

### 8.3 Net governance-increment envelope

**Additive form (worst case, strictly extra):** **34–75 pd** on top of 163-pd core.
**Offset form (net, after work obviated):**
- Low: 34 − 45 = **−11 pd** (net negative; governance layer saves more than it costs, if offset realised).
- Midpoint: 55 − 34 = **+21 pd** (net increment).
- High: 75 − 23 = **+52 pd** (net increment, high).

**Net envelope: ≈ −11 to +52 pd** (midpoint ~+21 pd).

### 8.4 Envelope implications on ΔE

Combining with S6 §7.2 role-compression envelope (163 pd → 78–141 effective pd indicative):

| Scenario | Effective pd | ΔE vs 163 |
|---|---|---|
| Low (tight governance + realised offsets + role-compression upside) | 78 − 11 = **67 pd** | **−96 pd (59% reduction)** |
| Midpoint (central assumptions) | ~110 + 21 = **~131 pd** | **−32 pd (20% reduction)** |
| High (complex governance, limited offset realisation) | 141 + 52 = **193 pd** | **+30 pd (18% increase)** |

**Honest framing (per S6 §4.6):**
- ΔE can credibly claim reduction **in low and midpoint scenarios**; ΔE may not be the load-bearing metric on this proof — high-scenario ΔE is net negative.
- **Load-bearing triad ΔC + ΔR + ΔRW structurally stands across all scenarios** per S6 §4.4 credibility threshold.
- The proof is credible *with governance-increment admitted* because ΔC + ΔR + ΔRW do not depend on ΔE direction; claiming ΔE reduction alone would be fragile.
- **If the high scenario materialises, the proof stakes its credibility on the triad.** This is the structural honesty of the design — MAS-TRM compliance-evidence-by-construction has a genuine cost; the value is in what the client would otherwise have to produce separately (O1 + O3 + O4 sum to 18–35 pd of evidence-work the conventional delivery must do post-hoc).

### 8.5 Quantification-completion commitment

Per E-cycle progression:
- **E3** refines I1, I3, I4, I6, I8 as architecture binds storage and framework choices.
- **E4** refines I5, I9 as CI-5, CI-7, CI-10 resolve.
- **E7** refines I10 as test-infrastructure is built.
- **E9** measures **realised** increment from chain records.

### 8.6 Missing inputs that would tighten the envelope (named, not fuzzed)

1. **CI-5** operator-identity policy — shifts I5 by up to +8 pd.
2. **CI-7** IMDA / regulatory obligations — shifts I9 by up to +4 pd.
3. **CI-10** SOP/KB structure + version metadata availability — shifts I6 by up to +3 pd.
4. **CI-11** reviewer UI host — shifts I8 and may share surface with reviewer-UI backend.
5. **CI-12** test-incident-set provenance — shifts I10 by up to +10 pd or to 0 if entirely test-bench side.
6. **NFR-O.3** observability destination (E3-owned) — shifts I8 within its range.

---

## 9. Ratification corrections

### 9.1 E1 §5.1 PII/PDPA — downgraded (from knowledge contribution)

Incident tickets carry no PII. PDPA scope-shaping from E1 §5.1 is **not-triggered** for this delivery. Operator-identity in governance records remains a design concern (CI-5) but is not incident-payload PII. E1 §5.1 stands as written; this cycle's scope resolves the "may force on-prem / may constrain API usage / may require chain-record masking" triggers:
- On-prem: confirmed by deployment constraint (not PII-driven).
- API egress: restricted by IR-O.4 hardened (operational policy, not PII).
- Chain-record masking of incident payload: not required.
- **Residual surface:** operator-identity handling (CI-5).

### 9.2 E1 §8.9 governance-mode declaration

E2 inherits partial governance; stated §5.6. **CARRY-FWD-4 tension resolved:** no contradiction between CARRY-FWD-4 and progressive governance. CARRY-FWD-4 asserts no prior substantial delivery was 4WRD-governed; MVGH-β is the first governed delivery; governance coverage progresses within the delivery as MVGH-β substrate comes online. "First fully governed" = first time full-harness evidence can be produced, structurally achievable only once all 15 elements are live.

### 9.3 CARRY-FWD-2 at product level — not triggered

Anthropic-concentration carry-forward applies to 4WRD's own substrate. NOC product's OpenShift AI + self-hosted-models posture is concentration-independent at product layer.

---

## 10. Flags + test-incident-set escalation

### 10.1 NOC-bias

Requirements above are NOC-shaped (low-volume latency-dominant; ticket-based discrete units; SOP-codified; human-in-loop gate; regulated sector). Generalisation of any NFR or FR to other domains shall re-audit against S1 §6 flags (E1 §7).

### 10.2 Methodology

Gate-based posture (§5.5) stated as likely for MAS TRM; final binding Orchestrator-level.

### 10.3 Test-incident-set (X4) unavailability — escalation path

If the client cannot provide a test-incident-set before E7 (Test cycle):

- **Escalation required before E7.** E6 → E7 gate shall not close with X4 unresolved. Resolution options:
  - **(a) Synthetic test-set option.** E7 generates a synthetic incident-set using available ticketing data + domain-SME input. Quality evaluation becomes domain-proxy, not ground-truth-operator-validated. P4 acceptance threshold (CI-18) must be re-scoped against synthetic baseline.
  - **(b) Deferred acceptance option.** E9 acceptance for P4 is deferred to post-deployment operational period with operator-agreement / override-rate measured in production. Extends proof timeline. MAS TRM change-management evidence still applies.
  - **(c) Block-and-raise option.** Delivery gate held pending client X4 delivery; escalation to client governance.
- **Decision locus:** Orchestrator + client; not a silent Producing-Agent choice.
- **Consequence on proof:** P4 (recommendation quality) measurement form changes per option selected; load-bearing triad ΔC + ΔR + ΔRW not affected.

### 10.4 163-pd role breakdown

§6 functional mapping stated; numeric breakdown **CI-19**. ΔR evidence form conditional on CI-19 resolution (§6.1).

---

## 11. Open items and E3 inheritance surface

### 11.1 E2 open items / deferrals

1. **Governance-increment refinement** (§8.5) — E3/E4/E7/E9 progression; realised measurement at E9.
2. **Client-input items CI-1 through CI-20** (§7) — first-session priority CI-11 (top), then CI-1/CI-1a/CI-2/CI-3/CI-5/CI-7/CI-9/CI-10/CI-12/CI-18/CI-19 (high).
3. **ΔR evidence form** (§6.1) — conditional on CI-19 by E9.
4. **Test-incident-set escalation path** (§10.3) — Orchestrator + client decision before E7.
5. **S5 / S4 inherited open items** (via E1) — unchanged.

### 11.2 E3 Architecture inherits

1. **Functional requirements** (§2) — stages A–F, 4-agent decomposition, structured recommendation contract.
2. **Non-functional requirements** (§3) — 5-minute envelope with 3-minute production sub-budget; availability / reliability / auditability / observability envelopes.
3. **Integration requirements** (§4) — ticketing + SOP/KB + OpenShift AI; **IR-O.4 hardened external-egress-forbidden rule.**
4. **Governance requirements** (§5) — MVGH-β delivery invariants; evidence set; methodology posture; governance-mode matrix.
5. **Role-compression mapping** (§6) — functional mapping + ΔR proof-risk flagged.
6. **21 client-input open questions** (§7) — CI-11 top-priority.
7. **Governance-increment envelope** (§8) — additive / offset / net forms; per-item refinement plan.
8. **Test-incident-set escalation path** (§10.3) — E7 gate rule.
9. **E3-owned decisions flagged throughout §2–§4** — agent coordination pattern, retrieval pattern, model selection, orchestration framework, reviewer-UI host, deployment topology, retry numerics, auth mechanism, storage approach, query interface, replay semantics, observability destination, correlation-search approach, push/pull trigger, reviewer-UI platform.

### 11.3 Later-E-skill inheritance

- **E4 Security & Compliance** — T12 key-lifecycle; MAS TRM control-number mapping (S5 / S6); CI-5, CI-6, CI-7, CI-14 resolution; I5 + I9 increment refinement.
- **E5 Data** — AG-5b per-type variants (shared with E3); SOP corpus ingestion contracts (CI-10 bound).
- **E6 Build** — implementation of E3 design against §2–§5.
- **E7 Test** — FR-F.3 replay; CI-12 resolution; test-incident-set escalation (§10.3).
- **E8 Deployment** — OpenShift AI topology; CI-4 availability; CI-8 alert routing; CI-15 onboarding.
- **E9 Operations** — realised ΔE measurement; ΔR evidence form per CI-19; CI-16 SLA; CI-18 P4 threshold; realised governance-increment.
- **E10 Feedback & Learning** — post-MVGH secondary metrics (GR-S.4); theory-retirement loop via AG-5b.

---

## 12. Carry-forwards and Disciplines

**Carry-forwards inherited (all 4 active):**
- CARRY-FWD-1 — Need 13 partial technical-constraint readiness.
- CARRY-FWD-2 — Anthropic platform concentration (4WRD-substrate-only; not NOC-product-triggered).
- CARRY-FWD-3 — C4 capacity binding constraint.
- CARRY-FWD-4 — MVGH-β is first governed delivery; progressive governance within (§5.6 resolves tension).

**No new carry-forwards introduced at E2.**

**Disciplines (3, inherited):**
- DISCIPLINE-1 — source-of-count tagging.
- DISCIPLINE-2 — convergence-state transition preferences not expressed by AI; E2 does not make architectural selections (upheld — every architectural implication flagged E3-owned).
- DISCIPLINE-3 — qualitative classification cites criterion.

**No new disciplines introduced at E2.**

---

*End of E2 exit artefact.*
