# S2 Opening Prompt — Draft

**Status:** Pre-staged draft. Refine in your own voice before pasting to Claude Code.
**When to paste:** At the start of your next focused Claude Code session, after S1 persistence and commits are confirmed.

---

## Suggested opening

```
CYCLE START
CONVERGENCE STATE: Explorative
DIRECTION: Produce a first-pass map of the constraint landscape 
  that S2 will need to navigate for the full S1 gap register. Do 
  NOT yet map constraints against individual gaps. Produce:
  1. A taxonomy of constraint dimensions relevant to 4WRD 
     (regulatory, technical, organisational, commercial, 
     operational — candidates only, to be refined)
  2. For each dimension, a first-pass list of likely constraint 
     sources given the 4WRD context
  3. An initial scoping assessment — which of the thirteen 
     architectural gaps are most constrained by which dimensions? 
     This is a rough heat-map, not a mapping.

KNOWLEDGE CONTRIBUTION:
  - 4WRD implementation target: Anthropic Managed Agents 
    (single-vendor infrastructure, beta-tier with some features 
    in research preview — multi-agent orchestration and memory 
    tooling are in research preview, not public beta)
  - First live test target: Telco NOC delivery (audit-heavy, 
    incident-driven, high-consequence)
  - Secondary targets: Singapore fintech (MAS TRM), critical 
    infrastructure (CCoP 2.0), government (PDPA, Cybersecurity 
    Act 2018), aviation (CAAS/ICAO), Cyber Trust Mark
  - Orchestration model: Bhushan as sole human orchestrator, 
    second-in-command vacant
  - Commercial context: Bhushan solo founder. Building 4WRD 
    using 4WRD (dogfooding). Managed Agents chosen for speed 
    to first live test.
  - The thirteen architectural gaps from S1 exit artefact are 
    the primary mapping target, but the first cycle scopes the 
    landscape rather than mapping individual gaps.

PRIMARY DERIVATION INTENT: 
  docs/s1-exit-artefact.md (ratified S1 output)
  docs/foundation/INPUT-001-foundation-v4.md
  docs/foundation/INPUT-002-composition-trace.md
  docs/foundation/INPUT-003-operating-brief.md
```

---

## Points to refine in your own voice

- The knowledge contribution is in my words. Rewrite in yours. In particular:
  - The secondary targets list may need to be expanded or narrowed based on your actual commercial pipeline.
  - Commercial context — add anything about current client conversations or revenue pressure if relevant.
  - Orchestration model — if you have identified a second-in-command candidate, add it.

- The direction scopes the first cycle as landscape, not mapping. If your instinct is different — if you want to start with a specific high-risk gap like AG-9a (concurrency) — say so and rewrite the direction accordingly.

- If you want S2 to start with a specific first-target focus (Telco NOC constraints specifically, rather than all targets simultaneously), narrow the direction.

---

## Carry-forwards to flag to Claude Code at S2 start

From S1 close, S2 inherits:

**Seams:**
- SEAM-1 — Invariant special-class evolution
- SEAM-1a — Invariant-set initial instantiation  
- SEAM-2a — Recursion depth for meta-governance closure
- CARRY-FWD-1 — Need 13 partial technical-constraint readiness
- SEAM-2 procedural — Citation rule: cite s1-exit-artefact for S2-ready articulations; cite S2.3 provenance for Explorative-phase

**Discipline rules:**
- DISCIPLINE-1 — Source-of-count tagging for numerical claims
- PROCEDURAL-2 — S2 re-tags A→I (or I→A) for any gap that proves mis-tagged during mapping; reports as discipline note
- PROCEDURAL-3 — Citation rule (merged into SEAM-2 procedural)

These are already in docs/s1-exit-artefact.md so Claude Code will pick them up via derivation intent.

---

*End of S2 opening prompt draft.*
