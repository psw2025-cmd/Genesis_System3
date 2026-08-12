# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-12 11:00 IST`

> Single authority for `psw2025-cmd/Genesis_System3`. Google Cloud is the only runtime/deployment authority. LIVE remains OFF/LOCKED. No live order placement/modification/cancellation/routing is permitted. Secret payloads must never be exposed. `PATCHED`, `MERGED`, CI green, Cloud Run Ready, or source-only UI never equals CLOSED; closure requires exact serving-revision reproducible proof.

## 0. Exact revision and safety truth

- Repository: **`psw2025-cmd/Genesis_System3` only**.
- Main HEAD observed at run start: **`36e24d86e1aed1ae5ddbf77055cabf6e125e58cb`** (`docs(audit): refresh hourly exact control-loop checkpoint`).
- Application/source authority still deployed/tested in the latest Cloud Run attempt: **`0acf66ebf45049fbe8c6b1bc6c5912895aceda3e`** (merge PR #128).
- Runtime posture: **ANALYZER/PAPER**.
- LIVE: **OFF / LOCKED**.
- Real orders attempted in this control loop: **0**.
- Dashboard contract: **public/read-only PAPER**, no dashboard API-key/login UI.
- Canonical Dhan token authority: **`gcp-secret-manager-dynamic`**.

## 1. Mandatory control-loop position

`1 VERIFY -> 2 SELECT -> 3 ROOT CAUSE -> 4 DESIGN -> 5 PATCH -> 6 TEST -> 7 PR -> 8 CI -> 9 FIX/RETEST -> 10 MERGE -> 11 POST-MERGE VERIFY -> 12 PREP -> 13 USER GCP ONLY IF GENUINELY REQUIRED -> 14 DEPLOY VERIFY -> 15 RUNTIME TEST -> 16 USER DHAN/PIN/TOTP/OAuth ONLY IF GENUINELY REQUIRED -> 17 FULL EVIDENCE -> 18 CLOSED`

### Current primary P0 position

**STEP 13 = VERIFIED/CLOSED. STAY ON assistant-owned STEP 14 deployment verification.**

Human Step-13 proof supplied on 2026-08-12:
- active GCP account authenticated;
- project `system3-openalgo-safe` selected;
- `roles/datastore.user` successfully bound to `serviceAccount:genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com`;
- metadata verification returned the exact role/member pair.

Latest exact Cloud Run Auto Deploy run: **`31555951427`, attempt 2**, source **`0acf66ebf45049fbe8c6b1bc6c5912895aceda3e`**.

### Step-14 attempt-2 evidence

- WIF/keyless auth: **PASS**.
- Static safety/syntax: **PASS**.
- Firestore preflight: **PASS**.
- Frontend production build: **PASS**, 1,453 modules transformed.
- Required GCP resources/service-account existence checks: **PASS**.
- Cloud Build ID: **`777c080a-d57a-4b29-b565-84e2e1577502`** = SUCCESS.
- Previous production traffic protected: **`genesis-system3-web-00199-tq5` = 100%**.
- New candidate: **`genesis-system3-web-00219-pag` = 0% traffic**, tagged candidate URL present.
- Candidate Ready condition: **True**.
- Candidate container health: **True**; Uvicorn bound `0.0.0.0:8080`; startup TCP probe succeeded.
- Candidate bootstrap: canonical `GCP_SECRET_MANAGER_DYNAMIC`; `live_trading_enabled=false`; `order_placement_allowed=false`; raw token not exposed.
- Firestore 403 signature from candidates `00213/00214` **did not recur** on `00219` after Step 13.

### New repository-controlled blocker: GCP-IMAGE-PROVENANCE-TAG-DIGEST

Deployment stopped in `scripts/gcp_cloud_run_auto_deploy.py::_assert_candidate_image` with:
- expected form: Artifact Registry image **tag**;
- actual Cloud Run revision form: same image resolved to immutable **`@sha256:` digest**;
- exact observed digest: `sha256:0dbf16ec3635dbf0db9466b949d54bd1cb06d0c7ae44e7e8c36c05a612128686`;
- candidate remained healthy and at 0%, production traffic remained protected.

Classification: **deployment / provenance verifier defect**. It is not a Cloud Run application startup failure and not a reason to weaken provenance checks.

Permanent correction required: resolve the expected Artifact Registry tag to its immutable digest using authoritative Artifact Registry metadata, normalize both expected and deployed references to the same repository+digest form, compare digest-to-digest, fail closed on resolution/permission/schema failure, and add regression tests covering tag-vs-digest equivalence plus wrong-digest rejection. Google Cloud documentation explicitly supports describing Artifact Registry images by either tag or digest; a tag is therefore not a valid literal string-equality authority against Cloud Run's immutable digest representation.

Do **not** retry unchanged deployment. Fix verifier -> tests -> PR -> CI -> merge -> exact-current guarded deployment.

## 2. Permanent production sentinels

Mandatory read-only probes every run:
1. `https://genesis-system3-web-802404398783.asia-south1.run.app/api/broker/status`
2. `https://genesis-system3-web-802404398783.asia-south1.run.app/api/health`

This run's direct external fetch capability returned **cache-miss/fetch failure** for both URLs. Therefore both direct sentinel observations are **UNKNOWN**, not PASS/FAIL, from this agent environment.

Latest workflow runtime evidence independently classified:
- `/api/health` public proof: **FAIL / NOT_PROVEN**;
- Dhan read-only broker proof: **NOT_READY**;
- all four required option chains fresh/populated: **FAIL / NOT_PROVEN**;
- runtime lock: **PRODUCTION_BLOCKED**.

No endpoint body containing credentials/cookies/secrets was persisted.

## 3. Broker disconnect / token incident ledger

Chronological evidence retained; do not overwrite:

1. **Competing token-writer incident — PROVEN historical root cause.** Cloud Run loaded canonical Secret Manager token version 40 while Dhan rejected it as `TOKEN_EXPIRED_OR_INVALID` despite nominal JWT time remaining. Repository inventory found legacy Codespace/local/Render token writers capable of creating competing sessions. Prevention: single canonical GCP writer only; legacy writers retired/fail-closed.
2. **Version advancement is not recovery proof — PROVEN.** Canonical `dhan-access-token` reached version 50, yet serving runtime still reported `TOKEN_EXPIRED_OR_INVALID`. Recovery requires version advancement + runtime reload + successful Dhan read-only validation + `/api/broker/status connected=true`.
3. **Scheduler identity drift — PROVEN STALE.** Latest workflow evidence still shows `genesis-system3-dhan-token-rotate-daily` enabled at `30 7 * * *`, `Asia/Kolkata`, but OAuth service account is still `genesis-system3-web@...`, not dedicated `gs3-scheduler@...`.
4. **Rotator identity runtime proof — NOT_PROVEN.** Latest `gcloud run jobs describe` table did not prove the expected dedicated service account value. Treat as UNKNOWN until exact metadata proves `genesis-system3-dhan-rotator@...`.
5. **Current broker recovery — NOT_PROVEN.** Deployment verifier failed before rotator configuration/execution and downstream broker proof steps, so no new production token remediation was performed in attempt 2.

Current broker truth: **DISCONNECTED/NOT_READY based on last authoritative runtime evidence; `TOKEN_EXPIRED_OR_INVALID` remains unresolved.** No hidden fallback token strategy is permitted.

## 4. UI/dashboard priority

PR #128 merged the exact 22-tab deployed visual-proof harness. Contract remains:
- 22 canonical tabs;
- 22 desktop screenshots at `1600x1000`;
- 22 mobile screenshots at `430x932`;
- **44 exact-runtime screenshots total**;
- screenshot SHA-256, active-tab proof, no dashboard key/login, no order/paper mutations;
- bind visual proof to actual 100%-traffic serving revision + matching `DEPLOY_GIT_SHA`.

Current UI state: **SOURCE READY / RUNTIME PROOF BLOCKED**. Attempt 2 skipped the public-dashboard proof because Step 12 failed at provenance assertion. Proof count: **0/44 for exact-current serving deployment**.

Open UI/security intake:
- PR #129: permanent removal of dashboard credential/session authority; **OPEN**, source only, not runtime authority.
- Never merge stale LoginPage/AuthGate/API-key concepts from salvage branch.

## 5. P0 dependency truth

| Dependency | Truth | Next closure condition |
|---|---|---|
| Step-13 Firestore runtime authorization | **VERIFIED/CLOSED** | preserve binding |
| exact current deployment | **FAIL — verifier tag/digest mismatch** | permanent digest-normalized verifier fix + redeploy |
| public PAPER/no-key UI | source contract present; **runtime NOT_PROVEN** | exact serving deployment + anonymous proof |
| 22-tab visual proof | **0/44 exact-current** | exact serving deployment |
| MutationPolicy | PARTIAL / CI source proof; runtime skipped | exact deployment first |
| SafetyTruth + ExecutionEligibility | OPEN P0 | MutationPolicy runtime closure |
| PreTradeRiskService | OPEN P0 | SafetyTruth closure |
| AccountTruth + AccountSnapshotCoordinator | OPEN P0-P1 | prior P0 gates |
| durable PaperLedger + Reconciliation | PARTIAL / OPEN P0 | lifecycle/reconciliation proof |
| StateTruth/domain CAS | OPEN P0-P1 | Firestore + version/CAS authority |
| DeploymentTruth V2 | **PARTIAL / current blocker** | source->build->digest->candidate->traffic exact binding |
| WorkCoordinator/idempotency | OPEN P0-P1 | prior gates |
| OptionChainTruth -> StreamTruth -> ScannerTruth -> PredictionTruth | OPEN P1 | after P0 |
| Institutional UI/A11Y/observability | OPEN | runtime + visual + accessibility + operator proof |
| Real-money readiness | **NO** | multiple gates open; LIVE locked |

## 6. AlphaTruth

Current authoritative small sample:
- 5 days;
- 8 trades;
- 4 wins / 4 losses;
- win rate 50%;
- gross P&L `-101258.25`;
- costs `1378.10`;
- net P&L **`-102636.35`**.

**AlphaTruth = `INSUFFICIENT_EVIDENCE`.** Targets remain goals only. Historical strongest frozen research remains rejected: 489 fills / 492 holdout days; Sharpe `-1.3979`; Sortino `-3.4160`; MDD `52.3395%`; compounded return `-46.7306%`; promotion=false. model_auto_promotion=false; live=false; real_order_authority=false.

Factor/model decay trigger: **NOT_PROVEN / NOT_EVALUABLE** because authoritative rolling evidence is insufficient.

## 7. OperationsTruth / SRETruth

- PR #121 observability: **OPEN**, not runtime authority.
- PR #125 OperationsTruth/SRE baseline: **OPEN**, not runtime authority.
- Typed Phase-1 authoritative inventory: **NOT_PROVEN** in the single master authority.
- SLO scorecard: **NOT_PROVEN**; no missing metric defaults green.
- Targets only: availability >=99.95%; successful-request P95 <300ms; broker read success >=99.9%; token rotation success=100%; synthetic success >=99.9%; MTTR decreasing; false-alert rate decreasing; automated recovery increasing.

Current incident state:
- Firestore IAM incident: **RECOVERED at candidate startup / Step 13 closed**.
- New incident: **deployment provenance verifier tag-vs-digest mismatch**.
- Production traffic impact: **none observed**; prior 100%-traffic revision protected.
- Remediation attempt count for new verifier signature: **0 code fixes applied yet; do not count unchanged deploy retries as a fix**.
- Escalation: **not required yet**; repository-controlled.

## 8. `conflict_120826_0310` salvage lane

Fresh compare at this run:
- status: **diverged**;
- `main` is **188 commits ahead**;
- conflict branch is **6 commits ahead**;
- merge base: `5d1ec87a43c5778f6d010b91dc3adcd6a22ae797`;
- status remains **STALE / UNTRUSTED intake**;
- wholesale merge/rebase/copy remains rejected.

Selective ACCEPT/ADAPT/REJECT policy unchanged. `memory/test_credentials.md` remains a credential-exposure incident; never quote/merge the value and do not force-rewrite shared history without explicit authorization.

## 9. Updated TODO / dependency order

1. **P0 NOW:** permanently correct tag-vs-digest image provenance verifier; add wrong-digest and tag-resolves-to-same-digest regression tests.
2. PR/CI/merge only after deterministic gates pass; do not weaken provenance.
3. Exact-current guarded Cloud Run deploy: build -> immutable digest -> candidate 0% -> Ready -> safe HTTP proof -> exact promotion.
4. Prove both production sentinels and exact serving revision/source/digest.
5. Generate and inspect 44 UI screenshots; preserve public read-only credential-free contract.
6. Run MutationPolicy deny-only runtime capability matrix.
7. SafetyTruth/ExecutionEligibility.
8. PreTradeRiskService.
9. AccountTruth/AccountSnapshotCoordinator.
10. Durable PaperLedger/Reconciliation.
11. StateTruth/domain CAS.
12. DeploymentTruth V2 full closure.
13. WorkCoordinator/idempotency.
14. Dhan dedicated rotator identity + scheduler `gs3-scheduler` migration and proof; actual token remediation only in authorized runtime/deploy lane.
15. If Dhan still requires PIN/TOTP/OAuth, stop at **Step 16 user-only authentication**; never request secret values in chat.
16. P1 OptionChainTruth -> StreamTruth -> ScannerTruth -> PredictionTruth.
17. Merge/rebase current-main-safe observability and OperationsTruth foundations only after dependency review.
18. Institutional UI/accessibility/observability and SRE synthetics/incident/runbook/recovery proof.
19. AlphaTruth research remains isolated and fail-closed; no model promotion/live risk.
20. Continue selective salvage classification from current main only.

## 10. End-of-run checkpoint

- Exact run-start `main`: **`36e24d86e1aed1ae5ddbf77055cabf6e125e58cb`**.
- Application/source SHA tested: **`0acf66ebf45049fbe8c6b1bc6c5912895aceda3e`**.
- Primary P0: **Step 14 deployment verifier repair**.
- PR/CI/runtime: latest deploy run `31555951427` attempt 2 = **FAIL at Step 12 provenance verifier**; candidate `00219-pag` = Ready/0%; serving `00199-tq5` remains 100%.
- Sentinel `/api/broker/status`: **UNKNOWN direct fetch this run; last runtime broker proof NOT_READY/disconnected**.
- Sentinel `/api/health`: **UNKNOWN direct fetch this run; latest runtime evidence says public health proof failed**.
- UI/dashboard: **0/44 exact-current screenshots**.
- AlphaTruth: **INSUFFICIENT_EVIDENCE**, 8 trades / 5 days.
- OperationsTruth inventory: **NOT_PROVEN**.
- SLO scorecard: **NOT_PROVEN**.
- Incident: **GCP image tag-vs-digest provenance verifier defect**; no production traffic impact observed.
- Factor decay: **NOT_PROVEN / NOT_EVALUABLE**.
- Dhan identity/token truth: canonical dynamic source; broker unresolved; Scheduler identity STALE; dedicated rotator runtime identity NOT_PROVEN.
- Salvage divergence: **main +188 / conflict +6**.
- Remaining before human action: repository verifier fix and exact deployment/runtime proof. Human Dhan auth is not yet justified.
- **USER ACTION REQUIRED = NO.**
