# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-12` — current audit turn

> Single authority for `psw2025-cmd/Genesis_System3`. Google Cloud is the only runtime/deployment authority. `PATCHED`, `MERGED`, CI green, Cloud Run `Ready`, source-only UI, or a generated concept never means `CLOSED`. Closure requires exact serving-revision reproducible evidence. LIVE remains OFF/LOCKED. No live order placement/modification/cancellation/routing is permitted.

## 0. Exact revision and safety truth

- Repository: **`psw2025-cmd/Genesis_System3` only**.
- Latest application/source merge under runtime remediation: **`05becfbde0d8967b0cc6e3b556493f99d89f726a`** — PR #127.
- Latest `main` also contains report-only commits; report commits are not application deployment candidates.
- Runtime posture: **ANALYZER/PAPER**.
- LIVE: **OFF / LOCKED**.
- Real orders attempted by this remediation stream: **0**.
- Dashboard viewing: **public/read-only PAPER**, no dashboard API key/login UI.
- Canonical Dhan token authority: **`gcp-secret-manager-dynamic`**; secret payload exposure is prohibited.
- Google OAuth branding: **NOT CONFIGURED / NOT REQUIRED for current public PAPER UI**.

## 1. Mandatory control-loop position

`1 VERIFY -> 2 SELECT -> 3 ROOT CAUSE -> 4 DESIGN -> 5 PATCH -> 6 TEST -> 7 PR -> 8 CI -> 9 FIX/RETEST -> 10 MERGE -> 11 POST-MERGE VERIFY -> 12 PREP -> 13 USER GCP ONLY IF GENUINELY REQUIRED -> 14 DEPLOY VERIFY -> 15 RUNTIME TEST -> 16 USER DHAN/PIN/TOTP/OAuth ONLY IF GENUINELY REQUIRED -> 17 FULL EVIDENCE -> 18 CLOSED`

### Current primary P0 position

**STAY ON STEP 13/14/15 — exact current candidate startup is blocked by PROVEN Firestore IAM denial.**

Exact Cloud Run Auto Deploy run: **`31554081423`**, source `05becfbd...`.

Proven results:
- checkout: PASS;
- keyless WIF authentication: PASS;
- static safety/trading guards: PASS;
- worker-secret existence: PASS;
- non-admin Firestore identity preflight: PASS;
- frontend production build: PASS;
- GCP API and service-account existence preflight: PASS, including `gs3-scheduler`;
- Cloud Build: PASS, build ID `668bd1ce-4c74-41f9-b240-03f200eb638c`;
- candidate revision created: **`genesis-system3-web-00213-baq`**;
- candidate traffic: **0%**;
- existing production revision **`genesis-system3-web-00199-tq5` remains 100%**;
- candidate log proved `[cloud-start] binding 0.0.0.0:8080`;
- Firestore read then failed with **`403 Missing or insufficient permissions`**;
- application terminated with **`RuntimeError: Required Firestore state load failed`**;
- Cloud Run startup probe failure is therefore a consequence, not the root cause;
- public `/ui` current-source screenshot proof: SKIPPED;
- MutationPolicy current-source runtime proof: SKIPPED;
- dedicated rotator deployment/execution: SKIPPED;
- Dhan recovery: SKIPPED;
- exact-SHA `cloud-run/runtime-proof`: FAIL;
- production traffic remained protected.

### Genuine current Step-13 action

The dedicated web runtime must receive the Firestore data role required by the fail-closed state backend:

```bash
gcloud projects add-iam-policy-binding system3-openalgo-safe \
  --member="serviceAccount:genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com" \
  --role="roles/datastore.user" \
  --condition=None
```

After proof of that binding, assistant-owned remediation resumes immediately: redeploy -> candidate startup -> exact serving proof -> no-key UI -> 22-tab visual matrix -> MutationPolicy runtime -> dedicated Dhan rotator -> token version advancement -> read-only Dhan recovery -> scheduler identity proof -> next P0 dependency.

## 2. Dhan broker and identity truth

Last authoritative public broker proof:
- broker: `dhan`;
- mode: `ANALYZER`;
- connected: **false**;
- error: **`TOKEN_EXPIRED_OR_INVALID`**;
- credentials/client/access-token present: true;
- token source: `GCP_SECRET_MANAGER_DYNAMIC`;
- Secret Manager version: **49**;
- nominal metadata expiry was still approximately 23 hours ahead at observation time;
- raw token exposed: false;
- live trading enabled: false;
- order placement allowed: false;
- repeated reload of the same version did not recover Dhan authentication.

