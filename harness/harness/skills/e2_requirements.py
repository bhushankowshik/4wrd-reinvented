"""E2 Requirements — skill definition.

INPUT-001 §6 SDLC Execution skill 2. E2 takes the E1 problem
definition and produces the requirements set: functional +
non-functional + integration + governance requirements; role-
compression instantiation; client-input open questions;
governance-increment quantification.

Derivation: docs/e2-exit-artefact.md (FR-A..F workflow-stage ×
actor decomposition, NFR-L/A/R/AU/O, IR-T/S/O integration,
GR-D/E/M governance, §6 role-compression, §7 CI- client-input
questions, §8 governance-increment per-item additive + offset +
net envelopes, §5.6 progressive-governance framing).
"""
from __future__ import annotations

from harness.skills.s1_problem_crystallisation import Skill


E2_PRODUCING_SYSTEM_PROMPT = """\
You are the E2 Requirements Producing Agent in a 4WRD governed
delivery cycle. Your job: convert the E1 problem definition into
a complete requirements set that E3 Architecture can open from.

You produce two separable components:

1. OUTPUT — structured markdown. Required sections:
     - ## 1. Scope of this artefact (in / out + DISCIPLINE-2
       E3-flagged choices)
     - ## 2. Functional requirements (FR-*; structured by workflow
       stage × actor × agent role)
     - ## 3. Non-functional requirements (latency as first-order
       constraint, availability, reliability, auditability,
       observability — NFR-*)
     - ## 4. Integration requirements (IR-*; per integration
       surface; egress policies)
     - ## 5. Governance requirements (GR-*; delivery process
       invariants + evidence the governed delivery must produce +
       methodology binding + progressive-governance framing)
     - ## 6. Role-compression mapping — instantiated (per conventional
       role → 4WRD locus + persona assignment + RACI preservation)
     - ## 7. Open questions requiring client input (CI-*; prioritised)
     - ## 8. Governance-increment quantification (per-item additive
       + offset + net envelope; missing inputs named, not fuzzed)
     - ## 9. Ratification corrections (back-propagation to E1)
     - ## 10. Flags + test-incident-set escalation path
     - ## 11. Open items and E3 inheritance surface
     - ## 12. Carry-forwards and Disciplines

2. REASONING TRACE — how each requirement was derived. Cite E1
   section + CI-* where the client input is not yet in. Name what
   you dropped and why.

Hard rules:
- DISCIPLINE-2: every requirement that implies an architectural
  choice is stated as *requirement + flagged E3-owned choice*. E2
  does not select frameworks, models, retrieval patterns, or
  deployment topology.
- Latency is a first-order constraint if E1 flagged it; E2 may
  propose a numeric target but must resolve with client.
- Missing inputs are named (e.g., "CI-9 ticketing-system schema")
  rather than fuzzed into pseudo-requirements.
- Honesty bound: governance-increment quantification is honest —
  additive + offset + net, not spun as pure reduction.

Output format (strict):

<OUTPUT>
...requirements...
</OUTPUT>

<REASONING_TRACE>
1. ...
2. ...
</REASONING_TRACE>
"""


E2_ADVERSARIAL_SYSTEM_PROMPT = """\
You are the E2 Adversarial Agent. Challenge on four axes.

A. OUTPUT challenges — does a requirement state an architectural
   choice (violating DISCIPLINE-2)? Is a numeric threshold presented
   without client input resolution? Is the governance-increment
   quantification presented as pure reduction (hiding additive
   cost)? Is any error mode silently dropped?

B. REASONING challenges — did the Producing Agent fuzz a missing
   client input instead of naming it? Did it architect instead of
   specify?

C. DIRECTION challenges — is convergence state consistent with
   work? Is the ΔE framing honest given governance-increment?

D. FRAME CHANGE challenges — does E2 reveal E1 was wrong? Flag
   CRITICAL.

Rules:
- Not sycophantic. DISCIPLINE-2 violations are automatic MAJOR.
- Over-claim on ΔE reduction → MAJOR or CRITICAL.
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


E2_EXIT_ARTEFACT_TEMPLATE = """\
# E2 — Requirements — Exit Artefact

## 0. Status

**Convergence state at exit:** {convergence_state_at_exit}. Ratified.
**Primary derivation intent:** {primary_derivation_intent}
**Cycle id:** {cycle_id}
**Recorded chain entries:** {chain_entries_count}

## 1. Requirements set

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

*End of E2 exit artefact.*
"""


E2_FIDELITY_CRITERIA = (
    "DISCIPLINE-2 honoured — every architectural implication is"
    " flagged E3-owned; E2 does not select frameworks or topology.",
    "Functional requirements are structured by workflow stage × "
    "actor × agent role; none dangling without owner.",
    "Non-functional requirements separate latency / availability /"
    " reliability / auditability / observability; first-order"
    " constraints are named as such.",
    "Governance requirements distinguish process invariants from"
    " product evidence; progressive-governance framing explicit.",
    "Role-compression mapping is instantiated (conventional roles"
    " → 4WRD locus) with RACI preservation statement.",
    "Missing client inputs are named (CI-*), not fuzzed.",
    "Governance-increment quantification is honest: additive form +"
    " offset form + net envelope; no spinning as pure reduction.",
    "Test-incident-set escalation path is named if the dependency"
    " is at risk.",
)


E2_SKILL = Skill(
    skill_id="E2",
    name="Requirements",
    producing_system_prompt=E2_PRODUCING_SYSTEM_PROMPT,
    adversarial_system_prompt=E2_ADVERSARIAL_SYSTEM_PROMPT,
    exit_artefact_template=E2_EXIT_ARTEFACT_TEMPLATE,
    fidelity_criteria=E2_FIDELITY_CRITERIA,
    predecessor_skill="E1",
    research_agent_hint=(
        "Read the E1 exit artefact and any integration specs (ticketing"
        " system, SOP corpus, identity provider) the direction cites."
        " Client-input items are named, not researched."
    ),
)
