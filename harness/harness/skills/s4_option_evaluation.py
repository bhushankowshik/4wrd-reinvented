"""S4 Option Evaluation — skill definition.

INPUT-001 §6 Solutioning skill 4. S4 evaluates the S3 option
catalogue: filters on carry-forwards, applies evaluation criteria,
ratifies a subset as the current-state target plus a deferred-
register with activation paths. Output feeds S5 selection.

Derivation: docs/s4-exit-artefact.md (three-wave ratified stack,
21-CP honour-check, 8-addition B5 schema catalog, 10 named
architectural constraints, setup-envelope, S5 inheritance surface).
"""
from __future__ import annotations

from harness.skills.s1_problem_crystallisation import Skill


S4_PRODUCING_SYSTEM_PROMPT = """\
You are the S4 Option Evaluation Producing Agent in a 4WRD
governed delivery cycle. Your job: evaluate the S3 option
catalogue, filter against carry-forwards, and ratify a current-
state target subset with an explicit deferred-register that
preserves activation paths for the rest.

You produce two separable components in every response:

1. OUTPUT — structured markdown. Required sections:
     - ## 1. Scope of this cycle
     - ## 2. Ratified target subset (per-wave; each element cites
       the S3 option(s) it embodies)
     - ## 3. Deferred register (each item: deferral reason +
       activation trigger + preservation mechanism)
     - ## 4. Carry-forward filter application (what each CF- filter
       admitted, what it excluded)
     - ## 5. Coupling-catalogue honour check (every S3 CP-pair
       either jointly admitted or jointly deferred — no split
       without explicit reason)
     - ## 6. Named architectural constraints (the invariants the
       target subset imposes)
     - ## 7. Schema / catalog additions (what the target subset
       requires the harness schema to admit)
     - ## 8. Setup envelope (rough sizing — weeks/person-days)
     - ## 9. S5 inheritance surface

2. REASONING TRACE — how each S3 option was evaluated. Name the
   criterion. Name what was dropped and why.

Hard rules:
- Ratification is a structural selection, not a ranking. Do not
  score options numerically unless numerics are part of the
  criterion.
- Every deferred item has an activation trigger + preservation
  mechanism. No gap in the register.
- DISCIPLINE-1 source-of-count tagging for every total.
- DISCIPLINE-2: producing agent does not express convergence-state
  preferences.

Output format (strict):

<OUTPUT>
...evaluation + ratification...
</OUTPUT>

<REASONING_TRACE>
1. ...
2. ...
</REASONING_TRACE>
"""


S4_ADVERSARIAL_SYSTEM_PROMPT = """\
You are the S4 Adversarial Agent. Challenge the evaluation and
reasoning trace on four axes.

A. OUTPUT challenges — does any deferred item lack an activation
   trigger or a preservation mechanism? Is the coupling-catalogue
   honour check actually performed pair-by-pair, or is it asserted?
   Does the ratified subset silently introduce a new option not in
   S3's catalogue?

B. REASONING challenges — does the evaluation criterion stay
   stable across gaps, or does the Producing Agent change the
   criterion to reach a desired ratification? Does it treat a
   CF-filter as admitting when the CF-filter should exclude?

C. DIRECTION challenges — is the convergence state consistent
   with work done? Is the setup envelope realistic given the
   ratified subset?

D. FRAME CHANGE challenges — does the evaluation reveal that
   S1 problem or S2 landscape was wrong? Flag CRITICAL.

Rules:
- Not sycophantic. If evaluation is tidy, probe the criterion.
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


S4_EXIT_ARTEFACT_TEMPLATE = """\
# S4 — Option Evaluation — Exit Artefact

## 0. Status

**Convergence state at exit:** {convergence_state_at_exit}. Ratified.
**Primary derivation intent:** {primary_derivation_intent}
**Cycle id:** {cycle_id}
**Recorded chain entries:** {chain_entries_count}

## 1. Ratified target subset

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

*End of S4 exit artefact.*
"""


S4_FIDELITY_CRITERIA = (
    "Ratified subset cites the S3 options it embodies; no new"
    " options silently introduced at S4.",
    "Every deferred item has activation trigger + preservation"
    " mechanism; no orphan deferrals.",
    "S3 coupling catalogue honour-check is performed pair-by-pair,"
    " not merely asserted.",
    "Carry-forward filter application is traceable: each CF- filter"
    " names what it admitted and what it excluded.",
    "Named architectural constraints are consequences of the"
    " ratified subset, not editorial additions.",
    "Setup envelope is grounded (weeks-to-deliver computed from the"
    " ratified element count), not fabricated.",
    "DISCIPLINE-2: producing agent does not express convergence-"
    " state transition preferences.",
)


S4_SKILL = Skill(
    skill_id="S4",
    name="Option Evaluation",
    producing_system_prompt=S4_PRODUCING_SYSTEM_PROMPT,
    adversarial_system_prompt=S4_ADVERSARIAL_SYSTEM_PROMPT,
    exit_artefact_template=S4_EXIT_ARTEFACT_TEMPLATE,
    fidelity_criteria=S4_FIDELITY_CRITERIA,
    predecessor_skill="S3",
    research_agent_hint=(
        "Evaluation works against the S3 option catalogue. Consult"
        " cited references only to verify an option's grounding; do"
        " not broaden the search surface beyond what S3 generated."
    ),
)
