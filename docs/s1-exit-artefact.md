# 4WRD — S1 Exit Artefact

**Problem Crystallisation — Consolidated Input to S2 (Context and Constraint Mapping)**

- **Status:** Ratified at Exact. Primary input to S2.
- **Date:** 2026-04-17
- **Ratification chain:** S2.1 → S2.2 → S2.3 → S2.4 (Explorative); Targeted Axis-3 readiness; Targeted Axis-1/2 readiness; Exact convergence.

---

## 1. Problem Statement (solution-neutral)

Teams adopting AI in delivery have acquired production capacity without acquiring a governance surface over that production — one that is addressable, auditable, adversarially-challenged, multi-actor, composable, and evolvable under its own governance. Such a surface must govern three dimensions simultaneously: delivery production, coordination across multiple humans and multiple agents, and the harness's own evolution — including bounded retirement of theory that no longer serves (with tombstones, not gaps), explicit invariants on what cannot be retired, and closure that prevents meta-governance regress. No existing AI-in-delivery governance framework provides this natively.

---

## 2. Three-Axis Need Structure

### Axis 1 — Governance OVER delivery production (8 needs)

1. **Direction addressability** — AI production must be traceable to a declared human direction that is later queryable. *Mech:* Intent Cycle.
2. **Structural output critique** — AI output must be subject to a critique moment that is not optional. *Mech:* Adversarial AI role as required cycle moment.
3. **Direction revisability** — When direction itself is wrong, the system must distinguish this from output-wrong and handle it differently. *Mech:* Frame Change Sidecar.
4. **Artefact provenance** — Every produced artefact must carry a tamper-evident chain back through verification, critique, reasoning, direction. *Mech:* Artefact Lineage.
5. **Context integrity** — Each actor's view of context must be refreshed by construction, not by convention. *Mech:* Structurally-generated context packages per role per cycle.
6. **Policy enforcement** — Policy must be machine-enforced at production boundaries, not checklist-trusted. *Mech:* Schema validation, pre-commit gates, hook self-checks.
7. **Act attribution** — Every act by any actor must be attributable and tamper-evident. *Mech:* Per-actor HMAC chains anchored to a master audit chain.
8. **Composition across scale** — Reusable assets must stack from general to specific without re-implementation. *Mech:* Domain → Specialisation → Skill → Persona.

### Axis 2 — Governance ACROSS actors (1 need, load-bearing structural bet)

9. **Multi-actor coordination** — Multi-human × multi-agent delivery must be a native primitive; direction, critique, verification, and accountability must remain coherent when humans and agents each exceed one. *Mech:* Three agents as persona families + orchestration roles + per-actor audit chains.

### Axis 3 — Governance OF the harness itself (5 needs, evolvable under its own governance)

10. **Learning retention** — Each cycle's learnings must be addressable as durable artefacts, bound to the cycle that produced them, and structurally injected into subsequent cycles at defined injection points (examples illustrating the shape of the content — not a shortlist: direction formation, context package generation, adversarial prompting. Concrete content defined in implementation). Documentation without injection is not retention. *Mech:* Feedback Loop pattern, E10 Feedback and Learning skill.

11. **Theory retirement with tombstones** — The harness must be able to prune its own theory — where *theory* comprises skills, rules, learnings, registers, artefacts, schemas, personas, and any other harness-authored structure — and retirement acts must produce a tombstone: a durable, addressable marker recording at minimum (a) identity of the retired theory, (b) cycle in which retirement was enacted, (c) reason for retirement, (d) any successor reference. The tombstone is itself a harness artefact, subject to governance. Absence is not retirement; silent removal is prohibited. *Mech:* Not yet designed — first-class open question for implementation.

12. **Invariance** — The harness must declare an invariant set — structural properties that must hold across any evolution — specifying for each invariant: (a) identity, (b) enforcement locus (design-time schema, runtime hook, audit check, or combination), and (c) rationale. Candidate invariants (examples illustrating the shape of the content — not a shortlist; concrete set defined in implementation): cycle structure with adversarial moment, artefact lineage, direction-before-production, retirement recording. The process by which the invariant set itself is evolved is governed by SEAM-1 and out of scope for this need. *Mech:* Not yet designed — first-class open question for implementation.

13. **Meta-governance closure** — Governance of harness evolution must not require a governance system separate from the one governing production. Structural claim: the Intent Cycle is applied recursively to harness-as-artefact. Meta-cycles are distinguishable from production-cycles by an explicit mechanism — tagging, subject metadata, or equivalent — to be defined in implementation. This permits role assignments, audit scoping, and constraint application to differ while keeping the primitive unified. This need remains a load-bearing structural commitment; if recursive application proves unworkable, Axis 3 falls. *Structural claim (not an open implementation question):* Intent Cycle applied recursively to harness-as-artefact.

