# System3 Phases 76–100 – ULTRA GENI Completion Plan  
Root: `C:\Genesis_System3`  
Primary entry: `system3_ultra.py`  

This document defines **Phase 76–100** in full micro-level detail, ready for Cursor Agent to implement.

---

## 0. Conventions

- Root folder: `C:\Genesis_System3`
- Python package root: `core/engine`
- Config: `config/`
- Ultra outputs for these phases: `storage/ultra/ph76_ph100/`
- All new modules MUST:
  - Be read-only by default (no real orders, no baseline overwrite)
  - Use existing logging style (`logging.getLogger(...)`)
  - Respect safety flags from existing System3 configs

**New folder to create (if not present):**

- `storage/ultra/ph76_ph100/`

---

# BLOCK A — GENI AUTONOMOUS LEARNING LOOP (76–80)

## Phase 76 – GENI Self-Critique Engine

### Goal
GENI reviews past signals vs outcomes and creates a **self-critique report**: where it was right, wrong, late, or too conservative.

### Files to create

1. `core/engine/system3_phase76_geni_self_critique.py`
2. `storage/ultra/ph76_ph100/` (ensure exists)
3. Output:
   - `storage/ultra/ph76_ph100/phase76_geni_self_review.json`
   - `storage/ultra/ph76_ph100/phase76_geni_self_review.md`

### Implementation details (for agent)

- Input sources:
  - `storage/live/angel_index_ai_signals.csv`  (historical signals)
  - `storage/live/angel_index_ai_trades_plan.csv` (if exists)
  - `storage/live/angel_index_ai_pnl_log.csv` (if exists)
- For each **signal** row (unique by timestamp, underlying, strike, side):
  - Find any corresponding trade (optional)
  - Find any outcome in PnL log (optional)
- Compute:
  - `was_trade_taken`: bool
  - `direction_correct`: bool / null
  - `missed_profit_opportunity`: bool
  - `too_conservative`: bool (signal was strong but thresholds prevented trade)
  - `too_aggressive`: bool (loss > configured risk threshold)
- Aggregate metrics:
  - Overall:
    - total_signals
    - total_trades
    - correct_direction_count
    - incorrect_direction_count
    - missed_opportunities
    - too_conservative_count
    - too_aggressive_count
  - Per underlying:
    - same metrics grouped by underlying
- Save:
  - JSON with raw structured stats
  - MD summary with human-readable bullets

### Validation command

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase76_geni_self_critique
```

### Expected confirmation in log

- `[PH76] Loaded X signals, Y trades, Z pnl rows`
- `[PH76] Self-critique summary written to storage/ultra/ph76_ph100/phase76_geni_self_review.json`
- `[PH76] Markdown report written to storage/ultra/ph76_ph100/phase76_geni_self_review.md`

Expected output for me:
- MD file with:
  - Table per underlying
  - Sections “Too conservative” and “Too aggressive” with counts and explanation.

---

## Phase 77 – GENI Self-Correction Engine

### Goal
Use Phase 76 self-critique to propose **concrete corrections** (not apply them automatically) to thresholds and rules.

### Files to create

1. `core/engine/system3_phase77_geni_self_correction.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase77_geni_self_corrections.json`
   - `storage/ultra/ph76_ph100/phase77_geni_self_corrections.md`

### Implementation details

- Load Phase 76 review JSON.
- For each underlying:
  - If `too_conservative_count` is high and accuracy is good:
    - Propose lower `min_confidence` or `min_abs_score`
  - If `too_aggressive_count` is high and accuracy is poor:
    - Propose higher `min_confidence` or `min_abs_score`
  - Keep adjustments within safe bands (e.g. 0.60–0.95 for confidence).
- Structure JSON as:

```json
{
  "timestamp": "...",
  "recommendations": [
    {
      "underlying": "NIFTY",
      "current_conf": 0.80,
      "suggested_conf": 0.75,
      "reason": "Too conservative: missed X profitable opportunities."
    }
  ]
}
```

- MD summary:
  - Table of `underlying | current_conf | suggested_conf | reason`
  - Section with human-readable bullet recommendations.

### Validation command

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase77_geni_self_correction
```

### Expected confirmation

- `[PH77] Loaded self-review from phase76_geni_self_review.json`
- `[PH77] Generated N correction recommendations`
- `[PH77] Saved JSON + MD to storage/ultra/ph76_ph100/phase77_geni_self_corrections.*`

