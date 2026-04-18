# S5 Opening Prompt

**Status:** Ratified S5 direction.
**Date:** 2026-04-18
**Forcing function:** Prove 4WRD works and delivers significant
productivity improvement across the SDLC.

---

## Cycle Start

CYCLE START
CONVERGENCE STATE: Explorative
DIRECTION: Open S5 Solution Selection. Read
  docs/s4-exit-artefact.md before producing. Then read
  docs/s3-exit-artefact.md and docs/s1-exit-artefact.md.

  S5 selects among the evaluated options from S4 to produce
  a coherent solution. S5 does not generate new options.

  Forcing function: there is an immediate need to prove
  4WRD works and delivers significant productivity
  improvement across the SDLC. This is a proof-of-concept
  requirement, not a full commercial deployment requirement.

  S5 primary task: identify the minimum viable governed
  harness (MVGH) — the smallest coherent subset of the
  ratified S4 three-wave stack that:
  (a) can run a real SDLC delivery cycle end-to-end,
  (b) produces governed, audited, adversarially-challenged
      output,
  (c) demonstrates measurable productivity improvement
      relative to ungoverned AI use, and
  (d) can be built by a solo orchestrator in a realistic
      timeframe.

  Produce:
  1. MVGH definition — which S4 ratified options are
     included, which are deferred. Justify each inclusion
     and each deferral against the four criteria above.
  2. Productivity measurement framework — how "significant
     productivity improvement" will be demonstrated. What
     is measured, against what baseline, and what would
     constitute a credible proof.
  3. MVGH delivery timeline — realistic setup-weeks for the
     MVGH subset only, with solo-orchestrator attention
     capacity applied.
  4. Deferred items register — what is explicitly out of
     MVGH scope, with activation path preserved per the
     defined-but-dormant patterns in the S4 ratified stack.

  Per DISCIPLINE-2: S5 may make selections among evaluated
  options. This is S5's mandate. Selections must be
  grounded in the forcing function and the four MVGH
  criteria, not in preference.

KNOWLEDGE CONTRIBUTION:
  - Forcing function: prove 4WRD works and delivers
    significant productivity improvement across the SDLC.
    Audience is likely a technical or business stakeholder
    who needs to see a real delivery, not a demo.
  - The S4 ratified stack has extensive defined-but-dormant
    patterns (AG9d-5 override shell, M9c-3 quorum-commit
    shell, AG6b-3 target-state path, quorum machinery) —
    these were designed to be deferred without breaking
    the current-state harness. MVGH leverages this.
  - Solo orchestrator. No deputy. No multi-actor
    coordination required for MVGH.
  - The productivity claim is the primary value proposition
    from S1: elimination of compliance remediation sprints,
    architectural rework, and compounding institutional
    knowledge loss — not just faster production.
  - The dogfooding model applies: 4WRD should be used to
    build itself as part of the proof.
  - The MVGH is not a separate product. It is the
    current-state instantiation of the full ratified stack.
    Every MVGH selection must be made from within the
    ratified S4 stack — not as a shortcut around it.
    Deferred items must remain on the deferred items
    register with explicit activation paths, not discarded.
  - S5 must produce two artefacts simultaneously:
    (1) the MVGH selection for immediate delivery, and
    (2) the full-stack activation roadmap showing how
    each deferred item re-enters the delivery as the
    product matures. Both are S5 outputs. Neither is
    optional.
  - The full S4 ratified three-wave stack is the design
    specification for the complete product. MVGH is a
    delivery sequencing decision, not an architectural
    simplification.

PRIMARY DERIVATION INTENT:
  docs/s4-exit-artefact.md (ratified S4 output)
  docs/s3-exit-artefact.md (ratified S3 output)
  docs/s1-exit-artefact.md (ratified S1 output)
