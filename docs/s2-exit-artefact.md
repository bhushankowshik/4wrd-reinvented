# 4WRD — S2 Exit Artefact

**Context and Constraint Mapping — Consolidated Input to S3 (Option Generation)**

- **Status:** Ratified at Exact. Primary input to S3.
- **Date:** 2026-04-17.
- **Ratification chain:** S2.1 → S2.2 (Explorative — taxonomy absorption); S2.3 (D2 Targeted reconciliation); S2.4 (uniformity check + priority-gap mapping); S2.5 (D1 reconciliation); S2.6 (D6 reconciliation AG-4/AG-6b); S2.7 (non-AG-9 remaining gap mapping); S2.8 (T4 decision + D5 reconciliation); S2.9 (AG-9 cluster under option b); Exact convergence.

---

## 1. Scope

S2 mapped the constraint landscape shaping the 4WRD harness build itself — current-state with target-state divergence surfaced. Out of scope per S2.1: client regulatory landscape (MAS TRM, CCoP 2.0, PDPA-as-client-side, CAAS/ICAO) as binding obligations on the build; Telco NOC engagement specifics. These may re-enter as design inputs at S3+.

---

## 2. Constraint Dimension Taxonomy (8 dimensions)

| ID | Dimension | Resolution path | Reconciliation state |
|---|---|---|---|
| D1 | Technical platform | Closes as Agent SDK matures / custom layer is built | Dedicated-reconciled (S2.5) |
| D2 | Epistemic / dogfooding | Closes by building unbuilt 4WRD mechanisms | Dedicated-reconciled (S2.3) |
| D3 | Capacity / attention | Closes only by more humans | Uniform (S2.4) |
| D4 | Organisational | Closes by team formation or multi-actor build-out | Per-gap |
| D5 | Commercial | Closes via market / cost engineering | Dedicated-reconciled (S2.8) |
| D6 | Regulatory | Non-negotiable while present | Dedicated-reconciled (S2.6–S2.7) |
| D7a | Methodological — binding | Binding by S1 ratification | Uniform (S2.4) |
| D7b | Methodological — deferred | Activates at future design moments | Deferred-tracked (S2.2) |

**Dimension count: 8 (7 active + 1 deferred-tracked), counted from table above, per DISCIPLINE-1.**

---

## 3. Dimensional constraint-source inventories

### 3.1 D1 Technical platform — T-sources (14)

**Provided (10):** T1 Subagents with isolated context windows; T2 SDK hooks (4 fixed types; **partially-provided** — enforcement surface present, persistence absent); T3 Skills system; T4 Agent Teams (experimental; Opus 4.6 minimum; known limitations: session resumption, task coordination, shutdown); T5 ClaudeAgentOptions env configuration; T6 Context window limits; T7 Rate limits / API quotas; T8 Model cost tier; T13 MCP server integration; T14 Permission/sandbox modes.

**Absent (4):** T9 Native persistent storage; T10 Native audit/lineage ledger; T11 Native cross-tenant isolation; T12 Native identity / key lifecycle.

### 3.2 D2 Epistemic / dogfooding — Build-state inventory of 14 S1 needs

- **Partial (5):** N1 Direction addressability, N2 Structural output critique, N5 Context integrity, N6 Policy enforcement, N8 Composition across scale.
- **Unbuilt (7):** N3 Direction revisability, N4 Artefact provenance, N7 Act attribution, N10 Learning retention, N11 Theory retirement, N12 Invariance, N14 Retirement candidate surfacing.
- **Target-state only (1):** N9 Multi-actor coordination.
- **Structural claim (1):** N13 Meta-governance closure.

### 3.3 D5 Commercial — C-sources (8)

C1 No client contracts current-state; C2 Target-state regulated client deployment; C3 Model API token cost (Opus 4.6 minimum for T4); C4 Solo-founder capital (attention + model spend); C5 Infrastructure cost for absent-T primitives; C6 IP/licensing model for composed assets; C7 Pricing model for client-facing deployment; C8 Platform concentration on Anthropic (elevated to CARRY-FWD-2).

### 3.4 D6 Regulatory — R-sources (4)

- **Binding current-state:** R1 PDPA (Singapore operating geography confirmed).
- **Conditional-binding current-state:** R2 GDPR (conservative assumption yes).
- **Likely non-binding current-state:** R3 CCPA/CPRA (commercial thresholds not met).
- **Emerging, target-state dominant:** R4 EU AI Act + emerging AI regulation.

**Source counts (per DISCIPLINE-1):** 14 T-sources, 14 S1 needs (5+7+1+1), 8 C-sources, 4 R-sources — all counted from inventories above.

