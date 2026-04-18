# E1 — Problem Definition — Exit Artefact

## 0. Status and frame

**Convergence state at exit:** Exact. Ratified.
**Primary derivation intent:** docs/e1-scope-statement.md; docs/s6-solution-brief.md; docs/s5-exit-artefact.md; docs/s1-exit-artefact.md §6 (NOC first-target bias).
**Contributing cycles:** E1.1 Explorative (problem-definition first-pass across 7 sections), E1 Targeted → Exact (9 adjustments absorbed: dual-layer frame retained, governance-mode declaration, E2-owned thresholds, latency elevated first-order, PII/PDPA scope-shaping, §3.2 scope-mapping corrected, human-review error modes in-scope, test-incident-set dependency, SOP version-pinning in-scope).

**Governance mode at this cycle:** **Partial governance.** Cycle primitives (Direction Capture, Production, Adversarial Challenge, Verification, Convergence-state discipline, DISCIPLINE-1/2/3, carry-forward registry) are active on this cycle. Full-harness infrastructure (HMAC chains, B5 write-through, Layer 2/3 views, Sidecar Detector structural channel, AG-3 validator chain, AG-7 identity binding) **activates progressively as MVGH-β setup completes.** This artefact is produced under the conditions it describes — per CARRY-FWD-4 (S5 §9) last substantial delivery remains ungoverned by 4WRD; first fully governed delivery begins at E1 of the first client-scope SDLC cycle.

**Dual-layer frame (retained):**
- **Layer A — NOC product problem:** the problem the delivered system solves for a Telco NOC operator. Single canonical product-problem statement in §1.4.
- **Layer B — 4WRD proof problem:** the problem the delivery itself solves for the forcing-function proof (per S5 §4). Layer B is out-of-scope for E2 Requirements but conditions success-criteria bifurcation (§3.1 product-level vs §3.2 delivery-level) and scope comparability (§3.2 scope-mapping correction).

## 1. Problem definition (Layer A)

### 1.1 Domain

Telco Network Operations Centre (NOC) — Incident Management. A NOC operator receives logged incident tickets and must determine how each incident is resolved.

### 1.2 Current-state workflow (as-is)

On ticket intake, the NOC operator must:
- **Diagnose** the fault from the ticket payload (symptoms, affected nodes, timestamps).
- **Correlate** with related open or recently-closed tickets to identify co-incidence, duplication, or shared root cause.
- **Consult SOPs** for applicable remediation guidance.
- **Decide** whether the incident can be resolved remotely (and with what remediation steps) or requires field engineer dispatch (and with what justification).

Work is manual, knowledge-intensive, and time-critical. Operator proficiency on correlation + SOP recall is the rate-limiting skill.

### 1.3 Problem characteristics

- **Knowledge-intensive:** requires operator judgement over tickets history, SOPs, network topology.
- **Time-pressured:** delays carry SLA and customer-impact consequences; latency envelope is a first-order constraint (§5.2).
- **Expertise-gated:** quality and speed vary sharply with operator seniority.
- **Auditable decision:** remote-vs-dispatch decisions require traceable justification (incident post-mortem, SLA reporting, regulatory audit).

### 1.4 Canonical product-problem statement

> When an incident ticket is logged, a NOC operator must diagnose the fault, correlate it with related tickets, consult SOPs, and determine whether the issue can be resolved remotely (with remediation steps) or requires field engineer dispatch (with justification). This determination is manual, knowledge-intensive, and time-critical; operator proficiency is the principal quality and speed variable.

### 1.5 Solution posture (inherited from scope statement)

Multi-agent system of four agents — **Diagnosis Agent**, **Ticket Correlation Agent**, **SOP Agent**, **Agent Orchestrator** — jointly producing a structured recommendation per incident: (i) remote resolution with remediation steps, or (ii) field engineer dispatch with justification. Recommendation is presented to a NOC operator for human-in-the-loop review and approval before any action is taken. **The system recommends; the human decides.**

E1 defines the problem. E1 does not select architecture, agent boundaries, orchestration pattern, or tool choices — these belong to E3 per DISCIPLINE-2.

## 2. Scope boundary

### 2.1 In scope

