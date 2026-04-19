"""Intent Cycle orchestrator — the atomic unit of 4WRD.

Implements the four moments per INPUT-001 §2.1:

  Moment 1 — Direction Capture         (human → chain)
  Moment 2 — AI Produces               (producing + adversarial → chain)
  Moment 3 — Human Verifies            (verifier → chain; may loop to Moment 2)
  Moment 4 — Cycle Closes              (artefact + lineage + master anchor)

Every moment writes one chain entry via MVGH-β Wave 1 `ChainWriter`
with HMAC-signed envelopes, per-actor chain linkage, and WAL
durability. On convergence in Moment 4 we snapshot the master anchor
(`mvghb.master_anchor.commit_anchor`) — this is the single
tamper-evident pointer that fixes the state of every actor chain
after the cycle closes.

This module is skill-agnostic: the orchestrator takes a `Skill`
record (producing prompt + adversarial prompt + artefact template)
and a `VerifierCallable` that surfaces Moment 3 to whatever UI the
caller chooses (CLI, test harness, web). The agent personas run on
Claude Sonnet 4.6 (producing) and Claude Opus 4.6 (adversarial).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Literal, Protocol
from uuid import UUID, uuid4

from mvghb.chain_write.writer import ChainEmitResult, ChainWriter
from mvghb.master_anchor.anchor import commit_anchor

from harness.agents.adversarial_agent import (
    AdversarialAgent,
    AdversarialOutput,
)
from harness.agents.producing_agent import ProducingAgent, ProducingOutput
from harness.agents.research_agent import (
    EMPTY_RESEARCH,
    ResearchAgent,
    ResearchOutput,
    should_invoke as should_invoke_research,
)
from harness.context_package import (
    build_challenge_package,
    build_producing_package,
)
from harness.lineage import emit_artefact_lineage, extract_lineage
from harness.sidecar.detector import (
    SidecarDecision,
    inspect_adversarial_output,
    run_session_boundary_scan,
)
from harness.skills.s1_problem_crystallisation import Skill


ConvergenceState = Literal["Explorative", "Targeted", "Exact"]
VerificationOutcome = Literal["CONFIRMED", "PARTIAL", "REJECTED"]


# ---- Data model ----


@dataclass(frozen=True)
class Moment1Input:
    """What the human provides at Direction Capture."""
    convergence_state: ConvergenceState
    direction: str
    primary_derivation_intent: list[str]
    knowledge_contribution: str | None = None

    def __post_init__(self) -> None:
        valid = ("Explorative", "Targeted", "Exact")
        if self.convergence_state not in valid:
            raise ValueError(
                f"convergence_state must be one of {valid}; "
                f"got {self.convergence_state!r}"
            )
        if self.convergence_state == "Explorative" and not self.knowledge_contribution:
            raise ValueError(
                "knowledge_contribution is required when convergence_state "
                "is 'Explorative' per INPUT-001 §2.1 / §3."
            )


@dataclass
class VerifierResponse:
    outcome: VerificationOutcome
    notes: str = ""
    refined_direction: str | None = None  # required if PARTIAL or REJECTED
    verifier_actor_id: str = "human"


class VerifierCallable(Protocol):
    """Moment 3 UI contract. Presents output + reasoning + challenges to a
    human and returns their verdict.
    """

    def __call__(
        self,
        *,
        producing: ProducingOutput,
        adversarial: AdversarialOutput,
        cycle_id: UUID,
        iteration: int,
    ) -> VerifierResponse:  # pragma: no cover - protocol definition
        ...


@dataclass
class CycleChainRecord:
    """One chain entry written as part of this cycle."""
    moment: str
    entry_type: str
    actor_id: str
    chain_id: UUID
    timestamp: datetime
    iteration: int = 0


@dataclass
class CycleResult:
    cycle_id: UUID
    skill_id: str
    convergence_state_at_exit: ConvergenceState
    iterations: int
    chain_records: list[CycleChainRecord]
    artefact_path: Path | None
    final_producing: ProducingOutput | None
    final_adversarial: AdversarialOutput | None
    final_verification: VerifierResponse | None
    frame_change: SidecarDecision | None
    anchor_chain_id: UUID | None


# ---- Orchestrator ----


class IntentCycle:
    """Run one governed Intent Cycle end-to-end."""

    ACTOR_ORCHESTRATOR = "orchestrator"
    ACTOR_PRODUCING = "producing_agent"
    ACTOR_ADVERSARIAL = "adversarial_agent"
    ACTOR_HUMAN = "human"

    def __init__(
        self,
        *,
        skill: Skill,
        verifier: VerifierCallable,
        producing_agent: ProducingAgent | None = None,
        adversarial_agent: AdversarialAgent | None = None,
        research_agent: ResearchAgent | None = None,
        writer: ChainWriter | None = None,
        artefact_dir: Path | None = None,
        max_iterations: int = 3,
        context_window: int = 5,
        stream_agents_to: object | None = None,
    ) -> None:
        self._skill = skill
        self._verifier = verifier
        self._producing = producing_agent or ProducingAgent(
            system_prompt=skill.producing_system_prompt,
            stream_to=stream_agents_to,
        )
        self._adversarial = adversarial_agent or AdversarialAgent(
            system_prompt=skill.adversarial_system_prompt,
            stream_to=stream_agents_to,
        )
        self._research = research_agent  # lazily constructed when needed
        self._stream_to = stream_agents_to
        self._writer = writer or ChainWriter()
        self._artefact_dir = artefact_dir or Path("docs")
        self._max_iterations = max_iterations
        self._context_window = context_window

    # ---- Public entry ----

    def run(self, moment1: Moment1Input) -> CycleResult:
        cycle_id = uuid4()
        records: list[CycleChainRecord] = []
        frame_change: SidecarDecision | None = None

        # Sidecar — boundary scan before Moment 1.
        scan = run_session_boundary_scan(new_direction=moment1.direction)
        if scan.likely_drift:
            # Wave 1 posture: surface to the caller via log only; human
            # retains override. A hard pause requires Wave 2 quorum.
            print(
                f"[sidecar] possible drift at session boundary: "
                f"{scan.drift_reason}",
                file=sys.stderr,
            )

        # Moment 1 — Direction Capture.
        m1_entry = self._record_moment1(cycle_id, moment1)
        records.append(
            CycleChainRecord(
                moment="1", entry_type="direction_capture",
                actor_id=self.ACTOR_HUMAN,
                chain_id=m1_entry.chain_id,
                timestamp=m1_entry.timestamp,
            )
        )

        # Moment 2 + Moment 3 loop (Moment 3 may loop back to Moment 2).
        current_direction = moment1.direction
        current_knowledge = moment1.knowledge_contribution
        current_state = moment1.convergence_state
        iteration = 1
        producing: ProducingOutput | None = None
        adversarial: AdversarialOutput | None = None
        verification: VerifierResponse | None = None
        prior_notes: str | None = None

        # Research pass — only once, before the first Moment 2.
        research = self._maybe_research(
            convergence_state=current_state,
            direction=current_direction,
            primary_derivation_intent=moment1.primary_derivation_intent,
            knowledge_contribution=current_knowledge,
        )
        research_rec = self._record_research(
            cycle_id=cycle_id, research=research,
        ) if research.invoked else None
        if research_rec is not None:
            records.append(research_rec)

        while iteration <= self._max_iterations:
            producing, adversarial, prod_rec, adv_rec = self._run_moment2(
                cycle_id=cycle_id,
                skill_id=self._skill.skill_id,
                convergence_state=current_state,
                direction=current_direction,
                knowledge_contribution=current_knowledge,
                primary_derivation_intent=moment1.primary_derivation_intent,
                iteration=iteration,
                research=research,
                prior_verification_notes=prior_notes,
            )
            records.append(prod_rec)
            records.append(adv_rec)

            # Secondary Sidecar Detector — adversarial FRAME_CHANGE.
            sidecar = inspect_adversarial_output(adversarial)
            if sidecar.frame_change:
                frame_change = sidecar
                print(
                    "[sidecar] Tier 2 frame change detected — "
                    f"{sidecar.reason}",
                    file=sys.stderr,
                )
                # Still let the human verify — the frame_change_detected
                # entry is already in the chain; the human decides whether
                # to continue or halt.

            # Moment 3 — Human Verifies.
            verification = self._verifier(
                producing=producing,
                adversarial=adversarial,
                cycle_id=cycle_id,
                iteration=iteration,
            )
            v_entry = self._record_verification(
                cycle_id=cycle_id,
                iteration=iteration,
                verification=verification,
            )
            records.append(
                CycleChainRecord(
                    moment="3", entry_type="verification",
                    actor_id=verification.verifier_actor_id,
                    chain_id=v_entry.chain_id,
                    timestamp=v_entry.timestamp,
                    iteration=iteration,
                )
            )

            if verification.outcome == "CONFIRMED":
                break
            if verification.outcome not in ("PARTIAL", "REJECTED"):
                raise ValueError(
                    f"Unknown verification outcome: {verification.outcome}"
                )
            if not verification.refined_direction:
                raise ValueError(
                    "PARTIAL/REJECTED verification must carry a "
                    "refined_direction to loop Moment 2."
                )
            # Loop back to Moment 2 with refined direction. The iteration
            # counter threads through every chain entry written on the
            # next pass so Layer 2 can replay each attempt independently.
            current_direction = verification.refined_direction
            prior_notes = verification.notes or None
            iteration += 1

        if verification is None or verification.outcome != "CONFIRMED":
            # Did not converge within max_iterations. Close without
            # writing a cycle_close entry — the chain records the trail.
            return CycleResult(
                cycle_id=cycle_id,
                skill_id=self._skill.skill_id,
                convergence_state_at_exit=current_state,
                iterations=iteration - 1 if iteration > 1 else iteration,
                chain_records=records,
                artefact_path=None,
                final_producing=producing,
                final_adversarial=adversarial,
                final_verification=verification,
                frame_change=frame_change,
                anchor_chain_id=None,
            )

        # Moment 4 — Cycle Closes.
        artefact_path = self._write_exit_artefact(
            cycle_id=cycle_id,
            moment1=moment1,
            producing=producing,  # type: ignore[arg-type]
            adversarial=adversarial,  # type: ignore[arg-type]
            verification=verification,
            records=records,
        )
        # Artefact lineage — structured refs (primary + incidental) as
        # their own chain entry, distinct from the cycle_close envelope.
        lineage_rec = self._record_artefact_lineage(
            cycle_id=cycle_id,
            moment1=moment1,
            producing=producing,  # type: ignore[arg-type]
            adversarial=adversarial,  # type: ignore[arg-type]
        )
        records.append(lineage_rec)

        close_entry = self._record_cycle_close(
            cycle_id=cycle_id,
            moment1=moment1,
            artefact_path=artefact_path,
            records=records,
        )
        records.append(
            CycleChainRecord(
                moment="4", entry_type="cycle_close",
                actor_id=self.ACTOR_ORCHESTRATOR,
                chain_id=close_entry.chain_id,
                timestamp=close_entry.timestamp,
            )
        )

        # Trigger master anchor commit.
        anchor = commit_anchor(writer=self._writer)

        return CycleResult(
            cycle_id=cycle_id,
            skill_id=self._skill.skill_id,
            convergence_state_at_exit=current_state,
            iterations=iteration,
            chain_records=records,
            artefact_path=artefact_path,
            final_producing=producing,
            final_adversarial=adversarial,
            final_verification=verification,
            frame_change=frame_change,
            anchor_chain_id=anchor.anchor_chain_id if anchor else None,
        )

    # ---- Moment 2 runner ----

    def _run_moment2(
        self,
        *,
        cycle_id: UUID,
        skill_id: str,
        convergence_state: ConvergenceState,
        direction: str,
        knowledge_contribution: str | None,
        primary_derivation_intent: list[str],
        iteration: int,
        research: ResearchOutput = EMPTY_RESEARCH,
        prior_verification_notes: str | None = None,
    ) -> tuple[
        ProducingOutput, AdversarialOutput,
        CycleChainRecord, CycleChainRecord,
    ]:
        prod_pkg = build_producing_package(
            skill_id=skill_id,
            convergence_state=convergence_state,
            direction=direction,
            knowledge_contribution=knowledge_contribution,
            primary_derivation_intent=primary_derivation_intent,
            max_prior_entries=self._context_window,
            research_block=research.render_for_producing() or None,
            iteration=iteration,
            prior_verification_notes=prior_verification_notes,
        )
        producing = self._producing.produce(prod_pkg)
        prod_entry = self._record_production(
            cycle_id=cycle_id,
            iteration=iteration,
            skill_id=skill_id,
            convergence_state=convergence_state,
            producing=producing,
        )
        prod_rec = CycleChainRecord(
            moment="2a", entry_type="production",
            actor_id=self.ACTOR_PRODUCING,
            chain_id=prod_entry.chain_id,
            timestamp=prod_entry.timestamp,
            iteration=iteration,
        )

        chall_pkg = build_challenge_package(
            skill_id=skill_id,
            convergence_state=convergence_state,
            direction=direction,
            producing_output=producing.output,
            reasoning_trace=producing.reasoning_trace,
        )
        adversarial = self._adversarial.challenge(chall_pkg)
        adv_entry = self._record_adversarial(
            cycle_id=cycle_id,
            iteration=iteration,
            skill_id=skill_id,
            adversarial=adversarial,
        )
        adv_rec = CycleChainRecord(
            moment="2b", entry_type="adversarial_challenge",
            actor_id=self.ACTOR_ADVERSARIAL,
            chain_id=adv_entry.chain_id,
            timestamp=adv_entry.timestamp,
            iteration=iteration,
        )
        return producing, adversarial, prod_rec, adv_rec

    # ---- Research helpers ----

    def _maybe_research(
        self,
        *,
        convergence_state: ConvergenceState,
        direction: str,
        primary_derivation_intent: list[str],
        knowledge_contribution: str | None,
    ) -> ResearchOutput:
        """Invoke the Research Agent iff Explorative + refs declared."""
        if not should_invoke_research(
            convergence_state=convergence_state,
            primary_derivation_intent=primary_derivation_intent,
        ):
            return EMPTY_RESEARCH
        agent = self._research or ResearchAgent(stream_to=self._stream_to)
        return agent.gather(
            direction=direction,
            primary_derivation_intent=primary_derivation_intent,
            knowledge_contribution=knowledge_contribution,
        )

    def _record_research(
        self, *, cycle_id: UUID, research: ResearchOutput,
    ) -> CycleChainRecord:
        payload = {
            "cycle_id": str(cycle_id),
            "skill_id": self._skill.skill_id,
            "moment": "2-pre",
            "model": research.model,
            "findings": research.findings,
            "sources": research.sources,
            "raw_length": len(research.raw),
        }
        res = self._writer.emit(
            entry_type="research",
            actor_id=self.ACTOR_PRODUCING,
            actor_role="producing_ai",
            incident_id=None,
            payload_ref=payload,
        )
        return CycleChainRecord(
            moment="2-pre", entry_type="research",
            actor_id=self.ACTOR_PRODUCING,
            chain_id=res.chain_id, timestamp=res.timestamp,
        )

    # ---- Lineage helpers ----

    def _record_artefact_lineage(
        self,
        *,
        cycle_id: UUID,
        moment1: Moment1Input,
        producing: ProducingOutput,
        adversarial: AdversarialOutput,
    ) -> CycleChainRecord:
        challenge_text = " ".join(
            f"{c.challenge} {c.evidence}" for c in adversarial.challenges
        )
        lineage = extract_lineage(
            cycle_id=cycle_id,
            skill_id=self._skill.skill_id,
            primary_derivation_intent=moment1.primary_derivation_intent,
            output_text=producing.output,
            reasoning_text=producing.reasoning_trace,
            challenge_text=challenge_text,
        )
        res = emit_artefact_lineage(
            lineage,
            actor_id=self.ACTOR_ORCHESTRATOR,
            actor_role="orchestrator",
            writer=self._writer,
        )
        return CycleChainRecord(
            moment="4-pre", entry_type="artefact_lineage",
            actor_id=self.ACTOR_ORCHESTRATOR,
            chain_id=res.chain_id, timestamp=res.timestamp,
        )

    # ---- Chain emit helpers ----

    def _record_moment1(
        self, cycle_id: UUID, m1: Moment1Input,
    ) -> ChainEmitResult:
        payload = {
            "cycle_id": str(cycle_id),
            "skill_id": self._skill.skill_id,
            "convergence_state": m1.convergence_state,
            "direction": m1.direction,
            "knowledge_contribution": m1.knowledge_contribution,
            "primary_derivation_intent": m1.primary_derivation_intent,
            "moment": "1",
        }
        return self._writer.emit(
            entry_type="direction_capture",
            actor_id=self.ACTOR_HUMAN,
            actor_role="human_operator",
            incident_id=None,
            payload_ref=payload,
        )

    def _record_production(
        self,
        *,
        cycle_id: UUID,
        iteration: int,
        skill_id: str,
        convergence_state: ConvergenceState,
        producing: ProducingOutput,
    ) -> ChainEmitResult:
        payload = {
            "cycle_id": str(cycle_id),
            "skill_id": skill_id,
            "convergence_state": convergence_state,
            "iteration": iteration,
            "moment": "2a",
            "model": producing.model,
            # Store excerpts, not full text — Layer 1 stays narrow.
            "output_excerpt": producing.output[:1000],
            "output_length": len(producing.output),
            "reasoning_excerpt": producing.reasoning_trace[:1000],
            "reasoning_length": len(producing.reasoning_trace),
        }
        return self._writer.emit(
            entry_type="production",
            actor_id=self.ACTOR_PRODUCING,
            actor_role="producing_ai",
            incident_id=None,
            payload_ref=payload,
        )

    def _record_adversarial(
        self,
        *,
        cycle_id: UUID,
        iteration: int,
        skill_id: str,
        adversarial: AdversarialOutput,
    ) -> ChainEmitResult:
        payload = {
            "cycle_id": str(cycle_id),
            "skill_id": skill_id,
            "iteration": iteration,
            "moment": "2b",
            "model": adversarial.model,
            "challenges": [
                {
                    "axis": c.axis, "severity": c.severity,
                    "challenge": c.challenge, "evidence": c.evidence,
                }
                for c in adversarial.challenges
            ],
            "frame_change_detected": adversarial.frame_change_detected,
            "severity_counts": {
                sev: sum(1 for c in adversarial.challenges if c.severity == sev)
                for sev in ("CRITICAL", "MAJOR", "MINOR")
            },
        }
        return self._writer.emit(
            entry_type="adversarial_challenge",
            actor_id=self.ACTOR_ADVERSARIAL,
            actor_role="adversarial_ai",
            incident_id=None,
            payload_ref=payload,
        )

    def _record_verification(
        self,
        *,
        cycle_id: UUID,
        iteration: int,
        verification: VerifierResponse,
    ) -> ChainEmitResult:
        payload = {
            "cycle_id": str(cycle_id),
            "skill_id": self._skill.skill_id,
            "iteration": iteration,
            "moment": "3",
            "verification_outcome": verification.outcome,
            "verification_notes": verification.notes,
            "refined_direction": verification.refined_direction,
        }
        return self._writer.emit(
            entry_type="verification",
            actor_id=verification.verifier_actor_id,
            actor_role="human_operator",
            incident_id=None,
            payload_ref=payload,
        )

    def _record_cycle_close(
        self,
        *,
        cycle_id: UUID,
        moment1: Moment1Input,
        artefact_path: Path,
        records: list[CycleChainRecord],
    ) -> ChainEmitResult:
        payload = {
            "cycle_id": str(cycle_id),
            "skill_id": self._skill.skill_id,
            "convergence_state_at_exit": moment1.convergence_state,
            "moment": "4",
            "artefact_path": str(artefact_path),
            "primary_derivation_intent": moment1.primary_derivation_intent,
            "chain_lineage": [
                {
                    "moment": r.moment,
                    "entry_type": r.entry_type,
                    "actor_id": r.actor_id,
                    "chain_id": str(r.chain_id),
                    "iteration": r.iteration,
                }
                for r in records
            ],
        }
        return self._writer.emit(
            entry_type="cycle_close",
            actor_id=self.ACTOR_ORCHESTRATOR,
            actor_role="orchestrator",
            incident_id=None,
            payload_ref=payload,
        )

    # ---- Exit artefact ----

    def _write_exit_artefact(
        self,
        *,
        cycle_id: UUID,
        moment1: Moment1Input,
        producing: ProducingOutput,
        adversarial: AdversarialOutput,
        verification: VerifierResponse,
        records: list[CycleChainRecord],
    ) -> Path:
        self._artefact_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = (
            f"{self._skill.skill_id.lower()}-cycle-"
            f"{cycle_id.hex[:8]}-{ts}.md"
        )
        path = self._artefact_dir / fname

        chain_lineage_md = "\n".join(
            f"- [{r.moment}] {r.entry_type} · {r.actor_id} · "
            f"chain_id={r.chain_id} · iter={r.iteration}"
            for r in records
        )
        pdi_md = "\n".join(f"- {p}" for p in moment1.primary_derivation_intent)

        rendered = self._skill.exit_artefact_template.format(
            convergence_state_at_exit=moment1.convergence_state,
            primary_derivation_intent=", ".join(moment1.primary_derivation_intent),
            primary_derivation_intent_list=pdi_md,
            cycle_id=str(cycle_id),
            chain_entries_count=len(records) + 1,  # +1 for the cycle_close
            producing_output=producing.output,
            reasoning_trace=producing.reasoning_trace,
            adversarial_challenges=adversarial.render(),
            verification_outcome=verification.outcome,
            verifier_actor_id=verification.verifier_actor_id,
            verification_notes=verification.notes or "(none)",
            chain_lineage=chain_lineage_md,
        )
        path.write_text(rendered, encoding="utf-8")
        return path
