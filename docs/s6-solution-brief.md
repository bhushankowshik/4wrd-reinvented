# 4WRD — Solution Brief

**Status:** Ratified at Exact (S6 exit artefact).
**Primary derivation:** docs/s5-exit-artefact.md; docs/s4-exit-artefact.md; docs/s2-exit-artefact.md; docs/s1-exit-artefact.md; docs/foundation/INPUT-001-foundation-v4.md.
**Audience:** Technical stakeholder (internal founder audience first; regulated-sector client audience second). Primary input to E1 Problem Definition. Complete enough that E1 can begin without re-reading S1–S5.

---

## Executive summary

4WRD is a governed agentic delivery harness that solves the governance gap left behind by AI production capacity: an addressable, auditable, adversarially-challenged, multi-actor, composable delivery surface that evolves under its own governance. The governed agentic delivery model (Intent Cycle + three-layer Recording + Frame Change Sidecar + Artefact Lineage, with Producing / Adversarial / Orchestrator agent persona families and Human Team as final decider) instantiates as **MVGH-β** — a 15-element current-state subset of the ratified full-stack design, with 17 deferred items preserving structural activation paths. The proof commitment is a single fully governed SDLC delivery on a real 163-person-day MAS-TRM-bound scope, measured against five primary metrics (effort, schedule, role compression, rework visibility, compliance readiness) with audience-bifurcated proof statements for founder (ΔE + wall-clock) and client (ΔC + ΔR + ΔRW). Wall-clock from now to first fully governed delivery completion: ≈17–33 months (setup ≈11–22 months ungoverned per CARRY-FWD-4 + first governed SDLC ≈6–11 months).

---

## 1. Problem statement

*(Source: S1 exit §1, ratified Exact 2026-04-17.)*

Teams adopting AI in delivery have acquired production capacity without acquiring a governance surface over that production — one that is addressable, auditable, adversarially-challenged, multi-actor, composable, and evolvable under its own governance. Such a surface must govern three dimensions simultaneously: delivery production, coordination across multiple humans and multiple agents, and the harness's own evolution — including bounded retirement of theory that no longer serves (with tombstones, not gaps), explicit invariants on what cannot be retired, and closure that prevents meta-governance regress. No existing AI-in-delivery governance framework provides this natively.

**Primary value proposition** *(source: S5 opening-prompt knowledge-contribution; traces to S1 Axis 3 needs):* elimination of compliance remediation sprints, architectural rework, and compounding institutional knowledge loss — not primarily faster production. Velocity benefits are supporting, not load-bearing. **These outcomes are the proof target of MVGH-β, not established effects**; claim-evidence is produced during the first governed SDLC cycle.

**First-target scope bias** *(source: S1 §6):* Telco NOC (audit-heavy, incident-driven). The crystallisation generalises beyond NOC; design choices discovered to be silently NOC-specific must be surfaced as bias-flagged decisions.

## 2. Solution concept — the governed agentic delivery model

*(Source: INPUT-001 §§2, 4, 5, 6.)*

### 2.1 Four structural elements (INPUT-001 §2)

1. **Intent Cycle** — atomic unit of 4WRD. Every act of AI production in delivery occurs within an Intent Cycle. Four moments: (i) Direction Capture — human declares convergence state, direction, and in Explorative state a knowledge contribution; primary derivation intent is declared; (ii) AI Produces — Producing Agent produces output and reasoning trace as two separable components, never blocking for more context; Adversarial Agent challenges both; (iii) Human Verifies — accountable verifiers respond independently on output and reasoning trace; Adversarial Agent challenges each verification act; (iv) Cycle Closes or Continues — on confirmation, cycle closes and lineage is recorded; on divergence, cycle continues with refined direction. Recursive at every granularity level including meta-cycles governing harness changes.

2. **Recording Mechanism (three layers):** Layer 1 raw record — per-actor HMAC chains anchored to a master chain; append-only, tamper-evident. Layer 2 derived views — human real-time, team coordination, auditor. Layer 3 AI context packages — Producing, Challenge, Orchestration context packages generated fresh before each agent invocation from Layer 1 entries since last generation. Five consumers: Human, Team, Auditor, Regulator, AI Actor.

