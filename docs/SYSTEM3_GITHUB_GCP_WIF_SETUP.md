# Genesis_System3 — GitHub to Google Cloud keyless setup

## Purpose

This one-time setup replaces the long-lived `GCP_SA_KEY` GitHub secret with
short-lived GitHub OIDC credentials through Google Cloud Workload Identity
Federation. The provider is restricted to:

- GitHub repository ID `1168640800` (`psw2025-cmd/Genesis_System3`)
- GitHub owner ID `176781239` (`psw2025-cmd`)
- branch `refs/heads/main`

No trading flag is enabled by this procedure.

## What is implemented in the repository

The retained `cloud-run-auto-deploy.yml` supports both modes during migration:

1. Workload Identity Federation when the three required GitHub variables exist.
2. Legacy `GCP_SA_KEY` only as a temporary fallback.

After deployment it creates a sanitized read-only artifact:

- `reports/latest/gcp_runtime_lock/gcp_runtime_lock.json`
- `reports/latest/gcp_runtime_lock/gcp_runtime_lock.md`

The artifact contains revision, deployed SHA, safe environment values, IAM
public-access state, scheduler metadata, secret metadata, sanitized log/metric
summaries, endpoint hashes and lock blockers. It never writes secret payloads.

## One manual Google Cloud step

Open Google Cloud Console, select project `system3-openalgo-safe`, then open
**Cloud Shell**. From a checkout of this repository run:

```bash
chmod +x deploy/gcp/bootstrap_github_wif.sh
./deploy/gcp/bootstrap_github_wif.sh
```

The command must be run by an account allowed to create workload identity
pools, service accounts and IAM bindings.

## Add the printed GitHub variables

Open:

`GitHub -> psw2025-cmd/Genesis_System3 -> Settings -> Secrets and variables -> Actions -> Variables`

Create exactly the three values printed by the script:

- `GCP_WIF_PROVIDER`
- `GCP_DEPLOY_SERVICE_ACCOUNT`
- `GCP_EVIDENCE_SERVICE_ACCOUNT`

These are identifiers, not secrets.

## Prove the migration before deleting the old key

Run **Cloud Run Auto Deploy** from `main`. Confirm:

1. The WIF authentication step ran.
2. The legacy-key authentication step was skipped.
3. Deployment completed.
4. Artifact `system3-gcp-runtime-evidence-<run number>` was uploaded.
5. `source_matches_deployment=true`.
6. Analyzer/live-off safety passed.
7. `secret_values_exposed=false`.

Only after those checks pass:

1. Delete GitHub Actions secret `GCP_SA_KEY`.
2. Locate the old Google service account associated with that key.
3. Disable the user-managed key.
4. Re-run deployment.
5. Delete the disabled key after the second WIF-only run passes.

## Intentionally unchanged

During the present analyzer/paper phase:

```text
REQUIRE_API_KEY=false
ANALYZE_MODE=1
LIVE_TRADING_ENABLED=0
SYSTEM3_LIVE_TRADING_ALLOWED=0
AUTO_EXECUTE_TRADES=0
```

The API-key-disabled state is temporary and must be reviewed before funds or
live order permissions are introduced.

## Remaining identity hardening

The current deployment workflow still uses the Cloud Run runtime identity for
Dhan token rotation. After WIF evidence is proven, the next controlled change
is to separate:

- web runtime identity;
- Dhan token-rotation identity;
- scheduler invoker identity.

Do not perform that split without first capturing the current runtime and
secret-IAM evidence artifact.
