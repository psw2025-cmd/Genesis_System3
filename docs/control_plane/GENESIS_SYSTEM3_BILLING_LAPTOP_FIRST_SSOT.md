# Genesis System3 — Billing + Laptop-First Controller SSOT

**Authority marker:** `SYSTEM3_BILLING_LAPTOP_FIRST_SSOT_V2`
**Status:** LIVING CONTROLLER DOCUMENT
**Repository:** `psw2025-cmd/Genesis_System3`
**Coordination bus:** Issue #188
**Controller document PR:** #436 until merged

## 0. Agent bootstrap — READ THIS FIRST
Every Codex/Google/other execution agent must start here, then read latest Issue #188 and relevant owning PRs. Never trust a stale local copy of this document. Fetch it from GitHub branch `docs/billing-laptop-first-ssot` while PR #436 is unmerged; after #436 merges, fetch it from current `main`.

Before work, post/record: AGENT, LANE, START_TIME_UTC, CURRENT_REMOTE_MAIN_SHA, LOCAL_SHA if applicable, CLAIMED_SCOPE, and whether another agent already owns that scope. Never duplicate an active lane unless explicitly assigned independent verification.

At completion, post evidence to Issue #188 and/or owning PR, including exact SHA/timestamp, commands/tests/proof, files changed, unresolved blockers, next recommended action. End with `WAIT FOR CHATGPT`. ChatGPT/controller reviews proof and advances the READY queue. The user should not need to relay technical output between agents.

## 1. Non-negotiable authority/safety
- GitHub remote `main` is code authority. Current main must be re-read at every checkpoint; never hard-code an old SHA as permanent truth.
- Issue #188 is live coordination/status authority.
- Existing dirty laptop checkouts are evidence/salvage sources, not code authority.
- Until a deliberate authority cutover is merged/recorded, GCP remains authoritative production and laptop is migration/PAPER-shadow candidate.
- LIVE remains locked: `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0` unless a future explicit human break-glass changes policy.
- Never place/modify/cancel real broker orders during this program.
- Never print/store secret values in GitHub, issues, PRs, reports, screenshots or prompts.
- No destructive cleanup, secret deletion, GCP shutdown, state deletion, scheduler cadence change, logging exclusion, or authority cutover without prerequisite proof and controller approval.

## 2. Goal
Stop unnecessary GCP spend without losing state/recovery capability; establish a clean laptop-first development/PAPER runtime; prove genuine PAPER lifecycle; preserve external observability; later deploy the exact proven SHA to GCP only when justified.

PAPER acceptance means: real/current market input where available -> strategy/prediction -> candidate -> PAPER-relevant gates -> simulated fill only -> durable authoritative PAPER persistence -> API -> dashboard -> exit -> costed P&L/reconciliation, with broker real-order count zero.

## 3. Billing truth and rules
Observed August 2026 Cloud Assist baseline:
- Total INR 21,086.72
- Cloud Run INR 10,115.50
- Cloud Logging INR 8,002.64
- Cloud Run + Logging are the dominant cost drivers.

Do not substitute tariff-model estimates for actual billing truth. If Billing Export/API is unavailable, mark detailed line-item cost `BILLING_ACTUAL_UNAVAILABLE` and retain Cloud Assist observed figures as the best observed baseline.

Do not switch `genesis-system3-web` to request-based CPU merely for savings while persistent queues/event listeners/socket/background dependencies remain. Do not blindly scale to zero before laptop replacements, token/state/recovery and observability are proven.

Cost-control order: identify actual billable resources -> preserve state/current+rollback artifacts/secrets -> prove laptop replacements -> stop/scale unnecessary Cloud Run/jobs/schedulers -> reduce genuinely redundant logging without losing PAPER/broker/error/deploy/security/proof evidence -> archive/delete stale resources later -> verify new daily burn -> request Billing Support review/goodwill-credit consideration without promising credit.

## 4. Verified migration findings to carry forward
Checkpoint forensics found the active historical laptop checkout dirty/behind and multiple Genesis repos/worktrees. Therefore no bulk cleanup/reset/delete is allowed before salvage reconciliation. Preserve potentially irreplaceable DB/state, PAPER ledgers, market/option data, models, evidence and unique patches; rebuildable venv/node_modules/cache/build artifacts are not automatically migrated.

