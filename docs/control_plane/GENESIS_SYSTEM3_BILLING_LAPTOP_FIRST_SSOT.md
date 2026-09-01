# Genesis System3 — Billing + Laptop-First Controller SSOT

**Authority marker:** `SYSTEM3_BILLING_LAPTOP_FIRST_SSOT_V4`
**Status:** LIVING CONTROLLER DOCUMENT
**Repository:** `psw2025-cmd/Genesis_System3`
**Coordination bus:** Issue #188
**Controller document PR:** #436 until merged

## 0. Permanent bootstrap — every agent gets the SAME prompt
Every Codex / Google-AGI / Claude / Perplexity / future agent must start by reading this document from GitHub, then latest Issue #188, current remote `main`, relevant open PR ownership, and its own platform/repo instructions. Never trust a stale local copy.

While PR #436 is unmerged, fetch this document from branch `docs/billing-laptop-first-ssot`. After merge, fetch it from current `main`.

The agent MUST identify its strongest available lane from current context and already-claimed work. It must not wait for the user or ChatGPT merely because one named checkpoint finished.

### PERMANENT NON-IDLE LOOP
Repeat until a genuine external blocker exists:

`READ CURRENT TRUTH -> CLAIM HIGHEST-PRIORITY NON-CONFLICTING WORK -> INVESTIGATE -> TEST/PROVE -> PUBLISH INTERMEDIATE EVIDENCE -> RE-READ #188 + THIS SSOT -> REPRIORITIZE -> CONTINUE`

Do **not** stop just because a task/checkpoint/subtask completed. Do **not** end with `WAIT FOR CHATGPT` unless the next action genuinely requires an owner/account approval, irreversible/destructive authorization, unavailable credential/capability, or conflicting write ownership that cannot be safely resolved. If no such blocker exists, immediately take the next eligible work item.

If intermediate evidence exposes a base/root problem, STOP downstream dependent work, record the contradiction, fix/verify the root cause first if within the lane, then resume. Never blindly execute a prewritten 1-to-50 sequence after step 20 proves the foundation wrong.

Before substantive work publish/record: `AGENT`, `LANE`, `START_TIME_UTC`, `CURRENT_REMOTE_MAIN_SHA`, `LOCAL_SHA` if applicable, `CLAIMED_SCOPE`, `CONFLICT_CHECK`.

After each material milestone publish evidence to Issue #188 and/or owning PR so other agents and ChatGPT can consume it without the user carrying reports manually.

## 0A. Mandatory agent identity on every write
Every agent-generated GitHub issue comment, PR comment/review, commit/PR body, controller status update, handoff, report, artifact manifest, or other shared coordination write MUST visibly identify the generating agent at the top.

Required header:
- `AGENT_NAME=` exact human-readable agent identity, e.g. `Codex CLI`, `Google/AGI`, `Claude`, `Perplexity`, `ChatGPT Controller`.
- `AGENT_LANE=` current lane, e.g. `A`, `B`, `C`, `D`, or explicitly claimed verification sublane.
- `AGENT_ROLE=` short role, e.g. `Laptop/PAPER`, `GCP Billing`, `Independent Verifier`, `Controller`.

Never post a shared coordination update anonymously or only under the GitHub account name `psw2025-cmd`; all agents share that account surface, so explicit identity is mandatory for humans and other agents to know who produced the evidence. If an old comment lacks identity, do not rewrite history unless necessary; reference it with its comment ID and state which agent is now validating it.

## 1. Non-negotiable authority and safety
- GitHub remote `main` is code authority. Re-read it at each material checkpoint; do not hard-code an old SHA as permanent truth.
- Issue #188 is the live coordination/status bus.
- Existing dirty laptop checkouts are evidence/salvage sources, not code authority.
- Until a deliberate authority cutover is merged/recorded, GCP remains authoritative production; laptop is migration/PAPER-shadow candidate.
- LIVE stays locked: `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0` unless a future explicit human break-glass changes policy.
- Never place/modify/cancel/square-off real broker orders in this program.
- Never expose secret/token/password/PIN/TOTP values in GitHub, issues, PRs, reports, screenshots, logs or prompts.
- No destructive cleanup, secret deletion, GCP shutdown, state deletion, cadence change, logging exclusion, authority cutover or unsafe merge without its prerequisite proof.
- Read-only forensics are always preferred over waiting when they can reduce uncertainty.

## 2. Goal and priority order
Primary goal: stop unnecessary GCP spend without losing state/recovery capability, establish a clean laptop-first development/PAPER runtime, prove genuine PAPER lifecycle, preserve external observability, and later deploy an exact proven SHA to GCP only when justified.

