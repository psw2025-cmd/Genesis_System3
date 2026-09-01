# Genesis System3 — Local Laptop + GitHub Operating Standard

**Authority marker:** `SYSTEM3_LOCAL_LAPTOP_GITHUB_STANDARD_V1`

**Status:** ACTIVE / LIVING / FULL-GCP-EXIT TARGET

**Applies to:** ChatGPT, Codex, Gemini/Google AGI, Claude, Perplexity, Cursor, browser agents, laptop agents, GitHub agents, and any future System3 agent.

**Purpose:** Define one future-proof operating model for System3 after GCP exit so every agent uses the same code authority, local runtime paths, dashboard truth, schedules, logs, evidence, temporary-work rules, cleanup rules, retention rules, synchronization rules, and handoff protocol without requiring the user to repeatedly explain them.

---

## 0. Non-negotiable program state

1. **GitHub remote `main` is code authority.**
2. **Laptop/local runtime is the target runtime authority for development and PAPER.**
3. **GCP is being fully exited.** No retained GCP runtime, scheduler, token lifecycle, storage, secret, monitoring, WIF/deploy, or recreation dependency is accepted as steady state.
4. **PAPER/ANALYZER only.** LIVE trading remains disabled. `REAL_BROKER_ORDER_COUNT=0`.
5. **Issue #188 is the live multi-agent coordination bus.**
6. **This document defines canonical local/runtime/evidence paths.** Agents must not invent alternate roots unless a migration is explicitly recorded and controller-approved.
7. **Temporary test output is disposable.** If an agent creates temporary files/processes/repos/branches/logs/screenshots for investigation, it owns cleanup in the same work cycle unless the artifact is deliberately promoted to durable evidence.
8. **No agent may claim `DONE`, `FULLY WORKING`, `ZERO-GCP`, `DASHBOARD PASS`, or `PAPER PASS` from source/CI alone.** Runtime and UI evidence is required at the correct authority boundary.

---

## 1. Mandatory read order for every agent/session

Before material work, read in this exact order:

1. `docs/control_plane/GENESIS_SYSTEM3_BILLING_LAPTOP_FIRST_SSOT.md`
2. `docs/control_plane/SYSTEM3_LOCAL_LAPTOP_GITHUB_OPERATING_STANDARD.md` **(this file)**
3. `docs/control_plane/GENESIS_SYSTEM3_AGENT_LIVE_QUEUE.md`
4. latest GitHub Issue `#188`
5. current remote `main`
6. relevant open PR/workflow/file ownership
7. `docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md`
8. task-specific authority/policy files

If branch `docs/billing-laptop-first-ssot` is not yet merged, read the first three controller files from that branch.

Every shared write must begin with:

```text
AGENT_NAME=<exact agent identity>
AGENT_LANE=<lane>
AGENT_ROLE=<role>
```

An agent must re-read the live queue + #188 after every material checkpoint and continue the next safe non-conflicting task. `STANDING BY`, `WAITING FOR CHATGPT`, `WAIT FOR USER`, `NO TASK`, and `IDLE` are invalid while safe unresolved work exists.

---

## 2. Canonical local filesystem architecture

### 2.1 Code checkout

**Canonical clean code root:**

```text
C:\Genesis_System3_Clean
```

Rules:
- this is a Git worktree/clone of `psw2025-cmd/Genesis_System3`;
- before work, fetch remote and record exact remote-main SHA;
- do not place runtime DBs, raw logs, secret vaults, downloads, large model caches, screenshots, browser profiles, generated build artifacts, or ad-hoc temp files inside the code root unless the repository explicitly tracks that small file;
- do not treat another old folder as authority merely because it contains historical data;
- old checkouts are read-only evidence until reconciled, then archive/delete under the retention rules below.

### 2.2 Runtime root

**Target canonical runtime root:**

```text
C:\Genesis_System3_Runtime
```

Subdirectories:

```text
C:\Genesis_System3_Runtime\
  state\          # authoritative runtime state / checkpoints
  db\             # authoritative local SQLite/DB files
  logs\           # rotating runtime logs; NOT committed to Git
  evidence\       # bounded request-scoped proof bundles
  backups\        # bounded verified backups + manifests
  models\         # runtime model artifacts not suitable for Git
  market_data\    # durable local market/instrument history when needed
  cache\          # reproducible cache; safe to delete/rebuild
  tmp\            # disposable agent/test scratch; auto-clean
  browser\        # disposable browser profile/download temp if needed
  locks\           # PID/lock/lease files for duplicate-worker protection
```

Target environment variable:

```text
SYSTEM3_RUNTIME_ROOT=C:\Genesis_System3_Runtime
```

Agents must not silently create a third/fourth runtime state root. Any legacy root discovered must be classified:

```text
AUTHORITATIVE_IMPORT_SOURCE
READ_ONLY_ARCHIVE
DUPLICATE
STALE
DISPOSABLE
UNKNOWN_NEEDS_RECONCILIATION
```

Exactly one writable runtime-state root is allowed after migration.

### 2.3 Secret storage

Target local secret custody:

```text
%USERPROFILE%\.genesis_vault\
```

Secret values must be machine/user protected using Windows secure storage (Credential Manager/DPAPI or equivalent). Never store secret values in:
- GitHub;
- Markdown;
- screenshots;
- Issue #188;
- raw agent prompts;
- plaintext `.env` committed or shared;
- normal logs;
- evidence bundles.

A local runtime PASS requires broker/session/token/TOTP lifecycle to operate with **zero normal GCP Secret Manager / ADC calls**.

---

## 3. Canonical GitHub control-plane paths

All agents must use the same paths:

```text
docs/control_plane/GENESIS_SYSTEM3_BILLING_LAPTOP_FIRST_SSOT.md
    Permanent migration / billing / GCP-exit SSOT.

docs/control_plane/SYSTEM3_LOCAL_LAPTOP_GITHUB_OPERATING_STANDARD.md
    Canonical local paths, logs, schedules, dashboard, evidence, retention and hygiene standard.

docs/control_plane/GENESIS_SYSTEM3_AGENT_LIVE_QUEUE.md
    Current priority queue and lane ownership.

docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md
    Broader autonomous execution and evidence policy.

GitHub Issue #188
    Current live multi-agent coordination/status bus.
```

Durable implementation belongs in normal source paths and a governed PR. Do not use random root-level `.md`, `.txt`, `.json`, screenshots, or scripts as a permanent coordination mechanism.

---

## 4. Dashboard / URL authority after cloud exit

### 4.1 Historical cloud URL

The old Cloud Run URL is **historical/retirement evidence only** once GCP exit completes. It must not remain the runtime authority merely to preserve a convenient public URL.

### 4.2 Laptop dashboard authority

Target local dashboard URLs must be centrally configured, not hard-coded independently by agents. Preferred local bind model:

```text
Backend/API:  http://127.0.0.1:<configured-port>
Dashboard UI: http://127.0.0.1:<configured-port>/ui
```

The actual selected port and launcher must be recorded in one canonical runtime config and reflected in the status snapshot. Agents must discover current config instead of guessing `8000`, `5000`, or another historical port.

### 4.3 One-click launcher

There should be one supported user launcher, for example:

```text
Desktop\Start_Genesis_Local_Dashboard.bat
```

or a repo-owned equivalent that creates/updates this launcher. The launcher must:
- start only the canonical code/runtime roots;
- acquire a duplicate-worker lock;
- verify required local secret custody exists without printing values;
- start backend/supervisor/dashboard in the defined dependency order;
- write PID/heartbeat/status;
- open the canonical local dashboard URL;
- fail closed if LIVE flags are unsafe;
- not invoke GCP.

### 4.4 Dashboard truth contract

The dashboard must visibly expose at minimum:

```text
RUNTIME_STATE = RUNNING | OFFLINE | RECOVERING | INCOMPLETE_GAP
GIT_SHA
GENERATED_AT
HEARTBEAT_AGE
BROKER_STATE
MARKET_SESSION_STATE
DATA_SOURCE
DATA_AS_OF / FRESHNESS
PAPER_STATE
LIVE_TRADING_ENABLED=false
REAL_BROKER_ORDER_COUNT=0
STATE_ROOT_ID / DB ID (non-secret safe identifier)
LAST_SUCCESSFUL_PIPELINE_CYCLE
LAST_GAP / RECOVERY STATUS
```

No green health endpoint may hide stale/blank/contradictory UI data.

### 4.5 22-tab review contract

All agents reviewing the dashboard must apply their expertise to **all canonical tabs**, not only the screenshot the user happened to show. For each tab record:

```text
route/tab id
render status
visible loading/error/blank state
API source endpoint(s)
HTTP/WebSocket status
source/provenance
as-of/freshness
row/symbol/contract counts where relevant
semantic contradiction
console/network errors
state persistence/reload behavior
PAPER safety impact
fix owner
verification owner
```

The dashboard acceptance sequence is:

```text
backend/API healthy
-> broker/read-only source healthy where required
-> current data/freshness healthy
-> browser fresh session
-> 22 canonical tabs render
-> per-tab semantic/API parity
-> reload/reconnect/restart smoke
-> no stale-fake/synthetic production truth
-> PAPER lifecycle visibility
-> exact Git SHA/status truth
```

A screenshot is evidence of what was visible, not proof of hidden API/data correctness.

---

## 5. External dashboard access without GCP

If phone/external-AI access is required while the laptop is online, use a controller-approved **controlled HTTPS access mechanism**. It must:
- expose read-only dashboard/API surfaces by default;
- require appropriate authentication where needed;
- expose no secret values;
- expose no LIVE/order mutation endpoint;
- stop being reachable when laptop/runtime is offline;
- preserve runtime truth: external observer must see `OFFLINE/UNKNOWN` when heartbeat is stale;
- not make GitHub itself the high-frequency runtime transport.

External access is optional and must not become a new cloud dependency equivalent to the retired GCP architecture.

---

## 6. Local scheduler / daily work authority

### 6.1 Scheduler authority

After GCP exit, Windows Task Scheduler + the local supervisor is the canonical scheduling mechanism. There must not be parallel GCP Scheduler/Cloud Run job execution.

### 6.2 Scheduler registry

Maintain one machine-readable registry in source control, for example:

```text
config/local_scheduler_registry.yaml
```

If this file does not yet exist, an implementation agent must create it through a normal PR. It must define for every task:

```text
id
purpose
entrypoint
trigger/schedule
timezone
market-day/holiday condition
timeout
retry policy
missed-run policy
lock name
state/checkpoint path
log stream name
heartbeat expectation
PAPER/LIVE safety requirement
enabled/disabled
owner
```

Do not create ad-hoc Windows tasks without registering them.

### 6.3 Required schedule classes

Inventory and map every retired cloud schedule into one of:

```text
STARTUP_SUPERVISOR
BROKER_SESSION_MAINTENANCE
INSTRUMENT_MASTER_REFRESH
MARKET_DATA_COLLECTION
FORECAST
RANKING
SIGNAL_GENERATION
PAPER_LIFECYCLE
VALIDATION / RECONCILIATION
MODEL / PREDICTION EVALUATION
BACKUP
CLEANUP / RETENTION
HEARTBEAT / STATUS SNAPSHOT
```

Do not assume all historical cloud jobs still belong in the new design. Remove duplicate/dead schedules instead of blindly porting them.

---

## 7. Logs, status and evidence — exact storage model

### 7.1 Raw live logs stay local

Canonical raw log root:

```text
C:\Genesis_System3_Runtime\logs
```

Use structured JSONL/text logs with bounded rotation. Raw high-frequency logs **must not be committed to GitHub**. Replacing a file in Git still grows Git history, so using one filename does not solve repository growth.