3. **Frame Change Sidecar (always-live):** Detector — session boundary scan at every session start; in-session Tier 2 interrupt when Adversarial Agent detects frame invalidation during production. Receptor — six sources: humans, producing AI, adversarial AI, QA, qualification meetings, client. Frame Change is distinct from output-wrong: invalidates direction itself; cycle pauses and waits for new direction.

4. **Artefact Lineage** — every produced artefact carries a tamper-evident chain back through verification, critique, reasoning, direction. Primary derivation declared at Moment 1, recorded at Moment 4 on convergence. Incidental references captured passively.

### 2.2 Three convergence states (INPUT-001 §3)

Declared by the human at cycle start. Explorative (problem rough, knowledge contribution required) → Targeted (narrowing and verifying) → Exact (final convergence, produces clean exit artefact).

### 2.3 Four actors (INPUT-001 §4)

- **Human Team** — final point of call on all decisions; provides direction, knowledge contribution, verification.
- **Producing Agent** — persona family; one per skill per domain-specialisation.
- **Adversarial Agent** — persona family; highest capability tier; permanent challenger in every cycle moment; secondary Frame Change Detector.
- **Orchestrator Agent** — single instance; governs process; first receiver of Frame Change signals; nominates second-in-command.

### 2.4 Four configuration layers (INPUT-001 §5)

Domain → Specialisation → Skill → Persona. Reusable assets stack general to specific without re-implementation.

### 2.5 Sixteen reference skills and methodology (INPUT-001 §6)

Solutioning (6): S1 Problem Crystallisation, S2 Context and Constraint Mapping, S3 Option Generation, S4 Option Evaluation, S5 Solution Selection, S6 Solution Brief. SDLC Execution (10): E1 Problem Definition, E2 Requirements, E3 Architecture, E4 Security and Compliance, E5 Data, E6 Build, E7 Test, E8 Deployment, E9 Operations, E10 Feedback and Learning. Methodology (Waterfall/Agile/Hybrid) expressed in orchestration, not skills.

**Methodology-for-MVGH:** MVGH-β methodology is an orchestration-layer decision and is E1/E2 scope to confirm. For a MAS-TRM-bound delivery, a gate-based (Waterfall or Hybrid) methodology is the likely posture — MAS TRM expects documented gates, formal sign-offs, and discrete change-control moments that align more naturally with gate-based than with pure Agile cadence. E1 confirms methodology selection and binds orchestration-layer configuration accordingly.

### 2.6 Theory Retirement (INPUT-001 §8)

The harness governs its own evolution. Theory retirement is first-class: the harness must prune its own theory (skills, rules, learnings, registers, artefacts, schemas, personas — 7 types) and produce tombstones. Absence is not retirement; silent removal is prohibited. Harness evolution is governed by recursive application of the Intent Cycle.

### 2.7 Implementation target (INPUT-001 §9)

Claude Agent SDK (Python or TypeScript). Subagents with isolated context windows map to per-role context packages. SDK hooks map to 4WRD's four hook types. Skills system maps to the sixteen reference skills. The one custom component beyond SDK primitives is a thin shared-state layer for multi-user coordination across sessions.

## 3. MVGH-β selected architecture

*(Source: S5 exit §§2, 3, 7.)*

### 3.1 What is built (15 active structural elements)

[DISCIPLINE-1: 15 elements = Wave-0 (1) + Wave-1 (6) + Wave-2 (4) + Wave-3 (4 composite).]

**Wave 0 — commercial anchor (1):**
- SEAM-5 ownership-tier tag on every Layer-1 entry. (Commercial triple {O1-D layered ownership, O2-B vendor-curated abstraction, O3-D tiered subscription on per-cycle substrate} ratified at S4.1 but activates at commercial launch, not MVGH build.)

**Wave 1 — pivot substrate (6):**
- A2 per-actor HMAC chains (solo chain + master anchor).
- B1 master anchor + B5 chain-entry schema (additive-compatible forward policy).
- C2 custom-light T10 path (minimal infrastructure over absent Claude Agent SDK ledger).
- M9b-5 §9-direct messaging (trivial-solo self-messaging substrate).
- M9c-2 write-through coherence.
- Frame Change Sidecar Detector — in-session Tier 2 interrupt + session-boundary scan. Receptor sources scoped to {human, producing AI, adversarial AI}; {QA, qualification meetings, client} deferred.

