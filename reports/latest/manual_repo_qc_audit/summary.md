# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-12 07:08 IST`

> Single authority for the current `psw2025-cmd/Genesis_System3` remediation stream. `PATCHED`, `MERGED`, CI green, `Ready`, or latest revision never means `CLOSED`; closure requires exact serving-revision reproducible evidence. Google Cloud is the only runtime/deployment authority. LIVE remains OFF/LOCKED.

## 0. Scope, exact revision truth and safety lock

- Repository authority: **`psw2025-cmd/Genesis_System3` only**.
- Application/source SHA currently under deployment proof: **`05becfbde0d8967b0cc6e3b556493f99d89f726a`** — merge PR #127.
- PR #127 corrected the invalid long Scheduler service-account ID to the actually provisioned **`gs3-scheduler@system3-openalgo-safe.iam.gserviceaccount.com`**.
- This audit update is documentation-only and must not be treated as a new application deployment candidate.
- Runtime posture: **ANALYZER/PAPER**.
- LIVE: **OFF / LOCKED**.
- Real broker orders enabled/placed/modified/cancelled/routed by this remediation stream: **0**.
- Dashboard contract: **public/read-only PAPER**; no dashboard API-key/login UI is authorized.
- Secret payload access/exposure is prohibited. Canonical broker token authority remains **`gcp-secret-manager-dynamic`**.

## 1. Mandatory control-loop position

`1 VERIFY -> 2 SELECT -> 3 ROOT CAUSE -> 4 DESIGN -> 5 PATCH -> 6 TEST -> 7 PR -> 8 CI -> 9 FIX/RETEST -> 10 MERGE -> 11 POST-MERGE VERIFY -> 12 PREP -> 13 USER GCP ONLY IF GENUINELY REQUIRED -> 14 DEPLOY VERIFY -> 15 RUNTIME TEST -> 16 USER DHAN/PIN/TOTP/OAuth ONLY IF GENUINELY REQUIRED -> 17 FULL EVIDENCE -> 18 CLOSED`

### Current production position

**STEP 14/15 IN PROGRESS for source `05becfbd...`; no new human action is currently justified while exact deployment run `31554081423` is still executing.**

Current exact run state at this audit update:
- Checkout: PASS.
- WIF keyless authentication: PASS.
- Static safety/syntax: PASS.
- worker Secret Manager metadata/existence prerequisite: PASS.
- Firestore runtime preflight: PASS.
- frontend production build: PASS.
- required GCP API/service-account preflight: PASS, including the corrected `gs3-scheduler` identity.
- guarded Cloud Run candidate deployment: **IN_PROGRESS**.
- public `/ui` visual proof: pending.
- MutationPolicy runtime proof: pending.
- isolated Dhan rotator/Scheduler configuration: pending.
- token rotator execution: pending.
- broker recovery proof: pending.
- exact runtime evidence/provenance lock: pending.

Because candidate deployment is still running, serving traffic, candidate readiness, broker token recovery and MutationPolicy closure are **NOT YET PROVEN for `05becfbd...`**. No manual traffic shift is allowed.

## 2. Current executive truth table

