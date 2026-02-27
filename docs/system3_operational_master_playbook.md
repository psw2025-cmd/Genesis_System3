# System3 Operational Master Playbook

**Status**: Baseline frozen, Ultra in shadow/safe mode

---

This playbook describes **how to use System3 daily and weekly**, in a controlled way, with all safety switches respected.

It is organized as operational phases:

- **Phase OP1** – Pre-Market Safety & Health
- **Phase OP2** – Start Conservative Live Session (DRY-RUN)
- **Phase OP3** – Intraday Monitoring & Diagnostics
- **Phase OP4** – Post-Market Wrap-Up & Learning
- **Phase OP5** – Weekly Governance & Ultra Review
- **Phase OP6** – Shadow / Ultra Experiments (optional, safe only)

For each phase:

- Commands / menu options
- Files and outputs to check
- Exact confirmations to look for

> **IMPORTANT**: All auto-execution and auto-update switches must remain **disabled** unless explicitly changed.

---

## Phase OP1 – Pre-Market Safety & Health (09:00–09:15)

**Goal**: Confirm System3 is in safe mode and all components are healthy before the market opens.

### OP1.1 – Activate environment and basic status

**Command (PowerShell / CMD in project root):**

```bash
c:\Genesis_System3\venv\Scripts\activate
cd /d C:\Genesis_System3
python -m core.engine.system3_status_check
```

**Expected output / confirmation:**

Shows:

- 75+ engine modules
- 5 trained models
- 41+ menu options

Configuration section shows:

- Auto-execute: **DISABLED**
- Auto-update: **DISABLED**
- Ultra-Mode: Read-only / shadow

**If anything says enabled when it should be disabled, do not start live trading.**

---

### OP1.2 – Monday Morning Pre-Market Diagnostic (Phase 42 menu)

**Command:**

```bash
python run_system3.py
```

In the menu, select:

- **105) Ultra Phase 42: Take Baseline Snapshot**

OR for diagnostic:

- **42) Monday Morning Pre-Market Diagnostic** (if available in menu)

**Expected output / confirmation:**

No exceptions or tracebacks.

Summary lines:

- Models: 5/5 loaded
- Configs: all found
- Ultra-Mode: "read-only" or "safe"

It may write a report, e.g.:

- `storage/ultra/phase42_snapshot_report_*.md`

**You only proceed if this phase ends with "Status: OK" or similar.**

---

### OP1.3 – Environment Guard (Phase 43)

**Command (from menu or direct):**

**Menu:**

- **107) Ultra Phase 43: Environment & Broker Guard Check**

**OR direct:**

```bash
python -m core.engine.system3_phase43_env_guard
```

**Expected files:**

- `storage/config/system3_env_config.json` (auto-created if missing)
- `storage/ultra/phase43_env_guard_report.md`

**Expected confirmation inside report:**

Clear PASS/WARN table.

**Important checks:**

- AngelOne / Binance separation: **PASS**
- Baseline vs Ultra directories separation: **PASS**
- No auto-execute flags: **PASS**

**If any critical check is WARN/FAIL, you stop and investigate.**

---

## Phase OP2 – Start Conservative Live Session (DRY-RUN)

**Goal**: Run System3 in conservative, DRY-RUN mode to collect real signals and test the full pipeline safely.

### OP2.1 – Core boot + health check

In the main menu (`python run_system3.py`):

- **1) Core boot** (basic startup)
- **2) Health check**

**Expected console confirmations:**

No errors.

Messages similar to:

- "Core boot OK"
- "Health check: all green"

---

### OP2.2 – Verify trade config (thresholds & safety)

**In the menu:**

- **16) Threshold Lab / Threshold config viewer** (If there is a direct viewer; else check file.)

**OR:**

```bash
python -m core.engine.angel_trade_config_viewer
```

**OR check file directly:**

```bash
type core\engine\angel_trade_config.py
```

**Expected:**

For each underlying:

- `min_confidence` ≈ 0.80
- `min_abs_score` ≈ 0.30

Global safety limits:

- `max_trades_per_day` ≈ 20
- `max_trades_per_underlying` ≈ 5

