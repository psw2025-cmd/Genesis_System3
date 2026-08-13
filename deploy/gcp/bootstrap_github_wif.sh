#!/usr/bin/env bash
set -euo pipefail

# One-time bootstrap for keyless GitHub Actions -> Google Cloud authentication.
# Run manually in Google Cloud Shell while signed in as a project administrator.
# This script does not read or print secret payloads and does not enable trading.

PROJECT_ID="${PROJECT_ID:-system3-openalgo-safe}"
REGION="${REGION:-asia-south1}"
POOL_ID="${POOL_ID:-github-genesis-system3}"
PROVIDER_ID="${PROVIDER_ID:-github}"
GITHUB_REPOSITORY="${GITHUB_REPOSITORY:-psw2025-cmd/Genesis_System3}"
GITHUB_REPOSITORY_ID="${GITHUB_REPOSITORY_ID:-1168640800}"
GITHUB_OWNER_ID="${GITHUB_OWNER_ID:-176781239}"
DEPLOY_SA_NAME="${DEPLOY_SA_NAME:-genesis-system3-automation}"
EVIDENCE_SA_NAME="${EVIDENCE_SA_NAME:-system3-evidence-reader}"
WEB_RUNTIME_SA_NAME="${WEB_RUNTIME_SA_NAME:-genesis-system3-web}"
ROTATOR_SA_NAME="${ROTATOR_SA_NAME:-genesis-system3-dhan-rotator}"
# GCP service-account IDs are capped at 30 characters; keep this short.
SCHEDULER_SA_NAME="${SCHEDULER_SA_NAME:-gs3-scheduler}"
COLLECTOR_SA_NAME="${COLLECTOR_SA_NAME:-gs3-scheduler-collector}"
RANK_SA_NAME="${RANK_SA_NAME:-gs3-rank-job}"
FORECAST_SA_NAME="${FORECAST_SA_NAME:-gs3-forecast-job}"
SIGNALS_SA_NAME="${SIGNALS_SA_NAME:-gs3-signals-job}"
CLOUDBUILD_BUCKET="${CLOUDBUILD_BUCKET:-${PROJECT_ID}_cloudbuild}"
BUILDER_SA_NAME="${BUILDER_SA_NAME:-system3-builder}"

say() { printf '\n== %s ==\n' "$*"; }
exists_sa() { gcloud iam service-accounts describe "$1" --project="$PROJECT_ID" >/dev/null 2>&1; }

say "Select project and enable identity APIs"
gcloud config set project "$PROJECT_ID" >/dev/null
gcloud services enable \
  iamcredentials.googleapis.com \
  sts.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com \
  firestore.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com >/dev/null

PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
POOL_NAME="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}"
PROVIDER_NAME="${POOL_NAME}/providers/${PROVIDER_ID}"
DEPLOY_SA="${DEPLOY_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
EVIDENCE_SA="${EVIDENCE_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
BUILDER_SA="${BUILDER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
WEB_RUNTIME_SA="${WEB_RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
ROTATOR_SA="${ROTATOR_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
SCHEDULER_SA="${SCHEDULER_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
COLLECTOR_SA="${COLLECTOR_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
RANK_SA="${RANK_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
FORECAST_SA="${FORECAST_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
SIGNALS_SA="${SIGNALS_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

say "Create or verify Workload Identity Pool"
if ! gcloud iam workload-identity-pools describe "$POOL_ID" \
    --project="$PROJECT_ID" --location=global >/dev/null 2>&1; then
  gcloud iam workload-identity-pools create "$POOL_ID" \
    --project="$PROJECT_ID" --location=global --display-name="GitHub Actions"
fi

say "Create or verify repository-and-main-only OIDC provider"
ATTRIBUTE_MAPPING="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_id=assertion.repository_id,attribute.repository_owner=assertion.repository_owner,attribute.repository_owner_id=assertion.repository_owner_id,attribute.ref=assertion.ref"
ATTRIBUTE_CONDITION="assertion.repository_id=='${GITHUB_REPOSITORY_ID}' && assertion.repository_owner_id=='${GITHUB_OWNER_ID}' && assertion.ref=='refs/heads/main'"
if ! gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
    --project="$PROJECT_ID" --location=global --workload-identity-pool="$POOL_ID" >/dev/null 2>&1; then
  gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_ID" \
    --project="$PROJECT_ID" --location=global --workload-identity-pool="$POOL_ID" \
    --display-name="Genesis_System3 main" --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="$ATTRIBUTE_MAPPING" --attribute-condition="$ATTRIBUTE_CONDITION"
