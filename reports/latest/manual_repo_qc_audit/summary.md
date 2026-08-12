# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-12` — current audit turn

> Single authority for `psw2025-cmd/Genesis_System3`. Google Cloud is the only runtime/deployment authority. `PATCHED`, `MERGED`, CI green, Cloud Run `Ready`, source-only UI, or a generated concept never means `CLOSED`. Closure requires exact serving-revision reproducible evidence. LIVE remains OFF/LOCKED. No live order placement/modification/cancellation/routing is permitted.

## 0. Exact revision and safety truth

- Repository: **`psw2025-cmd/Genesis_System3` only**.
- Current `main` application/source HEAD before this audit-only update: **`0acf66ebf45049fbe8c6b1bc6c5912895aceda3e`** — merge PR #128.
- PR #128 merged the exact 22-tab deployed visual-proof harness; it is source authority but not runtime-verified because the exact-current candidate still fails before promotion.
- This audit update is documentation-only and must not be treated as a new application deployment candidate.
- Runtime posture: **ANALYZER/PAPER**.
- LIVE: **OFF / LOCKED**.
- Real orders attempted by this remediation stream: **0**.
- Dashboard viewing contract: **public/read-only PAPER**, no dashboard API key/login UI.
- Canonical Dhan token authority: **`gcp-secret-manager-dynamic`**; secret payload exposure is prohibited.
- Google OAuth branding: **NOT CONFIGURED / NOT REQUIRED for current public PAPER UI**.

## 1. Mandatory control-loop position

`1 VERIFY -> 2 SELECT -> 3 ROOT CAUSE -> 4 DESIGN -> 5 PATCH -> 6 TEST -> 7 PR -> 8 CI -> 9 FIX/RETEST -> 10 MERGE -> 11 POST-MERGE VERIFY -> 12 PREP -> 13 USER GCP ONLY IF GENUINELY REQUIRED -> 14 DEPLOY VERIFY -> 15 RUNTIME TEST -> 16 USER DHAN/PIN/TOTP/OAuth ONLY IF GENUINELY REQUIRED -> 17 FULL EVIDENCE -> 18 CLOSED`

### Current primary P0 position

**STAY ON STEP 13/14/15 — exact-current candidate startup is blocked by the same PROVEN Firestore IAM denial. No further repository patch is justified before the genuine Step-13 GCP role boundary is satisfied.**

Latest exact Cloud Run Auto Deploy run: **`31555951427`**, source **`0acf66ebf45049fbe8c6b1bc6c5912895aceda3e`**.

Latest proven results:
- checkout exact `0acf66eb...`: PASS;
- keyless WIF authentication: PASS;
- static syntax/trading safety gates: PASS;
- worker-secret existence: PASS;
- Firestore identity/preflight contract: PASS as a non-mutating preflight; it explicitly reported project IAM was not introspected and runtime candidate startup remains the permission authority;
- frontend production build: PASS, 1,453 modules transformed;
- GCP API/service-account existence preflight: PASS, including dedicated rotator and `gs3-scheduler` identities;
- Cloud Build: PASS, build ID **`02a1d975-cc7c-40d1-895a-bedb583bc90e`**;
- exact image: `asia-south1-docker.pkg.dev/system3-openalgo-safe/system3-containers/genesis-system3:0acf66ebf450-1786500578`;
- candidate revision created: **`genesis-system3-web-00214-xot`**;
- candidate remained **0% traffic**;
- existing production revision **`genesis-system3-web-00199-tq5` remains 100%**;
- candidate log proved `[cloud-start] binding 0.0.0.0:8080`;
- candidate bootstrap proved canonical Dhan token authority installed, LIVE false, order placement false, raw token not exposed;
- Firestore `batch_get_documents` then failed with **`google.api_core.exceptions.PermissionDenied: 403 Missing or insufficient permissions`**;
- application terminated with **`RuntimeError: Required Firestore state load failed`**;
- Cloud Run startup-probe/port message is therefore a secondary consequence, not the root cause;
- public exact-current `/ui` proof: SKIPPED because deployment failed;
- 22-tab / 44-image visual proof: SKIPPED because deployment failed;
- MutationPolicy exact-current runtime proof: SKIPPED;
- dedicated Dhan rotator configuration/execution: SKIPPED;
- broker recovery proof: SKIPPED;
- exact-SHA `cloud-run/runtime-proof`: **FAIL**;
- production traffic remained protected.

This is the second independent exact-current candidate (`00213-baq`, then `00214-xot`) to bind port 8080 and fail at required Firestore state load with the same 403. **Repository-controlled startup regression classification = REJECTED. External Firestore IAM boundary = PROVEN.**

### Genuine current Step-13 action

The dedicated web runtime must receive the Firestore data role required by the fail-closed state backend:

```bash
gcloud projects add-iam-policy-binding system3-openalgo-safe \
  --member="serviceAccount:genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com" \
  --role="roles/datastore.user" \
  --condition=None
```

Then verify only the binding metadata:

