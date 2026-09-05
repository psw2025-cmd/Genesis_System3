# Genesis System3 Local Runtime Lifecycle & Operations Standard

AGENT_NAME=ChatGPT
AGENT_LANE=D
AGENT_ROLE=Controller / lifecycle architecture / evidence governance
CREATED_BY=ChatGPT
LAST_EDITED_BY=ChatGPT
CREATED_AT_UTC=2026-09-02T04:40:00Z
UPDATED_AT_UTC=2026-09-02T04:40:00Z
TASK_OR_ISSUE=#188/#442/#443
STATUS=ACTIVE_PROPOSAL_PENDING_INDEPENDENT_VERIFICATION_AND_MERGE

> This is the single operational lifecycle contract for the laptop-first Genesis System3 runtime. All implementation agents and verifiers must read this file before changing startup, shutdown, broker authentication, local scheduling, evidence, logging, cleanup, recovery, Drive sync, or runtime paths. It is intentionally strict and fail-closed. GitHub `main` remains code/control authority; the laptop is the runtime authority after local cutover; Google Drive is evidence/archive/visual review storage. No active GCP runtime dependency is permitted in the target state.

---

## 1. Owner goal

Genesis System3 must be understandable and recoverable by a non-coder. The system must run locally on the Windows laptop, remain PAPER/ANALYZER only, never place real broker orders, preserve truthful 24-hour operational evidence, automatically recover from normal interruption where safe, and expose enough current evidence that any authorized agent can understand what is running without relying on the user's memory.

The user must not need to remember hidden commands, undocumented paths, background processes, or which agent created which file.

---

## 2. Hard invariants

1. `LIVE_TRADING_ENABLED=false`.
2. `SYSTEM3_LIVE_TRADING_ALLOWED=false`.
3. `ORDER_PLACEMENT_ALLOWED=false` for real broker orders.
4. `REAL_BROKER_ORDER_COUNT=0`.
5. Dhan may be connected for read-only market data and account/broker status.
6. PAPER execution is simulated locally only.
7. No active Cloud Run, Cloud Scheduler, Secret Manager, Firestore, Cloud Storage, Pub/Sub, GCP monitoring, or GCP runtime dependency is allowed in the final local architecture.
8. GitHub is the durable code/control authority.
9. Local runtime state is never committed raw to GitHub.
10. Google Drive may contain sanitized runtime evidence, logs, screenshots, traces, manifests, and closed log segments; it must never contain plaintext credentials, tokens, PINs, TOTP secrets, or unsafe broker/account payloads.
11. Every persistent artifact must include agent attribution or a companion manifest.
12. No component may claim PASS from missing data, zero/uninitialized values, replay data, stale evidence, or HTTP 200 alone.

---

## 3. Canonical paths

### 3.1 Code checkout

`C:\Genesis_System3_Clean`

This is the target canonical Git checkout after reconciliation. It must track current remote GitHub authority and must not contain runtime databases/logs/secrets.

### 3.2 Runtime root

`C:\Genesis_System3_Runtime`

Required subfolders:

- `state\`
- `db\`
- `logs\`
- `evidence\`
- `backups\`
- `models\`
- `market_data\`
- `cache\`
- `tmp\`
- `browser\`
- `locks\`
- `manifests\`
- `snapshots\`
- `recovery\`

### 3.3 Secure secret authority

Target secure local vault:

`%USERPROFILE%\.genesis_vault`

Use Windows DPAPI / Windows Credential Manager or an equivalently protected local mechanism. Never store secret values in GitHub, Drive, Markdown, CSV, screenshots, command history, or ordinary logs.

### 3.4 Drive evidence folder

Folder: `Genesis_System3_Archive/AGENT_REVIEW_SYSTEM3`

Folder ID:
`1r0CQbG1fZbK788LMl2lKEBI-YsYt_Y4v`

URL:
`https://drive.google.com/drive/folders/1r0CQbG1fZbK788LMl2lKEBI-YsYt_Y4v?usp=sharing`

### 3.5 Shared visual tracker

`SYSTEM3_MASTER_EXECUTION_TRACKER`

URL:
`https://docs.google.com/spreadsheets/d/15XoBRsUAzJkHO45WZ2bJ2OPvm1yHUBeSkPUm8_fO4yw/edit`

### 3.6 GitHub sanitized runtime mirror target

`reports/runtime/latest/`

