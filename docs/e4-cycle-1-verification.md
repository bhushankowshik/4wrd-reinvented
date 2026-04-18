# E4 Cycle 1 Verification

**Date:** 2026-04-18
**Cycle:** E4.1 Explorative — Security and Compliance first-pass

## Verification decisions — 9 adjustments for Targeted

1. OF-4.22 confirmed as must-resolve-before-Exact.
   Clause-number verification pass required against
   actual MAS TRM document before Targeted exit.

2. §1 table header addition: DSC/EVA/PAR/CAR
   classification applies to MVGH-β-active target
   state. During partial-governance interim (E1–E5),
   DSC rows carry PAR status — mechanism is designed
   and will be active when MVGH-β substrate is live.
   This distinction must be disclosed to the client
   before any evidence packaging.

3. OWASP LLM Top 10 supplement added to §6 threat
   model in Targeted. Map LLM01 (prompt injection),
   LLM02 (insecure output handling), LLM06 (sensitive
   information disclosure), LLM08 (excessive agency),
   LLM09 (overreliance) to product components and
   mitigations.

4. OF-4.8 strengthened with three additional controls:
   - Two-role approval on bulk reads of
     operator_identity_map (auditor + admin joint
     session, each chain-recorded)
   - Rate-limit on identity-map queries (max N records
     per session, configurable)
   - Anomaly detection on read volume above threshold
     triggers alert

5. §3 revocation rationale addition: revoked KEKs
   retained in verification-only mode cannot enable
   standalone backdated chain forgery because each
   entry HMAC covers prev_chain_id — attacker would
   need to fork entire chain from insertion point
   forward. Daily integrity verifier detects any chain
   fork by walking prev_chain_id linkage. Revoked-but-
   verifiable is safe provided chain linkage is intact.

6. OF-4.9 staging bucket added: pre-commit staging
   bucket (no Object Lock) receives archive writes
   first. Integrity check (HMAC verification +
   partition-seal manifest validation) runs against
   staging bucket. On successful verification, contents
   copied to Compliance-locked bucket and staging entry
   deleted. This prevents wrongly-written data from
   being permanently locked. Flag as E6 implementation
   requirement.

7. §1 footer addition: CAR items (physical access,
   threat intelligence, hardening baseline, secure
   coding standards) are client-accountable. A MAS TRM
   audit will examine the client posture on these
   independently. 4WRD-governed delivery evidence does
   not substitute for client obligations in CAR rows.
   Client must maintain their own evidence for CAR
   items.

8. OF-4.4 must not close at Exact without client legal
   sign-off on per-data-class retention schedule.
   If sign-off not available before Exact, §7 retention
   table carries flag: "Pending client legal
   confirmation — 7-year anchor is conservative
   minimum."

9. DISCIPLINE-2 audit: replace "OpenShift-native"
   rationale with explicit constraint citations
   IR-O.1 (deploy on OpenShift AI), IR-O.3 (agent
   orchestration on OpenShift), IR-O.4 (no external
   egress) throughout §§2–6.

## Additional notes

- OF-4.23 (FEAT/Veritas applicability): client-
  determination item; not closeable at E4 Targeted.
  Add to §1 bottom row noting unresolved applicability.

- Convergence state: advancing to Targeted.
  OF-4.22 is the gate — clause-number verification
  must be complete before Exact ratification.