Recommended retention target unless a stricter task requires otherwise:
- active runtime log: current file;
- rotate by size/day;
- keep 7 days normal logs;
- keep 30 days compact incident/error summaries;
- preserve only explicitly promoted evidence longer.

No secrets in logs.

### 7.2 GitHub-readable current status

External agents need current truth without raw-log bloat. Maintain small sanitized latest snapshots:

```text
reports/runtime/latest/runtime_status.json
reports/runtime/latest/runtime_status.md
reports/runtime/latest/dashboard_semantic_summary.json
reports/runtime/latest/scheduler_status.json
reports/runtime/latest/gcp_exit_status.json   # until GCP closure only
```

Rules:
- these are **small summaries**, not raw logs;
- update only on material state change or bounded checkpoint, not every tick;
- latest file is a pointer/snapshot, not the historical authority;
- Issue #188 receives concise material transitions and links/SHAs;
- do not commit browser video, huge screenshots, DBs, raw transcripts, or full logs here.

### 7.3 Request-scoped evidence

Local bounded evidence:

```text
C:\Genesis_System3_Runtime\evidence\<request_or_checkpoint_id>\
```

A proof bundle may include:

```text
manifest.json
summary.md
api_samples.json
browser_summary.json
screenshots\ (only necessary captures)
network_summary.json
console_summary.json
test_summary.txt
sha256_manifest.txt
```

When durable GitHub evidence is required, commit only the compact manifest/summary or attach bounded artifacts through approved GitHub mechanisms. Do not commit entire raw evidence directories by default.

### 7.4 Transcript rule

Agent shell transcripts belong under local rotating logs/evidence, not permanent repository source. If an agent produces something like:

```text
logs\inspector\transcript_YYYYMMDD_HHMMSS.txt
```

it must be deleted by retention unless promoted to a named incident proof. Timestamp-per-run files must not accumulate forever.

---

## 8. Replace-vs-append rule

The user wants current output to replace old output where appropriate. Apply this safely:

### Replace in-place / keep only latest
Use for regenerable current-state outputs:

```text
runtime_status.json
scheduler_status.json
dashboard_semantic_summary.json
current_health.json
current_broker_status.json
latest_mri_summary.json
```

### Append/history only when history itself is valuable
Use bounded append/history for:
- PAPER trades and exits;
- prediction-vs-actual evaluation;
- model accuracy history;
- incident timeline;
- migration/deletion audit;
- financial/billing proof;
- data-gap/recovery ledger.

These are not disposable because longitudinal truth matters.

### Never rely on Git overwrite to control repo size
Git retains history. Therefore:
- high-frequency outputs stay outside Git;
- Git stores compact state summaries/config/contracts;
- large mutable data belongs local with backup/manifest;
- temporary output is deleted locally after use.

---

## 9. Automatic cleanup and hygiene contract

Every agent owns cleanup of the side effects it creates.

### 9.1 Immediately remove after successful verification
Unless promoted to durable evidence:
- temp cloned repos;
- temp branches no longer needed;
- browser profiles/downloads;
- generated screenshots used only for a transient check;
- one-off JSON dumps;
- duplicate CSV exports;
- stale test databases;
- temporary patch files;
- `__pycache__`, test caches and disposable build outputs;
- abandoned agent folders;
- duplicate logs/transcripts;
- orphan PIDs/lock files from dead processes.

### 9.2 Never auto-delete without classification
- authoritative PAPER ledger/history;
- model artifacts needed for reproducibility;
- current/rollback broker credential metadata/custody;
- migration source until verified import;
- incident evidence;
- user-created files;
- unknown DBs until reconciled.

### 9.3 Pre-work cleanliness check
Before code work, record:

```text
git status --short
current branch
remote main SHA
untracked files relevant to task
runtime temp size
active System3 processes
active lock files
```

Do not begin by deleting unknown user changes.

### 9.4 Post-work cleanliness check
Before handoff:

```text
working tree status
only intended tracked changes remain
no unexpected root-level artifacts
no temp secrets
no orphan processes
no duplicate supervisor
no disposable browser/test output retained
```