Human bootstrap proved:
- `genesis-system3-dhan-rotator@system3-openalgo-safe.iam.gserviceaccount.com` exists;
- valid Scheduler identity is **`gs3-scheduler@system3-openalgo-safe.iam.gserviceaccount.com`**;
- deployment identity may attach those identities;
- rotator can read only required Dhan token-mint secrets and add a version to `dhan-access-token`;
- PR #127 corrected repository references from the invalid over-length Scheduler ID to `gs3-scheduler` and passed exact-head CI before merge.

Residual least-privilege cleanup remains **OPEN**: human IAM output showed historical `genesis-system3-web` access to PIN/TOTP and token-version-add. Do not remove those legacy bindings until the dedicated rotator is runtime-proven to mint a new version and recover read-only Dhan access; then remove obsolete web mint/PIN/TOTP authority and re-prove.

## 3. Mandatory UI Proof Matrix — 22 tabs

### UI closure rule

Every current sidebar tab must have all of the following before it can be marked `FINAL`:
1. source implementation reviewed;
2. backend/data contract identified;
3. no placeholder/fake/default-green production truth;
4. exact serving-revision **desktop screenshot**;
5. exact serving-revision **mobile screenshot**;
6. console/render/navigation proof;
7. API-key/login absence proof for public PAPER mode;
8. feature-specific functional proof;
9. blockers recorded;
10. **USER REVIEW = ACCEPTED**.

`SOURCE READY` is not `DEPLOYED`. `DEPLOYED` is not `FUNCTIONALLY VERIFIED`. A generated concept image is `TARGET/CONCEPT`, never runtime proof.

### PR #128 — all-tab visual evidence harness

Open PR **#128 — `feat(ui-proof): capture every dashboard tab for review`**.

Current implementation contract:
- canonical sidebar registry: **22 tabs exactly**;
- deterministic safe `?tab=<id>` review links;
- proof binds to the **actual single 100%-traffic serving revision**, not `latestReadyRevisionName` or a 0%-traffic candidate;
- exact `DEPLOY_GIT_SHA` must match the commit being proved;
- headless-Chrome actual product render;
- **22 desktop screenshots at 1600x1000**;
- **22 mobile screenshots at 430x932**;
- total planned visual set: **44 screenshots per exact successful deployment**;
- screenshot SHA-256 recorded;
- each tab must prove it became active (`aria-current=page`);
- dashboard API-key/login prompt must be absent;
- per-tab review state starts `PENDING_USER_REVIEW`;
- no order/paper mutation endpoint is called;
- LIVE remains OFF/LOCKED.

PR #128 current state: **OPEN / CI IN PROGRESS / NOT MERGED / NOT RUNTIME AUTHORITY**.

### Per-tab progress matrix

