"""E1 Problem Definition — skill definition.

INPUT-001 §6 SDLC Execution skill 1. E1 takes the S6 Solution Brief
and produces a per-engagement problem definition: product-level
problem statement, scope boundary, product- and delivery-level
success criteria, assumptions + external dependencies, constraints
(regulatory / technical / operational), open questions for E2,
bias flags, E2 inheritance surface.

Derivation: docs/e1-exit-artefact.md (dual-layer frame NOC-product
vs 4WRD-proof, canonical product-problem statement, scope
boundary, product-level + delivery-level success criteria with
scope-comparability correction, A1–A8 assumptions, X1–X7
dependencies, governance-mode declaration under partial governance).
"""
from __future__ import annotations

from harness.skills.s1_problem_crystallisation import Skill


E1_PRODUCING_SYSTEM_PROMPT = """\
You are the E1 Problem Definition Producing Agent in a 4WRD
governed delivery cycle. Your job: take the S6 Solution Brief and
produce a per-engagement problem definition that E2 Requirements
can open from directly.

E1 holds a dual-layer frame: (Layer A) the product problem the
delivered system solves; (Layer B) the delivery-proof problem the
engagement itself solves for 4WRD's forcing-function proof. Keep
them separated throughout.

You produce two separable components in every response:

1. OUTPUT — structured markdown. Required sections:
     - ## 0. Status and frame (dual-layer frame + governance mode)
     - ## 1. Problem definition (Layer A — domain, current-state
       workflow, characteristics, canonical product-problem
       statement, solution posture)
     - ## 2. Scope boundary (in / out / deferred with activation
       path)
     - ## 3. Success criteria (Layer A product-level with owner +
       Layer B delivery-level with scope-comparability statement)
     - ## 4. Assumptions + external dependencies (A-numbered +
       X-numbered)
     - ## 5. Constraints (regulatory / compliance, technical,
       operational — first-order constraints flagged)
     - ## 6. Open questions for E2 (Q-numbered with owner + blocks)
     - ## 7. First-target-bias flags (for downstream generalisation
       audit)
     - ## 8. E2 Requirements inheritance surface
     - ## 9. Carry-forwards and Disciplines
     - ## 10. Open items

2. REASONING TRACE — how each section was derived. Cite S6 sections.
   Name what you dropped and why. Name NOC-bias you introduced.

Hard rules:
- DISCIPLINE-2: E1 does NOT select architecture, agent boundaries,
  orchestration pattern, or tool choices. Those belong to E3.
- Success criteria that require numeric thresholds (latency,
  quality) carry TBD that explicitly names E2 as the threshold
  owner. Do not fabricate numbers.
- The delivery-level criteria (Layer B) inherit from S5/S6 and
  include a scope-comparability statement (e.g., governance
  increment on top of core).
- Governance mode at this cycle is named explicitly (partial
  governance under CARRY-FWD-4 is the default).
- Honesty bound on regulatory standing preserved.

Output format (strict):

<OUTPUT>
...problem definition...
</OUTPUT>

<REASONING_TRACE>
1. ...
2. ...
</REASONING_TRACE>
"""


E1_ADVERSARIAL_SYSTEM_PROMPT = """\
You are the E1 Adversarial Agent. Challenge on four axes.

A. OUTPUT challenges — is Layer A / Layer B separation maintained
   or conflated? Is any success criterion numeric when E2 should
   own the number? Does a constraint masquerade as a requirement?
   Are error modes (human-review reject/override/timeout/system-
   unavailable) named in scope?

B. REASONING challenges — did the Producing Agent architect inside
   E1 (violating DISCIPLINE-2)? Did it skip a NOC-bias flag when
   the decision was NOC-shaped? Did it over-read S6?

C. DIRECTION challenges — is convergence state consistent with
   work? Is scope boundary sharp (one canonical product-problem
   statement, not three)?

D. FRAME CHANGE challenges — does the engagement reveal S6 Brief
   is wrong? Flag CRITICAL.

Rules:
- Not sycophantic. DISCIPLINE-2 violations are automatic MAJOR.
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


E1_EXIT_ARTEFACT_TEMPLATE = """\
# E1 — Problem Definition — Exit Artefact

## 0. Status

**Convergence state at exit:** {convergence_state_at_exit}. Ratified.
**Primary derivation intent:** {primary_derivation_intent}
**Cycle id:** {cycle_id}
**Recorded chain entries:** {chain_entries_count}

## 1. Problem definition

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

*End of E1 exit artefact.*
"""


E1_FIDELITY_CRITERIA = (
    "Dual-layer frame (product problem vs delivery-proof problem)"
    " preserved — no conflation.",
    "Canonical product-problem statement is singular; multiple"
    " restatements are a fail.",
    "DISCIPLINE-2 honoured — no architecture, agent-boundary,"
    " orchestration, or tool selection inside E1.",
    "Numeric thresholds (latency, quality) carry TBD with E2 named"
    " as owner; fabricated numbers are a fail.",
    "Human-review-gate error modes are enumerated in scope (approve,"
    " reject, override, timeout, system-unavailable).",
    "First-target-bias flags are explicit so downstream cycles can"
    " audit generalisation claims.",
    "Governance mode declaration is explicit (partial governance by"
    " default under CARRY-FWD-4).",
    "Honesty bound on regulatory standing preserved.",
)


E1_SKILL = Skill(
    skill_id="E1",
    name="Problem Definition",
    producing_system_prompt=E1_PRODUCING_SYSTEM_PROMPT,
    adversarial_system_prompt=E1_ADVERSARIAL_SYSTEM_PROMPT,
    exit_artefact_template=E1_EXIT_ARTEFACT_TEMPLATE,
    fidelity_criteria=E1_FIDELITY_CRITERIA,
    predecessor_skill="S6",
    research_agent_hint=(
        "Read the S6 Solution Brief and any engagement scope documents"
        " the direction cites. Do not spider the web."
    ),
)
