# E4 Knowledge Contribution

**Date:** 2026-04-18
**Status:** Ratified
**Role:** Knowledge contribution for E4 Security 
and Compliance first Direction Capture.

---

## Key inputs

**MAS TRM document:** Available. E4 can produce 
control-number-level mapping, not just domain-level.
This is the primary differentiator from the S6/E2 
domain-level placeholder.

**E3 hardening items inherited (OF-4.1–OF-4.12):**
- OF-4.1: HMAC key management + rotation (T12)
- OF-4.2: Encryption at rest (PG + object storage 
  + model cache)
- OF-4.3: MAS TRM control-number-level mapping
- OF-4.4: CI-7 retention refinement under IMDA / 
  sectoral framework
- OF-4.5: Application RBAC roles + policies
- OF-4.6: CTTS service-account credential rotation
- OF-4.7: SSO/SAML hardening
- OF-4.8: Operator-identity-map access control + audit
- OF-4.9: Chain archival immutability (WORM/object-lock)
- OF-4.10: Synthetic test corpus sensitivity 
  classification
- OF-4.11: Penetration testing + threat modelling
- OF-4.12: Audit-evidence packaging format for regulator

**Governance mode:** Partial governance at E4. 
Cycle-primitive discipline active.

**Architecture context (from E3):**
- Two PostgreSQL clusters: incident-tier + 
  governance-tier (separate)
- Chain-write: local-disk WAL + async PG commit
- SSO/SAML operator identity; pseudonymous chain IDs
- 7-year retention; object storage (Ceph/S3-compat)
- OpenShift Secrets for credentials
- NetworkPolicy default-deny; no external egress
- Prometheus + Grafana observability