```bash
gcloud projects get-iam-policy system3-openalgo-safe \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/datastore.user AND bindings.members:serviceAccount:genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com" \
  --format="table(bindings.role,bindings.members)"
```

After proof of that binding, assistant-owned remediation resumes immediately: exact-current redeploy -> zero-traffic candidate startup -> exact serving revision proof -> public no-key UI -> 22-tab desktop/mobile visual matrix -> MutationPolicy runtime -> dedicated Dhan rotator -> token version advancement -> read-only Dhan recovery -> scheduler identity proof -> next P0 dependency.

## 2. Dhan broker and identity truth

Last authoritative public broker proof remains:
- broker: `dhan`;
- mode: `ANALYZER`;
- connected: **false**;
- error: **`TOKEN_EXPIRED_OR_INVALID`**;
- credentials/client/access-token present: true;
- token source: `GCP_SECRET_MANAGER_DYNAMIC`;
- Secret Manager version: **49**;
- raw token exposed: false;
- live trading enabled: false;
- order placement allowed: false;
- repeated reload of the same version did not recover Dhan authentication.

Human bootstrap previously proved:
- `genesis-system3-dhan-rotator@system3-openalgo-safe.iam.gserviceaccount.com` exists;
- valid Scheduler identity is **`gs3-scheduler@system3-openalgo-safe.iam.gserviceaccount.com`**;
- deployment identity may attach those identities;
- rotator can read only required Dhan token-mint secrets and add a version to `dhan-access-token`;
- PR #127 corrected repository references from the invalid over-length Scheduler ID to `gs3-scheduler` and passed exact-head CI before merge.

Latest post-deploy runtime report still showed:
- Cloud Run job `genesis-system3-dhan-token-rotate` exists, but the report did **not** prove the dedicated service account is attached because the configuration step was skipped after deployment failure;
- Cloud Scheduler `genesis-system3-dhan-token-rotate-daily` remains ENABLED at `30 7 * * *`, timezone `Asia/Kolkata`, but still uses **`genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com`** as OAuth service account;
- therefore Scheduler runtime identity state = **STALE / NOT YET MIGRATED**;
- do not modify it out of sequence: the workflow is designed to configure the isolated identities only after exact-current web deployment succeeds.

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

PR **#128 — `feat(ui-proof): capture every dashboard tab for review`** is **MERGED** at application/source SHA **`0acf66ebf45049fbe8c6b1bc6c5912895aceda3e`**.

Its exact-head PR checks passed before merge:
- Genesis System3 Global Safety CI: PASS;
- GCP Dhan Token Fix CI: PASS.

Merged implementation contract:
- canonical sidebar registry: **22 tabs exactly**;
- deterministic safe `?tab=<id>` review links;
- proof binds to the **actual single 100%-traffic serving revision**, not `latestReadyRevisionName` or a 0%-traffic candidate;
- exact `DEPLOY_GIT_SHA` must match the revision being proved;
- headless-Chrome actual product render;
- **22 desktop screenshots at 1600x1000**;
- **22 mobile screenshots at 430x932**;
- total visual set: **44 screenshots per exact successful deployment**;
- screenshot SHA-256 recorded;
- each tab must prove it became active (`aria-current=page`);
- dashboard API-key/login prompt must be absent;
- per-tab review state starts `PENDING_USER_REVIEW`;
- no order/paper mutation endpoint is called;
- LIVE remains OFF/LOCKED.

Runtime state for this harness: **SOURCE MERGED / EXACT-CURRENT DEPLOY FAILED / 44 SCREENSHOTS NOT GENERATED** because candidate `00214-xot` failed at Firestore before `/ui` proof.

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
| 21 | System | UPDATED | broker/token/safety/deployment truth | **SOURCE CI PROVEN; DEPLOY PENDING** | PENDING USER REVIEW |
| 22 | Live Gate | PRESENT | SafetyTruth/Risk/Account/Paper/Deployment | **PENDING DEPLOY** | LIVE OFF; PENDING USER REVIEW |

### Current UI reality

The newest System-tab broker/token truth and 22-tab proof code are merged in source, but **users are still served by old revision `00199-tq5`** because newer candidates fail before promotion. No screenshot from the old serving revision may be presented as proof of current `main` UI changes.

The next valid screenshot set must come only after the Firestore IAM blocker is resolved and an exact-current revision passes guarded deployment and promotion proof.

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
| exact current deployment | **FAIL — Firestore 403 on `00214-xot`** | grant runtime datastore role, redeploy exact current source |
| MutationPolicy | PARTIAL / CI VERIFIED / RUNTIME NOT RUN | exact deployment first |
| SafetyTruth + ExecutionEligibility | OPEN P0 | after MutationPolicy runtime |
| PreTradeRiskService | OPEN P0 | after SafetyTruth |
| AccountTruth + AccountSnapshotCoordinator | OPEN P0-P1 | after prior P0 gates |
| durable PaperLedger + Reconciliation | PARTIAL / OPEN P0 | lifecycle/reconciliation closure |
| StateTruth/domain CAS | OPEN P0-P1 | Firestore + version/CAS authority |
| DeploymentTruth V2 | PARTIAL / OPEN P0 | source/build/digest/candidate/serving-traffic binding |
| WorkCoordinator/idempotency | OPEN P0-P1 | pending |
| OptionChainTruth -> StreamTruth -> ScannerTruth -> PredictionTruth | OPEN P1 | after P0 |
| Institutional UI/A11Y | OPEN | 22-tab functional + visual + user review required |
| Real-money readiness | **NO** | multiple P0/P1 gates open; LIVE locked |