---

## 4. Per-gap Constraint Maps (13 A-tagged gaps)

Compact form. Per-gap rows per dimension. *[b] notation = conditioned on option (b) custom coordination layer.*

| Gap | D1 | D2 | D4 | D5 | D6 |
|---|---|---|---|---|---|
| **AG-2** critique form + non-optionality | T1, T2*, T6, T8, T10 (1 absent); Active | N2 partial + N6 partial; High | Current single-op; Target cross-actor critique → AG-9e | Low/Low | Moderate-current / Dense-target |
| **AG-3** Frame Change Sidecar **[gap-coextensive with N3]** | T1, T2*, T6, T10 (1 absent); Active | N3 unbuilt coextensive; N4 unbuilt; High-coextensive | Current no inter-actor framing; Target multi-actor framing | Low/Moderate | Moderate-current / Dense-target |
| **AG-4** Artefact Lineage **[gap-coextensive with N4; pivot gap]** | T9, T10, T11, T12 (4 absent); Active all-absent | N4 unbuilt coextensive; High-coextensive | Current single-actor; Target couples to AG-7a | Moderate/Dense | **Dense / Dense** — only current-state-dense gap |
| **AG-5b** deterministic composition rules | T1, T2*, T3, T6 (0 absent); Active | N5 partial + N10 unbuilt; Moderate | Current single-op; Target couples to AG-9c/9e (subject to AG-9 mapping) | Low/Moderate | Moderate-current / Dense-target |
| **AG-6b** exception/override semantics | T2*, T3, T10 (1 absent); Active | N6 partial + N12 unbuilt; High | Current single authority; Target couples to AG-9d, AG-7a | Low/Moderate | Low-current / Dense-target |
| **AG-7a** actor identity + joint-act | T10, T11, T12 (3 absent); Active all-absent | N7 unbuilt + N9 target-state; High | Current joint-act dormant; Target activates | Low/Moderate | Moderate-current / Dense-target |
| **AG-8** composition algebra + cross-tenant | T1, T3, T11 (1 absent); Active | N8 partial + N4 unbuilt; Moderate | Current single-actor; Target multi-tenant | **Low / Dense — architecturally determinative (D5-dec-1/2/3 S3)** | Low-current / Dense-target |
| **AG-9a** concurrency [b] | T1, T4, T5, T7 (0 absent); Active | N9 target + N7 unbuilt; Low-current / High-target | Current serial; Target concurrent | Low/Dense | Low-current / Dense-target |
| **AG-9b** communication protocol [b] | T1, T4, T10 (1 absent); Active; T4 session-resumption limitation applies | N9 target + N7 unbuilt; Low/High | Current none; Target constitutive | Low/Dense | Low-current / Dense-target |
| **AG-9c** coherence [b] — *heaviest custom-layer* | T4, T9, T10 (2 absent); Active; T4 task-coordination limitation applies | N9 target + N7 unbuilt; Low/High | Current none; Target critical | Low/Dense | Low-current / Dense-target |
| **AG-9d** quorum/consensus [b] | T1, T4, T12 (1 absent); Active; couples AG-7a via T12 | N9 target + N7 unbuilt; Sparse-current / High-target | Current no quorum; Target consensus-requiring | Dormant/Dense | Dormant-current / Dense-target |
| **AG-9e** role-assignment [b] — *T-17 absorbs SEAM-5 candidate* | T1, T3, T4 (0 absent); Active | N9 target; Low/High | Current implicit 1:1; Target coordination primitive | Low/Moderate | Low-current / Moderate-target |
| **AG-9f** handover [b] — *T4 shutdown manifestation locus* | T1, T4, T10 (1 absent); Active; T4 shutdown limitation applies | N9 target + N7 unbuilt; Low/High | Current no handover; Target frequent | Low/Dense | Low-current / Dense-target |

D3 uniform across all 13 gaps (single-human attention scalar). D7a uniform (disciplines on mapping-process).

**Gap count: 13 mapped, counted from table above, per DISCIPLINE-1.**

---

## 5. Structural Tension Register (18)