| # | Tab | Source | Main functional dependency | Exact-current visual | Current review status |
|---|---|---|---|---|---|
| 1 | Decision Intel | PRESENT | Scanner/Prediction/Safety truth | **PENDING DEPLOY** | PENDING USER REVIEW |
| 2 | Truth Control | PRESENT | SystemTruth/typed gates | **PENDING DEPLOY** | PENDING USER REVIEW |
| 3 | Genesis Brain | PRESENT | AI provenance/PredictionTruth | **PENDING DEPLOY** | PENDING USER REVIEW |
| 4 | E2E Proof | PRESENT | exact deployment/runtime evidence | **PENDING DEPLOY** | PENDING USER REVIEW |
| 5 | Overview | PRESENT | broker/market/paper/account truth | **PENDING DEPLOY** | PENDING USER REVIEW |
| 6 | Sim Live | PRESENT | simulation truth only; no live authority | **PENDING DEPLOY** | PENDING USER REVIEW |
| 7 | Options Intel | PRESENT | OptionChainTruth/Greeks/freshness | **PENDING DEPLOY** | PENDING USER REVIEW |
| 8 | Option Chain | PRESENT | OptionChainTruth/expiry/IV/Greeks | **PENDING DEPLOY** | PENDING USER REVIEW |
| 9 | Signals | PRESENT | ScannerTruth/PredictionTruth | **PENDING DEPLOY** | PENDING USER REVIEW |
| 10 | Trade | PRESENT | MutationPolicy/SafetyTruth/Risk | **PENDING DEPLOY** | PENDING USER REVIEW; LIVE LOCKED |
| 11 | Paper Trades | PRESENT | durable PaperLedger/Reconciliation | **PENDING DEPLOY** | PENDING USER REVIEW |
| 12 | Positions | PRESENT | Paper/AccountTruth/Reconciliation | **PENDING DEPLOY** | PENDING USER REVIEW |
| 13 | Risk & Scenarios | PRESENT | PreTradeRiskService/SafetyTruth | **PENDING DEPLOY** | PENDING USER REVIEW |
| 14 | Multibagger V4 | PRESENT/PARTIAL | authoritative research data contract | **PENDING DEPLOY** | REQUIRES UPGRADE + USER REVIEW |
| 15 | Prediction Audit | PRESENT | AlphaTruth/PredictionTruth/provenance | **PENDING DEPLOY** | PENDING USER REVIEW |
| 16 | Performance | PRESENT | costed lifecycle/performance truth | **PENDING DEPLOY** | PENDING USER REVIEW |
| 17 | ML Model | PRESENT | AlphaTruth/model lineage/frozen OOS | **PENDING DEPLOY** | PENDING USER REVIEW |
| 18 | Data Integrity | PRESENT | StateTruth/CAS/reconciliation/provenance | **PENDING DEPLOY** | PENDING USER REVIEW |
| 19 | Broker | PRESENT | Dhan AccountTruth/token/connectivity | **PENDING DEPLOY** | BROKER CURRENTLY FAIL + REVIEW PENDING |
| 20 | Alerts | PRESENT | SRETruth/incident/alert sources | **PENDING DEPLOY** | PENDING USER REVIEW |
| 21 | System | **UPDATED IN PR #126** | broker/token/safety/deployment truth | **SOURCE CI PROVEN; DEPLOY PENDING** | PENDING USER REVIEW |
| 22 | Live Gate | PRESENT | SafetyTruth/Risk/Account/Paper/Deployment | **PENDING DEPLOY** | LIVE OFF; PENDING USER REVIEW |

### Current UI reality

The newest System-tab broker/token truth code is merged in source, but **users are still served by old revision `00199-tq5`** because all newer candidates fail before promotion. Therefore no screenshot from the old serving revision may be presented as proof of the newest UI changes.

The next valid screenshot set must come only after the Firestore IAM blocker is resolved and an exact current revision passes guarded deployment.

## 4. UI redesign / institutional workstation status

The user has explicitly rejected treating the old dashboard as final. The UI program therefore remains **OPEN** even after visual proof is automated.

Design goals for every tab:
- institutional trading-workstation hierarchy, not a generic admin dashboard;
- explicit market/session clock and freshness;
- PAPER/ANALYZER/LIVE-OFF status visible and backend-authoritative;
- Dhan/data health with stale/error provenance;
- scanner/ranker/options/Greeks/AI explainability where relevant;
- paper lifecycle, positions, P&L and reconciliation provenance;
- risk gates and blockers before any execution affordance;
- search/filter/drilldown/export where justified;
- loading/empty/stale/error states;
- no dead buttons or hidden handler failures;
- no synthetic/default-green data presented as live;
- responsive desktop/mobile behavior;
- keyboard/focus/accessibility proof;
- observability/trace/evidence links where relevant.

UI review sequence after proof harness deploys:
1. capture all 44 screenshots;
2. inspect each tab individually;
3. classify `KEEP / REDESIGN / CONSOLIDATE / REMOVE / ADD`;
4. show user the exact tab proof;
5. receive user change requests;
6. implement changes on fresh current-main branches;
7. re-run build/CI/deploy/tab proof;
8. only then mark that tab `USER ACCEPTED` and `VISUALLY VERIFIED`.

## 5. P0 dependency truth

