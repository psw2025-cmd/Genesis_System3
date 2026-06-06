#!/usr/bin/env bash
set -euo pipefail

URL="${SYSTEM3_BACKEND_HEALTH_URL:-http://127.0.0.1:8000}"
MAX_ATTEMPTS="${SYSTEM3_HEALTH_ATTEMPTS:-12}"
SLEEP_SECONDS="${SYSTEM3_HEALTH_SLEEP_SECONDS:-5}"

echo "Genesis System3 Oracle healthcheck"
echo "URL=$URL"

for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
  echo "Attempt $attempt/$MAX_ATTEMPTS"
  if curl -fsS --max-time 10 "$URL" >/tmp/system3_oracle_health_response.txt; then
    echo "HEALTHCHECK_PASS"
    echo "Response bytes: $(wc -c </tmp/system3_oracle_health_response.txt)"
    docker ps --filter name=genesis-backend --format 'container={{.Names}} status={{.Status}} image={{.Image}}' || true
    exit 0
  fi
  sleep "$SLEEP_SECONDS"
done

echo "HEALTHCHECK_FAIL"
echo "Docker status:"
docker ps -a --filter name=genesis-backend || true
echo "Recent logs:"
docker logs --tail 120 genesis-backend || true
exit 1
