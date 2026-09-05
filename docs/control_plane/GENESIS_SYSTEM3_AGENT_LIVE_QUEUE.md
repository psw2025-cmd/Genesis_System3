# Genesis System3 — Live Multi-Agent Controller Queue

AGENT_NAME=ChatGPT Controller
AGENT_LANE=D
AGENT_ROLE=Controller / Reconciliation / Next-Task Dispatch

**Status:** ACTIVE / LIVING
**Current program goal:** FULL GCP EXIT + one clean laptop runtime + truthful PAPER dashboard + bounded GitHub coordination/evidence.

## Mandatory read order — updated 2026-09-01
1. `docs/control_plane/GENESIS_SYSTEM3_BILLING_LAPTOP_FIRST_SSOT.md`
2. `docs/control_plane/SYSTEM3_LOCAL_LAPTOP_GITHUB_OPERATING_STANDARD.md`
3. this file
4. latest Issue #188
5. current remote `main`
6. relevant PR/workflow/file ownership
7. `docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md`

Machine-readable operating contracts:
- `config/system3_local_runtime_contract.yaml`
- `config/local_scheduler_registry.yaml`

If these controller documents are not yet merged, read them from branch `docs/billing-laptop-first-ssot`.

Every shared write begins with `AGENT_NAME=`, `AGENT_LANE=`, `AGENT_ROLE=`.

## New permanent operating lock
All agents must follow `SYSTEM3_LOCAL_LAPTOP_GITHUB_OPERATING_STANDARD.md` for:
- canonical code/runtime paths;
- exactly one writable local state root;
- local secure secret custody;
- dashboard URL/runtime truth;
- 22-tab semantic review;
- external read-only access design;
- Windows/local scheduler registry;
- raw-log rotation and GitHub-safe summaries;
- MRI output paths;
- backup/restore/gap truth;
- temporary artifact cleanup;
- dirty-repo/root-junk prevention;
- laptop<->GitHub synchronization;
- bounded evidence retention.

Agents may not invent new roots/scheduler conventions/log folders/status formats merely for convenience. If a better architecture is proven necessary, update the standard through governance and reconcile all agents.

## P0 contradictions still open
1. Full GCP exit is NOT complete.
2. `minScale=0` is not shutdown.
3. Latest agent evidence reported `genesis-system3-dhan-token-rotate-daily` still enabled every 5 minutes and still writing/depending on Secret Manager. This contradicts zero-GCP target and must be removed after local broker session/token lifecycle is independently proven.
4. Historical/agent local paths currently vary; the new target contract is `C:\Genesis_System3_Clean` for code and `C:\Genesis_System3_Runtime` for writable runtime. Agents must measure existing paths, reconcile/migrate safely, and never delete unknown state before classification.
5. Current dashboard has user-visible issues. Review all 22 canonical tabs and semantic/API/network/source/freshness truth, not only screenshots supplied by the user.
6. High-frequency/raw runtime logs must not be committed to GitHub. Git history grows even when filenames are overwritten. Use local rotating raw logs + compact material GitHub summaries/Issue #188 transitions.

## Lane A — Codex / laptop implementation
Execute non-idle:

### A-LOCAL-1 — Canonical runtime migration
- measure all current code/state/db/log/evidence roots;
- produce classification matrix for every existing System3 root;
- move toward `C:\Genesis_System3_Clean` + one writable `C:\Genesis_System3_Runtime` contract;
- preserve unknown/irreplaceable state read-only until reconciliation;
- implement `SYSTEM3_RUNTIME_ROOT` and no third state root;
- prove restart uses same state/DB and no ledger fork.

### A-LOCAL-2 — Secure broker independence
- prove local vault/broker session/token/TOTP lifecycle without ADC/Secret Manager/Cloud Run;
- no plaintext secret output;
- expiry/relogin/restart fail-closed;
- REAL_BROKER_ORDER_COUNT=0.

### A-LOCAL-3 — Scheduler conversion
- populate `config/local_scheduler_registry.yaml` with actual local entrypoints, times, locks, missed-run/gap policy and test evidence;
- reconcile all historical 9 GCP schedules: KEEP_LOCAL / MERGE / REMOVE;
- implement duplicate-worker prevention;
- no unregistered Windows tasks.

### A-LOCAL-4 — Dashboard + API root-fix batch
- fresh local browser session;
- inventory all 22 canonical tabs;
- trace UI -> network/WebSocket -> API -> state/DB -> broker/data source;
- record blank/loading/error/stale/provenance/count contradictions;
- fix root causes with regression tests;
- prove reload/reconnect/restart semantics;
- current SHA/runtime/heartbeat/source/freshness/PAPER/LIVE truth visible.

