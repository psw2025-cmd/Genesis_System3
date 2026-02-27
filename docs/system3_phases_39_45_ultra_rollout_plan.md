# System3 Phases 39–45 – Ultra Rollout & Safety Shell

**Date**: 2025-11-29  
**Status**: DESIGN READY – SAFE, ADDITIVE ONLY

---

System3 Ultra Phases 31–38 are fully implemented, tested, and production-ready, including fusion, comparison, promotion planning, shadow trades, auditing, CULL orchestration, policy monitor, and governance summary.

This plan defines Phases 39–45 to move from "ready and monitored" to "operational rollout" while **preserving all safety guarantees**:

- Baseline remains frozen and protected.
- Ultra remains isolated and read-only by default.
- No auto-execution, no auto-promotion.
- All changes are additive.

---

## Global rules for Phases 39–45

Agent must follow these rules for **all** phases in this file:

1. **No baseline overwrite**
   - Never modify or delete anything under:
     - `core/models/angel_one/`
     - `storage/training/`
     - `storage/config/` (except read-only)
   - All new writes go under:
     - `storage/ultra/`
     - `storage/snapshots/`
     - `storage/reports_ultra/`
     - `storage/logs_ultra/`

2. **No auto-execution of real trades**
   - Do not send any order to any broker.
   - Only log *shadow* trades into:
     - `storage/live/angel_index_ai_ultra_trades_shadow.csv`
   - Trade executor remains DRY RUN only.

3. **No auto-promotion**
   - Baseline models/thresholds must **not** change unless:
     - A dedicated "PROMOTION EXECUTION" phase is run.
     - A hard, explicit "allow" flag is found (text keyword).
     - A snapshot is taken before any copy.

4. **Menu integration**
   - Add new options to `run_system3.py` **after** existing ones:
     - Use menu numbers: `102–108` for Phases 39–45.
   - Each menu option should call a single `run_phaseXX_*` function.

5. **Documentation**
   - For each phase implemented, update docs:
     - Append a short section into:
       - `docs/system3_phases_31_38_README.md` (or create `39_45` doc if cleaner).
     - At end, create:
       - `docs/system3_phases_39_45_completion_summary.md`
       - `docs/system3_phases_39_45_daily_playbook.md`

6. **Logging**
   - All phases must log major steps to:
     - `storage/logs_ultra/system3_phases_39_45.log`
   - Use simple text lines with timestamp.

---

## Phase 39 – Ultra Shadow Live Campaign Manager

**Goal**  
Turn Ultra shadow trading into a *structured campaign*: run fused decisions + shadow trades over a configurable window (e.g., whole trading day) and produce a daily summary.

**New module**  
- `core/engine/system3_phase39_shadow_campaign.py`

**Menu**  
- `run_system3.py` → add option:
  - `102 – Phase 39 – Ultra Shadow Campaign (today)`

### 39.1 – Implementation tasks for agent

1. **Create module skeleton**
   - Functions:
     - `load_config()` – read campaign parameters (loops, sleep seconds) from a simple JSON:
       - `storage/config/ultra_shadow_campaign_config.json`
       - If file missing, use defaults: `{ "loops": 60, "sleep_seconds": 30 }`
     - `run_campaign_once()`:
       - Call Phase 31 fusion (`system3_phase31_ultra_fusion.run_phase31_fusion()`).
       - Call Phase 34 shadow (`system3_phase34_ultra_shadow_exec.run_phase34_shadow_once()`).
     - `run_phase39_shadow_campaign()`:
       - Load config.
       - For `i` from `1..loops`:
         - Log `"[Phase39] Loop i/loops started"`.
         - Call `run_campaign_once()`.
         - Sleep `sleep_seconds`.
       - After loops:
         - Build a **daily summary** MD:
           - `storage/ultra/phase39_shadow_campaign_summary_<YYYYMMDD>.md`
           - Include:
             - Count of fused decisions (read from `phase31_ultra_fused_decisions.csv`).
             - Count of shadow trades (from `angel_index_ai_ultra_trades_shadow.csv`).
             - BUY vs HOLD distribution for Ultra.
             - SAFE vs RISKY decisions.
     - `main()` – CLI entry.