If a test creates junk, the same agent must remove it before reporting completion.

---

## 10. Repository hygiene / growth prevention

### Allowed tracked content
- source code;
- tests;
- configs/schemas;
- small docs;
- compact latest runtime summaries;
- small deterministic fixtures;
- migration manifests/checksums;
- lightweight proof summaries.

### Not allowed in Git by default
- SQLite runtime DBs;
- raw market history;
- secrets;
- model caches/large weights unless intentionally versioned through an approved artifact mechanism;
- raw browser videos;
- large screenshots collections;
- rotating logs;
- transcripts;
- temp clones;
- node_modules/venv;
- build caches;
- raw downloads;
- high-frequency heartbeat commits.

Agents must improve `.gitignore`/cleanup tooling through normal PR governance when a recurring junk class is discovered.

A recurring dirty-repo symptom must be fixed at its **producer**, not repeatedly cleaned manually.

---

## 11. Synchronization model: laptop <-> GitHub

### GitHub contains
- code;
- policies/control docs;
- scheduler definitions;
- schema/configuration;
- compact sanitized latest status;
- issue/PR evidence and decisions.

### Laptop contains
- runtime DB/state;
- raw logs;
- market data/history;
- secret vault;
- caches;
- live processes;
- browser runtime;
- large evidence/backups/models.

### Sync rule
Do not continuously `git add .` from the runtime machine.

A controlled sync process should:
1. fetch remote;
2. generate compact sanitized status snapshots from runtime;
3. diff only allowlisted tracked snapshot files;
4. ensure no secret/large/unexpected file enters staging;
5. commit only on material transition/checkpoint, not per-second/per-minute;
6. push through normal branch/PR policy unless explicitly designated controller-status path;
7. re-fetch/reconcile before write to avoid overwriting another agent.

Raw runtime truth is not duplicated into Git just to make it “live.” External agents consume latest summaries + Issue #188; if deeper raw evidence is needed, a bounded sanitized proof artifact is promoted.

---

## 12. Backup and recovery standard

Canonical backup root:

```text
C:\Genesis_System3_Runtime\backups
```

Backups must include manifest/checksums and identify:

```text
created_at
source_git_sha
runtime_state_root
DB files included
model/config versions
PAPER ledger boundary
known gaps
secret payload included = false
```

Secret vault backups, if needed, must use a separate secure machine/user-protected process and are never placed in normal Git/evidence bundles.

Recommended lifecycle:
- keep latest verified backup;
- keep one previous rollback backup;
- keep incident/migration checkpoint backups when materially different;
- prune redundant backups after checksum + restore verification;
- do not accumulate unlimited timestamped copies.

Recovery states:

```text
RUNNING
OFFLINE
RECOVERING
INCOMPLETE_GAP
```

If laptop is off/hung or data was not captured, preserve an explicit gap unless legitimate source backfill proves reconstruction. Never fabricate PAPER trades or performance across a gap.

---

## 13. Ultra-MRI default output contract

Every major forensic/review agent writes one structured result with these fields:

```text
AGENT_NAME
AGENT_LANE
AGENT_ROLE
CHECKPOINT_OR_TASK
REQUEST_STARTED_AT
EVIDENCE_GENERATED_AT
REMOTE_MAIN_SHA
LOCAL_HEAD_SHA
RUNTIME_ROOT
RUNTIME_STATE
BROKER_STATE
REAL_BROKER_ORDER_COUNT
DASHBOARD_URL
DASHBOARD_22_TAB_VERDICT
STATE_SSOT_VERDICT
SECRET_INDEPENDENCE_VERDICT
SCHEDULER_VERDICT
GCP_EXIT_VERDICT
REPO_CLEANLINESS_VERDICT
ROOT_CONTRADICTIONS
FIXES_IMPLEMENTED
TESTS_RUN
SMOKE_RESULT
RESTART_RECOVERY_RESULT
EVIDENCE_PATHS
TEMP_ARTIFACTS_CREATED
TEMP_ARTIFACTS_CLEANED
BLOCKERS
OWNER_ONLY_ACTION
NEXT_ACTION_TAKEN
```

