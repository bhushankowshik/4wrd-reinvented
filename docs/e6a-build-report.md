# E6a Build Report

**Date:** 2026-04-18
**Status:** M11 complete — E6a exit criteria met

## Services
14 services running/healthy via Docker Compose.

## Sample recommendation
- Incident: CTTS-ALPHA-0001 (BTS-447 packet loss, P2)
- Decision: FIELD_DISPATCH
- Confidence: 0.6 (llama3.2:3b)
- Correlation: 2 related incidents found via HNSW
- SOP: no_applicable_sop (fixture SOP corpus limited)

## Test results
68 passed in 6.68s

## Deviations from E6a spec
1. Grafana port 3000→3030 (host conflict)
2. Vault dev: SKIP_SETCAP=true + VAULT_DISABLE_MLOCK=true
3. llama3.2:3b hypothesis coercion in diagnosis.py
4. content_hash: direct hashlib.sha256(bytes) not 
   canonical-JSON re-serialisation
5. dblink skip in dev pgvector image

All deviations are environment-specific. 
Architecture unchanged.

## Next steps
- Swap to llama3.1:70b when download completes
- E6b: wire real HMAC chain writes when 
  MVGH-β Wave 1 substrate ready
- E7: test plan against this build
- MVGH-β setup: start as parallel workstream
