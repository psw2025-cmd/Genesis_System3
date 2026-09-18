# Genesis System3 — Local Migration Master Plan (2026-09-01)

**Author:** Claude (Lane C, picking up Lane A's A-LOCAL-1/A-LOCAL-3 while Codex is unavailable)
**Trigger:** Owner directive — full plan + checklist + CSV inventory + architecture, audited to full transparency, before implementation; then implement, verify live, and keep resolving upstream/downstream until the whole lifecycle is documented and working.
**Scope:** the two remaining unowned Lane A items — (1) reconcile every scattered local state/code/evidence root into one canonical architecture, and (2) replace the 9 GCP Cloud Run Jobs/Schedulers with a working local equivalent — done in a way that survives Codex being unavailable.

---

## 0. What the audit actually found (the single most important discovery)

Before writing a build plan, I searched for whether any of this already existed locally, rather than assuming it needed to be built from zero. It mostly does:

- **`core/engine/system3_phase82_job_scheduler.py`** is a real, working local scheduler **daemon** — it reads `config/system3_job_scheduler.json` (25 jobs already defined: pre-market checks, `daily_gain_rank` at 09:15, `daily_gain_validate`/`daily_gain_trend`, `paper_lifecycle_proof` x3/day, `ui_market_cross_verify` x3/day, `signal_engine_bhavcopy`, `system3_post_market_pipeline`, `auto_retrain`, weekly audit, etc.), respects market holidays/weekday-only flags, has per-job timeouts, and persists its own run state. **It has never been registered as a Windows Scheduled Task or run continuously** — it exists in the repo, wired into `dashboard/backend/app.py` for status reporting, but nothing currently invokes `run_daemon()`.
- **The one genuine gap**: `scripts/gcp_dhan_token_rotation_job.py` (636 lines — real Dhan login/TOTP/token-generation logic already implemented) is **not** in the local job scheduler and its persistence layer (`_persist_authoritative_token`, `_persist_candidate_token`, `_latest_token_snapshot`) calls Google Secret Manager directly. This is the single highest-priority local-replacement gap — broker session continuity depends on it.
- **`scripts/system3_laptop_supervisor.py`** (built earlier today, in progress) covers a `scheduler-collector`-equivalent loop (paper pipeline tick every 5s/60s) but nothing else.
- **`C:\Genesis_System3_Runtime`** (the target single writable runtime root, per the operating standard) exists as empty folders only — nothing has actually been migrated into it yet. State/logs/DBs are still written under `C:\Genesis_System3_Clean\{state,logs,outputs}`.
- **Four separate Genesis_System3 code roots exist on this machine** (`C:\Users\ADMIN\Genesis_System3\Genesis_System3` dirty/behind, `C:\Genesis_System3_Clean` exact-main + in-progress local work, `E:\Genesis_System3` dirty legacy, plus `C:\openalgo-main` which is a *different* repo entirely) — full detail in the CSV.

This changes the plan from "build 6 local job replacements from scratch" to "activate one existing daemon, register one existing-but-cloud-only script locally, and reconcile state roots" — materially less new code than initially scoped.

## 1. Guiding constraints (unchanged from the SSOT/operating standard)

- PAPER/ANALYZER only. `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`. `REAL_BROKER_ORDER_COUNT` must stay 0 throughout.
- No secret values ever printed to GitHub/chat/logs.
- No destructive deletion of any state/DB/evidence before it is classified and, where irreplaceable, archived.
- Every material change goes through a normal PR — nothing important stays only in an untracked/scratch file.
- GitHub gets compact sanitized summaries (`reports/runtime/latest/*`) — never raw logs, DBs, or media.

## 2. Phases

### Phase A — Full transparency audit (this document + CSV + checklist + architecture doc)
Deliverables: this plan, `GENESIS_SYSTEM3_STATE_ROOT_INVENTORY.csv`, `GENESIS_SYSTEM3_LOCAL_MIGRATION_CHECKLIST.md`, `GENESIS_SYSTEM3_LOCAL_ARCHITECTURE.md`. No code changes in this phase beyond what's already merged (PR #445, #446).

### Phase B — State root reconciliation (A-LOCAL-1)
1. Classify every root in the CSV (already done this pass — see CSV).
2. Hash/archive anything irreplaceable that isn't already archived (Codex's `C:\Genesis_System3_Archive_20260901.zip` already covers models/DBs/reports as of 17:29 today — verify it's still current, re-archive only what's changed since).
3. Do **not** touch `E:\Genesis_System3` or `C:\openalgo-main` beyond what's already been decided (`openalgo-main`'s stray scheduled tasks already disabled) — both stay `READ_ONLY_ARCHIVE` until a human decides otherwise; they are out of scope for active reconciliation this pass.
4. Point the running local dashboard's state/log/db writes at `C:\Genesis_System3_Runtime\{state,logs,db}` instead of paths under the code checkout, via env vars already supported by the app (`SYSTEM3_RUNTIME_ROOT` — needs confirming/adding if not already read) — this is the actual "single writable runtime root" migration, currently only the empty folders exist.
5. Prove restart uses the same state root (stop/start the dashboard, confirm no new/duplicate ledger).

