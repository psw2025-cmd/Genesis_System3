#!/usr/bin/env bash
set -euo pipefail

# One-time bootstrap for keyless GitHub Actions -> Google Cloud authentication.
# Run manually in Google Cloud Shell while signed in as a project administrator.
# This script does not read or print secret payloads and does not enable trading.

PROJECT_ID="${PROJECT_ID:-system3-openalgo-safe}"
REGION="${REGION:-asia-south1}"
POOL_ID="${POOL_ID:-github-actions}"
PROVIDER_ID="${PROVIDER_ID:-genesis-system3-main}"
GITHUB_REPOSITORY="${GITHUB_REPOSITORY:-psw2025-cmd/Genesis_System3}"
GITHUB_REPOSITORY_ID="${GITHUB_REPOSITORY_ID:-1168640800}"
GITHUB_OWNER_ID="${GITHUB_OWNER_ID:-176781239}"
DEPLOY_SA_NAME="${DEPLOY_SA_NAME:-system3-github-deployer}"
EVIDENCE_SA_NAME="${EVIDENCE_SA_NAME:-system3-evidence-reader}"
WEB_RUNTIME_SA_NAME="${WEB_RUNTIME_SA_NAME:-genesis-system3-web}"
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

say "Create or verify Workload Identity Pool"
if ! gcloud iam workload-identity-pools describe "$POOL_ID" \
    --project="$PROJECT_ID" --location=global >/dev/null 2>&1; then
  gcloud iam workload-identity-pools create "$POOL_ID" \
    --project="$PROJECT_ID" --location=global \
    --display-name="GitHub Actions"
fi

say "Create or verify repository-and-main-only OIDC provider"
ATTRIBUTE_MAPPING="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_id=assertion.repository_id,attribute.repository_owner=assertion.repository_owner,attribute.repository_owner_id=assertion.repository_owner_id,attribute.ref=assertion.ref"
ATTRIBUTE_CONDITION="assertion.repository_id=='${GITHUB_REPOSITORY_ID}' && assertion.repository_owner_id=='${GITHUB_OWNER_ID}' && assertion.ref=='refs/heads/main'"
if ! gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
    --project="$PROJECT_ID" --location=global \
    --workload-identity-pool="$POOL_ID" >/dev/null 2>&1; then
  gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_ID" \
    --project="$PROJECT_ID" --location=global \
    --workload-identity-pool="$POOL_ID" \
    --display-name="Genesis_System3 main" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="$ATTRIBUTE_MAPPING" \
    --attribute-condition="$ATTRIBUTE_CONDITION"
else
  gcloud iam workload-identity-pools providers update-oidc "$PROVIDER_ID" \
    --project="$PROJECT_ID" --location=global \
    --workload-identity-pool="$POOL_ID" \
    --attribute-mapping="$ATTRIBUTE_MAPPING" \
    --attribute-condition="$ATTRIBUTE_CONDITION"
fi

say "Create deployment, evidence and web runtime service accounts"
if ! exists_sa "$DEPLOY_SA"; then
  gcloud iam service-accounts create "$DEPLOY_SA_NAME" \
    --project="$PROJECT_ID" --display-name="System3 GitHub deployer"
fi
if ! exists_sa "$EVIDENCE_SA"; then
  gcloud iam service-accounts create "$EVIDENCE_SA_NAME" \
    --project="$PROJECT_ID" --display-name="System3 read-only evidence reader"
fi
if ! exists_sa "$WEB_RUNTIME_SA"; then
  gcloud iam service-accounts create "$WEB_RUNTIME_SA_NAME" \
    --project="$PROJECT_ID" --display-name="Genesis System3 web runtime"
fi

PRINCIPAL_SET="principalSet://iam.googleapis.com/${POOL_NAME}/attribute.repository_id/${GITHUB_REPOSITORY_ID}"
for SA in "$DEPLOY_SA" "$EVIDENCE_SA"; do
  gcloud iam service-accounts add-iam-policy-binding "$SA" \
    --project="$PROJECT_ID" \
    --member="$PRINCIPAL_SET" \
    --role="roles/iam.workloadIdentityUser" >/dev/null
