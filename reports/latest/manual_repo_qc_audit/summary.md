# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-12 09:22 IST`

> Single authority for `psw2025-cmd/Genesis_System3`. Google Cloud is the only runtime/deployment authority. Source patch, PR merge, CI green, Cloud Run Ready, or a generated UI image never means CLOSED by itself. Closure requires exact 100%-traffic serving-revision evidence. LIVE remains OFF/LOCKED and no live broker order operation is permitted in this remediation stream.

## 0. Exact source/runtime checkpoint

- Repository: **`psw2025-cmd/Genesis_System3` only**.
- Current `main` HEAD: **`36e24d86e1aed1ae5ddbf77055cabf6e125e58cb`** — report-only head based on UI-proof application source.
- Last merged application/source authority before current security branch: **`0acf66ebf45049fbe8c6b1bc6c5912895aceda3e`** — PR #128, 22-tab/44-image visual-proof harness.
- Active security branch: **`fix/permanent-public-dashboard-no-key`**, currently ahead of `main` by **28 commits / 27 files** before this report update.
- Runtime mode requirement: **ANALYZER/PAPER**.
- LIVE: **OFF / LOCKED**.
- Real broker order operations attempted by this remediation stream: **0**.
- Dashboard visibility requirement: **permanently PUBLIC / READ-ONLY; dashboard credential/session authority REMOVED**.
- Worker ingestion authority: dedicated worker token only; dashboard viewing is never mutation authority.

## 1. Primary P0 position and GCP truth

The former Firestore Step-13 boundary is now **HUMAN-ACTION COMPLETE / RUNTIME REPROOF PENDING**.

Human Cloud Shell proof received:
- active project `system3-openalgo-safe`;
- `roles/datastore.user` successfully bound to `genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com`;
- metadata verification returned the exact binding;
- marker: `FIRESTORE_RUNTIME_IAM_BINDING_COMPLETE`.

Previous exact candidate `genesis-system3-web-00214-xot` at source `0acf66...` is still historical failure evidence only:
- candidate 0% traffic;
- old production `00199-tq5` retained 100%;
- container bound `0.0.0.0:8080`;
- Firestore `batch_get_documents` returned 403;
- application failed closed with `Required Firestore state load failed`;
- Cloud Run PORT/startup-probe message was secondary.

Next primary sequence after current no-dashboard-credential PR passes:
`exact-current deploy -> zero-traffic candidate -> Firestore startup -> exact SHA/digest/revision -> anonymous /ui -> 44 tab screenshots -> MutationPolicy runtime -> broker/rotator/Scheduler proof -> continue P0 chain`.

## 2. Permanent public-dashboard/no-credential forensic program

### Incident / contradiction found

A manual Cloud Run command reintroduced retired configuration by setting the dashboard-key requirement true and mounting the obsolete dashboard-key secret. The credential value was pasted into terminal/chat output and is therefore classified **EXPOSED + OBSOLETE**; it must never be repeated. Application response still stated dashboard authentication was disabled, proving configuration and application authority had diverged.

The other agent claim that current CI requires `REQUIRE_API_KEY=true` is **REJECTED**. Prior current-main CI already expected the public PAPER dashboard without a key. The real problem was retained legacy dashboard credential/session capability plus operator/runtime drift.

### Current branch structural changes

The target invariant is stronger than `REQUIRE_API_KEY=false`: **the retired credential/session surface must be absent**.

Implemented on `fix/permanent-public-dashboard-no-key`:

1. `dashboard/backend/mutation_policy.py`
   - removed dashboard session-create/session-revoke capabilities;
   - public UI never becomes control authority;
   - LIVE mutation/approval remains hard denied;
   - worker ingestion remains dedicated-token only.
2. `dashboard/backend/security_policy.py`
   - public safe reads always allowed;
   - worker push requires dedicated worker token;
   - every other public write fails closed with `PUBLIC_DASHBOARD_READ_ONLY`;
   - obsolete browser credential kwargs are ignored and cannot grant authority.
3. `dashboard/backend/__init__.py`
   - new backend package boundary scrubs retired dashboard credential/session env before any backend submodule import.
4. `dashboard/backend/secure_app.py`
   - scrubs retired env before legacy app import;
   - forces legacy key globals inert;
   - removes live `/api/auth/session` and `/api/auth/logout` routes;
   - leaves only informational GET `/api/auth/status` with `required=false`, `configured=false`, `authenticated=false`, `mode=public_readonly`, `credential_surface=REMOVED`;
   - strips retired dashboard key header/session cookie at outer boundary;
   - preserves independent MutationPolicy and worker authority.
5. deleted `dashboard/backend/session_truth.py` and its tests.
6. `.env.example`
   - no dashboard credential/session environment knob.
