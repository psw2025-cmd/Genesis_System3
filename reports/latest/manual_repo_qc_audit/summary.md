# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-12 14:00 IST control loop`

> Single authority for `psw2025-cmd/Genesis_System3`. Google Cloud is the only runtime/deployment authority. LIVE remains OFF/LOCKED. No live order placement/modification/cancellation/routing is permitted. Secret payloads must never be exposed. Source, CI, Ready state, screenshots, and runtime health are separate evidence domains; none alone implies real-money readiness.

## 0. Exact revision truth

- Repository: **`psw2025-cmd/Genesis_System3` only**.
- Application/source `main` immediately before this report-only update: **`9e2ce91683f9fc9ac96a85b116451158c89d6159`** — merge PR #138.
- PR #136 source `1dd52f9c064fd35849a41c7176611ee315ecaba6` added fail-closed serial retry for timed-out UI proof tabs.
- PR #138 added a non-executable `deploy/gcp/**` proof contract solely to trigger exact runtime verification of the merged retry logic; no application/order/LIVE behavior changed.
- Last fully finalized serving evidence before run #73: source **`c9fdf17b9c840bd41848a24cffc8ebbd1d74215e`**, revision **`genesis-system3-web-00236-piz`**, 100% traffic, immutable digest `sha256:0944e48e912b30003bb14bc8efd43a258555c2b336023d7113b727d5dd11dae2`, source/deployment match=true.
- Current exact Cloud Run Auto Deploy run **`31579942785` / run #73** targets source `9e2ce916...`. At this update its guarded deployment step is **PASS** and the all-tab public-dashboard browser proof is **IN_PROGRESS**. Do not claim the final serving revision for `9e2ce916...` until run #73 evidence is finalized.
- Runtime posture: **ANALYZER/PAPER**.
- LIVE: **OFF / LOCKED**.
- Real orders attempted by this control loop: **0**.
- Dashboard contract: **public/read-only**, no dashboard API-key/login authority.

## 1. Mandatory control-loop position

`VERIFY -> ROOT CAUSE -> PATCH -> TEST -> PR -> CI -> MERGE -> EXACT DEPLOY -> RUNTIME PROOF -> EVIDENCE -> CLOSE/NEXT`

**Current primary position: STEP 14/15 — exact deployment/runtime proof.**

Run #73 results so far:
- keyless WIF authentication: PASS;
- static safety/syntax: PASS;
- worker Secret Manager prerequisite: PASS;
- Firestore runtime preflight: PASS;
- frontend production build: PASS;
- required GCP identities/resources: PASS;
- guarded Cloud Run deployment: **PASS**;
- 22-tab public-dashboard browser proof: **IN_PROGRESS**;
- MutationPolicy runtime proof: pending behind visual proof;
- isolated Dhan rotator/Scheduler configuration: pending behind visual proof;
- rotator execution and broker recovery re-proof: pending;
- final sanitized runtime/provenance lock: pending.

**USER ACTION REQUIRED=NO.** Current work is assistant/repository/runtime controlled.

## 2. Firestore and deployment truth

- Human Step-13 Firestore grant was completed previously for `genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com`.
- Earlier Firestore `403 Missing or insufficient permissions` is **RESOLVED for current deployment lineage**: later candidates became Ready and current guarded deployments pass the Firestore-backed startup path.
- Earlier tag-vs-digest verifier failure is also **RESOLVED**. Current DeploymentTruth compares immutable Artifact Registry provenance correctly enough for source `c9fdf17...` to reach 100% serving traffic.
- Remaining DeploymentTruth work: finish run #73; permanently include the UI proof script itself in deployment trigger coverage; keep source -> image digest -> candidate -> readiness -> 100% traffic -> browser/runtime evidence bound to the same SHA.

## 3. Broker / Dhan truth

Latest authoritative sanitized runtime artifact from run #72 proves:
- broker: **Dhan**;
- `/api/broker/status`: HTTP 200;
- connected: **true**;
- error present: false;
- token source: **`GCP_SECRET_MANAGER_DYNAMIC`**;
- Secret Manager access-token version: **76**;
- token value exposed: false;
- broker latency field: ~36 ms;
- `/api/health`: HTTP 200, status=`ok`, mode=`PAPER`;
- `/api/state`: broker_connected=true, data_source=`BROKER_LIVE`, positions_count=0;
- LIVE trading enabled=false;
- order placement allowed=false.

Therefore the earlier version-49 `TOKEN_EXPIRED_OR_INVALID` incident is historical, not current broker truth.

Broker infrastructure remains **PARTIAL**:
- exact dedicated rotator runtime identity still needs current-run proof;
- Scheduler metadata/configuration still needs current-run proof;
- previous job execution evidence showed legacy web-runtime invocation/identity drift;
- dedicated intended identities remain `genesis-system3-dhan-rotator@...` and `gs3-scheduler@...`;
- after dedicated rotator is proven, remove obsolete web-runtime PIN/TOTP/token-version-add authority and re-prove least privilege.

## 4. Market-data truth

Current broker connection does **not** imply market-data closure.

Run #72 option-chain evidence for NIFTY, BANKNIFTY, FINNIFTY and MIDCPNIFTY:
- HTTP 200 for each;
- spot available;
- source=`dhan`;
- source_priority=`dhan_only_no_rows`;
- contract count/fetched-at proof unavailable;
- latency about **25.3 s per chain**;
- `all_required_chains_ready=false`.

`/api/scanner/top_contract_gainers` also reached approximately 30 s timeout in the proof environment. This is an active P1 data/latency defect and explains several heavy UI render/capture delays. Do not default no-row chains green.

## 5. 22-tab UI proof matrix

Canonical tabs: **22**. Final review contract: **22 desktop + 22 mobile = 44 exact serving-revision screenshots**.