Expected output for me:
- MD file with at least one recommendation row (or a note “no recommendations, insufficient data”).

---

## Phase 78 – GENI Multi-Model Consensus Engine

### Goal
Combine **Baseline model, Ultra model, and any heuristic signals** into a single **consensus signal** per option leg.

### Files

1. `core/engine/system3_phase78_geni_consensus.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase78_geni_consensus.parquet`
   - `storage/ultra/ph76_ph100/phase78_geni_consensus.md`

### Implementation details

- Inputs:
  - Baseline prediction file(s) (same structure as live signals; re-use whichever file System3 already uses as baseline predictions)
  - Ultra prediction file(s) (from Ultra phases — reuse whichever is considered “Ultra primary signal table”)
- For each `(timestamp, underlying, strike, side)`:
  - Collect:
    - `baseline_label`, `baseline_conf`
    - `ultra_label`, `ultra_conf`
    - `heuristic_label` (optional; can be derived from simple rule-based logic)
- Consensus rule:
  - If baseline and ultra agree on BUY_CE or BUY_PE:
    - `consensus_label = that label`
    - `consensus_conf = average(baseline_conf, ultra_conf)`
  - If one says BUY_* and the other HOLD:
    - `consensus_label = BUY_*` if `conf > high_threshold` else `HOLD`
  - If they disagree on direction (BUY_CE vs BUY_PE):
    - `consensus_label = HOLD`
    - `conflict = True`
- Save full per-leg row with:
  - all model fields
  - `consensus_label`, `consensus_conf`, `conflict`.

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase78_geni_consensus
```

Expected logs:

- `[PH78] Loaded baseline predictions: X rows`
- `[PH78] Loaded ultra predictions: Y rows`
- `[PH78] Consensus table saved to phase78_geni_consensus.parquet`

Expected MD:
- Total rows
- Count of consensus BUY_CE / BUY_PE / HOLD
- Count of conflicts.

---

## Phase 79 – Adaptive Threshold Engine

### Goal
Use volatility/regime features to generate **adaptive thresholds** per regime instead of single fixed values.

### Files

1. `core/engine/system3_phase79_adaptive_thresholds.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase79_adaptive_thresholds.json`
   - `storage/ultra/ph76_ph100/phase79_adaptive_thresholds.md`

### Details

- Inputs:
  - Regime classification outputs (from existing regime phases, e.g. Phase 14/46/49)
  - Historical signals + PnL.
- For each **regime** (e.g. LOW_VOL, MID_VOL, HIGH_VOL, TREND_UP, TREND_DOWN, CHOPPY):
  - Grid-search threshold combinations:
    - conf: 0.60–0.95
    - score: 0.10–0.60
  - For each combo:
    - compute hit-rate
    - avg PnL per trade
    - number of trades (ensure `>= N_min`).
- Choose best combination per regime based on:
  - primary: highest avg PnL
  - secondary: stable hit-rate, enough trades.

JSON:

```json
{
  "timestamp": "...",
  "regimes": {
    "LOW_VOL": { "min_conf": 0.72, "min_score": 0.20, "win_rate": 0.61, "avg_pnl": 0.8 },
    "HIGH_VOL": { "min_conf": 0.83, "min_score": 0.35, "win_rate": 0.54, "avg_pnl": 1.2 }
  }
}
```

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase79_adaptive_thresholds
```

Expected log:

- `[PH79] Evaluated threshold grid for R regimes`
- `[PH79] Saved best per-regime thresholds to phase79_adaptive_thresholds.json`

Expected MD:
- Table: `regime | min_conf | min_score | win_rate | avg_pnl | trades_used`.

---

## Phase 80 – GENI Evolution Status

### Goal
Create a high-level **evolution status** overview describing how GENI should evolve (more aggressive, more conservative, feature focus, etc.).

### Files

1. `core/engine/system3_phase80_geni_evolution_status.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase80_geni_evolution_status.json`
   - `storage/ultra/ph76_ph100/phase80_geni_evolution_status.md`

### Details

- Inputs:
  - Phase 76–79 outputs.
- Combine into:
  - current strengths & weaknesses
  - proposed threshold adjustments
  - suggested risk profile changes
  - suggested feature emphasis.
