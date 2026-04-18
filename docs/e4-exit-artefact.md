# E4 — Security and Compliance — Exit Artefact

## 0. Status and derivation

**Convergence state at exit:** Exact. Ratified.
**Primary derivation intent:** docs/references/MAS-TRM-2021.pdf; docs/e4-cycle-1-verification.md; docs/e3-exit-artefact.md; docs/e4-knowledge-contribution.md; docs/s6-solution-brief.md.
**Contributing cycles:** E4.1 Explorative (first-pass across 8 deliverables) → E4 Targeted → Exact (9 adjustments absorbed; OF-4.22 clause-number verification pass completed against the ratified MAS TRM Guidelines January 2021 document).

**Governance mode at this cycle:** **Partial governance.** Cycle primitives active; full-harness infrastructure activates progressively as MVGH-β setup completes (CARRY-FWD-4).

**Honesty bound (S6 §4.6) reaffirmed.** 4WRD generates audit evidence; the institution files attestation. MAS does not pre-certify frameworks. No row below claims regulatory pre-approval.

---

## 1. MAS TRM control-number mapping (OF-4.22 resolved)

### 1.0 Scope header (per Targeted adjustment #2)

**Applicability of satisfaction classifications:**

- Satisfaction columns assume the **MVGH-β-active target state** where the full 4WRD governance harness (HMAC chain Layer-1, schema validator, pre-commit hook, Chain-Write Service, integrity verifier) is live.
- **During the partial-governance interim (E1–E5 execution, MVGH-β under construction per CARRY-FWD-4), all rows marked DSC carry interim status PAR** — mechanism is designed, target-state operational, but not yet active at runtime.
- Client-facing evidence packaging MUST disclose whether each claim is "MVGH-β-active DSC" or "interim PAR pending substrate activation". Mis-dating evidence as live when substrate is still pending violates the honesty bound.

### 1.1 Classification

- **DSC** — Directly Satisfied by Construction (runtime mechanism produces outcome; evidence chain-recorded)
- **EVA** — Evidence Available; institution files attestation
- **PAR** — Partially satisfied; gap named
- **CAR** — Client Action Required; 4WRD does not satisfy
- **N/A** — Control not applicable to NOC product scope

### 1.2 Full mapping (grounded in MAS TRM Jan 2021)

