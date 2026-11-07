# Genesis System3 — GCP-to-Laptop Extraction Record (2026-09-01)

**Purpose:** a single, complete reference of everything that exists on Google Cloud project `system3-openalgo-safe` right now, so that (a) every agent working on this repo can see exactly what must be replaced locally before any GCP resource is deleted, and (b) the human owner has one document, in GitHub + on the laptop + in their email, that nothing gets missed or forgotten.

**Author:** Claude (Claude Code, laptop-resident), Lane C independent verifier.
**Captured at:** 2026-09-01, local checkout HEAD `cbbcc2560...`, remote main `e411fb57d576f9e68ab4752e87209859b6f9e11e`.
**Method:** read-only `gcloud`/`gcloud storage`/`gcloud firestore` inspection under the project owner's own authenticated account (`warghade2012@gmail.com`), run directly on this laptop. No secret payloads were read or printed anywhere in this document. One command (`gcloud firestore export`) unintentionally executed a live (not dry-run) export instead of a describe; its outcome is documented in full below and the exported copy has already been pulled down to this laptop.

**Owner's stated goal driving this document:** stop 100% of Google Cloud billing — present and future — because the owner is currently unemployed and cannot sustain the ~₹21,000/month cost. Everything below exists to make that safe: extract/verify first, delete second.

---

## 1. Secret Manager — 11 secrets (names/metadata only; no values read)

| Secret name | Created | Used for (from code) |
|---|---|---|
| `dhan-access-token` | 2026-08-02 | Live Dhan broker session token, read dynamically by the web service (`DHAN_ACCESS_TOKEN_SECRET_ID`) |
| `dhan-access-token-candidate` | 2026-08-21 | Candidate/staging token written by the rotation job before promotion |
| `dhan-app-id` | 2026-08-02 | Dhan API application ID |
| `dhan-app-secret` | 2026-08-02 | Dhan API application secret |
| `dhan-pin` | 2026-08-03 | Dhan account PIN, used by the token-rotation job's login flow |
| `dhan-totp-secret` | 2026-08-04 | TOTP seed for Dhan 2FA during token rotation |
| `gemini_api_key` | 2026-08-16 | Gemini API key (used by some forecast/analysis code path) |
| `github-actions-deploy-sa-key` | 2026-08-04 | **A stored service-account JSON key for GitHub Actions deploy.** This directly conflicts with the repo's own stated policy ("normal cloud auth is keyless Workload Identity Federation; do not create/export long-lived service-account JSON keys" — `.github/CLAUDE_INSTRUCTIONS.md`). Flagged for the owner to review — it should be identified as either unused legacy (safe to delete) or an undocumented exception, before anyone deletes or migrates it. |
| `system3-dashboard-api-key` | 2026-08-02 | Dashboard API key gate |
| `system3-dashboard-worker-push-token` | 2026-08-10 | Worker-to-dashboard push auth token |
| `system3-dhan-client-id` | 2026-08-02 | Dhan client ID, injected into the web service as `DHAN_CLIENT_ID` |

**To fetch an actual value once you're ready to move it to local secure storage (never print it to a shared doc, chat, or GitHub):**
```
gcloud secrets versions access latest --secret=<name> --project=system3-openalgo-safe
```
Recommended local destination: Windows Credential Manager (`cmdkey` or the Python `keyring` package) or DPAPI-encrypted file — not a plaintext `.env`. This is Codex's A4.1/A-Z1.1 task; this document only inventories *which* secrets exist and *why*, not their values.

## 2. Firestore

- One database: `(default)`, native mode, region `asia-south1`.
- **A full export was taken today** (see note below) and downloaded to this laptop at:
  `C:\Genesis_System3_GCP_Extract\firestore_export\` (LevelDB export format, ~840 KB, 95 documents, export operation `SUCCESSFUL`, completed 2026-09-01T12:53Z).
- This export is a snapshot of whatever runtime/session state the web service had written to Firestore (per its `SYSTEM3_STATE_BACKEND=firestore` config) — it is evidence/backup, not yet reconciled into a single local-state SSOT. That reconciliation is Codex's A4.2/A-Z1.2 task.
- **Correction/disclosure:** this export was not originally intended as a mutation — a command meant to *describe* the database instead triggered a live `gcloud firestore export`. It succeeded, is low-cost (one-time, ~840 KB), and its output has already been pulled to the laptop above, so the net effect was actually useful for this extraction goal. No other unintended command was run.

## 3. Cloud Storage — 4 buckets, all currently empty of object content except folder placeholders

| Bucket | Region | Contents (top level) |
|---|---|---|
| `run-sources-system3-openalgo-safe-asia-south1` | asia-south1 | `services/` (Cloud Run source bundles — rebuildable from git, not required to preserve) |
| `system3-openalgo-safe-artifacts` | asia-south1 | `backtests/`, `reports/`, `state/` (plus the Firestore export folder added today) — check each for any content worth downloading before deletion |
| `system3-openalgo-safe_cloudbuild` | US | `source/` (Cloud Build cache — rebuildable, not required) |
| `adc-aab54293-...` | US-CENTRAL1 | Auto-created ADC bucket — not application data |

None of these buckets showed meaningful object counts in this pass (`TOTAL: 0 objects` at the folder-prefix level checked) — but only the top level was checked. Before deleting any bucket, do one more `gcloud storage ls -r gs://<bucket>/**` pass to confirm nothing meaningful is nested deeper (this was a quick pass, not an exhaustive recursive one).

