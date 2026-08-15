#!/usr/bin/env bash
set -euo pipefail

# Authoritative one-time System3 GCP bootstrap entrypoint.
# Run from this repository in Google Cloud Shell as the project owner/admin.
# It preserves keyless WIF and PAPER/LIVE safety and adds redundant IAM self-repair.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "${HERE}/bootstrap_github_wif.sh"
bash "${HERE}/bootstrap_autonomous_authority.sh"

echo "SYSTEM3_FULL_AUTHORITY_BOOTSTRAP_OK"
