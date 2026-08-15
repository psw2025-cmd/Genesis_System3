#!/usr/bin/env bash
set -euo pipefail

# One-time owner/admin bootstrap for autonomous, keyless System3 operations.
# Safe boundaries: no secret payload read, no Dhan rotation execution, no LIVE/order enablement.

PROJECT_ID="${PROJECT_ID:-system3-openalgo-safe}"
POOL_ID="${POOL_ID:-github-genesis-system3}"
PROVIDER_ID="${PROVIDER_ID:-github}"
GITHUB_REPOSITORY_ID="${GITHUB_REPOSITORY_ID:-1168640800}"
GITHUB_OWNER_ID="${GITHUB_OWNER_ID:-176781239}"
REPAIR_WORKFLOW_REF="${REPAIR_WORKFLOW_REF:-psw2025-cmd/Genesis_System3/.github/workflows/gcp-authority-repair.yml@refs/heads/main}"
DEPLOY_SA="genesis-system3-automation@${PROJECT_ID}.iam.gserviceaccount.com"
REPAIR_SA="gs3-iam-repair@${PROJECT_ID}.iam.gserviceaccount.com"
REPAIR_FALLBACK_SA="gs3-iam-repair-b@${PROJECT_ID}.iam.gserviceaccount.com"
REPAIR_ROLE_ID="GenesisSystem3IamRepair"

say() { printf '\n== %s ==\n' "$*"; }
exists_sa() { gcloud iam service-accounts describe "$1" --project="$PROJECT_ID" >/dev/null 2>&1; }

gcloud config set project "$PROJECT_ID" >/dev/null
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
POOL_NAME="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}"

say "Verify existing keyless GitHub WIF provider"
gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
  --project="$PROJECT_ID" --location=global --workload-identity-pool="$POOL_ID" >/dev/null

say "Restrict repair federation to repo numeric IDs, main, and exact repair workflow claim"
ATTRIBUTE_MAPPING="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_id=assertion.repository_id,attribute.repository_owner=assertion.repository_owner,attribute.repository_owner_id=assertion.repository_owner_id,attribute.ref=assertion.ref,attribute.workflow_ref=assertion.workflow_ref,attribute.authority=assertion.workflow_ref=='${REPAIR_WORKFLOW_REF}' ? 'repair' : 'standard'"
ATTRIBUTE_CONDITION="assertion.repository_id=='${GITHUB_REPOSITORY_ID}' && assertion.repository_owner_id=='${GITHUB_OWNER_ID}' && assertion.ref=='refs/heads/main'"
gcloud iam workload-identity-pools providers update-oidc "$PROVIDER_ID" \
  --project="$PROJECT_ID" --location=global --workload-identity-pool="$POOL_ID" \
  --attribute-mapping="$ATTRIBUTE_MAPPING" --attribute-condition="$ATTRIBUTE_CONDITION" >/dev/null

say "Create primary and fallback keyless IAM-repair identities"
for SPEC in \
  "gs3-iam-repair|Genesis System3 IAM repair primary" \
  "gs3-iam-repair-b|Genesis System3 IAM repair fallback"; do
  NAME="${SPEC%%|*}"; DISPLAY="${SPEC#*|}"; EMAIL="${NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
  if ! exists_sa "$EMAIL"; then
    gcloud iam service-accounts create "$NAME" --project="$PROJECT_ID" --display-name="$DISPLAY" >/dev/null
  fi
done

REPAIR_PRINCIPAL_SET="principalSet://iam.googleapis.com/${POOL_NAME}/attribute.authority/repair"
for SA in "$REPAIR_SA" "$REPAIR_FALLBACK_SA"; do
  gcloud iam service-accounts add-iam-policy-binding "$SA" \
    --project="$PROJECT_ID" --member="$REPAIR_PRINCIPAL_SET" \
    --role="roles/iam.workloadIdentityUser" >/dev/null
done

say "Create/update bounded resource-IAM repair custom role"
REPAIR_PERMISSIONS="iam.serviceAccounts.get,iam.serviceAccounts.getIamPolicy,iam.serviceAccounts.setIamPolicy,secretmanager.secrets.get,secretmanager.secrets.getIamPolicy,secretmanager.secrets.setIamPolicy,run.jobs.get,run.jobs.getIamPolicy,run.jobs.setIamPolicy,run.services.get,run.services.getIamPolicy,run.services.setIamPolicy,resourcemanager.projects.get"
if gcloud iam roles describe "$REPAIR_ROLE_ID" --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud iam roles update "$REPAIR_ROLE_ID" \
    --project="$PROJECT_ID" --title="Genesis System3 IAM Repair" \
    --description="Bounded resource IAM repair; no secret payload or Cloud Run job execution" \
    --permissions="$REPAIR_PERMISSIONS" --stage=GA --quiet >/dev/null
