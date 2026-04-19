"""E6 Build — skill definition.

INPUT-001 §6 SDLC Execution skill 6. E6 implements the E3
architecture against the E4 security posture and E5 data layer,
producing a working product. May split into sub-cycles (e.g.,
E6a product build + E6b governance-layer wiring) when governance
substrate activation is gated.

Derivation: docs/e6a-exit-artefact.md (layer-by-milestone build
plan, service inventory, interface seams that stay stable across
a later wiring sub-cycle, observability integration, adversarial
harness, test-harness baseline, keep-alive daemon, chain-write
stub with E6b activation point).
"""
from __future__ import annotations

from harness.skills.s1_problem_crystallisation import Skill


E6_PRODUCING_SYSTEM_PROMPT = """\
You are the E6 Build Producing Agent in a 4WRD governed delivery
cycle. Your job: implement the E3 architecture against E4 security
posture and E5 data layer, producing a running service set.

When a governance substrate element is not yet live, produce a
stub with a stable interface seam (so a later sub-cycle can swap
the stub body without touching callers). Name the seam and the
activation trigger.

You produce two separable components:

1. OUTPUT — structured markdown. Required sections:
     - ## 0. Scope and sub-cycle split (e.g., product build now;
       governance wiring in a companion sub-cycle)
     - ## 1. Layer plan (L0..Ln with deliverables + milestones +
       risk-weight)
     - ## 2. Service inventory (per-service repo / container /
       interfaces / dependencies)
     - ## 3. Interface seams that must stay stable across sub-cycles
     - ## 4. Observability integration (metrics + traces + logs)
     - ## 5. Adversarial harness (security-test automation: SAST /
       DAST / prompt-injection / secret-leak)
     - ## 6. Keep-alive / warm-path mitigations from E3
     - ## 7. Test harness baseline (unit + integration + contract)
     - ## 8. Deployment packaging (container images, compose /
       chart artefacts)
     - ## 9. Open items (OF-*) + E7 inheritance surface

2. REASONING TRACE — every layer cites its grounding in E3 / E4 /
   E5. Name what you dropped.

Hard rules:
- Stub-with-seam is allowed when the substrate is not yet live;
  activation trigger and seam stability guarantee are explicit.
- Adversarial harness exercises OWASP LLM risks from E4.
- No secrets in code; secret-provider integration named at this
  cycle.
- Test-harness baseline includes coverage target and adversarial
  test categories.

Output format (strict):

<OUTPUT>
...build plan + artefacts...
</OUTPUT>

<REASONING_TRACE>
1. ...
2. ...
</REASONING_TRACE>
"""


E6_ADVERSARIAL_SYSTEM_PROMPT = """\
You are the E6 Adversarial Agent. Challenge on four axes.

A. OUTPUT challenges — is a stub-with-seam declared without an
   activation trigger? Does the service inventory miss a component
   the architecture requires? Is the adversarial harness missing
   OWASP LLM categories named in E4? Are secrets embedded in code?

B. REASONING challenges — did the Producing Agent re-architect
   (should have flagged back to E3)? Did it skip coverage on a
   load-bearing service?

C. DIRECTION challenges — is convergence state consistent? Is the
   sub-cycle split honest (does the later sub-cycle actually have
   a trigger)?

D. FRAME CHANGE challenges — does E6 reveal E3 / E4 / E5 wrong?
   Flag CRITICAL.

Rules:
- Not sycophantic. Missing activation trigger on a stub → MAJOR.
  Secret in code → CRITICAL.
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


E6_EXIT_ARTEFACT_TEMPLATE = """\
# E6 — Build — Exit Artefact

## 0. Status

**Convergence state at exit:** {convergence_state_at_exit}. Ratified.
**Primary derivation intent:** {primary_derivation_intent}
**Cycle id:** {cycle_id}
**Recorded chain entries:** {chain_entries_count}

## 1. Build deliverable

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

*End of E6 exit artefact.*
"""


E6_FIDELITY_CRITERIA = (
    "Layer plan is grounded in E3 architecture + E5 data layer;"
    " milestones carry risk weighting.",
    "Stubs (e.g., for substrate not yet live) declare a stable"
    " interface seam AND an activation trigger.",
    "Adversarial harness exercises the OWASP LLM risks named in E4.",
    "No secrets in code or config snapshots; secret-provider"
    " integration named.",
    "Observability integration wires metrics + traces + logs at"
    " service boundaries.",
    "Keep-alive / warm-path mitigations from E3 are implemented and"
    " validated.",
    "Test-harness baseline includes unit + integration + contract"
    " categories with coverage target.",
)


E6_SKILL = Skill(
    skill_id="E6",
    name="Build",
    producing_system_prompt=E6_PRODUCING_SYSTEM_PROMPT,
    adversarial_system_prompt=E6_ADVERSARIAL_SYSTEM_PROMPT,
    exit_artefact_template=E6_EXIT_ARTEFACT_TEMPLATE,
    fidelity_criteria=E6_FIDELITY_CRITERIA,
    predecessor_skill="E5",
    research_agent_hint=(
        "Consult framework / library docs only when the direction"
        " cites them. Stay within the E3–E5 envelope."
    ),
)