Important provenance caution: the fallback `gcp_runtime_evidence.py` step reported `source_matches_deployment=true` after the failed candidate. That report does **not** close DeploymentTruth because the actual service traffic report still showed `00199-tq5` at 100% and `00214-xot` at 0%. The newly merged serving-revision-bound public/UI proof is the stronger authority, but it was skipped because deployment failed. Therefore exact-current serving provenance remains **NOT PROVEN**.

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

Factor/model decay trigger remains **NOT_PROVEN / NOT_EVALUABLE** because authoritative evidence is insufficient for the predeclared rolling deterioration estimate. No `RESEARCH_REQUIRED` trigger and no silent retraining.

## 7. OperationsTruth / observability

- PR #121 observability: **OPEN**, not merged/runtime authority. Its intended design remains read-only trace IDs, W3C traceparent, redacted browser evidence, uptime checks and runbooks; no broker order probe or secret payload.
- PR #125 OperationsTruth/SRETruth: **OPEN**, prior CI green, not runtime authority.
- Phase-1 typed GCP inventory therefore remains **NOT_PROVEN at runtime**.
- SLO scorecard remains **NOT_PROVEN** until minimum sample/window evidence exists: availability >=99.95%, successful API P95 <300 ms, broker read success >=99.9%, token rotation success 100%, synthetic success >=99.9%, MTTR decreasing, false-alert rate decreasing, automated-recovery rate increasing.
- Missing metrics never default green.
- Current incident class: **infrastructure/IAM — Firestore runtime authorization**.
- Remediation attempts: two exact-current zero-traffic candidates have reproduced the same Firestore 403 after successful port bind.
- Per bounded-remediation policy, further code retries without the external IAM fix are not justified; escalation package is effectively ready and the next action is the narrow human GCP binding only.

## 8. `conflict_120826_0310` salvage lane

Fresh divergence check:
- current `main` is **186 commits ahead** of `conflict_120826_0310`;
- conflict branch is **6 commits ahead** of `main`;
- merge base remains `5d1ec87a43c5778f6d010b91dc3adcd6a22ae797`;
- branch status: **DIVERGED / STALE / UNTRUSTED INTAKE**;
- wholesale merge/rebase-overwrite remains rejected.

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

- Exact application/source `main` before this audit-only update: **`0acf66ebf45049fbe8c6b1bc6c5912895aceda3e`**.
- Latest exact deployment run: **`31555951427` = FAIL at candidate startup**.
- Current serving revision: **`genesis-system3-web-00199-tq5` = 100%**.
- Latest failed candidate: **`genesis-system3-web-00214-xot` = 0%**.
- Exact deployment blocker: **PROVEN Firestore `batch_get_documents` 403** for `genesis-system3-web` after successful `0.0.0.0:8080` bind.
- PR #128: **MERGED**; 22-tab / 44-image exact-serving visual harness is now source authority; runtime images not generated because deployment failed first.
- MutationPolicy: **CI/source partial, exact-current runtime not run**.
- Dhan: **disconnected / TOKEN_EXPIRED_OR_INVALID / last proven secret version 49**; recovery not run because deployment failed first.
- Scheduler: runtime still uses **web service account**, so identity migration is **STALE** until post-deployment configuration runs.
- AlphaTruth: **INSUFFICIENT_EVIDENCE** — 8 trades / 5 days / 50% win / net `-102636.35`.
- OperationsTruth inventory: **NOT_PROVEN runtime**; PR #125 remains open.
- SLO scorecard: **NOT_PROVEN**.
- Incident/remediation/escalation: Firestore IAM incident **PROVEN**; two bounded candidate failures reproduce it; no additional code retry justified before human IAM action.
- Factor-decay trigger: **NOT_PROVEN / NOT_EVALUABLE**; no `RESEARCH_REQUIRED`.
- Observability: PR #121 open / not runtime authority.
- Salvage divergence: `main +186`, conflict branch `+6`; selective salvage only.
- Real-money readiness: **NO**.
- LIVE: **OFF / LOCKED**.
- Real orders attempted: **0**.
- What remains before assistant-owned work can resume: proof that `roles/datastore.user` is bound to `genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com`.
- **USER ACTION REQUIRED: YES — only the narrow Firestore role binding and metadata verification commands in Section 1. No PIN/TOTP/token/API key should be sent to chat.**