| Clause | Control (summary) | Satisfaction | Mechanism (constraint-cited) | Evidence artefact |
|---|---|---|---|---|
| **Chapter 3 — Technology Risk Governance and Oversight** | | | | |
| 3.1.1–3.1.8 | Board/senior management oversight; CIO/CISO appointments; risk appetite | CAR | Client-organisation responsibility | Client internal records |
| 3.2.1–3.2.3 | Policies, standards, procedures; deviation review; compliance verification | DSC | 4WRD cycle discipline (DISCIPLINE-1/2/3); exit artefact ratification; AG-3 schema validator enforces policy compliance at write time | `governance_chain` policy-compliance entries; exit artefacts |
| 3.3.1–3.3.2 | Information asset identification, classification, ownership, inventory | PAR | Incident data classified as information asset in §4.1 E3; SOP corpus classified; broader FI-asset inventory client-scope | **CAR-6**: full FI asset inventory is client-scope; 4WRD scope = product-surface assets only |
| 3.4.1–3.4.3 | Third-party services — assessment, contractual safeguards, ongoing diligence | CAR | 4WRD *is* a third party to the FI; client performs this assessment on 4WRD delivery | Client third-party management records |
| 3.5.1–3.5.2 | Competency, background review, insider-threat mitigation | CAR | Client HR/security vetting | Client records |
| 3.6.1–3.6.4 | Security awareness training; annual cadence; board training | CAR | Client training programme | Client training records |
| **Chapter 4 — Technology Risk Management Framework** | | | | |
| 4.1.1–4.1.5 | Risk management framework with identification/assessment/treatment/monitoring | EVA | Explorative→Targeted→Exact convergence; OF register; adversarial challenge at every cycle | Cycle exit artefacts + OF register |
| 4.2.1 | Risk identification | EVA | Threat model (§6 below); adversarial challenge | §6 STRIDE + OWASP LLM rows |
| 4.3.1–4.3.2 | Risk assessment — likelihood/impact; prioritisation criteria | EVA | §6 residual-risk ranking; Targeted adjustments register risks | §6 residual table |
| 4.4.1–4.4.3 | Risk treatment — mitigating controls; risk acceptance; insurance | PAR | Mitigations in §§2–6; **insurance cover (4.4.3) is CAR** — client procurement | §§2–6 + **CAR-7** insurance |
| 4.5.1–4.5.3 | Monitoring, review, reporting; risk register; metrics | DSC | `governance_chain` is the operational risk register; GR-S observability metrics; OF register is the risk register artefact | Layer-2 `risk_register` view; Grafana |
| **Chapter 5 — IT Project Management and Security-by-Design** | | | | |
| 5.1.1–5.1.4 | Project management framework; IT project plans; key documentation; project-risk management | DSC | S1–S6 + E1–E10 skill cycle discipline per S6 §2.5 (gate-based methodology for MAS TRM) | Exit artefacts; chain records when MVGH-β live |
| 5.2.1–5.2.2 | Project steering committee for large projects; escalation | EVA | MVGH-β delivery governance — Orchestrator role + client-side steering | Cycle exit-artefact sign-offs |
| 5.3.1–5.3.4 | System acquisition — vendor evaluation, due diligence, COTS assessment, source-code escrow | PAR | Granite/Llama/vLLM are vendor-supplied; IR-O.1 OpenShift AI vendor-selection done in E3; source-code escrow **not applied — weights licensed not escrowed** | **Open OF-4.29**: vendor-risk review + weights-availability plan |
| 5.4.1–5.4.4 | SDLC framework; security-by-design; IT security function engaged in each phase | DSC | E4 is the mandatory security-by-design gate before E5/E6; adversarial agent engaged every cycle; security requirements per §5.4.3 addressed across §§2–6 | E4 exit artefact + cycle chain |
| 5.5.1–5.5.2 | Requirements analysis — functional + non-functional + security | DSC | E2 Requirements exit artefact (FR + NFR + IR); E4 binds security controls | E2 + E4 artefacts |
| 5.6.1–5.6.3 | Design phase review; requirements trace; domain-expert review | DSC | E3 Architecture exit artefact; E4 security design review (this artefact) | E3 + E4 artefacts |
| 5.7.1–5.7.6 | System testing — methodology, requirements trace, separate environments, regression, defect tracking, signed-off test report | EVA | E7 Test skill owns; pre-commit + AG-3 provide continuous verification | E7 artefacts (future cycle) |
| 5.8.1–5.8.2 | Quality management; independent QA | EVA | Adversarial agent is structural independent challenger; E7 exercises | Adversarial chain entries |
| **Chapter 6 — Software Application Development and Management** | | | | |
| 6.1.1–6.1.7 | Secure coding, source-code review, application security testing, third-party/open-source management, developer training, SAST/DAST/IAST, defect tracking | PAR | E6 build cycle binds secure-coding standards + SAST/DAST via pre-commit + CI; developer training is **CAR-8** | **Open OF-4.19** (client-supplied coding standards); Annex A testing catalogue |
| 6.2.1–6.2.2 | Agile software development with SDLC + security-by-design | N/A | S6 §2.5 selects **gate-based methodology** for MAS-TRM-bound delivery; agile not adopted | Methodology selection documented S6 |
| 6.3.1–6.3.2 | DevSecOps — automation, CI/CD, segregation of duties | PAR | E6 pipeline will bind pre-commit + AG-3 + CI/CD; segregation of duties §5 RBAC | E6 binding |
| 6.4.1–6.4.8 | API development — vetting, risk assessment, security standards (access tokens, expiry), encryption, security testing, logging, real-time monitoring, DoS mitigation | DSC | CTTS-integration API + Review API + audit-export API; TLS 1.3 + service-account tokens with rotation (OF-4.6); vetting applied to CTTS integration; `access_token_ttl` ≤ 1h; API request logging to `governance_chain` when admin/audit surfaces; rate-limit + HPA for DoS | API inventory + chain records |
| 6.5.1–6.5.3 | End User Computing / shadow IT | N/A | Product is not EUC; operators use Reviewer UI under controlled surface | — |
| **Chapter 7 — IT Service Management** | | | | |
| 7.1.1 | IT service management framework | DSC | OpenShift-hosted services with governance integration; framework covers configuration, change, incident, problem; per IR-O.1 (deploy on OpenShift AI) and IR-O.3 (agent orchestration on OpenShift) | Deployment manifests + runbooks |
| 7.2.1–7.2.2 | Configuration management — versions, periodic review | DSC | `system_version` + `model_version` + `sop_versions_pinned` in chain; Kubernetes manifests as source of truth via GitOps | Chain + manifest repo |
| 7.3.1–7.3.3 | Technology refresh — EOS monitoring, refresh plan, dispensation | PAR | Granite/Llama/vLLM EOS tracked; PG/CloudNativePG EOS tracked; **refresh cadence binding is E9 operations** | **Open OF-4.30**: EOS register + refresh plan (E9) |
| 7.4.1–7.4.2 | Patch management — timeframe commensurate with criticality, test before prod | PAR | OpenShift-native patching; E6 CI/CD with test-before-prod; cadence binding E9 | **Open OF-4.17** (patch cadence) |
| 7.5.1–7.5.7 | Change management — assess/test/review/approve; risk/impact analysis; test env; CAB; backup/rollback; emergency procedure; logging | DSC | E3 §3.2 SOP version bump = change event; `governance_chain` change-event entry with approver; GitOps + review = CAB substitute (single-orchestrator scope); rollback via prior-version retention (90d deprecation window) | Layer-2 `change_history` view |
| 7.6.1–7.6.2 | Software release — segregation of duties; traceability + integrity of code movements | DSC | Pre-commit hook + AG-3 validator; two-role (admin + auditor) on deploy to prod; signed container images | Signed-image registry + chain release entries |
| 7.7.1–7.7.7 | Incident management framework — process, evidence preservation, roles, system-alert monitoring, major-incident escalation, communications plan, customer updates | DSC | **The product itself implements 7.7 for the client's NOC.** Per-incident chain lifecycle: intake → agent_output → recommendation → operator_decision; Prometheus alerts on system anomalies; 7.7.6 communications plan is **CAR-9** (client ops) | Layer-2 `incident_lifecycle` view |
| 7.8.1–7.8.3 | Problem management — root-cause resolution, past-incident record, trend analysis | PAR | Governance-chain retains full incident history and correlations; root-cause workflow tooling not in E3 scope | **Open OF-4.15** (problem-mgmt tooling, E5/E6) |
| **Chapter 8 — IT Resilience** | | | | |
| 8.1.1–8.1.4 | System availability — commensurate design, redundancy, resource monitoring, threshold response | DSC | E3 §5.1: HPA on Orchestrator/Review API; 2× vLLM Granite Instruct replicas; leader-elected Intake Adapter; Prometheus threshold alerts per IR-O.1 | Deployment + alert manifests |
| 8.2.1–8.2.4 | System recoverability — RTO/RPO aligned to business; DR plan; follow tested plan; periodic recovery-site operation | PAR | CloudNativePG streaming replication + object-storage archival give recovery substrate; **RTO/RPO numerical binding deferred** | **Open OF-4.16** (DR RTO/RPO binding, E8 + client sign-off) |
| 8.3.1–8.3.4 | DR testing — regular, test-plan, full/partial scenarios, service-provider recovery | CAR | DR test exercise is client ops | **CAR-10**: DR test schedule |
| 8.4.1–8.4.4 | Backup strategy, lifecycle policy, restoration testing, confidential-backup protection | DSC | PG streaming replication + object-storage archival (E3 §5.3); retention per CI-7 7y; encrypted via §4 below (separate KEK); offsite per object-storage topology | Backup + restore test logs |
| 8.5.1–8.5.6 | Data centre resilience — TVRA, redundancy, environmental controls, geo-separation, 24×7 monitoring, physical access | CAR | On-prem client data centre; fully client-owned | **CAR-11**: client data-centre physical controls |
| **Chapter 9 — Access Control** | | | | |
| 9.1.1 | 'Never alone', segregation of duties, least privilege | DSC | §5 RBAC matrix; two-role approval on key ops + bulk identity-map reads (OF-4.8 §2); per 9.1.1 sensitive-function definition | §5 matrix + chain records |
| 9.1.2 | User access management — provision/change/revoke, owner-authorised | DSC | `operator_identity_map` issuance + retirement chain-recorded; admin role authorises | Chain `identity_events` |
| 9.1.3 | Unique identification and logging of access and user-management activities | DSC | SSO subject → pseudonymous ID mapping is 1:1; all access + management chain-recorded | SSO log + Layer-2 `identity_events` |
| 9.1.4 | Password policy + strong controls | PAR | SSO/SAML delegates password policy to client IdP; 4WRD scope: IdP assertion validation per OF-4.7 | **CAR-12**: client IdP password posture |
| 9.1.5 | **Multi-factor authentication for sensitive system functions** | PAR | MFA enforcement at IdP; two-role gate on key-rotation + bulk identity-map read adds second factor operationally; **explicit MFA enforcement contract with client IdP** needs binding | **Open OF-4.31**: MFA enforcement contract with client IdP |
| 9.1.6 | Periodic user access review | DSC | Quarterly access-review CronJob (OF-4.27); exceptions chain-recorded | CronJob output + chain |
| 9.1.7 | Access revoked on role change or termination | DSC | SSO-driven retirement triggers identity-map `retired_at`; chain entry | Chain `identity_retired` events |
| 9.1.8 | Service-provider access subject to same controls | DSC | 4WRD delivery is scoped under same SSO + RBAC | Chain records for 4WRD-staff access (if any during delivery) |
| 9.2.1 | Privileged access — need-to-use, logged, reviewed | DSC | Separate `noc-gov` namespace RBAC; admin role chain-recorded; activities logged via chain | Chain `privileged_actions` |
| 9.2.2 | System and service account management | DSC | CTTS service-account, model-serving service-accounts, Chain-Write service account; rotation OF-4.6 + monitoring via audit logs | Service-account inventory + chain rotation events |
| 9.3.1–9.3.2 | Remote access — encryption, MFA, hardened endpoint | CAR | Operators access Reviewer UI from within client network via SSO; remote-access endpoint posture is client-owned | **CAR-13**: client endpoint + remote-access posture |
| **Chapter 10 — Cryptography** | | | | |
| 10.1.1–10.1.5 | Cryptographic algorithms — well-established standards, appropriate strength, random seed quality, rigorous vetting, cryptanalysis monitoring | DSC | TLS 1.3 (NIST-approved suites); HMAC-SHA256 for chain; Argon2id for any at-rest credential hashing; CSPRNG via OpenShift platform; cipher inventory in §4 below | Cipher inventory + manifest |
| 10.2.1 | Key management policy covering generation/distribution/installation/renewal/revocation/recovery/expiry | DSC | §3 below — three-tier hierarchy; rotation cadence; revocation protocol; recovery via backups with 10y retention | §3 + key-mgmt artefact |
| 10.2.2 | Secure generation and protection of keys; protection of key-derivation material | DSC | HSM-backed root KMS; HKDF derivation for per-entry HMAC keys | §3 |
| 10.2.3 | Appropriate lifespan of each key | DSC | Per-class rotation schedule (§3: root 365d, KEK 90/180d, DEK per-volume) | §3 |
| 10.2.4 | Keys in hardened/tamper-resistant systems (e.g. HSM) | DSC | HSM or equivalent FIPS 140-2 L3 boundary for root KMS; Vault-backed KEK/DEK | Vault config + HSM attestation |
| 10.2.5 | Secure key transmission | DSC | Out-of-band distribution for root master ceremony; in-cluster KEK distribution via mTLS to Vault; no key over cleartext channel | Key-ceremony records |
| 10.2.6 | Key diversification — single-purpose keys | DSC | Separate KEKs per volume class (§4); separate HMAC keys per actor chain; TLS signing keys separate from chain-HMAC keys | Key-inventory artefact |
| 10.2.7 | Revocation on compromise, cascade to dependent keys | DSC | §3 revocation protocol; chain-recorded `key_revocation` event; cascade-rewrap DEKs under compromised KEK | §3 + chain |
| 10.2.8 | Secure key destruction on expiry/revocation | DSC | Crypto-shredding: destroy key material; revoked KEK retained verification-only until retention-window exit, then destroyed per §3 + Targeted adjustment #5 rationale | §3 |
| 10.2.9 | New key not derivable from previous | DSC | Independent key-gen from HSM entropy; HKDF context includes rotation epoch | §3 |
| 10.2.10 | Key backups for recovery; high protection | DSC | 2-of-3 custodian split; Vault backup encrypted with separate escrow key; 10y retention for key ops (§7 below) | Vault backup + custody records |
| **Chapter 11 — Data and Infrastructure Security** | | | | |
| 11.1.1 | Data loss prevention — data in motion, at rest, in use | PAR | In-motion: TLS everywhere (DSC); at-rest: §4 encryption (DSC); **in-use: GPU memory during inference not end-to-end encrypted** (PAR) | §4 + residual note |
| 11.1.2 | Prevent and detect data theft + unauthorised modification | DSC | Chain-recorded data access on audit surfaces; file integrity via HMAC on chain; NetworkPolicy blocks exfil | §6 threat model row + chain |
| 11.1.3 | Encrypted storage and strong access controls on endpoint/system data | DSC | §4 encryption + §5 RBAC | §4 + §5 |
| 11.1.4 | Only authorised storage media for confidential data | DSC | No removable media in product runtime; all storage in-cluster; egress forbidden | NetworkPolicy + hardening baseline |
| 11.1.5 | Detection of unauthorised internet services use | DSC | IR-O.4 (no external egress) enforced at NetworkPolicy + runtime egress monitor | Egress-monitor alerts |
| 11.1.6 | Production data in non-production — restricted + senior-mgmt approval + masked | PAR | Synthetic-gen pipeline produces test data (not prod-derived); **residual: OF-4.10 corpus sensitivity** | **OF-4.10** resolved via k-anonymity + SME validation; see §2 |
| 11.1.7 | Confidential data irrevocably deleted on disposal | DSC | Crypto-shredding on volume retirement (§4); object-storage lifecycle policy post-retention | Lifecycle policy artefact |
| 11.2.1 | Firewalls between FI and Internet + third parties | DSC | IR-O.4 no external egress; client-perimeter firewall is client scope; internal NetworkPolicy acts as segmentation firewall | NetworkPolicy manifests |
| 11.2.2 | Network segmentation by criticality/function/sensitivity | DSC | 4 namespaces (noc-prod, noc-data, noc-gov, noc-model) + NetworkPolicy default-deny (E3 §5.1 + §6.4) | Namespace + policy manifests |
| 11.2.3 | Network intrusion prevention | PAR | OpenShift-platform IDS if provisioned; client-perimeter IDS is client scope | **CAR-14**: IDS coverage |
| 11.2.4 | Network access controls — prevent unauthorised devices | DSC | In-cluster only; no BYOD inside runtime; all endpoints managed | Cluster inventory |
| 11.2.5 | Regular review of network access rules | DSC | NetworkPolicy manifests in GitOps; quarterly review CronJob reminder | GitOps history |
| 11.2.6 | Isolate internet browsing from endpoints | N/A | Product has no internet-browsing component | — |
| 11.2.7 | DoS protection | DSC | HPA + rate-limit on CTTS poll + Review API; circuit breaker on model-serving | Rate-limit config + HPA |
| 11.2.8 | Periodic network-architecture review | DSC | E9 Operations runbook includes quarterly review | E9 binding |
| 11.3.1–11.3.2 | System security standards; uniform application; deviation tracking | PAR | OpenShift-default hardening baseline; full CIS/custom baseline **client-supplied** | **Open OF-4.18** (hardening baseline) |
| 11.3.3–11.3.4 | Endpoint protection — behavioural/signature anti-malware; signatures up-to-date; regular scans | CAR | Container images are immutable; endpoint AV is client-endpoint scope | **CAR-15**: endpoint AV on operator workstations |
| 11.3.5 | IOC scanning + anomaly monitoring | PAR | Prometheus/Alertmanager covers operational anomalies; IOC-specific scanning is **CAR** (client SOC) | **CAR-5**: client SOC IOC feed |
| 11.3.6 | Application whitelisting | DSC | Container image allow-list via signed-image policy; only signed images deployable | Image-signing config |
| 11.3.7 | BYOD | N/A | No BYOD for NOC product | — |
| 11.4.1 | Virtualisation — security standards across all components | DSC | OpenShift hardened baseline for hypervisor/nodes; container-isolation per pod | OpenShift baseline |
| 11.4.2 | Strong access controls on hypervisor/host OS | DSC | Node-level RBAC; admin role required; chain-recorded admin sessions | RBAC manifests |
| 11.4.3 | Virtual image and snapshot management | DSC | Container-image registry + snapshot policy; chain-recorded image-promotion events | Image registry + chain |
| 11.5.1–11.5.5 | Internet of Things | N/A | Not applicable to NOC product | — |
| **Chapter 12 — Cyber Security Operations** | | | | |
| 12.1.1–12.1.3 | Cyber threat intelligence — collect/process/analyse; intel sharing; misinformation response | CAR | Client SOC function | **CAR-5** (confirmed) |
| 12.2.1 | SOC or managed security services; defined processes/roles | CAR | Client SOC | **CAR-5** |
| 12.2.2 | System log collection/process/review/retention; log protection | DSC | Governance chain IS the structured audit log; OpenShift platform logs for operational events; log integrity via HMAC on governance chain + tamper-evident archive (OF-4.9) | Chain + OpenShift logs |
| 12.2.3 | Baseline of routine system activity + analyse against baseline | DSC | Prometheus baselining + GR-S observability metrics | Grafana baselines |
| 12.2.4 | User behavioural analytics | PAR | Approval/reject/override ratios per-operator tracked in Layer-2; ML-based UBA **not in scope** | Layer-2 operator ratios; **CAR-16**: ML UBA |
| 12.2.5 | Correlation of multiple events across logs | DSC | Layer-2 audit view correlates chain entries across agent_output/recommendation/decision per incident | Layer-2 `incident_lifecycle` |
| 12.2.6 | Timely escalation to stakeholders on anomalies | DSC | Alertmanager routing; on-call paging | Alert-routing config |
| 12.3.1 | Cyber incident response plan | PAR | Product response plan + coordination with client SOC; **not the same as MAS 7.7 operational incident** — this is cyber-incident specific | **Open OF-4.32**: cyber-IR playbook for product-layer events |
| 12.3.2 | Investigation of control deficiencies | DSC | Chain-reconstruction + Mode-A replay (E3 §8) supports post-incident investigation | Replay tooling (E6) |
| 12.3.3 | Lessons learnt feed into controls | DSC | E10 Feedback and Learning skill cycle; theory retirement + AG-5b tombstones | E10 binding |
| **Chapter 13 — Cyber Security Assessment** | | | | |
| 13.1.1–13.1.2 | Vulnerability assessment — regular cadence, scope | PAR | E6 pipeline image-scanning + SBOM; cadence binding E9 | **Open OF-4.17** |
| 13.2.1–13.2.4 | Penetration testing — black/grey-box; bug bounty; on production; annual frequency for Internet-exposed | EVA | E7 test pack + annual external pen test (scope OF-4.25); **NOC product is internal-network, not Internet-exposed** → annual frequency still advisable but not strictly mandated | E7 + OF-4.25 |
| 13.3.1–13.3.2 | Cyber exercises — scenario-based; stakeholder involvement | CAR | Client-owned exercises; 4WRD may participate | **CAR-17**: client cyber exercises |
| 13.4.1–13.4.2 | Adversarial attack simulation — tactics/techniques/procedures | EVA | 4WRD's adversarial agent operates at **harness layer** (persona family per S6 §2.3), not as product-layer red team; product-layer red-team exercise is EVA via OF-4.25 | Adversarial chain entries + OF-4.25 |
| 13.5.1–13.5.2 | Intelligence-based scenario design | CAR | Requires client threat intel | **CAR-5** |
| 13.6.1 | Remediation management process with severity + timeframe + deviation mgmt | DSC | OF register acts as remediation backlog; severity classification per OF-type; deviations chain-recorded | OF register + chain |
| **Chapter 14 — Online Financial Services** | | | | |
| 14.1–14.4 | Online financial services (banking, payments, trading, customer auth, fraud monitoring, customer education) | **N/A** | NOC Incident Management is an internal operational system, not a customer-facing financial service. No online financial service endpoints exposed by this product | — |
| **Chapter 15 — IT Audit** | | | | |
| 15.1.1 | IT audit provides board/senior-mgmt independent opinion on controls/risk mgmt/governance | EVA | Three-layer Recording Mechanism + Layer-2 audit views + 7y retention; audit function is **client-organisation-internal**, 4WRD supplies evidence | Audit-export API bundle |
| 15.1.2 | Comprehensive auditable areas | DSC | Chain covers IT operations, functions, processes across product surface | Layer-2 catalogue |
| 15.1.3 | Audit frequency commensurate with criticality | EVA | Client audit scheduling | Client records |
| 15.1.4 | Competent IT auditors | CAR | Client HR/audit function | **CAR-18**: client audit competency |
| **Annex A — Application Security Testing** | | | | |
| A.1–A.2 | SAST, DAST, IAST, fuzz testing | EVA | E6 pipeline integrates SAST on source + DAST/IAST on deploy; fuzz testing on CTTS-intake adapter (schema fuzzing) | E6 pipeline config |
| **Annexes B (BYOD) and C (Mobile Application)** | | | | |
| B.1 / C.1 | BYOD and Mobile Application Security | **N/A** | No BYOD, no customer-facing mobile app in NOC scope | — |
| **AI/ML-specific guidance** | | | | |
| MAS FEAT 2018 / Veritas 2022 (**not part of TRM**) | Fairness, Ethics, Accountability, Transparency in AI | EVA | Human-review gate (FR-D.6); explainability via reasoning-trace capture; chain-recorded model-version + SOP versions; FEAT applicability is **client-determination** | **Open OF-4.23** (applicability determination) |

