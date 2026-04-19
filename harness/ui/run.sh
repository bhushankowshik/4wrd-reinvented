#!/usr/bin/env bash
# 4WRD Harness UI launcher.
#
# Sources ../mvghb/.env and ./.env (if present) so DB + Anthropic creds
# reach the FastAPI process and every pty subprocess it spawns.
# Then starts uvicorn on localhost:8080 from the harness/ui directory.

set -euo pipefail

UI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_DIR="$(cd "${UI_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${HARNESS_DIR}/.." && pwd)"

load_env() {
  local f="$1"
  if [[ -f "$f" ]]; then
    echo ">> loading env from $f"
    set -a
    # shellcheck disable=SC1090
    source "$f"
    set +a
  fi
}

load_env "${REPO_ROOT}/mvghb/.env"
load_env "${HARNESS_DIR}/.env"
load_env "${UI_DIR}/.env"

PORT="${PORT:-8080}"
HOST="${HOST:-127.0.0.1}"

echo ""
echo "  4WRD Harness UI"
echo "  ───────────────"
echo "  http://${HOST}:${PORT}"
echo ""

cd "${HARNESS_DIR}"
exec uv run --with fastapi --with 'uvicorn[standard]' --with websockets \
  uvicorn ui.server:app --host "${HOST}" --port "${PORT}" --reload
