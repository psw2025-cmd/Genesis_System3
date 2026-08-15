#!/usr/bin/env bash
set -euo pipefail

# Authoritative one-time System3 GCP bootstrap entrypoint.
# Run from this repository in Google Cloud Shell as the project owner/admin.
# It preserves keyless WIF and PAPER/LIVE safety and adds redundant IAM self-repair.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${HERE}/../.." && pwd)"

bash "${HERE}/bootstrap_github_wif.sh"
bash "${HERE}/bootstrap_autonomous_authority.sh"

cd "$ROOT"
python3 -m unittest -q tests.test_gcp_authority_repair_contract
python3 scripts/gcp_authority_repair.py --apply
python3 scripts/gcp_authority_repair.py

echo "SYSTEM3_FULL_AUTHORITY_BOOTSTRAP_OK"