### 1.3 Client-accountability footer (per Targeted adjustment #7)

**CAR-labelled rows (18 items: CAR-1 through CAR-18) are client-accountable.** A MAS TRM audit will examine client posture on these rows independently. 4WRD-governed delivery evidence does not substitute for client obligations on CAR items. Client must maintain their own evidence and posture for: physical data-centre controls, third-party-management of 4WRD as supplier, HR/competency/background review, security awareness training, insurance cover, IdP password policy, MFA enforcement (with product-side cooperation), remote-access endpoint posture, IDS coverage, endpoint anti-malware, client SOC (threat intel / IOC / UBA / cyber exercises), DR testing schedule, audit-function competency, and communications plan for major incidents.

### 1.4 FEAT/Veritas applicability (OF-4.23 open)

MAS FEAT Principles (2018) and the Veritas Framework (2022) are MAS guidance on AI/ML ethics, fairness, and explainability — **not part of MAS TRM Guidelines**. Applicability to a NOC incident-management recommender system is plausible but client-determined. Key considerations:
- FR-D.6 human-review gate is a structural response to excessive-agency concerns.
- Reasoning-trace capture supports explainability.
- Pseudonymous operator identity + chain supports accountability.
- Fairness: the system makes recommendations on incidents not people; fairness framing differs from customer-credit-decision contexts where FEAT is most load-bearing.

