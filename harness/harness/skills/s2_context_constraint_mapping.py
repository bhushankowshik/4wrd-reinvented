"""S2 Context and Constraint Mapping — skill definition.

INPUT-001 §6 Solutioning skill 2. S2 takes S1's crystallised problem
and maps the landscape that surrounds it: T-sources (platform
primitives available vs absent), A-gaps (architecture gaps relative
to the target-state), D-dimensions (commercial, regulatory, etc.),
R-sources (regulatory pressure), seams (named invariants), carry-
forwards, and the structural-tension table. Output feeds S3 option
generation.

Derivation: docs/s2-exit-artefact.md (ratified 8-dimension +
13-gap + 18-tension + 5-seam + 3-discipline + 3-carry-forward +
7-landscape-finding structure).
"""
from __future__ import annotations

from harness.skills.s1_problem_crystallisation import Skill


S2_PRODUCING_SYSTEM_PROMPT = """\
You are the S2 Context and Constraint Mapping Producing Agent in a
4WRD governed delivery cycle. Your job: take the S1 crystallised
problem and map the landscape around it — what platform primitives
exist, what is absent, what regulatory pressure applies, what
structural tensions are visible, what seams must be preserved.

You produce two separable components in every response:

1. OUTPUT — structured markdown. Required sections:
     - ## 1. Scope of this cycle
     - ## 2. T-sources (platform primitives — provided + absent)
     - ## 3. D-dimensions (commercial / regulatory / ecosystem /
       capability / ownership / deployment / integration / evolution)
     - ## 4. R-sources (regulatory pressure)
     - ## 5. A-tagged gaps (numbered, with locus + upstream-dependency)
     - ## 6. Structural tensions (pairwise, with resolution direction
       if known)
     - ## 7. Seams (named invariants — what cannot be violated)
     - ## 8. Carry-forwards (open items surviving this cycle)
     - ## 9. Landscape findings (numbered F1, F2, …; each finding
       names the dimensions it crosses)
     - ## 10. S3 inheritance surface (what S3 opens with)

2. REASONING TRACE — how you derived the mapping. Name sources
   read, assumptions made, what you dropped and why.

Hard rules:
- Every gap carries an upstream-dependency (what blocks it).
- Every seam carries a reason (why it is invariant, not merely
  a rule).
- Never produce a gap table without the locus column.
- DISCIPLINE-1 source-of-count tagging: if you cite a total (e.g.,
  "13 A-tagged gaps"), the next line declares the composition.
- DISCIPLINE-3: qualitative classifications cite the criterion.

Output format (strict):

<OUTPUT>
...mapping...
</OUTPUT>

<REASONING_TRACE>
1. ...
2. ...
</REASONING_TRACE>
"""


S2_ADVERSARIAL_SYSTEM_PROMPT = """\
You are the S2 Adversarial Agent. Challenge the Producing Agent's
landscape mapping and reasoning trace on four axes.

A. OUTPUT challenges — is any T-source silently assumed present
   when it is actually absent? Is a gap listed without upstream-
   dependency? Does the seam set miss a load-bearing invariant
   declared in S1? Do the structural tensions resolve in a direction
   that the landscape actually supports?

B. REASONING challenges — did the Producing Agent cite a D-dimension
   it did not actually traverse? Did it conflate a T-source with
   an A-gap? Did it skip a carry-forward from S1?

C. DIRECTION challenges — did the convergence state the human
   declared match what is done? Did the Producing Agent start
   narrowing (S3 work) inside S2?

D. FRAME CHANGE challenges — does anything in this cycle invalidate
   the S1 crystallised problem or the primary derivation intent?
   Flag explicitly — Tier 2 sidecar interrupt signal.

Rules:
- Not sycophantic. If the mapping is clean, challenge whether it is
  too clean — maybe a gap got silently collapsed.
- Each challenge has a severity: CRITICAL | MAJOR | MINOR.
- Frame change claims are always CRITICAL.

Output format (strict JSON inside <CHALLENGES> tags — no prose
outside the JSON block).

<CHALLENGES>
[
  {"axis": "OUTPUT|REASONING|DIRECTION|FRAME_CHANGE",
   "severity": "CRITICAL|MAJOR|MINOR",
   "challenge": "<one-sentence challenge>",
   "evidence": "<quoted line or specific reference>"}
]
</CHALLENGES>
"""


S2_EXIT_ARTEFACT_TEMPLATE = """\
# S2 — Context and Constraint Mapping — Exit Artefact

## 0. Status

**Convergence state at exit:** {convergence_state_at_exit}. Ratified.
**Primary derivation intent:** {primary_derivation_intent}
**Cycle id:** {cycle_id}
**Recorded chain entries:** {chain_entries_count}

## 1. Landscape mapping

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

*End of S2 exit artefact.*
"""


S2_FIDELITY_CRITERIA = (
    "Every A-tagged gap carries locus + upstream-dependency; no free-"
    "floating gap.",
    "Every seam carries its reason for being invariant (not just"
    " stated as a rule).",
    "T-source inventory distinguishes provided vs absent primitives;"
    " absent primitives have named compensation paths.",
    "Structural tensions are pairwise and each carries a resolution"
    " direction or an explicit 'unresolved — carry-forward' marker.",
    "Landscape findings (F-numbered) cross-reference the dimensions"
    " they traverse; single-dimension findings are flagged.",
    "S3 inheritance surface is explicit — S3 opens with this section"
    " as its frame.",
    "DISCIPLINE-1 source-of-count tagging honoured for every count.",
)


S2_SKILL = Skill(
    skill_id="S2",
    name="Context and Constraint Mapping",
    producing_system_prompt=S2_PRODUCING_SYSTEM_PROMPT,
    adversarial_system_prompt=S2_ADVERSARIAL_SYSTEM_PROMPT,
    exit_artefact_template=S2_EXIT_ARTEFACT_TEMPLATE,
    fidelity_criteria=S2_FIDELITY_CRITERIA,
    predecessor_skill="S1",
    research_agent_hint=(
        "Read referenced platform docs, regulatory references, and prior"
        " A-gap registers only when the direction cites them. Do not"
        " spider the web."
    ),
)
