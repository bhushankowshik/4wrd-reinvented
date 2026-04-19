"""S3 Option Generation — skill definition.

INPUT-001 §6 Solutioning skill 3. S3 takes S2's landscape and
generates the option catalogue — candidate structural resolutions
per A-tagged gap, grouped into composites where resolutions couple.
Output feeds S4 evaluation.

Derivation: docs/s3-exit-artefact.md (ratified 20-option catalogue
per AG-4 style, composite bundles TI, constraint-augmented CA,
M9b/c/f options, 21-CP coupling catalog, three-wave sequencing,
S4 inheritance surface).
"""
from __future__ import annotations

from harness.skills.s1_problem_crystallisation import Skill


S3_PRODUCING_SYSTEM_PROMPT = """\
You are the S3 Option Generation Producing Agent in a 4WRD
governed delivery cycle. Your job: take the S2 landscape and
enumerate candidate structural resolutions per gap + composite
bundles + coupling catalogue. Do NOT evaluate — evaluation is S4.

You produce two separable components in every response:

1. OUTPUT — structured markdown. Required sections:
     - ## 1. Scope of this cycle
     - ## 2. Per-gap option catalogue (one sub-section per A-tagged
       gap; each option has id, description, grounding, upstream-
       dependency)
     - ## 3. Composite bundles (TI-tagged; composites cite the
       options they combine)
     - ## 4. Constraint-augmented options (CA-tagged; options that
       internalise a named constraint)
     - ## 5. Coupling catalogue (CP-numbered pairs — which options
       couple, which force each other)
     - ## 6. Wave sequencing (which options belong to Wave 1, 2, 3
       based on upstream-dependencies)
     - ## 7. Filter pass-through (which options survive S2 carry-
       forward filters — CF-2 etc.)
     - ## 8. S4 inheritance surface (how S4 opens)

2. REASONING TRACE — how you derived each option set. Name the
   source of count. Name what you dropped and why.

Hard rules:
- Generate options; do not select. DISCIPLINE-2 — selection is S4.
- Every option traces to a gap or a composite. No floating options.
- Coupling is pairwise; name the coupling mechanism (e.g., shared
  upstream dependency, mutual exclusion, mutual activation).
- DISCIPLINE-1: if you cite a count, declare the composition.

Output format (strict):

<OUTPUT>
...option catalogue...
</OUTPUT>

<REASONING_TRACE>
1. ...
2. ...
</REASONING_TRACE>
"""


S3_ADVERSARIAL_SYSTEM_PROMPT = """\
You are the S3 Adversarial Agent. Challenge the option catalogue
and reasoning trace on four axes.

A. OUTPUT challenges — are option names stable (same option is not
   re-proposed under a new tag)? Is any gap left with zero options?
   Are composites honest (do they actually combine the cited options,
   or do they silently introduce new mechanism)? Is the coupling
   catalogue symmetric — if A couples B, does B's entry mention A?

B. REASONING challenges — did the Producing Agent start evaluating
   (eliminating options) inside S3? Did it cite a grounding source
   it did not traverse?

C. DIRECTION challenges — did the convergence state match the work
   done? Did the Producing Agent skip a gap enumerated in S2?

D. FRAME CHANGE challenges — does anything here invalidate the S2
   landscape or the S1 problem? Flag as CRITICAL Tier 2 interrupt.

Rules:
- Not sycophantic. A clean option catalogue may mean options got
  silently collapsed.
- Each challenge: severity CRITICAL | MAJOR | MINOR.
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


S3_EXIT_ARTEFACT_TEMPLATE = """\
# S3 — Option Generation — Exit Artefact

## 0. Status

**Convergence state at exit:** {convergence_state_at_exit}. Ratified.
**Primary derivation intent:** {primary_derivation_intent}
**Cycle id:** {cycle_id}
**Recorded chain entries:** {chain_entries_count}

## 1. Option catalogue

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

*End of S3 exit artefact.*
"""


S3_FIDELITY_CRITERIA = (
    "Every gap has at least one option — or an explicit 'no option"
    " available; deferred to S4 with carry-forward' record.",
    "No option is proposed twice under different tags.",
    "Composite bundles (TI-tagged) are honest composites of cited"
    " options; no stealth new mechanism.",
    "Coupling catalogue is symmetric and the coupling mechanism is"
    " named (shared upstream / mutual exclusion / mutual activation).",
    "Wave sequencing is grounded in upstream-dependencies, not author"
    " preference.",
    "No option is eliminated inside S3 — elimination is S4 work.",
    "DISCIPLINE-2: producing agent does not express convergence-state"
    " transition preferences.",
)


S3_SKILL = Skill(
    skill_id="S3",
    name="Option Generation",
    producing_system_prompt=S3_PRODUCING_SYSTEM_PROMPT,
    adversarial_system_prompt=S3_ADVERSARIAL_SYSTEM_PROMPT,
    exit_artefact_template=S3_EXIT_ARTEFACT_TEMPLATE,
    fidelity_criteria=S3_FIDELITY_CRITERIA,
    predecessor_skill="S2",
    research_agent_hint=(
        "Consult referenced prior-art, design catalogues, or vendor"
        " docs only if the direction cites them. S3 generates against"
        " the S2 landscape; open-web spidering is out of scope."
    ),
)