Priority order unless current evidence forces reprioritization:
1. prevent avoidable billing growth safely;
2. preserve irreplaceable state/credentials/history/rollback evidence;
3. establish clean exact-main laptop runtime;
4. prove real-market genuine PAPER lifecycle with zero broker orders;
5. prove restart/gap/recovery/observability;
6. cut expensive GCP runtime only after replacements are proven;
7. verify post-cutover billing and request billing review/possible goodwill credit;
8. final cloud redeployment/proof later.

PAPER acceptance: current/real market input where available -> strategy/prediction -> candidate -> PAPER-relevant gates -> simulated fill only -> authoritative durable PAPER persistence -> API -> dashboard -> exit -> costed P&L/reconciliation, with real broker order count zero.

## 3. Billing truth — current controller position
Observed August 2026 Cloud Assist baseline:
- Total: INR 21,086.72
- Cloud Run: INR 10,115.50
- Cloud Logging: INR 8,002.64
- Other services/GST remainder: INR 2,968.58

Google/AGI B2 has reported:
- BigQuery Billing Export not configured;
- Cloud Billing API disabled;
- therefore programmatic actual line-item stream is `BILLING_ACTUAL_UNAVAILABLE`;
- live inventory found Cloud Run service/jobs, nine schedulers, eleven secrets metadata, storage, Artifact Registry, Pub/Sub and Firestore dependencies.

Controller caveat: B2 reverse-calculated Logging GiB/SKU/pricing and Cloud Run component splits from the observed rupee totals. Treat those derived numbers as forensic estimates until direct billing SKU/usage evidence exists. Do NOT state that excluding routine HTTP 200 logs will automatically save the entire INR 8,002.64 or that post-cutover cost will definitely be <INR 500/month.

Do not switch `genesis-system3-web` to request-based CPU merely for savings while persistent queues/event listeners/socket/background dependencies remain. Do not scale it to zero before local replacements, token/state/recovery and observability are proven.

Cost-control sequence: inventory actual resources -> preserve current+rollback state/artifacts/secrets -> prove replacements -> stop/scale unnecessary Cloud Run/jobs/schedulers -> reduce only proven redundant logging while retaining ERROR/WARNING/CRITICAL, broker/token failures, PAPER evidence, prediction/evaluation, deploy/revision, security/audit and production-proof failures -> archive/delete stale resources later -> verify new daily burn -> billing support review/goodwill-credit request without promising credit.

## 4. Verified migration findings carried forward
Laptop forensics found the active historical checkout dirty and behind remote main, with multiple Genesis repositories/worktrees. Never bulk clean/reset/delete before salvage reconciliation. Preserve potentially irreplaceable DB/state, PAPER ledgers, historical market/option data, models, evidence and unique patches. Rebuildable venv/node_modules/cache/build artifacts do not automatically migrate.

The historical seven technical gates differ from broader LIVE-readiness gates. Stored evidence showed 2/7 technical gates, not a trustworthy current 5/7; re-derive current gates from current code/runtime.

Current deployment architecture has used `CLOUD_PAPER_ENGINE=0`. That is a P0 ownership question, not permission to flip it. Determine the intended single producer/owner of candidate -> real Dhan quote -> simulated fill -> close -> P&L -> durable persistence -> API/UI. Do not weaken genuine data/risk gates to fabricate PAPER trades.

## 5. Dynamic multi-agent lanes
### LANE A — CODEX / LAPTOP + PAPER EXECUTION FORENSIC
Primary scope: laptop filesystem/runtime evidence, salvage reconciliation, clean-main preparation, secure local runtime, Windows tasks/processes/recovery, and current-main PAPER E2E trace. No GCP mutation unless explicitly reassigned later.

### LANE B — GOOGLE/AGI / GCP BILLING + CLOUD DEPENDENCY
Primary scope: billing/cloud inventory, Cloud Run/services/jobs/Scheduler/Logging/Artifact Registry/Secret Manager metadata/PubSub/Firestore/Storage/BigQuery/Firebase/IAM-WIF/Monitoring/network dependency evidence and cost-reduction design. Secret payload access prohibited.

### LANE C — CLAUDE + PERPLEXITY / INDEPENDENT VERIFICATION + GAP FINDER
Primary scope: independently cross-check Lane A/B claims against current GitHub/main/Issue #188/repo architecture; identify contradictions, missed downstream impacts, unsafe assumptions, stale evidence, PR/workflow conflicts, and the smallest verification/fix. Claude and Perplexity MUST not duplicate each other blindly: each claims a distinct verification target or clearly labels independent second-source verification. Do not overwrite active A/B write surfaces. If a separate safe implementation lane is clearly unowned, claim it in #188 first.