### Phase C — Local scheduler activation (A-LOCAL-3)
1. Populate `config/local_scheduler_registry.yaml` (the target canonical registry named in the operating standard) as a *reconciliation* of the existing `config/system3_job_scheduler.json` against the 9 retired GCP schedules — map GCP job -> local job id -> KEEP_LOCAL/MERGE/REMOVE.
2. Adapt `scripts/gcp_dhan_token_rotation_job.py`'s persistence layer to use `core.security.windows_secret_vault` instead of Secret Manager (behind a `TOKEN_ROTATION_LOCAL=1` style flag or a new local-only script, whichever is the smaller safe diff), and add it to the job scheduler at the GCP cron's cadence (`*/5 * * * *`, Asia/Kolkata).
3. Register **one** Windows Scheduled Task that runs `core/engine/system3_phase82_job_scheduler.py`'s `run_daemon()` continuously (or at logon + restart-on-failure), with a duplicate-worker lock so a second instance can't start.
4. Smoke-test: run each job once manually (`run_single_job(job_id)`), confirm no exceptions, confirm state file updates, confirm zero real broker orders.
5. Let it run through one real weekday (ideally live market hours) and verify the expected jobs actually fired at their scheduled times with correct pre/post-market gating.

### Phase D — Live verification + upstream/downstream defect closure
For every item above: reproduce -> root-cause -> regression test -> implement -> focused test -> full smoke -> independent verify -> clean temp side effects -> update this documentation -> continue. Repeat until the dashboard's own truth contract (`RUNNING/OFFLINE/RECOVERING/INCOMPLETE_GAP`, exact SHA, heartbeat age, broker state, PAPER state) is provably correct with the local scheduler as the sole automation, and GCP's corresponding scheduler/job can be safely deleted (not just paused) per the "do-not-delete-yet checklist" in the earlier extraction record.

### Phase E — Documentation closure
Update the checklist, CSV, and this plan after every phase; post material transitions to Issue #188; keep `reports/runtime/latest/*` current so any agent without laptop access can see status without raw logs.

## 3. Sequencing rationale (why this order)

Token rotation before scheduler registration before state-root migration would risk losing broker auth mid-migration; scheduler registration before state-root migration would let the daemon start writing to the *wrong* root. So: reconcile the root first (Phase B), then activate scheduling on top of the correct root (Phase C), so nothing is built twice.

## 4. Explicit non-goals for this pass

- Not migrating `E:\Genesis_System3` or `C:\openalgo-main` content — those stay archived/read-only.
- Not deleting any GCP resource — that remains gated on the do-not-delete-yet checklist from the earlier extraction record, independent of this plan.
- Not attempting a live-market-hours proof today (it's after-hours) — Phase C step 5 is explicitly deferred to the next real trading session.