**Wave 2 — identity + quorum + concurrency (4):**
- AG7-i HMAC per-actor identity + AG7-iii composite role-class binding + AG7-b chain-join joint-act.
- AG9d-1 trivial-solo quorum (N=1 degenerate).
- AG9a-3 concurrency — per-actor-serial branch active; cross-actor-parallel branch dormant.
- M9c-7 periodic reconcile scaffolded.

**Wave 3 — enforcement bundle (4 composite):**
- AG6b-1 sole-orchestrator override-authority.
- AG5b-4 hybrid inline + master-anchor common tombstone schema.
- AG9e-1 Orchestrator-gated normal-class role-assignment.
- AG2-4 dual-layer (pre-commit hook + schema validator) + AG8-5 registration + AG3-3 three-family validator chain — one composite enforcement bundle.

### 3.2 What is deferred (17 items with activation paths)

*(Source: S5 exit §3. Full register.)*

Every deferred item carries explicit activation trigger and structural-preservation mechanism:

1. AG6b-3 target-state multi-actor override-class → activates on deputy/2nd-actor crystallisation; role-class enum pre-provisioned.
2. AG6b-2 degenerate-intermediate → S4-preserved alternative.
3. AG6b-4 quorum-gated override → activates on quorum activation.
4. AG9d-2 larger-N quorum → activates on N>3 crystallisation.
5. AG9d-5 override-path shell → schema-gated dormant; activates with AG6b-3.
6. M9c-3 quorum-commit → dormant; activates on joint-act-rhythm signal.
7. AG9e-3 quorum-gated upgrade → activates with multi-actor quorum.
8. AG9e-2 human-gated forced override-class → activates with AG6b-3.
9. Multi-actor M9f-3 handover active → activates on 2nd actor onboarded; erasure-hook scaffold retained.
10. AG9a-3 cross-actor parallel branch → activates on 2nd actor.
11. AG-5b per-theory-type tombstone variants (7 types) → E3/E5 incremental per retirement event; common tombstone schema live in MVGH.
12. Fully-vendored {A7, B4, C3} alternative → preserved under D3-pressure or CA-class concentration acceptance.
13. AG9d-3 role-weighting policy → E3 on multi-actor approach.
14. AG9a-3 rollback-entry semantics → E3 on first failed joint-act.
15. T12 key-lifecycle full (rotation/revocation) → E4 ongoing.
16. M9c-3 activation instrumentation → E9 post-deployment.
17. Reconcile-window monitoring → E9 cross-actor only.

### 3.3 Three activation bands *(S5 exit §7)*

**Band 1 — E-skill incremental** (within first 1–2 governed deliveries): AG-5b per-type variants, T12 hardening, AG9d-3 role-weighting, AG9a-3 rollback semantics.
**Band 2 — Multi-actor activation** (on deputy/2nd-actor): AG6b-3, AG9e-2, M9f-3 active, AG9a-3 cross-actor, reconcile-window monitoring, AG9d-1 non-trivial quorum, AG9d-2 larger-N.
**Band 3 — Post-deployment operational signals**: M9c-3 activation, AG-9c-fuller revisit, AG9d-5 live, AG9e-3 quorum-gated upgrade.

Structural preservation verified: every Band-1/2/3 item is (i) schema-gated in B5 catalog (S4 §5), (ii) preserved-alternative in S4 §2.2 footnote, or (iii) locus-assigned in S4 §8. Activation = flag-flip or additive-schema, not re-design.

## 4. Proof structure

*(Source: S5 exit §§4, 5, 5a, 5b.)*

### 4.1 Baseline

163 person-days, conventional team delivery, MAS TRM-bound SDLC scope. Schedule not specified. Rework posture: buffer-no-tracking (conservative category 2 of 3). Compliance posture: MAS TRM-bound, non-null, back-loaded-in-practice. Provenance: conventional SDLC estimate, market-standard sizing. Role breakdown pending (template ready).

### 4.2 Five primary metrics