| Area | Current truth | Exact evidence / next condition |
|---|---|---|
| PAPER dashboard no-key viewing | **VERIFIED/CLOSED for stated viewing requirement** | Earlier real Cloud Run `/ui` proof passed; LoginPage/useAuth removed and AuthUnlock is passive only |
| Current source deployment | **IN_PROGRESS / NOT CLOSED** | run `31554081423`, source `05becfbd...`; candidate deployment step running |
| Firestore Step-13 boundary | **HUMAN ACTION PREVIOUSLY COMPLETED; runtime re-proof pending** | current deploy Firestore preflight PASS; candidate must prove required shared state before closure |
| MutationPolicy | **PARTIAL / CI VERIFIED / RUNTIME PENDING** | exact runtime denial/allow matrix has not run yet for `05becfbd...` |
| Dhan rotator identity separation | **MERGED / GCP BOOTSTRAP PARTIAL-PROVEN / RUNTIME PENDING** | dedicated rotator exists; valid Scheduler identity is `gs3-scheduler`; deploy runtime proof pending |
| Broker token truth | **LAST PROVEN FAILURE: TOKEN_EXPIRED_OR_INVALID** | previous serving endpoint rejected Secret Manager version 49 although metadata time-expiry had not elapsed; new-version recovery pending rotator execution |
| SafetyTruth / ExecutionEligibility | **OPEN P0** | do not advance until MutationPolicy runtime closure |
| PreTradeRiskService | **OPEN P0** | blocked by SafetyTruth dependency |
| AccountTruth / AccountSnapshotCoordinator | **OPEN P0-P1** | not authoritative yet |
| durable PaperLedger / Reconciliation | **PARTIAL / OPEN P0** | durable lifecycle/reconciliation closure pending |
| StateTruth / domain CAS | **OPEN P0-P1** | Firestore required; domain version/CAS authority incomplete |
| DeploymentTruth V2 | **PARTIAL / OPEN P0** | source->build->digest->candidate->serving traffic proof incomplete |
| WorkCoordinator / idempotency | **OPEN P0-P1** | pending |
| OptionChainTruth -> StreamTruth -> ScannerTruth -> PredictionTruth | **OPEN P1** | strictly after P0 chain |
| Institutional UI/A11Y | **OPEN P1** | responsive, keyboard, axe, console and full tab proof incomplete |
| Profitability | **NOT PROVEN** | no evidence permits profitability claim |
| Real-money readiness | **NO** | LIVE OFF/LOCKED; multiple P0 gates remain open |

## 3. Recent merged source authority

- PR #122 `feat(quant): add fail-closed AlphaTruth evaluator` — merged. Alpha goals are gates only, never claims; auto-promotion/live/order authority remain false.
- PR #123 `fix(gcp): isolate Dhan rotator and scheduler identities` — merged. Dedicated rotator/Scheduler architecture is source authority; zero order endpoint token algorithm retained.
- PR #124 `fix(gcp): stop Secret Manager static guard self-match` — merged. Static least-privilege guard remains hard-fail for real privilege grants.
- PR #126 `feat(ui): show Dhan token and connection truth in System workspace` — merged. UI reads existing broker truth only; no token writer or new order/live path.
- PR #127 `fix(gcp): use valid short scheduler service account` — merged as application/source **`05becfbde0d8967b0cc6e3b556493f99d89f726a`**. Exact-head required suites passed before merge.

Open lanes, not `main` runtime authority:
- PR #121 observability head `01fe0232ca03f2a46eb1ec92c5a9f5b2ca04e998` — read-only traced monitoring foundation; not merged/runtime-verified.
- PR #125 OperationsTruth head `e6926287a62e1bf4d6fcf55e2b700de0feeed037` — Workflow Priority Guard PASS and Genesis Global Safety CI PASS; still open/not runtime authority.

## 4. Broker / identity incident truth

Previous authoritative public broker proof showed:
- broker=`dhan`;
- mode=`ANALYZER`;
- connected=`false`;
- live_trading_enabled=`false`;
- order_placement_allowed=`false`;
- error=`TOKEN_EXPIRED_OR_INVALID`;
- token source=`GCP_SECRET_MANAGER_DYNAMIC`;
- Secret Manager version=`49`;
- raw token exposed=`false`;
- reload of the same Secret Manager version could not repair broker rejection.

GCP human bootstrap subsequently proved:
- `genesis-system3-dhan-rotator@system3-openalgo-safe.iam.gserviceaccount.com` exists;
- `gs3-scheduler@system3-openalgo-safe.iam.gserviceaccount.com` exists;
- deployer has `roles/iam.serviceAccountUser` on both;
- rotator has read access on Dhan client/access-token/PIN/TOTP secrets;
- rotator has `secretVersionAdder` on `dhan-access-token`;
- valid Scheduler account name is **`gs3-scheduler`** because the old long ID exceeded Google Cloud service-account ID limits.

