# S4 — Option Evaluation — Exit Artefact

## 0. Status

**Convergence state at exit:** Exact. Ratified.
**Primary derivation intent:** docs/s3-exit-artefact.md; docs/s2-exit-artefact.md; INPUT-001 §§2.2, 4, 7, 8, 9, 10, 11; CARRY-FWD-1, CARRY-FWD-2, CARRY-FWD-3.
**Contributing cycles:** S4.1 Explorative (DEC-D5 Wave 0), S4.2 Wave 1 multi-act (Acts 1–4 storage/schema/coordination/joint-close), S4.3 Wave 2 (Acts 1–4 AG-7a/AG-9d/AG-9a+AG-9c-fuller/close), S4.4 Wave 3 (Acts 1–5 AG-6b/AG-5b+AG-9e/AG-2+AG-8/AG-3/close+catalog).

## 1. Scope and non-scope

**In scope:** Three-wave option evaluation, ratified stack, coupling catalog honour-check (21 CPs), B5 schema addition catalog, named architectural constraints, delivery envelope, S5 inheritance surface.
**Out of scope:** Solution selection (deferred to S5); implementation (E1–E10); client engagement specifics; S5 scope-posture decision (framed, not resolved).

## 2. Ratified three-wave stack

### 2.1 Wave 0 — DEC-D5 (S4.1)

- **D5-1 IP ownership:** O1-D layered ownership.
- **D5-2 sharing model:** O2-B vendor-curated abstraction.
- **D5-3 pricing unit:** O3-D tiered subscription on per-cycle substrate.

Commercial anchor ratified: **{O1-D, O2-B, O3-D}**. SEAM-5 elevated at this ratification.

### 2.2 Wave 1 — Pivot cluster (S4.2)

- **AG-4 storage axis:** **A2-now / A8-target** (per-actor HMAC chains; A8 target-state path conditional on Act-2 schema satisfying T-1).
- **AG-4 schema axis:** **B1 master anchor** + **B5 chain entry schema** (additive-compatible forward policy ratified).
- **AG-4 T10-path:** **C2 custom-light** (minimal infrastructure, §9 messaging direct).
- **AG-9b messaging (M9b):** **M9b-5** §9-direct.
- **AG-9c coherence (M9c):** **M9c-2 write-through + M9c-7 periodic reconcile** (active pair).
- **AG-9f handover (M9f):** **M9f-3** with erasure-hook.
- **Composite TI:** **TI-C4** (= M9b-5 identity per S3.1 authoritative note).

**Target-state preserved alternative:** fully-vendored {A7, B4, C3} pair viable under D3-pressure or CA-class concentration accepted.

Wave 1 setup: **≈15w ±3w** (≈12–18w).

### 2.3 Wave 2 — Identity + quorum + concurrency + coherence (S4.3)

- **AG-7a identity + joint-act:** **AG7-i HMAC per-actor identity + AG7-iii composite role-class binding + AG7-b chain-join joint-act locus**.
- **AG-9d quorum:** **AG9d-1 (small-N target N ≤ 3) + AG9d-2 (larger-N target) + AG9d-5 (tiered override-path shell)**; shell schema-gated dormant via override-flag enum.
- **AG-9a concurrency:** **AG9a-3** (per-actor serial + cross-actor parallel + anchor optimistic reconcile via M9c-7).
- **AG-9c-fuller coherence:** **{M9c-2 + M9c-7 active; M9c-3 quorum-commit defined-but-dormant}** — activation gated on post-deployment joint-act-rhythm signal.

Wave 2 setup: **≈8–12w**.

### 2.4 Wave 3 — Downstream primary choices (S4.4)

- **AG-6b override-authority:** **AG6b-1 current-state (structurally-only-available: sole orchestrator) + AG6b-3 target-state activation path** (role-gated via AG7-iii role-class enum). AG6b-2 degenerate-intermediate preserved; AG6b-4 quorum-gated viable alternative preserved.
- **AG-5b theory retirement:** **AG5b-4 hybrid inline + master-anchor index**; ownership-tier-preserving retirement; per-theory-type variants (7 types per INPUT-001 §8) deferred to E3/E5 incremental.
- **AG-9e dynamic role-assignment:** **AG9e-5 composition pattern** — AG9e-1 Orchestrator-gated normal-class default + AG9e-3 quorum-gated upgrade path + AG9e-2 human-gated forced for override-class.
- **AG-2 artefact-boundary enforcement:** **AG2-4 dual-layer** — pre-commit hook (LRN-010 carry-forward) + schema validator at B5 write-time; hook presence-check + schema full-verify on OVERRIDE.
- **AG-8 artefact registration:** **AG8-5 hybrid inline + master-anchor index**; shared query surface with AG5b-4 via composite-status primitive.
- **AG-3 write-time validation:** **AG3-3 layered validator chain** on LRN-005 scaffold; three rule-families (ownership-tier → registration-required → tombstone-on-removal) with override-aware bypass policy per rule-family.

