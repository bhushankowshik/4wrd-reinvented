# INPUT-001 — 4WRD Foundational Design Document v4.0

**Status:** Pre-cycle input. Registered at Delivery Initialisation 2026-04-17.
**Purpose:** Foundational model reference. Load-bearing for all derivation intent that cites INPUT-001.

---

## 1. Purpose

4WRD is a delivery intelligence system. It governs fidelity between human intent and AI output across the full delivery lifecycle. Its purpose is to make AI production in delivery governable — addressable, auditable, adversarially-challenged, multi-actor, composable, and evolvable under its own governance.

---

## 2. Four Structural Elements

### 2.1 Intent Cycle — atomic unit

The Intent Cycle is the atomic unit of 4WRD. Every act of AI production in delivery happens within an Intent Cycle. Four moments:

1. **Direction Capture** — the human declares convergence state, direction, and (in Explorative state) knowledge contribution. Primary derivation intent is declared.
2. **AI Produces** — the Producing Agent produces output and reasoning trace as two separable components. Never blocks for more context. The Adversarial Agent then challenges both components.
3. **Human Verifies** — accountable verifiers respond independently on output dimension and reasoning trace dimension. The Adversarial Agent challenges each verification act.
4. **Cycle Closes or Continues** — if verifiers confirm both dimensions, the cycle closes and lineage is recorded. If divergence, the cycle continues with refined direction.

The Intent Cycle is recursive at every granularity level. It governs production of delivery artefacts. It also governs production of harness changes (meta-cycles).

### 2.2 Recording Mechanism — three layers

**Layer 1 — Raw record.** Per-actor HMAC chains anchored to a master chain. Every act by every actor is written as a structured entry. Append-only, tamper-evident.

**Layer 2 — Derived views.** Human real-time view, team coordination view, auditor view. Computed from Layer 1.

**Layer 3 — AI context packages.** Producing Context Package, Challenge Context Package, Orchestration Context Package. Generated fresh before each agent invocation from Layer 1 entries written since last generation.

Five consumers of the record: Human, Team, Auditor, Regulator, AI Actor.

### 2.3 Frame Change Sidecar — always-live

The Sidecar runs continuously alongside all active cycles. Two components:

**Detector** — internal signals. Session boundary scan at every session start. In-session Tier 2 interrupt when the Adversarial Agent detects frame invalidation during production.

**Receptor** — external signals. Six sources: humans, producing AI, adversarial AI, QA, qualification meetings, client.

Frame Change is distinct from output-wrong. A Frame Change invalidates the direction itself; the cycle pauses and waits for new direction.

### 2.4 Artefact Lineage — traceability

Every produced artefact carries a tamper-evident chain back through verification, critique, reasoning, direction. Primary derivation is declared at Moment 1 and recorded at Moment 4 on convergence. Incidental references are captured passively.

---

## 3. Three Convergence States

Declared by the human at cycle start. Signalled at transition.

- **Explorative** — problem is rough, needs crystallisation. Knowledge contribution required.
- **Targeted** — narrowing and verifying. No new structure; sharpen what exists.
- **Exact** — final convergence. Nothing pending; produces the clean exit artefact.

---

## 4. Four Actors

- **Human Team** — final point of call on all decisions. Provides direction, knowledge contribution, and verification.
- **Producing Agent** — persona family. One per skill per domain-specialisation. Produces outputs and reasoning traces.
- **Adversarial Agent** — persona family. Highest capability tier. Permanent challenger in every cycle moment. Secondary Frame Change Detector role.
- **Orchestrator Agent** — single instance. Governs process. First receiver of Frame Change signals. Nominates second-in-command.

---

## 5. Four Configuration Layers

Reusable assets stack from general to specific without re-implementation.

**Domain → Specialisation → Skill → Persona**

- Domain — broad sector (Telecommunications, Finance, Healthcare, Software Development Tooling)
- Specialisation — focused context within a domain (NOC Operations, Retail Banking Compliance, Governed Human-AI Delivery Harness)
- Skill — named capability with defined intent vocabulary, production form, fidelity criteria (S1 Problem Crystallisation, E3 Architecture)
- Persona — named Producing or Adversarial Agent instantiation configured for a specific skill within a specific domain-specialisation

---

## 6. Sixteen Reference Skills

### Solutioning (6)
- S1 Problem Crystallisation
- S2 Context and Constraint Mapping
- S3 Option Generation
- S4 Option Evaluation
- S5 Solution Selection
- S6 Solution Brief