Residual IAM cleanup from human snapshot remains **OPEN**: legacy `genesis-system3-web` bindings appeared to include PIN/TOTP access and token-version-add authority. Do not remove them until the dedicated rotator has been runtime-proven to mint a new token and recover broker reads. After successful rotator proof, least-privilege cleanup must remove obsolete web token-mint/PIN/TOTP authority and re-prove broker recovery.

Google Auth Platform branding/OAuth application setup is **NOT CONFIGURED** (App name not completed). It is **NOT REQUIRED for the current public PAPER dashboard** and must not block the current no-key runtime path. If a future feature genuinely requires Google OAuth, it becomes a Step-16 human authentication boundary.

## 5. AlphaTruth / quantitative research truth

Goals only, never current claims:
- OOS directional accuracy >65%;
- top-decile directional precision >70%;
- Sharpe >=2.5;
- Sortino >=3.5;
- max drawdown <=10%;
- average-win/average-loss magnitude >2.0;
- aligned after-cost benchmark outperformance;
- IS/OOS accuracy gap <=15 percentage points.

Current authoritative small costed walk-forward evidence remains:
- 5 days;
- 8 trades;
- 4 wins / 4 losses;
- win rate 50%;
- total gross P&L `-101258.25`;
- costs `1378.10`;
- total net P&L `-102636.35`.

**AlphaTruth state: `INSUFFICIENT_EVIDENCE`.** Mechanics proof is not performance proof. No new frozen-OOS tuning is authorized merely to improve the result.

Historical strongest frozen evidence remains rejected: 489 filled trades / 492 holdout days, Sharpe `-1.3979`, Sortino `-3.4160`, maximum drawdown `52.3395%`, compounded return `-46.7306%`, promotion=false.

Research governance remains fail-closed:
- source/data/feature/model hashes required;
- chronological train/validation/frozen-test separation required;
- explicit label horizon + purge/gap required;
- preprocessing train-only;
- aligned costs/benchmark required;
- minimum OOS observations/days required;
- declared trial count + selection-bias control required;
- maximum five self-correction attempts per lineage;
- failed trials preserved;
- `git reset --hard` on shared/main history prohibited;
- even `PROVEN` => model_auto_promotion=false, live=false, real_order_authority=false.

Factor/model decay trigger: **NOT_PROVEN / NOT_EVALUABLE** because current authoritative evidence is insufficient for a predeclared rolling decay estimate. No silent retraining or promotion.

## 6. OperationsTruth / SRETruth

PR #125 implements the typed Phase-1/SLO foundation but is still open. Current state:
- OperationsTruth code: **CI PASS / NOT MERGED**.
- Authoritative runtime inventory: **NOT_PROVEN** for the new typed collector until merged and run with read-only GCP authority.
- SLO scorecard: **NOT_PROVEN**. Missing observations never default green.

SLO targets, not claims:
- availability >=99.95%;
- successful-request API P95 <300 ms;
- broker read success >=99.9%;
- token rotation success =100%;
- synthetic success >=99.9%;
- MTTR decreasing;
- false-alert rate decreasing;
- automated recovery rate increasing.

Required scoring remains `PASS/FAIL/NOT_PROVEN` with source, observed_at, sample count and predeclared window. Baseline SLO proof alone cannot close the nine-phase SRE program.

Observability PR #121 remains open. Its read-only design includes request/trace IDs, W3C `traceparent`, redacted browser synthetic evidence, uptime checks and runbooks; no login/API key, broker order probe, PIN/TOTP, secret payload or LIVE authority.

Current incident classification: **deployment/broker-token recovery incident — active, remediation attempt in progress**. Deterministic remediation has not exceeded the two-attempt escalation budget in this current valid-identity lineage. No safety gate has been weakened.

## 7. Parallel `conflict_120826_0310` salvage lane

