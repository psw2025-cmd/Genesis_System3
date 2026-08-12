# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-12 09:08 IST`

> Single authority for `psw2025-cmd/Genesis_System3`. Google Cloud is the only runtime/deployment authority. `PATCHED`, `MERGED`, CI green, Cloud Run `Ready`, source-only UI, or concept output never means `CLOSED`. Closure requires exact serving-revision reproducible evidence. LIVE remains OFF/LOCKED. No live order placement/modification/cancellation/routing is permitted.

## 0. Exact revision and safety truth

- Repository: **`psw2025-cmd/Genesis_System3` only**.
- Current `main` HEAD before this audit-only update: **`6ca4acebd74f8f8aa64420bc2cddd3a3146eecd8`** — documentation-only audit commit.
- Current application/source authority: **`0acf66ebf45049fbe8c6b1bc6c5912895aceda3e`** — merge PR #128.
- PR #128 merged the exact 22-tab deployed visual-proof harness; source authority only until exact serving proof exists.
- Runtime posture: **ANALYZER/PAPER**.
- LIVE: **OFF / LOCKED**.
- Real orders attempted by this remediation stream: **0**.
- Dashboard viewing contract: **public/read-only PAPER**, no dashboard API-key/login UI.
- Canonical Dhan token authority: **`gcp-secret-manager-dynamic`**; secret payload exposure prohibited.
- Global Safety CI for audit HEAD `6ca4ace...`: **PASS**, run `31557528488`.

## 1. Mandatory control-loop position

`1 VERIFY -> 2 SELECT -> 3 ROOT CAUSE -> 4 DESIGN -> 5 PATCH -> 6 TEST -> 7 PR -> 8 CI -> 9 FIX/RETEST -> 10 MERGE -> 11 POST-MERGE VERIFY -> 12 PREP -> 13 USER GCP ONLY IF GENUINELY REQUIRED -> 14 DEPLOY VERIFY -> 15 RUNTIME TEST -> 16 USER DHAN/PIN/TOTP/OAuth ONLY IF GENUINELY REQUIRED -> 17 FULL EVIDENCE -> 18 CLOSED`

### Current primary P0 position

**STAY ON STEP 13/14/15 — exact-current candidate startup is blocked by the same PROVEN Firestore IAM denial. No further repository patch or code-only retry is justified before the genuine Step-13 GCP role boundary is satisfied.**

Latest exact Cloud Run Auto Deploy run: **`31555951427`**, source **`0acf66ebf45049fbe8c6b1bc6c5912895aceda3e`**.

Proven deployment chain:
- exact checkout: PASS;
- keyless WIF: PASS;
- static syntax/trading safety: PASS;
- worker-secret existence: PASS;
- Firestore identity preflight contract: PASS as non-mutating existence/contract check; project IAM was not introspected;
- frontend production build: PASS, 1,453 modules transformed;
- required GCP API/service-account existence: PASS, including dedicated rotator and `gs3-scheduler`;
- Cloud Build: PASS, build ID **`02a1d975-cc7c-40d1-895a-bedb583bc90e`**;
- exact image tag: `asia-south1-docker.pkg.dev/system3-openalgo-safe/system3-containers/genesis-system3:0acf66ebf450-1786500578`;
- candidate: **`genesis-system3-web-00214-xot`**, 0% traffic;
- prior production: **`genesis-system3-web-00199-tq5`**, 100% traffic;
- candidate log: `[cloud-start] binding 0.0.0.0:8080`;
- candidate bootstrap: canonical Dhan token authority installed, LIVE false, order placement false, raw token not exposed;
- Firestore `batch_get_documents`: **`403 Missing or insufficient permissions`**;
- terminal app error: **`RuntimeError: Required Firestore state load failed`**;
- Cloud Run port/startup-probe message is a secondary consequence, not root cause;
- exact-current `/ui`: SKIPPED;
- 22-tab / 44-image proof: SKIPPED;
- MutationPolicy runtime: SKIPPED;
- dedicated rotator configuration/execution: SKIPPED;
- broker recovery: SKIPPED;
- exact-SHA runtime proof: **FAIL**;
- production traffic protected: **YES**.

Two independent candidates (`00213-baq`, `00214-xot`) bound port 8080 and failed at the same required Firestore load. **Repository-controlled startup regression = REJECTED. External Firestore IAM boundary = PROVEN.**

### Genuine Step-13 action

Required narrow GCP binding:

```bash
gcloud projects add-iam-policy-binding system3-openalgo-safe \
  --member="serviceAccount:genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com" \
  --role="roles/datastore.user" \
  --condition=None
```

Metadata-only verification:

```bash
gcloud projects get-iam-policy system3-openalgo-safe \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/datastore.user AND bindings.members:serviceAccount:genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com" \
  --format="table(bindings.role,bindings.members)"
```

