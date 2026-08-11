# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 17:50 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Current `main` HEAD verified this iteration: `6a8f728d58d00cc91381306f8535225b2819777a`.
- Material application change occurred: PR #99 merged at `6a8f728d...`; therefore the current application/source baseline is now `6a8f728d58d00cc91381306f8535225b2819777a`, replacing the former `b70af343...` baseline.
- Compare former application baseline `b70af343... -> 6a8f728d...`: 24 commits ahead, 0 behind. Runtime code changed only in `dashboard/backend/app.py` and `dashboard/backend/cloud_paper_engine.py`; the other changed path is this master audit report.
- PR #99 is MERGED. PR #98 remains OPEN at `74f5b685...`; PR #97 remains OPEN at `29e7b2cf...`.
- Exact PR #99 head `e5fcfc8259f1d3f20f101e4e53ec369065644cc8` had three observed successful PR-triggered workflows: `Genesis System3 Global Safety CI`, `GCP Stage 2 Safety Checks`, and `GCP Dhan Token Fix CI`.
- The merge commit `6a8f728d...` has no workflow runs returned by the available commit-workflow connector, so exact merged-revision CI/deployment proof is still **NOT PROVEN**.
- Google Cloud is the only accepted deployment target. Render-era operational assumptions remain migration debt/non-authority.
- Audit posture remains ANALYZER/PAPER. Live order placement, modification, cancellation and routing are prohibited.
- This Markdown is the single continuously maintained audit/remediation authority.

## 1. Executive verdict

| Area | Verdict | Canonical solution / implementation state |
|---|---|---|
| Exact deployment revision proof | **FAIL / NOT PROVEN** | `DeploymentTruth` — READY TO PATCH |
| Dashboard auth/session | **FAIL / P0-P1** | `SessionTruth` — READY TO PATCH |
| Mutation authorization | **FAIL / P0-P1** | `MutationPolicy + CapabilityManifest` — READY TO PATCH |
| Global mode/order safety | **FAIL / P0** | `SafetyTruth + ExecutionEligibility` — READY TO PATCH |
| Broker/account truth | **FAIL / P0-P1** | `AccountTruth + AccountSnapshotCoordinator` — READY TO PATCH |
| DB/shared state | **FAIL / P0-P1** | `StateTruth + domain CAS` — READY TO PATCH |
| WebSocket/REST truth | **FAIL / P0-P1** | `StreamTruth` — READY TO PATCH |
| Option chain/Greeks | **FAIL / P0-P1** | `OptionChainTruth` — READY TO PATCH |
| Scanner/ranker | **FAIL / P0-P1** | `ScannerTruth` — READY TO PATCH |
| Performance/concurrency | **FAIL / P0-P1** | `WorkCoordinator + SnapshotScheduler` — READY TO PATCH |
| Paper lifecycle/reconciliation | **PARTIAL PATCH / STILL FAIL P0** | `PaperLedger + ReconciliationService` — READY TO PATCH |
| Pre-trade risk authority | **FAIL / P0** | `PreTradeRiskService` — READY TO PATCH |
| AI/prediction provenance | **MISSING / P0-P1** | `PredictionTruth + ModelArtifactManifest` — READY TO PATCH/DESIGN |
| Accessibility/responsive browser proof | **FAIL / P1** | `AccessibleWorkstationShell` — READY TO PATCH |
| Real-money readiness | **NO** | LIVE stays OFF/LOCKED |

## 2. System-wide invariant

Missing, stale, parse-failed, timed-out, unauthenticated, overloaded, contradictory, corrupt or unproven evidence must never become PASS, LIVE, safe, fresh, zero-risk, zero-P&L, zero-Greek, calibrated confidence, broker-connected, account-empty, deployed-current or trade-ready through defaults.

HTTP success, GitHub workflow green, Cloud Run READY, profile connectivity and image tag equality are each insufficient on their own. Transaction authority must be server-owned, revision-bound and evidence-backed. UI and JSON/CSV files are projections only.

## 3. Retained canonical remediation groups