| # | Metric | Type | Load |
|---|---|---|---|
| 1 | Effort delta (ΔE) | Supporting | +22 to +85 pd reduction (13–52%) |
| 2 | Schedule delta (ΔT) | Supporting | Baseline-silent on this scope |
| 3 | Role compression (ΔR) | **Load-bearing** | Conventional-multi-role → solo + personas; RACI preserved |
| 4 | Rework visibility (ΔRW) | **Load-bearing** | Category advancement: buffer-no-tracking (2) → explicit-tracking (3) |
| 5 | Compliance readiness (ΔC) | **Load-bearing** | Embedded-continuous vs back-loaded-sprint |

Load-bearing triad ΔC + ΔRW + ΔR directly corresponds to S1 primary value proposition (compliance remediation / rework / knowledge loss elimination).

### 4.3 Secondary instrumentation

**In MVGH (3, within 3–4w setup cap):** provenance query success rate, adversarial-catch rate, rework rate.
**Deferred post-MVGH (4):** frame-change detection latency, theory-churn delta, time-to-crystallisation, artefacts-per-attention-week.

### 4.4 Credibility threshold

≥3 of 5 primary dimensions must show material structural advantage; no residual dimension may show uncompensated material regression. **Structurally met by load-bearing triad before ΔE numbers settle.** ΔT baseline-silent does not count as regression.

### 4.5 Audience bifurcation

**Internal (Bhushan-self, go/no-go weighting):** ΔE + wall-clock-from-now. Decision variable: is ≈17–33 month commitment justified by forcing-function proof + full-stack activation roadmap pathway to commercial product?

**Client (regulated-sector, MAS-TRM-readiness weighting):** ΔC + ΔR + ΔRW. Claim: MAS TRM audit evidence produced at the 4WRD governance layer by construction — every write is schema-validated, adversarially-challenged, and chain-recorded; no end-of-project compliance remediation sprint; conventional multi-role team compresses with RACI preserved through persona assignment; rework explicitly chain-recorded. **Evidence is generated at the governance layer at MAS TRM domain level; control-number-level mapping to specific MAS TRM clauses is E4 work, not pre-established in MVGH-β.**

### 4.6 Honesty bounds

4WRD generates audit evidence; the institution files attestation. MAS does not pre-certify frameworks. Claim is "evidence generation by construction", not "regulatory pre-approval". No over-claim of regulatory standing.

## 5. Constraint landscape summary

*(Source: S2 exit §§4, 6, 7, 9.)*

### 5.1 Key findings

**F1 — AG-4 is the pivot gap** *(S2 §9 F1):* AG-4 (Artefact Lineage / N4 unbuilt) is simultaneously gap-coextensive with an unbuilt mechanism (D2), upstream dependency for T10 absent-primitive across 8 of 13 A-tagged gaps (SEAM-4), prerequisite for D7a enforceability (SEAM-3), the only current-state-dense gap on D6, and regulatory-dense across all 4 R-sources. AG-4 resolution is first-order implementation priority across all constraint dimensions.

**F2 — D6 is target-state dominated across 12 of 13 gaps** *(S2 §9 F2):* AG-4 is the single current-state-dense exception. Regulatory pressure scales sharply at deployment; commercial deployment readiness is regulatory-gated.

**F3 — D5 is target-state dominated with one architecturally-determinative exception (AG-8)** *(S2 §9 F3):* AG-8 is the only current-state commercial-architecture-determining gap; its sub-decisions (DEC-D5-1/2/3) were S3 priorities (resolved at S4.1 to {O1-D, O2-B, O3-D}).

**F4 — T4 Agent Teams named limitations map precisely onto three AG-9 sub-gaps** *(S2 §9 F4):* session-resumption → AG-9b; task-coordination → AG-9c; shutdown → AG-9f. DEC-T4 resolved to option (b) custom coordination layer on T4 via T5 at S2.8.

**F5 — T10 cascade (8/13) + T4-dependence (6/13) → AG-4 + T4-decision unblock 10+ gaps** *(S2 §9 F5).*

### 5.2 Named seams

