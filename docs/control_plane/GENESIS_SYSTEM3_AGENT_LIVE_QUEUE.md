# Genesis System3 — Live Multi-Agent Controller Queue

AGENT_NAME=ChatGPT Controller
AGENT_LANE=D
AGENT_ROLE=Controller / Reconciliation / Next-Task Dispatch

**Status:** ACTIVE / LIVING
**Current program goal:** FULL GCP EXIT. Genesis System3 development, PAPER runtime, state, secrets, scheduling, observability and dashboard work must move to the laptop/local stack. GCP is no longer a target runtime and must be reduced to zero ongoing dependence and zero intentional recurring GCP spend.

## Mandatory read order
1. `docs/control_plane/GENESIS_SYSTEM3_BILLING_LAPTOP_FIRST_SSOT.md`
2. this file
3. latest Issue #188
4. current remote `main`
5. relevant PR/workflow ownership

Every shared write begins with `AGENT_NAME=`, `AGENT_LANE=`, `AGENT_ROLE=`.

## CONTROLLER PRIORITY OVERRIDE — 2026-09-01
The prior plan of keeping a reduced-cost GCP footprint is superseded. Do NOT optimize for INR 695–1,475/month. Target is **no intentional GCP runtime/services retained** after required state/secret/config export.

Do not wait for A5/A6 PAPER perfection before stopping recurring GCP cost. The migration can continue locally after cloud runtime is stopped. Preserve irreplaceable data/config/secrets first where required, then stop the cost source immediately.

### Emergency shutdown acceptance sequence
**Z0 — stop new recurring GCP execution / redeploy first**
- Inventory exact active Cloud Run services/jobs, Scheduler jobs, uptime checks/Monitoring probes, Pub/Sub push/trigger paths, and GitHub Actions/workflows capable of GCP deploy/invocation.
- Pause/disable all GCP schedulers and uptime checks that invoke paid runtime.
- Prevent GitHub/main from automatically recreating or redeploying GCP resources. Current main contains `.github/workflows/cloud-run-auto-deploy.yml` references and GCP deployment scripts; identify every automatic trigger and neutralize the automatic GCP deploy path through normal GitHub governance.
- Stop recurring Cloud Run execution and background invocation. No real broker orders.

**Z1 — migrate all cloud-only dependencies to laptop**
- Secrets: move required broker/app credentials from Secret Manager into Windows secure storage (Credential Manager/DPAPI or equivalent). Never put values in GitHub, logs, Markdown or plaintext `.env`.
- Broker token/session lifecycle: provide a local rotation/login/session mechanism that does not require GCP Secret Manager or Cloud Run jobs.
- State/data: export/reconcile Firestore, Cloud Storage, Pub/Sub state if any, BigQuery/Firebase if present, models/artifacts, PAPER ledgers/history, instrument/market databases, job/scheduler definitions, relevant logs/evidence and required runtime configuration to local durable storage/backups.
- Replace cloud Scheduler/jobs/workers with Windows/local supervisor scheduling.
- Replace cloud Logging/Monitoring/alerts with local files/SQLite/structured logs + heartbeat/status evidence.
- Replace cloud external dashboard dependence with localhost and optional controlled laptop tunnel only if needed.

**Z2 — remove remaining billable GCP resources**
After required local copies are verified:
- delete/disable Cloud Run service(s) and all Cloud Run jobs;
- pause/delete all Cloud Scheduler jobs;
- remove uptime checks/Monitoring triggers that cause requests;
- remove unused Pub/Sub topics/subscriptions/triggers;
- remove Artifact Registry images/repos after local/repo reproducibility proof;
- remove Cloud Storage objects/buckets after verified local backup if no longer needed;
- remove Firestore/BigQuery/Firebase resources only after verified local export where used;
- remove Secret Manager secrets only after secure local secret custody and broker auth proof;
- retire GCP IAM/WIF/service-account/deploy paths no longer needed;
- disable/retire GCP-specific GitHub workflows so a later push cannot recreate spend.

**Z3 — billing-zero closure**
- Prove no Cloud Run service/job is serving/running.
- Prove no Scheduler job or uptime check can invoke GCP runtime.
- Prove no auto-deploy workflow can recreate GCP resources.
- Prove local runtime no longer calls Secret Manager/Firestore/Storage/GCP APIs for normal operation.
- Inventory any residual project resources and classify `ZERO_COST`, `CANNOT_BILL_WITHOUT_BILLING`, or `REMOVE`.
- If permissions allow after migration, unlink/disable project billing or shut down the GCP project to prevent future accidental charges. If this exact owner-level action cannot be done by the agent, publish the smallest one-time owner action with exact UI/command path.
- Verify billing trend after changes; accrued August charges remain historical and are not erased by shutdown.