Required bounded files after implementation:

- `runtime_status.json`
- `runtime_status.md`
- `dashboard_semantic_summary.json`
- `scheduler_status.json`
- `latest_mri_summary.json`
- `latest_mri_summary.md`
- `gcp_exit_status.json`
- `evidence_manifest.json`
- `SYSTEM3_MASTER_EXECUTION_TRACKER.csv`

Only small sanitized current-state summaries belong here. Raw logs, DBs, browser traces, videos, and high-frequency market data do not belong in GitHub.

---

## 4. Kid-level user guide — how to start System3

The final implementation must provide one supported start command or desktop shortcut. Until verified, agents must not invent one.

Target user experience:

### START

1. Turn on laptop.
2. Connect internet.
3. Wait for Windows login.
4. System3 supervisor should start automatically.
5. Open browser.
6. Go to:
   `http://127.0.0.1:8000/ui`
7. Confirm the top status strip shows:
   - LOCAL LAPTOP runtime
   - exact Git SHA
   - PAPER
   - LIVE OFF
   - broker state
   - market state
   - current feed mode
   - chain/QC state
   - last successful runtime cycle
8. If dashboard does not open within the documented startup window, follow the recovery section below.

### User-visible launcher requirement

Agents must implement one canonical launcher, for example:

`C:\Genesis_System3_Runtime\START_SYSTEM3.cmd`

or a Windows shortcut that invokes an equivalent controlled supervisor.

The launcher must:

- detect duplicate running instance;
- start only the canonical code checkout;
- set canonical runtime root;
- load only local secure credentials;
- set PAPER/ANALYZER safety flags;
- start backend/dashboard;
- start required scheduler/supervisor services;
- write a startup manifest;
- record exact Git SHA;
- record PID/process tree;
- record startup time;
- fail closed if required safety invariants are not present;
- never invoke GCP.

The exact launcher filename must be added here by the implementing agent once proven.

---

## 5. Kid-level user guide — how to know it is working

A non-coder should not need terminal knowledge.

The system is considered visibly healthy only if these user checks are all understandable:

### Green/acceptable

- Dashboard opens at `http://127.0.0.1:8000/ui`.
- Runtime authority says LOCAL LAPTOP.
- Exact Git SHA is present.
- LIVE says OFF.
- Real broker orders say 0.
- Dhan may say CONNECTED/READ-ONLY.
- Market state is truthful: OPEN / CLOSED / HOLIDAY / UNKNOWN.
- Feed state is explicit: BROKER_LIVE / REPLAY / STALE / UNKNOWN.
- Option-chain status includes contracts, timestamps and freshness.
- QC state includes reason.
- Scheduler status shows last run / next run / failures.
- Evidence heartbeat is recent.
- No tab remains indefinitely on Loading.
- No tab shows false success with zero/missing data.

### Not healthy / needs attention

Any of these must create a visible warning and evidence record:

- dashboard unavailable;
- `SERVING SHA` missing;
- GCP/Cloud Run shown as active runtime;
- broker disconnected during expected session;
- token near expiry without successful local rotation;
- market open but chain count remains 0;
- QC NOT_READY during market session;
- stale feed shown as fresh;
- replay shown as live;
- model missing but UI says model ready;
- scheduler stopped;
- supervisor stopped;
- Drive evidence uploader stale;
- local disk low;
- DB/state write failure;
- browser JavaScript crash;
- repeated restart loop;
- any real-order capability becomes enabled.

The dashboard should eventually expose a `System / Operations` panel that summarizes these checks without requiring PowerShell.

---

## 6. What the user should tell an agent when something looks wrong

The user should only need to provide one of these:

- a screenshot of the affected tab;
- the tab name;
- approximate time;
- or simply say "System3 not working".

Agents must then retrieve the current GitHub/Drive evidence and diagnose from standardized artifacts rather than asking the user for technical interpretation.

Required standard diagnostic bundle generated automatically by the laptop:

`C:\Genesis_System3_Runtime\evidence\latest\SYSTEM3_DIAGNOSTIC_BUNDLE.zip`

Target contents:

- runtime status summary;
- exact Git SHA;
- process list for System3 only;
- scheduler state;
- API health snapshot;
- broker metadata with secrets redacted;
- option-chain/QC summary;
- model summary;
- PAPER lifecycle summary;
- recent errors;
- browser semantic summary;
- storage/disk summary;
- restart history;
- Drive sync status;
- manifest with SHA-256.