14. **Retirement candidate surfacing** — The harness must compute and surface retirement candidates — harness-authored structures meeting declared decay criteria — at defined cycle moments. Candidate decay signals (examples illustrating the shape of the content — not a shortlist): skill non-invocation beyond threshold, rule contradiction frequency, artefact staleness, learning override rate. Candidate surfacing moments (examples illustrating the shape of the content — not a shortlist): cycle-opening context package, periodic orchestrator review, pre-evolution gate. Surfacing is observational; it must not trigger retirement. Retirement remains a deliberate orchestrator act via the cycle primitive. Signal set and surfacing cadence defined in implementation. *Mech:* Not yet designed — first-class open question for implementation.

---

## 3. Three-Axis Prevention Gaps

### Axis 1 — production governance gaps (8)

1. Direction vanishes — prompts persist mechanically but not semantically; no query surface for "what was directed, critiqued, verified."
2. Critique is ad-hoc or sycophantic — models default to agreement; humans lack a structural counter-discipline.
3. Frame change is social, not procedural — teams iterate outputs when direction itself is wrong, burning cycles.
4. AI artefacts have no traceable provenance — audit is forensic, not native.
5. Context is re-approximated each session — drift is invisible until contradiction surfaces.
6. Governance is aspirational — compliance, quality, security gates live as checklists, not enforced moments.
7. Attribution is log-scraping — no per-actor tamper-evident chain across humans and agents.
8. Skills are ad-hoc prompts re-invented per developer — no stacking from general to specific.

### Axis 2 — coordination gap (1)

9. Existing tools collapse n humans × m agents into a single conversation thread; multi-actor is a bolt-on, not a primitive.

### Axis 3 — self-evolution gaps (6)

10. Retros produce documents, not structural changes to the next cycle's production.
11. Existing AI-in-delivery governance frameworks accumulate theory indefinitely — no retirement mechanism, so they bloat over time and become the overhead they were designed to replace. *(Scoped: claim applies to AI-in-delivery governance frameworks specifically.)*
12. **Theory retirement failure modes:** skill sprawl (skills added but never removed); contradictory rules (rules accumulate without reconciliation, precedence becomes folklore); audit chains carry provenance for retired decisions (audit remains "complete" but cluttered; forensic value degrades).
13. **Invariance gap:** AI-in-delivery frameworks typically have rigid invariants (brittle, block evolution) or no invariants (unbounded evolution, including erosion of trustworthiness). Teams lack a structural way to declare bounds.
14. **Meta-governance regress or absence:** teams typically assume human oversight is sufficient (informal, non-auditable), build a second governance layer (regress), or ignore the problem. No cycle-primitive approach is standard.
15. **Retirement is passive:** decay signals (skills unused, rules contradicted, artefacts stale) are visible in principle but not structurally surfaced. Overhaul-level refactor becomes inevitable because incremental retirement never triggers.

---

## 4. Acceptable-Gap Register (tagged)

Each READY verdict from Targeted cycles carries a visible gap. S2 inherits the gap list, not just the readiness verdicts.

**Inheritance rules:**

- **Architectural (A)** gaps: first-class S2 inheritance. S2 must treat these as constraint-mapping surface to address, not defer.
- **Implementation-detail (I)** gaps: deferred to build time. Do not consume S2 constraint-mapping capacity.

**Register — counted from entries below: 13 architectural + 4 implementation-detail = 17 entries.**

| ID | Need | Content | Tag |
|---|---|---|---|
| AG-1 | N1 — Direction addressability | direction schema; query surface keys | I |
| AG-2 | N2 — Structural output critique | critique artefact form; enforcement locus for non-optionality | A |
| AG-3 | N3 — Direction revisability | differential handling semantics under frame change | A |
| AG-4 | N4 — Artefact provenance | provenance storage model; query surface; cross-tenant isolation | A |
| AG-5a | N5 — Context integrity | context package schema | I |
| AG-5b | N5 — Context integrity | deterministic composition rules; input selection logic | A |
| AG-6a | N6 — Policy enforcement | policy expression language | I |
| AG-6b | N6 — Policy enforcement | exception / override semantics | A |
| AG-7a | N7 — Act attribution | actor identity granularity; joint-act semantics | A |
| AG-7b | N7 — Act attribution | key lifecycle | I |
| AG-8 | N8 — Composition across scale | composition algebra; cross-tenant sharing/visibility | A |
| AG-9a | N9 — Multi-actor coordination | concurrency model | A |
| AG-9b | N9 — Multi-actor coordination | actor-to-actor communication protocol | A |
| AG-9c | N9 — Multi-actor coordination | coherence mechanisms (locking, ordering, state reconciliation) | A |
| AG-9d | N9 — Multi-actor coordination | quorum / consensus semantics | A |
| AG-9e | N9 — Multi-actor coordination | role-assignment model (static vs per-cycle) | A |
| AG-9f | N9 — Multi-actor coordination | handover protocol between actors | A |

---

## 5. Carry-Forward Seams and Disciplines

### Seams (design questions carried forward for future cycles)

