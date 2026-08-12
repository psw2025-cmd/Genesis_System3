# Genesis System3 Manual Repository QC Master Audit

As of 2026-08-12 21:01 IST. This file remains the single master authority for manual repository/runtime QC evidence. Do not create competing status reports.

## Executive state

- Deployed application SHA: `e3b1f3b40fcc65223acb65d5189529dae3af2e90`.
- Cloud Run Auto Deploy #79 (`31607212444`): **SUCCESS**.
- Serving / latest-created / latest-ready revision: `genesis-system3-web-00249-22f`.
- Promotion path: guarded 0%-traffic candidate -> exact runtime/UI proof -> 100% serving traffic.
- Automated UI proof: **22/22 tabs PASS; desktop 22/22; mobile 22/22; 44/44 screenshots; 0 failures; 0 retries**.
- Retired dashboard credential mounts: `API_KEY` absent and `DASHBOARD_API_KEY` absent on the exact serving revision.
- Runtime mode: ANALYZER / PAPER. LIVE remains **OFF / LOCKED**.
- Real order actions in the canonical proof: **0**.
- Operational readiness remains **DEPLOYMENT_LOCKED** because broker/state convergence, MIDCPNIFTY OptionChainTruth, and ScannerTruth remain unresolved.

## Required PR / CI authority

### PR #130 — immutable Cloud Run digest provenance

- State: **MERGED / CLOSED**.
- Exact head: `56a37ae3841fe5342e5359c03570b9431d52166c`.
- Merge commit: `e09824188ab7c30f08c0af48cf7e27bb0a22d798`.
- Global Safety CI: **PASS**.
- GCP Dhan Token Fix CI: **PASS**.
- Digest-resolution/provenance lane remains part of the canonical deployment path.

### PR #129 — stale no-key cleanup lane

- State: **OPEN / NON-MERGEABLE**.
- Exact head: `04f27e100b53e464f5d6ba5b407d8faaff74b3ef`.
- Global Safety CI: **FAIL**.
- GCP Dhan Token Fix CI: **PASS**.
- GCP Stage 2 Safety: **PASS**.
- Workflow Priority Guard: **PASS**.
- 41 commits / 37 changed files. No wholesale merge or rebase is authorized. Current-main focused fixes only.

### PR #146 — retired dashboard secret mount removal

- State: **MERGED** to deployed application SHA `e3b1f3b40fcc65223acb65d5189529dae3af2e90`.
- Exact-head required CI: **PASS** before merge.
- Runtime closure: run #79 proves `DASHBOARD_API_KEY` is physically absent from the exact serving revision while the dedicated worker credential remains separate.

### Parallel stale lanes

- PR #121 Observability: open/non-mergeable; selective read-only correlation IDs, redacted synthetics, uptime checks and runbook concepts only.
- PR #125 OperationsTruth: open/non-mergeable; selective typed inventory/SLO/operations evidence only.
- Neither lane grants LIVE/order authority and neither is a wholesale merge candidate.

## Cloud Run exact truth — run #79