Core agent logic + decision-output contract:
- Diagnosis, Ticket Correlation, SOP, Orchestrator agent roles (logical; boundaries resolved E3).
- Incident intake from ticketing system.
- Structured recommendation output (remote + steps OR dispatch + justification).
- Human-review gate before any outbound action.
- **SOP version-pinning at recommendation time:** every recommendation records the SOP version it was produced against, enabling reproducibility, review traceability, and invalidation on SOP change (named in-scope design requirement).
- **Human-review-gate error modes as named design requirements:**
  - **Operator-approval path.** Default "happy" path; recommendation approved.
  - **Operator-reject path.** Rejection must be captured structurally (not only narratively); rejection reason codes are an E2 design item.
  - **Operator-override path.** Operator takes a different action from the recommendation; the override decision must be captured and attributed.
  - **No-review / timeout path.** Recommendation issued but no human decision within operating window; behaviour is a design requirement not a deployment accident.
  - **System-unavailable path.** Agent system is offline or fails to produce a recommendation; fallback-to-manual must be graceful and must not block incident resolution.

### 2.2 Out of scope (this delivery)

- **Field engineer dispatch system integration.** Recommendation output lands in the ticketing system; dispatch actioning is human-initiated downstream.
- **Remediation execution (remote).** The system recommends remote steps; execution is operator-driven.
- **SOP content curation.** The system consumes the SOP knowledge base; creation, editing, approval, and lifecycle of SOP documents are outside this delivery.
- **Incident intake upstream** of the ticketing system (alerting, telemetry pipelines, event correlation).
- **Integrations, infrastructure, deployment pipeline** (per scope statement — these are out of the 163-pd estimate).
- **Ticketing system replacement or extension.** The ticketing system is a boundary.

### 2.3 Deferred with activation path

- **Multi-region / multi-tenant NOC operation.** Single NOC instance this delivery; multi-tenant activation path preserved via SEAM-5 ownership-tier tag on every record.
- **Non-English SOP corpus.** English-only this delivery; language-scope expansion is a post-MVGH item.
- **Field engineer dispatch system integration** (moved from out-of-scope to deferred if client later requests activation; activation trigger = dispatch-system availability + operator-workflow design task).

## 3. Success criteria

### 3.1 Product-level (Layer A)

| # | Criterion | Measurement posture | Threshold owner |
|---|---|---|---|
| P1 | Recommendations produced are **structurally complete** (all required output fields populated per contract) | Pass/fail per recommendation | E2 |
| P2 | Remote-vs-dispatch classification is **operator-reviewable** (every recommendation carries SOP reference + correlation evidence + diagnostic reasoning) | Audit of recommendation payload | E2 |
| P3 | **Human-review gate is the single authority** for action (no outbound action without operator approval) | System invariant; test-verifiable | E2 |
| P4 | **Recommendation quality** — operator agreement / override rate stays within acceptable band | Longitudinal; requires test-incident-set (§4.2) | E2 + E9 |
| P5 | **Latency** — recommendation produced within operator-workflow-compatible window | First-order constraint; see §5.2 | E2 |
| P6 | **SOP version-pinning** — every recommendation names the SOP version it was produced against | Structural; test-verifiable | E2 |

Thresholds for P4 and P5 are **strictly E2-owned**. E1 does not set numeric pass-bars. **TBD retained deliberately** — fabricating E1 thresholds would pre-empt E2 requirements authority and corrupt proof-credibility.

### 3.2 Delivery-level (Layer B — 4WRD proof)

Inherited from S5 §4 (5 primary metrics). Delivery-level criteria are E9-verified on completion of the first governed SDLC cycle; they are recorded here only as success criteria the delivery as a whole must meet to count as proof.

**Scope-comparability statement (corrected):**
- The 163-pd baseline is **core agent logic only.** MVGH-β SDLC **adds governance integration overhead** (chain wiring, validator chain, Sidecar Detector, Layer 2 views, MAS TRM evidence generation) on top of core agent logic.
- The comparison is therefore **conservative (favourable to the conventional baseline)** — the 4WRD delivery carries additional work the baseline does not carry, and still must demonstrate ΔE reduction.
- **E2 quantifies the governance increment** (what MVGH-β adds to the 163-pd core-agent-logic envelope) so ΔE is computed on a like-for-like effective-person-day basis after governance-overhead is named and sized.
- Per S5 §6.1 the current envelope (78–141 effective pd vs 163 pd baseline) is provisional under this framing; E2's governance-increment quantification may tighten or widen the envelope.