| Dependency | Truth | Next closure condition |
|---|---|---|
| public PAPER/no-key viewing | VERIFIED/CLOSED for viewing requirement | preserve contract |
| exact current deployment | **FAIL — Firestore 403** | grant runtime datastore role, redeploy |
| MutationPolicy | PARTIAL / CI VERIFIED / RUNTIME NOT RUN | exact deployment first |
| SafetyTruth + ExecutionEligibility | OPEN P0 | after MutationPolicy runtime |
| PreTradeRiskService | OPEN P0 | after SafetyTruth |
| AccountTruth + AccountSnapshotCoordinator | OPEN P0-P1 | after prior P0 gates |
| durable PaperLedger + Reconciliation | PARTIAL / OPEN P0 | lifecycle/reconciliation closure |
| StateTruth/domain CAS | OPEN P0-P1 | Firestore + version/CAS authority |
| DeploymentTruth V2 | PARTIAL / OPEN P0 | source/build/digest/revision/traffic binding |
| WorkCoordinator/idempotency | OPEN P0-P1 | pending |
| OptionChainTruth -> StreamTruth -> ScannerTruth -> PredictionTruth | OPEN P1 | after P0 |
| Institutional UI/A11Y | OPEN | 22-tab functional + visual + user review required |
| Real-money readiness | **NO** | multiple P0/P1 gates open; LIVE locked |

## 6. AlphaTruth / quantitative research truth

Targets are acceptance goals only: OOS directional accuracy >65%, top-decile precision >70%, Sharpe >=2.5, Sortino >=3.5, maximum drawdown <=10%, average-win/average-loss magnitude >2.0, aligned after-cost benchmark outperformance, IS/OOS accuracy gap <=15 percentage points.

Current authoritative small costed evidence:
- 5 days;
- 8 trades;
- 4 wins / 4 losses;
- win rate 50%;
- gross P&L `-101258.25`;
- costs `1378.10`;
- net P&L **`-102636.35`**.

**AlphaTruth = `INSUFFICIENT_EVIDENCE`.** Mechanics PASS is not performance PASS. No profitability or auto-promotion claim is allowed.

Historical strongest frozen research evidence remains rejected: 489 fills / 492 holdout days; Sharpe `-1.3979`; Sortino `-3.4160`; MDD `52.3395%`; compounded return `-46.7306%`; promotion=false.

## 7. OperationsTruth / observability

- PR #121 observability: open, prior exact-head CI green, not merged/runtime authority. Read-only trace IDs, W3C traceparent, redacted browser evidence, uptime checks and runbooks; no broker order probe or secret payload.
- PR #125 OperationsTruth/SRETruth: open, prior CI green, not runtime authority.
- SLO targets remain **NOT_PROVEN** until minimum sample/window evidence exists: availability >=99.95%, successful API P95 <300 ms, broker read success >=99.9%, token rotation success 100%, synthetic success >=99.9%, MTTR decreasing, false-alert rate decreasing, automated-recovery rate increasing.
- Missing metrics never default green.

## 8. `conflict_120826_0310` salvage lane

Branch remains stale/untrusted intake; wholesale merge is rejected.

Selective classifications:
- connection-stability concepts: ADAPT;
- broker token-health UI/read model: ADAPT; current-main System truth UI already selectively improved;
- real-data Multibagger concepts: ADAPT only after P0 and data-contract review;
- F&O eligibility/health digest: ADAPT after truth review;
- legacy token writer: REJECT;
- LoginPage/AuthGate/dashboard-key restoration: REJECT;
- Emergent webhook/runtime authority: REJECT;
- Render/local runtime authority: REJECT;
- generated reports/dist as source authority: REJECT.

Committed plaintext credential incident remains OPEN. Never quote/merge the value; treat affected credential as exposed until independent rotation proof. No force history rewrite without explicit authorization.

## 9. Current checkpoint

- Application/source SHA currently failed in GCP: **`05becfbde0d8967b0cc6e3b556493f99d89f726a`**.
- Current serving revision: **`genesis-system3-web-00199-tq5` = 100%**.
- Failed candidate: **`genesis-system3-web-00213-baq` = 0%**.
- Exact deployment blocker: **PROVEN Firestore 403** for `genesis-system3-web`.
- Dhan: **disconnected / TOKEN_EXPIRED_OR_INVALID / secret version 49**; recovery not run because deployment failed first.
- UI: **22 tabs; PR #128 implementing 44-image exact-deployed proof matrix; CI running; not merged**.
- System tab newest broker/token truth: source merged; not yet serving.
- AlphaTruth: **INSUFFICIENT_EVIDENCE**.
- SRE/OperationsTruth runtime: **NOT_PROVEN**.
- Real-money readiness: **NO**.
- LIVE: **OFF / LOCKED**.
- **USER ACTION REQUIRED: YES — only the narrow Firestore `roles/datastore.user` binding above.** No PIN/TOTP/token/API key should be sent to chat.