The historical technical seven-gate matrix is distinct from broader LIVE-readiness gates. Stored historical evidence showed 2/7 technical gates, not a reliable current 5/7. Re-derive current gate state from current code/runtime.

Current deployment architecture has used `CLOUD_PAPER_ENGINE=0`. This is a P0 architecture question, not permission to flip the flag. Determine the intended single PAPER producer/owner and prove whether another job/service owns execution. Do not manufacture PAPER trades by weakening genuine data/risk gates.

## 5. Parallel lane ownership
### LANE A — CODEX / LAPTOP MIGRATION + PAPER FORENSIC
Codex owns laptop filesystem/runtime evidence, salvage reconciliation, clean-main preparation, secure local runtime design, Windows tasks/processes/recovery, and current-main PAPER execution trace. It must not mutate GCP.

### LANE B — GOOGLE/AGI / GCP BILLING + CLOUD DEPENDENCY MRI
Google/AGI owns read-only GCP inventory and billing evidence: Cloud Run services/revisions/jobs, Scheduler, Logging buckets/sinks/exclusions/retention, Artifact Registry, Secret Manager metadata only, Pub/Sub, Firestore, Storage, BigQuery/Firebase status, IAM/WIF metadata, Monitoring/alerts, networking and other billable dependencies. It must not access secret payloads or mutate GCP.

### LANE C — CHATGPT CONTROLLER
ChatGPT owns GitHub remote reconciliation, Issue #188 coordination, PR/workflow evidence, conflict resolution between lanes, this living SSOT, readiness gates, and authorization of next checkpoints. ChatGPT should do all work available through connected tools before asking the user/laptop agents.

Agents must not overwrite another lane. Cross-lane discoveries are posted as `HANDOFF_TO=<lane>` with evidence.

## 6. READY QUEUE — Codex
### A2 — exhaustive salvage/reconciliation (READY)
Read-only/network-read allowed. Establish current remote main; inventory tracked/untracked changes; group ignored files; inventory all Genesis repos/worktrees and unique commits; inventory local DB/state/models/evidence; secret names+locations only; Windows tasks/processes/ports/resources; resolve intended PAPER owner including `CLOUD_PAPER_ENGINE=0`; produce exact salvage plan. No cleanup/reset/pull/merge/clone/install.

PASS requires: meaningful local differences classified; irreplaceable ignored state identified; unique commits reconciled; state stores and split-brain risk mapped; secret custody classified; Windows runtime mapped; current-main PAPER owner question answered; non-destructive salvage plan ready.

### A3 — preservation + clean-clone preparation (BLOCKED on A2 controller approval)
Hash/archive only approved irreplaceable material; preserve old checkouts read-only; create canonical clean clone from freshly verified main only after salvage proof. No arbitrary duplicate folders.

### A4 — local dependency/bootstrap (BLOCKED on A3)
Build secure local config/state/broker-token strategy. Prefer Windows secure storage/DPAPI/Credential Manager or temporary Secret Manager via ADC; do not normalize plaintext `.env` secrets and do not create service-account JSON keys. Recreate required schedulers/workers/supervisor/restart behavior.

### A5 — genuine PAPER E2E (BLOCKED on A4)
Prove market -> prediction/signal -> every PAPER gate -> simulated entry -> durable persistence -> API/UI -> exit -> costed P&L/reconciliation. Real broker order count must remain zero.

### A6 — resilience/observability (BLOCKED on A5)
Prove RUNNING/OFFLINE/RECOVERING/INCOMPLETE_GAP truth, power/process/internet restart, broker token expiry handling, missed schedule/data-gap behavior, backup/restore, heartbeat and controlled external visibility.

## 7. READY QUEUE — Google/AGI
### B2 — billing truth + dependency MRI (READY)
Strict read-only. First check whether actual Billing Export/API evidence exists. Never enable APIs or create exports. Reconcile observed August baseline with actual rows if accessible; otherwise state `BILLING_ACTUAL_UNAVAILABLE` and do not invent exact resource costs.

