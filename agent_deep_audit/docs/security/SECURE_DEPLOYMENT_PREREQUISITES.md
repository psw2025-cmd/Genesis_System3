# Secure Cloud Run Deployment Prerequisites

This document describes the active Genesis System3 Google Cloud Run security contract.
The dashboard is intentionally **public/read-only while the system is in ANALYZER/PAPER mode**.
Opening `/ui` must not require a dashboard API key. Public visibility is never mutation authority.

Active deployment paths:

- `.github/workflows/cloud-run-auto-deploy.yml`
- `scripts/gcp_cloud_run_auto_deploy.py`
- `deploy/gcp/deploy_web.sh`

Google Cloud is the only deployment target for this repository.

## 1. Required Secret Manager secret

| Purpose | Env var (secret ID override) | Secure default secret ID |
|---|---|---|
| Worker ingestion token (`WORKER_PUSH_TOKEN`) | `WORKER_PUSH_TOKEN_SECRET_ID` | `system3-dashboard-worker-push-token` |

`WORKER_PUSH_TOKEN` must exist in Secret Manager before deployment and must be
mounted with a Secret Manager reference. Its raw value must never be written to
source, logs, reports, PR text, or chat.

A dashboard `API_KEY` is **not required and must not be mounted** in the serving
PAPER/ANALYZER web service. The active deployment contract sets
`REQUIRE_API_KEY=false` and removes `API_KEY` from the Cloud Run revision.

## 2. IAM

The Cloud Run runtime identity needs Secret Manager access only for secrets that
the runtime actually consumes. Dashboard viewing does not require access to a
dashboard API-key secret.

The worker ingestion token remains secret-backed. Broker credential/rotation
permissions are governed separately by the canonical Dhan rotation authority and
must not be broadened merely to make dashboard reads public.

## 3. Fail-closed contract

Deployment must fail when any of these safety invariants is violated:

- `ANALYZE_MODE` is not enabled;
- `LIVE_TRADING_ENABLED`, `SYSTEM3_LIVE_TRADING_ALLOWED`, or
  `AUTO_EXECUTE_TRADES` is enabled;
- an `API_KEY` requirement is reintroduced into the public PAPER dashboard;
- `API_KEY` is mounted or exposed as a plaintext environment value;
- `WORKER_PUSH_TOKEN` is missing, not Secret-Manager-backed, or exposed as a
  plaintext value;
- the runtime source SHA does not match the deployed `DEPLOY_GIT_SHA`;
- Cloud Run serving traffic is not bound to the proven revision;
- mutation capability ownership is unknown/ambiguous;
- LIVE mutation or LIVE approval capability becomes executable in PAPER mode;
- secret payloads are exposed.

Deployment must **not** fail merely because the dashboard API key is absent. Its
absence is the approved public-read-only PAPER state.

## 4. Cloud Run ingress model

Cloud Run remains publicly reachable so the browser can load `/ui` and anonymous
read APIs. The application safety boundary is capability-based:

- GET/read dashboard surfaces may be public in PAPER/ANALYZER;
- anonymous control/paper/risk/scheduler/analyzer mutations remain denied unless a
  future explicit control-plane authority is implemented and proven;
- `LIVE_MUTATION` and `LIVE_APPROVAL` remain hard denied;
- worker ingestion uses only its dedicated worker token;
- UI state can never grant mutation authority.

Do not restore `LoginPage`, `AuthGate`, reusable browser API-key storage, or
`X-API-Key` replay as a prerequisite for viewing the PAPER dashboard.

## 5. Verifying a deployment without credentials

The public access contract is verified without sending any dashboard key:

```bash
curl -fsS "$SERVICE_URL/api/auth/status"
# Expected: required=false, configured=false, mode=auth_disabled

curl -fsS "$SERVICE_URL/ui" >/dev/null
curl -fsS "$SERVICE_URL/api/state" >/dev/null
curl -fsS "$SERVICE_URL/api/health" >/dev/null
```

The deploy workflow separately probes mutation-policy sentinels to prove that
public visibility does not become public write authority. Those probes must never
place, modify, cancel, or route a broker order.

## 6. Runtime evidence semantics

`scripts/gcp_runtime_evidence.py` reports:

- `safety.api_key_required` — must be `false` for the active PAPER dashboard;
- `safety.api_key_mounted` — must be `false`;
- `safety.api_key_plaintext_exposed` — must always be `false`;
- `safety.dashboard_public_readonly` — must be `true`;
- analyzer/live safety booleans independently.

A valid public PAPER dashboard therefore requires:

```text
ANALYZE_MODE = ON
LIVE_TRADING_ENABLED = OFF
SYSTEM3_LIVE_TRADING_ALLOWED = OFF
AUTO_EXECUTE_TRADES = OFF
REQUIRE_API_KEY = false
API_KEY mount = absent
API_KEY plaintext exposure = false
```

The workflow must still fail for source/deployment mismatch, secret exposure,
worker-auth failure, unsafe mutation capability, or LIVE-mode drift. Removing the
obsolete dashboard-key requirement must never weaken those controls.