- Workflow: Cloud Run Auto Deploy #79 / run `31607212444` / **SUCCESS**.
- Application SHA: `e3b1f3b40fcc65223acb65d5189529dae3af2e90`.
- Candidate revision: `genesis-system3-web-00249-22f`.
- Initial candidate traffic: **0%**.
- Exact candidate proof: **PASS**.
- Final serving traffic: **100%**.
- Serving revision: `genesis-system3-web-00249-22f`.
- Latest-created revision: `genesis-system3-web-00249-22f`.
- Latest-ready revision: `genesis-system3-web-00249-22f`.
- Source/deployment provenance match: **true**.
- Public invoker: **true**.
- `ANALYZE_MODE=1`.
- `SYSTEM3_MODE=ANALYZER`.
- `LIVE_TRADING_ENABLED=0`.
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`.
- `AUTO_EXECUTE_TRADES=0`.
- Dashboard credential authority: removed; no `API_KEY` or `DASHBOARD_API_KEY` serving mount.
- Worker ingestion token remains isolated from public dashboard authority.

## UI / dashboard exact-serving proof

UI/dashboard remains the top visible priority and is closed at the deterministic automated-proof level for run #79:

- Canonical tabs: **22**.
- Tabs PASS: **22/22**.
- Desktop screenshots: **22/22**.
- Mobile screenshots: **22/22**.
- Total exact screenshots: **44/44**.
- Failed tabs: **0**.
- Retries: **0**.
- API-key/login prompt rendered: **false**.
- API key used for dashboard reads: **false**.
- Browser mutation activity: **false**.
- Trading/order mutations: **0**.
- LIVE remains **OFF / LOCKED**.

Automated rendering/capture is therefore PASS. Product-design/UX review remains separate from this deterministic runtime proof.

## Permanent sentinels — exact run #79 evidence

### `/api/health`

- HTTP: **200**.
- status: **ok**.
- mode: **PAPER**.
- observed latency: approximately **306.68 ms**.

### `/api/broker/status` — direct BrokerTruth

- HTTP: **200**.
- `connected=false`.
- `error_present=true`.
- token source: `GCP_SECRET_MANAGER_DYNAMIC`.
- loaded secret version: **101**.
- endpoint-reported latest secret version: unavailable/null in this sanitized sample.
- LIVE trading: **false**.
- orders allowed: **false**.
- observed endpoint duration: approximately **12.79 s**.
- Secret payload value was not exposed or read into this report.

### `/api/state` — StateTruth

- HTTP: **200**.
- mode: **PAPER**.
- `broker_connected=true`.

## Broker disconnect / recurrence / RCA ledger

### Previous recurrence — run #78

- Direct `/api/broker/status`: `connected=true`.
- `/api/state`: `broker_connected=false`.
- Result: **CONTRADICTION / NOT CLOSED**.

### Current recurrence — run #79

- Direct `/api/broker/status`: `connected=false` and `error_present=true`.
- `/api/state`: `broker_connected=true`.
- Result: **CONTRADICTION / NOT CLOSED**.
- The direction of disagreement has flipped relative to run #78.

### Root cause

**UNPROVEN from the sanitized evidence currently available.** Do not attribute this to token expiry, cache state, probe timing, Firestore, Dhan, or any other subsystem without exact typed evidence.

### Required remediation

- Keep deployment/readiness locked.
- Require direct BrokerTruth and StateTruth to converge on the same connection state in the same proof window.
- Capture a typed, sanitized broker error category/phase when `error_present=true`; never expose credentials or broker payload secrets.
- Do not treat StateTruth alone or direct BrokerTruth alone as sufficient production-readiness authority while the two disagree.

### Prevention

- Fail closed whenever direct BrokerTruth and StateTruth disagree.
- Fail closed whenever direct broker `error_present=true`, even if a separate cached/state endpoint reports connected.
- Re-run the permanent read-only sentinels on every canonical deployment and preserve recurrence/root-cause/remediation/prevention here in this single master file.

## OptionChainTruth — run #79

- **NIFTY:** 160 contracts — READY.
- **BANKNIFTY:** 160 contracts — READY.
- **FINNIFTY:** 160 contracts — READY.
- **MIDCPNIFTY:** 0 contracts — `NO_DHAN_DATA / dhan_only_no_rows` — NOT READY.
- Required chains ready: **3/4**.
- `all_required_chains_ready=false`.

MIDCPNIFTY remains the sole strict OptionChainTruth blocker. The absence of rows is an observed result, not a proven upstream root cause.

## ScannerTruth — run #79

- Read-only scanner request timed out at approximately **30 seconds**.
- Scanner did not call a broker order path.
- Scanner readiness: **NOT READY / UNCONFIRMED**.
- Production-grade scanner claims remain disallowed until deterministic read-only proof completes within the accepted contract.

## MutationPolicy — run #79

- Runtime manifest: **ENFORCED**.
- Unknown write routes: **0**.
- Duplicate write routes: **0**.
- Public dashboard: **READ-ONLY**.
- LIVE mutation: **HARD_DENY**.
- LIVE approval: **HARD_DENY**.
- Real order calls in proof: **0**.
- Unsafe mutation calls in proof: **0**.
- Secret payload exposure: **none**.

## Dhan rotator / Scheduler recurrence ledger

- Scheduler: **ENABLED**.
- Cadence: `30 7 * * *`.
- Timezone: `Asia/Kolkata`.
- Run #79 explicit token-rotator execution: **SUCCESS**.
- Recent successful executions include `genesis-system3-dhan-token-rotate-zxbmd` and `genesis-system3-dhan-token-rotate-gvxvx`.
- Historical execution `genesis-system3-dhan-token-rotate-j6jlh` recorded a failure with `failedCount=1` / `ContainerCalledExit` (`container called exit(1)`).

Historical failure root cause is not re-attributed without exact evidence. Prevention remains mandatory identity, cadence and execution exit-state proof on every canonical deployment.

## Current blockers

1. **BrokerTruth:** direct broker is disconnected and reports an error in run #79.
2. **BrokerTruth vs StateTruth:** direct=false while StateTruth=true; contradiction remains open.
3. **MIDCPNIFTY OptionChainTruth:** 0 usable contracts / not ready.
4. **ScannerTruth:** read-only scanner timed out around 30 seconds and is unconfirmed.
5. **Operational readiness:** remains `DEPLOYMENT_LOCKED`; production-grade/live-readiness claims are prohibited until all strict blockers close with reproducible evidence.

UI/dashboard automated proof is **not** an active blocker: exact run #79 is 22/22 tabs and 44/44 screenshots.

## Safety authority

- LIVE: **OFF / LOCKED**.
- Real order actions: **0**.
- Public dashboard: credential-free and read-only.
- No retired dashboard secret mounted on the exact serving revision.
- No secret payload values recorded here.
- No gate has been weakened to obtain a green result.
