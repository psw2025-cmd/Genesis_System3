#!/usr/bin/env sh
set -eu

BASE_URL="${WEB_SERVICE_URL:-https://genesis-system3-backend.onrender.com}"
TOKEN="${WORKER_PUSH_TOKEN:-}"

echo "========================================"
echo "Genesis System3 Render Worker Mobile Check"
echo "========================================"
echo "BASE_URL=$BASE_URL"

if [ -z "$TOKEN" ]; then
  echo "WORKER_PUSH_TOKEN=MISSING"
  echo "RESULT=FAIL"
  echo "Fix in Render: Environment Groups -> dhan-shared-credentials -> add WORKER_PUSH_TOKEN"
  exit 2
fi

TOKEN_LEN=$(printf '%s' "$TOKEN" | wc -c | tr -d ' ')
TOKEN_HASH=$(printf '%s' "$TOKEN" | sha256sum | awk '{print substr($1,1,12)}')

echo "WORKER_PUSH_TOKEN=PRESENT"
echo "TOKEN_LENGTH=$TOKEN_LEN"
echo "TOKEN_HASH12=$TOKEN_HASH"
echo "NOTE=Token value is not printed. Safe to screenshot/share this output."

echo ""
echo "Testing backend /api/scheduler/health ..."
HTTP_HEALTH=$(curl -sS -o /tmp/scheduler_health.json -w "%{http_code}" "$BASE_URL/api/scheduler/health" || true)
echo "SCHEDULER_HEALTH_HTTP=$HTTP_HEALTH"
cat /tmp/scheduler_health.json 2>/dev/null | head -c 1200 || true
echo ""

echo ""
echo "Testing push endpoint with X-Worker-Token ..."
HTTP_PUSH=$(curl -sS -o /tmp/scheduler_push.json -w "%{http_code}" \
  -X POST "$BASE_URL/api/scheduler/health/push" \
  -H "Content-Type: application/json" \
  -H "X-Worker-Token: $TOKEN" \
  --data '{"daemon_heartbeat":"manual-render-shell-test","daemon_pid":0,"jobs":{},"jobs_status_today":{},"fired_keys_today":[]}' || true)

echo "SCHEDULER_PUSH_HTTP=$HTTP_PUSH"
cat /tmp/scheduler_push.json 2>/dev/null | head -c 1200 || true
echo ""

if [ "$HTTP_PUSH" = "200" ]; then
  echo "RESULT=PASS"
  echo "Meaning: This service token is valid for backend push."
else
  echo "RESULT=FAIL"
  echo "Meaning: token missing/mismatch OR backend does not accept this token."
  echo "Fix: Put one same WORKER_PUSH_TOKEN in Render Environment Group dhan-shared-credentials, then redeploy backend and worker."
  exit 1
fi