**If thresholds are much lower (e.g. 0.5 / 0.1) and you want conservative mode, adjust them back in `angel_trade_config.py`.**

---

### OP2.3 – Ensure auto-execution is OFF

**Inspect:**

```bash
type core\engine\angel_automation_config.py
```

**Confirm:**

```python
AUTO_EXECUTE_TRADES = False
AUTO_SIMULATE_PNL  = False
```

**If any of these are True and you want DRY-RUN only, set them back to False.**

---

### OP2.4 – Start LIVE AI signals loop (safe mode)

**From menu:**

- **11) Angel One index options LIVE AI signals (from models)**

This will:

- Fetch live snapshots from AngelOne
- Run 5 models
- Log into:
  - `storage/live/angel_index_ai_signals.csv`
  - (Optionally) trade plans CSV if any BUY signals appear

**Expected console behavior in conservative mode:**

Blocks like:

```
=== AI SIGNALS SNAPSHOT ===
NIFTY 26200.0 CE ... signal=HOLD conf=1.000 score=0.000
...
[TRADE] No eligible trade candidates in this snapshot.
```

**This is expected with conservative thresholds.**

**You keep this process running during market hours in one terminal.**

---

## Phase OP3 – Intraday Monitoring & Diagnostics

**Goal**: While menu 11 runs, you occasionally check audits, policy dashboards, and environment.

### OP3.1 – Decision Auditor (Phase 35)

**In a second terminal:**

```bash
c:\Genesis_System3\venv\Scripts\activate
cd /d C:\Genesis_System3
python -m core.engine.system3_phase35_ultra_auditor
```

**Expected output:**

Audits ~930 decisions over time.

Summary like:

- OK: xxx, WARN: 0, BLOCK: 0

**If WARN/BLOCK > 0, inspect the generated MD:**

- `storage/ultra/phase35_decision_audit_report.md`

---

### OP3.2 – Policy & Risk Monitor (Phase 37)

```bash
python -m core.engine.system3_phase37_policy_risk_monitor
```

**Expected:**

- `storage/ultra/phase37_policy_risk_dashboard.md`

**Check that:**

- Safety mode: **ACTIVE**
- Auto-execute: **DISABLED**
- Trade limits and thresholds as expected

---

### OP3.3 – Governance Summary (Phase 38)

```bash
python -m core.engine.system3_phase38_governance_summary
```

**Expected:**

- `storage/ultra/phase38_governance_summary.md`

Used mainly as a quick "all green" governance snapshot.

---

## Phase OP4 – Post-Market Wrap-Up & Learning

**Goal**: At the end of the trading session, summarize results, PnL (if any trades), and learning signals.

### OP4.1 – Stop live loop

Press **Ctrl + C** in the terminal that is running menu option 11.

---

### OP4.2 – PnL Simulation & Daily Summary

**If you have any DRY-RUN trade plans:**

```bash
python -m core.engine.angel_pnl_simulator
python -m core.engine.angel_daily_pnl_summary
```

**Expected files:**

- `storage/live/angel_index_ai_pnl_log.csv`

**MD or text summary in console:**

- PnL by underlying
- Trade count, win rate, exit reasons

**If there are no trades (0 BUY signals), PnL is 0% and this is expected.**

---

### OP4.3 – Daily Auto-Reports (menu or direct)

```bash
python -m core.engine.angel_daily_auto_reports
```

**Expected:**

Reports in `storage/reports/`:

- Daily learning report
- Rolling dashboard
- Quick summary

**These are for human review; they do not change configs.**

---

### OP4.4 – Real Outcome Logging (Phase 28–30 / 31–37, depending on naming)

**Run (as configured):**

```bash
python -m core.engine.angel_real_outcome_logger     # Phase 28
python -m core.engine.angel_signal_outcome_analyzer  # Phase 29
python -m core.engine.angel_misfire_detector        # Phase 30
python -m core.engine.system3_phase31_ultra_fusion  # Phase 31
```

**Expected:**

`storage/learning/` and/or `storage/ultra/learning/` filled with:

- Real outcomes CSVs
- Analysis MD files

**You confirm that:**

- New rows appear for the current date.
- Learning reports mention today's date.

---

## Phase OP5 – Weekly Governance & Ultra Review

**Goal**: Once per week (e.g. Saturday), run governance tools and (later) consider promotions.

### OP5.1 – Weekly Governance Pack (Phase 40)

```bash
python -m core.engine.system3_phase40_weekly_governance_pack
```

**Expected:**

Directory: `storage/ultra/weekly_packs/YYYY-Www/` with:

- MD summary
- JSON metrics
- File list

**Review this pack manually to understand performance and robustness.**

---

### OP5.2 – Shadow Campaign Manager (Phase 39)

```bash
python -m core.engine.system3_phase39_shadow_campaign
```

**Expected:**

Uses Phase 31 + 34 to simulate or shadow trades.

Writes a daily shadow summary into `storage/ultra/` (e.g. `phase39_shadow_campaign_summary_*.md`).

**Used for higher-level Ultra experiments without touching baseline.**

---

### OP5.3 – Promotion Executor (Phase 41) – Manual, only when sure

**Only when you have weeks of good results, and only after manual review:**

```bash
python -m core.engine.system3_phase41_promotion_executor
```

**Pre-conditions:**

- Staging models exist (Ultra or Real+Synthetic)
- Required flag file is present
- Baseline backup/snapshot is taken (Phase 42)

**Expected behavior:**

- If prerequisites not met → clean refusal (safety working).
- If all met and confirmation keyword given → promotion from staging to active models.

**Do not run this until you intentionally decide to upgrade models.**

---

## Phase OP6 – Shadow / Ultra Experiments (optional, safe only)

**Goal**: Use Ultra phases 10–20 / 21–30 etc. in shadow mode to learn and improve, while keeping baseline untouched.

### OP6.1 – Ultra Hyperparameter & Feature Exploration

**Examples:**

```bash
python -m core.engine.ultra_shadow_data_engine          # Phase 10
python -m core.engine.ultra_feature_engineering         # Phase 11
python -m core.engine.ultra_train_models                # Phase 12
python -m core.engine.ultra_hparam_explorer             # Phase 13
python -m core.engine.ultra_regime_classifier           # Phase 14
python -m core.engine.ultra_multi_consensus             # Phase 15
python -m core.engine.ultra_threshold_lab                # Phase 16
```

**Expected:**

Outputs under `storage/ultra/` and `core/models/angel_one_ultra/` (or similar Ultra directory).

**No files in baseline model dirs (`core/models/angel_one/`) are changed.**

**Always confirm:**

- Baseline paths unchanged.
- Ultra work stays in its own directories.

---

## Appendix – Daily All-in-One Script (if used)

There is a helper script:

- `system3_ultra_daily_all.bat`

**To run from PowerShell:**

```powershell
.\system3_ultra_daily_all.bat
```

**Use this only after you review what it does inside the .bat file and confirm:**

- It does not enable auto-execution.
- It only calls safe monitoring/report modules and generates reports.

---

## Quick Daily Checklist (operator view)

### Pre-Market (OP1)

- [ ] Status check: OK
- [ ] Env Guard: PASS
- [ ] Pre-market diagnostic: OK

### Start Session (OP2)

- [ ] Thresholds: conservative
- [ ] Auto-execute: DISABLED
- [ ] Menu 11 running: signals streaming, mostly HOLD

### Intraday (OP3)

- [ ] Decision Auditor: OK/WARN=0/BLOCK=0
- [ ] Policy & Risk dashboard: safe mode active

### End of Day (OP4)

- [ ] Stop menu 11
- [ ] Run PnL / reports
- [ ] Log real outcomes & learning

### Weekly (OP5)

- [ ] Weekly pack generated
- [ ] Shadow campaigns and Ultra analyses reviewed
- [ ] No promotions unless explicitly decided

### Ultra Experiments (OP6, optional)

- [ ] Run Ultra phases only in shadow
- [ ] Confirm baseline untouched

---

**This playbook is the main operational reference for System3 in its current safe, conservative configuration.**