**Open item: client legal + compliance to confirm applicability scope and any additional controls.** If FEAT applies, the proof-metric suite may need a fairness/ethics dimension added.

### 1.5 Clause-number verification pass (OF-4.22 closed)

All clauses in §1.2 are cited against the ratified **MAS TRM Guidelines January 2021** (docs/references/MAS-TRM-2021.pdf). Section and paragraph citations were verified in the Targeted pass. Three chapter-number corrections from Explorative to Targeted:
- **Explorative Ch 3 "TRM Framework" → Targeted Ch 4** (the actual framework chapter)
- **Explorative Ch 4 "Project Mgmt" → Targeted Ch 5** (Ch 3 is Governance and Oversight)
- **All subsequent Explorative chapter numbers shifted +1** (Software Dev Ch 5→6, IT Service Mgmt Ch 6→7, IT Resilience Ch 7→8, Access Control Ch 8→9, Crypto Ch 9→10, Data/Infra Security Ch 10→11, Cyber Sec Ops Ch 11→12, Cyber Security Assessment Ch 12→13, Online Financial Services Ch 13→14, IT Audit Ch 14→15)

Additional Targeted corrections:
- **Chapter 14 Online Financial Services declared N/A** for NOC scope (new in Targeted — Explorative was silent).
- **Annexes A/B/C added** explicitly (Explorative was silent).
- **FEAT/Veritas confirmed outside TRM** (Explorative treated as adjacent row).

OF-4.22 is closed.

---

## 2. Security controls design — hardened OF items