After exact proof of this binding, assistant-owned sequence resumes: exact-current deploy -> zero-traffic candidate -> readiness -> exact serving revision/source/digest proof -> public no-key UI -> 44-tab screenshots -> MutationPolicy runtime -> SafetyTruth/ExecutionEligibility -> PreTradeRiskService -> AccountTruth -> durable PaperLedger/Reconciliation -> StateTruth/domain CAS -> DeploymentTruth V2 -> WorkCoordinator/idempotency -> P1 truth chain.

## 2. Dhan broker and identity truth

Last authoritative public broker proof:
- broker: `dhan`;
- mode: `ANALYZER`;
- connected: **false**;
- error: **`TOKEN_EXPIRED_OR_INVALID`**;
- credentials/client/access-token present: true;
- token source: `GCP_SECRET_MANAGER_DYNAMIC`;
- raw token exposed: false;
- live trading enabled: false;
- order placement allowed: false.

Additional GCP evidence from the human read-only snapshot:
- canonical `dhan-access-token` reached **version 50** on `2026-08-12T02:00:14Z`;
- serving runtime later loaded version 50 and Dhan still rejected it as `TOKEN_EXPIRED_OR_INVALID` even though metadata expiry was in the future;
- therefore version creation alone is **not broker recovery proof**;
- `genesis-system3-dhan-rotator` exists and has multiple successful executions, but exact current dedicated service-account attachment/runtime validation remains not closed;
- Scheduler `genesis-system3-dhan-token-rotate-daily` remains ENABLED at `30 7 * * *`, `Asia/Kolkata`, and still uses **`genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com`** rather than `gs3-scheduler`;
- Scheduler identity state: **STALE / NOT YET MIGRATED**;
- historical web-runtime PIN/TOTP/token-version-add privilege remains a cleanup item only after dedicated rotator recovery proof.

Do not rotate again, alter Scheduler, or remove legacy privilege out of sequence before exact-current web deployment succeeds.

## 3. Mandatory UI Proof Matrix

PR #128 is **MERGED** at application/source SHA `0acf66eb...`.

Proof contract:
- canonical sidebar registry: **22 tabs exactly**;
- safe deterministic `?tab=<id>` links;
- proof binds to actual single 100%-traffic serving revision and matching `DEPLOY_GIT_SHA`;
- 22 desktop screenshots at `1600x1000`;
- 22 mobile screenshots at `430x932`;
- total **44 screenshots** per exact successful deployment;
- screenshot SHA-256;
- active-tab proof;
- dashboard key/login absence;
- no order/paper mutation calls;
- each tab starts `PENDING_USER_REVIEW`.

Runtime state: **SOURCE MERGED / EXACT-CURRENT DEPLOY FAILED / 44 SCREENSHOTS NOT GENERATED**.

All 22 tabs remain unfinalized until source, data contract, exact-current desktop/mobile visual, functional proof, error/loading/stale behavior, accessibility, and user acceptance are complete.

## 4. P0 dependency truth

| Dependency | Truth | Next closure condition |
|---|---|---|
| public PAPER/no-key viewing | VERIFIED/CLOSED for viewing requirement | preserve contract |
| Firestore runtime authorization | **FAIL / PROVEN IAM BOUNDARY** | Step-13 `roles/datastore.user` proof |
| exact current deployment | **FAIL — `00214-xot` Firestore 403** | IAM proof then exact-current redeploy |
| MutationPolicy | PARTIAL / CI VERIFIED / RUNTIME NOT RUN | exact deployment first |
| SafetyTruth + ExecutionEligibility | OPEN P0 | MutationPolicy runtime closure |
| PreTradeRiskService | OPEN P0 | SafetyTruth closure |
| AccountTruth + AccountSnapshotCoordinator | OPEN P0-P1 | prior P0 gates |
| durable PaperLedger + Reconciliation | PARTIAL / OPEN P0 | lifecycle/reconciliation authority |
| StateTruth/domain CAS | OPEN P0-P1 | Firestore + version/CAS authority |
| DeploymentTruth V2 | PARTIAL / OPEN P0 | source/build/digest/candidate/serving binding |
| WorkCoordinator/idempotency | OPEN P0-P1 | pending |
| OptionChainTruth -> StreamTruth -> ScannerTruth -> PredictionTruth | OPEN P1 | after P0 |
| Institutional UI/A11Y | OPEN | 22-tab functional + visual + user review |
| Real-money readiness | **NO** | multiple gates open; LIVE locked |

Important provenance caution: fallback runtime evidence previously reported `source_matches_deployment=true` after the failed candidate, but actual service traffic still proved `00199-tq5` = 100% and `00214-xot` = 0%. Exact-current serving provenance therefore remains **NOT PROVEN**.

## 5. AlphaTruth / quantitative research truth

Targets remain goals only: OOS directional accuracy >65%, top-decile precision >70%, Sharpe >=2.5, Sortino >=3.5, maximum drawdown <=10%, average-win/average-loss magnitude >2.0, aligned after-cost benchmark outperformance, IS/OOS accuracy gap <=15 percentage points.