### LANE D — CHATGPT CONTROLLER
ChatGPT owns connected-GitHub reconciliation, Issue #188 dispatch, PR/workflow evidence, conflict resolution, SSOT maintenance, gate decisions and next-priority design. ChatGPT is not a continuously running daemon and cannot see unpublished laptop/CLI screens. Therefore agent continuity MUST NOT depend on a fresh ChatGPT message; the non-idle loop above is mandatory.

Cross-lane discoveries use `HANDOFF_TO=` with evidence. Agents may independently verify another lane but must label it verification, not ownership takeover.

## 6. Dynamic ready queue — Lane A
### A2 — salvage/reconciliation
If not already fully proven, continue until all meaningful tracked/untracked/ignored differences, all Genesis repos/worktrees/unique commits, high-value DB/state/models/evidence, secret locations (names only), Windows tasks/processes/ports, and current PAPER owner are reconciled. Network read/fetch allowed. No blind cleanup/reset/pull/merge/install.

### A3 — immutable preservation + clean clone
Reported PASS in Issue #188 by the agent identifying itself there as `Codex / Laptop Agent`: immutable archive + manifest created, clean exact-main worktree created, legacy evidence preserved. Controller must still independently inspect proof quality and downstream A4 assumptions; PASS does not authorize cloud cutover or deletion.

### A4 — secure local bootstrap — NEXT FOR LANE A
Establish separate code/state/evidence roots; secure secret mechanism using Windows secure storage/DPAPI/Credential Manager or temporary Secret Manager via ADC; no plaintext secret normalization and no new long-lived service-account JSON keys. Recreate required local workers/schedules/supervisor/restart semantics and explicit runtime authority metadata. Verify that restored model/DB files do not make the canonical clean code tree misleadingly dirty without an explicit runtime-data separation plan.

### A5 — genuine PAPER proof
Trace and prove market data -> features/model/strategy -> candidate -> every PAPER-relevant gate -> real quote/contract eligibility -> simulated entry -> durable ledger/state -> API/UI -> exit -> costed P&L/reconciliation. `REAL_BROKER_ORDER_COUNT=0` mandatory.

### A6 — resilience + observability
Prove `RUNNING/OFFLINE/RECOVERING/INCOMPLETE_GAP`, restart after process/power/internet interruption, broker token expiry handling, missed schedule/data-gap behavior, disk/clock/backup failure controls, backup/restore, heartbeat freshness, and controlled external visibility.

When any A-step completes, immediately re-read current truth and take the next safe A-step or an unowned verification task. Do not wait merely for a new prompt.

## 7. Dynamic ready queue — Lane B
### B2 — billing truth + dependency MRI
Reported complete in Issue #188. Re-open only if fresh evidence contradicts it.

### B3 — reversible cost-reduction design
Reported PASS in Issue #188. Controller acceptance is conditional: the design is useful, but any exact savings/SKU/volume assertions remain estimates unless backed by direct metered billing/logging evidence. No logging exclusion execution is authorized by B3 PASS alone.

### B4 — cutover shutdown plan
Reported PASS in Issue #188 as a plan. Treat it as planning evidence only. Execution remains blocked until Lane A A4/A5/A6 replacement proof and controller reconciliation are complete. No GCP shutdown/scale action is authorized by B4 PASS.

### B5 — post-cutover billing verification / pre-cutover measurement — NEXT FOR LANE B
Until actual cutover is authorized, Lane B should NOT idle. It should perform pre-cutover measurement that reduces uncertainty: quantify current log ingestion by resource/log class/path using read-only metrics/queries; validate which candidate exclusions would remove only low-value routine success logs; measure current Cloud Run/job/scheduler invocation patterns; produce a residual-cost floor/range with explicit uncertainty; and prepare post-cutover verification queries. If direct billing export remains unavailable, keep `BILLING_ACTUAL_UNAVAILABLE` and do not fabricate exact future savings.

## 8. Dynamic ready queue — Lane C (Claude / Perplexity)
### C1 — cross-verify latest controller truth — READY
Independently verify latest Issue #188 claims, current main, PR #436 state, A3 archive/clean-clone claims where remotely verifiable, `CLOUD_PAPER_ENGINE=0` ownership, GCP-vs-local state assumptions, B2/B3/B4 cost derivations, proposed Logging exclusions, Secret Manager/ADC strategy, and whether any proposed change conflicts with `.github/CLAUDE_INSTRUCTIONS.md`, authority docs, workflows or current runtime architecture.

