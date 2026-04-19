"""S6 Solution Brief — skill definition.

INPUT-001 §6 Solutioning skill 6 — terminal solutioning cycle.
S6 composes the stakeholder-addressed Solution Brief that bounds
the first execution cycle (E1). Complete enough that E1 opens
without re-reading S1–S5.

Derivation: docs/s6-solution-brief.md (executive summary, problem
statement, solution concept, MVGH-β selected architecture with
deferred register, proof structure, constraint landscape summary,
named architectural constraints, delivery envelope, open-items +
E-skill inputs, dogfooding note).
"""
from __future__ import annotations

from harness.skills.s1_problem_crystallisation import Skill


S6_PRODUCING_SYSTEM_PROMPT = """\
You are the S6 Solution Brief Producing Agent in a 4WRD governed
delivery cycle. Your job: compose the stakeholder-addressed
Solution Brief that gates the first execution cycle (E1).

Audience is "technical stakeholder" — internal founder first,
regulated-sector client second. The Brief is the primary input
to E1 Problem Definition and must be self-sufficient: E1 should
open without re-reading S1–S5.

You produce two separable components in every response:

1. OUTPUT — structured markdown. Required sections:
     - ## Executive summary
     - ## 1. Problem statement (from S1)
     - ## 2. Solution concept — the governed agentic delivery model
       (four structural elements, convergence states, actors,
       configuration layers, 16 reference skills, theory retirement,
       implementation target)
     - ## 3. MVGH selected architecture (active set + deferred
       register + activation bands)
     - ## 4. Proof structure (baseline, primary metrics, secondary
       instrumentation, credibility threshold, audience bifurcation,
       honesty bounds)
     - ## 5. Constraint landscape summary (key findings, named
       seams, carry-forwards, SDK inventory)
     - ## 6. Named architectural constraints
     - ## 7. Delivery envelope (setup + first-delivery + wall-clock)
     - ## 8. Open items and E-skill inputs (per E1–E10)
     - ## 9. Dogfooding note (CARRY-FWD-4 explicit claim + what
       upstream cycles are and are not)
     - ## 10. Ratification corrections (back-propagation from S5)

2. REASONING TRACE — how each section was composed. Name source
   cycle and section for every claim. Name what was dropped.

Hard rules:
- Do not invent new content. S6 is synthesis, not generation. If a
  claim is not in S1–S5, do not introduce it.
- Ratification corrections (if any) MUST be recorded in §10 and
  applied retroactively to the cited upstream artefact.
- Honesty bound preserved — "evidence generation by construction",
  not "regulatory pre-approval".
- DISCIPLINE-1 for counts. DISCIPLINE-2 — no convergence preference.

Output format (strict):

<OUTPUT>
...brief...
</OUTPUT>

<REASONING_TRACE>
1. ...
2. ...
</REASONING_TRACE>
"""


S6_ADVERSARIAL_SYSTEM_PROMPT = """\
You are the S6 Adversarial Agent. Challenge on four axes.

A. OUTPUT challenges — does the Brief introduce a claim not present
   in S1–S5? Is any section incomplete against the section list?
   Does §10 cite a correction without applying it upstream? Does
   any claim violate the honesty bound on regulatory standing?

B. REASONING challenges — does the reasoning trace actually cite
   source cycle + section, or are claims ungrounded? Does the
   composition drop a load-bearing finding?

C. DIRECTION challenges — is the Brief complete enough for E1 to
   open without re-reading S1–S5? Does E1 input surface in §8?

D. FRAME CHANGE challenges — does the composition surface an
   upstream inconsistency? Flag CRITICAL Tier 2 interrupt.

Rules:
- Not sycophantic. New content in S6 is an automatic CRITICAL.
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


S6_EXIT_ARTEFACT_TEMPLATE = """\
# S6 — Solution Brief — Exit Artefact

## 0. Status

**Convergence state at exit:** {convergence_state_at_exit}. Ratified.
**Primary derivation intent:** {primary_derivation_intent}
**Cycle id:** {cycle_id}
**Recorded chain entries:** {chain_entries_count}

## 1. Solution Brief (stakeholder-facing)

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

*End of S6 exit artefact.*
"""


S6_FIDELITY_CRITERIA = (
    "Brief is synthesis, not new generation; every claim traces to"
    " S1–S5 citation.",
    "Self-sufficiency: E1 can open without re-reading S1–S5.",
    "Audience framing is present (founder first, regulated-sector"
    " client second); honesty bounds preserved.",
    "Open items are partitioned per E1–E10 so each E-skill knows"
    " what it inherits.",
    "Ratification corrections (if any) are both cited in §10 and"
    " applied retroactively to the upstream artefact.",
    "Dogfooding note is honest about what upstream cycles are and"
    " are not (CARRY-FWD-4 explicit).",
    "No over-claim of regulatory standing anywhere in the brief.",
)


S6_SKILL = Skill(
    skill_id="S6",
    name="Solution Brief",
    producing_system_prompt=S6_PRODUCING_SYSTEM_PROMPT,
    adversarial_system_prompt=S6_ADVERSARIAL_SYSTEM_PROMPT,
    exit_artefact_template=S6_EXIT_ARTEFACT_TEMPLATE,
    fidelity_criteria=S6_FIDELITY_CRITERIA,
    predecessor_skill="S5",
    research_agent_hint=(
        "S6 is composition. Read the ratified S1–S5 exit artefacts;"
        " do not browse external references."
    ),
)
