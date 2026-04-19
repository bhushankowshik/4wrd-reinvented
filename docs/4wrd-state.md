# 4WRD — Current State

**Date:** 2026-04-19
**Operator:** Bhushan (solo)
**Repo:** bhushankowshik/4wrd-reinvented
**Branch:** main

---

## What exists

### Chain substrate — MVGH-β Wave 1 (mvghb/)
- Real HMAC-SHA256 per-entry signing via HKDF
- Per-actor chains with prev_chain_id linkage
- Master anchor (periodic HMAC over all actor heads)
- Integrity verifier (walks chain, detects tampering)
- Frame Change Sidecar Detector (session boundary + 
  adversarial Tier 2 interrupt)
- Bootstrap script (KEK gen, actor registry, genesis)
- E6b activation script (wires real ChainWriter into 
  NOC product)
- 20 tests passing
- Connected to: noc-gov PostgreSQL (Docker Compose)

### NOC product — E6a + E6b (noc-product/)
- Four agents: Diagnosis, Correlation, SOP, Orchestrator
- LangGraph orchestration
- Ollama inference: llama3.1:70b (reasoning) + 
  nomic-embed-text (embeddings)
- FastAPI + HTMX Reviewer UI (localhost:8080)
- PostgreSQL two-cluster (noc-data + noc-gov)
- MinIO, Vault-dev, Dex OIDC — all in Docker Compose
- 14 services running healthy
- 68 tests passing
- Real HMAC chain writes active (E6b activated)
- Governance chain: 160+ entries with real signatures
- Processed: 4 incidents, operator approvals recorded
- Start: cd noc-product && docker compose up

### SDK harness — full (harness/)
- Intent Cycle: four moments, PARTIAL/REJECTED loop,
  iteration counter, artefact lineage at Moment 4
- Producing Agent: claude-sonnet-4-6 (streaming)
- Adversarial Agent: claude-opus-4-6 (streaming)  
- Research Agent: claude-haiku-4-5-20251001 (Haiku tier,
  Explorative + external refs only)
- 16 skills: S1-S6 (Solutioning), E1-E10 (Execution)
- Config layers: L1 harness, L2 domain, L3 specialisation
  (MAS TRM), L4 engagement
- Layer 2 views: operator, audit, session_replay
- Frame Change Sidecar: boundary scan + 6 external sources
- Artefact Lineage: primary + incidental ref extraction
- Multi-skill orchestrator: gate discipline (chain-enforced
  cycle_close at Exact), skill sequences, runner
- Theory Retirement: tombstones (permanent, durable)
- Extended CLI: run, gate, layer2, sidecar, retire
- 79 tests passing
- Connected to: same noc-gov PostgreSQL as MVGH-β

---

## Governance chain state

| Actor            | Entry count |
|------------------|-------------|
| human            | ~4          |
| producing_agent  | ~3          |
| adversarial_agent| ~2          |
| orchestrator     | ~15         |

Last cycle: S1 Problem Crystallisation, Explorative,
CONFIRMED. Exit artefact: docs/s1-cycle-f7601578-*.md
Problem crystallised: "Multi-session governance-chain 
replay on cold-start for solo operators"

---

## Gate state

| Skill | Gate     | Reason                          |
|-------|----------|---------------------------------|
| S1    | OPEN     | No predecessor                  |
| S2    | BLOCKED  | S1 not closed at Exact          |
| E1    | BLOCKED  | S6 not closed at Exact          |

S1 closed at Explorative — must re-run S1 at Targeted
then Exact to unblock S2.

---

## What is NOT yet done

- S1 at Exact (blocks all of S2-S6)
- S2 through S6 (no cycles run)
- E1 through E10 (no cycles run)
- E7 Test (no test suite run against NOC product)
- E8 Deployment (client OpenShift AI not accessible)
- CAG engagement (cag-data-migration repo — not started
  under harness)
- Wave 2 harness elements (quorum, enforcement) — 
  post-Wave-1 validation

---

## How to run

### Start NOC product
```bash
cd noc-product
docker compose up
# Reviewer UI: http://localhost:8080
# Login: operator@example.com / password123
```

### Run a governed cycle
```bash
cd harness
export ANTHROPIC_API_KEY=<key>
source ../mvghb/.env
uv run harness run \
  --skill S1 \
  --convergence Targeted \
  --direction "..." \
  --knowledge "..." \
  --pdi docs/foundation/INPUT-001-foundation-v4.md
```

### Check gate state
```bash
cd harness
uv run harness gate --skill S2
uv run harness gate --skill E1
```

### Session replay (where did I leave off)
```bash
cd harness
uv run harness layer2 replay
```

### Verify chain integrity
```bash
cd mvghb
uv run python -m mvghb.cli verify --actor all
```

---

## Key files

| File | Purpose |
|------|---------|
| docs/foundation/INPUT-001-foundation-v4.md | Foundation |
| docs/s1-cycle-f7601578-*.md | First governed cycle exit artefact |
| mvghb/mvghb/chain_write/writer.py | Real ChainWriter |
| harness/harness/intent_cycle.py | Intent Cycle orchestrator |
| harness/harness/skills/__init__.py | 16-skill registry |
| harness/harness/orchestrator/gate.py | Gate discipline |
| noc-product/docker-compose.yml | NOC product services |

---

## Next recommended action

Run S1 at Targeted then Exact against the crystallised
problem or start fresh with the CAG engagement as the
first fully governed client delivery under the harness.


---

## UI update — 2026-04-19

harness/ui/ is now the primary interaction surface.

- FastAPI + xterm.js browser terminal at localhost:8080
- Verification panel appears at Moment 3 with 
  CONFIRMED / PARTIAL / REJECTED buttons
- PDI auto-populates from last exit artefact for 
  selected skill, falls back to predecessor skill
- Kill Process button terminates stuck processes
- Convergence state tooltip explains each state
- Start: cd harness/ui && bash run.sh

## Estimator S1 status — 2026-04-19

AI-Assisted Solutioning Estimator S1 is ratified 
at Exact. S2 is OPEN. Ready to run S2.

Last S1 exit artefact: 
  harness/docs/s1-cycle-80e8970e-20260419T093341Z.md

