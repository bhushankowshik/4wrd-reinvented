# S2 Opening Prompt — Draft (revised)

**Status:** Pre-staged draft. Refine in your own voice before pasting to Claude Code.
**Revision:** Implementation target corrected to Claude Agent SDK. S2 scope corrected to harness build constraints only — client regulatory landscape is target-state unknown, not a current constraint.

---

## Suggested opening

```
CYCLE START
CONVERGENCE STATE: Explorative
DIRECTION: Produce a first-pass map of the constraint landscape 
  that applies to the 4WRD harness build itself. Constraints 
  are what shapes, limits, or governs the build — not what 
  4WRD will help clients meet in future.

  Do NOT map constraints against individual gaps yet. Produce:
  1. A taxonomy of constraint dimensions applicable to this 
     build (technical platform, organisational, commercial, 
     operational — candidates only, to be refined)
  2. For each dimension, the primary constraint sources as they 
     exist today for this build
  3. An initial density assessment — which of the thirteen 
     architectural gaps (counted from docs/s1-exit-artefact.md 
     §4: 13 A-tagged) appear constraint-dense vs constraint-
     sparse, without yet naming which specific constraints apply

  Two realities must be held simultaneously throughout S2:
  - Current-state: Bhushan as sole human orchestrator, Agent SDK 
    as implementation platform, no client contracts, no known 
    regulatory obligations on the harness itself
  - Target-state: multi-actor coordination as a native primitive, 
    harness commercially deployed to regulated clients
  S2 maps constraints on the current-state build. Where a 
  constraint differs materially between current and target state, 
  surface the split explicitly rather than collapsing to either.

KNOWLEDGE CONTRIBUTION:
  - Implementation target: Claude Agent SDK (Python/TypeScript). 
    Subagents with isolated context windows map to per-role 
    context packages. SDK hooks (PreToolUse, PostToolUse, 
    SessionStart, UserPromptSubmit) map to 4WRD four hook types. 
    Skills system maps to sixteen reference skills. Agent Teams 
    capability provides multi-agent coordination primitives. 
    One custom component needed: thin shared-state layer for 
    multi-user coordination across sessions.
  - Platform capability status: Agent SDK is production-grade. 
    Agent Teams (multi-agent coordination) is experimental and 
    disabled by default. This is a real constraint on Axis 2 
    mechanism availability during build.
  - Dogfooding recursion: 4WRD is being built using 4WRD. Some 
    S1 mechanisms (Need 10 learning retention, Need 14 retirement 
    candidate surfacing, parts of Need 6 policy enforcement via 
    hooks) do not yet exist and cannot be used during this build. 
    S2 must map constraints against what is available now, not 
    only against the target design.
  - Orchestration: Bhushan sole human orchestrator. Second-in-
    command vacant. Current-state is single-actor. Multi-actor 
    is target-state. S2 must surface where this split makes 
    constraints materially different.
  - Commercial: solo founder, no client contracts signed, no 
    regulatory obligations on the harness itself yet. Client 
    regulatory landscape (MAS TRM, CCoP 2.0, PDPA, CAAS/ICAO) 
    is relevant to what 4WRD will help clients meet — it is not 
    a current constraint on the build itself. Do not map client 
    regulatory landscape in S2.
  - First live test target: Telco NOC. Constraints specific to 
    that engagement belong in the engagement repo, not in the 
    harness build.

PRIMARY DERIVATION INTENT: 
  docs/s1-exit-artefact.md (ratified S1 output)
  docs/foundation/INPUT-001-foundation-v4.md
  docs/foundation/INPUT-002-composition-trace.md
  docs/foundation/INPUT-003-operating-brief.md
```

---

## What changed from the prior draft

1. **Implementation target corrected** — Claude Agent SDK throughout. Managed Agents removed. Agent Teams experimental status added as a real platform constraint.

2. **S2 scope corrected** — harness build constraints only. Client regulatory landscape explicitly excluded — these are target-state client-side use cases, not current constraints on the build.

3. **Current/target split made explicit** — two realities held simultaneously, but S2 maps current-state. Where the split is material, surface it rather than collapse.

4. **Dogfooding recursion added** — capability floor named upfront so S2 does not map against mechanisms that do not yet exist.

5. **Step 3 reframed** — density assessment without naming specific constraints, to avoid drifting into per-gap mapping inside a landscape cycle.

6. **DISCIPLINE-1 applied** — thirteen architectural gaps tagged with source-of-count.

---

## Points to refine in your own voice

- The direction language is mine. Rewrite before pasting — particularly the "two realities" framing.
- The knowledge contribution is detailed. Trim if over-specified for an Explorative cycle.
- If your instinct is to start with a specific high-density gap rather than a landscape cycle, rewrite the direction accordingly.

---

## Carry-forwards S2 inherits (already in s1-exit-artefact.md)

- SEAM-1 — Invariant special-class evolution
- SEAM-1a — Invariant-set initial instantiation
- SEAM-2a — Recursion depth for meta-governance closure
- CARRY-FWD-1 — Need 13 partial technical-constraint readiness
- SEAM-2 procedural — Citation rule
- DISCIPLINE-1 — Source-of-count tagging
- PROCEDURAL-2 — S2 tag-drift reporting
- PROCEDURAL-3 — Citation rule (merged into SEAM-2 procedural)

---

*End of S2 opening prompt draft (revised).*