The implementing agent must create and prove this bundle generator.

---

## 7. Startup automation

Required automation classes:

### 7.1 Supervisor

One canonical supervisor must own the runtime process tree.

It must prevent duplicate instances using a reliable Windows process check, not only a stale PID file.

### 7.2 Windows startup task

A reversible Windows Scheduled Task should start the supervisor at boot or user logon, according to the final verified design.

Required proof:

- actual task name;
- task path;
- trigger;
- executable/action;
- working directory;
- retry/restart settings;
- stop behavior;
- last result;
- next run;
- screenshot or exported sanitized XML if useful;
- independent verification.

### 7.3 Local job scheduler

`config/local_scheduler_registry.yaml` and the actual runtime scheduler must reconcile exactly.

Every former cloud schedule must be classified:

- `LOCAL_IMPLEMENTED`
- `MERGED_WITH_OTHER_JOB`
- `INTENTIONALLY_RETIRED`
- `BLOCKED_WITH_REASON`

No duplicate scheduler should run the same business job.

### 7.4 Dhan token rotation

Rotation must be fully local.

Required metadata only:

- local vault authority;
- token loaded yes/no;
- expiry/time remaining;
- last rotation time;
- last result;
- next due;
- retry count;
- final failure reason if any;
- zero GCP secret calls.

Never log token values.

---

## 8. Shutdown lifecycle

The final user experience should support one canonical safe shutdown mechanism, for example:

`C:\Genesis_System3_Runtime\STOP_SYSTEM3.cmd`

or a supervisor control action.

Before stopping, system must:

1. stop accepting new PAPER lifecycle work;
2. flush DB/state writers;
3. persist current open simulated positions;
4. persist scheduler state;
5. close active log segment;
6. write final heartbeat/runtime status;
7. produce end-of-session manifest;
8. queue closed evidence segments for Drive upload;
9. mark runtime `OFFLINE_EXPECTED`;
10. stop child processes cleanly;
11. verify no System3 worker remains unexpectedly running.

Do not fabricate PAPER exits merely because the laptop shuts down.

---

## 9. Power loss / forced shutdown / crash recovery

Runtime states:

- `RUNNING`
- `OFFLINE_EXPECTED`
- `OFFLINE_UNEXPECTED`
- `RECOVERING`
- `INCOMPLETE_GAP`

On unexpected interruption:

1. Next startup detects stale heartbeat.
2. Mark prior session `OFFLINE_UNEXPECTED`.
3. Record gap start/end.
4. Verify code SHA/config/runtime root.
5. Verify local vault accessible.
6. Verify DB integrity.
7. Verify latest backup.
8. Reconcile scheduler missed jobs.
9. Reconnect broker read-only.
10. Rebuild data feeds.
11. Backfill only from legitimate sources where supported.
12. Never invent market ticks/trades/signals/PAPER fills for the outage.
13. Mark unrecoverable period `INCOMPLETE_GAP`.
14. Resume state as `RECOVERING`.
15. Move to `RUNNING` only after health contracts pass.
16. Generate recovery evidence and sync it to Drive.

Open PAPER positions spanning an outage must be handled by a documented deterministic policy. No agent may assume an exit price that was never observed.

---

## 10. 24-hour logging architecture

The system must preserve all-day operational history without turning GitHub or Drive into an uncontrolled high-frequency database.

### 10.1 Local raw logs — authoritative runtime evidence

All raw high-frequency and detailed logs remain under:

`C:\Genesis_System3_Runtime\logs\`

Required logical streams:

- `runtime/`
- `supervisor/`
- `scheduler/`
- `broker/`
- `market_data/`
- `option_chain/`
- `qc/`
- `signals/`
- `paper/`
- `model/`
- `api/`
- `frontend/`
- `browser/`
- `recovery/`
- `drive_sync/`
- `alerts/`

Every record should include when appropriate:

- UTC timestamp;
- IST timestamp or timezone-aware timestamp;
- session ID;
- process ID;
- agent/component name;
- Git SHA;
- event type;
- severity;
- source;
- market/feed mode;
- correlation ID.

Never write secrets.

### 10.2 Rotation

Use bounded rotation by time and/or size.

Recommended initial policy to validate:

- active structured log rotates every 15 minutes or 25 MB, whichever comes first;
- compressed closed segments retained locally for at least 7 days if disk permits;
- daily manifest retained longer;
- automatic disk-pressure cleanup follows retention class, never random deletion.

Agents must benchmark and adjust based on actual data volume.

### 10.3 Google Drive near-live evidence sync

Do not upload every market tick as a separate Drive API write. That would be inefficient, fragile and difficult to review.

Instead, satisfy near-live observability using two layers:

A. **Current status snapshot**
- sanitized runtime/status JSON/CSV refreshed periodically, target every 1–5 minutes;
- one LATEST object may be replaced rather than creating endless duplicates.

B. **Closed log segments**
- sanitized/compressed closed log segments uploaded after rotation, target every 15 minutes;
- immutable segment naming includes date/time/session/component;
- daily manifest references every uploaded segment and SHA-256.

Suggested Drive subfolder structure under `AGENT_REVIEW_SYSTEM3`:

- `00_CURRENT_STATUS/`
- `01_DAILY_RUNTIME_LOGS/`
- `02_BROWSER_PROOF/`
- `03_DIAGNOSTIC_BUNDLES/`
- `04_RECOVERY_EVENTS/`
- `05_MANIFESTS/`
- `06_PAPER_EVIDENCE/`
- `07_SCHEDULER_EVIDENCE/`
- `08_BROKER_EVIDENCE/`
- `99_MILESTONES/`

Agents must create only if needed and must not create per-agent duplicate trees.

### 10.4 Drive upload manifest

Each uploaded artifact must record:

- filename;
- local source path;
- Drive file ID;
- Drive URL;
- component;
- session ID;
- created UTC;
- uploaded UTC;
- size;
- SHA-256;
- Git SHA;
- CREATED_BY;
- LAST_EDITED_BY;
- sensitivity;
- retention;
- proof purpose.

### 10.5 Drive sync failure

Drive failure must never stop broker/PAPER runtime unless evidence loss becomes unacceptable by configured policy.

Use a durable local upload queue.

States:

- `SYNC_OK`
- `SYNC_DELAYED`
- `SYNC_FAILED_RETRYING`
- `SYNC_BACKLOG`

Retry with backoff. Do not spin continuously.

When connectivity returns, upload missed closed segments and preserve original timestamps.

---

## 11. Google Drive is not a replacement for the local runtime DB

Drive is evidence/archive/visibility storage, not the live transactional database.

Do not run high-frequency trading state directly from Drive spreadsheets/files.

The laptop remains authoritative for active runtime state; Drive contains synchronized evidence copies and summaries.

---

## 12. GitHub day-to-day visibility

GitHub should always let agents answer:

- what exact code SHA should run;
- what runtime state was last published;
- which defects are open;
- who owns each defect;
- which scheduler jobs are implemented;
- whether GCP exit is complete;
- whether PAPER lifecycle is proven;
- where large Drive evidence lives.

Recommended sanitized update cadence:

- state changes / incidents: immediately;
- bounded latest runtime summary: periodically or at meaningful checkpoints;
- daily summary: once per day;
- raw logs: never.

Issue #188 remains the live coordination bus until superseded by an explicit authority update.

Issue #442 remains dashboard semantic defect authority.

Issue #443 remains evidence-routing authority.

---

## 13. No-GCP lifecycle contract

The target runtime must use `127.0.0.1` / localhost only for dashboard/backend communication unless a future explicitly approved external read-only observer is introduced.

Normal runtime responses must not advertise old Cloud Run URLs or GCP region/runtime authority.

Agents must scan active code/config for:

- `.run.app`
- `gcp-cloud-run`
- `asia-south1`
- `system3-openalgo-safe`
- Secret Manager runtime access
- Cloud Scheduler runtime access
- GCS/Firestore live state assumptions
- WIF deploy paths

Every occurrence must be classified as:

- `ACTIVE_FORBIDDEN_DEPENDENCY`
- `HISTORICAL_REFERENCE`
- `MIGRATION_ONLY`
- `TEST_ONLY`
- `SAFE_DOCUMENTATION`

No `ACTIVE_FORBIDDEN_DEPENDENCY` may remain at final acceptance.

Historical migration evidence may remain clearly labeled; do not rewrite history to pretend GCP never existed.

---

## 14. Broker/API lifecycle

Broker connectivity must expose safe metadata:

- broker name;
- read-only/permission mode;
- connection state;
- latency;
- last-good timestamp;
- error reason;
- local credential authority;
- token time remaining;
- last rotation result;
- next retry;
- source freshness;
- zero real-order permission.

On broker failure:

1. mark broker disconnected/degraded;
2. block dependent current-market PAPER entries;
3. retain existing truth without fabricating updates;
4. retry according to bounded policy;
5. log recovery;
6. update status snapshot;
7. upload evidence segment;
8. re-enable only after broker and market-data contracts pass.

---

## 15. Streaming and market-data lifecycle

For every important feed expose:

- source;
- mode: LIVE / REST_POLL / REPLAY / CACHE / UNKNOWN;
- last event timestamp;
- age;
- freshness threshold;
- sequence/gap metadata where possible;
- reconnect count;
- last disconnect reason;
- backfill state;
- current symbol/underlying coverage.

A "4-of-4 FRESH" badge is forbidden unless all four required index chains are actually contract-ready under the defined freshness contract.

Replay data must never satisfy live market-session proof.

---

## 16. PAPER lifecycle evidence

Each simulated PAPER trade must have durable provenance:

- candidate ID;
- strategy/model source;
- source market-data timestamp;
- option contract identifier;
- entry quote provenance;
- gate results;
- simulated fill rule;
- costs/slippage;
- persisted entry;
- exit reason;
- exit quote provenance;
- realized P&L;
- reconciliation state;
- API visibility;
- dashboard visibility.

If the laptop is offline during a period, do not create fictional fills.

Synthetic/test/replay data must never appear as current verified PAPER history.

---

## 17. Automation verification matrix

All automation must be continuously auditable.

For each automation record:

- `AUTOMATION_ID`
- purpose;
- owner component;
- schedule/trigger;
- Windows task/job ID;
- executable path;
- working directory;
- enabled state;
- last run;
- last result;
- next run;
- retry policy;
- timeout;
- duplicate protection;
- dependency;
- evidence path;
- Drive evidence;
- GitHub pointer;
- status: PASS/FAIL/UNKNOWN/RETIRED.

Required automation classes include at minimum:

- runtime supervisor;
- dashboard/backend startup;
- Dhan token rotation;
- market-data collector;
- option-chain refresh;
- forecasts/predictions where required;
- signal generation;
- PAPER engine;
- QC/validation;
- ranking/scanner jobs;
- reconciliation;
- backups;
- log rotation;
- Drive evidence sync;
- heartbeat/status publishing;
- recovery/gap reconciler;
- daily manifest generation.

No automation may be considered working because a config file exists; the actual Windows/runtime instance must be inspected and run-proofed.

---

## 18. Backup policy

Required backups must be local first and optionally copied to Drive after sanitization/encryption suitability review.

Back up:

- runtime DBs;
- state files needed for restart;
- scheduler state;
- model registry/weights that are not reproducibly downloadable;
- PAPER ledger;
- configuration snapshots excluding secrets;
- manifests.

Backups must be restorable, not just created.

Agents must periodically prove restore into a temporary isolated path and delete temporary test copies after evidence capture.

---

## 19. What may be cleaned automatically

Cleanup is allowed only under defined retention and authority.

### Safe candidates after classification

- `tmp\` files older than configured retention and not locked;
- browser cache/artifacts after evidence retention expires;
- expired compressed logs after manifest + Drive sync verification;
- superseded LATEST snapshots if duplicate-safe replacement is used;
- build caches that can be regenerated;
- stale lock files only after process-liveness verification;
- temporary test clones created by an agent after proof is captured.

### Never auto-delete without explicit classified rule

- active DBs;
- PAPER ledger;
- model weights not proven reproducible;
- current state root;
- secure vault;
- backups not yet superseded and verified;
- unsynced evidence;
- unknown user files;
- old repositories/worktrees with unclassified unique commits;
- manifests that prove evidence lineage.

Cleanup must write a deletion manifest with path, reason, size, retention class, actor and timestamp.

---

## 20. Disk pressure handling

Define thresholds after measuring actual disk size.

Suggested behavior:

- NORMAL
- WARNING
- CRITICAL

At WARNING:
- accelerate upload of closed logs;
- compress eligible logs;
- delete only expired TEMP_DELETE artifacts.

At CRITICAL:
- block creation of nonessential large browser/video evidence;
- never delete active DB/PAPER ledger/secrets;
- create visible alert;
- require evidence of cleanup action.

---

## 21. Browser proof automation

The laptop agent must automatically inspect all 22 canonical tabs and publish a bounded semantic matrix.

For each tab:

- URL;
- load time;
- visible state;
- console errors;
- failed network calls;
- WebSocket state;
- relevant API endpoints;
- source/provenance;
- freshness;
- screenshot path/Drive URL if needed;
- PASS/FAIL/UNKNOWN/NOT_EVALUABLE;
- exact Git SHA.

Do not require the user to manually screenshot every tab.

---

## 22. Daily lifecycle

### Before market

- supervisor running;
- exact SHA known;
- local vault healthy;
- broker token healthy;
- broker read-only connection tested;
- security master/instruments loaded;
- scheduler parity checked;
- data collectors ready;
- no GCP dependency detected;
- disk space healthy;
- Drive queue not stuck;
- PAPER ledger available;
- LIVE locks confirmed.

### During market

- broker heartbeat;
- tick/REST feed freshness;
- four index chains;
- QC contracts;
- model/strategy health;
- candidates/signals;
- PAPER lifecycle;
- scheduler;
- runtime heartbeat;
- browser semantic checks at bounded cadence;
- Drive status snapshot updates;
- closed log segments synced.

### After market

- finalize PAPER reconciliation;
- close daily logs;
- generate daily manifest;
- generate daily summary;
- upload closed evidence;
- run backups;
- verify next scheduled jobs;
- keep necessary supervisor services running if 24h mode is intended;
- mark market-closed states explicitly without resetting durable proof incorrectly.

### Overnight / 24h

- system may remain running locally;
- market feed state must show CLOSED/NO-LIVE-SESSION truth;
- token/scheduler/backup/evidence sync jobs continue as required;
- no fake live market freshness;
- incident/recovery logs continue.

---

## 23. Required user-facing operations document set

This standard is the umbrella file. Implementing agents must create/reconcile these durable documents or sections without duplication:

1. `SYSTEM3_LOCAL_RUNTIME_LIFECYCLE_OPERATIONS_STANDARD.md` — this file / master lifecycle authority.
2. `SYSTEM3_KID_LEVEL_USER_GUIDE.md` — simple start/stop/check/recover instructions.
3. `SYSTEM3_AUTOMATION_REGISTRY.md` — human-readable automation map backed by machine registry.
4. `SYSTEM3_RUNTIME_PATHS_AND_FILES.md` — exact file/folder names, purpose, owner, retention, safe-clean status.
5. `SYSTEM3_INCIDENT_RECOVERY_RUNBOOK.md` — power loss/network/broker/token/DB/scheduler/browser recovery.
6. `SYSTEM3_EVIDENCE_AND_DRIVE_SYNC.md` — local logs -> Drive -> GitHub pointer design.

Do not create these as disconnected competing plans. They must cross-reference this file and the machine-readable contracts.

---

## 24. Required machine-readable registries

Agents must implement/reconcile:

- `config/system3_local_runtime_contract.yaml`
- `config/local_scheduler_registry.yaml`
- `config/system3_job_scheduler.json`
- a runtime path/retention registry if not already represented;
- an evidence/Drive sync registry;
- a cleanup retention registry;
- a startup/supervisor registry if useful.

Every human-readable claim must match actual machine configuration and actual Windows/runtime state.

---

## 25. Agent operating rule

Every agent must follow:

`READ CURRENT MAIN + THIS STANDARD + #188 + #442 + #443 -> CHECK OWNERSHIP -> REPRODUCE -> ROOT CAUSE -> FAILING TEST -> IMPLEMENT -> RESTART -> VERIFY LOCAL RUNTIME -> UPDATE TRACKER -> PUBLISH GITHUB EVIDENCE -> UPLOAD LARGE DRIVE EVIDENCE -> RECHECK QUEUE -> CONTINUE`

