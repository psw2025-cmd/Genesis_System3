# Broker Recurrence Forensic Checklist

This checklist is the fail-closed operating contract for recurring Dhan broker disconnects in authoritative GCP production. It is evidence-first: do not mint, rotate, reload, deploy, or change IAM merely to make a red status green before the initiating evidence has been captured.

## Current incident snapshot — 2026-08-17

The fresh current-main audit and production browser run reproduced the same operational failure on serving runtime SHA `3e377e7a428f1ffefccb3348a7a0ed6edf178f7d`, revision `genesis-system3-web-00422-yec`:

- broker `connected=false`, `TOKEN_EXPIRED_OR_INVALID`;
- Secret Manager token version `260` with about 13.9 JWT-clock hours still remaining;
- Dhan market-data path also returned HTTP 429 / code 805;
- all four required index option-chain subviews had zero proven contracts/strikes;
- `/api/health` remained `not_ready` because broker-backed real data was unavailable;
- LIVE trading and order placement remained disabled;
- the rotator forensic saw no legacy safe rotator status marker and therefore could not classify the initiating event from rotator logs alone.

The web runtime already maintains a process-local, non-secret first-auth-rejection trace. The forensic path must preserve an allow-listed projection of that trace instead of losing it when a historical rotator execution lacks a status marker.

### Post-#266 evidence correction

After the safe trace projection was merged, fresh Full Cloud Audit run `31988631903` proved that the current runtime trace being labelled `DHAN_TOKEN_REJECTED` was actually HTTP `400` with upstream Dhan code `906`, with the process-local rejection counter already amplified to `44763`. Current `cloud_status_probe.py` was then inspected and found to contain the literal `dh-906` inside its authentication marker list. That mapping caused HTTP 400/DH-906 to become `TOKEN_EXPIRED_OR_INVALID` and to increment the first-auth-rejection latch.

This is a classifier defect. Dhan's documented taxonomy distinguishes DH-906 as an order/request error, code 805 as too many requests, and 808 as authentication failure / invalid client ID or token. The current DH-906 observation therefore must not be used as token-invalid evidence. Earlier independently captured HTTP 401/code 808 observations remain separate evidence and are not erased by this correction.

The remediation contract is now explicit:

- HTTP 401 or Dhan 808 may classify as affirmative authentication rejection and may increment the first-auth-rejection latch.
- HTTP 429 or Dhan 805 classifies as `DHAN_RATE_LIMITED`; it must not increment the auth latch.
- Dhan DH-906 classifies as `DHAN_REQUEST_REJECTED_906`; it must not become `TOKEN_EXPIRED_OR_INVALID` and must not increment the auth latch.
- No token recovery is justified from a DH-906-only observation. First deploy the corrected classifier and obtain a fresh process/revision trace.

## Mail correlation reviewed

Repo-related mail from the preceding two days was reviewed as a secondary signal, never as production authority. It surfaced fresh failures of `Full Cloud Audit and Forensic Consensus` and `Frontend Browser Runtime Smoke`; both were independently revalidated against current GitHub runs and live production evidence before action. The broader mail pass also surfaced repeated GCP uptime alert/resolved cycles and Cursor Bugbot usage-limit failures. Bugbot availability is external review-service state, not production authority; uptime mail must be correlated with live service/audit evidence before remediation.

## PRE — mandatory before any remediation

1. Run/read the permanent System3 preflight control-plane snapshot and verify current `main`, active relevant workflow failures, artifacts, PRs, issues, and Issue #188 markers.
2. Re-read current remote `main`; never use an old event SHA as expected production truth.
3. Read the latest canonical Cloud Run deployment run and `/api/deploy/info`; distinguish control-only main changes from runtime-affecting changes.
4. Capture `/api/broker/status` before recovery and record only safe fields: connected/error, token source/version, JWT clock metadata, probe strategy/timeout, auth classification, and the allow-listed first-rejection trace.
5. Capture `/api/health`, required chains, and market-data rate-limit evidence in the same request-scoped observation window.
6. Capture exact-serving-SHA production browser evidence. A 22-tab render pass is not a semantic broker/data pass.
7. Read the latest rotator execution metadata/log markers without executing the job or reading secret payloads.
8. Correlate scheduler/manual-recovery executions so concurrent or duplicate mint authority is ruled in/out before any mint.
9. Preserve `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0`; confirm order endpoints were not called.
10. If a first upstream auth rejection exists, preserve its first timestamp/version/classification/HTTP/upstream code before any reload or recovery can obscure ordering.

## Classification rules

- HTTP 401 or Dhan code 808 with a positive first-rejection trace is affirmative upstream authentication rejection evidence.
- HTTP 429 / Dhan code 805 is rate-limit evidence. It must not be relabelled as authentication rejection without separate affirmative auth evidence.
- HTTP 400 / Dhan DH-906 is request/order-error evidence. It is not token-invalid evidence and must not increment the auth-rejection latch.
- JWT `exp` time remaining does not prove Dhan will continue to accept a token; upstream rejection and JWT-clock validity are separate facts.
- A missing rotator status marker is `NOT_PROVEN` for the rotator path. If the current web runtime independently has a safe first-rejection trace, classify it explicitly as `runtime_first_auth_rejection_trace`; never pretend it came from the rotator log.
- Broker `connected=true` alone is not full E2E readiness. Required broker-backed read-only market data and UI/API parity must also pass.

## Remediation sequence

1. Fix evidence loss or contradictory truth before triggering recovery.
2. If evidence proves current token invalid and recovery is genuinely required, use only the approved bounded recovery authority after checking cooldown/concurrency guards.
3. Never add an automatic GitHub cron for token minting; canonical scheduled freshness remains a GCP scheduler concern and manual recovery remains guarded.
4. After any token/version change, verify the new version, broker read-only profile, market-data read path, health, four required chains, and UI/API consistency.
5. If Dhan returns 429/805, respect cooldown/backoff; do not create a retry/mint storm.
6. If the profile probe returns DH-906 after the classifier correction, investigate the profile endpoint/request contract before considering token recovery.
7. A recurrence after a claimed fix invalidates the fix and reopens/escalates the incident.

## POST — mandatory before closure or next transition

1. Exact source SHA is serving the expected Cloud Run revision at 100% traffic.
2. `/api/broker/status`: source is `GCP_SECRET_MANAGER_DYNAMIC`, no secret values exposed, LIVE false, orders false.
3. First-rejection trace is visible to forensic evidence through the strict safe allow-list and contains no raw token, client ID, authorization header, request body, cookie, PIN, TOTP, or secret payload.
4. Rotator forensic classification identifies its authority (`rotator_safe_status` or `runtime_first_auth_rejection_trace`).
5. A fresh revision proves DH-906/805 do not increment the auth latch; only affirmative 401/808 auth evidence may do so.
6. `/api/health` and at least one direct broker-backed read-only market-data path are checked.
7. NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY chain source/count/freshness semantics are proven, not merely rendered.
8. Fresh production browser proof captures all canonical tabs and required chain subviews on exact serving SHA.
9. Current mandatory CI/security/browser/audit workflows are re-read. Historical unrelated failures remain context only.
10. Issue #188 receives the exact run/job/artifact/revision/SHA and the new state marker.
11. Relevant governance/incident documentation is updated from observed evidence; no final PASS is claimed from CI/docs alone.

## Safety non-claims

This checklist does not grant token mint authority, deploy authority, IAM mutation authority, LIVE-trading authority, or order authority. Secret payloads must not be recorded in reports, logs, issues, artifacts, or UI evidence.