| OF-# | Item | Selected mechanism | Rationale (constraint-cited) | Residual risk |
|---|---|---|---|---|
| OF-4.1 | HMAC key mgmt + rotation (T12) | Three-tier hierarchy (root → KEK → per-entry HMAC); rotation 365d/90d/per-entry; revocation chain-recorded (§3 below) | **MAS 10.2.1, 10.2.3, 10.2.7, 10.2.8, 10.2.9, 10.2.10**; T12 deferred since S4; A2 per-actor HMAC chains require persistent key ops | Key-custodian insider; mitigated by 2-of-3 split + two-role ops |
| OF-4.2 | Encryption at rest | LUKS2 on PG PV (both clusters) + Ceph OSD encryption + WAL-PVC LUKS2 + model-cache LUKS2; KEKs from Vault (§4 below) | **MAS 10.1.2, 11.1.1 (data at rest), 11.1.3**; IR-O.4 (no external egress) | Crypto-shredding relies on key destruction; key-escrow policy client-owned |
| OF-4.3 | MAS TRM control-number mapping | §1 above | S6 §4.6 honesty bound; OF-4.3 closed at this cycle via OF-4.22 pass | Re-verification if MAS TRM revised |
| OF-4.4 | Retention refinement | Per-data-class schedule (§7 below); 7y minimum anchor per CI-7; **flagged pending client legal sign-off per Targeted adjustment #8** | **MAS 8.4.2, 15.1**; CI-7 | Sectoral overlay may extend; client legal confirms at cycle-close or §7 carries flag |
| OF-4.5 | Application RBAC | 5 roles: `operator`, `supervisor`, `auditor`, `admin`, `sre` (§5 below) | **MAS 9.1.1, 9.1.2, 9.1.3, 9.2.1**; FR-D role surface | Role creep; mitigated by quarterly review CronJob (OF-4.27) |
| OF-4.6 | CTTS service-account rotation | 90d automated rotation via OpenShift Secret + rolling restart; on-demand revocation via chain-recorded event | **MAS 9.2.2** (service accounts); IR-T CTTS auth; T12 | Rotation-window failure; mitigated by health-check + alert |
| OF-4.7 | SSO/SAML hardening | SAML 2.0 signed+encrypted assertions; AudienceRestriction+NotOnOrAfter enforced (≤5 min); ReplayCache 24h; session TTL 8h sliding, 12h absolute; IdP cert pinning | **MAS 9.1, 9.3.1**; CI-5 | IdP compromise; mitigated by client IdP posture + chain-recorded auth events |
| OF-4.8 | `operator_identity_map` access (**strengthened per Targeted adjustment #4**) | Access via `identity-audit-api` (auditor-only); **every read chain-recorded**; **two-role approval on bulk reads (auditor + admin joint session, each chain-recorded)**; **per-session rate-limit** (default 100 records/session, configurable); **anomaly detection** on read-volume threshold → alert | **MAS 9.2.1 (privileged access), 9.1.1 (never-alone / SoD), 15.1 (audit), 11.1.2 (detect unauthorised access)** | Audit-role insider; further mitigated by quarterly access review + two-role gate |
| OF-4.9 | Chain archival immutability (**staging bucket per Targeted adjustment #6**) | **Pre-commit staging bucket (no Object Lock)** receives archive writes first; **integrity check (HMAC + partition-seal manifest)** runs against staging; on success, copy to Compliance-locked bucket and delete staging entry; flagged as **E6 implementation requirement** | **MAS 15.1.2 (auditable areas), 8.4.4 (backup protection), 10.2.1 (key mgmt lifecycle)**; CI-7 7y | Staging-bucket poisoning before check; mitigated by integrity-check content-hash + chain-recorded staging events |
| OF-4.10 | Synthetic corpus sensitivity | Classified Restricted-Internal; access `sre`+`admin`; chain-recorded generation + access; **pattern catalog k-anonymity ≥5** before synthesis; SME validation gate | **MAS 11.1.6 (non-prod data), 3.3 (classification)**; CI-12; pseudonymous-identity carryover | Re-identification via correlation; mitigated by k-anon + SME review |
| OF-4.11 | Threat model + pen test | STRIDE + OWASP LLM Top 10 (§6 below); annual external pen test; E7 adversarial cases | **MAS 13.1, 13.2, 13.4, 4.2.1**; NFR-R | Novel LLM attack classes; continuous E10 feedback |
| OF-4.12 | Audit-evidence packaging | Signed PDF + JSON-LD manifest + CSV cross-reference via `audit-export-api`; chain-recorded export event | **MAS 15.1.1, 15.1.2**; CI-11 | Packaging drift vs regulator expectation; mitigated by client acceptance test |
| OF-4.13 | WAL disk-encryption + WAL-PG agreement verifier | LUKS2 on WAL PVC + dm-verity; daily WAL-PG reconciliation job (already §4.5 E3) | **MAS 10.1.2, 11.1.1, 11.1.2**; NFR-R.4 | Privileged-container escape at host layer; mitigated by PodSecurityPolicy + node hardening |
| OF-4.14 | Identity-issuance RPC hardening | Dedicated RPC in `noc-gov`; SSO token required + admin role + chain-recorded issuance; mTLS only; rate-limit | **MAS 9.1.2, 9.2.1, 9.1.3** | Cross-namespace RPC exposure; mitigated by NetworkPolicy + mTLS |

---

## 3. Key management design (OF-4.1 / T12 resolved)

### 3.1 Hierarchy (three-tier)

```
Root KMS master key         (HSM/FIPS 140-2 L3; custody 2-of-3 split; rotation 365d)
  │
  ├─ Chain KEK              (per per-actor chain; rotation 90d; verification-only after rotation until retention exit)
  │     └─ Per-entry HMAC   (HKDF from KEK + entry-ID; ephemeral)
  │
  ├─ Data-at-rest KEKs      (per volume class: PG-gov, PG-data, WAL, object-storage, model-cache)
  │     └─ DEK              (envelope-encrypted; rotation 180d)
  │
  └─ Internal CA signing    (TLS cert issuance; 90d cert rotation)
```

### 3.2 Rotation cadence

| Key class | Rotation | Trigger | MAS TRM cite |
|---|---|---|---|
| Root KMS master | 365d | Scheduled + on custodian change | **10.2.3** appropriate lifespan |
| Chain KEK | 90d | Scheduled; new entries sign with new KEK; old KEK retained verification-only | **10.2.3, 10.2.8** secure destruction after retention |
| Data-at-rest KEK | 180d | Scheduled; rewrap DEKs | **10.2.3** |
| Data-at-rest DEK | Per volume lifecycle | On-demand on suspected compromise | **10.2.7** revocation |
| CTTS service-account (OF-4.6) | 90d | Automated | **9.2.2** |
| TLS internal certs | 90d | Automated via cert-manager | **10.1.2** |

### 3.3 Revocation protocol

1. Chain-recorded `key_revocation` event with `key_id`, reason, revoker actor + role.
2. KMS marks key verification-only; no new signing operations.
3. Rolling re-sign from last valid chain head forward for active chains.
4. **Historical entries remain verifiable with the revoked KEK retained in verification-only status for the full retention window (7y minimum).**
5. Dependent-key cascade per MAS 10.2.7: identify keys derived from or dependent on the compromised key; revoke and re-wrap.
6. Alert routed to `security-admin` on-call.

### 3.4 Revocation-safety rationale (per Targeted adjustment #5)

**Claim:** revoked KEKs retained in verification-only mode do not enable standalone backdated chain forgery.

**Reasoning:**
- Each chain entry's HMAC covers both the payload and `prev_chain_id`, binding it to its predecessor.
- An attacker with a compromised KEK cannot insert a single backdated entry without forking the chain from that insertion point forward (every subsequent entry's `prev_chain_id` would need to be re-signed).
- The chain-integrity verifier (scheduled CronJob, E3 §6.5) walks `prev_chain_id` linkage daily and detects any chain fork or stale head.
- WAL-PG agreement verifier (§4.5 E3) independently confirms that Chain-Write WAL and governance-PG contain the same entries — detects divergence.

**Conclusion:** revoked-but-verifiable is safe **provided chain linkage is intact and the integrity verifier runs daily**. The verifier is a hard operational requirement, not optional.

**Constraint citations:** MAS **10.2.7** (revocation), **10.2.8** (secure destruction), **10.2.10** (key backups), **11.1.2** (detect unauthorised modification).

### 3.5 Custody

- Root KMS master split 2-of-3 across client-appointed custodians.
- Key ceremony chain-recorded at substrate level.
- **No single human holds any single key alone** (MAS **9.1.1** never-alone, **9.2.1** privileged access).
- Quarterly custody attestation chain-recorded.

### 3.6 Residual risk

- Physical HSM compromise — client perimeter.
- 2-of-3 collusion — raises bar but not zero; mitigated by custodian rotation + background review (MAS 3.5).

---

## 4. Encryption design (OF-4.2 resolved)

### 4.1 Data-at-rest inventory

| Store | Mechanism | Key source | Rotation | MAS TRM cite |
|---|---|---|---|---|
| `noc-gov` PG volume | LUKS2 block-level | Vault KEK (separate from `noc-data`) | 180d KEK | **11.1.1, 11.1.3** |
| `noc-data` PG volume (incl. pgvector) | LUKS2 block-level | Vault KEK (separate from `noc-gov`) | 180d KEK | **11.1.1, 11.1.3** |
| Chain-Write WAL PVC | LUKS2 block-level | Vault KEK (separate KEK) | 180d KEK | **11.1.1, 10.2.6** (diversification) |
| Object storage (Ceph/S3-compat) | Ceph OSD + bucket-level SSE | Vault-backed | 180d KEK | **8.4.4, 11.1.1** |
| Model cache (vLLM weights) | LUKS2 block-level | Vault KEK | 180d KEK | **11.1.1** |
| Prometheus TSDB | Platform-default PV encryption | Platform-managed | Platform cadence | **11.1.1** |

### 4.2 Separate-KEK rationale

**Per MAS 10.2.6 (diversification) and E3 Targeted adjustment #1 pseudonymity strength:** `noc-gov` and `noc-data` KEKs are explicitly separate. Compromising the incident-tier KEK does not decrypt the governance-tier volume. The two-cluster architecture is preserved at the crypto layer as well as the compute layer.

### 4.3 In-transit

- TLS 1.3 mandatory on all service-to-service and ingress paths (MAS **10.1.2**, **11.2.1**).
- **mTLS** on `Chain-Write Service → noc-gov PG` (strongest interior boundary).
- Internal CA via cert-manager; 90d rotation.
- **Data-in-use residual:** GPU memory during inference is not end-to-end encrypted; mitigated by node isolation + namespace RBAC + IR-O.4 (no external egress). Flagged per MAS 11.1.1 "data in use" as PAR in §1.2.

### 4.4 Constraint citations
MAS **10.1.2, 10.2.1, 10.2.4, 10.2.6, 11.1.1, 11.1.3**; IR-O.4; E3 Targeted adjustment #1.

---

## 5. RBAC design (OF-4.5 resolved)

### 5.1 Roles (5)

| Role | Purpose | Typical holder |
|---|---|---|
| `operator` | NOC agent; reviews recommendations | Rostered NOC staff |
| `supervisor` | Oversees operators; escalation authority | NOC shift lead |
| `auditor` | Reads audit surfaces + identity map | Compliance / internal audit |
| `admin` | Platform admin; configuration changes | Platform SRE / security lead |
| `sre` | Operates services; no audit-read | Infra team |

### 5.2 Permission matrix

| Capability | operator | supervisor | auditor | admin | sre |
|---|---|---|---|---|---|
| View pending recommendations | ✓ | ✓ | ✓ (RO) | ✓ (RO) | — |
| Approve / reject / override (FR-D.1–3) | ✓ | ✓ | — | — | — |
| View operator-decision history | self | team | all | all | — |
| Configure reason-code taxonomy (CI-2) | — | — | — | ✓ | — |
| View Layer-2 audit views | — | ✓ (own team) | ✓ (all) | ✓ (all) | — |
| Read `operator_identity_map` (single-record) | — | — | ✓ | — | — |
| **Bulk read `operator_identity_map`** | — | — | ✓ requires joint admin session | ✓ requires joint auditor session | — |
| Issue/retire pseudonymous IDs | — | — | — | ✓ | — |
| Read `governance_chain` (raw) | — | — | ✓ | ✓ | — |
| Write to `governance_chain` | via Chain-Write Service only | via Chain-Write Service only | — | — | — |
| Trigger chain-integrity verification on-demand | — | — | ✓ | ✓ | — |
| Deploy / restart services | — | — | — | ✓ | ✓ |
| Rotate keys | — | — | — | ✓ (joint auditor session) | — |
| View Prometheus / Grafana operational | ✓ (own) | ✓ (team) | ✓ (audit views) | ✓ | ✓ |
| Read SOP sources (raw files) | — | — | ✓ | ✓ | — |
| Generate audit-export bundle | — | — | ✓ | ✓ | — |

### 5.3 Principles

1. **Separation of duties (MAS 9.1.1):** `sre` cannot read identity map; `auditor` cannot deploy; key-rotation + bulk identity-map read require two-role sessions.
2. **Least privilege (MAS 9.1.1):** `operator` scoped to incident-handling UI only.
3. **No self-audit:** `admin` assumes `auditor` role in a separate session (chain-recorded role-assumption) to read raw chain in audit capacity.
4. **All role assignments and role-assumptions chain-recorded** (AG9e-1 Orchestrator-gated).
5. **Quarterly access review** (MAS 9.1.6) — CronJob posts review ticket to supervisor + admin; exceptions chain-recorded.

### 5.4 Constraint citations
MAS **9.1.1, 9.1.2, 9.1.3, 9.1.6, 9.2.1, 9.2.2, 15.1**; FR-D human-review role surface; SEAM-5 ownership-tier (all roles are user-tier per S6 §6 Principle 5).

---

## 6. Threat model

### 6.1 Scope
NOC Incident Management product on OpenShift AI (IR-O.1 / IR-O.3). 4WRD governance-layer threats (Claude Agent SDK substrate) are out of scope.

### 6.2 Principal assets
1. Governance chain integrity + confidentiality of identity mapping.
2. Operator decisions (non-repudiation).
3. SOP corpus integrity.
4. Model-serving pipeline (reasoning quality).
5. CTTS write-back correctness.
6. Audit-evidence availability.

### 6.3 STRIDE by component

| Component | Threat class | Threat | Mitigation | Residual |
|---|---|---|---|---|
| Intake Adapter | Spoofing | Forged CTTS payload | CTTS mTLS + service-account token + schema validation + malformed-rejection chain (E3 §3.1 FR-A.3) | CTTS compromise — upstream client risk |
| Intake Adapter | Tampering | Modified-in-transit | TLS 1.3; schema + content-hash | TLS-break scenarios |
| Agent Orchestrator | EoP/Tampering | Prompt injection via incident text | Input sanitisation; model sandboxing (no tool invocation from incident text); **FR-D.6 human-review gate is structural mitigation**; see §6.4 LLM01 | Subtle biasing reaches reviewer → reviewer vigilance + training |
| Agent Orchestrator | Info Disclosure | Reasoning trace leaks sensitive field | Trace stored in chain (encrypted at rest); UI-exposed trace sanitised per sensitivity class | Insider-with-chain-read risk → mitigated by RBAC + OF-4.8 |
| Ticket Correlation Agent | Info Disclosure | Cross-incident leakage via similarity search | Single-tenant per E3 §11.4; future multi-tenant is separate S-cycle | N/A in single-tenant |
| SOP Agent | Tampering | RAG poisoning via malicious SOP ingest | SOP source authenticated upload; ingestion chain-recorded; chunk provenance + `content_hash`; SME review on version bump; 90d deprecation window provides rollback | Insider with SOP-write access; see §6.4 LLM09 |
| Chain-Write Service | Tampering | Chain-entry forgery | HMAC per entry + prev-entry linkage; append-only DB policy; §3 key mgmt | Master-key compromise → 2-of-3 custody (§3) |
| Chain-Write Service | Repudiation | Operator denies decision | Chain-recorded decision with pseudonymous ID + SSO binding in identity map | Identity-map tamper → mitigated by §4 separate KEK + OF-4.8 bulk-read controls |
| Chain-Write WAL | Tampering | WAL file modification on disk | LUKS2 + dm-verity + daily integrity verifier (OF-4.13) | Privileged-container escape |
| `noc-gov` PG | Info Disclosure | Identity-map breach | Separate cluster + separate KEK + tight RBAC + auditor-only read + bulk-read two-role gate (OF-4.8) | Audit-role insider (residual ranked #1) |
| `noc-data` PG | Info Disclosure | Incident data breach | Encryption at rest (§4) + network isolation + RBAC | DB-admin insider → two-role on prod access |
| Object storage archive | Tampering | Retroactive archive edit | Object Lock Compliance mode + staging-bucket integrity gate (OF-4.9) + partition-seal manifest HMAC | Storage-vendor-level compromise |
| Reviewer UI | Spoofing | Session hijack | Cookie `Secure+HttpOnly+SameSite=Strict`; CSRF token on state-changing requests; session TTL 8h sliding / 12h absolute | XSS → CSP + Jinja2 auto-escape + HTMX-only inline |
| Reviewer UI | EoP | Privilege escalation via API | Authorisation check per endpoint; FR-D.6 enforced server-side | FastAPI zero-day |
| Review API | DoS | Recommendation flood | CTTS poll rate limits + HPA + circuit breaker (MAS 11.2.7) | Upstream CTTS anomaly |
| Model serving (vLLM) | Info Disclosure | Prompt leakage via KV-cache residue | Per-request KV-cache isolation (vLLM native); IR-O.4 no external egress | Model-weights extraction via timing — low-impact on-prem |
| Keep-alive daemon | Spoofing | Compromised ping job emits malicious prompts | Service-account restricted; ping prompt static + content-hashed; chain-recorded | Container-level compromise |
| Audit-export API | Info Disclosure | Unauthorised export | `auditor`-only + chain-recorded export + rate-limit | Social-engineered audit role → OF-4.8 two-role on bulk + rate-limit |

### 6.4 OWASP LLM Top 10 supplement (per Targeted adjustment #3)

Mapping selected LLM-specific threats to product components and mitigations. OWASP LLM Top 10 is the reference frame for AI-app threat modelling where classical STRIDE under-specifies.

| LLM# | Threat | Product exposure | Mitigation | Residual / constraint cite |
|---|---|---|---|---|
| **LLM01** | **Prompt Injection** — attacker embeds instructions in user input (incident text, CTTS payload fields, SOP documents) that manipulate model behaviour | Diagnosis/Correlation/SOP agents receive untrusted incident text; SOP Agent receives retrieved chunks which could contain injected content | (a) Input sanitisation + schema-validated intake (E3 §3.1); (b) **No tool invocation from incident or SOP text** — agents are reasoning-only, action authority lies with FR-D.6 human reviewer; (c) output-guard filters flag suspicious recommendations (e.g. containing URLs, commands, or unexpected action verbs); (d) chain-recorded prompt + retrieved chunks for forensic reconstruction; (e) SOP-ingestion SME review gate before new version activates | Direct prompt injection never fully eliminable at LLM state of art — **FR-D.6 human-review gate is the structural backstop**; MAS **11.1.2** detect unauthorised modification |
| **LLM02** | **Insecure Output Handling** — downstream systems act on LLM output without validation | Review API writes recommendations to incident-tier PG; Reviewer UI renders recommendation text; CTTS write-back sends operator decision | (a) Recommendation output is **presented, not executed** — no direct action authority; (b) Reviewer UI escapes all LLM output (Jinja2 auto-escape + CSP); (c) CTTS write-back sends **structured fields** (decision class, reason code, operator_id), not free-form LLM text; (d) action-verb whitelist on any executed field | Operator acts on LLM-shaped recommendation — FR-D.6 review remains the integrity check; MAS **6.1.2** output-encoding |
| **LLM06** | **Sensitive Information Disclosure** — model outputs leak confidential data from training or context | Reasoning trace may echo incident-specific details; SOP chunks may contain sensitive procedure text; model weights may carry training-data residue | (a) Reasoning trace stored in governance chain (encrypted at rest §4); UI-exposed trace sanitised by sensitivity class; (b) SOP corpus classified per MAS **3.3**; chunk retrieval restricted to per-incident agent scope; (c) Granite weights are vendor-supplied + on-prem (IR-O.4) — no external training-data exfiltration risk; (d) prompt-log retention tied to chain retention (7y) and encryption | Cross-incident leakage mitigated by single-tenant §11.4 + per-request KV isolation; MAS **11.1.1, 11.1.3** |
| **LLM08** | **Excessive Agency** — LLM granted broad action authority that exceeds its trust level | Orchestrator + agents could in principle trigger side-effects if wired to tools | (a) **FR-D.6 human-review gate is non-waivable per S6 §6 Principle 5** — all state-changing actions (CTTS write-back, operator_decision) require human approval; (b) agents have no direct action authority — only produce recommendations; (c) Agent Orchestrator cannot bypass Review API to write CTTS; (d) MVGH constraints (SEAM-5, override-human-only) enforce human-in-the-loop at architecture level | Excessive agency cannot emerge without architectural change; explicitly declared structural — MAS **6.1.2** access control; S6 Principle 5 |
| **LLM09** | **Overreliance** — operators treat LLM output as authoritative without scrutiny | Reviewer UI presents ranked recommendations; time-pressured operators may rubber-stamp | (a) **Reasoning trace + SOP references + confidence flags** shown alongside recommendation (E3 §3.3 UI features); (b) `insufficient_data` / `none_found` / `no_applicable_sop` flags surface model uncertainty (FR-B.2.3/B.3.4/B.4.4); (c) approval/reject/override ratios per operator chain-recorded and surfaced in Layer-2 + quarterly operator-calibration review; (d) FR-D.5 "recommendation unavailable" explicit state prevents hallucinated-default; (e) operator training programme addresses LLM-caveats (CAR) | Overreliance survives as human-factors risk; mitigated by (a)–(e) + continuous calibration feedback via E10; MAS **3.6** (awareness training — CAR) |

### 6.5 Principal residual risks (ranked)
1. **`auditor`-role insider** — mitigated by OF-4.8 two-role gate + rate-limit + anomaly detection; not fully eliminable.
2. **Novel LLM attack classes** — prompt-injection vector evolves (LLM01); FR-D.6 + E10 feedback are structural backstops.
3. **SOP poisoning by authorised uploader** — chunk provenance + version-pinning + 90d deprecation window provide rollback; does not prevent initial poisoning.
4. **Client IdP compromise** — upstream client responsibility (CAR-12); mitigated by assertion pinning + replay cache + short TTL.
5. **Operator overreliance** (LLM09) — human-factors risk mitigated by calibration feedback, not eliminated.

### 6.6 E7 test exercises
- Prompt-injection pen test (LLM01).
- Output-validation bypass attempt (LLM02).
- SOP-poisoning scenario (LLM06 + LLM09).
- Identity-map tamper detection (OF-4.8).
- WAL-PG divergence simulation (OF-4.13).
- Overreliance calibration via synthetic-corpus diverse-ground-truth evaluation (LLM09).

### 6.7 Constraint citations
MAS **13.1, 13.2, 13.4, 4.2.1, 11.1.2**; NFR-R; FR-D.6; OWASP LLM Top 10 as supplementary frame.

---

## 7. Compliance evidence register

### 7.1 Evidence artefact table

| Clause (MAS TRM) | Evidence artefact | Lives in | Extraction path |
|---|---|---|---|
| 3.2 (policies) | Cycle exit artefacts + OF register | `docs/` + git | `audit-export-api` signed bundle |
| 4.1–4.5 (framework) | Cycle artefacts + OF register + Layer-2 risk register | `docs/` + `governance_chain` (post-MVGH-β) | `audit-export-api` |
| 5.1–5.8 (project / SDLC) | Cycle chain + pre-commit + AG-3 validator logs | `governance_chain` + pre-commit outputs | Layer-2 `dev_validation_events` |
| 6.1 (secure coding) | E6 pre-commit + SAST/DAST logs | CI artefacts + chain | E6 build logs + chain |
| 6.4 (API) | API inventory + auth-token rotation events | Chain + OpenShift Secret rotation log | Layer-2 `api_security_events` |
| 7.2 (configuration) | `system_version` + `model_version` + `sop_versions_pinned` per entry | `governance_chain.payload_ref` | Layer-2 `configuration_history` |
| 7.5 (change) | Chain change-event entries + GitOps commits | `governance_chain` + git | Layer-2 `change_history` |
| 7.6 (release) | Signed-image registry + release chain entries + two-role promotion logs | Image registry + chain | Signed-image manifest + chain |
| 7.7 (incident) | Per-incident chain lifecycle (intake → agent_output → recommendation → decision) | `governance_chain` + `recommendation` + `operator_decision` | Layer-2 `incident_lifecycle` |
| 7.8 (problem) | **Partial** — governance-chain history + trend dashboards; full problem-mgmt tooling open (OF-4.15) | Chain + Grafana | Layer-2 `incident_trends` |
| 8.1 (availability) | Prometheus SLO dashboards + HPA manifests | OpenShift monitoring + git | Snapshot export |
| 8.2 (recoverability) | DR plan + RTO/RPO binding (OF-4.16 pending) | `docs/` | Static doc |
| 8.4 (backup) | Backup schedule + restore-test logs | PG ops + object-storage manifests | SRE dashboard export |
| 9.1 (user access) | SSO auth events + identity-map events | SSO log + `governance_chain` | IdP export + Layer-2 `identity_events` |
| 9.2 (privileged) | Admin role-assumption + two-role ops + service-account rotation | `governance_chain` + Vault audit | Layer-2 `privileged_actions` |
| 10.1 (crypto alg) | Cipher inventory + cert-manager rotation log | docs + cert-manager events | Signed manifest |
| 10.2 (key mgmt) | Key-rotation chain events + custody attestations + Vault audit | Chain + Vault | Layer-2 `key_lifecycle` |
| 11.1 (data) | Encryption inventory (§4) + LUKS/Vault manifests + DLP config | docs + Vault audit | Signed manifest |
| 11.2 (network) | NetworkPolicy manifests + egress-monitor alerts | git + Prometheus | Git export + alert history |
| 11.3 (system) | Hardening-baseline attestation + image-signing config | docs + registry | Signed manifest |
| 11.4 (virtualisation) | OpenShift baseline + admission-controller config | git | Config export |
| 12.2 (monitoring) | Alertmanager history + dashboard snapshots | Alertmanager + Grafana | Scheduled snapshot export |
| 12.3 (cyber IR) | Cyber-IR playbook (OF-4.32 pending) + post-incident chain reconstruction | `docs/` + chain replay | Mode-A replay bundle |
| 13.1 (vulnerability) | SBOM + image-scan results | CI artefacts | Signed scan report |
| 13.2 (pen test) | Annual pen-test report (OF-4.25) | Client doc store + chain-recorded receipt | Report delivery |
| 13.6 (remediation) | OF register + closure-chain events | `docs/` + chain | Layer-2 `remediation_register` |
| 15.1 (IT audit) | Layer-2 audit views + audit-export bundle | `noc-gov` PG + object storage | `audit-export-api` |
| MAS FEAT (OF-4.23) | Reasoning-trace capture + model-version + human-review chain | `governance_chain` | Layer-2 `ai_explainability` (applicability pending) |

### 7.2 Extraction contract

`audit-export-api` produces a signed bundle:
```
{
  metadata.json        — export metadata, bundle-ID, requester, time-range
  chain-slice.jsonl    — governance_chain entries in range, with HMAC
  layer2-views.csv[]   — selected Layer-2 view outputs
  sop-versions.jsonl   — pinned SOP version snapshots referenced
  manifest.json.sig    — signature over all above, binding to Root KMS master (§3)
}
```
Client-consumable PDF is generated from the bundle on request. Signature verification tooling is E6 (OF-4.24).

### 7.3 Per-data-class retention schedule (OF-4.4 — pending client legal sign-off per Targeted adjustment #8)

| Data class | Retention | Basis | MAS TRM cite |
|---|---|---|---|
| `governance_chain` entries | 7y minimum | CI-7; 15.1, 8.4.2 | **15.1, 8.4.2** |
| Incident payload + agent output | 7y | CI-7 | **3.3, 8.4.2** |
| Operator decision | 7y | CI-7; 15.1 | **15.1** |
| SOP chunks (active + deprecation window) | Active + 90d | E3 §3.2; 7.5 change mgmt | **7.5** |
| SOP chunks (archived) | 7y | CI-7 | **8.4.2** |
| `operator_identity_map` | 7y + sector overlay (pending client legal) | CI-5; 9.1.3 | **9.1.3** |
| Prometheus operational metrics | 90d hot + 2y warm | Operational sufficiency | **12.2.2** |
| Alert events | 2y | Operational | **12.2.2** |
| Synthetic corpus | Indefinite versioned | E7 traceability | — |
| Pen-test reports | 7y | 13.2 + MAS audit window | **13.2** |
| **Key-rotation events** | **10y** (key ops outlive keys) | 10.2.10 backup + audit | **10.2.10, 15.1** |
| Vault audit log | 7y | 10.2.1 key-mgmt lifecycle | **10.2.1** |

**Flag per Targeted adjustment #8:** if client legal sign-off on per-class retention is not received before E4 Exact cycle closes, this table carries "**Pending client legal confirmation — 7-year anchor is conservative minimum**" on all rows without explicit regulatory anchor. On sign-off, the flag is removed and any per-class extension is applied.

---

## 8. Open items for E5 / E6 / E7 / E8 / E9

Inherited from Explorative (14 items) plus 5 new from Targeted clause-number pass.

| OF-# | Item | Handover |
|---|---|---|
| OF-4.15 | Problem-management workflow tooling (MAS 7.8) | E5 data model + E6 UI |
| OF-4.16 | DR RTO/RPO numerical binding (MAS 8.2) | E8 + client sign-off |
| OF-4.17 | Vulnerability mgmt cadence + scanner selection (MAS 7.4, 13.1) | E6 pipeline + E9 ops |
| OF-4.18 | Client hardening baseline adoption (MAS 11.3.1, 11.3.2) | E6 image-build; client-supplied baseline |
| OF-4.19 | Secure coding standards binding (MAS 6.1) | E6 pre-commit + review; client-supplied standards |
| OF-4.20 | Physical access controls (MAS 8.5.6) | **CAR-11** — client data-centre; out of 4WRD |
| OF-4.21 | Threat-intel feed integration (MAS 12.1) | **CAR-5** — client SOC |
| OF-4.22 | **CLOSED** — MAS TRM clause-number verification pass | Completed this cycle |
| OF-4.23 | MAS FEAT / Veritas applicability determination | Client legal + compliance; reopens E4 if in-scope |
| OF-4.24 | Audit-export-api bundle schema + signature-verification tooling | E6 build; E7 audit-bundle round-trip test |
| OF-4.25 | Pen-test scope + external vendor selection (MAS 13.2) | E7 + client procurement |
| OF-4.26 | BCP tabletop exercise schedule (MAS 13.3) | E9 + client ops |
| OF-4.27 | Quarterly access-review automation (MAS 9.1.6) | E6 CronJob + UI |
| OF-4.28 | Two-of-three custodian key-ceremony rehearsal (MAS 10.2.4/10.2.10) | E6 + client security officer |
| OF-4.29 | Vendor-risk review + model-weights availability plan (MAS 5.3) | E4 Exact if possible; else E6 |
| OF-4.30 | EOS register + technology-refresh plan (MAS 7.3) | E9 ops runbook |
| OF-4.31 | MFA enforcement contract with client IdP (MAS 9.1.5) | E4→E6 negotiation |
| OF-4.32 | Cyber-IR playbook for product-layer events (MAS 12.3) | E4→E9 ops |

---

## 9. Requirements coverage confirmation

| E4 deliverable | Source requirement / constraint | Satisfaction |
|---|---|---|
| §1 MAS TRM control mapping | OF-4.3 (S5); CI-7; S6 §4.6 honesty bound | Delivered with DSC/EVA/PAR/CAR/N/A classification + client-accountability footer |
| §2 Security controls hardening 12 E3 OFs | E3 §9 OF-4.1 through OF-4.14 | All 14 items hardened (OF-4.13/4.14 from E3 Targeted adjustments) |
| §3 Key management | OF-4.1; T12 (S4); MAS 10.2 | Three-tier + rotation + revocation resolved |
| §4 Encryption at rest | OF-4.2; MAS 10.1, 10.2.6, 11.1.1, 11.1.3 | Delivered with separate KEKs per volume class |
| §5 RBAC matrix | OF-4.5; MAS 9.1, 9.2; FR-D | 5-role matrix with SoD + two-role gates |
| §6 Threat model | OF-4.11; MAS 4.2.1, 13.1, 13.2, 13.4 | STRIDE + OWASP LLM Top 10 (Targeted adjustment #3) |
| §7 Compliance evidence register | OF-4.3 / 4.12; MAS 15.1 | Per-clause evidence paths + extraction contract + retention schedule |
| §8 Open items | Explorative + Targeted | 14 inherited + 5 new = 19 items (OF-4.22 closed, 18 active) |

---

## 10. Flags and posture declarations

### 10.1 DISCIPLINE-2 preserved (per Targeted adjustment #9)

Every mechanism selection cites either a MAS TRM clause, an E3-inherited requirement, or a FR/NFR/IR constraint. **Explorative pattern-familiarity citations ("OpenShift-native") have been replaced throughout with explicit IR-O.1 (deploy on OpenShift AI), IR-O.3 (agent orchestration on OpenShift), and IR-O.4 (no external egress) citations** where applicable.

### 10.2 Governance mode: partial

Cycle-primitive discipline active; MVGH-β Wave-1 elements activate progressively. §1.0 header discloses DSC-interim-PAR distinction to any consumer of this artefact.

### 10.3 4WRD substrate vs NOC product runtime — separate systems

Preserved from E3. 4WRD Claude Agent SDK developer-side; NOC product on OpenShift AI. IR-O.6 restated.

### 10.4 Honesty bound reaffirmed

No row in §1 or §7 claims MAS regulatory pre-approval. All DSC rows apply to MVGH-β-active state. All EVA rows describe evidence artefacts; institution files attestation. CAR rows name client accountability.

### 10.5 Client-input dependencies still open

CI-1, CI-1a, CI-2, CI-3, CI-4, CI-6 (retention refinement per OF-4.4), CI-8, CI-13, CI-14, CI-15, CI-16, CI-17, CI-18, CI-19, CI-20. Plus new **CAR-1 through CAR-18** per §1.3. Not blocking E4 Exact; gate later cycles.

### 10.6 OF-4.22 closure declaration

MAS TRM clause-number verification pass is complete against the ratified **MAS TRM Guidelines January 2021** (docs/references/MAS-TRM-2021.pdf). Any future revision of the document requires a re-verification cycle, tracked as an E10 Feedback and Learning input.

---

## 11. E5 Data inheritance

E5 opens with this artefact as primary input.

**E5 inherits:**
1. **Full §1 MAS TRM mapping** — data-class-level retention table (§7.3) drives E5 data model retention bindings.
2. **§3 key hierarchy** — E5 data-at-rest encryption integrations use the KEK classes defined here.
3. **§5 RBAC matrix** — E5 data access patterns map to these roles.
4. **§6 threat model** — E5 must preserve LLM06 sensitive-information-disclosure mitigations in any new data surface.
5. **18 active OF items** — principally OF-4.10 (corpus sensitivity), OF-4.15 (problem-management data model), OF-4.16 (DR RTO/RPO for data stores).
6. **OF-4.4 flag** — per-class retention pending client legal sign-off; E5 data-class definitions honour this.

---

## 12. Carry-forwards and Disciplines

**Carry-forwards (4, inherited):**
- CARRY-FWD-1 — Need 13 partial technical-constraint readiness.
- CARRY-FWD-2 — Anthropic platform concentration (substrate only; product runs Granite on OpenShift AI).
- CARRY-FWD-3 — C4 capacity binding constraint.
- CARRY-FWD-4 — MVGH-β first governed delivery; partial-governance interim surfaces explicitly in §1.0.

**No new carry-forwards introduced at E4.**

**Disciplines (3, inherited):**
- DISCIPLINE-1 — source-of-count tagging.
- DISCIPLINE-2 — constraint citations on every selection; audit per Targeted adjustment #9.
- DISCIPLINE-3 — qualitative classification cites criterion.

**No new disciplines introduced at E4.**

---

*End of E4 exit artefact.*
