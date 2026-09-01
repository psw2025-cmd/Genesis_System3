# Genesis System3 — Live Multi-Agent Controller Queue

AGENT_NAME=ChatGPT Controller
AGENT_LANE=D
AGENT_ROLE=Controller / Reconciliation / Next-Task Dispatch

**Status:** ACTIVE / LIVING
**Current program goal:** FULL GCP EXIT. Genesis System3 development, PAPER runtime, state, secrets, scheduling, observability and dashboard work must move to the laptop/local stack. Target steady state = zero intentional GCP dependency and zero intentional recurring GCP spend.

## Mandatory read order
1. `docs/control_plane/GENESIS_SYSTEM3_BILLING_LAPTOP_FIRST_SSOT.md`
2. this file
3. latest Issue #188
4. current remote `main`
5. relevant PR/workflow ownership

Every shared write begins with `AGENT_NAME=`, `AGENT_LANE=`, `AGENT_ROLE=`.

## LIVE CONTROLLER RECONCILIATION — 2026-09-01 after B-Z0
Current remote main independently checked by ChatGPT Controller: `e411fb57d576f9e68ab4752e87209859b6f9e11e`.

### B-Z0 Google/AGI evidence received — CONTROLLER STATUS = PARTIAL / NEEDS CORRECTION + INDEPENDENT VERIFY
Google/AGI reported:
- all 9 Cloud Scheduler jobs paused;
- `genesis-system3-web` minScale 1 -> 0, maxScale 10 -> 1, CPU throttling enabled;
- `_Default` Logging exclusion `emergency-health-200` created;
- Cloud Run service/jobs, Secret Manager, Artifact Registry, Storage, Pub/Sub, Firestore and billing account still exist.

This is useful emergency cost-stop evidence but **NOT accepted as final PASS yet** because it is agent self-report and two important issues remain:

1. **Over-broad Logging exclusion:** reported filter excludes every Cloud Run request with `httpRequest.status=200`, not only health probes. That can remove successful PAPER/API/dashboard/proof request evidence. This violates the evidence-retention intent. Correct immediately by narrowing the exclusion to only explicitly proven redundant health endpoints (for example `/api/healthz` and `/api/health`, only successful routine probes) or remove the exclusion once the service is retired. Preserve PAPER lifecycle, prediction/evaluation, broker/token, deploy/revision, production-proof and other material evidence.
2. **Cloud Run still exists and is invokable:** `minScale=0` is cost reduction, not GCP exit. Direct requests or GitHub workflows can still start it. Current main still contains GCP authentication/deploy/recreation paths, including `.github/workflows/cloud-run-auto-deploy.yml`. These must be neutralized through normal GitHub governance.

Also, token-rotation Scheduler is now reported PAUSED. Therefore laptop broker token/session lifecycle becomes urgent: do not let local development silently depend on Secret Manager/Cloud Run rotation after the current token expires.

## LOADED WORK — LANE A / CODEX
Codex is not permitted to stand by. Execute continuously in this order, reprioritizing if root evidence changes:

### A-Z1.1 — Local secret + broker auth independence — P0
- Inventory all runtime secret names/config mappings actually required by current-main laptop PAPER path; never print values.
- Replace ADC/Secret Manager dependency with Windows secure custody (Credential Manager/DPAPI/equivalent).
- Implement/prove local broker token/session/TOTP lifecycle with zero GCP API calls for normal operation.
- Prove restart/relogin/expiry behavior fail-closed and `REAL_BROKER_ORDER_COUNT=0`.
- Produce machine-readable dependency proof showing normal laptop startup has no Secret Manager call.

### A-Z1.2 — Single laptop state SSOT + cloud-state migration — P0
- Resolve the third-state-root contradiction previously found by Claude.
- Inventory every state root used by supervisor/PAPER/API/UI and Firestore.
- Choose one authoritative local runtime state root outside the clean code tree where practical.
- Export/import/reconcile required Firestore/PAPER/history state into local DB/files without fabricating gaps/trades.
- Prove restart uses the same ledger/state root and no split-brain writes occur.

### A-Z1.3 — Forecast freshness root fix — P0
- Fix stale `state/gain_rank_history.json`/other stale-source use so 2026-06-14 history cannot silently generate 2026-09-01 current forecasts.
- Add explicit source/provenance/freshness fields and fail-closed stale behavior.
- Add regression tests reproducing exact stale-source symptom.
- Do not weaken real Dhan quote gate.

### A-Z1.4 — Local replacement for every GCP job/scheduler — P0
- Map all 9 Cloud Run jobs + all 9 Scheduler duties to local supervisor/tasks.
- Implement missing local equivalents, startup/restart/duplicate-worker prevention, missed-run/gap truth and local structured logging.
- Ensure token rotation is local and independent before current broker credentials age out.

### A-Z0G — GitHub GCP recreation kill-switch PR — P0
- Audit all current-main workflows/scripts/configs that authenticate to, deploy, repair, invoke or recreate GCP.
- Create a narrow PR that prevents ordinary main pushes/schedules/workflow chaining from creating/invoking GCP runtime while preserving useful non-GCP CI.
- At minimum inspect: `cloud-run-auto-deploy.yml`, `gcp-dhan-token-rotation.yml`, `gcp-dhan-token-fix-ci.yml`, `gcp-authority-repair.yml`, `system3-runbook-audit.yml`, `live-proof-center.yml`, `full-cloud-audit.yml` and any dependent workflow_run/workflow_call path.
- No deletion of historical evidence; disable/retarget GCP mutation paths cleanly.
- Publish PR + tests + trigger matrix to #188.