### AUTH-001..011 — SessionTruth
P0-P1 / FIX-REQUIRED. Login contract mismatch, raw API-key persistence, deterministic session token, browser-only expiry, missing server revocation and incomplete throttling/CSRF/idempotency proof remain open. Target: opaque server session, HttpOnly/Secure/SameSite cookie, authoritative issued/expiry/revocation, no reusable browser API key. Status: READY TO PATCH.

### MUT-001..008 — MutationPolicy + CapabilityManifest
P0-P1 / FIX-REQUIRED. Every POST/PUT/PATCH/DELETE must declare a capability and associated auth, CSRF, idempotency, audit and domain gate. Unknown mutation fails closed/CI. LIVE_MUTATION hard denied in analyzer/paper. Status: READY TO PATCH.

### SAFE-001..008 + RISK-001..009 — SafetyTruth + PreTradeRiskService
P0 / FIX-REQUIRED. One authoritative SafetyTruth and one immutable ExecutionDecision are required before any paper/live-adjacent mutation. `UNKNOWN|STALE|ERROR` inhibits. Kill-switch OK is necessary but never sufficient. Status: READY TO PATCH.

### ACCOUNT-001..008 — AccountTruth
P0-P1 / FIX-REQUIRED. Semantic Dhan error bodies, zero/default normalization, mixed account generations, connectivity/account conflation and missing risk binding remain open. Zero account exposure is valid only when `EMPTY_PROVEN`. Status: READY TO PATCH.

### STATE-001..012 — StateTruth + domain CAS
P0-P1 / FIX-REQUIRED. Firestore/shared state must be GCP authority; local files become projections. Domain revisions/CAS reject stale writers; shared-state failure becomes read-only degraded state. Status: READY TO PATCH.

### CHAIN-001..014 — OptionChainTruth
P0-P1 / FIX-REQUIRED. Null-to-zero, weak expiry/cache identity, source invention, parser collapse and incomplete Greeks remain open. Every row must carry provider/event/receive/age/TTL/schema/normalizer/evidence truth. Status: READY TO PATCH.

### WS-001..011 — StreamTruth
P0-P1 / FIX-REQUIRED. Socket-open is not market-stream health. Add heartbeat, sequence, schema, event/receive times and stale/out-of-order rejection; older REST cannot overwrite newer WS. Status: READY TO PATCH.

### SCAN-001..010 — ScannerTruth
P0-P1 / FIX-REQUIRED. Remove high-watermark rank carryover/restamping and auto-eligibility. Latest observation always replaces old even when gain falls; stale rows evict. Status: READY TO PATCH.

### PERF-001..009 — WorkCoordinator
P0-P1 / FIX-REQUIRED. Bounded domain workers, singleflight, serialized paper worker, completion-driven polling, event-loop and queue observability required. `PERF-004` remains open despite new manual-close lock because `/api/paper/tick` command idempotency/serialization is not fully solved. Status: READY TO PATCH.

### ML-001..014 — PredictionTruth
P0-P1 / FIX-REQUIRED. Immutable prediction/model artifact evidence, temporal validation, calibration and reconciled after-cost outcome linkage remain missing. Status: READY TO PATCH/DESIGN.

### UI/A11Y
P1 / FIX-REQUIRED. `UI-001` remains `LOCKED-20X / FIX-REQUIRED`. All Tier-0 badges must consume typed backend truth; responsive/accessibility/browser-console proof remains required. Status: READY TO PATCH.

## 4. Regression verification — PR #99 paper manual-close patch

### PAPER-017 — direct projection-file mutation

**Previous proof:** `/api/positions/{position_id}/close` directly edited `positions_live.json`.

**New code proof:** PR #99 changes the route to obtain `CloudPaperEngine` and call `engine.close_position_by_id(position_id)`. The direct JSON file-surgery block was removed.

**Assessment:** the specific direct-file-authority defect is **PATCHED in source**, not yet fully VERIFIED. The route no longer directly writes `positions_live.json`.

**Remaining closure conditions:** exact merged-revision tests must prove manual close + concurrent tick + restart cannot resurrect the position; persistence failures must fail closed; duplicate close idempotency and immutable event evidence are still absent.