else
  gcloud iam workload-identity-pools providers update-oidc "$PROVIDER_ID" \
    --project="$PROJECT_ID" --location=global --workload-identity-pool="$POOL_ID" \
    --attribute-mapping="$ATTRIBUTE_MAPPING" --attribute-condition="$ATTRIBUTE_CONDITION"
fi

say "Create deployment, evidence, web, rotator and scheduler identities"
for SPEC in \
  "$DEPLOY_SA_NAME|System3 GitHub deployer" \
  "$EVIDENCE_SA_NAME|System3 read-only evidence reader" \
  "$WEB_RUNTIME_SA_NAME|Genesis System3 web runtime" \
  "$ROTATOR_SA_NAME|Genesis System3 Dhan token rotator" \
  "$SCHEDULER_SA_NAME|Genesis System3 scheduler invoker" \
  "$COLLECTOR_SA_NAME|Genesis System3 scheduler evidence collector" \
  "$RANK_SA_NAME|Genesis System3 bounded rank job" \
  "$FORECAST_SA_NAME|Genesis System3 bounded forecast job" \
  "$SIGNALS_SA_NAME|Genesis System3 bounded signal job"; do
  NAME="${SPEC%%|*}"; DISPLAY="${SPEC#*|}"; EMAIL="${NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
  if ! exists_sa "$EMAIL"; then
    gcloud iam service-accounts create "$NAME" --project="$PROJECT_ID" --display-name="$DISPLAY"
  fi
done

PRINCIPAL_SET="principalSet://iam.googleapis.com/${POOL_NAME}/attribute.repository_id/${GITHUB_REPOSITORY_ID}"
for SA in "$DEPLOY_SA" "$EVIDENCE_SA"; do
  gcloud iam service-accounts add-iam-policy-binding "$SA" \
    --project="$PROJECT_ID" --member="$PRINCIPAL_SET" \
    --role="roles/iam.workloadIdentityUser" >/dev/null
done

say "Grant deployment identity only deployment-control roles"
for ROLE in \
  roles/run.admin \
  roles/cloudbuild.builds.editor \
  roles/artifactregistry.reader \
  roles/cloudscheduler.admin \
  roles/serviceusage.serviceUsageConsumer \
  roles/browser; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${DEPLOY_SA}" --role="$ROLE" --condition=None >/dev/null
done

if ! gcloud storage buckets describe "gs://${CLOUDBUILD_BUCKET}" >/dev/null 2>&1; then
  gcloud storage buckets create "gs://${CLOUDBUILD_BUCKET}" \
    --project="$PROJECT_ID" --location="$REGION" --uniform-bucket-level-access
fi
gcloud storage buckets add-iam-policy-binding "gs://${CLOUDBUILD_BUCKET}" \
  --member="serviceAccount:${DEPLOY_SA}" --role="roles/storage.objectAdmin" >/dev/null

if exists_sa "$BUILDER_SA"; then
  gcloud iam service-accounts add-iam-policy-binding "$BUILDER_SA" \
    --project="$PROJECT_ID" --member="serviceAccount:${DEPLOY_SA}" \
    --role="roles/iam.serviceAccountUser" >/dev/null
fi
for SA in "$WEB_RUNTIME_SA" "$ROTATOR_SA" "$SCHEDULER_SA" "$COLLECTOR_SA" "$RANK_SA" "$FORECAST_SA" "$SIGNALS_SA"; do
  gcloud iam service-accounts add-iam-policy-binding "$SA" \
    --project="$PROJECT_ID" --member="serviceAccount:${DEPLOY_SA}" \
    --role="roles/iam.serviceAccountUser" >/dev/null
done