2. **Shadow trade safety**
   - Ensure Phase 34 is still **log-only**:
     - Do not modify Phase 34 behavior.
     - Phase 39 just orchestrates calls.

3. **Config file**
   - If `ultra_shadow_campaign_config.json` does not exist:
     - On first run, create with defaults and log that defaults are used.

4. **Menu integration**
   - In `run_system3.py`:
     - Import `run_phase39_shadow_campaign`.
     - Add menu option 102.
     - In the dispatcher, when user selects `102`, call `run_phase39_shadow_campaign()`.

### 39.2 – What I want to see as confirmation

After agent implements Phase 39, run:

```bash
python -m core.engine.system3_phase39_shadow_campaign
```

**Expected:**

**Console:**
```
Lines like:
[Phase39] Loaded config: loops=X, sleep_seconds=Y
[Phase39] Loop 1/X started
(Phase31) ...
(Phase34) ...
After finishing:
[Phase39] Campaign complete. Summary written to storage/ultra/phase39_shadow_campaign_summary_YYYYMMDD.md
```

**Files:**
- `storage/config/ultra_shadow_campaign_config.json`
- `storage/ultra/phase39_shadow_campaign_summary_YYYYMMDD.md` with:
  - Total fused decisions processed.
  - Total shadow trades.
  - Basic distributions.
- No errors, no baseline writes.

---

## Phase 40 – Weekly Ultra vs Baseline Governance Pack

**Goal**  
Aggregate a full week of outputs into one weekly pack for manual review (no automation changes).

**New module**  
- `core/engine/system3_phase40_weekly_governance_pack.py`

**Menu**  
- `run_system3.py` → add option:
  - `103 – Phase 40 – Weekly Ultra Governance Pack`

### 40.1 – Implementation tasks for agent

**Inputs (7-day window)**

From:
- `storage/ultra/phase32_ultra_vs_baseline_comparison.csv`
- `storage/ultra/phase35_decision_audit.csv`
- `storage/ultra/phase37_policy_risk_dashboard.md`
- `storage/ultra/phase38_governance_summary.md`
- `storage/ultra/phase39_shadow_campaign_summary_*.md` (for last 7 days, if available)

**Time window:**
- Last 7 calendar days by file modification time.

**Outputs**

Create folder per week:
- `storage/ultra/weekly_packs/YYYYWW/` (ISO week).

Inside:
- `weekly_governance_pack.md`:
  - Sections:
    - Week summary (dates).
    - Ultra vs baseline performance summary.
    - Shadow activity summary.
    - Decision safety summary (OK/WARN/BLOCK counts).
    - Promotion readiness note (e.g., "FINNIFTY still eligible, but few trades").
- `weekly_governance_pack_meta.json`:
  - Week number, date range, counts.
- Optionally:
  - `weekly_governance_pack_files.txt` listing included inputs.

**Function**
- `run_phase40_weekly_pack()`:
  - Discover relevant files (last 7 days).
  - Aggregate metrics.
  - Write MD + JSON outputs.
- `main()` for CLI.

**Menu integration**
- `run_system3.py`: option 103 calls `run_phase40_weekly_pack()`.

### 40.2 – What I want to see as confirmation

Run:

```bash
python -m core.engine.system3_phase40_weekly_governance_pack
```

**Expected:**

**Console:**
```
[Phase40] Collecting files for week YYYY-WW
[Phase40] Found X comparisons, Y audits, Z shadow summaries
[Phase40] Weekly pack written to storage/ultra/weekly_packs/YYYYWW/weekly_governance_pack.md
```

**Files:**
- `storage/ultra/weekly_packs/YYYYWW/weekly_governance_pack.md`
- `storage/ultra/weekly_packs/YYYYWW/weekly_governance_pack_meta.json`
- Pack should be read-only: no promotion, no config changes.

---

## Phase 41 – Ultra Promotion Execution Framework (Staging Only)

**Goal**  
Provide a safe, two-step mechanism that can prepare promotion of Ultra to baseline, but does not execute it automatically. This remains a staging step only.

