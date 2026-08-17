# Broker Recurrence Forensic Checklist

This checklist is the fail-closed operating contract for recurring Dhan broker disconnects in authoritative GCP production. It is evidence-first: do not mint, rotate, reload, deploy, or change IAM merely to make a red status green before the initiating evidence has been captured.

## Current incident snapshot — 2026-08-17

The current remediation started only after re-reading remote `main` and rerunning the permanent `System3 Preflight Control Plane`. The exact pre-remediation source remained `10dcfead6a19c371d9ad14dfcc963ce32b1dcde1`; the fresh preflight rerun passed and still identified the exact-main Cloud Run/browser/full-cloud operational failures as the active remediation target.

Fresh exact-serving production evidence before this remediation showed:

- broker `connected=false` with current upstream classification `DHAN_REQUEST_REJECTED_906`;
- token source `GCP_SECRET_MANAGER_DYNAMIC`; the token was still JWT-clock valid at capture;
- Dhan market-data also returned HTTP 429 / code 805 (`Too many requests`);
- NIFTY, BANKNIFTY, FINNIFTY and MIDCPNIFTY had no proven live contracts/strikes;
- `/api/health` remained `not_ready` because broker-backed real data was unavailable;
- all canonical dashboard tabs rendered, but broker/data semantic proof failed;
- LIVE trading and order placement remained disabled;
- recent rotator reliability was below the production-readiness target, so broker recovery cannot be treated as complete merely because a later single execution succeeds.

No token mint, rotation, IAM mutation, order call, or Secret Manager payload read is authorized by this incident record.

### Current endpoint-contract correction

Official Dhan endpoint documentation is authoritative for request shape. The current contract is:

- **User Profile GET**: `access-token` only.
- **Fund Limit GET**: `access-token` only.
- **Option Chain / Market Quote family where documented**: preserve required `access-token` + `client-id`.
- The existing GCP Secret Manager client-ID configuration remains authoritative and must not be recreated, rotated, removed, or exposed merely because Profile/Fund Limit omit that header.

Before this remediation, the generic read-only REST helper added `client-id` to every GET, including Profile and Fund Limit. The fix makes header inclusion endpoint-specific while leaving endpoints that require the client ID unchanged.

### Current Dhan error taxonomy

The classification and recovery boundaries must use the same current taxonomy:

- `DH-901`: trading authentication error → affirmative auth evidence.
- `DH-904`: trading API rate limit → rate-limit evidence; no token recovery.
- Data API `805`: too many requests/connections → rate-limit evidence; no token recovery.
- Data API `807`, `808`, `809`: access-token/authentication failures → affirmative token/auth evidence.
- Data API `810`: invalid client ID → configuration/client-ID investigation; **not** token recovery.
- `DH-906`: request/order error → non-auth request rejection; no token recovery.
- HTTP 401 remains affirmative authentication evidence.
- HTTP 429 remains rate-limit evidence.

Known numeric codes override misleading free text. In particular, 805/904/906 must never become `TOKEN_EXPIRED_OR_INVALID` and must never trigger Secret Manager reload or canonical rotation. Code 810 must not rotate the token: first verify the currently loaded client-ID metadata/pairing without exposing the value.

### Post-#266/#267 evidence correction

After safe first-rejection trace projection was merged, a fresh Full Cloud Audit proved that a runtime trace previously labelled `DHAN_TOKEN_REJECTED` was actually HTTP 400 with Dhan code 906, with the process-local rejection counter already heavily amplified. Inspection found `dh-906` contaminating both status classification and recovery-trigger logic. PR #267 removed that false 906-as-auth path.

The present remediation goes one level deeper: it aligns the Profile/Fund request headers with Dhan's documented contracts and expands the explicit numeric taxonomy beyond the earlier 808-only handling so the next production response is classified safely and precisely.

## Mail correlation reviewed

Repo/GCP/Dhan-related mail from the preceding two days was reviewed as a secondary signal, never as production authority. It shows repeated `Frontend Browser Runtime Smoke` and `Full Cloud Audit and Forensic Consensus` failures across multiple source SHAs, repeated GCP uptime ALERT→RESOLVED flapping, previous BR1 auth-classification work, BR2 request-amplification/rate-limit work, and periods where the broker temporarily recovered but later failed again. This recurrence pattern requires a core request/classification/rate-control fix rather than workflow retries or repeated token mints.

Historical mail, old workflow notifications, and old artifacts are context only. Every transition must be revalidated against current GitHub and current production evidence.

## PRE — mandatory before any remediation or transition

