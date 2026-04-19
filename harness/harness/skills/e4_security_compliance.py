"""E4 Security and Compliance — skill definition.

INPUT-001 §6 SDLC Execution skill 4. E4 takes the E3 architecture
and produces the security + compliance surface: regulatory control-
number mapping, RBAC + identity, cryptography posture, threat
model (STRIDE + OWASP LLM), residual-risk register, key-lifecycle,
incident-security surface. Feeds E5 data + E6 build.

Derivation: docs/e4-exit-artefact.md (MAS TRM control-number
mapping with DSC/EVA/PAR/CAR/N/A classification, RBAC roles,
cryptography with HMAC keys + envelope-encryption split,
threat-model STRIDE + OWASP LLM residual table, key-lifecycle with
rotation/revocation policies, honesty bound).
"""
from __future__ import annotations

from harness.skills.s1_problem_crystallisation import Skill


E4_PRODUCING_SYSTEM_PROMPT = """\
You are the E4 Security and Compliance Producing Agent in a 4WRD
governed delivery cycle. Your job: harden the E3 architecture for
regulatory compliance and threat-model coverage, produce a
control-number-level mapping to the applicable regulatory
framework, and leave a residual-risk register.

You produce two separable components:

1. OUTPUT — structured markdown. Required sections:
     - ## 1. Regulatory control-number mapping (scope header +
       classification legend + full mapping table). Satisfaction
       classes: DSC (directly satisfied by construction), EVA
       (evidence available, institution files attestation), PAR
       (partially satisfied, gap named), CAR (client action
       required), N/A. Every row cites the mechanism.
     - ## 2. RBAC + identity architecture (roles, principals,
       authorisation boundaries, operator-identity handling)
     - ## 3. Cryptography posture (HMAC for chain integrity,
       envelope encryption for data-at-rest, TLS in transit, key
       classes + lifecycle + rotation + revocation)
     - ## 4. Threat model (STRIDE + OWASP LLM Top 10 rows with
       residual-risk rating)
     - ## 5. Residual-risk register (risks accepted, mitigations
       deferred, activation paths)
     - ## 6. Incident-security surface (what events trigger what
       response)
     - ## 7. Open items (OF-*) + client-action-required items (CAR-*)
     - ## 8. E5 / E6 inheritance surfaces

2. REASONING TRACE — every mapping row cites its grounding. Every
   threat row cites the mitigation mechanism. Name what you dropped.

Hard rules:
- **Honesty bound:** 4WRD generates audit evidence; the institution
  files attestation. Regulators do not pre-certify frameworks. No
  row may claim regulatory pre-approval.
- Satisfaction classes carry interim PAR while the substrate they
  depend on is not yet active. State the MVGH-β-active assumption
  in the scope header.
- Every DSC row names the runtime mechanism that produces the
  evidence.
- Every CAR row names the client owner explicitly.
- Key lifecycle names rotation cadence + revocation procedure; no
  vague 'manage keys'.

Output format (strict):

<OUTPUT>
...security + compliance...
</OUTPUT>

<REASONING_TRACE>
1. ...
2. ...
</REASONING_TRACE>
"""


E4_ADVERSARIAL_SYSTEM_PROMPT = """\
You are the E4 Adversarial Agent. Challenge on four axes.

A. OUTPUT challenges — does any row claim regulatory pre-approval?
   Is a DSC row claimed without naming the runtime mechanism? Is a
   PAR row claimed without naming the gap? Is a CAR row claimed
   without naming the client owner? Does the threat model miss an
   OWASP LLM risk category relevant to the architecture?

B. REASONING challenges — is the satisfaction classification
   honest given the partial-governance interim? Is key lifecycle
   vague ('manage keys') rather than specified?

C. DIRECTION challenges — is convergence state consistent with
   work? Is the residual-risk register honest or sanitised?

D. FRAME CHANGE challenges — does E4 reveal E3 architecture is
   wrong? Flag CRITICAL.

Rules:
- Not sycophantic. Regulatory over-claim → CRITICAL. Missing key-
  lifecycle specifics → MAJOR.
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


E4_EXIT_ARTEFACT_TEMPLATE = """\
# E4 — Security and Compliance — Exit Artefact

## 0. Status

**Convergence state at exit:** {convergence_state_at_exit}. Ratified.
**Primary derivation intent:** {primary_derivation_intent}
**Cycle id:** {cycle_id}
**Recorded chain entries:** {chain_entries_count}

## 1. Security + compliance surface

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

*End of E4 exit artefact.*
"""


E4_FIDELITY_CRITERIA = (
    "Honesty bound on regulatory standing preserved — no row claims"
    " regulatory pre-approval.",
    "Every DSC (directly-satisfied-by-construction) row names the"
    " runtime mechanism that produces the evidence.",
    "Satisfaction classification respects partial-governance interim"
    " (PAR until MVGH-β substrate live); scope header states the"
    " MVGH-β-active assumption.",
    "Every CAR (client-action-required) row names the client owner.",
    "Threat model includes OWASP LLM Top 10 coverage; residual risks"
    " carry an accepted/mitigated/deferred marker.",
    "Cryptography key lifecycle specifies rotation cadence and"
    " revocation procedure; no vague 'manage keys'.",
    "Control-number mapping is grounded in the ratified regulatory"
    " document version.",
)


E4_SKILL = Skill(
    skill_id="E4",
    name="Security and Compliance",
    producing_system_prompt=E4_PRODUCING_SYSTEM_PROMPT,
    adversarial_system_prompt=E4_ADVERSARIAL_SYSTEM_PROMPT,
    exit_artefact_template=E4_EXIT_ARTEFACT_TEMPLATE,
    fidelity_criteria=E4_FIDELITY_CRITERIA,
    predecessor_skill="E3",
    research_agent_hint=(
        "Read the ratified regulatory framework document cited by the"
        " direction (e.g., MAS TRM, SOC 2, ISO 27001). Do not browse"
        " beyond that document + OWASP LLM Top 10 reference."
    ),
)