### SDLC Execution (10)
- E1 Problem Definition
- E2 Requirements
- E3 Architecture
- E4 Security and Compliance
- E5 Data
- E6 Build
- E7 Test
- E8 Deployment
- E9 Operations
- E10 Feedback and Learning

Methodology (Waterfall, Agile, Hybrid) is expressed in the orchestration layer, not in skills.

---

## 7. Nine Foundational Principles

1. Intent is output, not input. The crystallised problem statement is a production artefact, not a given.
2. AI production cost is near zero. Do not block for more context — produce against approximate direction immediately.
3. Recording makes cognition visible. What is not recorded did not happen.
4. Verified status is frame-relative. A verified artefact under one frame may require re-verification under a new frame.
5. Humans are the final point of call. AI produces and challenges. AI does not decide.
6. Outcome correctness is outside scope. 4WRD governs fidelity to intent, not whether the intent was correct.
7. Time is first-class context. Delivery timelines, key commitments, and regulatory dates shape production.
8. Skills are methodology-agnostic. A skill produces the same form under Waterfall and Agile; orchestration differs.
9. Derivation is traceable. Every artefact has primary derivation (declared) and incidental references (captured passively).

---

## 8. Theory Retirement — First-Class Need (added during S1 live test)

The harness governs its own evolution, not only delivery production. Theory retirement is a first-class need: the harness must prune its own theory (skills, rules, learnings, registers, artefacts, schemas, personas) and produce tombstones when it does — durable, addressable markers recording what was retired, when, why, and what (if anything) succeeded it. Absence is not retirement; silent removal is prohibited.

This resolves the governance-over-governance concern structurally. Harness evolution is governed by recursive application of the Intent Cycle — meta-cycles and production-cycles share the same primitive, distinguished by an explicit mechanism (tagging, subject metadata, or equivalent — to be defined in implementation).

---

## 9. Implementation Target

**Claude Agent SDK** (Python or TypeScript). This is the foundational SDK evolved from Claude Code, giving Claude agents a computer — file system, bash, tools — as the primary execution model. Subagents provide isolated context windows. Hooks (PreToolUse, PostToolUse, SessionStart, UserPromptSubmit, and others) provide the event-driven interception points that map to 4WRD's four hooks. The Skills system and Agent Teams capability provide multi-agent coordination primitives.

This is the right target because:
- It is what the V4 harness was built on — familiar foundation
- Subagents with isolated context windows map directly to the per-role context package model
- SDK hooks map directly to 4WRD's four hook types
- Skills system maps to the sixteen reference skills
- No infrastructure phase — the SDK provides the execution environment

Multi-user coordination (multiple humans interacting with the same delivery record from different sessions) requires a thin shared-state layer beyond what the SDK provides natively. This is the one custom component — a lightweight shared file system or database that multiple sessions write to.

---

## 10. V4/V5 Carry-Forward Principles

Selected learnings from the phase-gated V4/V5 model are preserved in the reinvented model:

- **LRN-002** — Context refresh enforced structurally via Layer 3 package generation, not convention.
- **LRN-003** — Hooks must surface failures explicitly, never exit silently.
- **LRN-005** — Layer 1 entries validated against schema before writing. Policy-as-code, not policy-as-prompt.
- **LRN-010** — Artefact boundary enforced via pre-commit hook for unregistered artefacts.
- **F-001** — Hook invocation paths must be explicitly tested before trusting.
- V4 handoff types map to Moment 3 verification outcomes and Frame Change decision process.
- HMAC audit chain extended to per-actor chains with master anchor.
- Gate checklists reframed as skill fidelity criteria within specialisations.
- Feedback Loop pattern preserved in E10 Feedback and Learning skill.

---

## 11. Known Open Items

Items flagged as design-level concerns to be resolved during implementation or later skills:

- Per-actor HMAC chain master anchor mechanism (Merkle-tree-inspired, precise approach in implementation)
- Context package generation frequency and caching strategy
- Refined direction composition as production act (agent-invoked, not mechanical)
- Sidecar session boundary scan performance characteristics
- Verifier non-response handling escalation policies
- Cross-phase register structures (Assumption, Risk, Issue, Dependency, Action, Change) — designed during implementation as cycle-referenced, not phase-scoped

---

*End of INPUT-001.*