Latest authoritative Git comparison: **diverged**.
- current `main` is **172 commits ahead** of `conflict_120826_0310`;
- conflict branch is **6 commits ahead** of `main`;
- merge base `5d1ec87a43c5778f6d010b91dc3adcd6a22ae797`.

Therefore wholesale merge/rebase-overwrite remains **REJECTED**.

Selective classifications:
- connection-stability concepts: **ADAPT**;
- broker token-health UI/read model: **ADAPT**; useful truth UI has already been selectively reimplemented on current main via PR #126;
- real-data multibagger research UI/engine: **ADAPT after P0**;
- F&O eligibility/health digest: **ADAPT after truth-contract review**;
- branch token mint/persist writer: **REJECT**;
- LoginPage/AuthGate/dashboard API-key restoration: **REJECT**;
- `.emergent` webhook cron/runtime authority: **REJECT**;
- Render/local runtime authority: **REJECT**;
- generated reports/dist as source authority: **REJECT**.

`memory/test_credentials.md` remains a credential-exposure incident. Never quote/merge its value. Exposure remains open until independent credential/token rotation is proven. Do not force-rewrite shared history without explicit authorization.

## 8. P0 dependency order — immutable until closure

1. Current exact deployment + MutationPolicy runtime closure.
2. SafetyTruth + ExecutionEligibility.
3. PreTradeRiskService.
4. AccountTruth + AccountSnapshotCoordinator.
5. durable PaperLedger + ReconciliationService.
6. StateTruth + domain CAS/version authority.
7. DeploymentTruth V2: source SHA -> build ID -> immutable image digest -> zero-traffic candidate -> readiness/synthetic -> exact 100% serving revision/traffic.
8. WorkCoordinator/idempotency.
9. P1 OptionChainTruth -> StreamTruth -> ScannerTruth -> PredictionTruth + AlphaTruth -> institutional UI/A11Y/observability.

Do not advance while the current dependency is FAIL/UNKNOWN/STALE/UNPROVEN/PARTIAL.

## 9. Current end-of-run checkpoint

- Exact application/source SHA: **`05becfbde0d8967b0cc6e3b556493f99d89f726a`**.
- Current primary P0 step: **Step 14/15 exact deployment/runtime proof in progress; MutationPolicy remains the next closure gate**.
- PR/CI/runtime: PR #127 merged after exact-head required CI PASS; post-merge Cloud Run run `31554081423` has passed all pre-candidate gates and is currently executing guarded candidate deployment.
- AlphaTruth: **`INSUFFICIENT_EVIDENCE`**; sample 8 trades / 5 days / 50% win / net `-102636.35`.
- OperationsTruth inventory: **NOT_PROVEN runtime**; PR #125 implementation CI PASS but not merged.
- SLO scorecard: **NOT_PROVEN**; no default-green metrics.
- Incident/remediation/escalation: active deployment/broker-token recovery; bounded remediation in progress; escalation not yet triggered.
- Factor-decay trigger: **NOT_PROVEN / no RESEARCH_REQUIRED trigger**.
- Observability: PR #121 open, CI-verified design, not merged/runtime authority.
- Dhan identity: source separation merged; dedicated rotator + `gs3-scheduler` human bootstrap proven; runtime identity proof pending exact deploy.
- Broker token: last proven state `TOKEN_EXPIRED_OR_INVALID`, Secret Manager version 49; recovery/version advancement not yet proven.
- Salvage divergence: `main` +172 / conflict branch +6; selective salvage only.
- What remains before another human action: finish current exact deployment, candidate readiness, `/ui` proof, MutationPolicy proof, isolated rotator/Scheduler config, token rotation and read-only broker recovery. Only then determine whether Step-16 Dhan/PIN/TOTP/OAuth human authentication is genuinely necessary.
- **USER ACTION REQUIRED=NO at this checkpoint.** Exact reason: current assistant-owned post-merge deployment/runtime proof is still in progress; requesting another human action before its deterministic result would violate the mandatory control loop.