**Status:** `PATCHED / UNPROVEN` (not CLOSED).

### PAPER-018 — competing manual-close vs engine in-memory authority

**New code proof:** `CloudPaperEngine` now owns `close_position_by_id()` and uses the same `open_positions/closed_positions` state that produces projections. A `threading.Lock` serializes `step()` and manual close within one engine instance.

**Assessment:** the concrete same-process dual-authority/race identified earlier is materially reduced. However this remains an in-memory/file-state design, not an append-only event ledger; no cross-process/distributed lock, command idempotency, position revision or reconciliation checkpoint is present.

**Status:** `PATCHED / PARTIAL / UNPROVEN`.

### New regression concern from PR #99

`close_position_by_id()` closes using the stored `current_price` (falling back to `entry_price`) and immediately persists the result. It does not require a current quote snapshot ID, quote freshness, ExecutionDecision, PreTradeRisk/SafetyTruth, idempotency key or position revision. Therefore PR #99 fixes the concrete resurrection path but does not satisfy the target institutional close lifecycle.

**Required next step:** convert manual close to `ClosePositionIntent` through MutationPolicy -> SafetyTruth -> fresh market truth -> PreTradeRisk/ExecutionDecision -> serialized PaperMutationWorker -> immutable close/fill/position event -> reconciliation.

## 5. Latest deep slice — Google Cloud deployment/runtime provenance

### GCP-012 / P0 — deployment proof uses image tag, not immutable Artifact Registry digest

**Exact proof:** `scripts/gcp_cloud_run_auto_deploy.py` builds an image with a unique tag containing a short SHA plus timestamp and patches Cloud Run with that tag. `scripts/gcp_runtime_evidence.py` records `container.image`, revision and `DEPLOY_GIT_SHA`, but does not resolve/store the immutable image `sha256:` digest as the primary deployment identity.

**Root cause:** source identity and runtime artifact identity are linked by mutable metadata/tag rather than a cryptographic artifact digest chain.

**Impact:** tag/SHA agreement cannot independently prove which image bytes a revision executed; rollback and exact-revision incident forensics are weaker.

**Files:** `scripts/gcp_cloud_run_auto_deploy.py`, `scripts/gcp_runtime_evidence.py`, `.github/workflows/cloud-run-auto-deploy.yml`, Readiness/Proof UI.

**Target:** `DeploymentTruth {source_sha, cloud_build_id, artifact_uri, image_digest, cloud_run_revision, traffic_percent, runtime_reported_sha, deployment_policy_revision, evidence_id}`.

**Implementation:** after Cloud Build SUCCESS, query Artifact Registry/build results for digest; deploy by digest (`image@sha256:...`) or record resolved digest and verify Cloud Run revision digest; runtime evidence must compare source SHA + build ID + digest + revision.

**Migration:** retain human-readable tags as aliases only; never use tag match as closure proof.

**Security/safety:** deployment proof collector is read-only and must not read secret payloads.

**Tests/PASS:** altered tag pointing to different digest is rejected; only exact digest+SHA+revision chain passes; rollback names exact prior digest/revision.

**Rollback:** inability to resolve digest => `DEPLOYMENT_NOT_PROVEN`; no readiness promotion.

**Status:** READY TO PATCH / FIX-REQUIRED.

### GCP-013 / P0-P1 — web runtime identity is also Dhan rotator and scheduler identity

**Exact proof:** `cloud-run-auto-deploy.yml` reads the Cloud Run runtime service account into `RUNTIME_SA`, grants it Secret Manager access to client ID, Dhan access token, PIN, TOTP, dashboard API key and worker token, grants token-version-adder, deploys the Dhan rotation job using the same account, grants the same account Run Job invoker and configures Cloud Scheduler OAuth using the same account.

**Root cause:** web serving, privileged credential rotation and scheduled invocation are not separated by least privilege.

**Impact:** compromise of the web runtime identity expands blast radius to PIN/TOTP and token-write/rotation permissions.

**Files:** `.github/workflows/cloud-run-auto-deploy.yml`, WIF/bootstrap/IAM docs/scripts, Cloud Run/Job/Scheduler deployment config.

