#!/usr/bin/env bash
set -euo pipefail

# One-time infrastructure bootstrap for Genesis System3 read-only observability.
# This script intentionally has NO broker Secret Manager access and NO order/live authority.
PROJECT_ID="${PROJECT_ID:-system3-openalgo-safe}"
REGION="${REGION:-asia-south1}"
SERVICE_HOST="${SERVICE_HOST:-genesis-system3-web-doq2wplepa-el.a.run.app}"
BUCKET="${OBSERVABILITY_BUCKET:-system3-observability-artifacts}"
OBSERVER_SA_NAME="${OBSERVER_SA_NAME:-genesis-system3-observer}"
SCHEDULER_SA_NAME="${SCHEDULER_SA_NAME:-genesis-system3-observer-scheduler}"
JOB_NAME="${SYNTHETIC_JOB_NAME:-genesis-system3-synthetic}"
SCHEDULER_JOB="${SYNTHETIC_SCHEDULER_NAME:-genesis-system3-synthetic-5m}"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/system3-containers/genesis-system3-synthetic:${SYNTHETIC_IMAGE_TAG:-phase1}"
OBSERVER_SA="${OBSERVER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
SCHEDULER_SA="${SCHEDULER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

say() { printf '\n== %s ==\n' "$*"; }
exists_sa() { gcloud iam service-accounts describe "$1" --project="$PROJECT_ID" >/dev/null 2>&1; }

say "Select project and enable required APIs"
gcloud config set project "$PROJECT_ID" >/dev/null
gcloud services enable \
  run.googleapis.com \
  cloudscheduler.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  storage.googleapis.com \
  monitoring.googleapis.com \
  iam.googleapis.com \
  --project="$PROJECT_ID" >/dev/null

say "Create dedicated keyless observability identities"
if ! exists_sa "$OBSERVER_SA"; then
  gcloud iam service-accounts create "$OBSERVER_SA_NAME" \
    --project="$PROJECT_ID" --display-name="Genesis System3 synthetic observer"
fi
if ! exists_sa "$SCHEDULER_SA"; then
  gcloud iam service-accounts create "$SCHEDULER_SA_NAME" \
    --project="$PROJECT_ID" --display-name="Genesis System3 synthetic scheduler invoker"
fi

say "Create private uniform-access evidence bucket"
if ! gcloud storage buckets describe "gs://${BUCKET}" --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud storage buckets create "gs://${BUCKET}" \
    --project="$PROJECT_ID" \
    --location="$REGION" \
    --default-storage-class=STANDARD \
    --uniform-bucket-level-access \
    --public-access-prevention
fi
gcloud storage buckets update "gs://${BUCKET}" \
  --project="$PROJECT_ID" \
  --uniform-bucket-level-access \
  --public-access-prevention \
  --lifecycle-file=observability/gcs_lifecycle.json >/dev/null

gcloud storage buckets add-iam-policy-binding "gs://${BUCKET}" \
  --project="$PROJECT_ID" \
  --member="serviceAccount:${OBSERVER_SA}" \
  --role="roles/storage.objectCreator" >/dev/null

say "Verify observability identity has no user-managed keys"
KEYS="$(gcloud iam service-accounts keys list --iam-account="$OBSERVER_SA" --project="$PROJECT_ID" --managed-by=user --format='value(name)')"
SCHED_KEYS="$(gcloud iam service-accounts keys list --iam-account="$SCHEDULER_SA" --project="$PROJECT_ID" --managed-by=user --format='value(name)')"
if [[ -n "$KEYS" || -n "$SCHED_KEYS" ]]; then
  echo "ERROR: observability identities must remain keyless." >&2
  exit 2
fi

say "Build immutable synthetic image from current Git source"
SOURCE_SHA="$(git rev-parse HEAD)"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/system3-containers/genesis-system3-synthetic:${SOURCE_SHA:0:12}"
gcloud builds submit . \
  --project="$PROJECT_ID" \
  --config=observability/cloudbuild.synthetic.yaml \
  --substitutions="_IMAGE=${IMAGE}" \
  --quiet

