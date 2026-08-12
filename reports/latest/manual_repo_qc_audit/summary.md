# Genesis System3 Manual Repository QC Master Audit

As of 2026-08-12 22:01 IST. This file is the single master authority for manual repository/runtime QC evidence. Do not create competing status reports.

## Executive state

- Repository: `psw2025-cmd/Genesis_System3` only.
- Repository `main` before this report-only correction: `50cd417ca46b13660b3cac4984fd04e5fffe4bc4`.
- Deployed application SHA: `e3b1f3b40fcc65223acb65d5189529dae3af2e90`.
- Cloud Run Auto Deploy #79 (`31607212444`): **SUCCESS**.
- Canonical run #79 serving revision proved by deploy logs, UI proof, runtime identity proof and terminal control-plane query: **`genesis-system3-web-00248-lax` @ 100% traffic**.
- Correction: the prior report incorrectly recorded `genesis-system3-web-00249-22f`; canonical run #79 logs prove `00248-lax`. This correction changes documentation only and does not mutate Cloud Run.
- Promotion path: guarded 0%-traffic candidate -> exact candidate proof -> explicit promotion -> 100% serving traffic.
- Automated UI proof: **22/22 tabs PASS; desktop 22/22; mobile 22/22; 44/44 screenshots; 0 failures; 0 retries**.
- Retired dashboard credential mounts: `API_KEY` absent and `DASHBOARD_API_KEY` absent from the run #79 deployed candidate/runtime evidence.
- Runtime mode: ANALYZER / PAPER. LIVE remains **OFF / LOCKED**.
- Real order actions in the canonical proof: **0**.
- Operational readiness remains **DEPLOYMENT_LOCKED** because BrokerTruth, BrokerTruth/StateTruth convergence, MIDCPNIFTY OptionChainTruth and ScannerTruth are unresolved.

## Required PR / CI authority

### PR #130 — immutable Cloud Run digest provenance

- State: **MERGED / CLOSED**.
- Exact head: `56a37ae3841fe5342e5359c03570b9431d52166c`.
- Merge commit: `e09824188ab7c30f08c0af48cf7e27bb0a22d798`.
- Global Safety CI: **PASS**.
- GCP Dhan Token Fix CI: **PASS**.
- The digest resolver is wired into the canonical Cloud Run deployer and remains part of the active deployment path.

### PR #129 — stale no-key cleanup lane

- State: **OPEN / NON-MERGEABLE**.
- Exact head: `04f27e100b53e464f5d6ba5b407d8faaff74b3ef`.
- Global Safety CI: **FAIL**.
- GCP Dhan Token Fix CI: **PASS**.
- GCP Stage 2 Safety: **PASS**.
- Workflow Priority Guard: **PASS**.
- 41 commits / 37 changed files. Never wholesale merge or rebase this stale lane. Use focused current-main fixes only.

### PR #146 — retired dashboard secret mount removal

- State: **MERGED** into deployed application SHA `e3b1f3b40fcc65223acb65d5189529dae3af2e90`.
- Exact-head required CI: **PASS** before merge.
- Run #79 proves the canonical deployment scrub is active and the public dashboard remains credential-free/read-only.

### Parallel stale lanes

- PR #121 Observability: open/non-mergeable; selective current-main salvage only for read-only correlation IDs, redacted synthetics, uptime checks and runbook concepts.
- PR #125 OperationsTruth: open/non-mergeable; selective current-main salvage only for typed inventory/SLO/operations evidence.
- Neither lane grants LIVE/order authority and neither is a wholesale merge candidate.

## Cloud Run exact truth — run #79

Canonical run #79 evidence from workflow job `94149144665`:

- Workflow: Cloud Run Auto Deploy #79 / run `31607212444` / **SUCCESS**.
- Application SHA: `e3b1f3b40fcc65223acb65d5189529dae3af2e90`.
- Candidate revision: `genesis-system3-web-00248-lax`.
- Candidate image immutable digest: `sha256:353dd9813af683eaf017fc46d30d38b639f5c2a2b05b51c547abbb19e7d70702`.
- Initial candidate traffic: **0%**.
- Candidate HTTP proof: **PASS**.
- Promotion: explicit.
- Promoted traffic: **`genesis-system3-web-00248-lax`: 100%**.
- UI proof serving revision: `genesis-system3-web-00248-lax`.
- Runtime identity proof serving traffic: `genesis-system3-web-00248-lax`: 100%.
- Terminal workflow control-plane table: `genesis-system3-web-00248-lax` / 100%.
- Source/deployment provenance match: **true**.
- Public dashboard: read-only, no API key required.
- `ANALYZE_MODE=1`.
- `SYSTEM3_MODE=ANALYZER`.
- `LIVE_TRADING_ENABLED=0`.
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`.
- `AUTO_EXECUTE_TRADES=0`.
- No secret payload was included in proof artifacts.

No newer Cloud Run Auto Deploy exists after #79 at this checkpoint. The later `main` changes are report-only and do not supersede deployed application SHA `e3b1f3...`.

## UI / dashboard — top visible priority

Exact-serving run #79 deterministic proof:

- `/ui`: HTTP 200.
- Canonical tabs: **22**.
- Tabs PASS: **22/22**.
- Desktop screenshots: **22/22**.
- Mobile screenshots: **22/22**.
- Total exact screenshots: **44/44**.
- Failed tabs: **0**.
- Retries: **0**.
- Browser transport: `webdriver_single_session`.
- API-key/login prompt rendered: **false**.
- API key used for dashboard reads: **false**.
- Browser mutation activity: **false**.
- Trading/order mutations: **0**.
- LIVE remains **OFF / LOCKED**.

Automated rendering/capture is therefore PASS. Product-design/UX review remains a separate evidence domain.

## MutationPolicy — run #79

- Runtime proof: **PASS**.
- Manifest: **ENFORCED**.
- Write routes: **33**.
- Unknown write routes: **0**.
- Duplicate write routes: **0**.
- Public dashboard read-only: **true**.
- Control authority configured: **false**.
- LIVE mutation: **HARD_DENY**.
- LIVE approval: **HARD_DENY**.
- Paper mutation probe: 403 / `PAPER_MUTATION_AUTHORITY_REQUIRED`.
- LIVE mutation probe: 423 / `LIVE_MUTATION_LOCKED`.
- Invalid worker probe: 401 / `WORKER_AUTH_INVALID`.
- Unknown mutation probe: 403 / `MUTATION_CAPABILITY_UNKNOWN`.
- Real order calls: **0**.
- Paper mutation handlers called: **0**.
- Secret values exposed: **false**.

## Permanent sentinels / BrokerTruth / StateTruth

### Canonical run #79 sanitized runtime-evidence sample

`/api/health`:
- HTTP: **200**.
- status: **ok**.
- mode: **PAPER**.
- sanitized proof latency: approximately **281.2 ms**.

`/api/broker/status` direct BrokerTruth:
- HTTP: **200**.
- `connected=false`.
- `error_present=true`.
- token source: `GCP_SECRET_MANAGER_DYNAMIC`.
- sanitized sample secret metadata version: **95**.
- token value exposed: **false**.
- LIVE trading: **false**.
- order placement allowed: **false**.
- endpoint HTTP round-trip in sanitized proof: approximately **4.14 s**; broker-reported internal latency approximately **1.835 s**.

The workflow's earlier mandatory broker-read gate passed after bounded retries, proving that broker connectivity changed within the same deployment proof window. The later sanitized sample returned disconnected. Therefore BrokerTruth is temporally unstable and remains **NOT CLOSED**.

`/api/state` StateTruth:
- The prior master checkpoint recorded `broker_connected=true` while the later direct BrokerTruth sample was false.
- Result remains **CONTRADICTION / NOT CLOSED**.

### Fresh sentinel attempt at this checkpoint

A fresh anonymous read-only attempt to `/api/health` and `/api/broker/status` was made from the control-loop execution environment. DNS resolution for the Cloud Run hostname failed (`Temporary failure in name resolution`). This is an observer/tooling failure, not evidence that the service itself is down. It does not supersede canonical run #79 evidence.

### Broker disconnect / recurrence / RCA ledger

- Run #78 recurrence: direct BrokerTruth connected while StateTruth reported disconnected.
- Run #79 recurrence: mandatory broker-read gate passed after retries; later sanitized direct BrokerTruth was disconnected with `error_present=true`; StateTruth evidence remained non-convergent.
- Direction/timing of the disagreement is unstable across proof windows.
- Root cause: **UNPROVEN**. Do not attribute to token expiry, cache, Firestore, Dhan, probe timing or any other subsystem without typed evidence.

Required remediation:
- Keep readiness/deployment lock closed.
- Require direct BrokerTruth and StateTruth to agree in the same bounded proof window.
- Record typed sanitized broker error category/phase whenever `error_present=true`.
- Never expose credentials or raw broker-secret payloads.
- Do not let StateTruth alone or BrokerTruth alone grant readiness while they disagree.

Prevention:
- Fail closed on BrokerTruth/StateTruth disagreement.
- Fail closed on direct `error_present=true`.
- Re-run permanent read-only sentinels on every canonical deployment.
- Preserve every recurrence/root-cause/remediation/prevention update in this file only.

## OptionChainTruth — run #79

Sanitized runtime evidence:

- **NIFTY:** 160 contracts / Dhan verified snapshot / READY.
- **BANKNIFTY:** 160 contracts / Dhan verified snapshot / READY.
- **FINNIFTY:** 160 contracts / Dhan verified snapshot / READY.
- **MIDCPNIFTY:** no usable contract rows / `dhan_only_no_rows` / NOT READY.
- Required chains ready: **3/4**.
- `all_required_chains_ready=false`.

MIDCPNIFTY remains the sole strict OptionChainTruth blocker. The empty result is observed evidence, not a proven upstream cause.

## ScannerTruth — run #79

- Read-only scanner proof did not achieve accepted deterministic readiness in the canonical checkpoint.
- Previous attempt timed out around 30 seconds.
- No broker order path was called.
- Scanner readiness remains **NOT READY / UNCONFIRMED**.

## Dhan rotator / Scheduler

Run #79:
- Explicit token-rotator execution `genesis-system3-dhan-token-rotate-pb9bh`: **SUCCESS**.
- Rotator service account: `genesis-system3-dhan-rotator@system3-openalgo-safe.iam.gserviceaccount.com`.
- Scheduler: **ENABLED**.
- Schedule: `30 7 * * *`.
- Timezone: `Asia/Kolkata`.
- Scheduler service account: `gs3-scheduler@system3-openalgo-safe.iam.gserviceaccount.com`.
- LIVE/order flags remain OFF.
- Secret payload exposure: none.

Historical rotator failures remain historical evidence only; do not re-attribute them without exact typed logs.

## Current blockers

1. **BrokerTruth:** later run #79 sanitized sample is disconnected and reports an error despite an earlier bounded-retry broker gate passing.
2. **BrokerTruth vs StateTruth:** same-window convergence is not proven.
3. **MIDCPNIFTY OptionChainTruth:** no usable contracts / not ready.
4. **ScannerTruth:** deterministic read-only readiness remains unconfirmed.
5. **Operational readiness:** `DEPLOYMENT_LOCKED`; production/live-readiness claims remain prohibited until strict blockers close reproducibly.

UI/dashboard automated proof is **not** an active blocker: exact run #79 achieved 22/22 tabs and 44/44 screenshots.

## Safety authority

- LIVE: **OFF / LOCKED**.
- Real order actions: **0**.
- Public dashboard: credential-free and read-only.
- No gate has been weakened.
- No secret payload values are recorded here.
