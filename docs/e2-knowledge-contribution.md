# E2 Knowledge Contribution

**Date:** 2026-04-18
**Status:** Ratified
**Role:** Knowledge contribution for E2 Requirements 
first Direction Capture.

---

## Resolved E1 open questions

**Q1 — Latency target:**
5 minutes for diagnosis. Client goal is 1/5/10 minutes 
for detect/diagnose/resolve. Detect and resolve are out 
of scope. Diagnosis window = 5 minutes. This is 
generous for multi-agent AI — sync invocation and 
sequential agent coordination are viable. No 
sub-second latency optimisation required.

**Q9 — Deployment environment:**
On-premises. RedHat OpenShift AI Platform. 
Self-hosted models (not Anthropic-hosted).

**PII/PDPA:**
No PII in incident tickets. PDPA scope-shaping 
constraint from E1 §5.1 is not-triggered. Cross-border 
transfer concern is not-triggered. Downgrade from 
scope-shaping constraint to resolved.

## Clarification on implementation targets

4WRD (the delivery framework) runs on Claude Agent SDK. 
This governs the delivery process — Intent Cycle, HMAC 
chains, adversarial challenge, AG-2/AG-3 enforcement, 
lineage recording.

The NOC product (the thing being delivered) runs on 
OpenShift AI with self-hosted models. The four agents 
(Diagnosis, Ticket Correlation, SOP, Orchestrator) are 
implemented on OpenShift AI. This is a product 
architecture decision independent of 4WRD's substrate.

CARRY-FWD-2 is not triggered. INPUT-001 §9 
implementation target refers to 4WRD's own substrate, 
not to products built using 4WRD.

## Remaining open questions for E2

From E1 §6 (excluding resolved items above):
- Q2: Ticketing system API — push vs pull, auth, schema
- Q3: SOP/KB structure — documents / RAG / vector search
- Q4: Incident ticket schema — fields, severity vocab
- Q5: Human-reviewer interface — dashboard / inline / 
  separate app
- Q6: Recommendation acceptance workflow
- Q7: Accuracy threshold + test-incident set
- Q8: Multi-incident correlation window
- Q10: IMDA licensing obligations
- Q11: PII — resolved (none in workflow)
- Q12: Emergency-override procedure
- Q13: Operator onboarding model
- Q14: Governance-overhead increment quantification
- Q15: Test-incident dataset provenance
- Q16: SLA contractual terms (MTTR, first-response)
