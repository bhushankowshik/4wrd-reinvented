# S4 Opening Prompt

**Status:** Ratified S4 direction. Paste to Claude Code to open S4 Option Evaluation.
**Date:** 2026-04-17

---

## Cycle Start

CYCLE START
CONVERGENCE STATE: Explorative
DIRECTION: Open S4 Option Evaluation. Read docs/s3-exit-artefact.md 
  before producing. Then read docs/s2-exit-artefact.md for the 
  constraint dimensions.

  S4 evaluates options against constraints. It does not generate 
  new options. It does not select. It produces evaluated option 
  sets that S5 can select from.

  First act: resolve DEC-D5 (Wave 0 precondition).

  DEC-D5 comprises three decisions:
  - DEC-D5-1: IP ownership of composed assets
  - DEC-D5-2: Cross-tenant sharing model for composed assets
  - DEC-D5-3: Pricing unit for client-facing deployment

  These were deferred from S2 to S3 to S4. CP-18 (H-type) makes 
  them upstream to AG-4 storage-tenancy design. AG-4 design cannot 
  begin until DEC-D5 is resolved.

  For each DEC-D5 decision produce:
  1. The decision surface — what specifically must be decided
  2. The constraint mapping — which S2 dimensions (D1–D7) bind 
     this decision and how
  3. The option set — what the realistic choices are
  4. The evaluation — how each option performs against the 
     binding constraints
  5. A recommended direction — the option that best satisfies 
     the constraints given current-state context (Bhushan as 
     sole orchestrator, no client contracts, Agent SDK target, 
     dogfooding)

  After DEC-D5: assess whether Wave 1 pivot cluster evaluation 
  can begin in this same cycle or requires a separate cycle.

KNOWLEDGE CONTRIBUTION:
  - Current-state context: solo founder, no client contracts, 
    no revenue, building 4WRD using 4WRD. Target-state: 
    multi-client commercial deployment in regulated sectors.
  - DEC-D5 decisions are commercial-architecture decisions that 
    cascade into AG-4 storage-tenancy (CP-18). They are not 
    implementation choices — they are product decisions.
  - The S3 exit artefact §6 deferred-choice list carries a 
    joint-stance note: CF-2 baseline acceptance and §9 
    Friction-severity tolerance are interdependent postures. 
    This applies to DEC-D5 evaluation — the commercial stance 
    on sharing/pricing interacts with the technical stance on 
    storage isolation.
  - CP-18 is H-type: AG-4 storage-tenancy waits on DEC-D5. 
    Getting DEC-D5 right unblocks the most consequential 
    design decision in the delivery.

PRIMARY DERIVATION INTENT:
  docs/s3-exit-artefact.md (ratified S3 output)
  docs/s2-exit-artefact.md (ratified S2 output)
  docs/s1-exit-artefact.md (ratified S1 output)
  docs/foundation/INPUT-001-foundation-v4.md
