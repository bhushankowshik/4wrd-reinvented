/* 4WRD direction templates — 16 skills × 3 convergence states = 48 starters.
 *
 * Templates are deliberately short (2–4 sentences). They seed the Direction
 * textarea when the operator changes skill or convergence; the operator
 * edits them before running a cycle — they are not final directions.
 */
(function () {
  "use strict";

  const T = {
    S1: {
      Explorative:
        "Crystallise the problem for [initiative]. Surface the root frustration, the visible symptoms, and the assumptions that are currently load-bearing. Introduce a coarse structure for 'what kind of problem is this' so S2 can map against it.",
      Targeted:
        "Tighten the problem statement. Resolve remaining ambiguity about scope and actor, and explicitly name the constraints that disqualify naive framings. List the open uncertainties that S2 must still answer.",
      Exact:
        "Produce a ratifiable problem statement: one crisp sentence plus the three framing commitments we will not relitigate downstream. No open questions that block S2.",
    },
    S2: {
      Explorative:
        "Map the context and constraints for [problem]. Identify: what platforms and primitives are available, what architectural gaps exist, what regulatory and technical constraints apply, and what structural tensions must be resolved before options can be generated in S3.",
      Targeted:
        "Narrow the context map. Resolve the open uncertainties from S1. Name the hard constraints (regulatory, technical, operational) that will govern option generation in S3 and cull framings that violate them.",
      Exact:
        "Publish a ratifiable context and constraint map: the primitives we have, the gaps we accept, and the constraints S3 must honour. No unresolved framing questions.",
    },
    S3: {
      Explorative:
        "Generate a broad spread of candidate solution directions honouring the S2 constraint map. Favour diversity of mechanism over polish. Surface unconventional candidates the constraint map does not outlaw.",
      Targeted:
        "Narrow the option set. Discard candidates that violate S2 constraints or fail on the disqualifying criteria. Name the comparison axes S4 will use to evaluate the remaining options.",
      Exact:
        "Publish the ratifiable option set for S4 evaluation: each option scoped enough that its delivery shape is visible. No options that haven't cleared the S2 constraint map.",
    },
    S4: {
      Explorative:
        "Evaluate the S3 options against the comparison axes. Probe where each option is strongest, where it breaks, and what evidence we lack to judge confidently. Surface decision-blocking unknowns.",
      Targeted:
        "Resolve the evidence gaps identified in the exploratory pass. For each option, state the case for and against on the named axes, and explicitly reject options that fail a hard constraint.",
      Exact:
        "Publish a ratifiable evaluation: each surviving option scored against the named axes with evidence cited. S5 can select without re-running the comparison.",
    },
    S5: {
      Explorative:
        "Stress-test the candidate selection from the evaluation. Surface the frame-change risks, the reversibility concerns, and the adjacent decisions that should be taken together.",
      Targeted:
        "Name the selected option and the specific reasons other options were rejected. Resolve any open stakeholder objections. Name the commitments this selection implies for S6.",
      Exact:
        "Ratify the solution selection. State what we chose, what we rejected, why, and the non-negotiable commitments S6 must preserve in the brief.",
    },
    S6: {
      Explorative:
        "Draft the Solution Brief for the selected option. Introduce the shape of what will be built, the value proposition, and the success criteria. Flag the questions the execution sequence must answer first.",
      Targeted:
        "Sharpen the Solution Brief. Resolve open ambiguities about scope and success criteria. Name the hand-off commitments E1 must honour when it opens problem definition.",
      Exact:
        "Publish the ratifiable Solution Brief: scope, value, success criteria, and the commitments execution must carry. No open questions that block E1.",
    },
    E1: {
      Explorative:
        "Translate the Solution Brief into an execution-shaped problem definition. Surface the implementation unknowns, the users and their jobs, and the operational constraints the brief did not anticipate.",
      Targeted:
        "Narrow the execution problem statement. Resolve the unknowns surfaced in the exploratory pass. Name the scope boundary and the explicit non-goals that will govern E2.",
      Exact:
        "Publish a ratifiable execution problem definition: scope, users, non-goals, and success criteria. No open questions that block requirements capture.",
    },
    E2: {
      Explorative:
        "Surface the requirements implied by the problem definition. Distinguish functional from non-functional. Flag requirements that are in tension and requirements the team currently cannot satisfy.",
      Targeted:
        "Narrow the requirements set. Resolve the tensions and name the trade-offs. Explicitly defer or reject requirements that would blow the scope boundary.",
      Exact:
        "Publish a ratifiable requirements list: each requirement testable, scoped, and attributable to a user job or constraint. No requirements pending classification.",
    },
    E3: {
      Explorative:
        "Draft an architecture that satisfies the requirements. Surface the major components, their seams, the data boundaries, and the architectural risks the requirements did not anticipate.",
      Targeted:
        "Narrow the architecture. Resolve the component-seam ambiguities. Name the architectural invariants that cannot be violated by build-time decisions in E6.",
      Exact:
        "Publish a ratifiable architecture: components, seams, invariants, and the decision log. E6 can build against this without revisiting structural choices.",
    },
    E4: {
      Explorative:
        "Identify the security and compliance envelope. Surface the sensitive data flows, the regulatory exposures, the threat model shape, and the controls the architecture currently lacks.",
      Targeted:
        "Narrow the security and compliance plan. Resolve the threat-model ambiguities. Name the non-negotiable controls and the residual risks we accept with justification.",
      Exact:
        "Publish a ratifiable security and compliance plan: controls, residual risks, and the audit trail the ops sequence will maintain. No unresolved compliance gaps.",
    },
    E5: {
      Explorative:
        "Map the data shape. Surface the entities, the lifecycles, the stores, and the retention and migration concerns the architecture glossed over.",
      Targeted:
        "Narrow the data plan. Resolve schema and lifecycle ambiguities. Name the migration and backfill commitments the build must honour.",
      Exact:
        "Publish a ratifiable data plan: schemas, lifecycles, retention rules, and migration posture. E6 can build persistence without re-deciding structure.",
    },
    E6: {
      Explorative:
        "Stand up a working build of the architecture's primary path. Surface the integration surprises, the primitives that didn't behave as advertised, and the refactors the architecture will need.",
      Targeted:
        "Narrow the build to the ratifiable slice. Resolve the integration surprises, name the deviations from the architecture, and update the invariants if we've learned something load-bearing.",
      Exact:
        "Publish a ratifiable build: the slice is complete, tests pass, the deviations from architecture are documented and accepted. E7 can test against a stable surface.",
    },
    E7: {
      Explorative:
        "Draft a test strategy for the build. Surface the test axes, the coverage gaps, and the behaviours whose correctness the unit tests alone cannot guarantee.",
      Targeted:
        "Narrow the test plan. Resolve the coverage gaps. Name the test cases that must pass before we deploy and the ones we intentionally defer.",
      Exact:
        "Publish a ratifiable test result: coverage, pass rates, and the defects accepted with justification. E8 can deploy against a known-quality artefact.",
    },
    E8: {
      Explorative:
        "Draft a deployment plan. Surface the rollout shape, the reversibility options, and the environment differences the test sequence did not exercise.",
      Targeted:
        "Narrow the deployment plan. Resolve environment and rollback ambiguities. Name the gates that must be green before promotion.",
      Exact:
        "Publish a ratifiable deployment record: environments promoted, rollback plan in place, gates green. Operations can take ownership of a deployed surface.",
    },
    E9: {
      Explorative:
        "Establish an operations posture. Surface the on-call shape, the signals we will watch, the playbooks we need, and the operational debt the earlier skills created.",
      Targeted:
        "Narrow the operations plan. Resolve on-call and signal ambiguities. Name the playbooks that must exist before the system is considered self-sustaining.",
      Exact:
        "Publish a ratifiable operations plan: on-call, signals, playbooks, and the incident taxonomy. The system is operable without the build team's constant attention.",
    },
    E10: {
      Explorative:
        "Open feedback and learning. Surface the signals from users, from operations, and from the governance chain that suggest the brief's assumptions are wrong. Generate candidate learnings.",
      Targeted:
        "Narrow the learnings. Resolve which signals are noise and which indicate a real shift. Name the concrete changes (to brief, architecture, or operations) the learnings imply.",
      Exact:
        "Publish a ratifiable learnings record: what we learned, what we will change, and what we leave unchanged by deliberate choice. Feeds the next outer cycle of solutioning.",
    },
  };

  window.DIRECTION_TEMPLATES = T;
})();