| # | Delivery criterion | Metric (S5 §4.1) | Owner |
|---|---|---|---|
| D1 | Effort reduction on comparable basis after governance-increment quantification | ΔE | E2 quantifies governance increment; E9 measures realised ΔE |
| D2 | Schedule behaviour | ΔT (baseline-silent — not-primary per S5 §6.2) | E9 |
| D3 | Role compression realised (conventional team → solo + Producing/Adversarial/Orchestrator personas) | ΔR | E9 |
| D4 | Rework explicitly chain-recorded (3-valued category advancement) | ΔRW | E9 |
| D5 | MAS TRM compliance evidence generated by construction (embedded-continuous) | ΔC | E4 control-number mapping + E9 evidence |

### 3.3 Credibility threshold

Per S5 §4.3: ≥3 of 5 primary dimensions must show material structural advantage; no residual dimension may show uncompensated material regression. Load-bearing triad ΔC + ΔR + ΔRW structurally met by architecture before ΔE numbers settle.

## 4. Assumptions and external dependencies

### 4.1 Assumptions

| # | Assumption | If false |
|---|---|---|
| A1 | Ticketing system exposes incident payloads via a readable interface (API, export, or equivalent) | Scope-shaping; requires ingestion adapter work not currently sized |
| A2 | SOP knowledge base is machine-readable or can be made machine-readable within the 163-pd envelope | May require SOP content preparation effort outside scope |
| A3 | Historical ticket corpus is available for correlation (real or representative) | Correlation agent utility is degraded; test-set dependency (§4.2) intensifies |
| A4 | NOC operators are available for human-review-gate operation | System is non-operable; out-of-scope for E1 to design around operator absence |
| A5 | Regulatory posture is MAS TRM-bound (per scope statement) | Compliance surface changes (§5.1) |
| A6 | Production deployment is the target context (not prototype or pilot) | Acceptance bar changes; deployment-tier scope (out-of-scope) shifts |
| A7 | Volume is low (tens/day) — not throughput-dominant | Sizing of correlation search, SOP retrieval, and LLM call budgets changes |
| A8 | Human-review-gate is the sole authority for action (human-in-the-loop, not on-the-loop) | Autonomy level shifts; error-mode set and regulatory posture change |

### 4.2 External dependencies

