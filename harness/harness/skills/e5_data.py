"""E5 Data — skill definition.

INPUT-001 §6 SDLC Execution skill 5. E5 completes the data layer
the E3 architecture + E4 security posture imply: concrete schemas,
retention and archival, append-only + integrity triggers, cross-
cluster referential discipline, synthetic-corpus strategy where
test-data is scarce. Feeds E6 build and E7 test.

Derivation: docs/e5-exit-artefact.md (namespace + cluster table
inventory, per-table DDL with constraints + indexes + partitioning,
governance_chain append-only trigger, identity map access log,
integrity check results, synthetic corpus strategy, cross-cluster
logical FK policy, retention + archival pipeline).
"""
from __future__ import annotations

from harness.skills.s1_problem_crystallisation import Skill


E5_PRODUCING_SYSTEM_PROMPT = """\
You are the E5 Data Producing Agent in a 4WRD governed delivery
cycle. Your job: concretise the data layer implied by the E3
architecture and the E4 security posture.

DISCIPLINE-2: E5 does not make architectural selections; those
are E3-owned. E5 works inside the ratified E3 + E4 envelope.

You produce two separable components:

1. OUTPUT — structured markdown. Required sections:
     - ## 1. Complete data model (per-cluster / per-namespace table
       inventory + DDL outline; named constraints; indexes;
       partitioning; vector dimensions where applicable)
     - ## 2. Append-only + integrity controls (triggers, signing
       columns, chain-integrity verification job)
     - ## 3. Cross-cluster referential discipline (logical FK
       policy; reconciliation cadence; mismatch-event semantics)
     - ## 4. Retention + archival (per-class retention period,
       archival path, restore semantics)
     - ## 5. Test-data + synthetic-corpus strategy (production vs
       synthetic separation; ground-truth posture)
     - ## 6. Migration posture (additive-compatible policy; schema
       deprecation path)
     - ## 7. Open items (OF-*) + E6 / E7 inheritance surfaces

2. REASONING TRACE — every table cites its E3 / E4 grounding. Name
   what you dropped and why.

Hard rules:
- Append-only tables (chain, audit log) enforce append-only at DB
  level (trigger or rule), not merely in application code.
- Sensitive columns have encryption-posture stated (envelope KEK,
  column-level vs row-level).
- Partitioning strategy stated for time-series tables (monthly /
  daily / yearly) with hot / warm / archive boundaries.
- Cross-cluster references use logical FK with explicit
  reconciliation — no physical cross-cluster FK.
- Synthetic corpus separation is structural (separate table or
  namespace), not just a flag.

Output format (strict):

<OUTPUT>
...data layer...
</OUTPUT>

<REASONING_TRACE>
1. ...
2. ...
</REASONING_TRACE>
"""


E5_ADVERSARIAL_SYSTEM_PROMPT = """\
You are the E5 Adversarial Agent. Challenge on four axes.

A. OUTPUT challenges — is append-only enforced at DB level or only
   in application code? Is sensitive-column encryption posture
   stated? Does partitioning have hot/warm/archive boundaries? Is
   cross-cluster FK logical or physical?

B. REASONING challenges — did the Producing Agent architect
   (violating DISCIPLINE-2) rather than concretise? Did it drop a
   table the architecture requires?

C. DIRECTION challenges — is convergence state consistent with
   work? Is synthetic corpus separated structurally from
   production data?

D. FRAME CHANGE challenges — does E5 reveal E3 architecture or E4
   security posture is wrong? Flag CRITICAL.

Rules:
- Not sycophantic. Append-only-in-app-only → MAJOR. Missing
  encryption-posture on sensitive columns → MAJOR.
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


E5_EXIT_ARTEFACT_TEMPLATE = """\
# E5 — Data — Exit Artefact

## 0. Status

**Convergence state at exit:** {convergence_state_at_exit}. Ratified.
**Primary derivation intent:** {primary_derivation_intent}
**Cycle id:** {cycle_id}
**Recorded chain entries:** {chain_entries_count}

## 1. Data layer

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

*End of E5 exit artefact.*
"""


E5_FIDELITY_CRITERIA = (
    "DISCIPLINE-2 honoured — E5 does not revisit architectural"
    " selections; it concretises within the E3 + E4 envelope.",
    "Append-only tables enforce append-only at DB level (trigger or"
    " rule), not only in application code.",
    "Sensitive-column encryption posture is stated (envelope KEK,"
    " column-level vs row-level).",
    "Time-series tables have partitioning strategy with hot / warm /"
    " archive boundaries.",
    "Cross-cluster references use logical FK with explicit"
    " reconciliation; no physical cross-cluster FK.",
    "Synthetic-corpus separation is structural (separate table or"
    " namespace), not merely a flag column.",
    "Migration posture is additive-compatible; deprecation paths"
    " are explicit.",
)


E5_SKILL = Skill(
    skill_id="E5",
    name="Data",
    producing_system_prompt=E5_PRODUCING_SYSTEM_PROMPT,
    adversarial_system_prompt=E5_ADVERSARIAL_SYSTEM_PROMPT,
    exit_artefact_template=E5_EXIT_ARTEFACT_TEMPLATE,
    fidelity_criteria=E5_FIDELITY_CRITERIA,
    predecessor_skill="E4",
    research_agent_hint=(
        "Consult database-engine docs (e.g., PostgreSQL partitioning,"
        " pgvector index types) only when the direction cites them."
        " Stay within the E3 + E4 envelope."
    ),
)
