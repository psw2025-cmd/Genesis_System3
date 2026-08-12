# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-12 05:26 IST`

> This file is the single authority for the current Genesis System3 remediation stream. `PATCHED`/`MERGED`/green PR CI never imply `CLOSED`; exact serving-revision runtime proof is required where applicable. Historical milestones are retained below in condensed evidence form. Quantitative targets are acceptance goals, never current-performance claims unless frozen out-of-sample evidence proves them.

## 0. Scope, revision truth and safety lock

- Repository authority: **`psw2025-cmd/Genesis_System3` only**.
- Deployment target: **Google Cloud only**. Render is non-authoritative migration debt.
- Latest **application/source HEAD on `main`**: **`b6d70db9f2d26c66f235c1e144fbe9a2892fd3f7`** (merge PR #120).
- Runtime posture: **ANALYZER/PAPER**.
- LIVE: **OFF / LOCKED**.
- No live broker order was enabled, placed, modified, cancelled or routed by this remediation stream.
- PAPER dashboard viewing is intentionally **public/read-only**. It must not ask for a dashboard API key.
- Public visibility is never mutation authority. Worker ingestion retains a separate Secret-Manager-backed token and mutation capabilities remain fail-closed.
- Open implementation lanes are not `main` authority:
  - PR #121 observability head `01fe0232ca03f2a46eb1ec92c5a9f5b2ca04e998` — exact-head Global Safety, GCP Stage 2 and GCP Dhan/WIF CI **PASS**; not merged.
  - PR #122 AlphaTruth branch current head after workflow consolidation: `e2c43c968346f311554469833caa3ee327dd02fd` — CI rerun pending at this report update; not merged.
  - `fix/gcp-dhan-rotator-identity` — least-privilege remediation lane in progress; not merged and not runtime authority.

## 1. Smart-cascade position

Mandatory flow:

`1 VERIFY -> 2 SELECT -> 3 ROOT CAUSE -> 4 DESIGN -> 5 PATCH -> 6 TEST -> 7 PR -> 8 CI -> 9 FIX/RETEST -> 10 MERGE -> 11 POST-MERGE VERIFY -> 12 PREP -> 13 USER GCP ONLY IF GENUINELY REQUIRED -> 14 DEPLOY VERIFY -> 15 RUNTIME TEST -> 16 USER DHAN AUTH ONLY IF REQUIRED -> 17 FULL EVIDENCE -> 18 CLOSED`

### Current production position

**STEP 13 — genuine Google Cloud IAM human boundary.**

PR #120 deliberately removed the false requirement that the deployment identity must inspect/mutate project IAM before deployment. Exact `main` then reached a real zero-traffic candidate. That candidate reproduced the actual Firestore permission failure at runtime. The remaining production blocker is therefore not a dashboard-key issue and not a speculative preflight: the dedicated Cloud Run web runtime genuinely lacks the Firestore data role required by the fail-closed state backend.

**USER ACTION REQUIRED: YES — one narrow Google Cloud IAM binding only. No secret/token/PIN/TOTP is requested.**

Repo-side observability, broker-identity hardening and AlphaTruth research-evaluator work continue in parallel without weakening this boundary.

## 2. Current executive verdict

| Area | Verdict | Evidence / next condition |
|---|---|---|
| PAPER dashboard view without API key | **VERIFIED / CLOSED for stated requirement** | Real `/ui` runtime proof previously passed; key prompt paths removed from active frontend source |
| Dashboard API-key workflow semantics | **PATCHED / CI VERIFIED** | PR #116 + #117 removed obsolete key-absence and self-matching false failures |
| Active dashboard credential-entry UI | **PATCHED / CI VERIFIED** | PR #119 removed LoginPage/useAuth and converted AuthUnlock to passive public-read contract error |
| Firestore runtime authority | **BLOCKED — STEP 13** | exact candidate `genesis-system3-web-00211-jol` failed with Firestore 403; web runtime needs `roles/datastore.user` |
| Current exact-main deployment | **BLOCKED / NOT SERVING** | run `31545671126`; candidate failed at 0% traffic; old serving revision retained 100% |
| Serving revision safety | **PROTECTED** | candidate failure did not move production traffic |
| MutationPolicy | **PARTIAL / CI VERIFIED, runtime proof pending** | runtime probe cannot close until exact current app can start with required Firestore state |
| 24/7 observability foundation | **PATCHED ON PR #121 / CI VERIFIED / NOT MERGED** | trace correlation, redacted read-only browser synthetic, uptime checks, evidence bucket lifecycle and runbooks; exact-head 3/3 suites green |
| Dhan token rotation algorithm | **EXISTS / READ-ONLY VERIFICATION** | canonical job validates token/profile, uses Secret Manager versions, forces LIVE OFF, calls no order endpoint |
| Dhan rotator IAM separation | **OPEN P0-P1 / FIX LANE ACTIVE** | current main deploy path reuses web runtime identity for PIN/TOTP/token minting; dedicated rotator/scheduler identities required |
| AlphaTruth quantitative evaluator | **PATCHED ON PR #122 / CI IN PROGRESS** | evaluator-first fail-closed protocol; no performance claim and no auto-promotion |
| Current small costed walk-forward | **MECHANICS PASS / PERFORMANCE FAIL-UNPROVEN** | 8 trades / 5 days / 50% win / net P&L `-102636.35`; explicitly not a performance claim |
| Strongest historical frozen research result | **REJECTED** | PR #81 frozen holdout lost money and failed Sharpe/drawdown gates; never promote this model |
| SafetyTruth / ExecutionEligibility | **OPEN P0** | next production dependency after MutationPolicy runtime closure |
| PreTradeRiskService | **OPEN P0** | next dependency after SafetyTruth |
| AccountTruth | **OPEN P0-P1** | not yet authoritative for risk decisions |
| PaperLedger/Reconciliation | **PARTIAL / OPEN P0** | PR #99 fixed one dual-authority route; durable append-only lifecycle remains |
| StateTruth | **OPEN P0-P1** | Firestore is required; domain CAS/versioned authority still incomplete |
| DeploymentTruth V2 | **PARTIAL / OPEN P0** | serving-revision binding/digest/IAM identity chain still incomplete |
| WorkCoordinator/idempotency | **OPEN P0-P1** | pending |
| OptionChainTruth / StreamTruth / ScannerTruth / PredictionTruth | **OPEN P1** | pending after P0 chain; AlphaTruth becomes PredictionTruth evaluation dependency |
| Institutional UI/A11Y | **OPEN P1** | one real desktop render proven; responsive/keyboard/axe/console proof incomplete |
| Profitability proven | **NO** | strongest large frozen test is negative; current small proof is also net negative |
| Real-money readiness | **NO** | LIVE stays OFF/LOCKED |

## 3. Dashboard no-key remediation — exact evidence

### Previously runtime-verified product behavior

PR #107 merged as `a875876ecf64a44706b3fc57fe0a3f8f00991337` and PR #108 merged as `7a127f5452d0b337db7d6af294f21d4879dd78a0`.

Exact Cloud Run Auto Deploy run `31507282801` succeeded and published:
- `public-dashboard/runtime-proof = SUCCESS`;
- `cloud-run/runtime-proof = SUCCESS`.

Real headless-Chrome `/ui` evidence proved:
- actual SYSTEM3 product UI rendered;
- no dashboard API-key prompt rendered;
- no API key used;
- PAPER visible;
- LIVE OFF visible;
- anonymous `/ui`, `/api/auth/status`, `/api/state` and `/api/health` access succeeded;
- `REQUIRE_API_KEY=false`;
- `API_KEY` not mounted;
- worker token remained separate.

### PR #116 — remove obsolete key-absence workflow failures

PR #116 head `32cfb8fdfc508cd2fb93a245cdb4f2349a196653`, merge **`b7f402ee7ce3fb0f4da682516e38c8c65a82a951`**.

Approved PAPER state:
- `REQUIRE_API_KEY=false`;
- `API_KEY` unmounted;
- API key plaintext exposure = false;
- `dashboard_public_readonly=true`;
- worker secret remains required;
- LIVE flags remain hard OFF.

### PR #117 — eliminate static-guard self-match

PR #117 head `b23a4f63a00cb088f9e6f78dc69aff3a906a7927`, merge **`abe1cabfcf276d78af1cd9c461f8de2562d0ee99`**.

Root cause: static WIF guards embedded the exact forbidden legacy credential marker text and then searched the workflow for that text. The patch constructs legacy markers without embedding literal forbidden tokens and scans executable/non-comment lines.

### PR #119 — remove remaining frontend key-prompt paths

PR #119 head `b89ad1e3bd221e63b8fa8977bd5858f162fc8ac3`, merge **`8126f85f531655f0313cc52a74491a9049410269`**.

Changes:
- `AuthUnlock.tsx` became a passive **Public read contract error** notice;
- obsolete `LoginPage.tsx` deleted;
- obsolete `useAuth.ts` deleted;
- obsolete `scripts/gcp_session_runtime_proof.py` deleted;
- regression tests prevent credential-entry paths from returning.

**Conclusion:** no dashboard API key is required for PAPER dashboard viewing. Do not restore the old browser credential workflow.

## 4. Genuine current deployment blocker — Firestore IAM

### Earlier failed candidate

Exact source `abe1cabfcf276d78af1cd9c461f8de2562d0ee99` reached candidate `genesis-system3-web-00210-huf` in run `31542005028` and failed with Firestore `PermissionDenied: 403 Missing or insufficient permissions`. Candidate traffic remained 0%; `genesis-system3-web-00199-tq5` retained 100%.

### PR #118 — explicit Firestore prerequisite

PR #118 head `fa905fa8428b61ac8b54980e145ae09f0b62853f`, merge **`776eab796a31d081e2f8932ad2e90d4a03983731`**.

Implemented dedicated web runtime identity contract, required `roles/datastore.user`, Firestore-required/fail-closed state, and tests. Its first preflight implementation exposed that the GitHub deployment identity could not inspect project IAM.

### PR #120 — candidate startup is now the permission authority

PR #120 merged to current main **`b6d70db9f2d26c66f235c1e144fbe9a2892fd3f7`**.

Purpose:
- stop requiring deployment automation to possess project-IAM inspection/admin authority;
- keep Firestore mandatory;
- let the guarded 0%-traffic candidate itself prove whether the runtime service account can read Firestore;
- retain sanitized failed-revision forensics and previous-traffic protection.

Exact current-main Cloud Run run **`31545671126`**:
- WIF authentication: PASS;
- static safety/syntax: PASS;
- worker secret prerequisite: PASS;
- non-admin Firestore preflight: PASS;
- frontend production build: PASS;
- Cloud Build: PASS, build ID `4cc219d8-1e88-4318-9551-0962138551bf`;
- previous serving traffic: `genesis-system3-web-00199-tq5 = 100%`;
- candidate created: `genesis-system3-web-00211-jol`;
- candidate traffic: **0%**;
- candidate Ready: **False / HealthCheckContainerError**;
- sanitized traceback: `google.api_core.exceptions.PermissionDenied: 403 Missing or insufficient permissions` from Firestore state load;
- terminal application error: `RuntimeError: Required Firestore state load failed`;
- production traffic remained on prior revision;
- exact-SHA `cloud-run/runtime-proof`: **FAIL**;
- LIVE remained OFF/LOCKED.

**Conclusion:** Step 13 is independently reproduced by real candidate startup. The fail-closed Firestore behavior and zero-traffic deployment guard worked as designed.

## 5. Step-13 required Google Cloud action

Grant only the required predefined Firestore data role to the dedicated web runtime service account:

```bash
gcloud projects add-iam-policy-binding system3-openalgo-safe \
  --member="serviceAccount:genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com" \
  --role="roles/datastore.user" \
  --condition=None
```

Optional read-back proof:

```bash
gcloud projects get-iam-policy system3-openalgo-safe \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/datastore.user AND bindings.members:serviceAccount:genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com" \
  --format="table(bindings.role,bindings.members)"
```

Do **not** send any GCP credential, service-account key, broker PIN, TOTP or token into chat.

After this binding is confirmed, the assistant-owned cascade resumes:
1. rerun exact current `main` deployment;
2. candidate startup must prove Firestore access;
3. prove `/ui` anonymous/read-only behavior and capture real product screenshot;
4. prove MutationPolicy runtime allow/deny matrix without broker-order action;
5. promote only the exact proven revision to 100%;
6. verify serving SHA/revision/image digest/traffic/safety;
7. fix/retest any further failure before advancing P0.

## 6. P0-2 MutationPolicy status

Merged foundations:
- PR #102 CapabilityManifest (`1d7e06a0f661a873528d96bcc685dc7b0af87f58`);
- `secure_app.py` capability-aware runtime policy;
- UNKNOWN/live mutation/live approval fail-closed;
- public reads do not create mutation authority;
- worker ingestion uses separate worker authority.

**Current status: PARTIAL / CI VERIFIED / RUNTIME PROOF BLOCKED BY STEP 13.**

## 7. DeploymentTruth correction still open

`scripts/gcp_runtime_evidence.py` can still conflate service-template/latest-candidate metadata with the actual 100%-traffic serving revision. DeploymentTruth V2 must:
- resolve actual serving traffic first;
- describe that exact revision;
- read image/service account/safe env/`DEPLOY_GIT_SHA` from the serving revision;
- report 0%-traffic candidate separately;
- bind source SHA to immutable image digest/build ID/revision/traffic.

**Status: OPEN / READY TO PATCH after Step-13 deployment resumes.**

## 8. 24/7 observability and self-remediation lane — PR #121

PR #121 title: `feat(observability): add traced read-only 24x7 monitoring foundation`.

Exact head: **`01fe0232ca03f2a46eb1ec92c5a9f5b2ca04e998`**.

Exact-head CI:
- Genesis System3 Global Safety CI: **PASS**;
- GCP Stage 2 Safety Checks: **PASS**;
- GCP Dhan Token Fix/WIF CI: **PASS**.

Implemented on the PR branch:
- existing structured logger extended to validated `x-request-id`, `x-trace-id` and W3C `traceparent` correlation;
- safe response metadata for serving revision/deploy SHA;
- read-only Playwright `/ui` synthetic;
- network timing + console warn/error + failure screenshot + Playwright trace;
- HAR scrub removes request/response bodies, cookies, query values and sensitive headers before persistence;
- success evidence sampling; failures retained;
- private uniform-access GCS evidence bucket lifecycle design;
- dedicated observer identity with object-creator only;
- dedicated Scheduler invoker identity with job-invoker only;
- 5-minute full browser synthetic design plus 1-minute `/api/health` and `/ui` uptime monitoring;
- startup-crash, token-rotation and high-error-rate fail-safe runbooks;
- no login/API key, no Dhan PIN/TOTP, no order placement, no LIVE authority.

Deliberately not copied from the external agent brief:
- no broker/sandbox order as a token test;
- no `secretmanager.admin` for monitoring;
- no blind redeploy/restart loop;
- no fake 30-second Cloud Scheduler cadence;
- no continuous real-user HAR/RUM capture without a consent/privacy design.

**Status: READY FOR REVIEW/MERGE FROM CI PERSPECTIVE, but not runtime-verified.** Production deployment remains independently blocked by Step 13.

## 9. Broker token rotation identity separation

The existing canonical `scripts/gcp_dhan_token_rotation_job.py` is safer than the generic external template in one important respect: it validates Dhan token/profile state and explicitly calls **zero order endpoints** while forcing LIVE flags off.

New forensic finding on current main deployment workflow:
- Dhan rotation job is configured using the web runtime service account;
- that identity is granted Dhan client/token/PIN/TOTP secret access and token-version-add capability;
- Scheduler also invokes the rotator using the same runtime identity.

This violates least-privilege identity separation even though the token algorithm itself is safe.

Target identity model:
- `genesis-system3-web`: runtime read-only broker token access needed by dashboard/backend only;
- dedicated Dhan rotator: client/PIN/TOTP access + token-version-add only;
- dedicated rotation Scheduler invoker: run-job invocation only;
- GitHub deployer: deployment/act-as rights only; no standing Secret Manager administrator role.

Branch `fix/gcp-dhan-rotator-identity` exists for this remediation. **Do not claim it implemented on main until its exact diff, tests, PR CI, merge and runtime IAM proof pass.**

## 10. Autonomous Quantitative Alpha Engine / AlphaTruth

### User-supplied target goals

These are acceptance goals, **not current performance**:
- OOS directional accuracy: **> 65%**;
- top-decile signal precision: **> 70%**;
- Sharpe: **>= 2.5**;
- Sortino: **>= 3.5**;
- max drawdown: **<= 10%**;
- average win / average loss magnitude: **> 2.0**;
- aligned same-window return must beat the configured benchmark;
- IS/OOS accuracy gap: **<= 15 percentage points**;
- continuous factor-decay detection should trigger a new research candidate, never silent live promotion.

### Current main evidence — capability PASS is not performance PASS

`reports/latest/recent_backtest_walkforward_proof/costed_walkforward_proof.json` currently records:
- mechanics `pass=true`;
- 5 bhavcopy days (`20260608`–`20260612`);
- 8 trades;
- 4 wins / 4 losses;
- win rate 50.0%;
- total gross P&L `-101258.25`;
- costs `1378.10`;
- total net P&L **`-102636.35`**;
- its own note says the proof validates cost model/pipeline correctness and is **not a performance claim**.

Therefore the old top-level `PASS` must never be interpreted as Alpha/Prediction readiness.

### Strongest historical frozen research evidence — rejected

Open research PR #81 is not main authority and must not be merged/promoted wholesale. Its recorded frozen holdout result was materially negative:
- holdout days: 492;
- filled trades: 489;
- row ROC-AUC: 0.4682;
- win rate: 38.4458%;
- profit factor: 0.8025;
- annualized Sharpe: **-1.3979**;
- annualized Sortino: **-3.4160**;
- maximum drawdown: **52.3395%**;
- compounded total return: **-46.7306%**;
- walk-forward positive-return folds: 0/2;
- mean fold Sharpe: **-2.0923**;
- promotion allowed: false;
- real orders attempted: 0.

PR #84 contains useful leakage/frozen-proof hardening ideas but is also not main authority. Salvage validation concepts only; do not promote its model by implication.

### AlphaTruth V1 implementation — PR #122

PR #122 introduces an evaluator before any new model optimization:
- `config/quant_alpha_targets.json` locks target goals and governance;
- `src/quant/alpha_truth.py` computes and gates OOS directional accuracy, top-decile directional precision, Sharpe, Sortino, MDD, win/loss ratio, profit factor and aligned benchmark return;
- provenance requires exact source/data/feature/model hashes;
- chronological train/validation/frozen-test ordering is mandatory;
- label horizon and purge gap are explicit;
- preprocessing/feature fit must be train-only;
- frozen test tuning is a hard blocker;
- multiple declared strategy trials require a selection-bias-adjusted/deflated-Sharpe probability field;
- default System3 evidence floor is 100 OOS trades and 60 OOS days; this is a project governance floor, not a universal statistical guarantee;
- current 8-trade legacy proof is classified `INSUFFICIENT_EVIDENCE` rather than profitability proof;
- even `PROVEN` returns `model_auto_promotion_allowed=false`, `live_trading_enabled=false`, `real_order_authority=false`;
- five failed research iterations produce `RESEARCH_REJECTED_AFTER_RETRY_BUDGET`; shared Git history is not destroyed with `git reset --hard`.

Initial standalone workflow attempt was correctly rejected by `Workflow Priority Guard` because System3 allows only the permanent priority workflow set. The AlphaTruth tests/evaluation were then consolidated into existing `.github/workflows/ci.yml`; the standalone workflow was deleted. Exact-head CI must pass again before merge.

### Research basis adopted

Research direction incorporated into the evaluator design:
- time-ordered validation rather than random future/past mixing;
- explicit train/test gap/purge for overlapping horizons;
- frozen OOS test discipline;
- multiple-testing/selection-bias awareness instead of trusting the best raw Sharpe;
- benchmark and after-cost returns;
- no self-confidence or single-pass model output as promotion evidence.

**AlphaTruth status: NOT PROVEN. Profitability status: NOT PROVEN. New model optimization has not yet been authorized by evidence.**

## 11. Quant self-correction / continuous-learning policy

The autonomous research loop is allowed to:
1. discover authoritative data/model/backtest paths;
2. build features in isolated research space;
3. train challenger models;
4. tune on train/validation folds only;
5. run deterministic static/tests/evaluator checks;
6. reject weak/decaying factors;
7. repeat for at most five research attempts per candidate lineage;
8. preserve exact trial count and metrics for selection-bias correction;
9. create a new frozen OOS evaluation only under an explicit versioned evidence policy;
10. update this master report with current truth.

It is not allowed to:
- tune repeatedly against the frozen OOS set until metrics pass;
- erase failed trials;
- reset shared/main Git history destructively;
- change the LIVE lock;
- auto-promote a model into execution;
- increase risk sizing because a backtest looks good;
- claim accuracy/profitability from synthetic unit-test fixtures;
- treat 24/7 retraining activity as evidence of improvement.

Factor-decay policy: a rolling Information Ratio deterioration can trigger `RESEARCH_REQUIRED`, but retraining must produce a new isolated candidate and pass AlphaTruth again. "Always improves and never goes backward" is not a valid market guarantee; regressions must be detected, recorded and blocked.

## 12. Remaining P0 order and dependency integration

Production safety order remains:
1. Public PAPER dashboard/no-key — **VERIFIED/CLOSED for viewing requirement**.
2. MutationPolicy runtime enforcement — **runtime proof pending Step 13**.
3. SafetyTruth + ExecutionEligibility.
4. PreTradeRiskService.
5. AccountTruth + AccountSnapshotCoordinator.
6. Durable PaperLedger + ReconciliationService.
7. StateTruth + domain CAS.
8. DeploymentTruth V2 / immutable digest + serving-revision authority + identity separation.
9. WorkCoordinator/idempotency.

P1/data/prediction sequence:
OptionChainTruth -> StreamTruth -> ScannerTruth -> **PredictionTruth + AlphaTruth** -> institutional UI/accessibility/observability.

Quant sizing (Fractional Kelly/volatility parity/mean-variance) remains research-only until PreTradeRiskService and AlphaTruth are both proven. RL/TFT/boosted challengers are not justified merely by model complexity; they must beat simpler baselines under identical frozen evidence.

## 13. Parallel `conflict_120826_0310` salvage lane

Branch remains untrusted/stale intake and must never be merged wholesale.

Security quarantine:
- branch contains a committed plaintext broker credential file;
- never quote the credential value;
- never merge that file;
- affected credential remains classified exposed until independent rotation is proven;
- do not force-rewrite shared history without explicit authorization.

Current salvage classifications:
- `connection_stability.py`: **ADAPT**;
- broker token-health read model/UI: **ADAPT**;
- real-data multibagger engine/UI: **ADAPT / RECOMMENDED after P0**;
- F&O eligibility / health digest: **ADAPT after truth-contract review**;
- branch token mint/persist writer: **REJECT**;
- AuthGate/LoginPage restore: **REJECT**;
- `.emergent` webhook cron as runtime authority: **REJECT**;
- stale generated reports/dist as source authority: **REJECT**;
- unrelated note/editor `design_guidelines.json`: **REJECT**.

## 14. Closure discipline

- Merge != closure.
- PR-head green != merged-revision runtime proof.
- 0%-traffic failed candidate != serving deployment.
- `latestReadyRevisionName`/service template != serving traffic authority.
- Mechanics/backtest-code PASS != quantitative-performance PASS.
- A high in-sample score != frozen OOS proof.
- UNKNOWN/STALE/ERROR/INSUFFICIENT_EVIDENCE remain fail-closed.
- Failed research trials are evidence and must not be erased from selection-bias accounting.
- No profitability or real-money readiness claim is permitted without reproducible lifecycle/risk/model evidence.
- LIVE stays OFF/LOCKED.

**CURRENT USER ACTION REQUIRED FOR PRODUCTION DEPLOYMENT: YES — Step 13, the single narrow Firestore IAM binding in Section 5.**

**CURRENT QUANT USER ACTION REQUIRED: NO. Assistant-owned evaluator/CI/research work continues without secrets or live execution.**
