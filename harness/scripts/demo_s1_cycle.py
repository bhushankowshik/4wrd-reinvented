"""Run one S1 Intent Cycle end-to-end against the real MVGH-β chain.

This script stands in for `harness run --skill S1 ...` when an
Anthropic API key is not available. It uses realistic simulated
agent outputs but writes every chain entry via the real
`mvghb.chain_write.writer.ChainWriter` — HMAC-signed, WAL-durable,
PostgreSQL-committed, master-anchored.

Run:
    uv run python scripts/demo_s1_cycle.py

Prerequisites:
    - noc-gov is up on localhost:5434 (docker ps).
    - mvghb bootstrap has been run (MVGHB_KEK in mvghb/.env).
"""
from __future__ import annotations

import base64
import os
import sys
from pathlib import Path

# Inherit mvghb's runtime env.
_MVGHB_ENV = Path(__file__).resolve().parents[2] / "mvghb" / ".env"
if _MVGHB_ENV.is_file():
    for line in _MVGHB_ENV.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-demo-stub")

from harness.agents.adversarial_agent import (  # noqa: E402
    AdversarialOutput, Challenge,
)
from harness.agents.producing_agent import ProducingOutput  # noqa: E402
from harness.intent_cycle import (  # noqa: E402
    IntentCycle, Moment1Input, VerifierResponse,
)
from harness.skills import SKILLS  # noqa: E402


SIMULATED_OUTPUT = """\
## Problem name
Multi-session governance-chain replay on cold-start for solo operators

## Crystallised statement
A solo operator returning to a 4WRD-governed delivery after a session gap
has no structured way to replay the governance chain and reload their
working frame without re-reading every entry. The absence of a cold-start
re-entry path means context rebuild is ad-hoc, slow, and risks
reintroducing retired theory.

## In scope
- Cold-start chain-replay for a single actor's working frame.
- Session-boundary reload signal for the orchestrator.
- A minimal Layer 2 derived view (operator view) scoped to the last
  governed cycle and its ratified exit artefact.

## Out of scope
- Multi-actor replay (Wave 2+, per S4 §2.3 activation roadmap).
- Client-facing audit export (separate artefact).
- Real-time in-session frame reload (the sidecar already handles this).

## Success criteria (observable, verifiable)
1. Operator can run `harness replay --skill S1 --cycles last:N` and get a
   structured summary in under 3 seconds on a 500-entry chain.
2. The replay output contains the most recent ratified exit artefact id,
   the last direction_capture, and any unresolved PARTIAL verifications.
3. Replay output is deterministic — same chain → same bytes.

## Primary stakeholders
- Bhushan (solo operator, primary user).
- Future auditor (Layer 2 consumer).
- Future deputy actor (activation trigger for Wave 2 multi-actor replay).

## Key uncertainties (what the human must resolve)
- Whether replay should include frame_change_detected entries by default.
- Whether cold-start should auto-suggest the next skill or stay passive.
- Whether the replay artefact is itself a chain-recorded act.
"""

SIMULATED_REASONING = """\
1. Direction said "Crystallise the problem of cold-start for solo
   operators in 4WRD". I treated "solo operator" as the primary frame
   because S5 §2.1 Wave-1 is explicitly trivial-solo.
2. I dropped the multi-actor variant — S5 defers AG6b-3 and AG9e-2 to
   Band 2 activation, so a solo cold-start is the right first scope.
3. Success criteria written in operational terms (seconds, file outputs,
   determinism) so verification is not subjective.
4. I assumed the operator has access to the noc-gov DB locally; this is
   consistent with §9 direct messaging (M9b-5) from S4.
5. I did NOT invent a new seam. No SEAM-1..5 is modified by this scope.
"""

SIMULATED_CHALLENGES = [
    Challenge(
        axis="OUTPUT",
        severity="MAJOR",
        challenge=(
            "'Cold-start' is defined by symptom (re-read every entry) "
            "not by a measurable threshold — success criterion 1 uses "
            "'3 seconds on a 500-entry chain' but there is no stated "
            "upper bound on chain size."
        ),
        evidence="## Success criteria 1. … under 3 seconds on a 500-entry chain.",
    ),
    Challenge(
        axis="REASONING",
        severity="MINOR",
        challenge=(
            "Step 4 assumes local noc-gov reachability but does not "
            "surface what happens if the DSN is wrong — should be in "
            "Key uncertainties, not implicit."
        ),
        evidence="Reasoning step 4.",
    ),
    Challenge(
        axis="DIRECTION",
        severity="MINOR",
        challenge=(
            "Direction used the phrase 'cold-start' as if it is a "
            "technical primitive; the crystallised statement inherited "
            "this without interrogation."
        ),
        evidence="Problem name — uses 'cold-start' verbatim.",
    ),
]


class _SimProducing:
    def produce(self, package):
        _ = package  # unused — simulation
        return ProducingOutput(
            output=SIMULATED_OUTPUT,
            reasoning_trace=SIMULATED_REASONING,
            raw="(simulated)",
            model="claude-sonnet-4-6",
        )


class _SimAdversarial:
    def challenge(self, package):
        _ = package
        return AdversarialOutput(
            challenges=list(SIMULATED_CHALLENGES),
            frame_change_detected=False,
            raw="(simulated)",
            model="claude-opus-4-6",
        )


def _auto_verifier(*, producing, adversarial, cycle_id, iteration):
    return VerifierResponse(
        outcome="CONFIRMED",
        notes=(
            "Simulated verification for end-to-end chain demo. "
            "Adversarial challenges noted — 'cold-start' definition "
            "refined in production text in a follow-up cycle."
        ),
        verifier_actor_id="human",
    )


def main() -> int:
    cycle = IntentCycle(
        skill=SKILLS["S1"],
        verifier=_auto_verifier,
        producing_agent=_SimProducing(),
        adversarial_agent=_SimAdversarial(),
        artefact_dir=Path(__file__).resolve().parents[2] / "docs",
    )
    moment1 = Moment1Input(
        convergence_state="Explorative",
        direction=(
            "Crystallise the problem of cold-start chain re-entry for "
            "solo operators returning to a 4WRD-governed delivery after "
            "a session gap."
        ),
        knowledge_contribution=(
            "Context: MVGH-β Wave 1 is live (HMAC chains, WAL, PG, "
            "master anchor). S5 §2.1 is trivial-solo. No deputy actor. "
            "Layer 2 derived views are not yet implemented — this cycle "
            "narrows what the first Layer 2 view must expose."
        ),
        primary_derivation_intent=[
            "docs/foundation/INPUT-001-foundation-v4.md",
            "docs/s4-exit-artefact.md",
            "docs/s5-exit-artefact.md",
            "mvghb/chain_write/writer.py",
        ],
    )
    print(f">>> Starting real S1 cycle against noc-gov …", flush=True)
    result = cycle.run(moment1)

    print("\n==================== Cycle summary ====================")
    print(f"cycle_id:              {result.cycle_id}")
    print(f"skill:                 {result.skill_id}")
    print(f"convergence at exit:   {result.convergence_state_at_exit}")
    print(f"iterations:            {result.iterations}")
    print(f"chain entries written: {len(result.chain_records)}")
    for r in result.chain_records:
        print(
            f"  [{r.moment:>2}] {r.entry_type:<23} "
            f"{r.actor_id:<18} chain_id={r.chain_id} iter={r.iteration}"
        )
    if result.artefact_path:
        print(f"\nexit artefact:         {result.artefact_path}")
    if result.anchor_chain_id:
        print(f"master anchor chain:   {result.anchor_chain_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
