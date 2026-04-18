# SOP PROC-RR-001 — Remote Resolution of Access-Layer Packet Loss

**Version:** v1
**Effective Date:** 2026-01-15
**Owner:** NOC Tier-2 Engineering
**Classification:** Internal — No Secrets

---

## Overview

This Standard Operating Procedure (SOP) governs the remote investigation
and resolution of intermittent packet loss events reported against
Access-Layer Base Transceiver Stations (BTS) and Optical Line Terminals
(OLT). It applies to P2 and P3 severity incidents where no customer
outage has been confirmed and where remote instrumentation is available.

The intent is to restore service without dispatching a field engineer
whenever the root cause can be conclusively determined and remediated
through remote configuration change, port reset, or software-level
recovery action.

## Scope

This SOP covers access-layer nodes in regions SG-NORTH, SG-SOUTH,
SG-EAST, SG-WEST, and SG-CENTRAL. It does not cover core-layer routers,
MPLS backbone devices, or peering edges — those are addressed by
separate SOPs (PROC-CORE-*). It also excludes microwave backhaul
radio faults (PROC-MW-*) and power-system faults (PROC-PWR-*).

## Precondition

Before applying the remediation steps below, confirm ALL of the
following:

- The incident has been correctly triaged as access-layer packet loss
  via CTTS ticket inspection.
- The affected node responds to SNMP polling on the management network.
- No concurrent planned-maintenance window is active for the affected
  node (check PlanMaint calendar).
- The operator has read-write access to the NMS configuration plane.
- At least one working historical baseline exists for the affected
  interface (≥ 14 days of continuous counters).

If any precondition fails, escalate per the Escalation section rather
than proceeding with remote remediation.

## Diagnostic Steps

1. **Inspect alarm state.** From the NMS, list current active alarms
   on the affected node. Note any line-card-level, power, or optical
   alarms — these take precedence over interface-level diagnostics.

2. **Pull interface counters.** For the affected interface, retrieve
   the last 24 hours of:
   - input errors (CRC, framing, giants, runts)
   - output errors and discards
   - input/output drops
   - carrier transitions

3. **Compare against baseline.** Compute the 7-day moving average for
   each counter. Flag any counter exceeding baseline by more than 3σ.

4. **Check optical levels.** If the interface is optical, retrieve
   TX/RX power. RX below -24 dBm or above -3 dBm indicates an optical
   fault and warrants remediation via optical cleaning or transceiver
   replacement (field dispatch — see PROC-FD-001).

5. **Verify upstream path.** Traceroute from the affected node toward
   the aggregation router. Note any hop with abnormal latency (> 5 ms
   on metro links) or packet loss (> 0.5%).

## Remediation Actions

Apply remediation in the following order. Proceed to the next step only
if the previous step failed to restore the interface.

### Action A — Soft interface reset

Issue an `interface shut` / `no interface shut` sequence on the
affected port. Wait 30 seconds between commands. Observe counters for
2 minutes. If input errors have ceased, consider the incident
remediated and proceed to Verification.

### Action B — Clear MAC-address table entries

On the affected interface, clear dynamic MAC entries. This resolves
ARP/L2 loop conditions that sometimes manifest as packet loss.
Observe counters for 2 minutes.

### Action C — Transceiver soft-reset

For optical interfaces only, issue a transceiver-level reset. This
power-cycles the SFP/QSFP without reloading the line card. Observe
optical levels and counters for 2 minutes.

### Action D — Line-card reload

As a last remote option, reload the affected line card. This is a
disruptive action affecting all interfaces on the card — ensure
customer-impact assessment is documented in the CTTS ticket before
proceeding. Wait 5 minutes for line-card recovery, then verify.

If Action D fails to restore the interface, dispatch a field engineer
per PROC-FD-001.

## Verification

After applying a remediation action, confirm ALL of the following
before closing the incident:

- Input/output errors have returned to within baseline range.
- No new alarms have been raised against the node in the past
  10 minutes.
- The upstream aggregation path shows < 0.1% packet loss over a
  5-minute synthetic probe.
- Customer-impacting services on the node report Green in the
  service-health dashboard.

## Escalation

Escalate to Tier-3 Engineering if:
- Remediation Action D fails to restore the interface.
- Optical levels indicate transceiver fault requiring field dispatch.
- The node is flagged as "critical" in the CMDB (hosts priority
  customers) and the incident has been open > 30 minutes.
- Any concurrent incident on the same node has been open > 60 minutes.

Escalate to the Incident Commander if:
- Customer-impact assessment indicates > 500 subscribers affected.
- The incident severity has been upgraded to P1.
- Tier-3 Engineering does not acknowledge within 15 minutes of
  escalation.

## References

- NMS Interface Counter Reference Guide (internal)
- SOP PROC-FD-001 — Field Dispatch for Access-Layer Faults
- SOP PROC-CORE-003 — Core-Layer Packet Loss Investigation
- CMDB Service Criticality Matrix (v4.2)
- Incident Severity Classification — Governance Appendix A