Verdicts: `PASS`, `FAIL`, `PARTIAL`, `BLOCKED`, `NOT_APPLICABLE`.

No `PASS` when a required field is unverified.

Default compact local MRI output:

```text
C:\Genesis_System3_Runtime\evidence\latest_mri\manifest.json
C:\Genesis_System3_Runtime\evidence\latest_mri\summary.md
```

GitHub summary pointer:

```text
reports/runtime/latest/latest_mri_summary.json
reports/runtime/latest/latest_mri_summary.md
```

The `latest_mri` directory may be replaced on each normal run. If a run proves a material incident/fix/migration checkpoint, promote it to a stable checkpoint ID before replacement.

---

## 14. Multi-agent dashboard review responsibilities

When dashboard defects exist, all agents must review the whole system through their expertise rather than wait for the user to identify every broken tab.

### Codex / implementation lane
- trace UI -> API -> service -> DB/state -> market/broker source;
- reproduce defect;
- add regression test;
- implement smallest root fix;
- run local browser/API smoke;
- clean temporary output.

### Gemini/Google AGI / integration + migration lane
- verify broker/data/session behavior and cloud-to-local dependency removal;
- verify schedules, external dependencies and runtime resource state;
- ensure no retired GCP dependency silently remains.

### Claude / independent verifier
- fresh browser session;
- inspect DOM/console/network/WebSocket/API parity;
- verify source/freshness/semantic truth;
- verify another agent's implementation independently;
- reject superficial render-only PASS.

### Perplexity / second-source audit
- inspect architecture, dependency gaps, stale assumptions, duplicate/dead paths and missed edge cases;
- compare implementation against current source and accepted architecture;
- identify hidden downstream impact.

### ChatGPT Controller
- reconcile contradictory findings;
- update SSOT/live queue/control docs;
- assign correction to implementation owner;
- require independent re-verification;
- preserve one direction across all agents.

---

## 15. Defect lifecycle — no repeated historical problems

A recurring defect must become a permanent control.

Required lifecycle:

```text
SYMPTOM
-> REPRODUCTION
-> ROOT CAUSE
-> REGRESSION TEST / CONTRACT
-> FIX
-> FOCUSED TEST
-> FULL APPLICABLE SMOKE
-> INDEPENDENT VERIFY
-> CLEANUP PRODUCER/SIDE EFFECT
-> DOCUMENT CONTROL
-> CLOSE WITH EVIDENCE
```

Examples:
- dirty repo repeats -> fix ignore/producer/cleanup automation;
- stale forecasts repeat -> freshness gate + provenance contract;
- duplicate worker repeats -> lock/lease + startup test;
- blank dashboard repeats -> semantic browser gate + API parity;
- temporary files repeat -> standard temp root + cleanup hook;
- GCP resource reappears -> workflow/deploy recreation kill-switch.

Do not merely “clean it again.”

---

## 16. Time-based agent expectations

Agents must not wait indefinitely for another agent or the controller.

Use bounded waiting:
- local process/browser warm-up: seconds/minutes with explicit timeout;
- CI: continue safe non-conflicting work while checks run;
- market-hours-only proof: document exact pending observation and continue all off-market work;
- another agent ownership: work another non-conflicting lane;
- controller response: re-read live queue/#188 and continue defined next work.

If a task genuinely requires a specific time (e.g. market-open live data semantic proof), the agent must record:

```text
TIME_BOUND_DEPENDENCY
next_valid_window
what can be completed before then
exact evidence required during window
```

---

## 17. Full GCP-exit compatibility

This local standard must remain compatible with the zero-new-GCP-usage program:
- local launcher never requires GCP;
- local secret lifecycle never requires GCP;
- normal dashboard/API never calls GCP;
- Windows schedules replace required cloud schedules;
- local logs/heartbeat replace Cloud Logging/Monitoring;
- GitHub workflows cannot deploy/invoke/recreate GCP;
- cloud URL is retired;
- after local preservation proof, remaining cloud resources are removed and billing/project closure is verified.