| ID | Tension | Primary gap | Category |
|---|---|---|---|
| T-1 | Audit immutability vs right-to-erasure | AG-4 | Technical |
| T-2 | Retention duration vs audit longevity | AG-4 | Technical |
| T-3 | Cross-tenant isolation boundary at replication | AG-4 | Technical |
| T-4 | Override-with-audit dependency | AG-6b | Technical |
| T-5 | Bounded-override floor (un-overrideable category) | AG-6b | Technical |
| T-6 | Override-authority delegation (multi-actor) | AG-6b | Technical |
| T-7 | Determinism vs context-adaptive composition | AG-5b | Technical |
| T-8 | Actor identity granularity vs tenant boundary | AG-7a | Technical |
| T-9 | Share-by-default vs isolate-by-default | AG-8 | Technical |
| T-10 | IP/licensing model for composed assets | AG-8 | Commercial |
| T-11 | Concurrency fairness vs audit ordering | AG-9a | Technical |
| T-12 | Message synchrony vs asynchrony | AG-9b | Technical |
| T-13 | Consistency vs availability under partition | AG-9c | Technical |
| T-14 | Lock granularity vs throughput | AG-9c | Technical |
| T-15 | Quorum floor vs agility | AG-9d | Technical |
| T-16 | Tie-breaking authority | AG-9d | Technical |
| T-17 | Static vs dynamic role binding *(absorbs SEAM-5 candidate)* | AG-9e | Technical |
| T-18 | Handover atomicity vs availability | AG-9f | Technical |

**Tension count: 18 (17 Technical + 1 Commercial), counted from register above, per DISCIPLINE-1.**

Dependency tags (blocks/relates-to) retained in working register; summarised here.

---

## 6. Seams, Disciplines, Procedurals

### 6.1 Named Seams (5 + 1 procedural)

- **SEAM-1** — Invariant special-class evolution (from S1).
- **SEAM-1a** — Invariant-set initial instantiation (from S1).
- **SEAM-2 procedural** — Citation rule (from S1; PROCEDURAL-3 merged).
- **SEAM-2a** — Recursion depth for meta-governance closure (from S1).
- **SEAM-3** (S2.4) — AG-4 ↔ D7a lineage-citation co-dependency. Design-order constraint: AG-4 mechanism choice prerequisite for D7a enforceability. Extended at S2.6 to include D6 manifestation.
- **SEAM-4** (S2.5) — T10 build-cascade. AG-4 mechanism choice is upstream dependency for T10 across 8 of 13 A-tagged gaps (AG-2, AG-3, AG-4, AG-6b, AG-7a, AG-9b, AG-9c, AG-9f). Build-order constraint.

**Named seam count: 5 + SEAM-2 procedural, counted from list above, per DISCIPLINE-1.**

### 6.2 Disciplines (3)

- **DISCIPLINE-1** (S1 Exact) — Numerical claims in convergence artefacts must be source-of-count tagged. Origin: open correction of prior miscount.
- **DISCIPLINE-2** (S2.3) — Producing AI shall not express convergence-state transition preferences; surface stability evidence and await human decision.
- **DISCIPLINE-3** (S2.4) — Qualitative classifications must cite the criterion applied inline.

### 6.3 Procedurals (1)

- **PROCEDURAL-2** (S1 Exact) — A/I tag-drift reporting during constraint mapping. Tag drift expected and visible.

---

## 7. Carry-Forwards (3)

- **CARRY-FWD-1** (S1 Exact) — Need 13 partial technical-constraint readiness; distinguishing mechanism (tagging / subject metadata / equivalent) chosen at implementation.
- **CARRY-FWD-2** (S2.8) — Anthropic platform concentration risk. Applies landscape-wide via D1 T-source dependency; every gap's D1 engagement is contingent on Anthropic-as-provider.
- **CARRY-FWD-3** (S2.9) — AG-9 cluster constraint maps conditioned on custom-layer feasibility. First implementation cycle for the custom coordination layer must include a feasibility validation gate before maps are treated as confirmed.

**Carry-forward count: 3, counted from list above, per DISCIPLINE-1.**

---

## 8. Unified Decision Register

| ID | Decision | Status | Locus |
|---|---|---|---|
| DEC-T4 | Agent Teams engagement mode (a/b/c) | **Resolved: option (b)** — custom coordination layer on T4 via T5 | S2.8 decider action |
| DEC-D5-1 | IP ownership of composed assets | **Deferred to S3** | S3 Option Generation |
| DEC-D5-2 | Cross-tenant sharing model for composed assets | **Deferred to S3** | S3 Option Generation |
| DEC-D5-3 | Pricing unit for client-facing deployment | **Deferred to S3** | S3 Option Generation |
| DEC-SEAM-1 | Invariant special-class evolution mechanism | Deferred (design-order) | Future cycle |
| DEC-SEAM-1a | Invariant-set initial instantiation | Deferred (bootstrap) | Future cycle |
| DEC-SEAM-2a | Recursion depth for meta-governance closure | Deferred | Future cycle |
| DEC-CF1 | Need 13 distinguishing mechanism (tagging / subject metadata / equivalent) | Deferred | Implementation |
| DEC-INV | Initial invariant set | Pending | Bootstrap |

