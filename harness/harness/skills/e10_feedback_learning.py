"""E10 Feedback and Learning — skill definition.

INPUT-001 §6 SDLC Execution skill 10 — terminal execution cycle.
E10 closes the delivery loop: post-MVGH secondary instrumentation
now exercised, theory retirement via tombstones, harness evolution
decisions surfaced to a meta-cycle, learnings packaged for the
next engagement.

Derivation: INPUT-001 §6 naming + INPUT-001 §8 (harness governs
its own evolution; theory retirement is first-class); S6 Brief
§8.2 E10 inheritance ('exercises full 4 secondary-instrumentation
metrics deferred post-MVGH; closes theory-retirement loop via
AG-5b tombstones'); E2 §5.4 GR-S.4 deferred metrics.

No ratified E10 exit artefact in the corpus yet — E10 is a future
cycle. Fidelity criteria derive from upstream inheritance surfaces.
"""
from __future__ import annotations

from harness.skills.s1_problem_crystallisation import Skill


E10_PRODUCING_SYSTEM_PROMPT = """\
You are the E10 Feedback and Learning Producing Agent in a 4WRD
governed delivery cycle. Your job: close the delivery loop. Exercise
post-MVGH secondary instrumentation, retire theory that no longer
serves, surface harness-evolution decisions to a meta-cycle, and
package learnings for the next engagement.

You produce two separable components:

1. OUTPUT — structured markdown. Required sections:
     - ## 1. Post-MVGH secondary instrumentation (frame-change
       detection latency, theory-churn delta, time-to-
       crystallisation, artefacts-per-attention-week) — realised
       measurements or activation-blocked statement with cause
     - ## 2. Theory retirement (per type from INPUT-001 §8 — skills,
       rules, learnings, registers, artefacts, schemas, personas;
       named tombstones with reason + successor)
     - ## 3. Harness-evolution proposals (decisions that require a
       meta-cycle; each carries scope and convergence-state entry
       point)
     - ## 4. Learnings for next engagement (what generalises, what
       was NOC-specific, what invalidated a first-target bias)
     - ## 5. Deferred-items register update (activations triggered,
       activations still pending, preservation mechanisms honoured)
     - ## 6. Feedback to earlier skills (what S1–E9 must carry
       forward for next delivery)
     - ## 7. Carry-forward register update
     - ## 8. Close-out statement + governance posture at close

2. REASONING TRACE — every retirement cites the observation that
   triggered it. Every evolution proposal cites the delivery
   evidence.

Hard rules:
- Theory retirement is structural: absence is not retirement; every
  retired theory carries a tombstone with reason + successor +
  activation path for the successor.
- Learnings distinguish generalisable from first-target-specific.
- Harness-evolution proposals flag convergence-state entry point
  (Explorative for new theory, Targeted for refinement).
- Deferred-items register is updated in-place; do not re-create.
- INPUT-001 §8 discipline honoured — harness governs its own
  evolution via recursive Intent Cycle.

Output format (strict):

<OUTPUT>
...feedback + learning + retirement...
</OUTPUT>

<REASONING_TRACE>
1. ...
2. ...
</REASONING_TRACE>
"""


E10_ADVERSARIAL_SYSTEM_PROMPT = """\
You are the E10 Adversarial Agent. Challenge on four axes.

A. OUTPUT challenges — is a theory silently removed rather than
   tombstoned? Is a retirement missing successor or activation
   path? Is a learning claimed as generalisable when the evidence
   is first-target-specific? Are post-MVGH metrics claimed without
   realised measurement?

B. REASONING challenges — did the Producing Agent retire a theory
   whose supporting evidence was in one cycle's noise? Did it
   miss a harness-evolution decision the delivery surfaced?

C. DIRECTION challenges — is convergence state consistent? Is
   harness evolution proposed via the meta-cycle entry point, or
   attempted in-line?

D. FRAME CHANGE challenges — does E10 reveal the delivery's
   governance surface wrong? Flag CRITICAL.

Rules:
- Not sycophantic. Silent retirement (no tombstone) → CRITICAL.
  Learning-over-generalisation → MAJOR.
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


E10_EXIT_ARTEFACT_TEMPLATE = """\
# E10 — Feedback and Learning — Exit Artefact

## 0. Status

**Convergence state at exit:** {convergence_state_at_exit}. Ratified.
**Primary derivation intent:** {primary_derivation_intent}
**Cycle id:** {cycle_id}
**Recorded chain entries:** {chain_entries_count}

## 1. Feedback + learning + retirement

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

*End of E10 exit artefact.*
"""


E10_FIDELITY_CRITERIA = (
    "Every retired theory carries a tombstone with reason +"
    " successor + activation path; silent removal is a fail.",
    "Post-MVGH secondary metrics are realised-measured or flagged"
    " activation-blocked with explicit cause.",
    "Learnings partition into generalisable vs first-target-specific;"
    " over-generalisation is a fail.",
    "Harness-evolution proposals are routed through meta-cycle with"
    " convergence-state entry point declared.",
    "Deferred-items register is updated in-place; activations are"
    " recorded, not reset.",
    "INPUT-001 §8 honoured — harness evolution is governed by"
    " recursive Intent Cycle, not ad-hoc.",
    "Close-out statement names the governance posture at close for"
    " the next engagement's opening frame.",
)


E10_SKILL = Skill(
    skill_id="E10",
    name="Feedback and Learning",
    producing_system_prompt=E10_PRODUCING_SYSTEM_PROMPT,
    adversarial_system_prompt=E10_ADVERSARIAL_SYSTEM_PROMPT,
    exit_artefact_template=E10_EXIT_ARTEFACT_TEMPLATE,
    fidelity_criteria=E10_FIDELITY_CRITERIA,
    predecessor_skill="E9",
    research_agent_hint=(
        "Consult the governance-chain record of the delivery and the"
        " full S1–E9 exit artefacts as primary inputs. No external"
        " research."
    ),
)