**New module**  
- `core/engine/system3_phase41_promotion_executor.py`

**New directories**  
- `core/models/angel_one_ultra_staging/`
- `storage/snapshots/` (shared with Phase 42)

**Menu**  
- `run_system3.py` → add option:
  - `104 – Phase 41 – Prepare Ultra Promotion (staging only)`

### 41.1 – Promotion rules

Promotion must only proceed to staging if all conditions are met:

1. **Promotion flag file exists:**
   - `storage/config/ultra_promotion_flag.txt`
   - File must contain exact keyword: `ALLOW_ULTRA_PROMOTION_STAGING`

2. **Promotion plan recommends at least 1 underlying:**
   - From `storage/ultra/phase33_promotion_plan.json`

3. **Snapshot directory exists for current time** (created by Phase 42 – see later).

Even when all are true, do not overwrite baseline models; copy to staging only.

### 41.2 – Implementation tasks for agent

**Snapshot check helper**
- Function: `find_latest_snapshot_dir()`:
  - Look under `storage/snapshots/`.
  - Return the latest snapshot path or None.

**Promotion execution to staging**
- `run_phase41_promotion_executor()`:
  - Check flag file; if missing or keyword not present → log and exit.
  - Load `phase33_promotion_plan.json`; extract underlyings with `"eligible": true`.
  - If none → log and exit.
  - Call `find_latest_snapshot_dir()`:
    - If None → log error "No snapshot found, cannot stage promotion" and exit.
  - For each eligible underlying (e.g., FINNIFTY):
    - Identify Ultra model path:
      - `core/models/angel_one_real_blended/<UNDERLYING>_model.pkl`
      - `core/models/angel_one_real_blended/<UNDERLYING>_model_meta.json`
    - Copy these into staging:
      - `core/models/angel_one_ultra_staging/<UNDERLYING>_model.pkl`
      - `core/models/angel_one_ultra_staging/<UNDERLYING>_model_meta.json`
    - Log:
      - `[Phase41] Staged Ultra model for UNDERLYING based on snapshot SNAPSHOT_DIR`
  - Create report:
    - `storage/ultra/phase41_promotion_staging_report.md` describing:
      - Underlyings staged.
      - Source paths.
      - Snapshot used.
      - Flag file status.

**Menu integration**
- `run_system3.py`: option 104 calls `run_phase41_promotion_executor()`.

### 41.3 – What I want to see as confirmation

**Before run:**

Ensure:
- `storage/config/ultra_promotion_flag.txt` exists with correct keyword.
- At least one eligible underlying in `phase33_promotion_plan.json` (e.g., FINNIFTY).
- At least one snapshot exists (Phase 42 will create; see below).

**Run:**

```bash
python -m core.engine.system3_phase41_promotion_executor
```

**Expected:**

**Console:**
```
[Phase41] Promotion flag detected and valid
[Phase41] Eligible underlyings: FINNIFTY, ...
[Phase41] Using snapshot: storage/snapshots/YYYYMMDD_HHMMSS
[Phase41] Staged Ultra model for FINNIFTY -> core/models/angel_one_ultra_staging/...
```

**Files:**
- `core/models/angel_one_ultra_staging/FINNIFTY_model.pkl`
- `core/models/angel_one_ultra_staging/FINNIFTY_model_meta.json`
- `storage/ultra/phase41_promotion_staging_report.md`
- **No files in `core/models/angel_one/` changed.**

---

## Phase 42 – Model Snapshot & Rollback Manager

**Goal**  
Guarantee we can always roll back: snapshot baseline models + configs before any future promotion and provide rollback helpers.

**New module**  
- `core/engine/system3_phase42_snapshot_manager.py`

**Directory**  
- `storage/snapshots/` (if not already present)

**Menu**  
- `run_system3.py` → add options:
  - `105 – Phase 42 – Take Baseline Snapshot`
  - (optional) `106 – Phase 42 – List / View Snapshots`

### 42.1 – Implementation tasks for agent

**Snapshot contents**

