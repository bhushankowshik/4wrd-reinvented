# SOP PROC-FD-001 — Field Dispatch for Access-Layer Faults

**Version:** v1
**Effective Date:** 2026-01-20
**Owner:** NOC Tier-2 Engineering + Field Operations
**Classification:** Internal — No Secrets

---

## Overview

This SOP governs the dispatch of field engineers to resolve
access-layer faults that cannot be remediated remotely. It
coordinates the handover from NOC to Field Operations, specifies
the pre-dispatch readiness checklist, and defines the on-site
validation procedure.

Field dispatch is the resolution path of last resort for remote-first
NOC workflows. Unnecessary truck rolls incur cost, customer disruption,
and operational risk — this SOP's purpose is to ensure that when a
dispatch IS required, it is executed correctly on the first attempt.

## Scope

Applies to field-dispatch requests for access-layer BTS, OLT, and
DSLAM equipment in regions SG-NORTH, SG-SOUTH, SG-EAST, SG-WEST, and
SG-CENTRAL. Does not apply to:
- Core or backbone equipment (PROC-CORE-FD-*)
- Customer-premises equipment (CPE) replacement (PROC-CPE-*)
- Tower-climb operations (requires separate safety SOPs)

## Precondition

Before initiating a field dispatch, the NOC operator MUST confirm:

- PROC-RR-001 remote-resolution steps have been fully attempted and
  documented in the CTTS ticket, OR remote diagnostics have
  conclusively identified a fault class (e.g. transceiver optical
  out-of-spec) that is known to require physical intervention.
- The affected node has been correctly identified by asset tag and
  GPS coordinates from the CMDB.
- Site access has been pre-authorised (keyholder contact verified,
  site-access permit valid).
- The on-call field team covering the affected region has capacity
  within the Target Resolution Window (see Severity table below).
- No safety-critical blockers apply to the site (e.g. active
  flooding, electrical hazard, civil unrest advisory).

If any precondition fails, either remediate it or escalate — do NOT
dispatch blind.

## Action — Dispatch Initiation

1. **Create dispatch ticket in FieldOps portal.** Link to the parent
   CTTS incident. Include:
   - Incident severity (P1/P2/P3/P4)
   - Affected node(s) and interface(s)
   - Customer-impact summary
   - Suspected fault class (optical, power, hardware, cable-cut)
   - Suggested spare parts (if known)

2. **Communicate expected arrival window** to the affected customer
   account managers per severity-based SLA:
   - P1: 4 hours
   - P2: 8 hours
   - P3: 24 hours
   - P4: 72 hours

3. **Verify spare-parts availability** at the nearest field hub.
   If parts must be sourced from central inventory, recalculate the
   arrival window and re-communicate.

4. **Pre-brief the field engineer** via voice call. Cover:
   - Fault summary and suspected root cause
   - Safety advisories for the site
   - Required test equipment (OTDR for optical, power meter, laptop
     with console access)
   - Rollback criteria if on-site action worsens service health

5. **Emit dispatch-accepted event** in the NOC workflow. This
   transitions the incident to "awaiting field arrival" state.

## On-Site Validation

The field engineer performs the following before declaring the
incident resolved:

- Physical inspection of the affected hardware (visible damage,
  indicator LEDs, cooling/fan operation).
- Replacement part installation (if applicable) with part serial
  number recorded in the ticket.
- Post-replacement functional test:
  - Interface link UP
  - Counters clean for 5 consecutive minutes
  - Optical levels within spec (if optical)
  - End-to-end customer service reachability test
- Photo evidence uploaded to the dispatch ticket.
- CTTS ticket updated with part-replacement details and final
  service-health status.

## Verification (NOC side)

Before closing the parent CTTS incident, the NOC operator confirms:

- Field engineer has posted "On-Site Complete" status.
- Service-health dashboard shows Green for affected customers for
  ≥ 10 minutes post-remediation.
- No regression alarms have fired on the node in the past 15 minutes.
- Customer-notification sent per SLA-communication policy.
- Root-cause annotation added to the incident's problem-management
  record (links to PROC-PROB-001).

## Escalation

Escalate to Field Operations Manager if:
- Field engineer does not arrive within SLA window.
- Replacement part unavailable at any field hub.
- On-site action has worsened service health.
- Multiple adjacent nodes in the same region require simultaneous
  dispatch (pattern suggests upstream fault).

Escalate to Incident Commander if:
- P1 dispatch cannot be resourced within the 4-hour SLA.
- Safety-critical blocker prevents site access.

## References

- SOP PROC-RR-001 — Remote Resolution of Access-Layer Packet Loss
- SOP PROC-PROB-001 — Problem Management Record Creation
- FieldOps Portal User Guide (v6.1)
- CMDB Asset Registry (v4.2)
- SLA Communication Policy — Governance Appendix B