- **SEAM-1** — Invariant changes are special-class evolution acts requiring higher bar / more scrutiny / potentially super-majority orchestrator action. Exact mechanism is downstream design work.
- **SEAM-1a** — *Invariant-set initial instantiation.* Who authors and ratifies the initial invariant set at harness bootstrap, and whether this uses the same higher-bar process as SEAM-1 or is separate. Surfaced during Targeted analysis of Need 12.
- **SEAM-2a** — *Recursion depth for meta-governance closure.* Whether meta-of-meta cycles are supported, reserved for escalation, or prohibited. Surfaced during Targeted analysis of Need 13.
- **CARRY-FWD-1** — Need 13's S2-readiness is partial at the technical-constraint dimension until the distinguishing mechanism (tagging / subject metadata / equivalent) is chosen. S2 must produce a constraint-mapping that flags this as a downstream implementation dependency.
- **SEAM-2 procedural (with citation rule)** — Axis 1 / Axis 2 full Explorative articulation is canonical in S2.3. This S1-exit artefact is the ratified convergence document. **Citation rule (PROCEDURAL-3):** future cycles cite this S1-exit artefact for S2-ready articulations; cite S2.3 for Explorative-phase provenance.

### Disciplines (conventions carried forward)

- **DISCIPLINE-1** — Numerical claims in convergence artefacts must be tagged with source-of-count (e.g., "counted from register above: 13 A + 4 I"). Applies to both Producing AI and Adversarial AI production, and to human verification acts. Recorded because the human is decider not checker; adversarial counter-discipline applies even post-signoff. Origin: open correction of a prior-cycle miscount during Exact convergence.

### Procedural rules (carried forward for downstream phases)

- **PROCEDURAL-2** — During S2 constraint-mapping, if any A-tagged gap proves to be implementation-detail rather than architectural, S2 re-tags it as I and reports the re-tagging as a discipline note. The reverse move (I → A) is also permitted if a gap proves architecturally load-bearing during mapping. Tag drift is expected and should be visible.

---

## 6. First-Target Bias Acknowledgement (Telco NOC)

The first live test target is Telco NOC delivery — audit-heavy, incident-driven, high-consequence. This biases the harness toward emphasising audit-immutability (Need 7), policy enforcement (Need 6), and artefact provenance (Need 4). Properties that may be load-bearing for exploratory or creative delivery — speed of theory addition, flexibility of frame change (Need 3), tolerance for informal critique (Need 2) — are under-pressured by this first target.

**Action for S2 and downstream:** the crystallisation generalises beyond Telco NOC; implementation must verify that design choices are not silently NOC-specific. Where NOC-specific framing is discovered, S2 or a subsequent phase must surface it as a bias-flagged design decision, not absorb it as default.

---

## 7. Convergence Test — Does Gap Tagging Bound the Permissiveness Concern?

**Test:** Would any architectural gap have been caught as REFINE under the strict bar? If yes, does it now receive appropriate first-class treatment in S2 inheritance?

| Gap | Would-be-REFINE under strict bar? | Tagged A + inherited first-class? | Bounds concern? |
|---|---|---|---|
| AG-2 | Yes (critique artefact form unspecified; non-optionality enforcement locus unspecified) | Yes | ✓ |
| AG-3 | Yes ("handle differently" unoperationalised) | Yes | ✓ |
| AG-4 | Yes (storage/query/isolation all affect regulatory + commercial mapping) | Yes | ✓ |
| AG-5b | Yes (composition rules load-bearing for regulated-data inclusion) | Yes | ✓ |
| AG-6b | Yes (exception semantics affect regulatory compliance mapping) | Yes | ✓ |
| AG-7a | Yes (actor identity model load-bearing for non-repudiation + multi-actor) | Yes | ✓ |
| AG-8 | Yes (composition algebra affects per-layer cascade; sharing affects IP) | Yes | ✓ |
| AG-9a | Yes (concurrency fundamentally unspecified) | Yes | ✓ |
| AG-9b | Yes | Yes | ✓ |
| AG-9c | Yes | Yes | ✓ |
| AG-9d | Yes | Yes | ✓ |
| AG-9e | Yes | Yes | ✓ |
| AG-9f | Yes | Yes | ✓ |

**Result — convergence test PASSES.** All 13 architectural gaps that would have been REFINE under strict bar are preserved as first-class A-tagged S2 inheritance. The permissiveness concern from the prior Targeted cycle is bounded: strict-bar REFINE concerns are not lost; they are structurally preserved as architectural inheritance rather than cycle-level REFINE verdicts.

**Treatment of I-tagged gaps:** 4 I gaps (AG-1 schema, AG-5a schema, AG-6a expression language, AG-7b key lifecycle) are genuinely implementation-detail — downstream from architecture and appropriately deferred to build time. Under strict bar these might have generated REFINE verdicts, but those REFINEs would have been over-caution rather than substantive architectural concern.

---

**S1 CLOSED. S2 OPEN with this artefact as primary input.**