- JSON: structured, machine-readable.
- MD: clearly separated sections:
  - Accuracy improvements
  - Risk adjustments
  - Threshold recommendations
  - Next-step actions (5–10 bullet points).

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase80_geni_evolution_status
```

Expected:

- `[PH80] Aggregated GENI evolution recommendations`
- MD with at least 5 concrete bullet actions.

---

# BLOCK B — LATENCY, SCHEDULING, PERFORMANCE (81–85)

## Phase 81 – Micro-Latency Profiler

### Goal
Measure per-step latency inside live loops: data fetch, feature build, model inference, trade logic, logging.

### Files

1. `core/engine/system3_phase81_latency_profiler.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase81_latency_profile.json`
   - `storage/ultra/ph76_ph100/phase81_latency_profile.md`

### Details

- Wrap existing live loop (or simulate) but **do not modify production behavior**:
  - For each iteration:
    - time snapshot: before/after each step.
  - Steps to track:
    - snapshot_fetch_ms
    - features_build_ms
    - model_infer_ms
    - trade_logic_ms
    - logging_ms
    - total_loop_ms.
- Collect metrics for N iterations (configurable).

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase81_latency_profiler
```

Expected logs:

- `[PH81] Collected latency metrics across N iterations`
- `[PH81] Latency profile saved`

Expected MD:
- Table: `step | min_ms | max_ms | avg_ms`
- Brief comments about any step above a threshold.

---

## Phase 82 – Async Job Scheduler

### Goal
Provide a **job scheduler abstraction** to run tasks (fetch, train, eval, reports) in a controlled way.

### Files

1. `core/engine/system3_phase82_job_scheduler.py`
2. Config:
   - `config/system3_job_scheduler.json`
3. Output:
   - `storage/ultra/ph76_ph100/phase82_job_scheduler_state.json`
   - `storage/ultra/ph76_ph100/phase82_job_scheduler_log.md`

### Details

- Define schema for `system3_job_scheduler.json`:

```json
{
  "jobs": [
    {
      "id": "daily_status",
      "name": "Daily Status Check",
      "module": "core.engine.check_system3_status",
      "enabled": true,
      "type": "daily"
    }
  ]
}
```

- Scheduler behavior:
  - `--list`: print all jobs + status.
  - `--run-once`: run all `enabled==true` jobs sequentially.
  - Optional `--job-id` to run a single job.
- Record in state JSON:
  - `last_run_time`
  - `last_status`
  - `last_error` (if any).

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase82_job_scheduler --list
(venv) C:\Genesis_System3> python -m core.engine.system3_phase82_job_scheduler --run-once
```

Expected logs:

- `[PH82] Loaded K jobs from config/system3_job_scheduler.json`
- `[PH82] Job <id> completed with status=SUCCESS`

Expected MD:
- Table: `id | name | enabled | last_status | last_run_time`.

---

## Phase 83 – Tick-to-Trade Latency Monitor

### Goal
Measure total real-time latency from **market snapshot time** to **trade decision timestamp**.

### Files

1. `core/engine/system3_phase83_tick_to_trade_latency.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase83_tick_to_trade_latency.json`
   - `storage/ultra/ph76_ph100/phase83_tick_to_trade_latency.md`

### Details

- Inputs:
  - trade plan and/or PnL logs with both `snapshot_ts` and `decision_ts`.
- For each trade:
  - compute `latency_ms`.
- Aggregate:
  - overall mean, median, p95, p99 per underlying.
- MD:
  - table of metrics
  - commentary: classify latency as OK / HIGH vs a threshold (e.g. 500 ms).

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase83_tick_to_trade_latency
```

Expected logs:

- `[PH83] Processed T trades for latency analysis`
- `[PH83] Tick-to-trade latency summary saved`

---

## Phase 84 – Resource Optimizer

### Goal
Analyze CPU/memory usage logs (if available) and suggest **performance optimizations**.

### Files

1. `core/engine/system3_phase84_resource_optimizer.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase84_resource_usage.json`
   - `storage/ultra/ph76_ph100/phase84_resource_usage.md`

### Details

- Inputs:
  - If a dedicated resource log exists, use it.
  - Else, create one synthetic pass that:
    - measures CPU/mem per selected module run.
- Find:
  - top N heaviest modules by CPU/mem.