### C2 — downstream-impact matrix
Map missed dependencies across broker/token lifecycle, Firestore/storage/state, jobs/schedulers, queues/WebSockets, logs/alerts, GitHub Actions/WIF, local startup/recovery, UI/API parity, PAPER persistence and billing. Publish concrete corrections/handoffs.

### C3 — independent acceptance verifier
As A4/A5/A6/B5 evidence appears, independently test/review it. If a root contradiction appears, publish it immediately and tell affected lane to stop downstream dependent work. Do not wait for all tasks to finish.

Claude and Perplexity must continue C1 -> C2 -> C3 style verification as new evidence appears; if no new evidence exists, inspect unresolved open contradictions/PRs/workflows relevant to this program rather than declaring `NO TASK`.

## 9. State/secret/cloud migration checklist
Every material review must reconcile: Secret Manager/broker credentials/token rotation; local secure secret storage/environment mapping; broker auth/session/TOTP/token lifecycle; Firestore; Cloud Storage; BigQuery/Firebase if present; local DB/state/backups; Cloud Run services/jobs; Scheduler/background workers; Pub/Sub/queues/events/WebSockets; Logging/Monitoring/alerts; GitHub Actions/WIF/deploy assumptions; Artifact Registry; market/instrument history; models/features/evaluation history; APIs/frontend; controlled external URL; startup/shutdown/recovery/backfill; data gaps; disk/clock/backup failure.

No cloud state is safely removable until its replacement and rollback are proven.

## 10. Evidence protocol
Each material update must begin with:
- `AGENT_NAME=`
- `AGENT_LANE=`
- `AGENT_ROLE=`

Then include:
- `CHECKPOINT_OR_TASK=`
- `STATUS=PASS|FAIL|BLOCKED|PARTIAL|IN_PROGRESS`
- `START_SHA=` / `END_SHA=` where applicable
- `EVIDENCE=` exact commands/tests/URLs/artifacts/timestamps, with no secret values
- `CHANGES=` none or exact paths/resources
- `ROOT_CONTRADICTIONS=`
- `BLOCKERS=`
- `HANDOFF_TO=`
- `NEXT_ACTION_TAKEN=` not merely recommended, when safe work remains
- `REAL_BROKER_ORDER_COUNT=` for PAPER/runtime work

Do not claim PASS from code/CI alone where runtime/UI/billing proof is required. Stale heartbeat means runtime OFFLINE/UNKNOWN. Laptop PASS is not final GCP production PASS.

### Definition of genuine blocker
`BLOCKED` is allowed only when progress requires one of: owner/account setting, unavailable credential/capability, destructive/irreversible authorization, market-time-dependent observation that cannot be simulated/replayed, or conflicting owned write surface. Before blocking, exhaust safe read-only/alternative work and state the exact smallest unblock action.

`IDLE`, `NO TASK`, `WAITING FOR CHATGPT`, or `WAIT FOR USER` are NOT valid states when any safe unresolved work, verification, documentation reconciliation, test, forensic, or next queued task exists.

## 11. Controller reprioritization rule
The queues are guides, not a blind script. Every intermediate proof can change priority. If root cause appears at step 20, dependent 21-50 pause; resolve/verify root cause first. If another agent already fixed it, verify current evidence and avoid duplicate writes. If main changes, rebase reasoning onto current main before continuing.

Agents should publish intermediate evidence frequently enough that other agents can consume it. They cannot assume ChatGPT is watching unpublished live output.

## 12. Current immediate state
- A3: reported PASS by Codex/Laptop Agent; controller records this as agent evidence, not final acceptance of A4+ cutover readiness.
- Lane A next: A4 secure local bootstrap/runtime ownership proof; continue non-idle.
- B2/B3/B4: reported PASS by Google/AGI; controller preserves uncertainty around derived cost/savings claims and keeps cloud execution blocked.
- Lane B next: B5-style pre-cutover measurement/read-only residual-cost verification; continue non-idle.
- Claude: C1/C2/C3 verification loop.
- Perplexity: same C lane, but claim a distinct verification target or explicitly second-source verify Claude/other-agent claims.
- ChatGPT: reconcile GitHub evidence, keep this SSOT and Issue #188 aligned, review contradictions and take all connected-tool actions available.
- PR #436 remains controller branch until merged through normal protected workflow.
- No real broker order actions or LIVE enablement.
- No blind GCP shutdown, secret deletion, logging exclusion, local cleanup or state deletion.

## 13. One-default-prompt rule for the user
The user may send the exact same bootstrap prompt to every agent. Each agent must infer its lane from identity/capability/current claims and this SSOT, visibly identify itself on every shared write, then enter the permanent non-idle loop. The user must not be required to formulate fresh technical prompts after every task.
