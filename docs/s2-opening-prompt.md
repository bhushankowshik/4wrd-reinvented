# S2 Opening Prompt — Draft (revised v2)

**Status:** Pre-staged draft. Refine in your own voice before pasting to Claude Code.
**Revision v2:** Six adversarial challenges absorbed — coordination layer scoped correctly, regulatory obligations corrected, client landscape boundary clarified, Agent Teams reframed as decision point, SDK mappings qualified as candidate primitives, DISCIPLINE-1 applied consistently.

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
    sector-specific regulatory obligations on the harness itself
  - Target-state: multi-actor coordination as a native primitive, 
    harness commercially deployed to regulated clients
  S2 maps constraints on the current-state build. Where a 
  constraint differs materially between current and target state, 
  surface the split explicitly rather than collapsing to either.

KNOWLEDGE CONTRIBUTION:
  - Implementation target: Claude Agent SDK (Python/TypeScript). 
    Candidate implementation primitives (not confirmed equivalences 
    — equivalence to be verified during implementation):
    - Subagents with isolated context windows are candidate 
      primitives for per-role context packages
    - SDK hooks (PreToolUse, PostToolUse, SessionStart, 
      UserPromptSubmit — four per Agent SDK docs) are candidate 
      primitives for 4WRD four hook types
    - Skills system is a candidate primitive for the sixteen 
      reference skills (sixteen per INPUT-001)
    - Agent Teams capability is a candidate primitive for 
      multi-agent coordination
  - Agent Teams decision point: Agent Teams is experimental and 
    disabled by default. This is not a settled constraint — it 
    is a decision point with three options: (a) accept 
    experimental status and its instability risk, (b) build a 
    custom coordination layer to close the six AG-9 gaps 
    (concurrency, communication, coherence, quorum/consensus, 
    role-assignment, handover — six per s1-exit-artefact.md §4), 
    (c) operate single-actor for current-state and defer 
    multi-actor to target-state pending Agent Teams maturation. 
    S2 should surface this as an explicit output, not treat it 
    as pre-decided.
  - Coordination gap: a custom coordination layer is likely 
    required to close the gap between Agent Teams primitives and 
    the six AG-9 concerns. Exact shape is S2 output, not S2 
    input.
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
  - Regulatory: baseline data-protection obligations likely apply 
    (PDPA if operating in Singapore; GDPR/CCPA depending on user 
    geography). No sector-specific or contractual regulatory 
    obligations on the harness itself yet. Client regulatory 
    landscape (MAS TRM, CCoP 2.0, PDPA as client-side, 
    CAAS/ICAO) is out of scope for S2 constraint mapping as 
    binding obligations on the build — but may re-enter as 
    design inputs in later phases where harness features are 
    designed to accommodate likely client requirements. S2 does 
    not map client landscape; S3+ may cite it.
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

## What changed from draft v1

1. **Coordination layer scoped correctly** — "thin shared-state layer" replaced with "custom coordination layer likely required; exact shape is S2 output." Avoids pre-committing to a single component for six architecturally distinct AG-9 gaps.

2. **Regulatory obligations corrected** — "no regulatory obligations yet" replaced with accurate statement: baseline data-protection (PDPA, GDPR/CCPA depending on geography) likely applies now; sector-specific and contractual obligations do not yet apply.

3. **Client landscape boundary clarified** — explicitly out of scope for S2 constraint mapping as binding obligations; explicitly may re-enter as design inputs in S3+ phases.

4. **Agent Teams reframed as decision point** — three options named (accept experimental, build custom, defer to target-state). S2 surfaces the choice rather than inheriting a pre-decision.

5. **SDK mappings qualified** — "map to" replaced with "are candidate implementation primitives for" across subagents, hooks, and skills. Equivalence is a hypothesis to verify, not a confirmed fact.

6. **DISCIPLINE-1 applied consistently** — "sixteen reference skills" and "four hook types" now carry source-of-count tags. "Thirteen architectural gaps" tag retained from v1.

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

*End of S2 opening prompt draft (revised v2).*