- MD:
  - table of heaviest modules
  - “Top 3 recommendations” for performance improvement.

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase84_resource_optimizer
```

Expected:

- `[PH84] Resource usage analysis completed`
- `[PH84] Suggestions written to phase84_resource_usage.md`

---

## Phase 85 – Heartbeat Engine

### Goal
Maintain a **heartbeat log**: System3 alive + status, for monitoring.

### Files

1. `core/engine/system3_phase85_heartbeat.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase85_heartbeat.log`

### Details

- CLI parameters:
  - `--iterations N`
  - `--interval-seconds S`
- Each loop:
  - append a line:

```text
[timestamp] status=ALIVE mode=<BASELINE/ULTRA> auto_exec=<TRUE/FALSE> safety=<SAFE/LOCKDOWN>
```

- Default: 5 iterations, 5 seconds if no params.

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase85_heartbeat --iterations 5 --interval-seconds 1
```

Expected:

- `[PH85] Heartbeat iteration i/5` log lines
- 5 entries in `phase85_heartbeat.log`.

---

# BLOCK C — PROFIT ENGINE (86–90)

## Phase 86 – Position Sizing Engine

### Goal
Define per-trade **position size** based on risk rules (max capital % per trade, volatility, underlying risk).

### Files

1. `core/engine/system3_phase86_position_sizing.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase86_position_sizing_rules.json`
   - `storage/ultra/ph76_ph100/phase86_position_sizing_examples.md`

### Details

- Inputs:
  - A config for risk:
    - max_risk_per_trade_pct (e.g. 0.5–1.0).
    - max_open_risk_pct.
- For test:
  - use synthetic portfolio capital (e.g. 1,00,000).
  - derive recommended quantity using option premium and risk per point.
- JSON:
  - base rules
  - several example scenarios per underlying.

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase86_position_sizing
```

Expected:

- `[PH86] Position sizing rules computed for N scenarios`

Expected MD:
- At least 3 example cases with capital, risk%, CE/PE, and recommended quantity.

---

## Phase 87 – Expected Value Calculator

### Goal
Compute **Expected Value (EV)** per signal/trade based on historical performance.

### Files

1. `core/engine/system3_phase87_expected_value.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase87_expected_value.parquet`
   - `storage/ultra/ph76_ph100/phase87_expected_value.md`

### Details

- Inputs:
  - PnL log with realized PnL.
- For each grouping (e.g. by underlying, direction, regime, time-of-day bucket):
  - calculate:
    - P(win)
    - P(loss)
    - avg_win
    - avg_loss
    - EV.
- Attach EV to relevant views.

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase87_expected_value
```

Expected logs:

- `[PH87] Expected value computed for N pattern buckets`

Expected MD:
- “Top 5 positive EV patterns”
- “Bottom 5 negative EV patterns.”

---

## Phase 88 – Portfolio Risk Engine

### Goal
Analyze exposures across underlyings and strikes to detect **portfolio-level risk**.

### Files

1. `core/engine/system3_phase88_portfolio_risk.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase88_portfolio_risk.json`
   - `storage/ultra/ph76_ph100/phase88_portfolio_risk.md`

### Details

- Inputs:
  - trade plans and/or PnL with notional sizes.
- Compute:
  - per-underlying notional exposure
  - CE vs PE net bias
  - maximum single-strike concentration.
- MD:
  - table with risk flags: HIGH / MEDIUM / LOW.

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase88_portfolio_risk
```

Expected:

- `[PH88] Portfolio risk analysis complete`

---

## Phase 89 – Optimal Entry Engine

### Goal
Assess quality of **entry timing** for trades.

### Files

1. `core/engine/system3_phase89_optimal_entry.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase89_optimal_entry.parquet`
   - `storage/ultra/ph76_ph100/phase89_optimal_entry.md`

### Details

- For each trade:
  - Look at price series before entry (e.g. few candles).
  - Determine:
    - was there a better entry within a small window.
- Label:

```text
entry_quality = GOOD / EARLY / LATE
```

- MD:
  - counts per class
  - 2–3 detailed examples.

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase89_optimal_entry
```

Expected:

- `[PH89] Entry quality evaluated for M trades`

---

## Phase 90 – Optimal Exit Engine

### Goal
Assess quality of **exit logic** for trades.

### Files

1. `core/engine/system3_phase90_optimal_exit.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase90_optimal_exit.parquet`
   - `storage/ultra/ph76_ph100/phase90_optimal_exit.md`

### Details