else
  gcloud iam roles create "$REPAIR_ROLE_ID" \
    --project="$PROJECT_ID" --title="Genesis System3 IAM Repair" \
    --description="Bounded resource IAM repair; no secret payload or Cloud Run job execution" \
    --permissions="$REPAIR_PERMISSIONS" --stage=GA --quiet >/dev/null
fi

say "Grant repair identities project-policy recovery plus bounded resource-IAM authority"
for SA in "$REPAIR_SA" "$REPAIR_FALLBACK_SA"; do
  for ROLE in \
    roles/resourcemanager.projectIamAdmin \
    roles/iam.roleAdmin \
    "projects/${PROJECT_ID}/roles/${REPAIR_ROLE_ID}"; do
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
      --member="serviceAccount:${SA}" --role="$ROLE" --condition=None >/dev/null
  done
done

say "Restore normal deployment authority required by the current production workflow"
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

say "Prove repair identities remain keyless"
for SA in "$REPAIR_SA" "$REPAIR_FALLBACK_SA"; do
  KEYS="$(gcloud iam service-accounts keys list --iam-account="$SA" --project="$PROJECT_ID" --managed-by=user --format='value(name)')"
  if [[ -n "$KEYS" ]]; then
    echo "ERROR: user-managed key exists on ${SA}; refusing autonomous bootstrap." >&2
    exit 3
  fi
done

say "Remove known-forbidden broker Secret Manager payload roles from deploy/repair identities"
for SECRET in system3-dhan-client-id dhan-access-token dhan-pin dhan-totp-secret system3-dashboard-worker-push-token; do
  for SA in "$REPAIR_SA" "$REPAIR_FALLBACK_SA" "$DEPLOY_SA"; do
    for ROLE in roles/secretmanager.secretAccessor roles/secretmanager.secretVersionAdder; do
      gcloud secrets remove-iam-policy-binding "$SECRET" \
        --project="$PROJECT_ID" --member="serviceAccount:${SA}" --role="$ROLE" \
        --quiet >/dev/null 2>&1 || true
    done
  done
done

say "Verify deploy/repair identities have no broker Secret Manager payload roles"
for SECRET in system3-dhan-client-id dhan-access-token dhan-pin dhan-totp-secret system3-dashboard-worker-push-token; do
  POLICY="$(gcloud secrets get-iam-policy "$SECRET" --project="$PROJECT_ID" --format=json)"
  for SA in "$REPAIR_SA" "$REPAIR_FALLBACK_SA" "$DEPLOY_SA"; do
    if printf '%s' "$POLICY" | python3 -c 'import json,sys; p=json.load(sys.stdin); sa=sys.argv[1]; bad={"roles/secretmanager.secretAccessor","roles/secretmanager.secretVersionAdder"}; raise SystemExit(0 if any(b.get("role") in bad and ("serviceAccount:"+sa) in (b.get("members") or []) for b in p.get("bindings",[])) else 1)' "$SA"; then
      echo "ERROR: forbidden broker secret payload role remains on ${SA} for ${SECRET}." >&2
      exit 4
    fi
  done
done

cat <<EOF

AUTONOMOUS AUTHORITY BOOTSTRAP COMPLETE
PROJECT=${PROJECT_ID}
DEPLOY_SA=${DEPLOY_SA}
REPAIR_PRIMARY=${REPAIR_SA}
REPAIR_FALLBACK=${REPAIR_FALLBACK_SA}
REPAIR_WORKFLOW_REF=${REPAIR_WORKFLOW_REF}
KEYLESS_WIF=true
SECRET_PAYLOAD_ACCESS_FOR_DEPLOY_REPAIR=false
DHAN_ROTATION_EXECUTED=false
LIVE_TRADING_CHANGED=false
ORDER_ACTION_PERFORMED=false
STRICT_SCHEDULER_ONLY_IAM=false
DEPLOYER_RUN_ADMIN_TEMPORARY=true
EOF
