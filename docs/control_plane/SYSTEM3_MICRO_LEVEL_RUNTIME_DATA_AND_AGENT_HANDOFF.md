# Genesis System3 Micro-Level Runtime, Data, Evidence & Agent Handoff

AGENT_NAME=ChatGPT
AGENT_LANE=D
AGENT_ROLE=Controller / runtime-data governance / agent coordination
CREATED_BY=ChatGPT
LAST_EDITED_BY=ChatGPT
CREATED_AT_UTC=2026-09-02T05:45:00Z
UPDATED_AT_UTC=2026-09-02T05:45:00Z
TASK_OR_ISSUE=#188/#442/#443/PR#453
STATUS=ACTIVE_PROPOSAL_PENDING_INDEPENDENT_VERIFICATION_AND_MERGE

> Companion to `SYSTEM3_LOCAL_RUNTIME_LIFECYCLE_OPERATIONS_STANDARD.md`. This file defines the micro-level inspection, path, evidence, data lineage, folder hygiene, broker, dashboard, DB, feature, option-chain, backtest/history, scheduler and agent-handoff contract. Codex is currently unavailable, so no lane may remain idle because it was previously assigned to Codex.

## 1. Hard safety and authority

- Runtime target: laptop/local only.
- Canonical UI: `http://127.0.0.1:8000/ui`.
- Code authority: GitHub remote `main` after reconciliation.
- Target code checkout: `C:\Genesis_System3_Clean`.
- Runtime root: `C:\Genesis_System3_Runtime`.
- Secure secret authority: `%USERPROFILE%\.genesis_vault` using DPAPI/Windows secure storage or equivalent.
- `LIVE_TRADING_ENABLED=false`.
- `SYSTEM3_LIVE_TRADING_ALLOWED=false`.
- `AUTO_EXECUTE_TRADES=false`.
- `ORDER_PLACEMENT_ALLOWED=false` for real broker orders.
- `REAL_BROKER_ORDER_COUNT=0`.
- No active GCP runtime, Cloud Run, Cloud Scheduler, Secret Manager, Firestore, Cloud Storage, Pub/Sub, GCP monitoring or hidden GCP fallback is allowed in the target local architecture.
- Missing/stale/replay/synthetic data must never be represented as current live truth.

## 2. Agent reassignment while Codex is unavailable

### 2.1 Gemini / Google-AGI — PRIMARY LOCAL IMPLEMENTATION & OPERATIONS OWNER

Until Codex returns, Gemini/Google-AGI takes over all safe non-conflicting Codex local-runtime work, including:

- start/stop/restart System3;
- Windows process/PID/port control;
- stale or duplicate System3 process termination;
- Windows Task Scheduler creation/modification/deletion for System3-owned tasks when safe and reversible;
- scheduler registry reconciliation;
- Dhan local token/vault lifecycle;
- backend and frontend implementation where needed;
- broker data/option-chain/QC tracing;
- local DB/state inspection and migrations;
- runtime launcher/supervisor/recovery implementation;
- browser 22-tab proof automation;
- evidence uploader and Drive backlog/retry;
- folder/path hygiene implementation;
- safe cleanup implementation;
- tracker/GitHub evidence publication.

Gemini must not wait for Codex.

### 2.2 Claude — INDEPENDENT ADVERSARIAL VERIFIER + SECONDARY IMPLEMENTER

Claude must:

- independently verify Gemini implementation;
- reproduce defects independently;
- inspect DOM/console/network/XHR/WebSocket/API/state/DB;
- challenge false green/PASS;
- verify PIDs/ports/tasks/restart behavior;
- verify no real broker order path is enabled;
- verify no GCP fallback remains;
- implement a fix only on a clearly non-conflicting lane when Gemini is blocked/unavailable and publish ownership first.

### 2.3 Perplexity — FORENSIC / ARCHITECTURE / HIDDEN-DEPENDENCY REVIEW

Perplexity must inspect:

- hidden/stale producers;
- duplicate state roots;
- fixture/synthetic/replay contamination;
- old GCP paths;
- historical DB/data files;
- unused or conflicting schedulers;
- feature/model/backtest provenance;
- option-chain dependency graph;
- file/folder duplication and cleanup candidates;
- alternative implementation choices before irreversible cleanup.