After each checkpoint, re-read this queue + #188 and continue. `STANDING BY` is invalid.

## LOADED WORK — LANE B / GOOGLE-AGI
Google/AGI is not permitted to stand by after B-Z0.

### B-Z0.4 — Correct Logging exclusion now — P0
- Read current `_Default` exclusion exactly as applied.
- If it excludes all HTTP 200 Cloud Run requests, replace it with a narrow health-probe-only filter or remove it if safe after runtime retirement.
- Prove retained classes include material PAPER/API/proof/broker/token/deploy evidence plus WARNING/ERROR/CRITICAL/audit.
- Publish exact before/after filter and sample retained/excluded queries. Do not claim exact rupee savings without metered billing rows.

### B-Z0.5 — Independent after-state GCP inventory — P0
Publish fresh actual after-state for:
- Cloud Run services/revisions traffic/min/max/CPU;
- all Cloud Run jobs and executions;
- all Scheduler states;
- uptime checks/Monitoring synthetic probes;
- Pub/Sub topics/subscriptions/push endpoints;
- Logging sinks/exclusions;
- Secret Manager metadata only;
- Firestore/Storage/Artifact Registry/BigQuery/Firebase;
- IAM/WIF/service accounts relevant to recreation;
- billing link/project state.
Classify every resource: `STOPPED`, `PAUSED`, `STILL_BILLABLE`, `MIGRATE_THEN_DELETE`, `DELETE_NOW_SAFE`, `OWNER_ONLY`.

### B-Z0.6 — Stop remaining automatic invokers — P0
- Disable/pause Monitoring uptime checks and any Pub/Sub push/other automated path that can wake Cloud Run, if present and not required for migration.
- Do not wait for PAPER perfection.
- Record before/after evidence.

### B-Z2 — Delete components as Lane A proves local independence
- Cloud Run service + all jobs -> delete after local replacement proof.
- Scheduler jobs -> delete after local schedule proof.
- Secret Manager -> delete after local secure custody/auth proof.
- Firestore/Storage/Artifact Registry/PubSub -> delete after verified export/reproducibility proof.
- Retire GCP IAM/WIF identities and billing link last.

### B-Z3 — Final zero-GCP proof
- no serving Cloud Run service/job;
- no scheduler/probe/push invoker;
- no required Secret Manager/Firestore/Storage/GCP API call from normal laptop runtime;
- no billable retained resource intentionally used;
- billing/project closure or exact OWNER_ONLY one-time action.

## LOADED WORK — LANE C / CLAUDE
Claude independently verified supervisor cannot reach a real broker order. Continue non-idle:
- C-Z0.1 independently verify Google/AGI B-Z0 states with fresh commands/evidence where capability allows;
- C-Z0.2 specifically test the Logging exclusion scope and reject broad `status=200` evidence loss;
- C-Z1.1 verify Codex local-secret path has zero GCP dependency and no plaintext secret leakage;
- C-Z1.2 verify state-root consolidation/restart consistency and stale-forecast fix;
- C-Z0G verify Codex workflow kill-switch PR covers direct triggers, workflow_call, workflow_run and manual dispatch paths without breaking unrelated CI;
- publish contradictions immediately; do not wait for all tasks to finish.

## LOADED WORK — LANE C / PERPLEXITY
Distinct verification target:
- P-Z0.1 independent repo-wide hidden-GCP-dependency audit: WIF/IAM, service-account references, Cloud Run/Jobs/Scheduler, Monitoring, Pub/Sub push, Firestore/Storage/Artifact Registry, Cloud Build, Firebase/BigQuery and deploy/proof scripts;
- P-Z0.2 classify each as runtime dependency, evidence-only, dead/stale, recreation risk or safe-to-remove;
- P-Z0.3 cross-check Google/AGI after-state claims and identify any resource/path omitted from `GCP_ZERO_DEPENDENCY_MATRIX`;
- P-Z0.4 review Codex kill-switch PR independently rather than duplicating Claude's local filesystem checks.

## LANE D / CHATGPT CONTROLLER
- reject self-declared PASS until independently corroborated;
- keep queue/#188 reconciled;
- verify repo-side recreation risks directly;
- route contradictions to the agent able to implement the correction;
- GCP EXIT COMPLETE only after Z3 evidence, not from minScale=0.

## Current acceptance state
- `A3 preservation/clean clone`: independently corroborated earlier.
- `A4`: still PARTIAL due stale forecast + state-root issues.
- `C3.2 real-order reachability`: independently reported PASS by Claude; point-in-time static proof only.
- `B-Z0 schedulers/minScale/logging`: AGENT-REPORTED, controller status PARTIAL pending correction + independent verification.
- `GCP EXIT COMPLETE`: NO.

## Safety locks
PAPER/ANALYZER only. LIVE OFF. `REAL_BROKER_ORDER_COUNT=0`.
Never expose secret/token/PIN/TOTP values.
Do not delete irreplaceable state before verified local export.
Full GCP exit is the goal, but evidence integrity and local preservation remain mandatory.

## Non-idle rule
After every material result, publish evidence, re-read this file + Issue #188, claim the next highest-priority safe non-conflicting task and continue. `IDLE`, `NO TASK`, `STANDING BY`, `WAITING FOR CHATGPT`, `WAIT FOR USER` are invalid while safe work remains.