## 4. Cloud Run Service — `genesis-system3-web`

Current live state: `minScale=0`, `maxScale=1`, CPU throttling **on** (no longer always-allocated) — already changed by another agent today as a cost-stop measure. Full environment-variable contract (safety locks, Dhan token config, Firestore state backend, etc.) matches `scripts/gcp_cloud_run_auto_deploy_impl.py`'s `SAFE_ENV` block in the repo exactly — confirmed live, not just from reading code. Container resources: 1 vCPU / 1 GiB, concurrency 50.

**Local replacement:** run the same FastAPI app (`dashboard/backend/app.py`) directly on the laptop with `SYSTEM3_STATE_BACKEND` pointed at a local store instead of Firestore (part of A4.2), and the same safety-lock env vars (`LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0`, `ANALYZE_MODE=1`) always set.

## 5. Cloud Run Jobs (9) and Cloud Scheduler triggers (9 active + 3 legacy duplicates, all currently PAUSED)

| Cloud Run Job | Scheduler trigger | Cron | Timezone | Local replacement status |
|---|---|---|---|---|
| `genesis-system3-dhan-token-rotate` | `genesis-system3-dhan-token-rotate-daily` | `*/5 * * * *` | Asia/Kolkata | **Not yet proven locally — highest priority.** This is the job that keeps the Dhan broker session alive. Pausing it in the cloud with no local replacement risks the broker session lapsing with no recovery. |
| `genesis-system3-scheduler-collector` | `genesis-system3-scheduler-collector-every-minute` | `* * * * *` | UTC | Partially replaced — the new `scripts/system3_laptop_supervisor.py` (Codex, in progress) covers a version of this loop, not yet durability-tested |
| `genesis-system3-forecast` | `genesis-system3-forecast-daily` | `0 4 * * MON-FRI` | UTC | Not yet proven locally; also blocked on the separate stale-forecast-source finding (`state/gain_rank_history.json` last updated 2026-06-14) |
| `genesis-system3-rank` | `genesis-system3-rank-daily` | `45 3 * * MON-FRI` | UTC | Not yet proven locally |
| `genesis-system3-validate` | `genesis-system3-validate-daily` | `5 10 * * MON-FRI` | UTC | Not yet proven locally |
| `genesis-system3-signals` | `genesis-system3-signals-daily` | `15 13 * * MON-FRI` | UTC | Not yet proven locally |
| `genesis-system3-control-plane-verify` | (no dedicated scheduler found in this pass) | — | — | Not yet proven locally |
| `genesis-system3-ml-history-bootstrap` | (one-off/manual job, no recurring scheduler) | — | — | One-off; can be rerun locally when needed |
| `genesis-system3-smoke` | (CI-triggered, not on a recurring scheduler) | — | — | Already runs in GitHub Actions CI, not a laptop concern |

Three additional scheduler entries (`genesis-system3-signals-schedule`, `genesis-system3-rank-schedule`, `genesis-system3-forecast-schedule`) exist as older v1-API duplicates of the `-daily` ones above, and were already `PAUSED` before anyone touched them today — they look like dead legacy duplicates, but confirm with Codex/repo history before deleting.

**Job-to-code mapping** (from `scripts/gcp_worker_job.py`): each job invokes `run_job(kind=...)` with `SYSTEM3_JOB_KIND` matching the table above (`scheduler-collector`, `rank`, `validate`, `forecast`, `signals`, `control-plane-verify`, `ml-history-bootstrap`, `smoke`). There is also a `paper-pipeline-v8` kind in the same file that is **not** wired to any scheduler above — see Issue #188 C1 finding for detail; this is the dormant genuine-PAPER worker path.

