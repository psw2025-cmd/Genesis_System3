#!/usr/bin/env bash
set -euo pipefail

# Compatibility wrapper only. There is exactly one Cloud Run web deployment
# authority: scripts/gcp_cloud_run_auto_deploy.py. Keeping an independent
# `gcloud run deploy` implementation here would allow a manual/emergency path to
# bypass candidate/no-traffic health proof and exact-revision promotion.

if [[ "${ALLOW_GCP_DEPLOY:-NO}" != "YES" ]]; then
  echo "Refusing deployment: set ALLOW_GCP_DEPLOY=YES after explicit approval." >&2
  exit 2
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT}"

export LIVE_TRADING_ENABLED=0
export SYSTEM3_LIVE_TRADING_ALLOWED=0
export AUTO_EXECUTE_TRADES=0
export REQUIRE_API_KEY=false

# Fail closed if the canonical deployer ever loses the retired dashboard-key
# scrub contract. This wrapper delegates mutation; it does not run gcloud itself.
grep -F -- '--remove-secrets=API_KEY' scripts/gcp_cloud_run_auto_deploy.py >/dev/null || {
  echo "Refusing deployment: canonical --remove-secrets=API_KEY contract missing." >&2
  exit 3
}

if [[ $# -gt 0 ]]; then
  echo "NOTE: direct immutable-image deployment is retired; canonical deployer builds the exact checked-out git SHA." >&2
fi

echo "Using canonical fail-safe Cloud Run deployer: candidate 0% -> HTTP proof -> exact revision 100%."
exec python scripts/gcp_cloud_run_auto_deploy.py