7. canonical `scripts/gcp_cloud_run_auto_deploy.py`
   - does not configure a dashboard key flag;
   - removes retired dashboard auth env and both historical dashboard-key secret env names from every candidate;
   - refuses promotion if any retired credential config remains;
   - candidate HTTP proof requires `public_readonly / credential_surface=REMOVED`.
8. `scripts/gcp_runtime_evidence.py` schema v2
   - binds evidence to the actual single 100%-traffic serving revision, not latest-ready/latest-created/template state;
   - any retired dashboard env/secret/plaintext presence is a runtime blocker;
   - compares `GITHUB_SHA` to serving revision `DEPLOY_GIT_SHA`.
9. `scripts/gcp_public_dashboard_runtime_proof.py`
   - requires retired credential surface absent before screenshot capture;
   - requires fixed anonymous public-readonly status contract;
   - captures real deployed `/ui` then all 22 desktop + 22 mobile visuals.
10. new `scripts/public_dashboard_no_key_forensic.py`
   - recursively scans active backend/frontend/scripts/tools/deploy/workflows/config;
   - rejects new dashboard credential/session semantics outside tightly bounded removal/detection files;
   - rejects active direct launcher of `dashboard.backend.app:app`;
   - reports active-files-scanned count and typed proof.
11. deleted obsolete authenticated/key tools:
   - `tools/dashboard_auth_smoke.py`;
   - `tools/dashboard_authenticated_shell_warmup.mjs`;
   - `tools/dashboard_live_ui_proof.mjs`;
   - `tools/dashboard_shell_diagnostic.mjs`;
   - `tools/dashboard_visible_issue_tracker.mjs`;
   - legacy direct-backend `scripts/verify_dashboard.ps1`.
12. CI/tests updated with adversarial drift: even if a process starts with retired dashboard auth variables enabled and dummy key values, the real Cloud Run wrapper must scrub them before import; auth session/logout write routes must not exist and mutation manifest must remain valid.
13. security/WIF docs updated: dashboard credential absence is permanent, WIF is keyless deployment authority, and old dashboard-key/session guidance is retired.

### Closure criteria — NOT YET CLOSED

Required before marking permanent removal VERIFIED/CLOSED:
- recursive forensic gate PASS on exact PR head;
- full Global Safety + GCP Dhan/WIF + priority/workflow gates PASS;
- PR merged without stale-base conflict;
- exact merge-SHA Cloud Run deployment succeeds;
- actual 100%-traffic serving revision has **none** of the retired dashboard credential/session env names or secret mounts;
- `/api/auth/status` proves `public_readonly / credential_surface=REMOVED`;
- `/api/auth/session` and `/api/auth/logout` are absent on serving app;
- `/ui` renders anonymously with no credential prompt;
- 22 desktop + 22 mobile visual proof passes;
- MutationPolicy runtime proof passes independently;
- zero GCP active references to the obsolete dashboard-key secret are proven;
- only then retire/delete obsolete exposed dashboard-key secret through the appropriate human GCP boundary.

The phrase “will never affect anything” is implemented as a fail-closed prevention/detection contract: source CI blocks reintroduction, canonical deployment scrubs drift, runtime proof rejects serving drift. No engineering system can prevent a project owner from making a future manual GCP change outside the repository, but that change must be detected and rejected by the canonical proof chain before closure/promotion.

## 3. Dhan broker and identity truth

Current last public runtime broker evidence remains:
- broker `dhan`;
- mode `ANALYZER`;
- connected **false**;
- error **`TOKEN_EXPIRED_OR_INVALID`**;
- token source `GCP_SECRET_MANAGER_DYNAMIC`;
- canonical `dhan-access-token` version reached **50**;
- version 50 creation alone is not recovery proof because serving broker still rejected it;
- raw token exposed false;
- LIVE false;
- order placement false.

Identity state:
- dedicated rotator SA exists;
- `gs3-scheduler` exists;
- Scheduler runtime still last proved using old web SA, therefore **STALE / MIGRATION PENDING**;
- web runtime still has historical excessive PIN/TOTP/token-version-add grants; remove only after dedicated rotator is proven working;
- canonical vs legacy Dhan token secret authority remains a forensic check after current web deployment succeeds.

## 4. UI proof/review program

PR #128 source authority provides **22 tabs exactly** and **44 required real deployed screenshots**:
- 22 desktop `1600x1000`;
- 22 mobile `430x932`;
- actual single 100%-traffic serving revision only;
- exact `DEPLOY_GIT_SHA` binding;
- active-tab proof, screenshot SHA-256 and no credential/login prompt;
- no order/paper mutation calls;
- every tab starts `PENDING_USER_REVIEW`.

No tab is FINAL until frontend + backend/data contract + exact deployed desktop/mobile visual + loading/error/stale behavior + user review are complete.

