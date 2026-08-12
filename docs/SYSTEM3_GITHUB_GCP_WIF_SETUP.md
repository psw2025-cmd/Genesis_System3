# Genesis_System3 — GitHub to Google Cloud keyless setup

## Purpose

GitHub deploys Genesis System3 through short-lived OIDC credentials and Google
Cloud Workload Identity Federation (WIF). The active deployment workflow has no
long-lived service-account JSON-key fallback.

The provider is restricted to repository `psw2025-cmd/Genesis_System3`. No
trading flag is enabled by this procedure.

This identity topic is separate from dashboard visibility: the browser dashboard
is permanently public/read-only and has no dashboard API-key/session authority.

## Active repository contract

The retained `.github/workflows/cloud-run-auto-deploy.yml` authenticates with:

- Workload Identity provider:
  `projects/802404398783/locations/global/workloadIdentityPools/github-genesis-system3/providers/github`
- deploy service account:
  `genesis-system3-automation@system3-openalgo-safe.iam.gserviceaccount.com`

The workflow creates sanitized runtime evidence under:

- `reports/latest/gcp_runtime_lock/gcp_runtime_lock.json`
- `reports/latest/gcp_runtime_lock/gcp_runtime_lock.md`

Runtime evidence contains serving revision, serving SHA, safe environment names,
IAM/public-access state, scheduler metadata, Secret Manager metadata, sanitized
log/metric summaries, endpoint hashes, and blockers. It never reads or persists
secret payloads.

## One-time Google Cloud bootstrap

Open Cloud Shell in project `system3-openalgo-safe` and run the current bootstrap
from a trusted checkout only when infrastructure identities must be provisioned:

```bash
chmod +x deploy/gcp/bootstrap_github_wif.sh
./deploy/gcp/bootstrap_github_wif.sh
```

The account running bootstrap must be authorized for the specific IAM resources
it creates. Ordinary application deployment must not become project-IAM
administration.

Current dedicated identities include:

- web runtime: `genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com`
- Dhan rotator: `genesis-system3-dhan-rotator@system3-openalgo-safe.iam.gserviceaccount.com`
- scheduler invoker: `gs3-scheduler@system3-openalgo-safe.iam.gserviceaccount.com`
- GitHub deployer: `genesis-system3-automation@system3-openalgo-safe.iam.gserviceaccount.com`

## Prove WIF-only deployment

A valid deployment must prove:

1. `google-github-actions/auth` authenticated through the expected WIF provider.
2. No service-account JSON-key authentication path was used.
3. The exact source SHA produced the tested immutable image/revision.
4. The exact tested revision became the single 100%-traffic serving revision.
5. Runtime evidence binds `DEPLOY_GIT_SHA` to that serving revision.
6. LIVE/off safety passed.
7. `secret_values_exposed=false`.
8. The retired dashboard credential/session surface is absent from the serving
   revision and `/api/auth/status` reports `credential_surface=REMOVED`.

If an old user-managed GCP service-account key still exists from historical
migration, treat it as independent credential debt: prove WIF-only deployment,
disable the old key, re-prove WIF, then delete the disabled key. Never add such a
key back as a workflow fallback.

## Permanent dashboard contract

The current dashboard state is **not temporary**:

```text
Dashboard visibility = PUBLIC / READ-ONLY
Dashboard credential authority = REMOVED
Dashboard session authority = REMOVED
ANALYZE_MODE = 1
LIVE_TRADING_ENABLED = 0
SYSTEM3_LIVE_TRADING_ALLOWED = 0
AUTO_EXECUTE_TRADES = 0
```

No future funds/live-order work requires restoration of a dashboard API key.
Execution safety must be implemented through independent capability, risk,
approval, state, idempotency, and broker controls rather than browser-view
credentials.

## Identity separation

The intended least-privilege model is:

- web runtime: runtime reads/state access only;
- Dhan rotator: PIN/TOTP/token-version authority required for rotation only;
- scheduler invoker: invoke the rotator job only;
- GitHub deployer: WIF deployment authority, not long-lived credential storage;
- worker ingestion: dedicated worker token, separate from dashboard visibility.

Any historical excessive Secret Manager or project-level IAM grants must be
reported and removed only after replacement identities are proven working.