1. Run/read the permanent System3 preflight control-plane snapshot and verify current `main`, relevant workflow failures, artifacts, PRs/issues, and active blocker markers.
2. Re-read remote `main`; never use an old event SHA as expected production truth.
3. Check relevant workflows before starting overlapping work; do not launch duplicate deploy/recovery/token actions that can collide.
4. Read the latest canonical Cloud Run deployment run and exact serving revision/SHA.
5. Capture `/api/broker/status` before recovery and record only safe fields: connected/error, token source/version, JWT clock metadata, probe strategy/header contract, auth classification, upstream classification/code, and safe first-rejection trace.
6. Capture `/api/health`, required chains, and market-data rate-limit evidence in the same observation window.
7. Capture exact-serving-SHA production browser evidence. A tab-render pass is not a semantic broker/data pass.
8. Read latest rotator execution metadata/log markers without executing the job or reading secret payloads.
9. Correlate scheduler/manual-recovery executions so concurrent or duplicate mint authority is ruled in/out before any mint.
10. Preserve `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0`; confirm order endpoints were not called.
11. Verify endpoint-specific request contracts before blaming credentials. For Profile/Fund Limit, do not add `client-id`; for endpoints whose docs require it, use the existing Secret Manager-backed client ID.
12. If a first upstream auth rejection exists, preserve its first timestamp/version/classification/HTTP/upstream code before any reload or recovery can obscure ordering.

## Classification rules

- HTTP 401 or Dhan `901/807/808/809` is affirmative upstream authentication/token evidence.
- HTTP 429 or Dhan `904/805` is rate-limit evidence. It must not increment the auth latch and must not trigger auth recovery.
- Dhan `906` is request/order-error evidence. It must not become `TOKEN_EXPIRED_OR_INVALID`, increment the auth latch, or trigger auth recovery.
- Dhan `810` is client-ID/configuration evidence. Verify existing GCP Secret Manager client-ID loading/pairing safely; do not rotate the access token as the first response.
- Known numeric codes override ambiguous response free text.
- `auth_classification` is auth-only. Non-auth upstream conditions use `upstream_classification`.
- JWT `exp` time remaining does not prove Dhan will accept a token; upstream acceptance and JWT-clock validity are separate facts.
- A missing rotator status marker is `NOT_PROVEN`, not permission to mint.
- Broker `connected=true` alone is not E2E readiness. Broker-backed market data, required chains, health, UI/API consistency and exact-serving source proof must also pass.

## Remediation sequence

1. Fix contradictory/evidence-loss paths before recovery.
2. Fix endpoint request contract before credential replacement.
3. Keep classification and recovery-trigger taxonomy identical; non-auth 805/904/906 and config 810 must not enter token recovery.
4. If genuine 901/807/808/809/401 token rejection is freshly proven, use only approved bounded recovery after checking concurrency/global cooldown guards.
5. Never add an automatic GitHub cron for token minting; scheduled freshness remains GCP scheduler authority and manual recovery remains guarded.
6. If Dhan returns 429/805/904, respect cooldown/backoff and investigate request fan-out, polling, caching/coalescing, and retry behavior; do not create a retry/mint storm.
7. After a code fix: exact-head CI → merge when green → re-read new main → exact-main Cloud Run deployment → exact-serving URL/API/browser proof.
8. If deployment succeeds but URL proof fails, investigate and open/implement the next bounded remediation immediately; do not stop at the red report.
9. A recurrence after a claimed fix invalidates that closure claim and reopens/escalates the incident.

## POST — mandatory before closure or next transition

1. Exact merged source SHA is serving the expected Cloud Run revision at 100% traffic.
2. `/api/broker/status`: source is `GCP_SECRET_MANAGER_DYNAMIC`, no secret values exposed, LIVE false, orders false.
3. Profile probe reports the canonical `access-token-only` header contract; no client-ID value is logged/exposed.
4. First-rejection trace is available through the strict safe allow-list and contains no raw token, client ID, authorization header, request body, cookie, PIN, TOTP, or secret payload.
5. Fresh revision proves 805/904/906 do not increment the auth latch or trigger Secret Manager reload/canonical rotation; 810 produces a config/client-ID classification rather than token recovery; only affirmative auth/token evidence enters recovery.
6. `/api/health` and at least one direct broker-backed read-only market-data path are checked.
7. NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY chain source/count/freshness semantics are proven, not merely rendered.
8. Fresh production browser proof captures all canonical tabs and required chain subviews on the exact serving SHA.
9. Current mandatory CI/security/browser/audit workflows are re-read. Historical unrelated failures remain context only.
10. Current deployment/runtime artifacts are fresh and pinned to the exact serving SHA; no stale artifact may be promoted as current truth.
11. Issue/governance/system-state records are updated with exact run/job/artifact/revision/SHA and new state marker where applicable.
12. Run final smoke only after the preceding checks. Final PASS requires both control-plane and live semantic proof; CI/docs alone cannot close the incident.

## Safety non-claims

This checklist does not grant token mint authority, deploy authority, IAM mutation authority, LIVE-trading authority, or order authority. Secret payloads must not be recorded in reports, logs, issues, artifacts, or UI evidence.
