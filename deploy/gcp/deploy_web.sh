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
  --no-allow-unauthenticated \
  --set-env-vars="SYSTEM3_DEPLOY_TARGET=gcp-cloud-run,SYSTEM3_STATE_BACKEND=firestore,SYSTEM3_STATE_BACKEND_REQUIRED=1,SYSTEM3_FIRESTORE_PROJECT=${PROJECT},SYSTEM3_STATE_REFRESH_S=5,SYSTEM3_SYNC_INTERVAL_S=60,SYSTEM3_REAL_ONLY=1,SYSTEM3_MODE=analyzer,ANALYZE_MODE=1,LIVE_TRADING_ENABLED=0,SYSTEM3_LIVE_TRADING_ALLOWED=0,CLOUD_PAPER_ENGINE=0,DEFER_INSTRUMENT_WARMUP=1,REQUIRE_API_KEY=true,MEM_WARN_MB=380,MEM_GC_MB=420,MEM_LIMIT_MB=480"
