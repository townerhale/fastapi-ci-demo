#!/usr/bin/env bash
# scripts/wait_for_db.sh
# Poll for a Postgres host:port to become available using nc (netcat).
# Designed for CI and docker-compose. Exits 0 when reachable, non-zero on timeout.

set -euo pipefail

# --- Config (env-overridable) -------------------------------------------------
: "${DB_HOST:=}"            # e.g. "db" in docker-compose, or "localhost"
: "${DB_PORT:=}"            # e.g. "5432"
: "${DATABASE_URL:=}"       # e.g. "postgresql+psycopg2://user:pass@db:5432/appdb"
: "${WAIT_RETRIES:=120}"    # total attempts
: "${WAIT_DELAY:=1}"        # seconds between attempts
: "${NC_TIMEOUT:=2}"        # per-attempt nc timeout (seconds)

# --- Derive DB_HOST/DB_PORT from DATABASE_URL if not provided -----------------
if [[ -z "${DB_HOST}" || -z "${DB_PORT}" ]]; then
  if [[ -n "${DATABASE_URL}" ]]; then
    # Strip scheme/creds up to '@', then take host:port up to the next '/'
    hostport="${DATABASE_URL#*@}"
    hostport="${hostport%%/*}"
    if [[ "$hostport" == *:* ]]; then
      DB_HOST="${DB_HOST:-${hostport%:*}}"
      DB_PORT="${DB_PORT:-${hostport##*:}}"
    else
      DB_HOST="${DB_HOST:-$hostport}"
      DB_PORT="${DB_PORT:-5432}"
    fi
  fi
fi

# --- Fallback defaults (compose-friendly) -------------------------------------
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"

# --- Validation ----------------------------------------------------------------
if ! [[ "$DB_PORT" =~ ^[0-9]+$ ]]; then
  echo "wait_for_db: DB_PORT must be a number, got: '$DB_PORT'" >&2
  exit 2
fi

echo "==> Waiting for Postgres at ${DB_HOST}:${DB_PORT}"
echo "    Retries: ${WAIT_RETRIES}, Delay: ${WAIT_DELAY}s, nc timeout: ${NC_TIMEOUT}s"

attempt=0
until nc -z -w "${NC_TIMEOUT}" "${DB_HOST}" "${DB_PORT}" >/dev/null 2>&1; do
  attempt=$(( attempt + 1 ))
  if (( attempt >= WAIT_RETRIES )); then
    echo "❌ wait_for_db: timed out after ${attempt} attempts checking ${DB_HOST}:${DB_PORT}" >&2
    exit 1
  fi
  if (( attempt % 5 == 0 )); then
    echo "   still waiting... (attempt ${attempt}/${WAIT_RETRIES})"
  fi
  sleep "${WAIT_DELAY}"
done

echo "✅ Postgres is reachable at ${DB_HOST}:${DB_PORT}"