say "Grant bounded job identities their narrow runtime roles"
for ROLE in roles/datastore.user roles/run.viewer roles/cloudscheduler.viewer; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${COLLECTOR_SA}" --role="$ROLE" --condition=None >/dev/null
done
for SA in "$RANK_SA" "$FORECAST_SA" "$SIGNALS_SA"; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${SA}" --role="roles/datastore.user" --condition=None >/dev/null
done
for SECRET in system3-dhan-client-id dhan-access-token; do
  gcloud secrets add-iam-policy-binding "$SECRET" --project="$PROJECT_ID" --member="serviceAccount:${RANK_SA}" --role="roles/secretmanager.secretAccessor" >/dev/null
done

say "Grant web runtime only shared-state and read-only runtime secrets"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${WEB_RUNTIME_SA}" --role="roles/datastore.user" \
  --condition=None >/dev/null
for SECRET in system3-dhan-client-id dhan-access-token system3-dashboard-worker-push-token; do
  gcloud secrets describe "$SECRET" --project="$PROJECT_ID" >/dev/null
  gcloud secrets add-iam-policy-binding "$SECRET" \
    --project="$PROJECT_ID" --member="serviceAccount:${WEB_RUNTIME_SA}" \
    --role="roles/secretmanager.secretAccessor" >/dev/null
done

# Deployment identity may administer runtime resources but never receives broker secret payload access.
say "Grant Dhan rotator only token-mint secrets and version-add authority"
for SECRET in system3-dhan-client-id dhan-access-token dhan-pin dhan-totp-secret; do
  gcloud secrets describe "$SECRET" --project="$PROJECT_ID" >/dev/null
  gcloud secrets add-iam-policy-binding "$SECRET" \
    --project="$PROJECT_ID" --member="serviceAccount:${ROTATOR_SA}" \
    --role="roles/secretmanager.secretAccessor" >/dev/null
done
gcloud secrets add-iam-policy-binding dhan-access-token \
  --project="$PROJECT_ID" --member="serviceAccount:${ROTATOR_SA}" \
  --role="roles/secretmanager.secretVersionAdder" >/dev/null

say "Grant read-only evidence permissions"
for ROLE in \
  roles/run.viewer \
  roles/logging.viewer \
  roles/monitoring.viewer \
  roles/secretmanager.viewer \
  roles/datastore.viewer \
  roles/cloudscheduler.viewer \
  roles/artifactregistry.reader \
  roles/serviceusage.serviceUsageConsumer \
  roles/browser; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${EVIDENCE_SA}" --role="$ROLE" --condition=None >/dev/null
done

say "Verify all System3 service identities remain keyless"
for SA in "$DEPLOY_SA" "$EVIDENCE_SA" "$WEB_RUNTIME_SA" "$ROTATOR_SA" "$SCHEDULER_SA" "$COLLECTOR_SA" "$RANK_SA" "$FORECAST_SA" "$SIGNALS_SA"; do
  KEYS="$(gcloud iam service-accounts keys list --iam-account="$SA" --project="$PROJECT_ID" --managed-by=user --format='value(name)')"
  if [[ -n "$KEYS" ]]; then
    echo "ERROR: user-managed key unexpectedly exists on ${SA}." >&2
    exit 3
  fi
done

cat <<EOF

BOOTSTRAP COMPLETE
GCP_WIF_PROVIDER=${PROVIDER_NAME}
GCP_DEPLOY_SERVICE_ACCOUNT=${DEPLOY_SA}
GCP_EVIDENCE_SERVICE_ACCOUNT=${EVIDENCE_SA}
GCP_WEB_RUNTIME_SERVICE_ACCOUNT=${WEB_RUNTIME_SA}
DHAN_ROTATOR_SERVICE_ACCOUNT=${ROTATOR_SA}
DHAN_SCHEDULER_SERVICE_ACCOUNT=${SCHEDULER_SA}

Least-privilege boundaries:
- web runtime -> Firestore + client-id/access-token/worker-token read only
- rotator -> client-id/access-token/PIN/TOTP read + access-token version add
- scheduler -> no broker secrets; invoke job only after job IAM binding
- deployer -> no broker Secret Manager role

Safety unchanged: ANALYZE_MODE=1, LIVE=0, AUTO_EXECUTE_TRADES=0, public PAPER dashboard read-only.
EOF
