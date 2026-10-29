# Genesis System3 — Billing + Laptop-First Controller SSOT

**Authority marker:** `SYSTEM3_BILLING_LAPTOP_FIRST_SSOT_V5`
**Status:** LIVING CONTROLLER DOCUMENT
**Repository:** `psw2025-cmd/Genesis_System3`
**Coordination bus:** Issue #188
**Controller document PR:** #436 until merged

## 0. Permanent bootstrap
Every Codex / Google-AGI / Claude / Perplexity / future agent must read this document, then `GENESIS_SYSTEM3_AGENT_LIVE_QUEUE.md`, latest Issue #188, current remote `main`, relevant PR/workflow ownership, and its platform instructions. Never trust stale local instructions.

While PR #436 is unmerged, read both controller files from branch `docs/billing-laptop-first-ssot`. After merge, read them from current `main`.

Every shared write must begin with:
- `AGENT_NAME=`
- `AGENT_LANE=`
- `AGENT_ROLE=`

Permanent loop:
`READ CURRENT TRUTH -> CLAIM HIGHEST-PRIORITY NON-CONFLICTING WORK -> INVESTIGATE -> TEST/PROVE -> PUBLISH EVIDENCE -> RE-READ SSOT + LIVE QUEUE + #188 -> REPRIORITIZE -> CONTINUE`

`IDLE`, `NO TASK`, `WAITING FOR CHATGPT`, and `WAIT FOR USER` are invalid while safe unresolved work exists.

## 1. Superseding user goal — FULL GCP EXIT
The program goal is now explicit and permanent until the user changes it:

**Genesis System3 must stop using Google Cloud for runtime/development/PAPER operation and must move all required functionality to the local laptop. The target steady state is zero intentional GCP runtime/dependency and zero intentional recurring GCP spend. Do not plan a later GCP redeployment.**

GitHub remote `main` remains code authority and Issue #188 remains the coordination/evidence bus. Laptop becomes the intended runtime authority after local cutover. GCP is now a migration source to be drained and retired, not a future target.

LIVE trading remains locked OFF. Never place/modify/cancel/square-off real broker orders. `REAL_BROKER_ORDER_COUNT=0` for PAPER/runtime work.

## 2. Billing truth and urgency
Observed August 2026 Cloud Assist baseline:
- Total: INR 21,086.72
- Cloud Run: INR 10,115.50
- Cloud Logging: INR 8,002.64
- Other services/GST remainder: INR 2,968.58

Google/AGI previously reported that direct programmatic actual line-item billing is unavailable because BigQuery Billing Export is not configured and Cloud Billing API is disabled. Therefore derived SKU/GiB and future-cost claims remain estimates.

Previous residual-cost proposals such as keeping a small GCP footprint are superseded. The target is not `minScale=0` plus some retained services; the target is full GCP exit after required local export/migration.

Stopping future GCP use does not erase already-accrued historical charges.

## 3. Emergency priority order
1. Stop new recurring GCP execution/invocation/redeploy as quickly as safely possible.
2. Preserve/export irreplaceable cloud-only state, credentials, history, configuration and evidence needed locally.
3. Move required secrets/token lifecycle/state/workers/schedulers/monitoring/dashboard dependencies to laptop.
4. Remove GCP services/resources after their local replacement/export is verified.
5. Disable any GitHub/GCP automation capable of recreating cloud resources.
6. Verify no normal laptop runtime path depends on GCP APIs.
7. Unlink project billing or shut down the GCP project if permissions allow after required migration; otherwise surface the exact smallest owner action.
8. Verify billing trend and pursue billing support/goodwill review separately without promising credit.

A5/A6 PAPER perfection is **not** a prerequisite for stopping recurring GCP compute/logging spend. Preserve/migrate the specific dependency, then stop its cloud cost source and continue development locally.

## 4. Full GCP exit matrix
Every agent review must reconcile and eventually close all of these:
- Cloud Run service `genesis-system3-web` and every revision/traffic path;
- all Cloud Run jobs, including token rotation, collector, forecast, rank, signals, validation, smoke, bootstrap/control-plane jobs;
- all Cloud Scheduler jobs;
- Monitoring uptime checks/alerts/probes that can cause requests or cloud activity;
- Cloud Logging ingestion/sinks/buckets/retention relevant to project use;
- Secret Manager and broker credential/token lifecycle;
- Firestore and any cloud runtime state;
- Cloud Storage buckets/objects;
- Pub/Sub topics/subscriptions/push triggers/events;
- BigQuery/Firebase if used;
- Artifact Registry/container images;
- IAM/service accounts/WIF/deploy identities;
- GitHub Actions/workflows that deploy/invoke GCP;
- network/static-IP/NAT/load-balancer/other billable infra if present;
- budgets/billing link/project billing status;
- any hidden API dependency from local code.

For each item record: `CURRENT_GCP_STATE`, `LOCAL_REPLACEMENT_OR_EXPORT`, `STOPPED_OR_REMOVED`, `INDEPENDENT_PROOF`, `RESIDUAL_COST_RISK`, `OWNER_ACTION_IF_ANY`.

## 5. Local replacement contract
The laptop implementation must own required System3 behavior without GCP dependence:
- code from clean current GitHub main;
- one explicit local mutable runtime-state root separate from code/evidence;
- secure local secret storage using Windows Credential Manager/DPAPI or equivalent; no plaintext secret files;
- broker login/session/TOTP/token lifecycle independent of Secret Manager/Cloud Run;
- local DB/state/history/backups replacing Firestore/cloud state as needed;
- local workers/schedules/supervisor replacing Cloud Run jobs/Scheduler;
- local structured logs, heartbeat, alerts and evidence replacing cloud Logging/Monitoring;
- localhost dashboard/API and optional controlled laptop tunnel only if external viewing is required;
- explicit `RUNNING`, `OFFLINE`, `RECOVERING`, `INCOMPLETE_GAP` truth;
- restart/gap/backfill/recovery semantics;
- PAPER/ANALYZER only, LIVE off.