Any newly discovered GCP call in normal local operation is `FULL_GCP_EXIT_FAIL` and must be routed to the responsible implementation lane.

---

## 18. Acceptance checklist for the local operating model

Do not declare this migration architecture operational until independently proven:

- [ ] one canonical clean Git code root;
- [ ] one canonical writable runtime root;
- [ ] one authoritative local state/DB SSOT;
- [ ] local secure secret custody;
- [ ] local broker token/session lifecycle without GCP;
- [ ] registered Windows/local schedules only;
- [ ] duplicate-worker protection;
- [ ] startup/restart/recovery proof;
- [ ] rotating bounded local logs;
- [ ] bounded evidence/backup retention;
- [ ] compact GitHub-readable latest status;
- [ ] no raw-log/high-frequency Git growth;
- [ ] temporary artifact auto/manual cleanup verified;
- [ ] dirty-repo producer controls in place;
- [ ] dashboard canonical URL/config declared;
- [ ] all 22 tabs semantically reviewed;
- [ ] source/freshness/provenance visible;
- [ ] PAPER lifecycle visible and truthful;
- [ ] no synthetic/fake hidden production truth;
- [ ] `LIVE=false`, real broker orders zero;
- [ ] external access, if enabled, is controlled and read-only by default;
- [ ] no normal runtime GCP dependency;
- [ ] no GitHub GCP recreation path;
- [ ] full GCP exit independently verified.

---

## 19. Permanent same prompt for every agent

Once this file is available to the agent, the user should not need to paste a giant task repeatedly. The reusable prompt is:

```text
Work autonomously on psw2025-cmd/Genesis_System3.

First read, in exact order:
1. docs/control_plane/GENESIS_SYSTEM3_BILLING_LAPTOP_FIRST_SSOT.md
2. docs/control_plane/SYSTEM3_LOCAL_LAPTOP_GITHUB_OPERATING_STANDARD.md
3. docs/control_plane/GENESIS_SYSTEM3_AGENT_LIVE_QUEUE.md
4. latest Issue #188
5. current remote main
6. relevant active PR/workflow ownership
7. docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md

If the controller docs are not yet merged, read them from branch docs/billing-laptop-first-ssot.

Identify yourself with AGENT_NAME / AGENT_LANE / AGENT_ROLE on every shared write.
Take the highest-priority safe non-conflicting work for your expertise. Do not wait for ChatGPT/user while safe work exists.

Follow the local-path, runtime-state, dashboard/22-tab, logging, evidence, scheduler, backup, retention, repo-cleanliness and temporary-artifact cleanup rules in SYSTEM3_LOCAL_LAPTOP_GITHUB_OPERATING_STANDARD.md.

For defects use: reproduce -> root cause -> regression -> implement -> smoke -> independent proof -> cleanup -> publish evidence -> continue.

For dashboard work, review all canonical tabs and API/network/source/freshness semantics, not only user screenshots.

For every temporary test/repo/log/screenshot/process you create, either promote it as bounded evidence or delete/clean it before handoff.

Keep GitHub code/control authoritative, laptop runtime authoritative, PAPER/ANALYZER only, LIVE=false, REAL_BROKER_ORDER_COUNT=0, and continue toward full GCP exit / zero new GCP usage after shutdown.

Publish material evidence to Issue #188, re-read the queue, and continue automatically.
```

---

## 20. Change-control rule for this standard

This is a living control document. When a verified discovery changes:
- canonical paths;
- scheduler architecture;
- runtime state model;
- dashboard URL/access model;
- evidence/retention model;
- secret lifecycle;
- GCP-exit dependency;
- multi-agent coordination;
- cleanup/hygiene rules;

then the discovering agent must propose/update this file (or hand the exact change to the controller), update Issue #188, and keep the SSOT/live queue consistent. No important architectural rule should survive only in chat or a temporary agent transcript.