- For each trade:
  - analyze price after entry until exit or timeout.
  - compute:
    - best-case PnL
    - worst-case PnL
    - actual PnL.
- Label:

```text
exit_quality = GOOD / TOO_SOON / TOO_LATE
improvable_pnl_pct = (best_case - actual) / best_case
```

- MD:
  - distribution of exit_quality
  - avg improvable_pnl_pct for improvable trades.

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase90_optimal_exit
```

Expected:

- `[PH90] Exit quality evaluated for M trades`

---

# BLOCK D — HUMAN CONTROL, DASHBOARDS, REPLAY (91–95)

## Phase 91 – Live Control Dashboard (MD)

### Goal
Provide a text/MD **live dashboard** snapshot of System3.

### Files

1. `core/engine/system3_phase91_live_dashboard.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase91_live_dashboard.md`

### Details

Sections:

1. System Status
   - mode (BASELINE/ULTRA)
   - profile
   - auto_exec (ON/OFF)
   - safety_status (SAFE/LOCKDOWN)
2. Today Stats
   - signals count
   - trades count
   - realized PnL
3. Risk
   - largest underlying exposure
   - any HIGH risk flags from Phase 88
4. GENI Recommendations
   - top 3 actions from Phase 80.

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase91_live_dashboard
```

Expected:

- `[PH91] Live dashboard snapshot written`

---

## Phase 92 – Session Replay Player

### Goal
Reconstruct a day’s events as a chronological **replay log**.

### Files

1. `core/engine/system3_phase92_session_replay.py`
2. Directory:
   - `storage/ultra/ph76_ph100/session_replay/`
3. Output:
   - `storage/ultra/ph76_ph100/session_replay/phase92_replay_log_YYYYMMDD.md`

### Details

- Inputs:
  - filter signals, trade plans, executions, PnL by date.
- Sort by timestamp; emit:

```text
[timestamp] TYPE=SIGNAL ...
[timestamp] TYPE=TRADE_PLAN ...
[timestamp] TYPE=EXECUTION ...
[timestamp] TYPE=PNL ...
```

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase92_session_replay --date YYYY-MM-DD
```

Expected:

- `[PH92] Reconstructed session for date=YYYY-MM-DD`

---

## Phase 93 – Operator Override Engine

### Goal
Allow operator to define **override rules** and log what they would block.

### Files

1. `core/engine/system3_phase93_operator_override.py`
2. Config:
   - `config/system3_operator_override.json`
3. Output:
   - `storage/ultra/ph76_ph100/phase93_override_state.json`
   - `storage/ultra/ph76_ph100/phase93_override_log.md`

### Details

- Example config:

```json
{
  "blocked_underlyings": ["SENSEX"],
  "force_hold_all": false,
  "max_trades_per_day": 5
}
```

- This phase:
  - reads today’s signals/trades
  - determines which would be blocked
  - logs summary; does **not** enforce in live engine.

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase93_operator_override
```

Expected:

- `[PH93] Evaluated operator overrides on N candidates`

---

## Phase 94 – Notification Engine

### Goal
Central notification router, writing events to a log only (no external sends yet).

### Files

1. `core/engine/system3_phase94_notification_engine.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase94_notifications.log`
   - `storage/ultra/ph76_ph100/phase94_notifications.md`

### Details

- Implement:

```python
def notify(event_type: str, payload: dict) -> None:
    ...
```

- CLI `--self-test`:
  - send a few sample notifications (BIG_LOSS, HIGH_CONF_SIGNAL, RISK_LIMIT_NEAR).
- MD:
  - counts per event_type.

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase94_notification_engine --self-test
```

Expected:

- `[PH94] Sent test notifications (K events)`

---

## Phase 95 – Operator Activity Log

### Goal
Track **operator actions** in a structured log.

### Files

1. `core/engine/system3_phase95_operator_activity_log.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase95_operator_actions.log`
   - `storage/ultra/ph76_ph100/phase95_operator_actions.md`

### Details

- Provide:

```python
def log_operator_action(action: str, details: dict) -> None:
    ...
```

- CLI `--self-test`:
  - log a few sample actions (e.g. ran_dashboard, ran_full_validation).
- MD:
  - aggregated counts by action.

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase95_operator_activity_log --self-test
```

Expected:

- `[PH95] Logged sample operator actions`

---

# BLOCK E — HARDENING & FINAL CERTIFICATION (96–100)

## Phase 96 – Chaos Test Engine