### 2.4 Cursor — OPTIONAL NON-CONFLICTING IMPLEMENTATION/REVIEW

If Cursor is available, it may implement/review only after checking #188 and current ownership. It must identify exact branch/SHA and must not duplicate Gemini work.

### 2.5 ChatGPT — CONTROLLER

ChatGPT owns:

- GitHub/Drive/tracker reconciliation;
- maintaining these control-plane documents;
- challenging unsupported DONE/PASS;
- assigning/taking over stale lanes;
- updating shared Google Sheet when evidence is available;
- writing controller findings to #188/#442/#443;
- keeping one consistent data/path/evidence contract.

ChatGPT cannot directly inspect unpublished localhost runtime. Therefore laptop agents must publish standardized evidence automatically. If no fresh GitHub/Drive evidence arrives, status becomes `LOCAL_RUNTIME_INPUT_STALE`, not PASS.

## 3. Mandatory non-idle loop

Every agent executes:

`READ CURRENT TRUTH -> CLAIM NON-CONFLICTING WORK -> REPRODUCE -> TRACE PRODUCER -> ROOT CAUSE -> FAILING TEST -> IMPLEMENT -> FOCUSED TEST -> FULL APPLICABLE SMOKE -> RESTART -> API/UI/DB PROOF -> PUBLISH EVIDENCE -> UPDATE TRACKER -> RE-READ -> CONTINUE`

Invalid states while safe work exists:

- `WAITING_FOR_CODEX`
- `WAITING_FOR_CHATGPT`
- `WAITING_FOR_USER`
- `NO_TASK`
- `IDLE`

## 4. Runtime root and required folders

Target runtime root:

`C:\Genesis_System3_Runtime`

Required canonical structure:

```text
C:\Genesis_System3_Runtime\
  state\
  db\
  logs\
    supervisor\
    backend\
    broker\
    market_data\
    option_chain\
    features\
    models\
    paper\
    scheduler\
    browser\
    evidence_sync\
    recovery\
  evidence\
    latest\
    daily\
  backups\
  models\
  market_data\
    raw\
    normalized\
    snapshots\
  features\
    current\
    history\
  backtests\
    runs\
    manifests\
  history\
    paper\
    signals\
    predictions\
    market\
  cache\
  tmp\
  browser\
    screenshots\
    traces\
    console\
    network\
  locks\
  manifests\
  snapshots\
  recovery\
  upload_queue\
```

Agents must not create another permanent runtime root without controller reconciliation.

## 5. Canonical path registry — required machine-readable artifact

Implement and maintain:

`C:\Genesis_System3_Runtime\manifests\path_registry.json`

Sanitized GitHub mirror target:

`reports/runtime/latest/path_registry.json`

Each entry must include:

- `logical_name`
- `absolute_local_path`
- `purpose`
- `owner_component`
- `producer`
- `consumer`
- `data_class`
- `authority`
- `retention`
- `sensitivity`
- `backup_required`
- `drive_sync_policy`
- `safe_to_clean`
- `cleanup_rule`
- `created_by`
- `last_edited_by`
- `as_of`
- `git_sha` when applicable

Unknown files are not safe to delete.

## 6. Broker / Dhan micro-level contract

Agents must continuously expose sanitized metadata for:

- broker name;
- connection state;
- read-only/analyzer mode;
- client ID present yes/no only;
- access token present yes/no only;
- credential authority;
- token source;
- token expiry/time remaining;
- last successful authentication;
- last failed authentication;
- last rotation attempt;
- last successful rotation;
- next due rotation;
- latency;
- rate-limit state;
- retry/backoff state;
- reconnect attempts;
- last-good connection timestamp;
- real broker order capability=false;
- real broker order count=0;
- any GCP secret calls=0.

Required local evidence:

`C:\Genesis_System3_Runtime\evidence\latest\broker_status.json`

Drive destination:

`AGENT_REVIEW_SYSTEM3/08_BROKER_EVIDENCE/`

Never log secret values, account credentials, PIN, password, TOTP seed or full token.

