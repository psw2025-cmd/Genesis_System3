# Genesis System3 — Local Migration Checklist (2026-09-01)

Companion to the master plan, CSV inventory, and architecture doc in this same folder. Check items off only with live evidence, not from a report alone.

## Phase A — Transparency audit
- [x] Full read-only inventory of every local Genesis_System3-related root (code checkouts, runtime root, state DBs, secret vault) — see CSV
- [x] Identified the existing-but-unactivated local scheduler daemon and its 25-job config
- [x] Identified the one real scheduling gap (Dhan token rotation, GCP-only persistence)
- [x] Master plan, CSV, architecture doc written and committed to GitHub

## Phase B — State root reconciliation (A-LOCAL-1)
- [ ] Re-verify `C:\Genesis_System3_Archive_20260901.zip` is still current (re-hash, compare manifest) before relying on it
- [ ] Confirm/add `SYSTEM3_RUNTIME_ROOT` support in `dashboard/backend/app.py` (or wherever state/log/db paths are constructed) so it can be pointed at `C:\Genesis_System3_Runtime` via env var
- [ ] Move `state/historical_market_data.db`, `src/storage/live/option_chain.db`, `outputs/db/system3_metrics.sqlite` under `C:\Genesis_System3_Runtime\db\` (copy first, verify, then remove the old copy — never delete-then-verify)
- [ ] Point `logs/` output at `C:\Genesis_System3_Runtime\logs\`
- [ ] Restart the local dashboard; confirm it reads the same state (no fresh/duplicate ledger created)
- [ ] `E:\Genesis_System3` and `C:\openalgo-main` explicitly left as `READ_ONLY_ARCHIVE` — no action taken, confirmed not silently used as authority anywhere

## Phase C — Local scheduler activation (A-LOCAL-3)
- [x] Create `config/local_scheduler_registry.yaml` reconciling all 9 retired GCP schedules against the existing local jobs: KEEP_LOCAL / MERGE / REMOVE / NOT_YET_MAPPED for each (see file — 2 open gaps remain, documented not hidden)
- [ ] Decide and record: does `scripts/system3_laptop_supervisor.py`'s recurring loop get merged into the phase82 daemon, or does one explicitly own the paper-pipeline tick while the other stays disabled? (Do not run both against the same state.) — **still open, flagged in the registry's `open_gaps`**
- [x] Adapt `scripts/gcp_dhan_token_rotation_job.py` into a local-only twin (`scripts/local_dhan_token_rotate.py`) persisting via `core.security.windows_secret_vault` instead of Secret Manager
- [x] Added the token-rotation job to `config/system3_job_scheduler.json` as `local_dhan_token_rotate` at `*/5 * * * *` Asia/Kolkata
- [x] Added a duplicate-worker guard to `run_daemon()` in `core/engine/system3_phase82_job_scheduler.py` (PID-file + `psutil.pid_exists` check — verified `os.kill(pid, 0)` is unreliable on Windows and does not detect this correctly, used psutil instead) — verified live: a second daemon instance correctly refuses to start while the first is running
- [ ] **Register the Windows Scheduled Task that runs the daemon continuously (at-logon/at-startup, auto-restart) — built and dry-run tested manually, but NOT yet registered as a persistent auto-start task. This is a standing background-process change and needs explicit owner approval before being made permanent.**
- [x] Ran the new token-rotation job once via the daemon's own `--job-id local_dhan_token_rotate` path (not just standalone): exit 0, correctly detected an existing token with 16.81h remaining and skipped unnecessary rotation, zero secret values printed, `REAL_BROKER_ORDER_COUNT=0`
- [ ] Let the daemon run unattended through one full local day; confirm the expected jobs fired at their scheduled times — blocked on the Windows Scheduled Task registration above

## Phase D — Live verification + defect closure
- [ ] Re-run the 22-tab dashboard check with `SYSTEM3_RUNTIME_ROOT` active — confirm no regression from the earlier verified state
- [ ] Confirm dashboard truth contract fields (`RUNTIME_STATE`, `GIT_SHA`, `HEARTBEAT_AGE`, `BROKER_STATE`, `DATA_AS_OF`) all read from the new runtime root correctly
- [ ] For any defect found in this phase: reproduce → root cause → regression test → implement → focused test → full smoke → independent verify → clean temp side effects → update this checklist → continue
- [ ] Repeat Phase C step 5 (real weekday, ideally live market hours) once one is available — explicitly deferred, not skipped

## Phase E — Documentation closure
- [ ] Update this checklist, the CSV, and the master plan after each phase
- [ ] Post each material transition to Issue #188 in the standard evidence-protocol format
- [ ] Keep `reports/runtime/latest/*` current so agents without laptop access can see status without needing raw logs

## Explicit non-goals (do not silently expand scope)
- [ ] Do NOT migrate or clean up `E:\Genesis_System3` or `C:\openalgo-main` content this pass
- [ ] Do NOT delete any GCP resource — gated separately on the do-not-delete-yet checklist in the extraction record
- [ ] Do NOT flip any LIVE/order-placement flag at any point in this checklist