**Target identities:** `system3-web` (read-only runtime secrets only), `system3-dhan-rotator` (Dhan PIN/TOTP/token write only), `system3-scheduler-invoker` (Run Job invoke only), `system3-deployer`, `system3-evidence-reader`.

**Implementation:** pre-provision identities/IAM; stop granting privileged secret roles to web SA; job uses rotator SA; scheduler uses invoker SA; evidence artifact records identities and effective capabilities.

**Migration:** prove current runtime first, then dual-stage cutover; revoke web PIN/TOTP/token-write roles only after rotator/scheduler tests pass.

**Tests/PASS:** web SA denied PIN/TOTP access and secret version add; rotator denied web/API unrelated secrets; scheduler can invoke only named job; evidence reader cannot mutate.

**Rollback:** if split fails, disable scheduled rotation and keep read-only web runtime; do not broaden web SA again automatically.

**Status:** READY TO PATCH / FIX-REQUIRED.

### GCP-014 / P1 — long-lived `GCP_SA_KEY` fallback remains active

**Exact proof:** deploy workflow prefers WIF only when variables are present; otherwise it authenticates with `${{ secrets.GCP_SA_KEY }}`. The WIF setup document explicitly calls this a temporary fallback and instructs deletion only after WIF-only proof.

**Root cause:** migration fallback can silently preserve long-lived deploy credentials indefinitely.

**Impact:** key exfiltration/reuse risk and weaker auditable identity provenance.

**Target:** WIF mandatory for automatic deploy; legacy key path disabled after one independently proven WIF migration artifact.

**Implementation:** add explicit migration deadline/state; after proof remove legacy auth step and secret; CI fails if WIF variables missing.

**Tests/PASS:** WIF-only deployment succeeds twice; legacy key disabled/deleted; workflow without WIF fails closed before deployment.

**Status:** READY TO PATCH.

### GCP-015 / P1 — deployment is not one atomic canonical Cloud Run spec

**Exact proof:** `gcp_cloud_run_auto_deploy.py::_patch_service()` sets scaling `minInstanceCount=1,maxInstanceCount=10`, while the workflow later executes `gcloud run services update --min-instances=0 --max-instances=1`. `deploy/gcp/README.md` describes zero minimum/one maximum as the safety invariant. If the workflow fails between these stages, an intermediate revision/service configuration differs from the documented target.

**Root cause:** deployment desired state is spread across multiple mutation steps and scripts.

**Impact:** configuration drift, transient unintended scaling/cost/concurrency and harder rollback/provenance.

**Target:** one reviewed canonical Cloud Run service specification applied once; all safety env/scaling/service-account/secret bindings are part of the same desired-state change.

**Implementation:** central deployment manifest/config builder; remove conflicting later update; post-deploy validation reads exact revision and compares to desired spec.

**Tests/PASS:** injected failure after deploy cannot leave noncanonical scaling; desired-vs-actual diff = 0 for safety fields.

**Rollback:** redeploy previous canonical digest+spec, not partial `gcloud update` mutations.

**Status:** READY TO PATCH.

### GCP-016 / P1 — deployment workflow mutates IAM and operational scheduler topology on every deploy

**Exact proof:** every auto-deploy adds Secret Manager IAM bindings, adds Run Job invoker, deploys/reconfigures the rotation job and creates/updates Cloud Scheduler.

**Root cause:** application deployment and infrastructure/IAM administration are coupled.

**Impact:** a source-code deploy principal has broad operational mutation scope; IAM drift can be hidden inside normal app deployment; failure modes are harder to isolate.

**Target:** infrastructure/IAM provisioned separately (Terraform/gcloud bootstrap with review); app deployment only builds image and updates the approved Cloud Run revision. Scheduler/rotator changes require their own controlled pipeline.

**Tests/PASS:** standard app deploy makes zero IAM policy changes and zero scheduler topology changes; infra drift is reported, not silently repaired by app deployment.

**Status:** READY TO PATCH.

### GCP-017 / P1 — auto-deploy executes privileged Dhan token rotation immediately

