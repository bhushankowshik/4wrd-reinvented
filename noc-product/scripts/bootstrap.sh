#!/usr/bin/env bash
# Bootstrap the Docker Compose dev environment.
# Idempotent — safe to re-run.

set -euo pipefail

cd "$(dirname "$0")/.."

export PGHOST_DATA=${NOC_DATA_HOST:-localhost}
export PGPORT_DATA=${NOC_DATA_PORT:-5433}
export PGHOST_GOV=${NOC_GOV_HOST:-localhost}
export PGPORT_GOV=${NOC_GOV_PORT:-5434}
export PGUSER=${NOC_DATA_USER:-noc}
export PGPASSWORD=${NOC_DATA_PASSWORD:-noc}

wait_for_pg () {
  local host=$1 port=$2 db=$3
  echo "Waiting for ${host}:${port}/${db}..."
  for i in {1..60}; do
    if docker compose exec -T "$host" pg_isready -U noc -d "$db" >/dev/null 2>&1; then
      echo "  up."
      return 0
    fi
    sleep 2
  done
  echo "Timeout waiting for $host"; return 1
}

wait_for_pg noc-data 5432 noc_data
wait_for_pg noc-gov  5432 noc_gov

apply () {
  local host=$1 db=$2 file=$3
  echo "Applying $file → $host/$db"
  docker compose exec -T "$host" psql -U noc -d "$db" -v ON_ERROR_STOP=1 < "$file"
}

for f in db/migrations/noc_data/*.sql; do
  apply noc-data noc_data "$f"
done
for f in db/migrations/noc_gov/*.sql; do
  apply noc-gov noc_gov "$f"
done

echo "Creating MinIO buckets..."
docker compose exec -T minio sh -lc '
  mc alias set local http://localhost:9000 minioadmin minioadmin >/dev/null
  mc mb --ignore-existing local/noc-archive >/dev/null
  mc mb --ignore-existing local/noc-staging >/dev/null
  mc ls local
'

echo "Seeding identity map (Dex test users)..."
docker compose exec -T noc-gov psql -U noc -d noc_gov -v ON_ERROR_STOP=1 <<'SQL'
INSERT INTO operator_identity_map
  (pseudonymous_id, sso_subject_id, display_name, role, issuance_chain_id)
VALUES
  ('pseudo-op-001', 'op-001', 'Operator One', 'operator',
     '00000000-0000-0000-0000-000000000001'),
  ('pseudo-sv-001', 'sv-001', 'Supervisor One', 'supervisor',
     '00000000-0000-0000-0000-000000000002'),
  ('pseudo-au-001', 'au-001', 'Auditor One', 'auditor',
     '00000000-0000-0000-0000-000000000003'),
  ('pseudo-ad-001', 'ad-001', 'Admin One', 'admin',
     '00000000-0000-0000-0000-000000000004'),
  ('pseudo-sr-001', 'sr-001', 'SRE One', 'sre',
     '00000000-0000-0000-0000-000000000005')
ON CONFLICT (pseudonymous_id) DO NOTHING;
SQL

echo "Bootstrap complete."