| # | Dependency | Owner / Source | Required for |
|---|---|---|---|
| X1 | Ticketing-system read access + payload schema | Client / NOC operations | E2 intake contract; E3 adapter design |
| X2 | SOP knowledge base — structure, access, version metadata | Client / NOC knowledge management | E2 SOP-retrieval contract; §2.1 SOP version-pinning |
| X3 | Historical ticket corpus with outcome labels (remote-resolved vs dispatched) | Client / NOC historical data | E2 correlation requirements; E9 recommendation-quality measurement |
| X4 | **Test-incident-set** — curated incidents with ground-truth outcomes (operator-validated) usable for pre-deployment evaluation of recommendation quality (P4) | Client + E2 curation work | E2 acceptance design; E9 P4 measurement |
| X5 | MAS TRM control-number authoritative mapping source (specific clauses in effect for this client's posture) | Client compliance function | E4 control-level mapping |
| X6 | NOC operator availability for human-review-gate testing and rollout | Client / NOC operations | E8 rollout; E9 proof operation |
| X7 | Production deployment environment access (client infrastructure) | Client platform / security | E8 deployment |

## 5. Constraints

### 5.1 Regulatory / compliance constraints

- **MAS TRM-bound.** Technology Risk Governance, IT Project Management, SDLC, Change Management, IT Audit, Access Control, Cryptography domains in effect (per S5 §5.3). Evidence generated at governance layer at domain level; control-number-level mapping is E4 work.
- **PII / PDPA — upgraded to scope-shaping constraint.** Incident tickets may contain customer-identifying data (subscriber IDs, contact details, service addresses, device identifiers), operator identity, and engineer identity. PII/PDPA handling is not a downstream hardening concern; it **shapes architecture** from E3 onwards:
  - **May force on-prem or in-region deployment** (ruling out or constraining hosted/SaaS LLM routes; affecting T-family selection).
  - **May constrain external API usage** (redaction-before-egress requirements, region-pinned endpoints, provider attestations).
  - **May require chain-record PII masking or tokenisation** — HMAC chain entries must not become a PII leak surface; B5 schema entries carry governance metadata, but payloads that land in chain records need masking/tokenisation policy at the schema level.
  - Human-review records, override records, and operator-attribution records are PII-bearing by construction.
- **Audit trail, change management, SDLC controls apply** (per scope statement). 4WRD governance layer generates evidence; institution files attestation (S5 §5.3 honesty bound preserved).

### 5.2 Technical constraints

- **Latency — first-order constraint.** Recommendation latency must be compatible with NOC operator workflow; the constraint is workflow-compatibility, not a pre-specified millisecond bound. **Most load-bearing open question. E2 resolution is a prerequisite before E3 architecture can proceed** — latency envelope directly gates:
  - Agent orchestration pattern (sequential vs parallel vs hybrid).
  - LLM call budgets per recommendation.
  - Correlation search strategy (index pre-build vs on-demand; corpus size admissible).
  - SOP retrieval approach (pre-embedded vs on-demand).
  - Deployment topology interacting with §5.1 on-prem pressure.
- **Volume (tens/day)** — throughput not a binding constraint; per-incident latency is.
- **Integration boundary** — ticketing system (intake + output) + SOP/KB (read-only). No dispatch-system, no telemetry-pipeline, no remediation-execution plane integration.
- **Deterministic audit evidence.** Governance-layer evidence must be reproducible per recommendation: same inputs + same SOP version → same recorded justification chain. Non-determinism within the LLM stack is acceptable if **the justification record is deterministically reconstructable** from the chain.
- **Failure-mode explicitness.** Every no-recommendation or degraded-recommendation path must be explicit (§2.1); silent failure is a design defect not an edge case.

### 5.3 Operational constraints

- **Solo orchestrator.** No deputy, no multi-actor team (S5 §9 CARRY-FWD-4 context).
- **Attention-intensity 0.5–0.7 operating fraction** (S5 §5.4); first governed SDLC cycles produce direct empirical calibration.
- **Governance-mode declaration (restated):** E1 operates under **partial governance** — cycle primitives active; full-harness infrastructure activates progressively as MVGH-β setup completes. Downstream E-cycles inherit increasing governance coverage as MVGH-β elements come online. E2 opens under the same partial governance; E3 onwards progressively richer.
- **Dogfooding.** 4WRD is used to produce 4WRD + this NOC delivery. No separate methodology for the proof delivery.
- **Human-review-gate authority is non-waivable.** The system recommends; the human decides — this is an operational constraint, not a preference.

## 6. Open questions for E2

The following are named E1 → E2 handoff items. Each has an owner and a downstream block.

| # | Open question | Owner | Blocks |
|---|---|---|---|
| Q1 | Latency envelope — numeric target for P5, derived from NOC operator workflow analysis | E2 | E3 architecture (most load-bearing per §5.2) |
| Q2 | Recommendation-quality threshold (P4) — operator agreement / override-rate acceptable band | E2 + client | E9 acceptance |
| Q3 | Test-incident-set — curation method, size, outcome-labelling discipline, operator validation | E2 + client | E9 P4 measurement |
| Q4 | SOP version-pinning mechanism — snapshot at recommendation time vs reference-by-version-ID | E2 | E3 SOP-retrieval design |
| Q5 | Human-review-gate UI / workflow — approval, reject-with-reason, override-with-reason, no-review-timeout | E2 | E3 UX + E8 rollout |
| Q6 | PII handling policy — on-prem deployment requirement vs redaction-before-egress vs provider attestation route | E2 + client compliance | E3 architecture, T-family selection |
| Q7 | Chain-record PII masking / tokenisation policy | E2 + client compliance | E3 B5 entry payload schema; MVGH-β AG-7 identity binding PII-bearing fields |
| Q8 | MAS TRM control-number mapping — specific clauses in effect | E4 | E9 evidence completeness |
| Q9 | Correlation-agent corpus — size, access pattern, refresh cadence | E2 | E3 correlation design |
| Q10 | Dispatch-justification structured fields — what the recommendation must name for a dispatch output to be audit-acceptable | E2 + client | E3 output contract |
| Q11 | Remote-resolution steps structured fields — format, granularity, executable-vs-advisory distinction | E2 + client | E3 output contract |
| Q12 | Rejection-reason and override-reason taxonomy | E2 | E3 design; E9 ΔRW measurement |
| Q13 | Fallback-to-manual behaviour — what the operator sees when the system is unavailable | E2 | E3 degradation design |
| Q14 | Governance-increment sizing on 163-pd core-agent-logic baseline | E2 | §3.2 ΔE like-for-like comparability |
| Q15 | Operator-identity and SoD evidence — which MAS TRM Access Control expectations apply to operator approval records | E2 + E4 | E3 AG-7 identity binding for operator records |
| Q16 | Incident-classification taxonomy — what defines "remote resolvable" vs "requires dispatch" in this NOC's posture | E2 + client | E3 decision-output contract |

## 7. NOC-bias flags (per S1 §6 first-target discipline)

E1 has been produced with the NOC as the first target. Downstream cycles must audit for NOC-specific assumptions that do not generalise to other domains in the 4WRD forcing-function proof surface:

- **F1** — Low-volume / latency-dominant. Throughput-bound domains (e.g. high-frequency trading ops, consumer support) invert the constraint structure.
- **F2** — Human-in-the-loop approval before action. Domains with autonomous action (industrial control, trading) do not have this gate and require different governance topology.
- **F3** — Ticket-based discrete work unit. Stream-of-work domains (on-call SRE, chat support) lack the ticket boundary.
- **F4** — SOP-codified domain expertise. Less-codified domains (frontier research, product strategy) lack the SOP anchor.
- **F5** — Regulated-sector compliance posture (MAS TRM). Non-regulated domains have different ΔC weighting.
- **F6** — Operator-identity PII centrality. Anonymous-user domains do not carry the same chain-record PII pressure.

Flags are recorded here for downstream audit — they do not change this delivery's design. They condition generalisation claims made from this proof.

## 8. E2 Requirements inheritance surface

E2 opens with:

1. **Canonical product-problem statement** (§1.4) as the problem reference.
2. **Scope boundary** (§2 in/out/deferred) as the envelope.
3. **Success criteria with TBD thresholds** (§3.1) — E2 fills numeric thresholds for P4, P5, and ratifies P1/P2/P3/P6 structural criteria.
4. **Delivery-level criteria with scope-comparability correction** (§3.2) — E2 quantifies governance increment on 163-pd core-agent-logic baseline (Q14).
5. **Assumptions A1–A8** and **external dependencies X1–X7** (§4) as preconditions.
6. **Constraints** (§5 regulatory incl. upgraded PII/PDPA; latency first-order; operational incl. governance-mode declaration).
7. **16 open questions Q1–Q16** (§6) as E2's opening backlog.
8. **NOC-bias flags F1–F6** (§7) for downstream generalisation audit.
9. **Governance-mode declaration** — E2 operates under the same partial governance as E1; incremental governance coverage as MVGH-β progresses.

## 9. Carry-forwards and Disciplines

**Carry-forwards inherited (S5 §9, all 4 active):**
- CARRY-FWD-1 — Need 13 partial technical-constraint readiness.
- CARRY-FWD-2 — Anthropic platform concentration.
- CARRY-FWD-3 — C4 capacity binding constraint.
- CARRY-FWD-4 — MVGH setup + this E1 cycle conducted under partial governance; full-harness infrastructure activates progressively as MVGH-β setup completes.

**No new carry-forwards introduced at E1.**

**Disciplines (3, inherited):**
- DISCIPLINE-1 — source-of-count tagging.
- DISCIPLINE-2 — convergence-state transition preferences not expressed by AI; E1 does not make architectural selections (inherited property, upheld — no agent-boundary, orchestration, or tool choices made here).
- DISCIPLINE-3 — qualitative classification cites criterion.

**No new disciplines introduced at E1.**

## 10. Open items

1. **Q1 latency envelope** — most load-bearing open question (§5.2); E2 resolution prerequisite before E3 architecture.
2. **Q6/Q7 PII policy + chain-record masking** — scope-shaping (§5.1); may force on-prem and constrain T-family selection downstream.
3. **Q14 governance-increment sizing** — enables like-for-like ΔE comparison (§3.2) and resolves S5 §6.1 envelope framing.
4. **Q3 test-incident-set curation** — required for P4 measurement credibility; client-dependent.
5. **S5 §10 items and S4 §8 open-items** inherited unchanged.

---

*End of E1 exit artefact.*