`IDLE`, `WAIT FOR CHATGPT`, and `WAIT FOR USER` are invalid while safe non-conflicting work exists.

Only genuine blockers:

- unavailable credential/capability;
- owner/account-only external setting;
- destructive authorization;
- unavoidable market-time observation;
- conflicting owned write surface.

---

## 26. Mandatory verification before declaring this lifecycle implemented

No agent may call this standard implemented until all are proven:

- canonical code path exists and is used;
- canonical runtime root exists and is used;
- one supervisor owns runtime;
- Windows startup behavior proven;
- one supported START action proven;
- one supported STOP action proven;
- clean restart proven;
- crash restart proven;
- forced power-off recovery drill or safe equivalent proven;
- network outage/recovery proven;
- broker disconnect/reconnect proven;
- token rotation proven locally;
- zero Secret Manager calls in normal operation;
- scheduler registry matches actual tasks;
- all required jobs have explicit disposition;
- 24h log rotation proven;
- Drive current-status sync proven;
- Drive closed-log-segment sync proven;
- Drive outage queue + catch-up proven;
- daily manifest proven;
- backup + restore proof completed;
- safe cleanup policy proven;
- no GCP runtime URL advertised by localhost;
- active GCP dependency scan clean;
- exact Git SHA visible in runtime;
- 22-tab browser semantic proof completed;
- genuine PAPER lifecycle proven when market conditions permit;
- LIVE OFF and real broker orders 0 independently verified.