**Decision count: 9, counted from register above (1 resolved, 3 deferred-S3, 5 deferred-future/implementation), per DISCIPLINE-1.**

---

## 9. Landscape-level Findings (top-line)

**F1. AG-4 is the pivot gap of the constraint landscape.** AG-4 (N4 Artefact Lineage) is simultaneously:
- gap-coextensive with an unbuilt mechanism (D2);
- upstream dependency for T10 (absent audit/lineage ledger) across 8 of 13 gaps (D1, per SEAM-4);
- prerequisite for D7a enforceability (SEAM-3);
- the only current-state-dense gap on D6;
- regulatory-dense across all 4 R-sources.

AG-4 resolution is first-order implementation priority across all dimensions. Paired with F2 below.

**F2. D6 is target-state-dominated across 12 of 13 gaps.** AG-4 is the single current-state-dense exception. Implication: regulatory pressure scales sharply at deployment; current-state baseline is modest but target-state is uniformly dense. Commercial deployment readiness is regulatory-gated.

**F3. D5 is target-state-dominated with one architecturally-determinative exception (AG-8).** Parallel pattern to F2. AG-8 is the only current-state commercial-architecture-determining gap; its D5 sub-decisions (DEC-D5-1/2/3) are S3 priorities. *Nuance:* D5 and D6 share target-state dominance as a landscape pattern; D6 is bound by 4 regulatory sources of non-negotiable character, D5 by 8 commercial sources of varying activation strength. The parallelism is directional, not mechanism-symmetric.

**F4. T4 (Agent Teams) named limitations map precisely onto three AG-9 sub-gaps.** Session resumption → AG-9b; task coordination → AG-9c; shutdown → AG-9f. Option (b) custom-layer adds most value at precisely these three loci.

**F5. T10 cascade (8 of 13 gaps) + T4-dependence (6 of 13) mean AG-4 and T4-decision resolution unblock 10+ gaps.** Scheduling implication: AG-4 mechanism and custom-layer feasibility validation are sequencing priorities for S3+.

**F6. D1 is universally Active across all 13 A-tagged gaps.** D1 Active-uniformity reflects D1's foundational nature — the SDK capability surface touches every architectural gap because every gap requires platform primitives to implement. Not a classification failure.

**F7. Tension clustering around SEAM-3/SEAM-4.** 6 of 18 tensions (T-1, T-3, T-4, T-6, T-8, T-9) relate to SEAM-3/4 or absent T-primitives that SEAM-3/4 depend on. The pivot-gap property of AG-4 extends into the tension register.

---

## 10. S3 Inheritance Surface

S2 inherits the following dependencies forward to S3. Five items are S3 dependencies — not completeness conditions — and each sits on the inheritance surface exactly as SEAMs and CARRY-FWDs did at S1 exit.

- **C-I.** AG-9 cluster maps depend on custom-layer feasibility (CARRY-FWD-3).
- **C-II.** D5 target-state entries depend on future client contracts and pricing model choices (DEC-D5-1/2/3).
- **C-III.** D6 R2/R3 classifications depend on future operating/user geography (conservative assumptions recorded).
- **C-IV.** D7b deferred commitments bind only at activation (SEAM-1, SEAM-1a, SEAM-2a decisions).
- **C-V.** Need 13 meta-governance closure remains structural claim until distinguishing mechanism chosen (CARRY-FWD-1).

Each is an explicit post-S2 dependency — none invalidates current mapping but each bounds its confirmed-state.

---

## 11. S3 entry handoff

**S3 entry conditions:**

1. S2 exit artefact ratified at Exact — **this document**.
2. Option (b) ratified as coordination-strategy starting point (DEC-T4).
3. Architecturally-determinative decisions surfaced for S3 resolution: DEC-D5-1/2/3.
4. First-order implementation priorities identified: AG-4 mechanism design; custom-layer feasibility gate.
5. 18-tension register carried forward as design-decision surfaces for S3 Option Generation.

**S3 expected outputs (from this vantage point):**

- Options for AG-4 mechanism design (storage/ledger/isolation/identity primitives).
- Custom coordination layer feasibility validation + scope + cost magnitude.
- Resolution of DEC-D5-1/2/3 (IP, sharing, pricing).
- Option sets for remaining tension surfaces.
- Initial invariant set candidate (DEC-INV).

---

**S2 CLOSED. S3 OPEN with this artefact as primary input.**