Inventory current resource configuration and dependency graph. For every resource classify provisional `KEEP_FOR_MIGRATION`, `STOP_AFTER_REPLACEMENT`, `SCALE_AFTER_PROOF`, `ARCHIVE`, `DELETE_LATER`, or `TO_VERIFY`; include dependency, risk, evidence, and prerequisite. Logging analysis must preserve ERROR/WARNING/CRITICAL, broker/token failures, PAPER trade evidence, prediction/evaluation evidence, deployment/revision evidence, security/audit and production-proof failures. Never access Secret Manager payloads.

### B3 — zero-impact cost candidate plan (BLOCKED on B2 controller review)
Prepare exact reversible commands/rollback for only evidence-proven zero-functional-impact savings. Do not execute.

### B4 — laptop-cutover cloud shutdown plan (BLOCKED on A4/A5 + B3)
Map exact Cloud Run/jobs/schedulers/logging sources that become unnecessary after laptop replacements. Calculate retained-cloud dependency/cost uncertainty and rollback. Do not execute until controller authorizes.

### B5 — post-cutover billing verification (BLOCKED on actual cutover)
Verify stopped/scaled resources, residual billable inventory, new accrued/daily trend if actual billing data is available, and unexpected cost drivers. Billing Support review/credit request is separate and must not be represented as guaranteed.

## 8. State, secret and cloud migration checklist
Must explicitly reconcile: Secret Manager/broker credentials/token rotation; local secure secret storage/env mapping; broker auth/session/TOTP/token lifecycle; Firestore; Cloud Storage; BigQuery/Firebase if present; local DB/state and backups; Cloud Run services/jobs; Scheduler/background workers; Pub/Sub/queues/events/WebSockets; Logging/Monitoring/alerts; GitHub Actions/WIF/deploy assumptions; Artifact Registry; market/instrument history; models/features/evaluation history; APIs/frontend; controlled external URL; startup/shutdown/recovery/backfill; data gaps; disk/clock/backup failure.

No cloud state is considered safely removable until its local replacement and rollback are proven.

## 9. Evidence protocol
Every agent update uses:
- `AGENT=`
- `LANE=`
- `CHECKPOINT=`
- `STATUS=PASS|FAIL|BLOCKED|PARTIAL`
- `START_SHA=` / `END_SHA=` where applicable
- `EVIDENCE=` exact commands/tests/URLs/artifacts/timestamps (no secrets)
- `CHANGES=` none or exact paths/resources
- `BLOCKERS=`
- `HANDOFF_TO=`
- `NEXT_RECOMMENDED_ACTION=`
- `REAL_BROKER_ORDER_COUNT=` when PAPER/runtime work is involved

End exactly: `WAIT FOR CHATGPT — <CHECKPOINT> COMPLETE`.

Do not claim PASS from code/CI alone when runtime/UI/billing proof is required. Stale heartbeat means runtime OFFLINE/UNKNOWN. Laptop PASS is not final GCP production PASS.

## 10. Controller advancement rules
The controller may give both lanes work in parallel. An agent may execute only checkpoints marked READY for its lane. BLOCKED checkpoints are pre-written so the next work is already visible, but the agent must not self-authorize them. When evidence lands in GitHub, controller reviews it, updates this SSOT/Issue #188, changes checkpoint state, and assigns the next lane work.

Material contradictions remain visible until reconciled. No agent may silently choose one conflicting truth.

## 11. Immediate state
- Codex: A2 READY.
- Google/AGI: B2 READY.
- ChatGPT: continuously reconcile GitHub/Issue/PR evidence and prepare A3/B3 decisions.
- PR #436 must be rebased/reconciled against current main before merge because its original base is stale. Do not force merge.
- No GCP shutdown, secret migration, laptop cleanup, fresh-clone cutover, logging exclusion, scheduler cadence change, or LIVE enablement is authorized by this document yet.

## 12. User instruction
The user should only need to point each agent to this GitHub controller document and tell it to execute its READY lane. Technical results must be posted back to GitHub, not manually relayed by the user.
