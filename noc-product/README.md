# NOC Incident Management — E6a Build

Implementation of the NOC Incident Management product
as specified in `docs/e6a-exit-artefact.md`. This is
the Docker Compose development environment. Production
OpenShift AI deployment is E8 scope and lives under
`deploy/`.

## Prerequisites

- macOS (tested on Mac Studio M3 Ultra) or Linux
- Docker Desktop or Colima (engine + Compose v2)
- Ollama running on the **host machine** (not in
  Docker) — services reach it via
  `host.docker.internal:11434`
- `uv` for local dev loops (`pip install uv`)
- Python 3.11+ if running tests outside Docker

## Host Ollama setup

```bash
brew install ollama
ollama serve
ollama pull llama3.2:3b
ollama pull nomic-embed-text
# later: ollama pull llama3.1:70b
```

Swap the reasoning model via `.env`:
```
OLLAMA_REASONING_MODEL=llama3.1:70b
```
No code change required — all model calls route
through the `ModelBackend` abstraction.

## Bring up the stack

```bash
cp .env.example .env
docker compose build
docker compose up -d
./scripts/bootstrap.sh     # migrations + seed data
docker compose ps          # every service should be healthy
```

Bring-up order is handled by Compose `depends_on`
with `condition: service_healthy`. Initial build
may take 10–15 min due to Python wheel compilation
(pdfminer, psycopg).

## Service endpoints

| Service            | URL                          |
|--------------------|------------------------------|
| Reviewer UI        | http://localhost:8080        |
| Agents API         | http://localhost:7002        |
| Chain-Write        | http://localhost:7001        |
| Identity-Audit API | http://localhost:7005        |
| Mock CTTS          | http://localhost:8001        |
| MinIO Console      | http://localhost:9001        |
| Vault              | http://localhost:8200        |
| Dex                | http://localhost:5556/dex    |
| Prometheus         | http://localhost:9090        |
| Grafana            | http://localhost:3000        |
| Alertmanager       | http://localhost:9093        |

Default Dex test users (password: `password`):
- `operator@example.com` — role `operator`
- `supervisor@example.com` — role `supervisor`
- `auditor@example.com` — role `auditor`
- `admin@example.com` — role `admin`
- `sre@example.com` — role `sre`

## Run tests

```bash
pip install uv
uv pip install -e '.[dev]'
pytest                                   # unit + fast integration
pytest tests/adversarial -v              # OWASP LLM Top 10
pytest tests/chain -v                    # chain integrity walks
pytest -m 'not slow'                     # skip long-running
```

Integration tests assume the Compose stack is up.
Unit tests run standalone.

## Fixture data

`fixtures/incidents/` holds 3 representative
incident payloads (see `fixtures/README.md`).
`fixtures/sops/` holds 2 Telco NOC SOPs that
M7 ingestion consumes.

## Exit verification (M11)

```bash
./scripts/e6a_exit_verify.sh
```
Runs the full incident lifecycle across the 3
fixture incidents and prints a sample
recommendation payload.

## Deviations from E6a spec

- **Model backend:** Ollama on host (not vLLM in
  Compose). Swap at E8 via config. See §2 of
  `docs/e6a-exit-artefact.md` — the ModelBackend
  abstraction keeps this a config change.
- **CPU-only inference:** dev latency numbers are
  indicative; NFR-L.1 hard gate moves to E8 on
  GPU hardware.
- **Kafka not brought up:** intake uses file-drop
  + mock CTTS polling instead (E6a §3.12 was
  optional).
- **Object Lock Compliance on MinIO archive
  bucket:** left off in dev to keep test cycles
  fast (OF-6.7 — flip at E8).
- **deploy/:** scaffolded but empty. Not built,
  not linted, not tested in E6a CI. E8 owns.

## Layout

```
noc-product/
  docker-compose.yml
  pyproject.toml
  .env.example
  README.md
  services/              # all Python services
  db/migrations/         # Alembic migrations
  dev/                   # Dockerfile, dex config, Grafana/Prom
  fixtures/              # incidents + SOPs
  scripts/               # bootstrap + exit verify
  tests/                 # unit, integration, adversarial, chain
  deploy/                # E8 scope — not built in E6a
```
