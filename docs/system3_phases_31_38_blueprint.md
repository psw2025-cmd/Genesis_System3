# System3 Ultra Integration Phases 31–38
**Blueprint + Cursor Agent Instructions (Single MD)**

This document defines **Phases 31–38** for System3.  
All work must be **additive**, **safe**, and **Ultra-only** (no baseline overwrite).

> **Note**: Phases 39–40 are intentionally reserved for future global consolidation once more real data is collected. This document fully specifies Phases 31–38 only.

---

## 0. Global Rules and Conventions

### 0.1. Paths and structure

Assume existing structure:

- Project root: `C:\Genesis_System3`
- Core engine: `core/engine/`
- Models:
  - Baseline: `core/models/dhan/`
  - Real+synthetic Ultra: `core/models/dhan_real_blended/`
  - Existing Ultra: `core/models/dhan_ultra/` (if already created)
- Data:
  - Training: `storage/training/`
  - Live signals: `storage/live/dhan_index_ai_signals.csv`
  - Trades: `storage/live/dhan_index_ai_trades_plan.csv`
  - PnL: `storage/live/dhan_index_ai_pnl_log.csv`
  - Learning: `storage/learning/`
  - Reports: `storage/reports/`
  - Ultra: `storage/ultra/` (create if not present)

### 0.2. Safety rules

1. **Never overwrite** baseline files:
   - No write to `core/models/dhan/`
   - No write to baseline config files (except where explicitly allowed and documented)
2. **Ultra outputs** must go under:
   - `storage/ultra/phaseXX_*.{csv,json,md}`
   - `core/models/dhan_ultra/`
3. **No auto-execution**:
   - No automatic broker orders
   - No changes in `AUTOMATION_CONFIG` defaults
4. **All actions must be callable via menu options**.
5. **All write operations must be logged** to console and (if possible) to a small log file under `storage/ultra/`.

### 0.3. New menu options (high level)

Extend `run_system3.py` with:

- `94) Ultra Phase 31: Decision Fusion`
- `95) Ultra Phase 32: vs Baseline Comparator`
- `96) Ultra Phase 33: Promotion Planner`
- `97) Ultra Phase 34: Live Shadow Comparison`
- `98) Ultra Phase 35: Decision Auditor`
- `99) Ultra Phase 36: Continuous Learning Cycle (CULL)`
- `100) Ultra Phase 37: Policy & Risk Monitor`
- `101) Ultra Phase 38: Governance Summary`

(Note: Menu options 94-101 are used to maintain consistency with existing Ultra phase numbering 84-93.)

### 0.4. Implementation conventions for all new phase modules

For every new `system3_phaseXX_*.py` file:

1. **Include a main entrypoint for direct CLI use**:
   ```python
   if __name__ == "__main__":
       path = run_phaseXX_...()
       print(f"[PHASE XX] Output written to: {path}")
   ```

2. **Log key metrics to stdout**:
   - Number of rows processed
   - Number of BUY/HOLD/AVOID (or OK/WARN/BLOCK) where applicable
   - Any early-exit or "no data" conditions

3. **Never modify**:
   - `core/models/dhan/` (baseline models)
   - Baseline automation configs (trade execution, thresholds)
   - All Ultra-related writes must go under `storage/ultra/` or `core/models/dhan_ultra/`.

4. **On any error**:
   - Catch exceptions
   - Print a short `[PHASE XX][ERROR] ...` message
   - Return a string path to a small error MD under `storage/ultra/phaseXX_error_*.md` when possible.

---

# Phase 31 – Ultra Decision Fusion Layer

### 31.1. Objective

Combine all **Ultra outputs** (SL/TP, risk, position size, regime, confidence, score, consensus) into a **single fused per-leg decision**:

- `final_action`: {`STRONG_BUY_CE`, `BUY_CE`, `STRONG_BUY_PE`, `BUY_PE`, `HOLD`, `AVOID`}
- `final_size`: normalized position size (0–1)
- `final_risk_flag`: {`SAFE`, `RISKY`, `BLOCKED`}

### 31.2. Inputs

- Latest Ultra signal-level artifacts (already implemented in phases 21–30), e.g.:
  - `storage/reports_ultra/phase21_risk_evaluations.csv` (from Phase 21)
  - `storage/reports_ultra/phase24_confidence_drift_report.json` (from Phase 24)
  - `storage/reports_ultra/phase29_sensitivity_summary.json` (from Phase 29)
  - `storage/reports_ultra/phase30_calibration_results.csv` (from Phase 30)
  - Note: Phases 22, 23, 25, 26, 27 provide runtime calculations, not stored files