Include at minimum:
- `core/models/angel_one/` (all `*_model.pkl` + `*_meta.json`)
- `storage/config/thresholds_auto.json`
- `storage/config/angel_trade_config.py` (copy file as `.txt` for reference)

Store under:
- `storage/snapshots/YYYYMMDD_HHMMSS/`

**Functions**
- `create_snapshot()`:
  - Create new dir with timestamp.
  - Recursively copy required files.
  - Log each copied file.
- `list_snapshots()`:
  - List all snapshot directories with creation time and file counts.
- `run_phase42_snapshot_create()`:
  - Wrapper for command line / menu.
- `run_phase42_snapshot_list()`:
  - Print available snapshots.

**Optional simple rollback helper:**
- Do not auto-rollback; just print instructions:
  - "To rollback, manually copy files from SNAPSHOT_DIR to baseline model directory."

**Menu integration**
- Option 105: call `run_phase42_snapshot_create()`.
- Option 106: call `run_phase42_snapshot_list()`.

### 42.2 – What I want to see as confirmation

Run:

```bash
python -m core.engine.system3_phase42_snapshot_manager create
python -m core.engine.system3_phase42_snapshot_manager list
```

(or via menu)

**Expected:**

**New folder:**
- `storage/snapshots/20251129_XXXXXX/` with:
  - Model files.
  - Configs.

**Console list:**
- Snapshot name, time, file counts.

This snapshot directory will be used by Phase 41 as protection.

---

## Phase 43 – Environment & Broker Guard (Angel vs Binance Separation)

**Goal**  
Ensure System3 (Angel indices) never accidentally touches non-Angel brokers and prepare guardrails for future Binance System3.

**New module**  
- `core/engine/system3_phase43_env_guard.py`

**Menu**  
- `run_system3.py` → add option:
  - `107 – Phase 43 – Environment & Broker Guard Check`

### 43.1 – Implementation tasks for agent

**Checks to implement**

Confirm:
- Angel environment variables present:
  - `ANGEL_API_KEY`, `ANGEL_CLIENT_ID`, etc. (read-only).
- Confirm:
  - No Binance-specific env vars required by this System3 instance (just log if they exist).

**Scan code base for obvious mixed usage** (simple static checks):
- For now, in this phase:
  - Check that `run_system3.py` menu for Angel does not import Binance modules.

**Read a small config:**
- `storage/config/system3_env_config.json`:
  - E.g., `{ "angel_system3_enabled": true, "binance_system3_enabled": false }`
- If missing, create with defaults.

**Output**

MD report:
- `storage/ultra/phase43_env_guard_report.md`:
  - Section:
    - Environment variables detected.
    - Angel config status.
    - Binance config status.
    - Any warnings (e.g., if both true).

**Function**
- `run_phase43_env_guard()`:
  - Perform all checks.
  - Write report.
  - Print summary with PASS/WARN.

### 43.2 – What I want to see as confirmation

Run:

```bash
python -m core.engine.system3_phase43_env_guard
```

**Expected:**

**Console:**
```
[Phase43] Env guard started
Angel System3: ENABLED
Binance System3: DISABLED (for now)
[Phase43] Report written to storage/ultra/phase43_env_guard_report.md
```

**MD report** with clear PASS/WARN lines.

---

## Phase 44 – One-Click "Ultra + Baseline Health & Backup"

**Goal**  
Provide a single entry point that runs core health checks, Ultra checks, and snapshot creation in a controlled sequence.

**New files**  
- `system3_ultra_daily_all.ps1`
- `system3_ultra_daily_all.bat`

**Existing modules used**  
- Phase 37 (policy monitor)
- Phase 38 (governance summary)
- Phase 39 (optional)
- Phase 40 (optional)
- Phase 42 (snapshot create)
- Phase 43 (env guard)

### 44.1 – Implementation tasks for agent

**PowerShell script: `system3_ultra_daily_all.ps1`**

**Steps:**
1. Activate venv.
2. Run:
   - `python -m core.engine.system3_phase43_env_guard`
   - `python -m core.engine.system3_phase37_policy_risk_monitor`
   - `python -m core.engine.system3_phase38_governance_summary`
   - `python -m core.engine.system3_phase42_snapshot_manager create`