- **SEAM-1** — Invariant special-class evolution *(S1)*.
- **SEAM-1a** — Invariant-set initial instantiation *(S1)*.
- **SEAM-2** / SEAM-2 procedural — Citation rule *(S1)*.
- **SEAM-2a** — Recursion depth for meta-governance closure *(S1)*.
- **SEAM-3** *(S2.4)* — AG-4 ↔ D7a lineage-citation co-dependency. Design-order constraint: AG-4 mechanism choice prerequisite for D7a enforceability. Extended at S2.6 to include D6 manifestation.
- **SEAM-4** *(S2.5)* — T10 build-cascade. AG-4 mechanism choice upstream for T10 across 8 of 13 A-tagged gaps.
- **SEAM-5** *(elevated S4.1)* — Abstraction/instantiation ownership-tier boundary. Ownership-tier tag on every B5 entry; cross-tier writes rejected at validation.

### 5.3 Four carry-forwards

1. **CARRY-FWD-1** *(S1)* — Need 13 (meta-governance closure) partial technical-constraint readiness until distinguishing mechanism (tagging / subject metadata / equivalent) is chosen at implementation.
2. **CARRY-FWD-2** *(S2.8)* — Anthropic platform concentration risk. Applies landscape-wide via D1 T-source dependency. S3 CF-2 filter outcome: CA/CAmp classes empty across surveyed landscape. S4 outcome: all ratified options CN (Concentration-Neutral); baseline concentration accepted; marginal-DIV not actively pursued.
3. **CARRY-FWD-3** *(S2.9)* — AG-9 cluster constraint maps conditioned on custom-layer feasibility. First implementation cycle for custom coordination layer must include a feasibility validation gate. At S3.6: preserved as sequencing/parallelism input, not filter.
4. **CARRY-FWD-4** *(S5 Targeted Act 1)* — MVGH setup conducted without 4WRD governance harness. Last substantial delivery ungoverned by 4WRD. First fully governed delivery begins at E1 of first client-scope SDLC cycle.

### 5.4 SDK platform inventory (for reference)

*(Source: S2 §3.1.)* 14 T-sources: 10 provided (T1 subagents; T2 hooks, partial-provided; T3 skills; T4 Agent Teams; T5 ClaudeAgentOptions; T6 context limits; T7 rate limits; T8 model cost tier; T13 MCP; T14 permission/sandbox) + 4 absent (T9 native persistent storage; T10 native audit/lineage ledger; T11 native cross-tenant isolation; T12 native identity/key lifecycle). The 4 absent primitives drive the custom-light build scope (C2 T10 path in MVGH Wave 1).

## 6. Named architectural constraints

*(Source: S4 exit §6 + S2 exit §6.1 + S5 exit §8 = 12 total.)*

[DISCIPLINE-1: 12 = 5 S1 SEAMs + 2 S2 SEAMs + 1 elevated-S4 SEAM + 3 operational/authority constraints from S4 + 1 S5 addition.]

1. **SEAM-1** — Invariant special-class evolution.
2. **SEAM-1a** — Invariant-set initial instantiation.
3. **SEAM-2 / SEAM-2 procedural** — Citation rule.
4. **SEAM-2a** — Recursion depth for meta-governance closure.
5. **SEAM-3** — AG-4 ↔ D7a lineage-citation co-dependency; design-order constraint that AG-4 mechanism choice is prerequisite for D7a enforceability.
6. **SEAM-4** — T10 build-cascade; AG-4 mechanism choice is upstream dependency for T10 across 8 of 13 A-tagged gaps.
7. **SEAM-5** — Abstraction/instantiation ownership-tier boundary. Ownership-tier tag on every B5 entry; cross-tier writes rejected at validation.
8. **Override-authority-human-only** — Override is a human primitive per INPUT-001 §7 Principle 5. AI actors may not hold override authority. Deputy must be human.
9. **Override-respects-ownership-tier** — Override-authority bounded by SEAM-5. Cross-tier modifications require vendor-tier authority. Human orchestrators operate within user-tier scope only.
10. **Registration-emission reconcile-window** — Cross-actor registration-to-emission requires minimum one M9c-7 reconcile-window gap. Same-actor registration-to-emission immediate. Surfaces at E9.
11. **Dual-layer enforcement responsibility split** — AG-2 pre-commit hook performs presence-check; AG-3 schema validator performs full identity + role-class + human-actor-set verification on OVERRIDE entries.
12. **OVERRIDE-reject deterministic-mode policy** *(S5 addition)* — OVERRIDE writes produce explicit validation-reject with rejection-event node until AG-6b gate flips via AG6b-3 activation. B5 schema enum values {NORMAL, OVERRIDE} both declared; AG-3 bypass-policy per rule-family lives only after gate-flip. Deterministic in both MVGH-active and post-activation regimes.