Wave 3 setup: **≈16–27w** (lower: mechanism delivery with per-type variants deferred; upper: full per-type tombstone variants included).

## 3. Filter outcomes at S4 exit

### 3.1 §9 multi-session filter

- Ratified options all **Compatible** or Compatible-via-composition; no Tension-class option selected.
- Friction-class options (e.g., AG5b-1 inline-only, AG8-1 inline-only, AG9d-4 override-bypass, AG6b-5 time-bounded overlay) evaluated and either not selected or preserved as overlay/alternative.
- Strong-alignment reframe (S3.2) preserved: classification refinement within Compatible, not selection signal.

### 3.2 CF-2 Anthropic-concentration filter

- **All ratified options CN** (Concentration-Neutral).
- **CA and CAmp classes empty** across ratified stack (carry-forward landscape observation from S3.3).
- **Baseline CF-2 concentration accepted** by ratified stack; marginal-DIV not actively pursued (per S3 deferral and DISCIPLINE-2 neutral framing).

## 4. Coupling catalog at S4 exit — 21-CP honour-check

[DISCIPLINE-1: 21 CPs per S3 §4 final distribution H-7, M-3, O-8, S-3, U-0. CP-13 dual-aspect (O-type slice + M-type broader) counted once in each type-bucket per S3 §4 authoritative scope note.]

### 4.1 H-type (7) — Hard upstream

| CP | Scope | Status at S4 exit |
|----|-------|-------------------|
| CP-1 | (Wave 1 internal) | Honoured (Wave 1 CLOSE) |
| CP-2 | (Wave 1 internal) | Honoured (Wave 1 CLOSE) |
| CP-3 | (Wave 1 internal) | Honoured (Wave 1 CLOSE) |
| CP-8 | AG-7a → AG-9d | Honoured-active (Wave 2 Acts 1–2) |
| CP-9 | AG-9d → AG-9c | Honoured-by-non-activation (Wave 2 Act 3; M9c-3 dormant) |
| CP-11 | (Wave 1 internal) | Honoured (Wave 1 CLOSE) |
| CP-18 | (Wave 1 internal) | Honoured (Wave 1 CLOSE) |

### 4.2 M-type (3) — Mutual co-design

| CP | Scope | Status at S4 exit |
|----|-------|-------------------|
| CP-12 | (Wave 1 + Wave 3 AG-8) | Partial-honoured |
| CP-13 (broader) | AG-2 / AG-6b broader governance | Not-triggered (slice O-type Honoured — see §4.3) |
| CP-15 | SEAM-1a / DEC-INV pending | Not-triggered |

### 4.3 O-type (8) — Option-constraining

| CP | Scope | Status at S4 exit |
|----|-------|-------------------|
| CP-5 | (Wave 1 internal) | Honoured (Wave 1 CLOSE) |
| CP-6 | (Wave 1 internal) | Honoured (Wave 1 CLOSE) |
| CP-7 | (constrained M9f option) | Not-triggered (M9f-3 selected) |
| CP-10 | (Wave 2 option-constraint) | Not-triggered |
| CP-13 (slice) | Artefact-boundary slice AG-2 ↔ AG-6b | Honoured (Wave 3 Act 3) |
| CP-17 | (Wave 3 O-edge) | Honoured-active (Wave 3) |
| CP-20 | AG-5b ↔ AG-9e | Honoured-active (Wave 3 Act 2) |
| CP-21 | AG-6b ↔ AG-9d | Honoured-by-non-activation (current-state); Honoured-active path on AG6b-3 activation (Wave 3 Act 1) |

### 4.4 S-type (3) — Shared mechanism

| CP | Scope | Status at S4 exit |
|----|-------|-------------------|
| CP-4 | (Wave 1 shared substrate) | Honoured (Wave 1 CLOSE) |
| CP-14 | (Wave 1 shared substrate) | Honoured (Wave 1 CLOSE) |
| CP-19 | {M9b-5, M9f-3, CA5} shared §9 substrate | Not-triggered (reclassified U→S at Wave 1 CLOSE; M9c-3 dormant; re-evaluates on M9c-3 activation) |