## Lane A — Codex / Laptop
### Highest priority now
A-Z1.1 Secure local secret independence: replace temporary ADC/Secret Manager dependency with local secure custody and prove broker auth/session works without GCP.
A-Z1.2 Local state authority: choose one laptop runtime-state root and import/reconcile cloud/local state needed for continued PAPER development.
A-Z1.3 Local scheduler/supervisor replacement: recreate every required Cloud Scheduler/Run job function locally and prove startup/restart semantics.
A-Z1.4 Preserve/export any irreplaceable Firestore/Storage/model/DB/history evidence needed before Lane B deletes or disables it.

Continue A4 stale forecast/state-root fixes in parallel, but these do **not** block emergency GCP cost-stop actions once their specific cloud dependency has been preserved.

## Lane B — Google/AGI / GCP Exit Executor
### Highest priority now
B-Z0.1 Publish exact current GCP inventory and current-state proof immediately before mutation.
B-Z0.2 Execute reversible recurring-cost stop now: pause/disable all Scheduler jobs and Monitoring uptime checks/other automated invokers; stop recurring Cloud Run service/job invocation. Record before/after evidence.
B-Z0.3 Identify all dependencies that still prevent deletion/unlink, hand each to Lane A with exact export requirement.
B-Z2.1 As Lane A confirms each dependency local, remove its GCP counterpart. Do not retain GCP merely for convenience.
B-Z3.1 Produce a final `GCP_ZERO_DEPENDENCY_MATRIX` covering Cloud Run, Jobs, Scheduler, Logging/Monitoring, Secret Manager, Firestore, Storage, Artifact Registry, Pub/Sub, BigQuery/Firebase, IAM/WIF, networking, budgets/billing and auto-deploy paths.
B-Z3.2 If authorized credentials permit, unlink project billing / shut down project after local migration proof. Otherwise surface the exact one-time owner action.

Previous B5 residual-cost target is CANCELLED; there is no accepted steady-state GCP monthly budget other than zero intentional use.

## Lane C — Claude + Perplexity independent verification
Claude:
- verify every Z0/Z1 claim independently, especially local secret independence, local state authority and whether any hidden GCP API dependency remains;
- verify GCP shutdown does not create real broker orders or corrupt PAPER history;
- verify Codex stale-forecast fix separately.

Perplexity:
- audit current main for every GCP auto-deploy/invocation/recreation path, including `.github/workflows/cloud-run-auto-deploy.yml`, deploy scripts, WIF/service-account assumptions, scheduled actions and production-proof workflows;
- build an independent cloud-dependency removal checklist and cross-check Google/AGI's GCP_ZERO_DEPENDENCY_MATRIX.

## Lane D — ChatGPT Controller
- keep this live queue and Issue #188 reconciled;
- verify published agent evidence before marking GCP component STOPPED/REMOVED;
- flag any hidden redeploy/recreation path;
- do not accept `minScale=0` as full GCP exit; service/job/scheduler/dependency removal or billing disablement is the target;
- continue GitHub-side GCP workflow forensic and controller updates.

## Current known contradictions
- Google/AGI B5 previously proposed a residual INR 695–1,475/month GCP footprint. That is now rejected because the goal is full GCP exit.
- Codex A4 used ADC/Secret Manager. That is only temporary migration evidence and is NOT acceptable final local independence.
- A5/A6 completion is no longer a prerequisite for stopping recurring GCP compute/logging costs. Only preserve/migrate the specific dependency before removing its cloud source.

## Safety locks
PAPER/ANALYZER only. LIVE OFF. `REAL_BROKER_ORDER_COUNT=0`.
Never expose secret/token/PIN/TOTP values.
Do not delete irreplaceable state before verified local export. Prefer reversible pause/stop first, then deletion after proof. Full GCP exit is explicitly authorized as the program goal.

## Evidence protocol
Each material update must include `CHECKPOINT_OR_TASK`, `STATUS`, exact before/after resource state, `EVIDENCE`, `CHANGES`, `ROOT_CONTRADICTIONS`, `BLOCKERS`, `HANDOFF_TO`, `NEXT_ACTION_TAKEN`, and `REAL_BROKER_ORDER_COUNT` for runtime work.

## Non-idle rule
After every step, re-read this file + Issue #188 and continue the next safe non-conflicting GCP-exit/local-replacement task. Do not wait for a fresh user/ChatGPT technical prompt while safe work remains.