## 7. Delivery envelope

*(Source: S5 exit §6 + S4 exit §7a.)*

### 7.1 MVGH setup (ratified, scope-independent)

- Wave 0 ≈1w + Wave 1 ≈12–18w + Wave 2 ≈6–9w + Wave 3 ≈12–18w = **≈31–46w linear**.
- Attention-multiplier 1.5x–2x for solo founder → **≈11–22 months elapsed**.
- CARRY-FWD-4: this setup is ungoverned-by-4WRD.

### 7.2 First governed SDLC (anchored to 163-pd scope)

- MVGH SDLC calendar: ≈26–47w.
- Attention-intensity fraction 0.5–0.7 (midpoint 0.6). **Calibration is directional, not quantitative:** the only empirical anchor is the S1–S4 cycle work (≈26 hours active wall-clock across ~1.5 calendar days), and S-cycle composition (lightweight verification + direction) differs materially from SDLC delivery composition (heavier artefact production + decision-hours). The 0.6 midpoint is an indicative operating assumption, not a measured rate. **Treat the full envelope below as indicative, with realised attention-intensity to be measured empirically during post-MVGH operation** (artefacts-per-attention-week secondary metric, deferred post-MVGH).
- Effective person-days under the indicative envelope: **78–141 pd** (low 78 / mid 110 / high 141).
- ΔE vs 163 pd baseline (indicative): **+22 to +85 pd (13–52% effort reduction)**.
- First governed SDLC calendar elapsed: **≈6–11 months**.

### 7.3 Wall-clock from now

**Total MVGH-β elapsed (setup + first fully governed SDLC): ≈17–33 months** — indicative envelope, attention-intensity-sensitive.

### 7.4 Schedule-risk compensation statement

ΔT is baseline-silent on this scope and not counted as primary. Independent of calendar-week parity, ΔC (embedded-continuous compliance) and ΔRW (explicit-tracking rework) structurally reduce schedule risk — the principal schedule-risk drivers in conventional MAS-TRM-bound delivery are late-surfacing compliance gaps and unvisible accumulating rework, both removed by construction. Calendar-parity MVGH delivery with structural schedule-risk reduction is a net advance.

## 8. Open items and E-skill inputs

### 8.1 Inherited open items (9 from S4, 5 from S5)

**S4 open items by locus** *(source: S4 exit §8)*:

| # | Item | Locus |
|---|---|---|
| 1 | AG9a-3 rollback-entry semantics for failed-quorum joint-acts | E3 |
| 2 | M9c-3 activation signal (joint-act frequency instrumentation) | Harness runtime / Layer 2 / operator |
| 3 | AG9d-3 role-weighting policy | E3 |
| 4 | T12 key-lifecycle (rotation, revocation) | E4 |
| 5 | AG-9c-fuller revisit if M9c-3 activates | Post-activation signal |
| 6 | AG-5b per-theory-type tombstone variants (7 types) | E3/E5 incremental |
| 7 | AG3-2 policy-as-code rule engine alternative (if rule-family count grows) | Future S-cycle or E-skill |
| 8 | Registration-emission reconcile-window constraint | E9 |
| 9 | AG6b-3 target-state activation on deputy/multi-actor crystallisation | Future target-state transition |

**S5 open items / deferrals** *(source: S5 exit §10.1)*:

1. Role-breakdown pd instantiation (template ready; numbers slot in without new S-cycle).
2. MAS TRM control-number-level mapping (domain-level done; control-level → E4).
3. Attention-intensity realised-fraction monitoring (proof-risk surface; post-MVGH sharpening).
4. Secondary-instrumentation Layer 2 wiring within 3–4w cap (3 metrics in MVGH; 4 post-MVGH).
5. S4 §8 nine open-items inherited unchanged.

### 8.2 E-skill inputs (where each E-skill picks up)

