# INPUT-002 — 4WRD Composition Trace v1.0

**Status:** Pre-cycle input. Registered at Delivery Initialisation 2026-04-17.
**Purpose:** End-to-end validation of Intent Cycle composition. Reference for what a cycle looks like in practice.

---

## 1. Purpose

The Composition Trace validates the theoretical model of the Intent Cycle by walking a single cycle of S1 Problem Crystallisation end-to-end for a hypothetical Telco NOC delivery. It names every agent invocation, every hook firing, every Layer 1 record write.

If the composition works for one cycle within one skill, the template holds for all cycles in all skills. The model is uniform by design.

---

## 2. Cycle Conditions

- Domain: Telecommunications
- Specialisation: NOC Operations — AI-assisted event detection and fault restoration
- Skill: S1 Problem Crystallisation
- Orchestration mode: Hybrid
- Convergence state: Explorative
- Producing Agent persona: Problem-Crystallisation-for-Telco-NOC
- Adversarial Agent persona: Problem-Crystallisation-Adversarial-for-Telco-NOC
- Accountable verifiers: Product Lead (problem representation fidelity), Solution Architect (technical framing)
- Pre-cycle inputs: As-is document (INPUT-001 in the hypothetical delivery), Client ask (INPUT-002 in the hypothetical delivery)

---

## 3. Trace Summary

### Delivery Initialisation (before any skill activates)
1. Domain and Specialisation Configuration — Orchestrator + Team declare values
2. Orchestration Mode and Governance Setup — mode, orchestrator identity, second-in-command, temporal context
3. Pre-Cycle Input Registration — each pre-existing input receives unique ID, provenance, timestamp

### Step 0 — Skill Activation
- Skill definition loaded from reference skill set
- Producing and Adversarial Agent personas instantiated
- Layer 3 context package configuration established (packages themselves generated fresh per invocation)
- Accountable verifier assignment by Orchestrator

### Moment 1 — Direction Capture
- Harness prompts human for convergence state, direction, knowledge contribution (Explorative), derivation intent
- Human responds
- Pre-production hook fires: confirms required Moment 1 entries present, retrieves Producing Context Package generated fresh from Layer 1

### Moment 2 — AI Production
- Producing Agent invoked with Producing Context Package and injected pre-cycle inputs
- Produces OUTPUT and REASONING TRACE as two separable components
- Post-production hook fires: writes both as distinct Layer 1 entries, captures incidental artefact references
- Adversarial Agent invoked sequentially with Challenge Context Package
- Challenges output and reasoning trace across all dimensions
- Tier 2 frame invalidation flag checked

### Moment 3 — Human Verification
- Harness surfaces output, reasoning trace, and adversarial challenge to accountable verifiers
- Verifiers respond independently on output dimension and reasoning trace dimension
- Adversarial Agent challenges each verification act
- Orchestrator Agent checks verification completeness
- If divergence identified by any verifier, cycle will continue

### Moment 4 — Cycle Continues (or Closes)
- If continues: refined direction composed by Producing Agent (production act, not mechanical), challenged by Adversarial Agent, confirmed by Orchestrator
- If closes: lineage record written, verified artefact persisted
- Next cycle opens with refined direction and carry-forward context

---

## 4. Seven Theory Additions from Adversarial Challenge

The Composition Trace was challenged adversarially as a whole. Seven theory additions resulted:

1. **Pre-Production Hook Failure Handling** — hook returns structured prompt on missing Moment 1 element. Does not invoke Producing Agent. Human must complete governance act before production proceeds.
2. **Context Packages Generated Per-Invocation** — Layer 3 packages are not static. Fresh generation step immediately before each agent invocation.
3. **Adversarial Challenge Response Tracking** — verification prompt surfaces adversarial challenges with reference IDs. Unaddressed challenges are carried into next cycle as refined direction components.
4. **Refined Direction Composition as Production Act** — composed by Producing Agent with specialised composition prompt, challenged by Adversarial Agent, confirmed by Orchestrator before Cycle 2 opens.
5. **Sidecar Session Boundary Scan** — added as explicit first step before every session starts. Adversarial Agent scans Challenge Context Package for Tier 1 frame stress signals.
6. **Verifier Non-Response Handling** — Orchestrator Agent monitors response status per configurable window. Non-response surfaces as process failure. Orchestrator decides: wait, escalate, or reassign.
7. **Per-Actor HMAC Chains with Master Anchor** — each actor maintains sequential chain. Master chain entry written by harness when all actor chains for a cycle step are complete.

---

## 5. Purpose for Derivation Intent

Cycles that derive from INPUT-002 are citing the validation that the Intent Cycle composition works end-to-end. The trace is the reference for what a cycle looks like in practice, not just in theory.

---

*End of INPUT-002.*