- Live signals snapshot:
  - `storage/live/dhan_index_ai_signals.csv` (latest)

### 31.3. Outputs

- Fused Ultra decision table:
  - `storage/ultra/phase31_ultra_fused_decisions.csv`
- Optional JSON summary:
  - `storage/ultra/phase31_ultra_fused_decisions_summary.json`

Columns in CSV (minimal):

- `timestamp`
- `underlying`
- `strike`
- `side`
- `ltp`
- `spot`
- `model_signal` (original HOLD/BUY_CE/BUY_PE)
- `confidence`
- `score`
- `regime`
- `risk_score`
- `risk_flag`
- `sl_pct`, `tp_pct`
- `ultra_weight` (0–1)
- `final_action`
- `final_size`
- `final_risk_flag`

### 31.4. Cursor Agent – Implementation Steps

1. **Create new engine module**  
   File: `core/engine/system3_phase31_ultra_fusion.py`  
   (Note: Phases 31-38 are integration phases, so they go in `core/engine/` not `core/ultra/`)

2. **Define main API**:

   - `def run_phase31_fusion(max_rows: int = 1000) -> str:`
     - Reads latest signals CSV.
     - Joins with Ultra artifacts (risk, SL/TP, size, regime, etc.).
     - Computes `final_action`, `final_size`, `final_risk_flag` using deterministic rules.
     - Writes `phase31_ultra_fused_decisions.csv`.
     - Returns full output path as string.

3. **Fusion logic (high level, inside comments)**:
   - If `risk_flag == 'BLOCK'` → `final_action = 'AVOID'`, `final_size = 0`, `final_risk_flag = 'BLOCKED'`
   - Else:
     - If `model_signal == 'BUY_CE'` and `score > 0` and `confidence >= 0.85` → `final_action = 'STRONG_BUY_CE'`
     - If `model_signal == 'BUY_PE'` and `score < 0` and `confidence >= 0.85` → `final_action = 'STRONG_BUY_PE'`
     - If `model_signal == 'BUY_CE'` with `confidence >= 0.70` → `BUY_CE`
     - If `model_signal == 'BUY_PE'` with `confidence >= 0.70` → `BUY_PE`
     - Else → `HOLD`
   - Size logic:
     - Base size = `ultra_weight` (0–1) * position_size_factor
     - Clamp between 0 and 1
     - If `final_risk_flag != 'SAFE'` → reduce size by 50–100% accordingly.

4. **Logging**:
   - Print counts of each `final_action` and risk flag.

5. **Menu wiring**:
   - Add option 94 in `run_system3.py`:
     - `python -m core.engine.system3_phase31_ultra_fusion` or call `run_phase31_fusion()` inside menu.

### 31.5. What result to return to you (verification)

From PowerShell:

```powershell
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase31_ultra_fusion
You should send here:

Console lines showing:

Fused decisions count

Distribution of final_action

Head of CSV:

powershell
Copy code
type storage\ultra\phase31_ultra_fused_decisions.csv | Select-Object -First 10
I will verify:

File exists

Columns listed as above

At least some rows present

Distribution looks sane (mostly HOLD/AVOID, maybe few BUYs).

Phase 32 – Ultra vs Baseline Comparator
32.1. Objective
Compare ULTRA fused decisions vs baseline trade plans and PnL, to see:

Does Ultra win more often?

Does Ultra reduce drawdown?

Does Ultra lower risk per trade?

32.2. Inputs
Baseline:

storage/live/dhan_index_ai_trades_plan.csv

storage/live/dhan_index_ai_pnl_log.csv

Ultra:

storage/ultra/phase31_ultra_fused_decisions.csv

32.3. Outputs
Comparison CSV:

storage/ultra/phase32_ultra_vs_baseline_comparison.csv

Summary MD:

storage/ultra/phase32_ultra_vs_baseline_summary.md

32.4. Cursor Agent – Implementation Steps
New file: core/engine/system3_phase32_ultra_vs_baseline.py

Main function:

def run_phase32_comparison() -> str:

Joins baseline trades with PnL.

Aligns Ultra decisions by timestamp/underlying/strike/side.

For each trade:

Baseline action vs Ultra final_action.

Baseline realized PnL vs a hypothetical Ultra PnL (approximate using same entry/exit or estimated).

Writes detailed CSV and summary MD.

Returns summary MD path.

Metrics to compute:

For each underlying and overall:

Baseline:

n_trades, win_rate, avg_pnl, max_dd

Ultra hypothetical:

n_trades_if_ultra, win_rate_ultra, avg_pnl_ultra

Diff:

win_rate_delta, avg_pnl_delta

Menu wiring:

run_system3.py option 95 → calls run_phase32_comparison().

32.5. What result to return here
From PowerShell:

powershell
Copy code
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase32_ultra_vs_baseline
type storage\ultra\phase32_ultra_vs_baseline_summary.md
I want to see:

Table in MD summarizing baseline vs Ultra.

Confirmation that Ultra is not changing any live logic yet (read-only).

Phase 33 – Ultra Promotion Planner (SAFE, NOT AUTO)
33.1. Objective
Design a planner that suggests promotions, but does not auto-apply anything.

It must only output:

“What would be promoted”

“Why”

“Under what conditions”

33.2. Inputs
Output from Phase 32:

phase32_ultra_vs_baseline_comparison.csv

Config snapshots:

Baseline thresholds from storage/config/thresholds_auto.json (or equivalent).

Any Ultra-specific config files (if exist).

33.3. Outputs
Promotion plan JSON:

storage/ultra/phase33_promotion_plan.json

MD explanation:

storage/ultra/phase33_promotion_plan.md

No configs are changed here.

33.4. Cursor Agent – Implementation Steps
New file: core/engine/system3_phase33_promotion_planner.py

Main function:

def run_phase33_promotion_planner() -> str:

Reads comparison data.

Applies simple rules:

If win_rate_ultra >= win_rate_baseline + 5% and avg_pnl_ultra >= avg_pnl_baseline and ultra_drawdown <= baseline_drawdown → eligible = true

Else → eligible = false

Builds JSON:

Per underlying: { "underlying": "...", "eligible": true/false, "recommended_changes": [...] }

Example changes: slightly tighter SL, slightly higher TP, small threshold change, etc.

Writes JSON + MD explanation.

Returns MD path.

Menu wiring:

Option 96 → run_phase33_promotion_planner().

33.5. What result to return here
Run:

powershell
Copy code
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase33_promotion_planner
type storage\ultra\phase33_promotion_plan.md
I will verify:

No configs were actually modified.

Plan clearly marks eligible or not_eligible per underlying.

Reasoning fields included (why/why not).

Phase 34 – Ultra Live Shadow Comparison
34.1. Objective
Run Ultra decisions in shadow, side-by-side with baseline:

Baseline still controls DRY RUN trades.

Ultra decisions are logged separately as shadow trades, never executed.

34.2. Inputs
Live signals (same as menu 11 uses).

Ultra fused decisions (Phase 31).

34.3. Outputs
Shadow trade plan:

storage/live/dhan_index_ai_ultra_trades_shadow.csv

34.4. Cursor Agent – Implementation Steps
New file: core/engine/system3_phase34_ultra_shadow_exec.py

Main function:

def run_phase34_shadow_once() -> str:

Reads latest dhan_index_ai_signals.csv.

Reads phase31_ultra_fused_decisions.csv.

For each leg:

If final_action in {BUY_CE, STRONG_BUY_CE, BUY_PE, STRONG_BUY_PE} and final_risk_flag == 'SAFE':

Append a shadow trade row:

timestamp, underlying, strike, side, action, size, reason='ULTRA_SHADOW'

Appends to dhan_index_ai_ultra_trades_shadow.csv.

Returns path.

Integration with live loop:

In live signals module (already exists), optionally call run_phase34_shadow_once() at end of each cycle only if a config flag like ULTRA_SHADOW_ENABLED = True in a special ultra config.

Default: False.

Menu entry:

Option 97 → manual one-shot shadow exec:

python -m core.engine.system3_phase34_ultra_shadow_exec

34.5. Verification
Run:

powershell
Copy code
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase34_ultra_shadow_exec
type storage\live\dhan_index_ai_ultra_trades_shadow.csv | Select-Object -First 10
Expected:

CSV exists.

Some rows appear (if Ultra produced BUY decisions).

Column reason is always ULTRA_SHADOW.

Phase 35 – Ultra Decision Auditor
35.1. Objective
Audit Ultra fused decisions for:

Over-aggression

Regime mismatch

Excessive size vs baseline risk limits

35.2. Inputs
phase31_ultra_fused_decisions.csv

Shadow Ultra trades: dhan_index_ai_ultra_trades_shadow.csv

Baseline safety limits (read-only from config).

35.3. Outputs
Audit CSV:

storage/ultra/phase35_decision_audit.csv

MD report:

storage/ultra/phase35_decision_audit_report.md

35.4. Cursor Agent – Implementation Steps
New file: core/engine/system3_phase35_ultra_auditor.py

Main function:

def run_phase35_audit() -> str:

For each Ultra trade:

Check if final_size > allowed limit.

Check if trade taken in disallowed regime (e.g., very high volatility).

Check if number of Ultra trades per day > configured max.

Mark each row as OK, WARN, or BLOCK.

Generate aggregated stats and red flags.

Write CSV and MD.

Return MD path.

Menu:

Option 98 → run_phase35_audit().

35.5. Verification
Run:

powershell
Copy code
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase35_ultra_auditor
type storage\ultra\phase35_decision_audit_report.md
I will check:

Counts of OK/WARN/BLOCK.

No auto-config changes.

Clear section listing serious issues (if any).

Phase 36 – Ultra Continuous Learning Cycle (CULL)
36.1. Objective
Create a single orchestrator that can run:

Real data extraction

Blended dataset creation

Ultra training

Ultra validation

Promotion planner

Audit

But only in offline, manual mode.

36.2. Inputs
Existing Phase 7–9 & Phase 10–20 outputs:

master datasets, blended training sets, etc.

Phases 31–35 outputs.

36.3. Outputs
Orchestration log:

storage/ultra/phase36_cull_execution_log.md

36.4. Cursor Agent – Implementation Steps
New file: core/engine/system3_phase36_cull_orchestrator.py

Main function:

def run_phase36_cull_full_cycle() -> str:

Step-wise calls (via imports) to:

Real data extractor

Blended dataset builder

Blended model trainer (Ultra)

Ultra comparison (Phase 32)

Promotion planner (Phase 33)

Auditor (Phase 35)

Captures console-style logs and writes into MD.

Returns MD path.

Safety:

No automatic promotion.

No config changes.

Only reads and writes Ultra files.

Menu:

Option 99 → run_phase36_cull_full_cycle().

36.5. Verification
Run:

powershell
Copy code
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase36_cull_orchestrator
type storage\ultra\phase36_cull_execution_log.md
Expected:

Each sub-phase logged with START/END status.

Any failures marked clearly.

No config files changed.

Phase 37 – Ultra Policy & Risk Monitor
37.1. Objective
Create a single dashboard-style report (MD) summarizing:

Thresholds

Safety limits

Trade caps

Ultra shadow activity

Any violations from Phase 35

37.2. Inputs
Config files (read-only).

Ultra audit results (Phase 35).

Shadow trades file.

37.3. Outputs
MD dashboard:

storage/ultra/phase37_policy_risk_dashboard.md

37.4. Cursor Agent – Implementation Steps
New file: core/engine/system3_phase37_policy_risk_monitor.py

Main function:

def run_phase37_policy_risk_dashboard() -> str:

Reads thresholds, safety limits, trade caps.

Reads last audit results.

Summarizes:

Current safety settings

Number of Ultra shadow trades

Any WARN/BLOCK issues.

Writes MD dashboard.

Returns MD path.

Menu:

Option 100 → run_phase37_policy_risk_dashboard().

37.5. Verification
Run:

powershell
Copy code
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase37_policy_risk_monitor
type storage\ultra\phase37_policy_risk_dashboard.md
Expected:

Clear, human-readable summary of current risk/safety posture.

Phase 38 – Ultra Governance Summary
38.1. Objective
Build a “board-level” one-pager summarizing:

Ultra vs Baseline performance

Risk status

Promotion readiness

Open issues

38.2. Inputs
Phase 32, 33, 35, 37 outputs.

38.3. Output
storage/ultra/phase38_governance_summary.md

38.4. Cursor Agent – Implementation Steps
New file: core/engine/system3_phase38_governance_summary.py

Main function:

def run_phase38_governance_summary() -> str:

Reads:

Ultra vs Baseline summary

Promotion plan

Audit results

Policy & risk dashboard

Produces a compact MD:

Section 1: Performance

Section 2: Risk

Section 3: Recommendation (e.g., “DO NOT PROMOTE YET” or “PROMOTION POSSIBLE AFTER X CONDITIONS”).

Returns MD path.

Menu:

Option 101 → run_phase38_governance_summary().

38.5. Verification
Run:

powershell
Copy code
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase38_governance_summary
type storage\ultra\phase38_governance_summary.md
Expected:

Clear final GO/NO-GO style recommendation text.

Still no automatic promotion.

How to Use This MD With Cursor Agent
For Cursor agent:

Open this file `system3_phases_31_38_blueprint.md` in the workspace.

Implement phases sequentially:

31 → 32 → 33 → 34 → 35 → 36 → 37 → 38

After each phase:

Run the specified Python command.

Capture console output + first lines of key CSV/MD.

Send those outputs back here for verification.

What I Expect From You After Agent Implementation
For each phase (31–38):

Terminal command you ran.

Console output.

type or Select-Object -First 10 of the key file.

Example (for Phase 31):

powershell
Copy code
(venv) PS C:\Genesis_System3> python -m core.engine.system3_phase31_ultra_fusion
(venv) PS C:\Genesis_System3> type storage\ultra\phase31_ultra_fused_decisions.csv | Select-Object -First 10
You paste that here.
I will:

Confirm logic is correct.

Suggest any threshold/logic improvements.

Decide when Ultra is mature enough to consider real influence on trading decisions.

makefile
Copy code
::contentReference[oaicite:0]{index=0}






You said:
See above anything u miss in md


ChatGPT said:

Thought for 26s
Short answer: functionally it’s complete for Phases 31–38.
The only real gap is a naming mismatch and a couple of small conventions you’ll want to add.

1. Main thing actually “missing”
Your MD is titled:

# System3 Ultra Integration Phases 31–40

but you only defined:

Phase 31 – Ultra Decision Fusion

Phase 32 – Ultra vs Baseline Comparator

Phase 33 – Ultra Promotion Planner

Phase 34 – Ultra Live Shadow Comparison

Phase 35 – Ultra Decision Auditor

Phase 36 – Ultra Continuous Learning Cycle

Phase 37 – Ultra Policy & Risk Monitor

Phase 38 – Ultra Governance Summary

There is no Phase 39 or Phase 40 defined.

Given how System3 is already very dense, my recommendation (Option B style) is:

Treat this MD as the final blueprint for Phases 31–38, not 31–40.

Reserve Phases 39–40 for a future “global consolidation / refactor” when you have more real data.

So the one change I strongly recommend the agent makes is:

markdown
Copy code
-# System3 Ultra Integration Phases 31–40  
+# System3 Ultra Integration Phases 31–38  
And optionally add one line after that header:

markdown
Copy code
> Note: Phases 39–40 are intentionally reserved for future global consolidation once more real data is collected. This document fully specifies Phases 31–38 only.
That removes confusion now and keeps space for future upgrades.

2. Two small conventions I would add (not mandatory but useful)
To keep all new modules consistent with existing System3 style, I would add one short subsection in the “0. Global Rules and Conventions” section.

You can ask the agent to append this under 0.3. New menu options (high level):

markdown
Copy code
### 0.4. Implementation conventions for all new phase modules

For every new `system3_phaseXX_*.py` file:

1. Include a main entrypoint for direct CLI use:
   ```python
   if __name__ == "__main__":
       path = run_phaseXX_...()
       print(f"[PHASE XX] Output written to: {path}")
