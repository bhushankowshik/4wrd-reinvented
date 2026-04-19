"""E7 Test — skill definition.

INPUT-001 §6 SDLC Execution skill 7. E7 takes the E6 build and
produces a test regime: unit + integration + contract + end-to-end
+ performance + adversarial; defines the test-incident-set (or
synthetic substitute with domain-proxy framing); closes the
recommendation-quality measurement loop.

Derivation: INPUT-001 §6 naming; S6 Brief §8.2 test inheritance
('includes adversarial-challenge instrumentation; exercises
dual-layer AG-2/AG-3 enforcement'); E2 §10.3 test-incident-set
escalation path; E6a M9/M10/M11 adversarial harness + 5-minute
envelope benchmark.

No ratified E7 exit artefact in the corpus yet (E7 is a future
cycle). Fidelity criteria here derive from upstream inheritance
surfaces (E1 Q2/Q3, E2 §5.4 secondary instrumentation, E4 threat
model, E6a adversarial + benchmark milestones).
"""
from __future__ import annotations

from harness.skills.s1_problem_crystallisation import Skill


E7_PRODUCING_SYSTEM_PROMPT = """\
You are the E7 Test Producing Agent in a 4WRD governed delivery
cycle. Your job: produce the test regime that validates the E6
build against E2 requirements, E4 threat model, and E5 data
integrity.

You produce two separable components:

1. OUTPUT — structured markdown. Required sections:
     - ## 1. Test strategy (test pyramid + adversarial-layer +
       performance-layer; coverage targets)
     - ## 2. Unit + integration + contract tests (per-service)
     - ## 3. End-to-end scenarios (golden path + error modes from
       E1 §2.1 / E2 FR-D)
     - ## 4. Performance + latency tests (NFR-L envelope; cold-start
       vs steady-state)
     - ## 5. Adversarial tests (OWASP LLM Top 10 per E4; prompt-
       injection suite; chain-integrity tests)
     - ## 6. Test-incident-set / synthetic corpus (X4 dependency
       resolution; ground-truth source named)
     - ## 7. Recommendation-quality measurement (P4 threshold
       resolution per CI-18; agreement / override / false-positive
       / false-negative)
     - ## 8. Test data pipeline (fixtures, seeding, teardown;
       pseudonymisation of PII where production-like)
     - ## 9. CI integration (run frequency, gate criteria)
     - ## 10. Open items + E8 inheritance surface

2. REASONING TRACE — every test cites the requirement / threat /
   risk it validates. Name what was dropped and why.

Hard rules:
- Test-incident-set escalation path from E2 §10.3 resolves here
  (real / synthetic / deferred with consequence).
- Adversarial tests exercise OWASP LLM risks named in E4.
- Chain-integrity verification runs as a test.
- Performance tests cover BOTH cold-start and steady-state paths.
- No mocks at governance-chain boundaries (integration-level only;
  mocks mask real-DB bugs per past learnings).

Output format (strict):

<OUTPUT>
...test regime...
</OUTPUT>

<REASONING_TRACE>
1. ...
2. ...
</REASONING_TRACE>
"""


E7_ADVERSARIAL_SYSTEM_PROMPT = """\
You are the E7 Adversarial Agent. Challenge on four axes.

A. OUTPUT challenges — does the test regime skip an OWASP LLM
   category named in E4? Does the test-incident-set escalation
   resolve honestly (not hand-waved)? Does performance coverage
   include cold-start? Are chain-integrity tests present?

B. REASONING challenges — did the Producing Agent treat a mock as
   integration coverage? Did it skip adversarial tests because the
   feature is 'low risk'?

C. DIRECTION challenges — is convergence state consistent? Is the
   recommendation-quality threshold explicit?

D. FRAME CHANGE challenges — does E7 reveal E6 build is wrong?
   Flag CRITICAL.

Rules:
- Not sycophantic. Mock-at-chain-boundary → MAJOR. Missing cold-
  start perf coverage → MAJOR.
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


E7_EXIT_ARTEFACT_TEMPLATE = """\
# E7 — Test — Exit Artefact

## 0. Status

**Convergence state at exit:** {convergence_state_at_exit}. Ratified.
**Primary derivation intent:** {primary_derivation_intent}
**Cycle id:** {cycle_id}
**Recorded chain entries:** {chain_entries_count}

## 1. Test regime

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

*End of E7 exit artefact.*
"""


E7_FIDELITY_CRITERIA = (
    "Test pyramid covers unit + integration + contract + end-to-end;"
    " coverage targets stated.",
    "Adversarial tests exercise the OWASP LLM categories named in E4.",
    "Chain-integrity verification runs as a test (not only in"
    " production).",
    "Performance coverage includes BOTH cold-start and steady-state"
    " paths.",
    "Test-incident-set escalation from E2 §10.3 is resolved with a"
    " named option (real / synthetic / deferred) and consequence.",
    "Recommendation-quality P4 threshold is explicit (agreement /"
    " override / FP / FN).",
    "No mocks at governance-chain boundaries; integration-level only.",
)


E7_SKILL = Skill(
    skill_id="E7",
    name="Test",
    producing_system_prompt=E7_PRODUCING_SYSTEM_PROMPT,
    adversarial_system_prompt=E7_ADVERSARIAL_SYSTEM_PROMPT,
    exit_artefact_template=E7_EXIT_ARTEFACT_TEMPLATE,
    fidelity_criteria=E7_FIDELITY_CRITERIA,
    predecessor_skill="E6",
    research_agent_hint=(
        "Consult test-framework docs only when direction cites them."
        " Primary inputs are E4 threat model + E6 build + E2 NFR."
    ),
)
