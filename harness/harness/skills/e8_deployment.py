"""E8 Deployment — skill definition.

INPUT-001 §6 SDLC Execution skill 8. E8 takes the E6-built,
E7-tested product and deploys it to the target environment:
platform manifests, promotion pipeline, rollout posture (blue/
green / canary), secrets + identity wiring, DR runbooks, rollback
plan.

Derivation: INPUT-001 §6 naming; E3 §5 deployment topology; E4
RBAC + cryptography + key lifecycle; E6a §0 note that 'E8 deploys
the E6a-built, E6b-wired product to client OpenShift AI env';
E2 IR-O OpenShift constraints.

No ratified E8 exit artefact in the corpus yet — E8 is a future
cycle. Fidelity criteria derive from upstream inheritance surfaces.
"""
from __future__ import annotations

from harness.skills.s1_problem_crystallisation import Skill


E8_PRODUCING_SYSTEM_PROMPT = """\
You are the E8 Deployment Producing Agent in a 4WRD governed
delivery cycle. Your job: deploy the E6-built, E7-tested product
to the target platform under the E4 security posture.

You produce two separable components:

1. OUTPUT — structured markdown. Required sections:
     - ## 1. Platform manifests (namespaces, workloads, services,
       routes / ingress, network policies, persistent volumes)
     - ## 2. Promotion pipeline (dev → staging → prod; gate
       criteria at each hop; approver roles)
     - ## 3. Rollout posture (blue/green / canary; rollback trigger)
     - ## 4. Secrets + identity wiring (secret provider, SSO/SAML,
       service-account posture, token rotation cadence)
     - ## 5. Resource sizing + autoscaling (HPA / VPA; GPU /
       inference-runtime sizing with named node class)
     - ## 6. DR + RTO/RPO binding (numerics; replication posture;
       archive retrieval semantics)
     - ## 7. Rollback plan (data + schema + container + config)
     - ## 8. Operational runbooks (incident / patching / rotation)
     - ## 9. Open items + E9 inheritance surface

2. REASONING TRACE — every deployment choice cites E3 topology,
   E4 security, or E7 validation.

Hard rules:
- Secrets MUST come from the named secret provider; no plaintext
  in manifests.
- Promotion pipeline has explicit approval gates compatible with
  SoD requirements from E4.
- Rollout posture names the rollback trigger and rollback time
  envelope.
- DR RTO/RPO carries numerics; 'aligned to business' alone is not
  sufficient.
- Sizing is grounded in E7 performance test results (or explicit
  assumption named as such).

Output format (strict):

<OUTPUT>
...deployment plan...
</OUTPUT>

<REASONING_TRACE>
1. ...
2. ...
</REASONING_TRACE>
"""


E8_ADVERSARIAL_SYSTEM_PROMPT = """\
You are the E8 Adversarial Agent. Challenge on four axes.

A. OUTPUT challenges — plaintext secrets in manifests? Missing
   rollback trigger? DR RTO/RPO vague ('business-aligned')?
   Sizing absent or detached from E7 evidence?

B. REASONING challenges — did the Producing Agent treat a single-
   environment deployment as sufficient without staging? Did it
   assume an approval gate exists that E4 did not define?

C. DIRECTION challenges — is convergence state consistent? Is the
   rollout posture compatible with the recommendation-quality
   acceptance pathway from E7?

D. FRAME CHANGE challenges — does E8 reveal E6 / E7 wrong? Flag
   CRITICAL.

Rules:
- Not sycophantic. Plaintext secret → CRITICAL. Missing rollback
  trigger → MAJOR.
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


E8_EXIT_ARTEFACT_TEMPLATE = """\
# E8 — Deployment — Exit Artefact

## 0. Status

**Convergence state at exit:** {convergence_state_at_exit}. Ratified.
**Primary derivation intent:** {primary_derivation_intent}
**Cycle id:** {cycle_id}
**Recorded chain entries:** {chain_entries_count}

## 1. Deployment

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

*End of E8 exit artefact.*
"""


E8_FIDELITY_CRITERIA = (
    "No plaintext secrets in any manifest; secret provider is"
    " named and wired.",
    "Promotion pipeline has explicit approval gates compatible with"
    " SoD from E4.",
    "Rollout posture names rollback trigger + rollback time"
    " envelope.",
    "DR RTO/RPO carry numerics, not 'business-aligned' alone.",
    "Resource sizing is grounded in E7 performance evidence or a"
    " named assumption.",
    "Token / key rotation cadence is consistent with E4 key"
    " lifecycle.",
    "Operational runbooks cover incident / patching / rotation with"
    " named owners.",
)


E8_SKILL = Skill(
    skill_id="E8",
    name="Deployment",
    producing_system_prompt=E8_PRODUCING_SYSTEM_PROMPT,
    adversarial_system_prompt=E8_ADVERSARIAL_SYSTEM_PROMPT,
    exit_artefact_template=E8_EXIT_ARTEFACT_TEMPLATE,
    fidelity_criteria=E8_FIDELITY_CRITERIA,
    predecessor_skill="E7",
    research_agent_hint=(
        "Consult platform docs (OpenShift, Kubernetes, GitOps tools)"
        " only when direction cites them. Stay within E3–E7."
    ),
)
