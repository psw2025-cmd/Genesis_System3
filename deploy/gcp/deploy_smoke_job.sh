#!/usr/bin/env bash
set -euo pipefail

if [[ "${ALLOW_GCP_DEPLOY:-NO}" != "YES" ]]; then
  echo "Refusing deployment: set ALLOW_GCP_DEPLOY=YES after explicit approval." >&2
  exit 2
fi
IMAGE="${1:?Usage: deploy_smoke_job.sh <immutable-image-reference>}"
PROJECT="${GOOGLE_CLOUD_PROJECT:-system3-openalgo-safe}"
REGION="${GCP_REGION:-asia-south1}"
EXPECTED_PREFIX="${REGION}-docker.pkg.dev/${PROJECT}/system3-containers/genesis-system3:"
[[ "${IMAGE}" == "${EXPECTED_PREFIX}"* ]] || { echo "Image must use ${EXPECTED_PREFIX}<commit-sha>" >&2; exit 2; }

gcloud run jobs deploy genesis-system3-smoke \
  --project="${PROJECT}" \
  --region="${REGION}" \
  --image="${IMAGE}" \
  --service-account="system3-worker@${PROJECT}.iam.gserviceaccount.com" \
  --command=python \
  --args=scripts/gcp_worker_job.py \
  --tasks=1 \
  --parallelism=1 \
  --max-retries=0 \
  --task-timeout=10m \
  --set-env-vars="SYSTEM3_DEPLOY_TARGET=gcp-cloud-run-job,SYSTEM3_WORKER_MODE=job,SYSTEM3_JOB_KIND=smoke,SYSTEM3_JOB_PUBLISH_STATE=1,SYSTEM3_ENABLE_PAPER_JOB=0,SYSTEM3_STATE_BACKEND=firestore,SYSTEM3_STATE_BACKEND_REQUIRED=1,SYSTEM3_FIRESTORE_PROJECT=${PROJECT},SYSTEM3_REAL_ONLY=1,SYSTEM3_MODE=analyzer,ANALYZE_MODE=1,LIVE_TRADING_ENABLED=0,SYSTEM3_LIVE_TRADING_ALLOWED=0"