## 6. Current laptop/PAPER findings
A3 immutable preservation + clean clone has been independently corroborated.

Codex A4 reported a local supervisor and used ADC/Secret Manager temporarily. Claude then found:
1. stale `state/gain_rank_history.json` from 2026-06-14 was being used to produce 2026-09-01-dated forecasts without a freshness gate;
2. a third local state root appeared under the clean checkout, creating split-brain risk.

Therefore A4 remains PARTIAL until stale forecast provenance/freshness and single-state-root issues are corrected. These correctness issues matter for PAPER truth, but they no longer block emergency shutdown of unrelated GCP recurring cost sources after required data/secret export.

## 7. Multi-agent lanes
### Lane A — Codex / Laptop + migration
Own secure local independence, state export/import, local secret custody, token/session replacement, local supervisor/jobs/schedules, state-root authority, stale-forecast fix, PAPER E2E, recovery/observability.

Immediate migration priority:
- remove ADC/Secret Manager as a normal runtime requirement;
- migrate needed cloud state/data/config to laptop;
- prove local broker auth/session without GCP;
- recreate all required job/scheduler functions locally;
- identify each GCP dependency that Lane B may safely remove.

### Lane B — Google/AGI / GCP Exit Executor
Own exact GCP inventory, stop/disable/delete sequence, before/after evidence, residual resource scan, billing-zero closure.

Immediate priority:
- pause/disable all recurring Scheduler and uptime/automated invokers;
- stop recurring Cloud Run execution;
- identify cloud-only dependencies and hand them to Lane A;
- remove each GCP resource once its required local export/replacement is proven;
- produce `GCP_ZERO_DEPENDENCY_MATRIX`;
- unlink project billing / shut down project if credentials permit after migration, or publish one exact owner action.

### Lane C — Claude + Perplexity / independent verification
Claude independently verifies Lane A local migration correctness and hidden GCP dependencies.
Perplexity independently audits repo/GitHub for GCP deploy/recreation paths and cross-checks Lane B's removal matrix.
Neither should blindly duplicate the other.

### Lane D — ChatGPT Controller
Own connected-GitHub reconciliation, Issue #188 dispatch, SSOT/live-queue maintenance, repo-side GCP workflow forensic, conflict resolution and final acceptance status.

## 8. GitHub/GCP recreation prevention
Current main contains GCP deployment architecture, including `.github/workflows/cloud-run-auto-deploy.yml` references and scripts such as `scripts/gcp_cloud_run_auto_deploy.py` / implementation helpers. Full exit is incomplete if a future push can automatically recreate GCP spend.

Agents must identify every deploy/invoke workflow, manual dispatch, script, WIF/service-account path and documentation/runbook instruction that can recreate GCP resources. Through normal GitHub governance, neutralize automatic GCP deployment for the local-only phase and update authority/runbook text accordingly. Historical scripts may remain only when clearly disabled/archive-only and incapable of automatic execution.

## 9. Shutdown safety
Full GCP exit is explicitly authorized as the program goal. However:
- do not expose secrets;
- do not delete irreplaceable state before verified local export;
- prefer reversible pause/stop first when export status is uncertain;
- after verified local export/replacement, deletion/retirement of cloud resources is expected, not blocked merely because old guidance preferred GCP;
- real broker trading remains forbidden.

## 10. GCP-zero acceptance
Do not say `GCP STOPPED` or `ZERO BILLING RISK` until evidence proves:
- no Cloud Run service/job is serving or running intentionally;
- no Scheduler/uptime/trigger can invoke GCP runtime;
- no GitHub workflow can automatically redeploy GCP;
- required secrets/state/data are securely available locally;
- normal laptop operation makes no required GCP API calls;
- Artifact/Storage/Firestore/Secret/Logging/PubSub/other retained resources are removed or proven non-billable pending project shutdown;
- billing is unlinked/project shut down when feasible, or the exact remaining owner-only step is identified;
- a post-change billing/resource check shows no new intentional GCP activity.

## 11. Evidence protocol
Each material update must include:
- `AGENT_NAME`, `AGENT_LANE`, `AGENT_ROLE`
- `CHECKPOINT_OR_TASK`
- `STATUS=PASS|FAIL|BLOCKED|PARTIAL|IN_PROGRESS`
- `START_SHA` / `END_SHA` where applicable
- exact commands/tests/resource states/timestamps with no secret values
- `CHANGES`
- `ROOT_CONTRADICTIONS`
- `BLOCKERS`
- `HANDOFF_TO`
- `NEXT_ACTION_TAKEN`
- `REAL_BROKER_ORDER_COUNT` for runtime work

A genuine blocker is only owner/account access, unavailable credential/capability, destructive action whose required export is not yet proven, unavoidable market-time observation, or conflicting owned write surface. Agents must exhaust safe alternatives first.

## 12. Current controller position
- Current remote main at last controller check: `e411fb57d576f9e68ab4752e87209859b6f9e11e`; re-read before relying on it.
- A3: corroborated.
- A4: PARTIAL due stale forecast source + split state root.
- Previous B5 reduced-cost steady state: CANCELLED.
- Full GCP exit: ACTIVE TOP PRIORITY.
- No real broker orders. LIVE remains off.
- Issue #188 + this SSOT + `GENESIS_SYSTEM3_AGENT_LIVE_QUEUE.md` are the shared controller surfaces.