### A-LOCAL-5 — Logs/evidence/hygiene
- implement bounded raw log rotation under runtime root;
- implement compact sanitized `reports/runtime/latest/*` snapshot generation;
- ensure temp/test output uses runtime `tmp/evidence` roots and is cleaned same work cycle unless promoted;
- fix recurring dirty-repo producers and `.gitignore` gaps through PR;
- do not use `git add .` as runtime sync.

### A-GCP-KILL — Recreation kill-switch
- neutralize all GCP deploy/invoke/rotate/repair workflows/scripts through normal PR governance while retaining useful non-GCP CI.

## Lane B — Google/AGI / GCP exit + dependency verifier
- keep measuring live GCP after-state;
- do not stand by while an invoker/resource remains;
- narrow/retire temporary Logging exclusions as cloud runtime is removed;
- after Lane A independent local proof, disable/delete remaining token scheduler/job and Secret Manager dependency;
- remove Cloud Run service/jobs/Scheduler/Monitoring/PubSub/Firestore/Storage/Artifact Registry/other retained GCP resources after verified local preservation;
- final billing/project closure and post-closure MRI;
- cross-check local runtime contract has zero normal GCP API calls.

## Lane C — Claude / independent browser + implementation verifier
- independently review all 22 local dashboard tabs, DOM, console, network, XHR/fetch/WebSocket and API parity;
- verify local vault has no hidden ADC/Secret Manager fallback;
- verify one state SSOT, restart consistency, stale-forecast blocking and PAPER safety;
- verify scheduler registry matches actual Windows tasks/processes;
- verify raw logs are local/rotated and GitHub summaries are sanitized/bounded;
- verify temp artifacts/processes are cleaned;
- reject render-only/self-declared PASS.

## Lane C2 — Perplexity / architecture + hidden-gap verifier
- audit local/GitHub architecture against the new operating standard;
- find duplicate roots, stale scripts/configs, hidden cloud calls, dead schedules, alternate dashboard URLs, hard-coded ports, ignored/unignored junk classes and data-loss risks;
- independently review dashboard missing features/semantics and downstream dependencies;
- identify any repo-growth design that would re-create storage problems.

## Lane D — ChatGPT Controller
- keep SSOT + operating standard + live queue + #188 reconciled;
- route contradictions to implementation owner and require independent re-verification;
- maintain one canonical path/schedule/log/evidence architecture;
- update the operating standard when verified discoveries change architecture;
- do not accept GCP exit/dashboard/PAPER/local-runtime completion from docs or self-report alone.

## Default outputs
Local raw/runtime:
- `C:\Genesis_System3_Runtime\logs`
- `C:\Genesis_System3_Runtime\evidence`
- `C:\Genesis_System3_Runtime\backups`
- `C:\Genesis_System3_Runtime\tmp`

Compact GitHub-readable latest state:
- `reports/runtime/latest/runtime_status.json`
- `reports/runtime/latest/runtime_status.md`
- `reports/runtime/latest/dashboard_semantic_summary.json`
- `reports/runtime/latest/scheduler_status.json`
- `reports/runtime/latest/latest_mri_summary.json`
- `reports/runtime/latest/latest_mri_summary.md`
- `reports/runtime/latest/gcp_exit_status.json` (until cloud closure)

These paths are target contracts until implementation agents reconcile actual current laptop state. Do not fabricate files/status values simply to satisfy the names.

## Defect closure rule
For every material defect:
`REPRODUCE -> ROOT CAUSE -> REGRESSION -> IMPLEMENT -> FOCUSED TEST -> FULL APPLICABLE SMOKE -> INDEPENDENT VERIFY -> CLEAN TEMP SIDE EFFECTS -> UPDATE CONTROL -> CONTINUE`.

If the same class recurs, fix its producer/contract so it does not require repeated manual cleanup.

## Safety locks
PAPER/ANALYZER only. LIVE OFF. `REAL_BROKER_ORDER_COUNT=0`.
Never expose secret/token/PIN/TOTP values.
Never delete unknown/irreplaceable state before verified classification/export.

## Non-idle rule
After every material result: publish evidence to #188, re-read SSOT + operating standard + this queue + current ownership, then take the next safe non-conflicting task. `IDLE`, `NO TASK`, `STANDING BY`, `WAITING FOR CHATGPT`, `WAIT FOR USER` are invalid while safe work remains.