---

## 27. Implementation ownership recommendation

### Codex / primary laptop implementation

- supervisor/start/stop/recovery;
- runtime paths;
- logging/rotation;
- local scheduler;
- broker/QC/PAPER plumbing;
- browser collector;
- diagnostic bundle;
- Drive upload queue implementation;
- tests.

### Claude / adversarial independent verifier

- restart/failure drills;
- path/registry parity;
- 22-tab DOM/console/network/API verification;
- false-green detection;
- secret/GCP fallback audit;
- cleanup safety audit.

### Google-AGI / Gemini

- no-GCP dependency verification;
- retired cloud schedule -> local disposition reconciliation;
- local token lifecycle verification;
- current GCP shutdown evidence where still needed.

### Perplexity

- architecture/dependency challenge;
- hidden duplicate producers;
- stale/synthetic/replay contamination;
- better operational alternatives.

### ChatGPT

- controller reconciliation;
- GitHub + Drive + tracker updates;
- reject unsupported PASS;
- maintain this lifecycle authority and issue dispatch.

---

## 28. Required agent checkpoint output

Every implementing/verifying checkpoint must include:

AGENT_NAME=
AGENT_LANE=
START_SHA=
END_SHA=
BRANCH=
PR=
ISSUE=
CANONICAL_CODE_PATH=
CANONICAL_RUNTIME_ROOT=
SUPERVISOR_STATUS=
WINDOWS_STARTUP_TASK=
BROKER_STATUS=
TOKEN_AUTHORITY=
TOKEN_ROTATION_STATUS=
SCHEDULER_STATUS=
LOG_ROTATION_STATUS=
DRIVE_SYNC_STATUS=
DRIVE_BACKLOG=
LATEST_DRIVE_EVIDENCE=
BACKUP_STATUS=
RECOVERY_STATUS=
DISK_STATUS=
22_TAB_STATUS=
PAPER_LIFECYCLE_STATUS=
REAL_BROKER_ORDER_COUNT=
LIVE_TRADING_ENABLED=
GCP_ACTIVE_DEPENDENCIES=
TRACKER_ROWS_UPDATED=
GITHUB_EVIDENCE=
OPEN_BLOCKERS=
NEXT_ACTION=