done

say "Grant deployment identity only the roles required by the current deployment path"
for ROLE in \
  roles/run.admin \
  roles/cloudbuild.builds.editor \
  roles/artifactregistry.reader \
  roles/cloudscheduler.admin \
  roles/serviceusage.serviceUsageConsumer \
  roles/browser; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${DEPLOY_SA}" --role="$ROLE" \
    --condition=None >/dev/null
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

gcloud iam service-accounts add-iam-policy-binding "$WEB_RUNTIME_SA" \
  --project="$PROJECT_ID" --member="serviceAccount:${DEPLOY_SA}" \
  --role="roles/iam.serviceAccountUser" >/dev/null

say "Grant the dedicated web runtime only the shared-state and secret access it needs"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${WEB_RUNTIME_SA}" \
  --role="roles/datastore.user" \
  --condition=None >/dev/null

for SECRET in system3-dhan-client-id dhan-access-token system3-dashboard-worker-push-token; do
  if gcloud secrets describe "$SECRET" --project="$PROJECT_ID" >/dev/null 2>&1; then
    gcloud secrets add-iam-policy-binding "$SECRET" \
      --project="$PROJECT_ID" --member="serviceAccount:${WEB_RUNTIME_SA}" \
      --role="roles/secretmanager.secretAccessor" >/dev/null
  else
    echo "WARNING: runtime secret metadata not found: ${SECRET}" >&2
  fi
done

# Deployment identity may administer broker rotation secrets, but they are never
# mounted into the public web runtime merely because deployment needs them.
for SECRET in system3-dhan-client-id dhan-access-token dhan-pin dhan-totp-secret; do
  if gcloud secrets describe "$SECRET" --project="$PROJECT_ID" >/dev/null 2>&1; then
    gcloud secrets add-iam-policy-binding "$SECRET" \
      --project="$PROJECT_ID" --member="serviceAccount:${DEPLOY_SA}" \
      --role="roles/secretmanager.admin" >/dev/null
  else
    echo "WARNING: secret metadata not found: ${SECRET}" >&2
  fi
done

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
    --member="serviceAccount:${EVIDENCE_SA}" --role="$ROLE" \
    --condition=None >/dev/null
done

say "Verify no service-account key was created"
DEPLOY_KEYS="$(gcloud iam service-accounts keys list --iam-account="$DEPLOY_SA" --project="$PROJECT_ID" --managed-by=user --format='value(name)')"
EVIDENCE_KEYS="$(gcloud iam service-accounts keys list --iam-account="$EVIDENCE_SA" --project="$PROJECT_ID" --managed-by=user --format='value(name)')"
RUNTIME_KEYS="$(gcloud iam service-accounts keys list --iam-account="$WEB_RUNTIME_SA" --project="$PROJECT_ID" --managed-by=user --format='value(name)')"
if [[ -n "$DEPLOY_KEYS" || -n "$EVIDENCE_KEYS" || -n "$RUNTIME_KEYS" ]]; then
  echo "ERROR: user-managed key unexpectedly exists on a keyless System3 service account." >&2
  exit 3
fi

cat <<EOF

BOOTSTRAP COMPLETE

Repository variables:
GCP_WIF_PROVIDER=${PROVIDER_NAME}
GCP_DEPLOY_SERVICE_ACCOUNT=${DEPLOY_SA}
GCP_EVIDENCE_SERVICE_ACCOUNT=${EVIDENCE_SA}
GCP_WEB_RUNTIME_SERVICE_ACCOUNT=${WEB_RUNTIME_SA}

Runtime shared-state prerequisite:
${WEB_RUNTIME_SA} -> roles/datastore.user

Safety was not changed:
- ANALYZE_MODE remains 1.
- LIVE_TRADING_ENABLED remains 0.
- SYSTEM3_LIVE_TRADING_ALLOWED remains 0.
- AUTO_EXECUTE_TRADES remains 0.
- PAPER dashboard viewing remains public/read-only with no dashboard API key.
EOF
