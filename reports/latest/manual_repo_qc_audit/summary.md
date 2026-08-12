# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-12 11:59 IST`

> Single authority for `psw2025-cmd/Genesis_System3`. Google Cloud is the only runtime/deployment authority. LIVE remains OFF/LOCKED. No live order placement/modification/cancellation/routing is permitted. Secret payloads must never be exposed. `PATCHED`, `MERGED`, CI green, Cloud Run Ready, or source-only UI never equals CLOSED; closure requires exact serving-revision reproducible proof.

## 0. Exact revision and safety truth

- Repository: **`psw2025-cmd/Genesis_System3` only**.
- Current `main` HEAD observed this run: **`38c148747d5a1f1f122c506caa0755d729a5fd2b`** (`docs(audit): record post-IAM deploy verifier incident`).
- Application/source authority in latest guarded Cloud Run attempt: **`0acf66ebf45049fbe8c6b1bc6c5912895aceda3e`** (merge PR #128).
- Runtime posture: **ANALYZER/PAPER**.
- LIVE: **OFF / LOCKED**.
- Real orders attempted in this control loop: **0**.
- Dashboard contract: **public/read-only PAPER**, no dashboard API-key/login UI.
- Canonical Dhan token authority: **`gcp-secret-manager-dynamic`**.

## 1. Mandatory control-loop position

`1 VERIFY -> 2 SELECT -> 3 ROOT CAUSE -> 4 DESIGN -> 5 PATCH -> 6 TEST -> 7 PR -> 8 CI -> 9 FIX/RETEST -> 10 MERGE -> 11 POST-MERGE VERIFY -> 12 PREP -> 13 USER GCP ONLY IF GENUINELY REQUIRED -> 14 DEPLOY VERIFY -> 15 RUNTIME TEST -> 16 USER DHAN/PIN/TOTP/OAuth ONLY IF GENUINELY REQUIRED -> 17 FULL EVIDENCE -> 18 CLOSED`

### Current primary P0 position

**STEP 13 = VERIFIED/CLOSED. STAY ON assistant-owned STEP 14 deployment verification.**

Step-13 human proof already supplied:
- active GCP account authenticated;
- project `system3-openalgo-safe` selected;
- `roles/datastore.user` bound to `serviceAccount:genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com`;
- metadata verification returned the exact role/member pair.

Latest exact guarded deploy attempt remains run **`31555951427`, attempt 2**, source **`0acf66ebf45049fbe8c6b1bc6c5912895aceda3e`**.

### Step-14 attempt-2 evidence retained

- WIF/keyless auth: **PASS**.
- Static safety/syntax: **PASS**.
- Firestore preflight: **PASS**.
- Frontend production build: **PASS**, 1,453 modules transformed.
- Required GCP resources/service-account existence checks: **PASS**.
- Cloud Build ID: **`777c080a-d57a-4b29-b565-84e2e1577502`** = SUCCESS.
- Previous production traffic protected: **`genesis-system3-web-00199-tq5` = 100%**.
- Candidate **`genesis-system3-web-00219-pag` = 0% traffic**.
- Candidate Ready: **True**.
- Candidate container health: **True**; Uvicorn bound `0.0.0.0:8080`; startup probe succeeded.
- Candidate bootstrap: canonical dynamic token source; live=false; order placement=false; raw token not exposed.
- Earlier Firestore 403 signature **did not recur** on candidate `00219` after Step 13.

### Active repository-controlled blocker: `GCP-IMAGE-PROVENANCE-TAG-DIGEST`

Exact implementation on current `main` still uses literal/string-containment comparison in `scripts/gcp_cloud_run_auto_deploy.py::_assert_candidate_image`:

```python
if image not in deployed_image and deployed_image != image:
    raise RuntimeError(...)
```

Observed deployment shape:
- expected authority supplied to deployer: Artifact Registry **tag**;
- Cloud Run revision returns immutable **`@sha256:` digest** form;
- observed digest: `sha256:0dbf16ec3635dbf0db9466b949d54bd1cb06d0c7ae44e7e8c36c05a612128686`;
- candidate stayed Ready/0%; production traffic stayed protected.

Truth: **FAIL / repository-controlled verifier defect**. It is not an application startup failure. Do not retry the same code unchanged and do not weaken provenance verification.

Required permanent fix remains: resolve expected Artifact Registry tag to authoritative immutable digest; normalize expected/deployed repository+digest; compare digest-to-digest; fail closed on resolution/permission/schema failure; regression-test equivalent tag/digest and wrong-digest rejection.

No code fix was committed in this run because the available GitHub write surface is whole-file replacement only and the deployer is a large safety-critical file. A partial/manual reconstruction would create avoidable corruption risk. The dependency therefore correctly remains open instead of applying an unsafe patch.

## 2. Permanent production sentinels

Mandatory read-only probes:
1. `https://genesis-system3-web-802404398783.asia-south1.run.app/api/broker/status`
2. `https://genesis-system3-web-802404398783.asia-south1.run.app/api/health`

Run observation at ~11:59 IST:
- `/api/health`: external fetch returned **cache miss / fetch failure** -> typed state **UNKNOWN**.
- `/api/broker/status`: external fetch returned **cache miss / fetch failure** -> typed state **UNKNOWN**.
- This is a recurrence of the agent-environment observability limitation, **not evidence that either endpoint is healthy or unhealthy**.
- No endpoint body containing credentials/cookies/secrets was persisted.

Last authoritative workflow/runtime truth remains:
- public `/api/health` proof: **FAIL / NOT_PROVEN**;
- Dhan read-only broker proof: **NOT_READY**;
- all four required option chains fresh/populated: **FAIL / NOT_PROVEN**;
- runtime lock: **PRODUCTION_BLOCKED**.

## 3. Broker disconnect / token incident ledger

Chronological evidence retained; never overwrite:

1. **Competing token-writer incident — PROVEN historical root cause.** Cloud Run loaded canonical Secret Manager token version 40 while Dhan rejected it as `TOKEN_EXPIRED_OR_INVALID` despite nominal JWT time remaining. Repository inventory found legacy Codespace/local/Render token writers capable of creating competing sessions. Prevention: one canonical GCP writer only; legacy writers retired/fail-closed.
2. **Version advancement is not recovery proof — PROVEN.** Canonical `dhan-access-token` reached version 50, yet serving runtime still reported `TOKEN_EXPIRED_OR_INVALID`. Recovery requires version advancement + runtime reload + successful Dhan read-only validation + `/api/broker/status connected=true`.
3. **Scheduler identity drift — PROVEN STALE.** Last authoritative evidence showed `genesis-system3-dhan-token-rotate-daily` enabled at `30 7 * * *`, `Asia/Kolkata`, but OAuth service account still `genesis-system3-web@...`, not dedicated `gs3-scheduler@...`.
4. **Rotator identity runtime proof — NOT_PROVEN.** Dedicated `genesis-system3-dhan-rotator@...` runtime identity not yet proven from exact job metadata.
5. **Current recovery — NOT_PROVEN.** Deploy verifier stopped before downstream rotator/broker proof; no production token remediation was performed in attempt 2.
6. **Sentinel-observability recurrence — UNKNOWN, not broker RCA.** This agent environment again could not fetch the public sentinel URLs. Prevention requirement remains GCP-native uptime/synthetic monitoring plus workflow evidence so agent cache-miss cannot hide runtime truth.

Current broker truth: **DISCONNECTED/NOT_READY based on last authoritative runtime evidence; `TOKEN_EXPIRED_OR_INVALID` unresolved.** Missing fresh proof cannot be promoted to green.

## 4. UI/dashboard priority

PR #128 merged the exact 22-tab deployed visual-proof harness. Required contract:
- 22 canonical tabs;
- 22 desktop screenshots at `1600x1000`;
- 22 mobile screenshots at `430x932`;
- **44 exact-runtime screenshots total**;
- screenshot SHA-256, active-tab proof, no dashboard key/login, no order/paper mutations;
- bind proof to actual 100%-traffic serving revision + matching `DEPLOY_GIT_SHA`.

Current UI state: **SOURCE READY / RUNTIME PROOF BLOCKED**. Exact-current proof count: **0/44**.

### PR #129 exact state this run

- PR **#129** `security: permanently remove dashboard credential and session authority`: **OPEN**, not merged, not mergeable.
- Head: **`04f27e100b53e464f5d6ba5b407d8faaff74b3ef`**.
- PR base snapshot remains **`36e24d86e1aed1ae5ddbf77055cabf6e125e58cb`**, therefore it is behind current `main` and must be refreshed before merge authority.
- Workflow results on head:
  - GCP Dhan Token Fix CI: **PASS**.
  - GCP Stage 2 Safety Checks: **PASS**.
  - Workflow Priority Guard: **PASS**.
  - Genesis System3 Global Safety CI: **FAIL**.
- Exact Global Safety failure remains the **Permanent public-readonly forensic gate**, which detected active/retired dashboard API-key/session references across workflow/tools/scripts plus legacy launch signatures. Do not weaken that gate. Remove/adapt genuine active remnants on refreshed current main, rerun full CI, then merge only if green.

No old screenshot is acceptable as proof for the new UI. Final new-UI closure remains 44 exact-current screenshots from the deployed serving revision.

## 5. P0 dependency truth

| Dependency | Truth | Next closure condition |
|---|---|---|
| Step-13 Firestore runtime authorization | **VERIFIED/CLOSED** | preserve binding |
| exact current deployment | **FAIL — tag/digest verifier** | permanent digest-normalized verifier fix + redeploy |
| public PAPER/no-key UI | source contract present; **runtime NOT_PROVEN** | PR #129 cleanup/refresh + exact serving proof |
| 22-tab visual proof | **0/44 exact-current** | exact serving deployment |
| MutationPolicy | PARTIAL / source proof; runtime skipped | exact deployment first |
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

Current authoritative small sample retained:
- 5 days;
- 8 trades;
- 4 wins / 4 losses;
- win rate 50%;
- gross P&L `-101258.25`;
- costs `1378.10`;
- net P&L **`-102636.35`**.

**AlphaTruth = `INSUFFICIENT_EVIDENCE`.** Historical frozen research remains rejected: 489 fills / 492 holdout days; Sharpe `-1.3979`; Sortino `-3.4160`; MDD `52.3395%`; compounded return `-46.7306%`; promotion=false. model_auto_promotion=false; live=false; real_order_authority=false.

Factor/model decay: **NOT_PROVEN / NOT_EVALUABLE** due insufficient authoritative rolling evidence.

## 7. OperationsTruth / SRETruth

- PR #121 observability: **OPEN**, not runtime authority.
- PR #125 OperationsTruth/SRE baseline: **OPEN**, not runtime authority.
- Typed Phase-1 inventory: **NOT_PROVEN** in this master authority.
- SLO scorecard: **NOT_PROVEN**; no missing metric defaults green.
- Targets only: availability >=99.95%; successful-request P95 <300ms; broker read success >=99.9%; token rotation success=100%; synthetic success >=99.9%; MTTR decreasing; false-alert rate decreasing; automated recovery increasing.

Incident state:
- Firestore IAM: **RECOVERED at candidate startup / Step 13 closed**.
- Active P0 incident: **image tag-vs-digest provenance verifier defect**.
- Production traffic impact: **none proven**; prior serving revision protected.
- Code-remediation attempts for this signature: **0**.
- Escalation: **not required**; repository-controlled.

## 8. `conflict_120826_0310` salvage lane

Fresh compare this run:
- status: **diverged**;
- current `main` is **189 commits ahead**;
- conflict branch is **6 commits ahead**;
- merge base: **`5d1ec87a43c5778f6d010b91dc3adcd6a22ae797`**;
- status remains **STALE / UNTRUSTED intake**;
- wholesale merge/rebase/copy remains rejected.

Notable still-untrusted content includes Emergent webhook cron authority, legacy token changes, generated `dist`, generated report authority, and `memory/test_credentials.md`. Credential-exposure incident remains unresolved until independent rotation proof exists; never quote/merge the value.

## 9. Updated TODO / dependency order

1. **P0 NOW:** implement permanent digest-normalized image provenance verifier and wrong-digest regression guard.
2. Refresh/rebase PR #129 on current main; remove/adapt every genuine forensic no-key violation; full CI green required.
3. Merge only exact reviewed fixes; do not weaken safety/provenance gates.
4. Exact-current guarded Cloud Run deploy: source SHA -> Cloud Build -> immutable digest -> 0%-traffic candidate -> Ready -> safe HTTP proof -> exact promotion.
5. Prove both production sentinels and exact serving source/revision/digest.
6. Produce and inspect 44 genuinely new UI screenshots; reject historical/old UI evidence.
7. Run MutationPolicy deny-only runtime capability matrix.
8. SafetyTruth/ExecutionEligibility.
9. PreTradeRiskService.
10. AccountTruth/AccountSnapshotCoordinator.
11. Durable PaperLedger/Reconciliation.
12. StateTruth/domain CAS.
13. DeploymentTruth V2 full closure.
14. WorkCoordinator/idempotency.
15. Prove dedicated Dhan rotator identity and migrate/prove Scheduler `gs3-scheduler`; production token remediation only via canonical authorized lane.
16. If Dhan genuinely requires PIN/TOTP/OAuth, stop at **Step 16 user-only authentication**; never request secret values in chat.
17. P1 OptionChainTruth -> StreamTruth -> ScannerTruth -> PredictionTruth.
18. Current-main-safe observability + OperationsTruth foundations after dependency review.
19. Institutional UI/accessibility/observability, GCP-native synthetics, incident/runbook/recovery proof.
20. AlphaTruth stays isolated/fail-closed; no model promotion/live risk.
21. Continue selective salvage classification from current main only.

## 10. End-of-run checkpoint

- Exact current `main` at observation: **`38c148747d5a1f1f122c506caa0755d729a5fd2b`**.
- Application/source SHA last tested in guarded deploy: **`0acf66ebf45049fbe8c6b1bc6c5912895aceda3e`**.
- Primary P0: **Step 14 deployment provenance verifier repair**.
- PR/CI/runtime: PR #129 OPEN/not mergeable; 3 supporting workflows PASS, Global Safety FAIL at permanent no-key forensic gate. Latest guarded deploy remains FAIL at image-provenance assertion; candidate `00219-pag` Ready/0%; serving `00199-tq5` last proven 100%.
- Sentinel `/api/broker/status`: **UNKNOWN direct observation; last authoritative broker proof NOT_READY/disconnected**.
- Sentinel `/api/health`: **UNKNOWN direct observation; last authoritative public health proof FAIL/NOT_PROVEN**.
- UI/dashboard: **0/44 exact-current screenshots**.
- AlphaTruth: **INSUFFICIENT_EVIDENCE**, 8 trades / 5 days.
- OperationsTruth: **NOT_PROVEN**.
- SLO scorecard: **NOT_PROVEN**.
- Incident/remediation: tag-vs-digest verifier defect; 0 safe code fixes applied; no production traffic impact proven.
- Recurrence/prevention delta: sentinel cache-miss recurrence explicitly classified as agent-observability limitation; GCP-native synthetics remain required prevention.
- Factor decay: **NOT_PROVEN / NOT_EVALUABLE**.
- Dhan identity/token/broker truth: canonical dynamic token source; broker unresolved; Scheduler identity STALE; dedicated rotator runtime identity NOT_PROVEN.
- Salvage divergence: **main +189 / conflict +6**.
- Remaining before human action: repository verifier fix, PR #129 forensic cleanup/refresh, exact deployment/runtime proof. Human Dhan authentication is not yet justified.
- **USER ACTION REQUIRED = NO.**
