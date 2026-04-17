# S2 Opening Prompt — Draft (revised v3)

**Status:** Pre-staged draft. Refine in your own voice before pasting to Claude Code.
**Revision v3:** Two fixes from pass 3 adversarial review + two Agent Teams clarifications from verified source (Anthropic docs).

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
    disabled by default (source: Anthropic docs, confirmed). 
    Known limitations: session resumption, task coordination, 
    shutdown behaviour. Additional constraints: requires Opus 4.6 
    minimum for all agents — a cost constraint, not just a 
    stability one. Accessible programmatically via Agent SDK 
    through ClaudeAgentOptions env configuration.
    This is a decision point with three options:
    (a) Accept experimental status and its instability and cost 
        risks
    (b) Build a custom coordination layer on top of Agent Teams 
        or from scratch — likely required under this option to 
        close the six AG-9 gaps (concurrency, communication, 
        coherence, quorum/consensus, role-assignment, handover — 
        six per s1-exit-artefact.md §4). Agent Teams SDK access 
        via ClaudeAgentOptions provides a concrete starting point 
        rather than requiring a full custom build.
    (c) Operate single-actor for current-state and defer 
        multi-actor to target-state pending Agent Teams maturation
    S2 surfaces this choice as an explicit output, not a 
    pre-decided constraint.
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
  - Operational: solo founder capacity is the binding resource 
    constraint. S2 must assess which constraints are attention-
    bound, not just cost-bound.
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

## What changed from draft v2

1. **Coordination bullet tension resolved** — two separate bullets 
   (decision point + coordination gap) consolidated into one. Custom 
   coordination layer is now clearly scoped to option (b), not asserted 
   as a given across all options.

2. **Operational dimension elaborated** — "solo founder capacity is the 
   binding resource constraint; S2 must assess which constraints are 
   attention-bound, not just cost-bound" added to knowledge contribution.

3. **Agent Teams cost constraint added** — Opus 4.6 minimum for all agents 
   confirmed from Anthropic docs. Named as a cost constraint, not just 
   a stability one.

4. **Agent Teams SDK access clarified** — programmatic access via 
   ClaudeAgentOptions confirmed. Option (b) now notes this as a concrete 
   starting point rather than requiring a full custom build from scratch.

---

## Review pass summary

- Pass 1: six substantive issues found and absorbed
- Pass 2: six new issues found and absorbed  
- Pass 3: two worth-addressing fixes applied, two optional deferred to S2
- Pass 4 (this version): two Agent Teams clarifications from verified source

Meta-observation from pass 3 adversarial review: returns are diminishing. 
This draft is ready to paste. Do not request a further review pass.

---

## Points to refine in your own voice

- The direction language is mine. Rewrite before pasting.
- The knowledge contribution is detailed. Trim if over-specified.
- If your instinct is to start with a specific high-density gap rather 
  than a landscape cycle, rewrite the direction accordingly.

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

*End of S2 opening prompt draft (revised v3).*