**Exact proof:** deploy workflow runs `gcloud run jobs execute genesis-system3-dhan-token-rotate --wait` after configuring the job.

**Root cause:** application deployment is coupled to credential rotation side effects.

**Impact:** deploy rollback/retry can trigger repeated credential rotation independent of schedule; credential lifecycle evidence becomes coupled to code deployment.

**Target:** deployment validates job configuration/IAM but does not rotate broker credentials. Rotation is Scheduler/manual break-glass with unique rotation event ID and replay control.

**Tests/PASS:** app deploy causes zero token rotations; scheduler execution produces one rotation event; repeated event ID is rejected/no-op.

**Status:** READY TO PATCH.

### GCP-018 / P1 — runtime evidence does not prove traffic ownership of exact revision

**Exact proof:** runtime evidence captures `latestReadyRevision` and service URL but does not record the full traffic allocation and require 100% (or explicitly intended split) to the proven revision before declaring deployment lock.

**Root cause:** latest ready revision is assumed too close to active serving revision.

**Impact:** an older revision could still serve some traffic while proof reports the newest ready revision.

**Target:** record all traffic targets/percentages/tags and require policy match; endpoint probes must bind to the serving revision where possible.

**Tests/PASS:** 90/10 split fails a 100%-current policy; stale tagged revision cannot satisfy deployment proof.

**Status:** READY TO PATCH.

### GCP-019 / P1-P2 — substantial Render-era operational tooling remains executable

**Exact proof:** repository search still returns executable Render-specific tools/scripts and operational docs including `tools/sync_render_secrets.py`, `tools/render_deploy_commit_proof.py`, `tools/render_env_alignment_audit.py`, `scripts/render_worker_mobile_check.sh` and multiple Render runbooks/reports.

**Root cause:** migration retained old deployment-operational code without a single archival/non-authoritative boundary.

**Impact:** an agent/operator can select stale Render tooling, creating contradictory deployment authority and wasted/unsafe remediation.

**Target:** move historical Render material under clearly archived documentation or mark executable entry points hard-disabled with message `GCP is canonical deployment target`; remove Render from current runbooks/automation decisions.

**Tests/PASS:** current operational docs/workflows contain zero instructions to deploy/change Render; CI flags new Render runtime authority references outside archive.

**Status:** READY TO PATCH.

## 6. Canonical solution — DeploymentTruth V2

**Status:** READY TO PATCH.

Required chain:

`main source SHA -> Cloud Build ID -> Artifact Registry digest -> Cloud Run revision -> traffic allocation -> runtime reported SHA -> safety/IAM evidence -> immutable evidence ID`.

Required fields:

`DeploymentTruth {state: PASS|STALE|ERROR|UNKNOWN, source_sha, build_id, artifact_repo, image_digest, revision, traffic[], service_account, runtime_sha, safe_env_revision, secret_binding_metadata, scheduler_identity, rotator_identity, deployed_at, observed_at, evidence_id}`.

Ordered implementation:
1. Resolve/store image digest after Cloud Build and deploy/verify by digest.
2. Consolidate Cloud Run desired state into one canonical atomic deployment definition.
3. Record full traffic allocation and require policy match.
4. Split web/rotator/scheduler/deployer/evidence identities and least-privilege IAM.
5. Separate infra/IAM/scheduler provisioning from ordinary app deployment.
6. Remove auto token rotation from app deployment.
7. Complete WIF migration; remove `GCP_SA_KEY` fallback.
8. Add runtime endpoint/evidence showing source SHA, revision and deployment evidence ID without secrets.
9. Archive/hard-disable Render-era operational tooling.
10. Add Readiness/Proof UI drilldown for SHA/build/digest/revision/traffic/IAM/safety.

PASS criteria: exact source SHA, build, digest, revision and intended traffic all match; live flags are OFF; secret payload exposure is false; identity split is least privilege; WIF is keyless; no ordinary app deploy mutates IAM/scheduler or rotates Dhan credentials.