---

## 29. Current known implementation gaps at creation time

At creation of this document, the following are not yet accepted as complete and must remain open until independently proven:

- canonical local code/runtime path cutover consistency;
- runtime still observed advertising historical Cloud Run URLs from localhost root endpoint;
- option-chain/QC market-open contracts;
- mode semantics PAPER vs ANALYZER;
- local scheduler full unattended proof;
- Windows startup task proof;
- local token authority structural removal of any GCP fallback;
- Drive near-live uploader and closed-segment pipeline;
- 24h log manifest/retention implementation;
- one-click start/stop scripts/user guide;
- crash/power-loss recovery drills;
- Google Sheet -> GitHub sanitized tracker mirror synchronization;
- full 22-tab semantic proof exact current SHA;
- final full-GCP-exit independent proof.

These are implementation tasks, not reasons to weaken the standard.

---

## 30. Definition of success

A non-coder can turn on the laptop, System3 starts predictably, the dashboard shows truthful local state, broker market data is read-only, PAPER execution is simulated, all required automation is visible and verified, interruption is recoverable without fabricated history, 24-hour logs and near-live evidence are preserved locally and synchronized safely to Drive, GitHub always exposes current sanitized status and evidence pointers, all agents can understand the same system without private context, and no normal operation requires GCP.