### Goal
Simulate failures to ensure System3 **fails safe** (no trades, no corruption).

### Files

1. `core/engine/system3_phase96_chaos_test.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase96_chaos_test_summary.json`
   - `storage/ultra/ph76_ph100/phase96_chaos_test_report.md`

### Details

- Chaos scenarios:
  - missing config
  - corrupted CSV header
  - empty signals
- For each:
  - run selected modules in protected mode.
  - confirm:
    - no unhandled exceptions
    - system logs explicit “FAIL-SAFE” outcome.
- MD:
  - list scenario | module | result | safe (YES/NO).

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase96_chaos_test
```

Expected logs:

- `[PH96] Chaos scenario <name>: PASS/FAIL-SAFE`

---

## Phase 97 – Backup & Recovery Engine

### Goal
Create snapshots of **key state files** for backup.

### Files

1. `core/engine/system3_phase97_backup_recovery.py`
2. Directory:
   - `storage/ultra/ph76_ph100/recovery_points/`
3. Output:
   - `storage/ultra/ph76_ph100/phase97_backup_manifest.json`

### Details

- Define list of essential files:
  - key configs
  - thresholds JSON
  - model metadata.
- On `--create-backup`:
  - create timestamped folder
  - copy files
  - update manifest with list of files.

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase97_backup_recovery --create-backup
```

Expected:

- `[PH97] Created backup recovery_points/<timestamp>`

---

## Phase 98 – Rollback Mechanism

### Goal
Read backup manifest and print **rollback plan** (dry-run only).

### Files

1. `core/engine/system3_phase98_rollback.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase98_rollback_plan.md`

### Details

- CLI:
  - `--backup latest` or `--backup <id>`
- Reads manifest, prints:
  - which files would be restored
  - target paths
  - manual commands (e.g. copy).

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase98_rollback --backup latest
```

Expected:

- `[PH98] Generated rollback plan for backup=<id>`

---

## Phase 99 – Version Freeze & Tagging

### Goal
Create a **version manifest** marking current System3 code & config as a named release.

### Files

1. `core/engine/system3_phase99_version_freeze.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase99_version_manifest.json`
   - `storage/ultra/ph76_ph100/phase99_version_manifest.md`

### Details

- Gather:
  - timestamp
  - optional git commit hash (if accessible)
  - module counts, menu options.
- Default release name: `"SYSTEM3_ULTRA_V1"`.

JSON:

```json
{
  "release_name": "SYSTEM3_ULTRA_V1",
  "timestamp": "...",
  "modules_count": 80,
  "menu_options": 100,
  "notes": "Phases 1–100 implemented and validated."
}
```

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase99_version_freeze
```

Expected:

- `[PH99] Version manifest created for SYSTEM3_ULTRA_V1`

---

## Phase 100 – Final Certification Engine

### Goal
Run a **final checklist** and produce a certification file:

> `SYSTEM3_CERTIFIED = TRUE` (if all checks pass).

### Files

1. `core/engine/system3_phase100_final_certification.py`
2. Output:
   - `storage/ultra/ph76_ph100/phase100_final_certification.json`
   - `storage/ultra/ph76_ph100/phase100_final_certification.md`

### Details

- Checks:
  - required folders exist (`core/`, `config/`, `storage/live/`, `storage/ultra/`, `storage/ultra/ph76_ph100/`)
  - key configs present
  - validation MDs for earlier phase groups exist.
- If all good:
  - `certified = true`
  - link to release name from Phase 99.
- MD: formal certificate stating certification, date, and scope.

### Validation

```bash
(venv) C:\Genesis_System3> python -m core.engine.system3_phase100_final_certification
```

Expected logs:

- `[PH100] All required checks passed. SYSTEM3_CERTIFIED = TRUE`

---

## What I want from Cursor Agent

1. Implement all modules as described above.
2. For each phase:
   - ensure module path, outputs, and validation command exactly match this MD.
3. After implementation:
   - Run **one combined test script** (agent can create e.g. `test_phases_76_100.py`) or run each `python -m core.engine.system3_phaseXX_...` and capture logs.
4. Provide you (and me) with:
   - Confirmation that:
     - all 25 phases (76–100) ran without unhandled errors
     - each expected output file exists
     - any phases that depend on real trades behave gracefully if data is small.

This MD is the single source-of-truth spec for Phases 76–100.