Fail-safe: any missing digest/traffic/IAM/runtime proof => DeploymentTruth UNKNOWN/ERROR, readiness blocked, paper/live-adjacent safety decision inhibited where deployment truth is required, LIVE locked.

## 7. Prioritized remediation roadmap

### P0
1. SessionTruth.
2. MutationPolicy + CapabilityManifest.
3. SafetyTruth + ExecutionEligibility + mandatory PreTradeRiskService.
4. AccountTruth + AccountSnapshotCoordinator.
5. Complete PaperLedger + ReconciliationService; treat PR #99 as partial bridge only.
6. DeploymentTruth V2: immutable digest/revision/traffic and identity split.
7. StateTruth + domain CAS.
8. WorkCoordinator + serialized/idempotent paper mutation worker.

### P1
1. OptionChainTruth.
2. StreamTruth.
3. ScannerTruth.
4. Versioned fill/cost/P&L provenance.
5. WIF-only deploy and remove legacy GCP key.
6. Separate IAM/infra/scheduler/token-rotation pipelines.
7. PredictionTruth linked to reconciled paper outcomes.
8. Responsive/accessibility/browser-console proof.
9. Retire Render-era operational authority.

### P2
Advanced institutional analytics, scenario controls and tuning only after P0/P1 truth contracts are proven.

## 8. Counters / status changes

- `UI-001` remains `LOCKED-20X / FIX-REQUIRED`.
- `PAPER-017`: source status upgraded from READY TO PATCH to `PATCHED / UNPROVEN`; counter remains below LOCKED-20X because patch closure needs independent runtime/test reproductions.
- `PAPER-018`: upgraded to `PATCHED / PARTIAL / UNPROVEN`; long-term ledger/reconciliation solution remains required.
- `PERF-004` remains open; PR #99's instance lock does not provide command idempotency or full paper-worker serialization semantics.
- `GCP-012..019`: NEW, `1/20` each, FIX-REQUIRED.
- No new finding reaches LOCKED-20X.
- No deployment, readiness, profitability or real-money finding is CLOSED.
- LIVE remains OFF/LOCKED; no live order was enabled, placed, modified, cancelled or routed.

## 9. Product-design track — Readiness / Deployment Proof V21

This iteration's required product UI is the real `Readiness / Proof` workspace.

### REQUIRED
- Tier-0 source SHA, image digest, Cloud Run revision, traffic ownership, WIF state, IAM split state, SafetyTruth and LIVE LOCKED.
- Explicit deployment chain: Git SHA -> Cloud Build -> digest -> revision -> traffic -> runtime SHA.
- Revision/traffic table showing source/digest/mode/safety/evidence per serving revision.
- Identity panel separating deployer, web runtime, Dhan rotator, Scheduler invoker and evidence reader.
- Scheduler/token-rotation panel with identity, invoker role, job digest and last evidence; web PIN/TOTP/token-write capability must show NO.
- Operator proof showing deployment state, revision age, runtime/source match, secret-exposure state, rollback revision and redacted evidence export.

### RECOMMENDED
- One-click drilldown to sanitized Cloud Run spec/IAM diff and build provenance.
- Rollback preview to prior known digest/revision with safety policy diff.
- Deployment history with evidence IDs and revision traffic transitions.

### OPTIONAL
- Cost/performance trend by revision after runtime telemetry is authoritative.

## 10. Closure discipline

`PATCHED` means source changed. `VERIFIED/CLOSED` requires exact-revision unit/integration/runtime/browser proof, reproducible evidence IDs, safety regression and independent verification. `LOCKED-20X` means repeatedly reproduced, not fixed. Workflow green, HTTP 200, Cloud Run READY, UI labels or image tags alone can never prove deployment/trading readiness.

## 11. Next deep slice

Inspect the merged PR #99 paper close path and complete Paper mutation authority end-to-end: authentication/capability, idempotency, fresh quote/chain binding, ExecutionDecision, lock scope, persistence failure behavior, restart/replay, duplicate close/tick semantics, fill/cost provenance and reconciliation. In parallel regression-check that GCP deployment remains LIVE OFF and no newly merged route can reach broker place/modify/cancel paths.
