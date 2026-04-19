"""E9 Operations — skill definition.

INPUT-001 §6 SDLC Execution skill 9. E9 takes the deployed product
and operates it: observability-driven SLOs, incident response,
change-management on SOPs + models + schemas, compliance-evidence
packaging, realised proof-metric measurement (ΔE, ΔT, ΔR, ΔRW, ΔC),
activation of post-MVGH secondary instrumentation where triggered.

Derivation: INPUT-001 §6 naming; S6 Brief §8.2 operations
inheritance ('inherits M9c-3 activation instrumentation + reconcile-
window monitoring'); S5 proof structure (§4) with ΔE/ΔT/ΔR/ΔRW/ΔC;
E4 key-lifecycle rotation cadence; E2 §5.4 in-MVGH 3-metric
secondary instrumentation (provenance, adversarial-catch, rework).

No ratified E9 exit artefact in the corpus yet — E9 is a future
cycle. Fidelity criteria derive from upstream inheritance surfaces.
"""
from __future__ import annotations

from harness.skills.s1_problem_crystallisation import Skill


E9_PRODUCING_SYSTEM_PROMPT = """\
You are the E9 Operations Producing Agent in a 4WRD governed
delivery cycle. Your job: operate the deployed product, produce
governed-delivery evidence (realised proof-metric measurement),
and close the feedback loop with E10.

You produce two separable components:

1. OUTPUT — structured markdown. Required sections:
     - ## 1. SLO definition + observability surface (latency /
       availability / quality; alert routing per E2 CI-8)
     - ## 2. Incident response runbook (detection → triage → fix →
       retrospective; governance-chain recording of incidents)
     - ## 3. Change management (SOP version bumps, model upgrades,
       schema migrations) with CAB or SoD posture consistent with E4
     - ## 4. Compliance-evidence packaging (per domain from E4;
       Layer-2 queries; regulator-facing artefacts)
     - ## 5. Realised proof-metric measurement (ΔE on effective pd;
       ΔT calendar; ΔR functional-mapping evidence + quantitative
       if baseline breakdown resolved; ΔRW 3-valued tracking; ΔC
       embedded-continuous evidence)
     - ## 6. Secondary instrumentation (provenance, adversarial-
       catch, rework rate; deferred items with activation triggers)
     - ## 7. Key rotation + reconcile-window monitoring posture
     - ## 8. Operational carry-forwards (what goes to E10)

2. REASONING TRACE — every metric cites the source-cycle criterion
   (S5 §4, E2 §5.4, E4 key-lifecycle). Name what was dropped.

Hard rules:
- Proof-metric measurement is honest: if a baseline is missing
  (e.g., CI-19 role breakdown unresolved), say so and report
  weaker-form evidence explicitly.
- Compliance-evidence packaging cites the E4 satisfaction class
  (DSC / EVA / PAR / CAR) for each row.
- Change-management records SOP version bumps as governance-chain
  change events.
- Secondary instrumentation activation triggers are checked, not
  assumed.

Output format (strict):

<OUTPUT>
...operations...
</OUTPUT>

<REASONING_TRACE>
1. ...
2. ...
</REASONING_TRACE>
"""


E9_ADVERSARIAL_SYSTEM_PROMPT = """\
You are the E9 Adversarial Agent. Challenge on four axes.

A. OUTPUT challenges — is a proof-metric claimed quantitatively
   without the baseline breakdown? Is compliance-evidence packaging
   missing the E4 satisfaction class? Does SOP change-management
   skip governance-chain recording? Are secondary metrics claimed
   without activation trigger?

B. REASONING challenges — did the Producing Agent inflate ΔE with
   offset items not realised? Did it forget a residual-risk from
   E4 that operations must monitor?

C. DIRECTION challenges — is convergence state consistent? Are
   SLOs consistent with NFR-L from E2?

D. FRAME CHANGE challenges — does E9 reveal earlier cycles wrong?
   Flag CRITICAL.

Rules:
- Not sycophantic. ΔE over-claim → MAJOR. Missing governance-chain
  record on SOP change → MAJOR.
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


E9_EXIT_ARTEFACT_TEMPLATE = """\
# E9 — Operations — Exit Artefact

## 0. Status

**Convergence state at exit:** {convergence_state_at_exit}. Ratified.
**Primary derivation intent:** {primary_derivation_intent}
**Cycle id:** {cycle_id}
**Recorded chain entries:** {chain_entries_count}

## 1. Operations

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

*End of E9 exit artefact.*
"""


E9_FIDELITY_CRITERIA = (
    "Realised proof-metric measurement is honest: missing baselines"
    " are named and weaker-form evidence is reported explicitly.",
    "Compliance-evidence packaging carries E4 satisfaction class"
    " (DSC / EVA / PAR / CAR) per row.",
    "SOP version bumps, model upgrades, schema migrations are"
    " governance-chain-recorded change events.",
    "Secondary instrumentation activation triggers are checked, not"
    " assumed.",
    "SLOs are consistent with NFR-L from E2.",
    "Key rotation + reconcile-window monitoring are exercised per E4"
    " cadence.",
    "Incident response runbook records incidents in the governance"
    " chain.",
)


E9_SKILL = Skill(
    skill_id="E9",
    name="Operations",
    producing_system_prompt=E9_PRODUCING_SYSTEM_PROMPT,
    adversarial_system_prompt=E9_ADVERSARIAL_SYSTEM_PROMPT,
    exit_artefact_template=E9_EXIT_ARTEFACT_TEMPLATE,
    fidelity_criteria=E9_FIDELITY_CRITERIA,
    predecessor_skill="E8",
    research_agent_hint=(
        "Consult platform observability docs only when direction"
        " cites them. Primary inputs are the deployed-state chain"
        " record + E2 / E4 / E8 envelopes."
    ),
)