Run #72 baseline:
- 18/22 tabs PASS browser/render proof;
- 36 screenshots produced;
- 4 tabs failed only at browser subprocess timeout: **Truth Control, E2E Proof, Signals, Trade**;
- no broker/order/paper mutation calls by proof harness;
- no dashboard API-key/login prompt detected in passing visuals.

PR #136 retry contract:
- initial 3-worker pass retained;
- only failed tabs retry once, serially;
- retry timeout 70 seconds;
- still fail-closed if a retry fails;
- exact four-tab timeout pattern covered by regression tests.

Run #73 is currently executing this retry contract. Final 22/22 result is **NOT YET PROVEN** at this report update.

### Product-quality findings independent of screenshot PASS

- Desktop is functional but several workspaces remain overly dense and inconsistent in hierarchy.
- Mobile is **NOT FINAL**: current 190px desktop sidebar consumes too much of a 430px viewport and visibly cramps/clips workspaces.
- Signals and Trade still contain stale auth-era fallback wording in source. Final public-readonly UI must show contract drift/error, never ask for an API key.
- Truth/E2E/Signals/Trade are read-heavy and affected by slow chain/scanner endpoints; UI must surface typed pending/stale/error states rather than appear frozen.

Draft PR **#139** (`feat/ui-mobile-shell-review`) is isolated and CI-green but intentionally unmerged. It changes the mobile navigation to a 58px accessible icon rail while retaining all 22 `aria-label`/title navigation targets. It must be reviewed against exact deployed screenshots before merge/finalization.

No tab is `UI FINAL` until it has: exact serving desktop proof + mobile proof + data/backend truth + no credential prompt + acceptable responsive layout + user review.

## 6. MutationPolicy / P0 chain

| Dependency | Truth | Required next evidence |
|---|---|---|
| Firestore runtime authorization | VERIFIED for current lineage | preserve |
| exact current deploy | IN PROGRESS run #73 | finalized serving revision + source/digest evidence |
| public no-key dashboard | VERIFIED architecture; exact run #73 pending | all-tab exact-serving proof |
| MutationPolicy | source/CI partial | run #73 runtime capability proof |
| SafetyTruth + ExecutionEligibility | OPEN P0 | MutationPolicy runtime closure |
| PreTradeRiskService | OPEN P0 | SafetyTruth closure |
| AccountTruth / SnapshotCoordinator | OPEN P0-P1 | prior P0 gates |
| durable PaperLedger / Reconciliation | PARTIAL | lifecycle + reconciliation truth |
| StateTruth/domain CAS | PARTIAL/OPEN | domain version/CAS authority |
| DeploymentTruth V2 | PARTIAL | run #73 full chain + trigger cleanup |
| WorkCoordinator/idempotency | OPEN | prior gates |
| OptionChainTruth -> StreamTruth -> ScannerTruth -> PredictionTruth | OPEN P1 | after P0 ordering |
| Real-money readiness | **NO** | multiple mandatory gates open; LIVE remains locked |

## 7. AlphaTruth

Quantitative targets remain **goals only**, never current claims.

Current authoritative small evidence remains insufficient: 5 days / 8 trades / 50% win rate / net P&L `-102636.35`. **AlphaTruth=`INSUFFICIENT_EVIDENCE`**.

Historical large frozen holdout also failed performance: negative Sharpe, high drawdown and negative compounded return. No model promotion is allowed. Continuous-learning/retraining may create isolated research challengers only; it may never silently promote a model or increase live risk.

## 8. OperationsTruth / observability

- PR #125 OperationsTruth/SRE foundation: historically CI-green but stale relative to current main; **do not merge wholesale**. Refresh/reimplement on current main after immediate runtime gate.
- PR #121 observability foundation: historically CI-verified but stale; **do not merge wholesale**. Selectively rebase/reimplement request/trace correlation, redacted synthetic evidence, uptime checks and runbooks after current deployment gate.
- SLO goals (99.95% availability, API P95 <300ms, broker/synthetic success targets, MTTR trends) remain **NOT_PROVEN** until sufficient measured windows exist.

## 9. Open-branch hygiene / salvage

- Duplicate runtime-trigger PR #137 was closed as **SUPERSEDED** by merged PR #138.
- PR #139 is DRAFT/hold for mobile UI review.
- Old high-risk auth PRs #129/#131 are stale/diverged; never merge wholesale. Compare safe slices against current serving public-readonly implementation first.
- `conflict_120826_0310` remains quarantined/selective salvage only; never wholesale merge. Its committed credential incident remains exposed until independent rotation proof; never quote the credential.

## 10. Current checkpoint

- Application/source before this report update: **`9e2ce91683f9fc9ac96a85b116451158c89d6159`**.
- Last fully finalized serving source: **`c9fdf17b9c840bd41848a24cffc8ebbd1d74215e`**, revision `genesis-system3-web-00236-piz`, 100% traffic.
- Current Cloud Run proof: run **`31579942785`**; deployment PASS; 22-tab visual step IN_PROGRESS.
- Broker: **CONNECTED** on last authoritative evidence, token version 76, LIVE/order false.
- Required chains: **NOT READY** (Dhan no-row + ~25 s latency evidence).
- UI baseline: **18/22 tab render PASS; 4 timeout; mobile quality BLOCKED**.
- Draft mobile improvement PR #139: CI green / NOT MERGED.
- AlphaTruth: INSUFFICIENT_EVIDENCE.
- SRE/observability: partial/stale branches, not current runtime authority.
- **USER ACTION REQUIRED=NO.** Continue run #73 -> 22/22 evidence -> MutationPolicy -> dedicated rotator/Scheduler -> broker re-proof -> master update -> next strict P0 dependency.
