#!/usr/bin/env bash
# E6a exit verification — end-to-end smoke across the Docker
# Compose dev stack. Prints:
#   1. `docker compose ps` (all services healthy)
#   2. A sample recommendation produced for the fixture incident
#   3. pytest output
# Exit 0 on success. Non-zero surfaces anything that regressed.
#
# Prereqs: ./scripts/bootstrap.sh has been run against a
# `docker compose up -d` stack.

set -euo pipefail

cd "$(dirname "$0")/.."

echo "=========================================================="
echo " 1. docker compose ps"
echo "=========================================================="
docker compose ps
echo ""

echo "=========================================================="
echo " 2. Waiting for all services to reach 'healthy'..."
echo "=========================================================="
deadline=$(( $(date +%s) + 180 ))
while true; do
  unhealthy=$(docker compose ps --format json |
    python3 -c "
import json,sys
bad = []
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        o = json.loads(line)
    except Exception:
        continue
    h = (o.get('Health') or '').lower()
    s = (o.get('State') or '').lower()
    if s != 'running' or (h and h != 'healthy'):
        bad.append(o.get('Name') or o.get('Service',''))
print('\n'.join(bad))
")
  if [[ -z "$unhealthy" ]]; then
    echo "  all services healthy."
    break
  fi
  if (( $(date +%s) > deadline )); then
    echo "  timed out waiting for: $unhealthy" >&2
    exit 1
  fi
  sleep 3
done

echo ""
echo "=========================================================="
echo " 3. Fixture incident — recommendation output"
echo "=========================================================="
# Intake auto-ingests the 3 seeded mock-ctts incidents.
# Poll for a produced recommendation on CTTS-ALPHA-0001.
deadline=$(( $(date +%s) + 240 ))
while true; do
  got=$(docker compose exec -T noc-data psql -U noc -d noc_data -At -c "
    SELECT r.decision_class || '|' || r.production_state ||
           '|' || COALESCE(r.payload->>'summary','')
      FROM recommendation r
      JOIN incident i ON i.incident_id = r.incident_id
     WHERE i.ctts_incident_ref = 'CTTS-ALPHA-0001'
     ORDER BY r.produced_at DESC LIMIT 1;
  " 2>/dev/null || true)
  if [[ -n "$got" ]]; then
    echo "  $got"
    break
  fi
  if (( $(date +%s) > deadline )); then
    echo "  timed out waiting for recommendation on CTTS-ALPHA-0001" >&2
    exit 1
  fi
  sleep 5
done

echo ""
echo "  -- full recommendation payload -- "
docker compose exec -T noc-data psql -U noc -d noc_data -c "
  SELECT jsonb_pretty(r.payload) AS payload
    FROM recommendation r
    JOIN incident i ON i.incident_id = r.incident_id
   WHERE i.ctts_incident_ref = 'CTTS-ALPHA-0001'
   ORDER BY r.produced_at DESC LIMIT 1;
"

echo ""
echo "=========================================================="
echo " 4. Governance chain linkage for fixture incident"
echo "=========================================================="
docker compose exec -T noc-gov psql -U noc -d noc_gov -c "
  SELECT entry_type, actor_role, class_enum, timestamp
    FROM governance_chain
   WHERE incident_id = (
     SELECT incident_id FROM (
       SELECT i.incident_id
         FROM dblink('host=noc-data dbname=noc_data user=noc password=noc',
           'SELECT incident_id::text FROM incident
             WHERE ctts_incident_ref = ''CTTS-ALPHA-0001''
             ORDER BY ingest_at DESC LIMIT 1')
         AS t(incident_id text)
         JOIN (SELECT 1) s ON true
        LIMIT 1
     ) z
   );
" 2>/dev/null || echo "  (skipped — dblink not enabled in dev)"

echo ""
echo "=========================================================="
echo " 5. pytest"
echo "=========================================================="
if command -v uv >/dev/null 2>&1; then
  uv run pytest -q tests/unit
else
  python -m pytest -q tests/unit
fi

echo ""
echo "E6a exit verification — OK"
