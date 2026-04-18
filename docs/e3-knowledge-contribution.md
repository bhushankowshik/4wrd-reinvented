# E3 Knowledge Contribution

**Date:** 2026-04-18
**Status:** Ratified
**Role:** Knowledge contribution for E3 Architecture 
first Direction Capture.

---

## Resolved E2 client-input items

**CI-11 — Reviewer UI:**
Separate review application. Purpose-built UI owned 
by this product. Recommendation presentation, 
approval/rejection/override capture, and reason codes 
all in product UI. Not inline in CTTS.

**CI-9 — Ticketing system:**
System name: CTTS. Integration pattern: REST API 
polling (pull). We poll CTTS for new/updated incidents.
Write-back via REST API against originating incident.

**CI-10 — SOP/KB structure:**
Structured documents (Word, PDF). Large corpus — 
thousands of documents. RAG with vector search is 
the likely retrieval pattern for E3. Ingestion 
pipeline, chunking strategy, and index maintenance 
are non-trivial at this scale.

**CI-5 — Operator identity:**
Pseudonymous in governance chain (anonymised but 
internally traceable). Authentication via SSO/SAML. 
SSO token carries real identity; governance chain 
records pseudonymous identifier with internal 
mapping.

**CI-7 — Retention:**
7 years. Regulatory framework beyond MAS TRM unknown; 
7 years is conservative anchor. E4 designs for 7 
years.

**CI-12 — Test-incident set:**
Historical incidents with known outcomes exist. 
Synthetic generation required (historical data not 
directly usable — format or coverage reasons). E3 
must design a synthetic generation approach grounded 
in historical incident patterns.

**NFR-O.3 — Observability destination:**
OpenShift built-in monitoring — Prometheus + Grafana. 
No external monitoring platform required.

---

## E3 architecture decisions to make

From E2, flagged as E3-owned:

1. Agent orchestration framework — LangGraph / 
   LlamaIndex / OpenShift AI Pipelines / other
2. Self-hosted model selection — Llama / Mistral / 
   Granite / IBM-supported candidates
3. SOP retrieval pattern — RAG / vector search 
   (likely given corpus size); chunking strategy; 
   index maintenance approach
4. Correlation search architecture — index / vector 
   / graph
5. CTTS integration pattern — REST polling frequency,
   auth mechanism, schema parsing
6. Reviewer UI platform and framework
7. OpenShift AI deployment topology
8. Retry policy numerics
9. SOP snapshot storage vs reference-by-version-ID
10. Query interface for Layer-2 audit view
11. Replay semantics for test-incident evaluation
12. Synthetic test-incident generation approach

## Constraints E3 must design within

- On-prem RedHat OpenShift AI — no external API egress
  from product runtime (IR-O.4 hard constraint)
- 5-minute diagnosis window; system production 
  sub-budget ≤3 minutes (NFR-L.1 / CI-1a)
- Pseudonymous operator identity via SSO/SAML (CI-5)
- 7-year retention on governance chain and incident 
  records (CI-7)
- Prometheus + Grafana for observability (NFR-O.3)
- Separate review application (CI-11)
- CTTS via REST API polling (CI-9)
- Human-review gate non-waivable (FR-D.6 / 
  INPUT-001 §7 Principle 5)