Broker `connected=true` does NOT prove market-data chain readiness. These are separate states.

## 7. Dashboard micro-level contract

All 22 tabs must be checked against the same runtime authority.

For every tab record:

- tab name;
- exact URL;
- page rendered yes/no;
- loading completed/timeout;
- JS console errors;
- failed network calls;
- WebSocket state;
- API endpoints consumed;
- displayed Git SHA;
- runtime authority;
- broker state;
- market state;
- feed mode;
- data source;
- as-of time;
- age;
- freshness threshold;
- row/count metrics;
- empty/missing state;
- contradictions;
- screenshot path;
- trace path;
- verifier;
- verdict.

Required local artifact:

`C:\Genesis_System3_Runtime\evidence\latest\dashboard_22_tab_matrix.json`

Drive destination:

`AGENT_REVIEW_SYSTEM3/02_BROWSER_PROOF/`

No HTTP 200-only PASS.

## 8. Database and state micro-level contract

Agents must inventory every DB/state source actually consumed by runtime.

Required inventory fields:

- absolute path;
- file type (SQLite/JSON/CSV/Parquet/etc.);
- schema/version;
- size;
- last modified;
- producer process;
- reader process/API;
- row counts/table counts;
- newest business timestamp;
- oldest business timestamp;
- WAL/journal mode if SQLite;
- integrity-check result;
- backup status;
- restore-test status;
- whether test/fixture/demo data exists;
- whether current production/PAPER paths can ever read fixture/demo data.

Target local artifact:

`C:\Genesis_System3_Runtime\evidence\latest\db_state_inventory.json`

Sanitized Drive destination:

`AGENT_REVIEW_SYSTEM3/03_DIAGNOSTIC_BUNDLES/`

DB rules:

1. Runtime DBs stay outside Git checkout.
2. No raw DB committed to GitHub.
3. Before destructive schema/cleanup, create verified backup.
4. PAPER history must identify canonical DB/table/source.
5. Fixture/demo DB must be structurally isolated from runtime authority.
6. A runtime cannot label fixture records current/fresh.
7. After crash/power loss run safe integrity/reconciliation checks before RUNNING.

## 9. Feature pipeline micro-level contract

Trace each trading feature end-to-end:

`RAW MARKET INPUT -> NORMALIZATION -> FEATURE COMPUTATION -> FEATURE STORE/STATE -> MODEL/STRATEGY CONSUMER -> SIGNAL/PREDICTION -> UI/API`

For each feature family document:

- feature name;
- input fields;
- source endpoint/feed;
- timeframe/window;
- calculation module/function;
- missing-data rule;
- warm-up requirement;
- freshness requirement;
- output path/table;
- latest timestamp;
- validation range;
- NaN/inf handling;
- model/strategy consumers;
- leakage prevention;
- replay/backtest/live distinctions.

Target evidence:

`C:\Genesis_System3_Runtime\evidence\latest\feature_pipeline_status.json`

Do not call feature pipeline healthy when values are default zero or stale cache.

## 10. Option-chain micro-level contract

During market hours, trace all four expected underlyings where applicable:

- NIFTY
- BANKNIFTY
- FINNIFTY
- MIDCPNIFTY

For each underlying record:

- security/instrument ID source;
- spot source/value/as-of;
- expiry list source/count;
- selected expiry;
- strike range policy;
- CE contract count;
- PE contract count;
- LTP/bid/ask/OI/volume/IV/Greeks availability;
- broker response status;
- normalization count;
- rejected contract count and reason;
- QC verified count;
- last successful fetch;
- age/freshness threshold;
- live/snapshot/replay mode;
- rate-limit/backoff state;
- API endpoint visible result;
- UI tab visible result.

Target evidence:

`C:\Genesis_System3_Runtime\evidence\latest\option_chain_status.json`

Drive:

`AGENT_REVIEW_SYSTEM3/08_BROKER_EVIDENCE/` and browser proof where visual.

Zero contracts during market open is NOT READY, never green success.

## 11. Market data history contract

Market data must be separated into:

- raw broker capture;
- normalized current state;
- immutable/append-only historical segments where appropriate;
- replay datasets;
- backtest datasets.

