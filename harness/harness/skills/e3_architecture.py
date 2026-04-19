"""E3 Architecture — skill definition.

INPUT-001 §6 SDLC Execution skill 3. E3 takes the E2 requirements
and selects the architecture: agent decomposition, orchestration
framework, model selection, integration + data architecture,
deployment topology, observability surface. Feeds E4 security /
E5 data / E6 build.

Derivation: docs/e3-exit-artefact.md (agent architecture with
framework + model + per-agent shape + coordination timing budget
incl. cold-start, integration arch, data architecture with
two-cluster PG + chain-write bridge, deployment topology,
observability, alternative-architectures-considered section).
"""
from __future__ import annotations

from harness.skills.s1_problem_crystallisation import Skill


E3_PRODUCING_SYSTEM_PROMPT = """\
You are the E3 Architecture Producing Agent in a 4WRD governed
delivery cycle. Your job: select the architecture that E6 Build
will implement, E4 will harden, and E5 will ground in the data
layer.

E3 is the first cycle where architectural selections are made.
DISCIPLINE-2 previously forbade them; E3 is the locus where they
are permitted — and must cite the constraints they resolve.

You produce two separable components:

1. OUTPUT — structured markdown. Required sections:
     - ## 1. Architecture overview (diagram + data-flow + runtime
       boundaries)
     - ## 2. Agent architecture (orchestration framework +
       rationale tied to NFR-L / FR-*; model selection + rationale;
       per-agent shape; coordination timing budget including cold-
       start path and keep-alive mitigation)
     - ## 3. Integration architecture (per external surface:
       interface, auth, error handling, idempotency)
     - ## 4. Data architecture (cluster split, schema outline,
       chain-write bridge, retention, archival)
     - ## 5. Deployment topology (platform selection, resource
       sizing envelope, scaling posture)
     - ## 6. Observability architecture
     - ## 7. Alternative architectures considered (and why they were
       rejected — cite constraint that rejected them)
     - ## 8. E4 / E5 / E6 inheritance surfaces

2. REASONING TRACE — every selection cites the constraints it
   resolves. Name the E2 requirement (FR-*, NFR-*, IR-*, GR-*, CI-*).

Hard rules:
- Every architectural selection is grounded in constraints: state
  'Selection: X. Rationale: FR-Y / NFR-Z requires …'.
- Alternatives considered is mandatory — name what was rejected.
- Coordination timing budget covers BOTH steady-state and cold-start
  paths with named mitigations.
- External egress policies stated at deployment level (no silent
  default-permit).
- Determinism for audit-evidence — state the reconstruction
  property (given same inputs + pinned versions, record is
  reconstructable).

Output format (strict):

<OUTPUT>
...architecture...
</OUTPUT>

<REASONING_TRACE>
1. ...
2. ...
</REASONING_TRACE>
"""


E3_ADVERSARIAL_SYSTEM_PROMPT = """\
You are the E3 Adversarial Agent. Challenge on four axes.

A. OUTPUT challenges — does a selection lack constraint citation?
   Is alternative-considered missing? Is cold-start path ignored?
   Does the deployment topology silently permit external egress?
   Does the data architecture expose a PII-leak surface via chain
   records? Does the timing budget pretend warm state is universal?

B. REASONING challenges — did the Producing Agent over-fit to a
   preferred framework without citing constraints? Did it double-
   count capability of a single mechanism? Did the model selection
   justify itself with license considerations that were not in
   E2?

C. DIRECTION challenges — is the architecture within the E2 scope,
   or has scope crept? Is the coordination budget compatible with
   NFR-L?

D. FRAME CHANGE challenges — does the architecture reveal E2 was
   wrong? Flag CRITICAL.

Rules:
- Not sycophantic. Ungrounded selection → MAJOR. Missing cold-start
  path → MAJOR. Silent external egress → CRITICAL.
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


E3_EXIT_ARTEFACT_TEMPLATE = """\
# E3 — Architecture — Exit Artefact

## 0. Status

**Convergence state at exit:** {convergence_state_at_exit}. Ratified.
**Primary derivation intent:** {primary_derivation_intent}
**Cycle id:** {cycle_id}
**Recorded chain entries:** {chain_entries_count}

## 1. Architecture

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

*End of E3 exit artefact.*
"""


E3_FIDELITY_CRITERIA = (
    "Every architectural selection is grounded in a cited E2"
    " requirement (FR-*, NFR-*, IR-*, GR-*, CI-*).",
    "Alternatives-considered section is present and names the"
    " constraint that rejected each alternative.",
    "Coordination timing budget covers BOTH steady-state and cold-"
    "start paths; keep-alive / warm-up mitigations are explicit.",
    "External egress policies are explicit; no silent default-permit.",
    "Data architecture does not create a PII leak via chain records"
    " (masking / tokenisation / pseudonymisation named).",
    "Determinism-for-audit statement present: given same inputs +"
    " pinned versions, record is reconstructable.",
    "Framework lock-in is named with mitigation (interface"
    " abstraction, thin wrappers).",
    "E4 / E5 / E6 inheritance surfaces are explicit.",
)


E3_SKILL = Skill(
    skill_id="E3",
    name="Architecture",
    producing_system_prompt=E3_PRODUCING_SYSTEM_PROMPT,
    adversarial_system_prompt=E3_ADVERSARIAL_SYSTEM_PROMPT,
    exit_artefact_template=E3_EXIT_ARTEFACT_TEMPLATE,
    fidelity_criteria=E3_FIDELITY_CRITERIA,
    predecessor_skill="E2",
    research_agent_hint=(
        "Consult vendor / platform documentation (model serving,"
        " orchestration framework, deployment platform) only when the"
        " direction cites them. Prefer the E2 artefact and the S6"
        " Brief as primary inputs."
    ),
)
