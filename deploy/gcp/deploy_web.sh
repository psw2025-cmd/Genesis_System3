#!/usr/bin/env bash
set -euo pipefail

if [[ "${ALLOW_GCP_DEPLOY:-NO}" != "YES" ]]; then
  echo "Refusing deployment: set ALLOW_GCP_DEPLOY=YES after explicit approval." >&2
  exit 2
fi
IMAGE="${1:?Usage: deploy_web.sh <immutable-image-reference>}"
PROJECT="${GOOGLE_CLOUD_PROJECT:-system3-openalgo-safe}"
REGION="${GCP_REGION:-asia-south1}"
EXPECTED_PREFIX="${REGION}-docker.pkg.dev/${PROJECT}/system3-containers/genesis-system3:"
[[ "${IMAGE}" == "${EXPECTED_PREFIX}"* ]] || { echo "Image must use ${EXPECTED_PREFIX}<commit-sha>" >&2; exit 2; }

# Secret Manager secret IDs for the dashboard's API key and worker-push
# token. Configurable via env vars; secure named defaults otherwise.
API_KEY_SECRET_ID="${API_KEY_SECRET_ID:-system3-dashboard-api-key}"
WORKER_PUSH_TOKEN_SECRET_ID="${WORKER_PUSH_TOKEN_SECRET_ID:-system3-dashboard-worker-push-token}"

for SECRET in "${API_KEY_SECRET_ID}" "${WORKER_PUSH_TOKEN_SECRET_ID}"; do
  gcloud secrets describe "${SECRET}" --project="${PROJECT}" >/dev/null 2>&1 \
    || { echo "Refusing deployment: required secret '${SECRET}' does not exist in Secret Manager. See docs/security/SECURE_DEPLOYMENT_PREREQUISITES.md." >&2; exit 2; }
done

# Cloud Run ingress stays public (--allow-unauthenticated) so the browser can
# reach the login/session flow and static UI; application-level auth in
# dashboard/backend/app.py (REQUIRE_API_KEY + session cookie) protects every
# other API route and fails closed if API_KEY is unset.
gcloud run deploy genesis-system3-web \
  --project="${PROJECT}" \
  --region="${REGION}" \
  --platform=managed \
  --image="${IMAGE}" \
  --service-account="system3-web@${PROJECT}.iam.gserviceaccount.com" \
  --port=8080 \
  --cpu=1 \
  --memory=512Mi \
  --min=0 \
  --max=1 \
  --concurrency=50 \
  --timeout=300 \
  --allow-unauthenticated \
  --set-secrets="API_KEY=${API_KEY_SECRET_ID}:latest,WORKER_PUSH_TOKEN=${WORKER_PUSH_TOKEN_SECRET_ID}:latest" \
  --set-env-vars="SYSTEM3_DEPLOY_TARGET=gcp-cloud-run,SYSTEM3_STATE_BACKEND=firestore,SYSTEM3_STATE_BACKEND_REQUIRED=1,SYSTEM3_FIRESTORE_PROJECT=${PROJECT},SYSTEM3_STATE_REFRESH_S=5,SYSTEM3_SYNC_INTERVAL_S=60,SYSTEM3_REAL_ONLY=1,SYSTEM3_MODE=analyzer,ANALYZE_MODE=1,LIVE_TRADING_ENABLED=0,SYSTEM3_LIVE_TRADING_ALLOWED=0,AUTO_EXECUTE_TRADES=0,CLOUD_PAPER_ENGINE=0,DEFER_INSTRUMENT_WARMUP=1,REQUIRE_API_KEY=true,MEM_WARN_MB=380,MEM_GC_MB=420,MEM_LIMIT_MB=480"
