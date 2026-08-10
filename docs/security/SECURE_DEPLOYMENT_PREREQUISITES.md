# Secure Cloud Run Deployment Prerequisites

This document lists the one-time, human-performed setup required before any
of the following can deploy successfully, now that they fail closed on
missing dashboard authentication:

- `.github/workflows/cloud-run-auto-deploy.yml`
- `scripts/gcp_cloud_run_auto_deploy.py`
- `deploy/gcp/deploy_web.sh`

None of these files create secrets or deploy anything by themselves outside
their normal trigger (push to `main` / `workflow_dispatch` for the workflow,
manual invocation for the scripts). This document does not perform any of
the steps below — an operator with Secret Manager admin access must.

## 1. Required Secret Manager secrets

| Purpose | Env var (secret ID override) | Secure default secret ID |
|---|---|---|
| Dashboard API key (`API_KEY`) | `API_KEY_SECRET_ID` | `system3-dashboard-api-key` |
| Worker push token (`WORKER_PUSH_TOKEN`) | `WORKER_PUSH_TOKEN_SECRET_ID` | `system3-dashboard-worker-push-token` |

Both must exist in the target GCP project (`GOOGLE_CLOUD_PROJECT`, default
`system3-openalgo-safe`) before deploying. All three deployment paths
(workflow, auto-deploy script, manual `deploy_web.sh`) verify this and
**refuse to deploy** if a secret is missing — they never fall back to
disabling auth or leaving `API_KEY` unmounted.

To create the secrets (run outside of any automated pipeline, by a human
with the appropriate IAM role):

```
gcloud secrets create system3-dashboard-api-key \
  --project=system3-openalgo-safe --replication-policy=automatic
printf '%s' "<generate a long random value, e.g. openssl rand -hex 32>" | \
  gcloud secrets versions add system3-dashboard-api-key \
    --project=system3-openalgo-safe --data-file=-

gcloud secrets create system3-dashboard-worker-push-token \
  --project=system3-openalgo-safe --replication-policy=automatic
printf '%s' "<generate a separate long random value>" | \
  gcloud secrets versions add system3-dashboard-worker-push-token \
    --project=system3-openalgo-safe --data-file=-
```

Use distinct, high-entropy values for each secret. Never paste secret
values into commit messages, PR descriptions, CI logs, or chat.

## 2. IAM

The Cloud Run runtime service account must hold
`roles/secretmanager.secretAccessor` on both secrets. The GitHub Actions
workflow grants this automatically during the "Configure rotator IAM, Cloud
Run Job and Cloud Scheduler" step. For manual deploys via `deploy_web.sh`,
grant it once ahead of time:

```
gcloud secrets add-iam-policy-binding system3-dashboard-api-key \
  --project=system3-openalgo-safe \
  --member="serviceAccount:system3-web@system3-openalgo-safe.iam.gserviceaccount.com" \
  --role=roles/secretmanager.secretAccessor

gcloud secrets add-iam-policy-binding system3-dashboard-worker-push-token \
  --project=system3-openalgo-safe \
  --member="serviceAccount:system3-web@system3-openalgo-safe.iam.gserviceaccount.com" \
  --role=roles/secretmanager.secretAccessor
```

## 3. What "fail closed" means here

- If a required secret does not exist or is inaccessible, the deploy step
  raises immediately (`SystemExit` in the Python script, `exit 1`/`exit 2`
  in the workflow/shell script) before any Cloud Run mutation happens.
- `REQUIRE_API_KEY` is always set to `true` and `API_KEY` is never removed
  or left unmounted. Automation must not weaken this; if a future change
  needs `REQUIRE_API_KEY=false`, that is a deliberate security regression
  and must go through review, not a deploy-script default.
- `LIVE_TRADING_ENABLED`, `SYSTEM3_LIVE_TRADING_ALLOWED`, and
  `AUTO_EXECUTE_TRADES` stay `0` across every deploy path, independent of
  the auth hardening above.

## 4. Cloud Run ingress model

Cloud Run ingress remains `--allow-unauthenticated` (public), by design:
the browser needs unauthenticated access to load the static UI and to call
`/api/auth/session`, `/api/auth/status`, `/api/auth/logout`, `/api/health`,
and `/healthz` (see `PUBLIC_EXACT` / `PUBLIC_PREFIXES` in
`dashboard/backend/security_policy.py`). Every other route requires a valid
dashboard session (HttpOnly cookie) or `X-API-Key` header validated against
`API_KEY`, and mutation routes additionally fail closed with `503` if auth
is not configured. Do not add `--no-allow-unauthenticated` at the Cloud Run
IAM layer as a substitute for application-level auth — it would break the
public login flow; the existing app-layer check is the intended control.

## 5. Verifying a deployment without printing credentials

After a deploy, verify auth is enforced using only booleans — never fetch
or print the actual `API_KEY` / `WORKER_PUSH_TOKEN` values:

```
curl -fsS "$SERVICE_URL/api/auth/status"
# Expect: {"required": true, "configured": true, "authenticated": false, ...}
```

To confirm mutation routes and session creation fail closed for anonymous
callers, probe with a deliberately invalid key and check only the HTTP
status code (never the real secret):

```
curl -s -o /dev/null -w '%{http_code}\n' -X POST "$SERVICE_URL/api/auth/session" \
  -H 'Content-Type: application/json' \
  -d '{"api_key":"deliberately-invalid-probe"}'
# Expect: 401
```

To verify a *real* session locally (e.g. as an operator with the actual
key), pipe the key in from a secret store or prompt — never hardcode it in
a script or paste it into a shared terminal/log:

```
read -rs API_KEY   # prompts, does not echo
curl -s -o /dev/null -w '%{http_code}\n' -X POST "$SERVICE_URL/api/auth/session" \
  -H 'Content-Type: application/json' \
  -d "{\"api_key\":\"${API_KEY}\"}"
unset API_KEY
```

The `.github/workflows/cloud-run-auto-deploy.yml` "Public UI broker proof"
step follows this pattern: it asserts `required`/`configured`/`authenticated`
booleans and one invalid-key probe status code, and never reads or logs the
real secret values.

## 6. Runtime evidence auth semantics

`scripts/gcp_runtime_evidence.py` computes `safety.api_key_required` and
`safety.api_key_mounted`. Both being `true` is the secure, expected state:
dashboard auth is enforced (`REQUIRE_API_KEY` is not disabled) and the
`API_KEY` value is sourced from Secret Manager (a `valueFrom.secretKeyRef`
env entry), not a plain `value`. This matches the workflow's own "Enforce
deployment provenance and safety lock" step, which fails the run if either
boolean is `false`.

The script also reports `safety.api_key_plaintext_exposed`, which is `true`
only if `API_KEY` (or `WORKER_PUSH_TOKEN`) is present on the Cloud Run
container as a plain environment value instead of a Secret Manager
reference; the value itself is never captured or logged, only the fact
that a plaintext binding exists. `safety_pass` (and therefore
`lock_result`/`production_grade_claim_allowed`) requires
`api_key_required == true`, `api_key_mounted == true`, and
`api_key_plaintext_exposed == false`, alongside the existing
analyzer-mode-on and live-trading-off invariants. The script's `blockers`
list reports *missing or disabled* authentication (e.g. "Dashboard API key
authentication is missing or disabled", "Dashboard API key is not mounted
from Secret Manager") — never enabled authentication — so a locked report
and the workflow's explicit auth checks always agree.