say "Deploy read-only Playwright synthetic Cloud Run Job"
gcloud run jobs deploy "$JOB_NAME" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --image="$IMAGE" \
  --service-account="$OBSERVER_SA" \
  --tasks=1 \
  --parallelism=1 \
  --max-retries=0 \
  --task-timeout=3m \
  --set-env-vars="SERVICE_URL=https://${SERVICE_HOST},SYSTEM3_ENV=prod,SERVICE_NAME=genesis-system3-web,OBSERVABILITY_BUCKET=${BUCKET},OBSERVABILITY_UPLOAD_REQUIRED=1,SUCCESS_SAMPLE_RATE=0.02" \
  --quiet

# Scheduler may invoke the synthetic job, but cannot mutate Cloud Run services.
gcloud run jobs add-iam-policy-binding "$JOB_NAME" \
  --project="$PROJECT_ID" --region="$REGION" \
  --member="serviceAccount:${SCHEDULER_SA}" \
  --role="roles/run.invoker" --quiet >/dev/null

say "Schedule full browser synthetic every five minutes"
RUN_URI="https://run.googleapis.com/v2/projects/${PROJECT_ID}/locations/${REGION}/jobs/${JOB_NAME}:run"
if gcloud scheduler jobs describe "$SCHEDULER_JOB" --project="$PROJECT_ID" --location="$REGION" >/dev/null 2>&1; then
  gcloud scheduler jobs update http "$SCHEDULER_JOB" \
    --project="$PROJECT_ID" --location="$REGION" \
    --schedule="*/5 * * * *" --time-zone="UTC" \
    --uri="$RUN_URI" --http-method=POST \
    --oauth-service-account-email="$SCHEDULER_SA" \
    --oauth-token-scope="https://www.googleapis.com/auth/cloud-platform" \
    --update-headers="Content-Type=application/json" --message-body='{}' --quiet
else
  gcloud scheduler jobs create http "$SCHEDULER_JOB" \
    --project="$PROJECT_ID" --location="$REGION" \
    --schedule="*/5 * * * *" --time-zone="UTC" \
    --uri="$RUN_URI" --http-method=POST \
    --oauth-service-account-email="$SCHEDULER_SA" \
    --oauth-token-scope="https://www.googleapis.com/auth/cloud-platform" \
    --headers="Content-Type=application/json" --message-body='{}' --quiet
fi

say "Create one-minute public uptime checks if absent"
create_uptime_if_missing() {
  local name="$1" path="$2"
  local existing
  existing="$(gcloud monitoring uptime list-configs --project="$PROJECT_ID" --filter="displayName='${name}'" --format='value(name)' | head -n1 || true)"
  if [[ -z "$existing" ]]; then
    gcloud monitoring uptime create "$name" \
      --project="$PROJECT_ID" \
      --resource-type=uptime-url \
      --resource-labels="host=${SERVICE_HOST},project_id=${PROJECT_ID}" \
      --protocol=https --request-method=get --path="$path" \
      --period=1 --timeout=10 --status-classes=2xx --validate-ssl=true
  fi
}
create_uptime_if_missing "Genesis System3 API Health" "/api/health"
create_uptime_if_missing "Genesis System3 Dashboard UI" "/ui"

say "Run one synthetic execution and wait for proof"
gcloud run jobs execute "$JOB_NAME" --project="$PROJECT_ID" --region="$REGION" --wait

cat <<EOF
OBSERVABILITY_BOOTSTRAP_COMPLETE
project=${PROJECT_ID}
job=${JOB_NAME}
schedule=*/5 * * * *
bucket=gs://${BUCKET}
observer_sa=${OBSERVER_SA}
scheduler_sa=${SCHEDULER_SA}
source_sha=${SOURCE_SHA}
image=${IMAGE}
dashboard_api_key_used=false
broker_order_called=false
live_trading_enabled=false
EOF