3. Optionally (config flag inside script):
   - Run Phase 39 (shadow campaign) if `RUN_CAMPAIGN_TODAY` variable set.
4. At end:
   - Print colored summary: PASS/FAIL per step.

**Batch wrapper: `system3_ultra_daily_all.bat`**
- Simple wrapper calling the PowerShell script.

No menu integration needed (this is OS-level entry).

### 44.2 – What I want to see as confirmation

Run:

```bash
system3_ultra_daily_all.bat
```

**Expected:**

Sequential run of env guard, policy monitor, governance, snapshot.

All PASS with clear messages.

New snapshot directory created.

No crashes even if some inputs missing (must handle gracefully).

---

## Phase 45 – Documentation & Index Consolidation

**Goal**  
Tie everything together into a concise, human-readable index for System3 Ultra, with daily usage patterns.

**New docs**  
- `docs/system3_ultra_master_index.md`
- `docs/system3_ultra_daily_routine.md`

### 45.1 – Implementation tasks for agent

**Master index**

`docs/system3_ultra_master_index.md`:
- Sections:
  - Overview of all Ultra phases (21–38 + 39–45).
  - Table: Phase, Purpose, Module, Output file.
  - "Critical commands":
    - `system3_ultra_master_monitor.bat`
    - `system3_ultra_daily_quick.bat`
    - `system3_ultra_daily_full.bat`
    - `system3_ultra_daily_all.bat`
  - Safety guarantees summary.

**Daily routine**

`docs/system3_ultra_daily_routine.md`:
- **Morning:**
  - Run `system3_ultra_daily_quick.bat`.
  - Optional: run Phase 39 campaign during market hours.
- **After market:**
  - Run `system3_ultra_daily_full.bat`.
  - Run `python -m core.engine.system3_phase40_weekly_governance_pack` once per week.
- **Weekly:**
  - Review weekly pack.
  - Decide whether to set promotion flag + create snapshot.
  - If yes: run Phase 41 staging.

**Strict rule:**
- No change to baseline without:
  - Snapshot (Phase 42).
  - Promotion plan (Phase 33).
  - Staging (Phase 41).
  - Manual confirmation.

**Update existing docs**

In `docs/system3_phases_31_38_README.md` (or new 39–45 doc), add a short section:
- "Phases 39–45: Rollout & Safety Shell" pointing to new docs.

### 45.2 – What I want to see as confirmation

Two new docs with:
- Clear phase table.
- Clear daily/weekly routine.
- Existing docs updated with short references to these.

---

## Final verification checklist for Phases 39–45

After agent implements everything in this plan, I want you to run and share:

1. **Phase 39 basic run**
   ```bash
   python -m core.engine.system3_phase39_shadow_campaign
   ```
   (with small loops in config).

2. **Phase 40 weekly pack**
   ```bash
   python -m core.engine.system3_phase40_weekly_governance_pack
   ```

3. **Phase 42 snapshot**
   ```bash
   python -m core.engine.system3_phase42_snapshot_manager create
   python -m core.engine.system3_phase42_snapshot_manager list
   ```

4. **Phase 41 staging** (after snapshot + flag)
   ```bash
   python -m core.engine.system3_phase41_promotion_executor
   ```

5. **Phase 43 env guard**
   ```bash
   python -m core.engine.system3_phase43_env_guard
   ```

6. **Daily all script**
   ```bash
   system3_ultra_daily_all.bat
   ```

If all of these run without errors, create:

`docs/system3_phases_39_45_completion_summary.md` with:
- Short table: Phase, Status, Notes.
- Statement: "System3 Ultra Phases 39–45 implemented and verified. Baseline remains unchanged; Ultra remains in safe, shadowed mode."

At that point, System3 Ultra will have:
- Full integration (Phases 21–38).
- Rollout, safety shell, snapshots, and routines (Phases 39–45).
- Baseline fully protected and ready for future controlled promotions.

---

**Next step from your side:**  
Ask Cursor agent to implement **exactly this MD** as the new plan, then run the verification commands at the end and paste the outputs when ready.

