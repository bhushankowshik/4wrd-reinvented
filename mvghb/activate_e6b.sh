#!/usr/bin/env bash
#
# activate_e6b.sh — flip noc-product's Chain-Write from E6a stub
# to the MVGH-β Wave 1 real implementation.
#
# Steps:
#   1. Copy mvghb/noc_bridge/writer.py  →  noc-product/services/chain_write/writer.py
#      (backing up the stub to writer.py.e6a-stub-backup)
#   2. Sync MVGHB_KEK (+ mode flag) from mvghb/.env into noc-product/.env
#   3. Restart the chain-write container so it picks up the new writer + env
#   4. Wait for healthz, then POST a smoke /emit request and verify:
#      - HTTP 200 with committed=true
#      - chain_id is a UUIDv4 (real), not the UUIDv5 stub namespace
#      - hmac_signature_hex length == 64 hex chars (32 bytes)
#   5. Query noc-gov for the new governance_chain entry to prove persistence
#
# Idempotent: re-runs are safe. The stub is backed up exactly once.

set -euo pipefail

MVGHB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOC_ROOT="$(cd "${MVGHB_ROOT}/../noc-product" && pwd)"

SRC_WRITER="${MVGHB_ROOT}/noc_bridge/writer.py"
DST_WRITER="${NOC_ROOT}/services/chain_write/writer.py"
STUB_BACKUP="${DST_WRITER}.e6a-stub-backup"

MVGHB_ENV="${MVGHB_ROOT}/.env"
NOC_ENV="${NOC_ROOT}/.env"

STUB_NAMESPACE_UUID="6ba7b810-9dad-11d1-80b4-00c04fd430c8"

say() { printf '\033[1;36m[activate_e6b]\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m[activate_e6b] FAIL:\033[0m %s\n' "$*" >&2; exit 1; }

[[ -f "$SRC_WRITER" ]] || die "missing ${SRC_WRITER}"
[[ -f "$MVGHB_ENV"  ]] || die "missing ${MVGHB_ENV} — run 'mvghb bootstrap init' first"
[[ -f "$NOC_ENV"    ]] || die "missing ${NOC_ENV}"

# ---------- 1. Replace the stub writer (with one-shot backup) ----------

if [[ ! -f "$STUB_BACKUP" ]]; then
    say "backing up E6a stub → ${STUB_BACKUP##*/}"
    cp "$DST_WRITER" "$STUB_BACKUP"
fi
say "copying real ChainWriter into noc-product/services/chain_write/"
cp "$SRC_WRITER" "$DST_WRITER"

# ---------- 2. Sync KEK + mode flag into noc-product/.env ----------

MVGHB_KEK_VALUE="$(grep '^MVGHB_KEK=' "$MVGHB_ENV" | head -1 | cut -d= -f2-)"
[[ -n "$MVGHB_KEK_VALUE" ]] || die "MVGHB_KEK not found in ${MVGHB_ENV}"

SYSTEM_VERSION_VALUE="$(grep '^MVGHB_SYSTEM_VERSION=' "$MVGHB_ENV" | head -1 | cut -d= -f2-)"
SYSTEM_VERSION_VALUE="${SYSTEM_VERSION_VALUE:-mvghb-w1-0.1.0}"

_set_env_kv() {
    local key="$1" value="$2" file="$3"
    if grep -q "^${key}=" "$file"; then
        # macOS/BSD sed needs an empty -i suffix arg
        sed -i '' -E "s|^${key}=.*|${key}=${value}|" "$file"
    else
        printf '\n# MVGH-β activation\n%s=%s\n' "$key" "$value" >> "$file"
    fi
}

say "writing MVGHB_KEK + CHAIN_WRITE_MODE=real into ${NOC_ENV##*/}"
_set_env_kv MVGHB_KEK            "$MVGHB_KEK_VALUE"        "$NOC_ENV"
_set_env_kv CHAIN_WRITE_MODE     "real"                    "$NOC_ENV"
_set_env_kv MVGHB_SYSTEM_VERSION "$SYSTEM_VERSION_VALUE"   "$NOC_ENV"

# Bump noc-product's SYSTEM_VERSION so the envelope records the E6b flip
_set_env_kv SYSTEM_VERSION "$SYSTEM_VERSION_VALUE" "$NOC_ENV"

# ---------- 3. Restart the chain-write container ----------

say "restarting chain-write container"
(cd "$NOC_ROOT" && docker compose up -d --force-recreate --no-deps chain-write >/dev/null)

say "waiting for chain-write /healthz"
for i in {1..30}; do
    if curl -sf http://localhost:7001/healthz >/dev/null 2>&1; then
        break
    fi
    sleep 1
    if [[ $i -eq 30 ]]; then
        docker logs --tail 50 chain-write >&2 || true
        die "chain-write did not become healthy in 30s"
    fi
done
say "chain-write healthy"

# ---------- 4. Smoke test ----------

say "emitting smoke governance_chain entry via POST /emit"
RESP="$(curl -sf -X POST http://localhost:7001/emit \
    -H 'content-type: application/json' \
    -d '{
        "entry_type": "intake",
        "actor_id": "producing_agent",
        "actor_role": "producing_ai",
        "incident_id": null,
        "payload_ref": {"kind": "e6b_activation_smoke", "note": "first real HMAC emit"}
    }')"
echo "$RESP" | python3 -m json.tool

python3 - <<PY
import json, sys, uuid
r = json.loads('''${RESP}''')
assert r.get("committed") is True, f"committed != true: {r}"
cid = uuid.UUID(r["chain_id"])
assert cid.version == 4, f"chain_id not UUIDv4 (version={cid.version}) — still stub path"
sig = r["hmac_signature_hex"]
assert len(sig) == 64, f"hmac length {len(sig)} != 64 hex chars"
# Verify it is NOT the stub UUIDv5 fingerprint
assert str(cid) != str(uuid.uuid5(uuid.UUID("${STUB_NAMESPACE_UUID}"), json.dumps(r, sort_keys=True))), \
    "chain_id collides with UUIDv5 stub — check writer swap"
print(f"[activate_e6b] OK: chain_id={cid} sig={sig[:16]}…")
PY

# ---------- 5. Read back from noc-gov ----------

say "querying noc-gov for the new entry"
docker exec noc-gov psql -U noc -d noc_gov -t -A -F '|' -c "
    SELECT chain_id, actor_id, entry_type, system_version,
           encode(hmac_signature, 'hex'), prev_chain_id,
           timestamp
      FROM governance_chain
     WHERE system_version = '${SYSTEM_VERSION_VALUE}'
     ORDER BY timestamp DESC
     LIMIT 5;
"

say "DONE — E6b active. CHAIN_WRITE_MODE=real, KEK=${MVGHB_KEK_VALUE:0:8}…"
