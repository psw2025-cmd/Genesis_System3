# Secure Cloud Run Deployment Prerequisites

This document describes the active Genesis System3 Google Cloud Run security
contract. The dashboard is permanently **public/read-only** while execution
capabilities remain separately fail-closed. Opening `/ui` never requires a
dashboard credential, login session, API-key header, or dashboard-key secret.
Public visibility is never mutation authority.

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

There is intentionally **no dashboard API-key secret requirement**. Retired
dashboard credential/session names are deny markers only; the canonical deployer
removes them from every candidate and runtime proof fails if they reappear.

## 2. IAM

The Cloud Run runtime identity needs access only to resources the web runtime
actually consumes. Dashboard viewing does not require access to any dashboard
credential secret.

The worker ingestion token remains secret-backed. Broker credential/rotation
permissions are governed separately by the canonical Dhan rotation authority and
must not be broadened merely because dashboard reads are public.

## 3. Fail-closed contract

Deployment must fail when any of these safety invariants is violated:

- `ANALYZE_MODE` is not enabled;
- `LIVE_TRADING_ENABLED`, `SYSTEM3_LIVE_TRADING_ALLOWED`, or
  `AUTO_EXECUTE_TRADES` is enabled;
- a retired dashboard credential/session environment variable reappears;
- a retired dashboard credential secret is mounted or appears as plaintext;
- the browser renders a dashboard credential/login prompt;
- the serving API exposes dashboard login/session creation or logout authority;
- `WORKER_PUSH_TOKEN` is missing, not Secret-Manager-backed, or exposed as a
  plaintext value;
- the runtime source SHA does not match the actual 100%-traffic serving
  revision's `DEPLOY_GIT_SHA`;
- Cloud Run serving traffic is not bound to exactly one proven revision;
- mutation capability ownership is unknown or ambiguous;
- LIVE mutation or LIVE approval capability becomes executable;
- secret payloads are exposed.

The absence of a dashboard credential is not a degraded mode. It is the required
architecture.

## 4. Cloud Run ingress model

Cloud Run remains publicly reachable so browsers can load `/ui` and anonymous
read APIs. The application safety boundary is capability-based:

- GET/read dashboard surfaces are public;
- public control/paper/risk/scheduler/analyzer mutations remain denied unless a
  distinct, explicitly implemented and proven control-plane authority exists;
- `LIVE_MUTATION` and `LIVE_APPROVAL` remain hard denied in the current runtime;
- worker ingestion uses only its dedicated worker token;
- UI state and browser inputs can never grant mutation authority.

Do not restore `LoginPage`, `AuthGate`, browser dashboard-key storage,
`X-API-Key` replay, dashboard session cookies, or `/api/auth/session`.

## 5. Verifying deployment without credentials

```bash
curl -fsS "$SERVICE_URL/api/auth/status"
# Required contract:
# required=false
# configured=false
# authenticated=false
# mode=public_readonly
# credential_surface=REMOVED

curl -fsS "$SERVICE_URL/ui" >/dev/null
curl -fsS "$SERVICE_URL/api/state" >/dev/null
curl -fsS "$SERVICE_URL/api/health" >/dev/null
```

The deploy workflow separately probes MutationPolicy sentinels to prove that
public visibility cannot become public write authority. Those probes never place,
modify, cancel, or route a broker order.

## 6. Runtime evidence semantics

`scripts/gcp_runtime_evidence.py` binds evidence to the actual single 100%-traffic
serving revision. The required state is:

```text
ANALYZE_MODE = ON
LIVE_TRADING_ENABLED = OFF
SYSTEM3_LIVE_TRADING_ALLOWED = OFF
AUTO_EXECUTE_TRADES = OFF
retired dashboard credential env = absent
retired dashboard secret mounts = absent
retired dashboard plaintext credentials = absent
/api/auth/status credential_surface = REMOVED
```

Compatibility report fields such as `api_key_required`, `api_key_mounted`, and
`api_key_plaintext_exposed` represent detected regression/drift only. All must be
false because the credential surface itself must be absent.

The workflow must still fail for source/deployment mismatch, secret exposure,
worker-auth failure, unsafe mutation capability, Firestore failure, or LIVE-mode
drift. Permanently removing dashboard credentials must never weaken those
independent controls.