Current state: **proof harness merged; exact-current visuals pending successful deployment after this security branch**.

## 5. Runtime performance/SRE incident truth

New independent defects proven from Cloud Run logs and human endpoint profiling:
- old serving revision exceeded **1024 MiB** memory with observed **1044 MiB**, causing instance termination;
- `/api/trader/requirements`, `/api/portfolio/unified`, `/api/qc/runtime` exceeded 15s diagnostic cap;
- several broker endpoints took seconds; `/prediction/all` observed >30s;
- backend emitted `ValueError: Out of range float values are not JSON compliant` for at least one response path;
- human manually raised service to `2Gi`, `2 CPU`, concurrency `80` on the old revision.

Important: canonical deployer currently still specifies `1Gi / 1 CPU / concurrency 50`; therefore the manual resource increase is **NOT authoritative or durable** and OOM regression remains OPEN. This must be handled as a separate repo-controlled SRE patch after the no-dashboard-credential PR, with evidence rather than permanent manual drift.

OperationsTruth/SRETruth:
- PR #121 observability: OPEN / must be refreshed against current main before merge;
- PR #125 OperationsTruth: OPEN / must be refreshed against current main before merge;
- SLO targets remain goals, not claims;
- missing monitoring dashboards/alerts/uptime proof must never default green.

## 6. AlphaTruth

Targets remain research goals only: OOS directional accuracy >65%, top-decile precision >70%, Sharpe >=2.5, Sortino >=3.5, MDD <=10%, average-win/average-loss magnitude >2.0, aligned after-cost benchmark outperformance and IS/OOS accuracy gap <=15 percentage points.

Current small evidence: 5 days / 8 trades / 4 wins / 4 losses / 50% win rate / net P&L `-102636.35` after costs.

**AlphaTruth = `INSUFFICIENT_EVIDENCE`.** No profitability, automatic model promotion, live, or real-order authority claim is allowed.

## 7. P0 dependency state

| Dependency | Current truth |
|---|---|
| Permanent public/read-only dashboard credential removal | **PATCHED ON BRANCH / CI+RUNTIME PENDING** |
| Firestore runtime role | **HUMAN BINDING PROVEN / NEW CANDIDATE REPROOF PENDING** |
| Exact-current deployment | BLOCKED until current security PR passes/merges |
| MutationPolicy | source/CI partial; runtime proof pending exact deploy |
| SafetyTruth + ExecutionEligibility | OPEN P0 |
| PreTradeRiskService | OPEN P0 |
| AccountTruth + AccountSnapshotCoordinator | OPEN |
| durable PaperLedger + Reconciliation | PARTIAL / OPEN |
| StateTruth/domain CAS | OPEN |
| DeploymentTruth V2 | PARTIAL; new serving-revision evidence logic patched |
| WorkCoordinator/idempotency | OPEN |
| OptionChainTruth -> StreamTruth -> ScannerTruth -> PredictionTruth | OPEN P1 after P0 |
| Institutional UI/A11Y | OPEN / 22-tab user review pending |
| Real-money readiness | **NO** |

## 8. Conflict/salvage lane

`conflict_120826_0310` remains stale/untrusted intake only. Never merge wholesale. ACCEPT/ADAPT only from fresh current main. Reject LoginPage/AuthGate/dashboard-key restoration, legacy token writers, Render/local runtime authority, generated output authority and unsafe cron/webhook authority.

Committed plaintext credential incident on that branch remains OPEN; never quote/merge the value and treat it exposed until independent rotation proof. No force-rewrite without explicit authorization.

## 9. Current checkpoint

- Main HEAD: `36e24d86e1aed1ae5ddbf77055cabf6e125e58cb`.
- Last merged application source: `0acf66ebf45049fbe8c6b1bc6c5912895aceda3e`.
- Current branch: `fix/permanent-public-dashboard-no-key`, ahead by 28 commits / 27 files before this report commit.
- Firestore role: **BOUND + VERIFIED by human Cloud Shell**.
- Dashboard-key incident: **EXPOSED/OBSOLETE credential + manual runtime drift; structural retirement patch in progress**.
- Broker: disconnected / `TOKEN_EXPIRED_OR_INVALID` / version 50 not recovery proof.
- Scheduler: old web-SA identity last proved; migration pending.
- UI: 22-tab/44-image runtime proof pending.
- OOM/latency/NaN JSON defects: OPEN.
- AlphaTruth: `INSUFFICIENT_EVIDENCE`.
- SRETruth: OPEN.
- LIVE: OFF/LOCKED.
- Real order operations attempted by this remediation stream: 0.
- **USER ACTION REQUIRED: NO at this checkpoint. Repository/CI work is controllable by assistant. Do not create, rotate, mount, paste, or test any dashboard API key.**
