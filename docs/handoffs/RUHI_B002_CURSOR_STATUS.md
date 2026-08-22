# RUHI B002 — Cursor status

RULE_VERSION=RUHI_RULE_V2
BATCH_ID=B002
WRITTEN_UTC=2026-08-22T10:25:00Z
INVESTIGATION_START_UTC=2026-08-22T10:16:10Z
MARKET_PHASE=CLOSED

## Authority SHAs

- Previous serving/runtime SHA (pre-#318): `d3119d669b7bcb871c8dc7b94eabcc44363f8e65`
- New GitHub main after PR #318 merge: `3661b61b4543a6f45b0ecf48a56cd0f765716881`
- Serving SHA after #318: NOT recaptured as current yet. Cloud Run Auto Deploy run `32567500703` was `in_progress` at 2026-08-22T10:24:22Z.

## PREVIOUS_BATCH_COMMITMENT

- RUHI-004 exact-main vs serving recapture
- RUHI-005 safe broker recovery/root cause
- Issue #188 / ChatGPT mail: sanitized scheduler-health validator on current main; do not merge stale #286

## PREVIOUS_BATCH_RESULT

- RUHI-004 = DONE
- RUHI-005 = PARTIAL
- RUHI-006 = OPEN
- RUHI-021 = DONE_CODE / DONE_TESTED / MERGED; deploy/UI proof pending

## COMPLETED_WITH_PROOF

- RUHI-004 | serving SHA matched runtime-affecting main after #316 | GET `/api/deploy/info` 2026-08-22T10:16:10Z `git_sha=d3119d66`
- RUHI-021 | named scheduler-health gate | PR #318 merged 2026-08-22T10:23:56Z as `3661b61b4543a6f45b0ecf48a56cd0f765716881`; local 32 tests passed; live replay named `observability.alert_severity_none`

## NOT_COMPLETED

- RUHI-005 | `connected=true`, secret version metadata `298`, LIVE=false, orders=false is not AUTH_OK + live 4/4 acceptance
- RUHI-007/008/016/017 | weekend CLOSED; 4/4 chains were honest Dhan snapshots from ~08:35Z, not live ticks
- RUHI-021 deploy proof | waiting exact serving SHA `3661b61b4` and named gate artifact from Cloud Run Auto Deploy `32567500703`

## BLOCKERS_OR_CONFUSION

- Live `genesis-system3-dhan-token-rotate-daily` schedule is `*/5 * * * *` Asia/Kolkata
- `dashboard/backend/scheduler_contract.py` expects `30 * * * *`
- ChatGPT owns which SSOT wins
- Issue #188 comment API was denied from this Cursor cloud identity; durable write is this file + ledger + path index

## HANDOFF_REQUIRED

- Cursor → ChatGPT | rotate-daily cadence contradiction | `dashboard/backend/scheduler_contract.py`
- Cursor → ChatGPT | read path index | `docs/handoffs/CURSOR_TO_CHATGPT_PATH_INDEX.md`
- Cursor → deploy | prove `3661b61b4` 100% serving

## NEXT_BATCH_COMMITMENT

1. Wait Cloud Run Auto Deploy `32567500703` for exact `3661b61b4`
2. Fresh `/api/deploy/info` after that time; do not reuse pre-merge SHA
3. Read named scheduler-health artifact (`CURL_*` vs predicate names)
4. ChatGPT decide `*/5` vs `30 * * * *`
5. Consume PR #313 Dhan verifier only from a successful exact-main deploy event
6. 4/4 semantic chain source/freshness
7. Canonical `/ui` parity
8. Keep LIVE=false, orders=false
9. No blind rotator/IAM retry
10. Keep Gmail as mirror only

## METRICS

- TOTAL_KNOWN=21
- DONE=5 (RUHI-001/002/003/004 + RUHI-021 merged)
- PARTIAL=1 (RUHI-005)
- OPEN_EXECUTABLE=15
- USER_ACTION_REQUIRED=NONE

## Gmail now used

Past failure: Gmail MCP was `needsAuth`, so Cursor could not read ChatGPT controller mail.

Now used:

- Latest ChatGPT controller mail 2026-08-22T09:25:16Z: `RHUI V2 Genesis Controller: Cloud Run gate failure isolated next fix defined`
- Latest ChatGPT URL-truth mail 2026-08-22T09:53:44Z: `Genesis URL Truth Watch: Production acceptance remains on hold`
- User lock 2026-08-22T00:06:16Z: `SYSTEM3 ALL-AGENT COORDINATION LOCK — Issue #188 SSOT`

Those mails agree with Issue #188: isolate the opaque scheduler-health jq failure, do not merge stale #318/#286 confusion, keep production acceptance on hold until exact-serving semantic proof. Cursor already executed the isolated fix as merged PR #318.
