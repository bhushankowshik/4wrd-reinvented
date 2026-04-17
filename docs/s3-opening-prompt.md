# S3 Opening Prompt

**Status:** Ratified S3 direction. Paste to Claude Code to open S3 Option Generation.
**Date:** 2026-04-17

---

## Cycle Start

CYCLE START
CONVERGENCE STATE: Explorative
DIRECTION: Produce a first-pass option landscape for S3 Option 
  Generation. The primary input is the S2 exit artefact 
  (docs/s2-exit-artefact.md). Read it before producing.

  Do NOT select options. Do NOT evaluate options. Generate the 
  option space only.

  Produce:
  1. For AG-4 (Artefact Lineage — pivot gap, first-order 
     priority): a structured set of mechanism design options 
     covering storage choice, lineage schema approach, and 
     T10 implementation path. These are the most consequential 
     design decisions in the delivery.
  2. For the custom coordination layer (option b, AG-9 cluster): 
     a structured set of design options covering coordination 
     architecture, T4 integration depth, and the three T4 
     limitation mitigations (session resumption → AG-9b; task 
     coordination → AG-9c; shutdown → AG-9f).
  3. A first-pass option inventory for the remaining 11 A-tagged 
     gaps — lighter treatment, identifying the primary design 
     choice each gap presents without full option elaboration.

  AG-4 and the coordination layer are the two hardest design 
  problems. Give them proportionate depth. The remaining 11 
  gaps are context for S4 evaluation — surface them without 
  over-investing this cycle.

KNOWLEDGE CONTRIBUTION:
  - S2 top-line findings to carry into option generation:
    AG-4 is the pivot gap — coextensive with N4, upstream 
    dependency for T10 across 8 of 13 gaps (SEAM-4), 
    prerequisite for D7a enforceability (SEAM-3), only 
    current-state-dense gap on D6.
  - Custom coordination layer is option (b) — built on T4 
    primitives via T5 (ClaudeAgentOptions). T4 named 
    limitations map precisely: session resumption → AG-9b 
    (message loss), task coordination → AG-9c (coherence — 
    heaviest work), shutdown → AG-9f (handover instability).
  - D6 is target-state-dominated across 12 of 13 gaps. 
    Regulatory pressure scales sharply at deployment. Options 
    must be assessed for regulatory compatibility even if D6 
    does not bind current-state.
  - D3 (attention) is the binding current-state scalar. Options 
    that require high solo-founder attention to implement or 
    maintain carry a real cost.
  - AG-4 mechanism choice is upstream of 8 other gap designs — 
    generate AG-4 options first; coordination layer options 
    second; remaining gaps third.
  - 18-tension register from S2 is the primary source of design 
    constraints for option generation. Key tensions for AG-4: 
    T-1 (audit immutability vs erasure), T-2 (retention 
    duration), T-3 (cross-tenant isolation). Key tensions for 
    coordination layer: T-12 (message synchrony), T-13 
    (consistency vs availability), T-18 (handover atomicity).

PRIMARY DERIVATION INTENT:
  docs/s2-exit-artefact.md (ratified S2 output)
  docs/s1-exit-artefact.md (ratified S1 output)
  docs/foundation/INPUT-001-foundation-v4.md