## 6. Artifact Registry — 2 Docker repos: `cloud-run-source-deploy`, `system3-containers`
Container images for Cloud Run deploys. Not required locally once Cloud Run is retired — the laptop runs Python directly, not containers. Safe to delete once Cloud Run is confirmed gone.

## 7. Pub/Sub — 3 topics: `genesis-system3-ops-events`, `genesis-system3-incidents`, `broker-token-rotate`
Used for inter-service signaling (token-rotation notifications, ops/incident events). No local subscriber currently proven; if the laptop supervisor doesn't need cross-process pub/sub, these can likely be deleted once confirmed unused locally (in-process function calls replace them).

## 8. Windows Scheduled Tasks — found pointing at the wrong, legacy repo, now disabled

Live `Get-ScheduledTask` inspection on this laptop found four tasks named `System3_*` that were all actually invoking `C:\openalgo-main`, which is **not** this repo — it's a separate, older codebase (`git remote` = `psw2025-cmd/System-3-Openalgo`, a top-level `app.py`, no `dashboard/` folder), matching what `.github/CLAUDE_INSTRUCTIONS.md` already calls "Angel-era... historical/non-authoritative":

| Task | Path | Target (before) |
|---|---|---|
| `System3_DailyFreshStart` | `\` | `C:\openalgo-main\daily_system3_fresh_start.bat` |
| `System3_WeeklyMaintenance` | `\` | `C:\openalgo-main\scripts\venv_scheduled.cmd scripts\repo_weekly_maintenance.py --apply` |
| `System3_MarketOpenAutoProof` | `\OpenAlgo\` | `C:\openalgo-main\scripts\venv_scheduled.cmd scripts\market_open_auto_proof.py --mode market-open` |
| `System3_WeeklyMaintenance` | `\OpenAlgo\` | `C:\openalgo-main\scripts\venv_scheduled.cmd scripts\repo_weekly_maintenance.py --apply` |

These were already failing (see Checkpoint-2/A2 last-run-result codes) and, even when they did run, were executing the wrong, non-authoritative codebase — not `Genesis_System3`. **All four have now been disabled** (`Disable-ScheduledTask`, reversible via `Enable-ScheduledTask` with the same name/path), at the owner's explicit direction, so there is no confusing parallel legacy activity while the real local supervisor/dashboard is being brought up. A separate, unrelated task (`Genesis_DiskRepair`, running `chkdsk C: /f /r`) was left untouched — it is not part of this system and its ownership/purpose has not been established.

Once the current `Genesis_System3` local supervisor + dashboard are proven working, a **new** scheduled task should be created pointing at the correct location (the clean checkout, not `C:\openalgo-main`) rather than re-enabling these.

## 9. What's already been changed today (by other agents, before this document existed)

- All 9 active Cloud Schedulers: `PAUSED` (confirmed live, this pass).
- `genesis-system3-web`: scaled to `minScale=0`/`maxScale=1`/CPU-throttled (confirmed live, this pass).
- A Cloud Logging exclusion filter `emergency-health-200` was added to the `_Default` sink — already flagged by the controller thread as too broad (may suppress non-health-check evidence) and not yet corrected as of this document.

## 10. Do-not-delete-yet checklist (blocks full shutdown until each is proven)

- [ ] Dhan broker token rotation proven working from the laptop, without GCP, before that scheduler/job is deleted (not just paused).
- [ ] Single local state SSOT chosen and Firestore reconciled/exported into it (the export above is a start, not the finish).
- [ ] Stale forecast-source (`state/gain_rank_history.json`) issue fixed, independent of the shutdown work.
- [ ] All 11 secrets either migrated to local secure storage or confirmed genuinely unneeded (e.g. `github-actions-deploy-sa-key` reviewed and classified).
- [ ] Storage buckets checked recursively (not just top level) for anything worth downloading.
- [ ] Logging exclusion filter narrowed per the controller's own correction before relying on it.
- [ ] GitHub Actions workflows capable of redeploying/reinvoking GCP (`cloud-run-auto-deploy.yml` and 6 others named in Issue #188) neutralized so a future `git push` cannot recreate billable resources.
- [ ] Only then: delete Cloud Run services/jobs, delete schedulers, delete secrets, delete Firestore, delete storage buckets/Artifact Registry/Pub/Sub, and finally unlink billing or shut down the project (owner-only action if the current account lacks that permission).

This document will be superseded by whatever the agents post next in Issue #188 as extraction/migration work continues — treat it as the 2026-09-01 baseline snapshot, not a living file to keep editing in place.