Current authoritative small evidence:
- 5 days;
- 8 trades;
- 4 wins / 4 losses;
- win rate 50%;
- gross P&L `-101258.25`;
- costs `1378.10`;
- net P&L **`-102636.35`**.

**AlphaTruth = `INSUFFICIENT_EVIDENCE`.** Mechanics proof is not performance proof. No profitability, live, or model-auto-promotion claim is allowed.

Historical strongest frozen research remains rejected: 489 fills / 492 holdout days; Sharpe `-1.3979`; Sortino `-3.4160`; MDD `52.3395%`; compounded return `-46.7306%`; promotion=false.

Factor/model decay trigger: **NOT_PROVEN / NOT_EVALUABLE**. No `RESEARCH_REQUIRED`; no silent retraining.

## 6. OperationsTruth / SRETruth

- PR #121 observability: **OPEN**, not runtime authority.
- PR #125 OperationsTruth/SRETruth: **OPEN**, not runtime authority.
- Phase-1 typed GCP inventory: **NOT_PROVEN at runtime** because recent Cloud Shell follow-up lost active gcloud auth and returned `API_ERROR` for later inventory sections; those errors must not be interpreted as empty resources.
- Earlier successful snapshot proved Artifact Registry and Cloud Build resources; Pub/Sub/monitoring/alert/uptime emptiness is not upgraded to `PROVEN_EMPTY` until an authenticated authoritative query succeeds.
- SLO scorecard: **NOT_PROVEN**; missing metrics never default green.
- Targets only: availability >=99.95%, API successful-request P95 <300ms, broker read success >=99.9%, token rotation success 100%, synthetic success >=99.9%, MTTR decreasing, false-alert rate decreasing, automated-recovery rate increasing.
- Incident class: **infrastructure/IAM — Firestore runtime authorization**.
- Bounded remediation attempts: two exact-current candidate failures reproduced the same 403 after successful port bind.
- Further code retry before IAM completion is not justified.

## 7. `conflict_120826_0310` salvage lane

Fresh divergence:
- `main` is **187 commits ahead** of `conflict_120826_0310`;
- conflict branch is **6 commits ahead** of `main`;
- merge base: `5d1ec87a43c5778f6d010b91dc3adcd6a22ae797`;
- status: **DIVERGED / STALE / UNTRUSTED INTAKE**;
- wholesale merge/rebase-overwrite remains rejected.

Selective policy:
- connection-stability concepts: ADAPT;
- broker token-health UI/read model: ADAPT on current main;
- real-data Multibagger ideas: ADAPT only after P0/data-contract review;
- F&O eligibility/health digest: ADAPT after truth review;
- legacy token writer: REJECT;
- LoginPage/AuthGate/dashboard-key restoration: REJECT;
- Emergent webhook/runtime authority: REJECT;
- Render/local runtime authority: REJECT;
- generated reports/dist as source authority: REJECT.

Committed plaintext credential incident remains OPEN. Never quote/merge the value; treat affected credential as exposed until independent rotation proof. No shared-history force rewrite without explicit authorization.

## 8. Current checkpoint

- Current audit `main` before this update: **`6ca4acebd74f8f8aa64420bc2cddd3a3146eecd8`**.
- Application/source authority: **`0acf66ebf45049fbe8c6b1bc6c5912895aceda3e`**.
- Audit-head Global Safety CI: **PASS**, run `31557528488`.
- Primary P0 step: **13/14/15 blocked at genuine Firestore IAM boundary**.
- Latest exact deployment: `31555951427` = **FAIL**.
- Serving revision: `genesis-system3-web-00199-tq5` = **100%**.
- Failed candidate: `genesis-system3-web-00214-xot` = **0%**.
- Root cause: **PROVEN Firestore `batch_get_documents` 403 after successful port bind**.
- PR #128: MERGED; 22-tab/44-image harness source-authoritative, runtime proof pending.
- MutationPolicy: CI/source partial, runtime not run.
- Dhan: disconnected / `TOKEN_EXPIRED_OR_INVALID`; version 50 creation is not recovery proof.
- Scheduler: still web-SA runtime identity; migration stale.
- AlphaTruth: **INSUFFICIENT_EVIDENCE**.
- OperationsTruth inventory: **NOT_PROVEN runtime**.
- SLO scorecard: **NOT_PROVEN**.
- Incident/remediation: external Firestore IAM incident proven; two bounded code/deploy attempts exhausted for this unchanged cause.
- Factor decay: **NOT_PROVEN / NOT_EVALUABLE**.
- Observability: PR #121 open.
- OperationsTruth: PR #125 open.
- Salvage divergence: `main +187`, conflict `+6`.
- Real-money readiness: **NO**.
- LIVE: **OFF / LOCKED**.
- Real orders attempted: **0**.
- What remains before assistant-owned work can resume: authoritative proof that `roles/datastore.user` is bound to `genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com`.
- **USER ACTION REQUIRED: YES — only the narrow Firestore role binding and metadata verification in Section 1. No PIN/TOTP/token/API key should be sent to chat.**