### 4.5 U-type (0)

**Zero Unverified CPs at S4 exit.** CP-19 U→S reclassification at Wave 1 CLOSE closed last U-type.

### 4.6 Catalog summary

- **Honoured / Honoured-active:** 14 CPs.
- **Honoured-by-non-activation:** 2 CPs (CP-9, CP-21 current-state).
- **Partial-honoured:** 1 CP (CP-12).
- **Not-triggered (distinct):** 4 CPs (CP-7, CP-10, CP-15, CP-19).
- **Dual-aspect:** 1 CP (CP-13 broader Not-triggered, slice Honoured).

**Total: 21 distinct CPs accounted for; zero open.**

## 5. B5 schema addition catalog

8 additive schema additions across Waves 2 and 3; all additive-compatible per B1 Wave 1 CLOSE forward-compatibility policy.

| # | Addition | Wave/Act | Status |
|---|----------|----------|--------|
| 1 | AG7-b joint-act node type | Wave 2 Act 1 | Emit-able |
| 2 | override-flag enum (NORMAL \| OVERRIDE) | Wave 2 Act 2 | Emit-able with OVERRIDE path schema-gated until AG-6b activation |
| 3 | quorum-commit entry type (M9c-3 shell) | Wave 2 Act 3 | Dormant — schema-gated until post-deployment activation signal |
| 4 | rollback-entry type | Wave 2 Act 3 | Deferred — specification at E3 |
| 5 | role-assignment node type | Wave 3 Act 2 | Emit-able; ownership-tier field mandatory |
| 6 | tombstone node type | Wave 3 Act 2 | Emit-able (common schema); per-type variants deferred to E3/E5 |
| 7 | registration node type | Wave 3 Act 3 | Emit-able; shared master-anchor index with tombstone |
| 8 | rejection-event node type | Wave 3 Act 4 | Emit-able — LRN-003 explicit-failure operationalisation |

**5 active + 3 dormant-or-deferred.** All pre-provisioned at schema layer.

## 6. Named architectural constraints

- **SEAM-1** — Invariant special-class evolution (carry-forward from S1).
- **SEAM-1a** — Invariant-set initial instantiation (carry-forward).
- **SEAM-2** — Citation rule (carry-forward).
- **SEAM-2a** — Recursion depth for meta-governance closure (carry-forward).
- **SEAM-2 procedural** — Citation procedural (carry-forward).
- **SEAM-5** — Abstraction/instantiation ownership-tier boundary. Elevated at S4.1 with O2-B commercial anchor. Ownership-tier tag on every B5 entry; cross-tier writes rejected at validation.
- **Override-authority-human-only** — Override is a human primitive per INPUT-001 §7 Principle 5. AI actors may not hold override authority. Deputy must be human. (Named at Wave 3 Act 1 verification.)
- **Override-respects-ownership-tier** — Override-authority bounded by SEAM-5. Cross-tier modifications require vendor-tier authority. Human orchestrators operate within user-tier scope only. (Named at Wave 3 Act 4 verification; SEAM-5 reaffirmation.)
- **Registration-emission reconcile-window** — Under AG9a-3, cross-actor registration-to-emission requires minimum one M9c-7 reconcile-window gap. Same-actor registration-to-emission is immediate. (Named at Wave 3 Act 4 verification; operational property, surfaces at E9.)
- **Dual-layer enforcement responsibility split** — AG-2 pre-commit hook performs presence-check; AG-3 schema validator performs full identity + role-class + human-actor-set verification on OVERRIDE entries. (Named at Wave 3 Act 3 verification.)

## 7a. Setup estimate (ratified)

| Wave | Range |
|------|-------|
| Wave 1 | ≈12–18w (15 ±3w) |
| Wave 2 | ≈8–12w |
| Wave 3 | ≈16–27w (lower: mechanism only; upper: full per-type tombstone variants) |
| **Setup total** | **≈36–57w** |

Setup-weeks are per-act ratified at cycle close; consolidated here.

## 7b. SDLC projection and elapsed-time overlay (preliminary)

**SDLC projection (E1–E10 post-setup, preliminary — E-skills not cycle-processed):**