- **E1 Problem Definition** — this Solution Brief is the primary input. **E1's opening task is to source or produce the 163-pd MAS-TRM scope statement as the first Direction Capture knowledge contribution.** The 163-pd figure is the baseline size; the scope content (statement, target, architecture posture, principal artefacts, role breakdown) is E1's first concrete production. Telco NOC first-target-bias per S1 §6 applies.
- **E2 Requirements** — specific scope requirements per engagement; proof-structure ties to 5 primary metrics; confirms methodology selection (gate-based likely for MAS TRM) and binds orchestration-layer configuration.
- **E3 Architecture** — inherits 4 items (1, 3, 6, 9 in §8.1 above — AG9a-3 rollback, AG9d-3 role-weighting, AG-5b per-type, AG3-2 alternative); designs detailed architecture for MVGH-β 15-element set.
- **E4 Security and Compliance** — inherits T12 key-lifecycle (item 4) + MAS TRM control-number-level mapping (S5 item 2).
- **E5 Data** — inherits AG-5b per-theory-type variants (item 6, shared with E3).
- **E6 Build** — consumes E3 architecture; implements Wave 1/2/3 substrate.
- **E7 Test** — includes adversarial-challenge instrumentation; exercises dual-layer AG-2/AG-3 enforcement.
- **E8 Deployment** — base cycle; no MVGH-specific inheritance beyond generic E-skill envelope.
- **E9 Operations** — inherits M9c-3 activation instrumentation (item 2) + reconcile-window monitoring (item 8).
- **E10 Feedback and Learning** — exercises full 4 secondary-instrumentation metrics deferred post-MVGH; closes theory-retirement loop via AG-5b tombstones.

### 8.3 Deferred register (17 items, §3.2 above)

Each item has explicit activation trigger and structural-preservation mechanism. Full register in §3.2.

## 9. Dogfooding note

*(Source: S5 exit §9 CARRY-FWD-4; S5 opening-prompt knowledge-contribution.)*

**CARRY-FWD-4 explicit claim:** MVGH setup work is conducted without the 4WRD governance harness. This is the last substantial delivery that will not be 4WRD-governed. First fully governed delivery begins at E1 of the first client-scope SDLC cycle.

**What the S1–S4 work is and is not:**
- **Is:** partial evidence that the governance model operates. The S1–S4 cycle work exercised Intent Cycle moments (Direction / Production / Verification / Close), convergence-state discipline (Explorative / Targeted / Exact), DISCIPLINE-1/2/3 consistently, adversarial challenge at every production, primary derivation intent declaration, and tombstone-equivalent exit artefacts (ratified exit-artefact files persisted under version control with `[S<n>]` commit prefixes). Frame Change Sidecar Detector operated informally via adversarial conversation in S1–S4 — adversarial moments surfaced frame-change-adjacent issues (e.g., setup-week corrections, catalog-completion-gap flags) through dialogue rather than structural Tier 2 interrupt. These are structural components of the governance surface operating on harness-design work.
- **Is not:** full 4WRD-governance. No HMAC-chain Layer-1 recording, no Layer-3 context-package auto-generation, no structural Frame Change Sidecar Detector (the structural Detector — Tier 2 interrupt + session-boundary scan — is a Wave 1 MVGH-β element, not present during S1–S4), no AG-2 pre-commit hook enforcement, no AG-3 schema-validator chain, no AG-5b tombstone emission-on-retirement. The S1–S4 work is cycle-primitive-only + adversarial-dialogue-only + version-controlled exit artefacts.

**Honesty statement for stakeholders:** when 4WRD is demonstrated to a stakeholder, the S1–S4 chain can be cited as evidence of cycle-primitive operation across 5 convergence-state acts with explicit ratification. It cannot be cited as evidence of full-harness operation. The first full-harness evidence is produced during the first governed client-scope SDLC cycle — the MVGH proof itself.

## 10. Ratification corrections (back-propagation)

Recorded during S6 Targeted synthesis. These corrections bind the Brief and are applied retroactively to the cited upstream artefact:

- **S5 §5b "Claude Code" → "Claude Agent SDK":** S5 Targeted Act 2 client proof statement used "Claude Code personas" in one location. The ratified implementation target per INPUT-001 §9 and throughout S1–S5 is Claude Agent SDK. The Brief standardises on Claude Agent SDK throughout. The S5 §5b prior phrasing is superseded by Brief §4.5, which carries the authoritative client proof statement wording.

No other corrections identified at S6 Exact ratification.

---

*End of 4WRD Solution Brief (S6 Exact).*