Every dataset needs:

- source;
- start/end timestamps;
- timezone;
- instrument universe;
- timeframe;
- row count;
- gaps;
- duplicate count;
- schema version;
- checksum/manifest;
- whether adjusted/unadjusted;
- live/replay/backtest classification.

Do not mix replay data into broker-live status.

## 12. Backtest micro-level contract

For every backtest run preserve a manifest with:

- run ID;
- exact Git SHA;
- strategy/model version;
- dataset ID/checksum;
- date range;
- symbols/contracts;
- bar/tick frequency;
- feature version;
- entry/exit logic;
- fees;
- taxes/charges;
- slippage;
- latency assumption;
- position sizing;
- risk limits;
- lookahead/leakage tests;
- train/validation/test split;
- walk-forward policy;
- random seed if relevant;
- metrics;
- result artifact paths;
- creator/verifier.

Canonical local destination:

`C:\Genesis_System3_Runtime\backtests\runs\<RUN_ID>\`

Large backtest result files are not committed to GitHub. Small sanitized summaries may go under `reports/runtime/latest/` only if currently relevant.

Backtest success must never satisfy a genuine current PAPER lifecycle gate.

## 13. PAPER history contract

Canonical PAPER lifecycle must be traceable:

`MARKET INPUT -> FEATURES -> STRATEGY/MODEL -> CANDIDATE -> GATES -> SIMULATED ENTRY -> POSITION -> SIMULATED EXIT -> COSTS -> REALIZED PNL -> DB -> API -> UI`

Each PAPER trade must preserve:

- unique trade ID;
- candidate/signal ID;
- source market timestamp;
- underlying;
- option type;
- strike;
- expiry;
- simulated entry time/price;
- quote source/freshness;
- SL/TP/exit policy;
- simulated exit time/price;
- costs/slippage;
- realized P&L;
- model/strategy version;
- Git SHA;
- gate snapshot;
- provenance;
- `real_broker_order_id=null`;
- `real_broker_order_count=0`.

Fixture/demo historical trades must never be read by current PAPER production path.

## 14. Prediction/model history contract

For every model/prediction record document:

- model ID/version;
- model file path;
- model checksum;
- training dataset ID;
- training date window;
- validation/test window;
- features;
- target definition;
- prediction timestamp;
- prediction horizon;
- symbol/underlying;
- score/confidence;
- calibration status;
- later actual outcome;
- evaluation timestamp;
- error/accuracy metrics;
- stale threshold;
- fallback used yes/no.

UI states must distinguish:

- NOT_CONFIGURED
- NOT_FOUND
- LOAD_FAILED
- STALE
- LOADED
- VALIDATED
- FORWARD_PAPER_PROVEN

## 15. Scheduler / automation micro-level contract

Inventory all automation from:

- Windows Task Scheduler;
- local scheduler daemon;
- background Python processes;
- browser automation;
- evidence uploader;
- token rotation;
- backup/cleanup jobs;
- daily close/open jobs.

For every task:

- task ID/name;
- owner;
- trigger;
- executable/script;
- working directory;
- environment/runtime root;
- enabled state;
- last start;
- last end;
- last result;
- next run;
- runtime duration;
- retry policy;
- overlap policy;
- duplicate guard;
- output log path;
- recovery behavior;
- expected market-state dependency;
- evidence destination.

Actual tasks must reconcile with `config/local_scheduler_registry.yaml`.

## 16. Start/stop/port/process control

Primary local operator (currently Gemini) must repeatedly prove:

1. identify expected System3 processes;
2. identify owning PID for port 8000 and any other required port;
3. reject duplicate runtime trees;
4. safely kill only System3-owned stale processes;
5. start canonical supervisor;
6. prove API health;
7. prove broker metadata;
8. prove scheduler state;
9. prove dashboard;
10. stop gracefully;
11. confirm ports released;
12. restart;
13. prove state recovery;
14. forced-process-kill drill;
15. recovery drill;
16. reboot/logon startup drill when practical.

Never kill unrelated Windows processes.

## 17. Power loss / shutdown / crash recovery

Runtime states:

- RUNNING
- DEGRADED
- OFFLINE
- RECOVERING
- INCOMPLETE_GAP

After unexpected stop:

1. record stale heartbeat/gap start;
2. restart supervisor;
3. verify exact SHA/config;
4. verify DB integrity;
5. reconcile open simulated PAPER positions;
6. reconcile scheduler missed runs;
7. reconnect broker read-only;
8. restore market-data state without fabricating missing ticks;
9. mark missing interval as gap unless legitimate backfill exists;
10. upload recovery event evidence;
11. transition RECOVERING -> RUNNING only after checks pass.

Drive recovery evidence:

`AGENT_REVIEW_SYSTEM3/04_RECOVERY_EVENTS/`.

## 18. 24-hour logging and Drive evidence policy

Raw high-frequency logs remain local and rotated.

Drive receives sanitized, bounded evidence:

- current status snapshot every ~1–5 minutes when system is running;
- closed/compressed sanitized log segments approximately every ~15 minutes or size boundary;
- immediate failure/recovery event bundles;
- daily manifest/end-of-day summary;
- browser proof on scheduled/triggered MRI cycles;
- scheduler/broker/PAPER evidence on material state change.

If Drive is unavailable, queue locally under:

`C:\Genesis_System3_Runtime\upload_queue\`

Then retry/catch up after connectivity returns.

Drive is not the tick database.

## 19. Drive folder mapping

Shared root:

`AGENT_REVIEW_SYSTEM3`

- `00_CURRENT_STATUS` — replace/update bounded current sanitized status.
- `01_DAILY_RUNTIME_LOGS` — closed sanitized daily/runtime segments.
- `02_BROWSER_PROOF` — 22-tab screenshots/traces/videos.
- `03_DIAGNOSTIC_BUNDLES` — sanitized diagnostic bundles.
- `04_RECOVERY_EVENTS` — shutdown/crash/reconnect/gap events.
- `05_MANIFESTS` — SHA-256/provenance manifests.
- `06_PAPER_EVIDENCE` — PAPER lifecycle summaries/evidence.
- `07_SCHEDULER_EVIDENCE` — task scheduler/local scheduler proof.
- `08_BROKER_EVIDENCE` — broker/token/chain sanitized proof.
- `99_MILESTONES` — milestone-only retained evidence.

## 20. Folder hygiene and cleanup

### NEVER auto-delete

- `.git` or Git source authority;
- canonical runtime DB/state;
- secure vault;
- active model weights;
- current open PAPER position state;
- manifests needed to interpret evidence;
- latest verified backups;
- unresolved diagnostic bundles;
- evidence referenced from an open issue/PR;
- any unknown file.

### Safe-to-clean only by explicit rule

- `cache\` entries past documented TTL;
- `tmp\` after no active process references them;
- old browser screenshots/traces after manifest + retention condition;
- rotated logs after retention + backup/Drive policy is satisfied;
- stale lock/PID files only after verifying owning process is absent;
- test artifacts created by the current test run after evidence capture.

### Repo hygiene

Repo must not contain:

- runtime DBs;
- secrets/token files;
- raw logs;
- screenshots/videos;
- browser traces;
- caches;
- venv/node_modules;
- duplicate runtime roots;
- arbitrary generated reports at repo root.

Dirty repo after task is a defect unless every change is intentionally tracked in the owning PR.

## 21. Continuous status artifacts laptop agents must publish

Laptop agent must maintain sanitized evidence so external agents can understand current runtime without user relay:

- `runtime_status.json`
- `broker_status.json`
- `option_chain_status.json`
- `dashboard_22_tab_matrix.json`
- `db_state_inventory.json`
- `feature_pipeline_status.json`
- `scheduler_status.json`
- `paper_lifecycle_status.json`
- `model_status.json`
- `backtest_latest_summary.json`
- `history_data_status.json`
- `path_registry.json`
- `folder_hygiene_status.json`
- `drive_sync_status.json`
- `recovery_status.json`
- `evidence_manifest.json`

Local authoritative current copies:

`C:\Genesis_System3_Runtime\evidence\latest\`

Drive sanitized current copies:

`AGENT_REVIEW_SYSTEM3/00_CURRENT_STATUS/`

Small bounded GitHub summaries may be mirrored under:

`reports/runtime/latest/`

but only through normal branch/PR governance.

## 22. Freshness rule for external agents

If no new localhost-origin evidence is visible in GitHub/Drive within the expected heartbeat window:

- do not assume runtime is healthy;
- mark `LOCAL_RUNTIME_INPUT_STALE`;
- record last-good timestamp;
- continue all GitHub/Drive work that does not require fresh localhost proof;
- laptop agent must diagnose its evidence uploader/heartbeat;
- user should not be required to manually copy terminal output unless all automatic evidence paths are broken.

## 23. Mandatory diagnostic bundle

Implement one command/automation to create:

`C:\Genesis_System3_Runtime\evidence\latest\SYSTEM3_DIAGNOSTIC_BUNDLE.zip`

Contents, sanitized:

- runtime identity/SHA;
- System3-only process/PID/port tree;
- API health/state;
- broker metadata;
- option-chain/QC;
- scheduler/task state;
- DB/state inventory;
- feature/model status;
- PAPER status;
- recent errors;
- browser semantic matrix;
- folder/disk status;
- Drive sync status;
- recovery history;
- manifest/checksums.

No secrets.

## 24. Current known P0 focus from latest evidence

Current market-hours evidence previously showed:

- localhost running;
- Dhan connected read-only;
- market open;
- `BROKER_LIVE` state;
- QC NOT_READY;
- zero verified contracts/underlyings;
- no current trade;
- no active model;
- generic/contradictory cycle counters;
- stale Cloud Run URLs still surfaced by localhost root;
- LIVE disabled and real order placement disabled.

Therefore priority sequence is:

1. option-chain/QC current-market contract;
2. local runtime identity/no-GCP residues;
3. broker/token structural local-only proof;
4. scheduler/unattended restart proof;
5. PAPER DB/history real-only lineage;
6. feature/model lineage;
7. 22-tab semantic proof;
8. backtest/history provenance;
9. evidence synchronization;
10. folder/path hygiene.

## 25. Done criteria per subsystem

A subsystem is DONE only when:

- exact implementation exists;
- regression test exists where applicable;
- focused test passes;
- full applicable smoke passes;
- runtime restarted;
- API/state/DB/browser evidence agrees;
- no semantic contradiction remains;
- exact Git SHA recorded;
- evidence published;
- tracker row updated;
- independent verifier signs off.

Read-only observation is never DONE.

## 26. Required checkpoint output from every agent

```text
AGENT_NAME=
AGENT_LANE=
TASK=
START_SHA=
END_SHA=
BRANCH=
PR=
LOCAL_RUNTIME_PATH=
RUNTIME_ROOT=
BROKER_STATE=
TOKEN_AUTHORITY=
OPTION_CHAIN_STATE=
QC_STATE=
DB_STATE=
FEATURE_STATE=
MODEL_STATE=
PAPER_STATE=
BACKTEST_STATE=
HISTORY_DATA_STATE=
SCHEDULER_STATE=
22_TAB_STATE=
DRIVE_SYNC_STATE=
FOLDER_HYGIENE_STATE=
REAL_BROKER_ORDER_COUNT=0
LIVE_TRADING_ENABLED=false
GCP_RUNTIME_DEPENDENCY=
TESTS=
EVIDENCE_GITHUB=
EVIDENCE_DRIVE=
EVIDENCE_LOCAL=
INDEPENDENT_VERIFIER=
VERIFICATION_STATUS=
OPEN_BLOCKERS=
NEXT_ACTION=
```

## 27. Controller acceptance

The controller must continually reconcile these domains rather than focusing on UI alone:

BROKER -> MARKET DATA -> OPTION CHAIN -> QC -> FEATURES -> MODEL/STRATEGY -> CANDIDATE -> PAPER LIFECYCLE -> DB/HISTORY -> API -> DASHBOARD -> SCHEDULERS -> RECOVERY -> LOGGING -> DRIVE EVIDENCE -> GITHUB STATUS -> FOLDER HYGIENE.

Any upstream failure invalidates downstream green claims that depend on it.