| Skill | Estimate | Notes |
|-------|----------|-------|
| E1 Problem Definition | largely delivered via S1/S2 cycle inheritance | |
| E2 Requirements | ≈2–4w | per delivery scope |
| E3 Architecture | ≈6–10w | includes AG9a-3 rollback, AG9d-3 weighting policy, AG-5b per-type variants initial |
| E4 Security and Compliance | ≈4–6w | includes T12 key-lifecycle |
| E5 Data | ≈3–5w | |
| E6 Build | ≈6–10w | |
| E7 Test | ≈4–6w | |
| E8 Deployment | ≈2–4w | |
| E9 Operations | ≈2–4w | includes M9c-3 activation instrumentation, reconcile-window monitoring |
| E10 Feedback and Learning | ≈2–4w | |
| **SDLC total (preliminary)** | **≈31–53w** | |

**Elapsed-time overlay:** solo-founder attention-bound per S2 operational input. Linear setup-weeks + SDLC-weeks assume single-track dedicated work. Realistic elapsed-time multiplier 1.5x–2x for context-switching, dogfooding overhead, other commitments. **Preliminary elapsed-time envelope: ≈23–50 months.**

**Scope-posture framing (neutral per DISCIPLINE-2):** full-target-state path and current-state-first path are both structurally preserved in ratified stack via defined-but-dormant and activation-gated patterns. Scope-posture decision is S5 inheritance.

## 8. Open items by locus

| # | Item | Locus |
|---|------|-------|
| 1 | AG9a-3 rollback-entry semantics for failed-quorum joint-acts | E3 |
| 2 | M9c-3 activation signal (joint-act frequency instrumentation) | Harness runtime / Layer 2 / operator decision |
| 3 | AG9d-3 role-weighting policy | E3 |
| 4 | T12 key-lifecycle (rotation, revocation) | E4 |
| 5 | AG-9c-fuller revisit if M9c-3 activates | Post-activation signal |
| 6 | AG-5b per-theory-type tombstone variants (7 types) | E3/E5 incremental |
| 7 | AG3-2 policy-as-code rule engine alternative (if rule-family count grows) | Future S-cycle or E-skill |
| 8 | Registration-emission reconcile-window constraint | E9 Operations |
| 9 | AG6b-3 target-state activation on deputy/multi-actor crystallisation | Future target-state transition |

## 9. Carry-forwards and Disciplines

**Carry-forwards:**
- **CARRY-FWD-1** — Need 13 partial technical-constraint readiness (from S1).
- **CARRY-FWD-2** — Anthropic platform concentration (from S2; CF-2 filter at S3.3; S4 outcome: all ratified options CN; baseline accepted).
- **CARRY-FWD-3** — C4 capacity binding constraint (from S2; sequencing input, not filter; preserved at S3.6 verification).

**Disciplines (inherited; none added at S4):**
- **DISCIPLINE-1** — source-of-count tagging.
- **DISCIPLINE-2** — convergence-state transition preferences not expressed by AI.
- **DISCIPLINE-3** — qualitative classification cites criterion.

## 10. S5 inheritance surface

S5 Solution Selection inherits at Targeted entry:

1. **Ratified three-wave stack** (§2) across three timelines:
   - Current-state operational (solo orchestrator, single-actor, dormant target-state paths).
   - Target-state activation path (multi-actor, override-class role, quorum, M9c-3 when joint-act rhythm signals).
   - E-skill deferrals (6 deferred items per §8 locus distribution).
2. **Filter outcomes** (§3) — §9 all Compatible; CF-2 all CN with baseline accepted; no marginal-DIV active pursuit.
3. **Coupling catalog** (§4) — 21 CPs; zero open; status-class summary.
4. **B5 schema addition catalog** (§5) — 8 additions, 5 active + 3 dormant-or-deferred.
5. **Named architectural constraints** (§6) — 10 constraints spanning SEAMs, override discipline, dual-layer enforcement, operational property.
6. **Delivery envelope** (§7a ratified + §7b preliminary) — setup ≈36–57w; SDLC ≈31–53w preliminary; elapsed ≈23–50 months; preliminary envelope not commitment.
7. **Scope-posture decision explicitly on S5 surface** — full-target-state vs current-state-first staging. Both paths preserved structurally in ratified stack.
8. **Open items (§8)** — 9 items by locus; S5 aware of downstream distribution.
9. **Seams inherited** (§6) — no new seams at S4.
10. **Disciplines inherited** (§9) — carry-forward only.

---

*End of S4 exit artefact.*