Log key metrics to stdout:

Number of rows processed

Number of BUY/HOLD/AVOID (or OK/WARN/BLOCK) where applicable

Any early-exit or “no data” conditions

Never modify:

core/models/dhan/ (baseline models)

Baseline automation configs (trade execution, thresholds)
All Ultra-related writes must go under storage/ultra/ or core/models/dhan_ultra/.

On any error:

Catch exceptions

Print a short [PHASE XX][ERROR] ... message

Return a string path to a small error MD under storage/ultra/phaseXX_error_*.md when possible.

markdown
Copy code

This doesn’t change logic; it just makes all new modules easier to run, debug, and track.

---

### 3. Quick checklist: what is already covered and OK

You **did not miss** any of these for Phases 31–38:

- For each phase:
  - Objective
  - Inputs and Outputs (with exact file paths)
  - New engine file name (e.g. `system3_phase31_ultra_fusion.py`)
  - Menu mapping (options 48–55)
  - Safety rules (no auto-execute, no baseline overwrite)
  - Exact verification commands (`python -m ...` + `type ... | Select-Object -First 10`)

So once you:

1. Rename the header to “31–38”, and  
2. Optionally add the small **0.4 conventions** block,

the MD is consistent, complete, and ready for the Cursor agent to implement exactly as written.

If you want, I can now give the **exact edit instructions for the agent** (very short) to:

- Update the title line.
- Insert the 0.4 block.
::contentReference[oaicite:0]{index=0}