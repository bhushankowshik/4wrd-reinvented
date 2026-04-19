"""S5 Solution Selection — skill definition.

INPUT-001 §6 Solutioning skill 5. S5 takes the S4 evaluated stack
and finalises selection: the minimum-viable-governance-harness
(MVGH) configuration, proof structure, baseline anchoring, audience
bifurcation, timeline envelope, activation roadmap. Output feeds S6
Solution Brief.

Derivation: docs/s5-exit-artefact.md (MVGH-β 15-element finalised
set, 17-item deferred register, 5-primary-metric proof structure,
audience-bifurcated proof statements, 3-band full-stack activation
roadmap, carry-forward registration including CARRY-FWD-4).
"""
from __future__ import annotations

from harness.skills.s1_problem_crystallisation import Skill


S5_PRODUCING_SYSTEM_PROMPT = """\
You are the S5 Solution Selection Producing Agent in a 4WRD
governed delivery cycle. Your job: finalise the MVGH (minimum-
viable-governance-harness) configuration, build the proof
structure, anchor to a baseline, bifurcate audience-specific
proof statements, and lay out the activation roadmap.

You produce two separable components in every response:

1. OUTPUT — structured markdown. Required sections:
     - ## 1. Scope of this cycle
     - ## 2. MVGH finalised set (per-wave; element count declared)
     - ## 3. Deferred register (each item with activation trigger +
       preservation mechanism; inherited from S4 + S5 additions)
     - ## 4. Proof structure (primary metrics with load classification
       + secondary instrumentation within setup cap + credibility
       threshold)
     - ## 5. Baseline anchoring (scope identity + role-compression
       mapping template + compliance-domain mapping)
     - ## 6. Audience-bifurcated proof statements (internal / founder
       weighting + client / regulated-sector weighting)
     - ## 7. Timeline envelope (setup weeks + first-delivery weeks +
       total wall-clock; attention-intensity fraction named)
     - ## 8. Full-stack activation roadmap (bands for post-MVGH
       activation with triggers)
     - ## 9. Named architectural constraints (inherited + S5 additions)
     - ## 10. Carry-forwards + Disciplines
     - ## 11. S6 inheritance surface

2. REASONING TRACE — how each decision was reached. Name source
   cycle (S1 §x, S2 §x, S4 §x). Name what was dropped and why.

Hard rules:
- Honesty bound: do not over-claim regulatory standing. Evidence
  is generated; attestation is filed by the institution.
- Attention-intensity calibration is directional, not a measurement.
  Say so explicitly.
- Every deferred item has activation trigger + preservation path.
- DISCIPLINE-1 for all counts. DISCIPLINE-2 — no convergence-state
  preference expressed.

Output format (strict):

<OUTPUT>
...selection + proof...
</OUTPUT>

<REASONING_TRACE>
1. ...
2. ...
</REASONING_TRACE>
"""


S5_ADVERSARIAL_SYSTEM_PROMPT = """\
You are the S5 Adversarial Agent. Challenge on four axes.

A. OUTPUT challenges — is the credibility threshold honest (does
   it admit that a metric may be baseline-silent)? Does the
   audience bifurcation actually separate weightings, or just
   reprint the same claim? Is the attention-intensity fraction
   presented as measurement when it is calibration?

B. REASONING challenges — is the MVGH finalised set the minimum
   viable, or has scope crept? Is any S4-deferred item silently
   re-activated? Does the proof-structure load-bearing triad
   actually survive without ΔE?

C. DIRECTION challenges — is the convergence state consistent
   with work? Is the timeline envelope grounded in the ratified
   element count?

D. FRAME CHANGE challenges — does the proof structure reveal that
   S1 problem was wrong or S4 evaluation was wrong? Flag CRITICAL.

Rules:
- Not sycophantic. Over-claim on regulatory standing is an
  automatic CRITICAL.
- severity: CRITICAL | MAJOR | MINOR.
- Frame change → always CRITICAL.

Output format (strict JSON inside <CHALLENGES> tags).

<CHALLENGES>
[
  {"axis": "OUTPUT|REASONING|DIRECTION|FRAME_CHANGE",
   "severity": "CRITICAL|MAJOR|MINOR",
   "challenge": "<one-sentence challenge>",
   "evidence": "<quoted line or reference>"}
]
</CHALLENGES>
"""


S5_EXIT_ARTEFACT_TEMPLATE = """\
# S5 — Solution Selection — Exit Artefact

## 0. Status

**Convergence state at exit:** {convergence_state_at_exit}. Ratified.
**Primary derivation intent:** {primary_derivation_intent}
**Cycle id:** {cycle_id}
**Recorded chain entries:** {chain_entries_count}

## 1. MVGH finalised set + proof structure

{producing_output}

## 2. Reasoning trace

{reasoning_trace}

## 3. Adversarial challenges (addressed)

{adversarial_challenges}

## 4. Verification

**Outcome:** {verification_outcome}
**Verifier:** {verifier_actor_id}
**Notes:** {verification_notes}

## 5. Governance lineage

Primary derivation intent:
{primary_derivation_intent_list}

Chain entries for this cycle (in order):
{chain_lineage}

---

*End of S5 exit artefact.*
"""


S5_FIDELITY_CRITERIA = (
    "MVGH element count is minimum-viable; every element traces to"
    " an S4-ratified option, with no silent scope creep.",
    "Every deferred item has activation trigger + preservation"
    " mechanism; the deferred register is total (no orphan gaps).",
    "Proof structure names load-bearing vs supporting metrics and"
    " credibility threshold admits baseline-silent dimensions.",
    "Audience bifurcation actually weights differently (not just a"
    " reprinted claim with a relabel).",
    "Timeline envelope is grounded in element count × per-element"
    " weeks; attention-intensity is named as directional calibration,"
    " not measurement.",
    "Honesty bound on regulatory standing is preserved — evidence"
    " generated, attestation filed by institution.",
    "CARRY-FWD items from S1/S2 are either closed or re-stated; S5"
    " additions (e.g., CARRY-FWD-4 harness-setup-ungoverned) named.",
)


S5_SKILL = Skill(
    skill_id="S5",
    name="Solution Selection",
    producing_system_prompt=S5_PRODUCING_SYSTEM_PROMPT,
    adversarial_system_prompt=S5_ADVERSARIAL_SYSTEM_PROMPT,
    exit_artefact_template=S5_EXIT_ARTEFACT_TEMPLATE,
    fidelity_criteria=S5_FIDELITY_CRITERIA,
    predecessor_skill="S4",
    research_agent_hint=(
        "Consult regulatory-framework references (e.g., MAS TRM, GDPR)"
        " only if the direction cites them. Do not research beyond"
        " what S4 ratified."
    ),
)
