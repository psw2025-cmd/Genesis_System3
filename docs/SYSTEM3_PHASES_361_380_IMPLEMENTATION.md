# SYSTEM3 PHASES 361–380 — IMPLEMENTATION BRIEF (PRODUCTION GRADE)

Status:
- Existing phases 1–360: VERIFIED healthy (foundation, mid-core, hardened layers).
- Safety: DRY-RUN ONLY (LIVE_TRADING_ENABLED = False, USE_LIVE_EXECUTION_ENGINE = False, AUTO_EXECUTE_TRADES = False).

Goal for phases 361–380:
- Add **live model-health, signal-quality, and data-quality intelligence**.
- Automatically **measure**, not blindly trust, System3’s predictions.
- Provide **cleaned, validated signal data** for future real trading.
- Keep everything **safe, DRY-RUN**, and fully auditable.

Constraints:
- DO NOT modify existing phases 1–360 unless absolutely necessary.
- DO NOT enable live trading.
- All new phases must:
  - have clear logging,
  - write outputs into `storage/live/`, `storage/metrics/`, or `reports/`,
  - be callable from the autorun phase runner.

Naming conventions:
- Files: `system3_phase{N}_*.py`
- Main entry in each file: `run_phase{N}(context)` (or match existing convention if different).
- Each phase must be idempotent and safe to re-run many times.

---

## PHASE 361 — SIGNAL PIPELINE SNAPSHOT & QUALITY SUMMARY

**Objective:**  
Create a single, consolidated snapshot of the current **signal pipeline state** (index options) and write a human-readable report and machine-readable JSON.

**Inputs:**
- `storage/live/dhan_index_ai_signals.csv`
- `storage/live/dhan_index_ai_signals_curated.csv`
- `storage/live/dhan_index_ai_signals_with_forward.csv`
- Optional: `storage/live/dhan_virtual_orders.csv` (if present)

**Outputs:**
- `storage/metrics/signal_pipeline_snapshot_361.json`
- `reports/SIGNAL_PIPELINE_SNAPSHOT_361.md`

**Core actions:**
- Load all four CSVs if present. If any is missing, log a WARN and continue with available files.
- Compute:
  - row counts per file,
  - distinct symbol/expiry/strike counts,
  - counts per signal type (BUY/SELL/HOLD/FLAT/etc.),
  - percentage of missing values per file and column.
- Write to JSON a structured object with metrics.
- Write MD report summarizing:
  - which files are present,
  - basic distribution of signals,
  - any obvious issues (e.g., 0 rows, all HOLD, excessive NaN).
- No mutation of source CSVs.

**Why it helps:**
- Gives an immediate picture of “what System3 is seeing” before any decision/learning.

**When to run:**  
- PRE-MARKET and HOURLY (safe to run often).  
- Parallel: YES (read-only).

---

## PHASE 362 — LIVE FORWARD-RETURN CALIBRATOR

**Objective:**  
Measure the **real-world predictive strength** of signals using the `*_with_forward.csv` file and produce calibration metrics for thresholds.

**Inputs:**
- `storage/live/dhan_index_ai_signals_with_forward.csv`
  - Must contain at least: symbol, expiry, strike, signal, forward_return_Xmin/hour (name as currently in your file).

**Outputs:**
- `storage/metrics/forward_calibration_362.json`
- `reports/FORWARD_RETURN_CALIBRATION_362.md`

**Core actions:**
- Load CSV; if missing/empty:
  - log WARN, write minimal report, exit gracefully.
- Group by signal type (BUY/SELL/HOLD/etc.).
- For each signal type:
  - compute average forward return (for each horizon available),
  - median, standard deviation,
  - win-rate (% of forward return > 0, per horizon),
  - max drawdown approximation (min forward return).
- Compute **global calibration score**:
  - e.g. weighted average of win-rates and mean returns.
- Write JSON + MD summary:
  - explicit numbers,
  - call out if any signal type has negative expectation.

**Why it helps:**
- This is the first live “is our model actually right?” measurement.

**When to run:**  
- HOURLY and EOD.  
- Parallel: YES (read-only).

---

## PHASE 363 — MODEL DRIFT & FEATURE DISTRIBUTION CHECKER

**Objective:**  
Detect if the live data distribution has drifted far from the training baseline.

**Inputs:**
- Training baseline stats (if present): e.g. `storage/models/feature_baseline_stats.json`
- Live signals / features:
  - `storage/live/dhan_index_ai_signals_curated.csv`
  - Or any live feature CSV used by the model (agent must inspect existing model pipeline to choose correct file).

**Outputs:**
- `storage/metrics/model_drift_363.json`
- `reports/MODEL_DRIFT_REPORT_363.md`

**Core actions:**
- If baseline stats missing:
  - log WARN, create “baseline missing” report, exit safely.
- Identify key numeric feature columns (same as trained model).
- For each key feature:
  - compute live mean, std, min, max.
  - compare with baseline mean/std.
  - calculate a drift score (e.g., normalized absolute difference or simple z-score).
- Produce:
  - per-feature drift scores,
  - overall drift index (e.g., mean or max across features).
- Write MD report with:
  - sorted list of most drifted features,
  - simple “LOW / MEDIUM / HIGH drift” classification.

**Why it helps:**
- Early warning if model is now misaligned with market regime.

**When to run:**  
- HOURLY and EOD.  
- Parallel: YES (read-only).

---

## PHASE 364 — MODEL HEALTH & CONFIDENCE DASHBOARD FEED

**Objective:**  
Aggregate information from phases 361–363 into a single JSON/MD that can be shown in a dashboard panel and heartbeat.

**Inputs:**
- `storage/metrics/signal_pipeline_snapshot_361.json`
- `storage/metrics/forward_calibration_362.json`
- `storage/metrics/model_drift_363.json`

**Outputs:**
- `storage/metrics/model_health_summary_364.json`
- `reports/MODEL_HEALTH_SUMMARY_364.md`
- Optional: update `system3_daily_heartbeat.json` with high-level fields:
  - `model_health_score`
  - `signal_calibration_score`
  - `drift_status`

**Core actions:**
- Load metrics from 361–363; if any missing, mark that section as “unknown” but do not fail.
- Combine into:
  - single overall health score (0–100),
  - color-coded status (“GREEN/YELLOW/RED”).
- Write JSON + MD.

**Why it helps:**
- Gives a human + machine friendly single place to see model status.

**When to run:**  
- After 361–363 in any schedule where they’re included (e.g. HOURLY).  
- Parallel: YES.

---

## PHASE 365 — LIVE SIGNAL ACCURACY TRACKER

**Objective:**  
Compute **rolling live accuracy metrics** over recent N bars/hours/days using forward returns.

**Inputs:**
- `storage/live/dhan_index_ai_signals_with_forward.csv`

**Outputs:**
- `storage/metrics/live_accuracy_tracker_365.json`
- `reports/LIVE_ACCURACY_TRACKER_365.md`

**Core actions:**
- Define a rolling window (e.g. last 1 day or last X records, configurable).
- For each signal type and horizon:
  - calculate win-rate, average profit, average loss, profit factor.
- Compute an “effective accuracy” metric:
  - for BUY/SELL only, ignoring HOLD.
- Track this over time by appending to a simple time-series JSON or CSV:
  - `storage/metrics/live_accuracy_history_365.csv`.

**Why it helps:**
- Converts the system performance into a time-series that can be monitored and used for gating.

**When to run:**  
- HOURLY, EOD.  
- Parallel: YES.

---

## PHASE 366 — STRATEGY ENSEMBLE EVALUATOR (THRESHOLD SWEEP)

**Objective:**  
Evaluate different internal “threshold” configurations (e.g. probability cutoffs, risk multipliers) using current forward-return data, **without changing live behavior yet**.

**Inputs:**
- `storage/live/dhan_index_ai_signals_with_forward.csv`
- Configuration: either:
  - `config/system3_strategy_thresholds.json`
  - or a new config file created by this phase.

**Outputs:**
- `storage/metrics/strategy_ensemble_evaluation_366.json`
- `reports/STRATEGY_ENSEMBLE_EVALUATION_366.md`

**Core actions:**
- Define a small grid of strategies (3–5 variants) based on thresholds present in your config:
  - e.g. base / conservative / aggressive.
- For each variant:
  - simulate applying that threshold to signals (paper).
  - compute expected PnL, win-rate, max drawdown approximation using forward returns.
- Rank strategies.
- Do NOT change live config here; just report.

**Why it helps:**
- Gives data-driven guidance on which configuration is currently best, but keeps system safe.

**When to run:**  
- EOD (once per day is enough).  
- Parallel: YES.

---

## PHASE 367 — SAFETY GUARDRAIL RECOMMENDER (READ-ONLY)

**Objective:**  
Based on metrics from 362, 363, 365, 366, compute **recommended safety mode**, but DO NOT auto-apply.

**Inputs:**
- `storage/metrics/forward_calibration_362.json`
- `storage/metrics/model_drift_363.json`
- `storage/metrics/live_accuracy_tracker_365.json`
- `storage/metrics/strategy_ensemble_evaluation_366.json`

**Outputs:**
- `storage/metrics/safety_guardrail_recommendations_367.json`
- `reports/SAFETY_GUARDRAIL_RECOMMENDATIONS_367.md`

**Core actions:**
- Define simple decision rules, for example:
  - If live accuracy < 55% OR drift is HIGH ⇒ recommend `mode = "ULTRA_SAFE"`.
  - If drift is MEDIUM ⇒ recommend `mode = "SAFE"`.
  - If accuracy > 65% and drift LOW ⇒ recommend `mode = "NORMAL"`.
- Do not mutate `config` yet; only write recommendations.
- Summarize rationale in MD.

**Why it helps:**
- Prepares the logic to eventually change behavior in the future, but right now everything stays DRY-RUN and manual.

**When to run:**  
- EOD, or after other metrics phases.  
- Parallel: YES.

---

## PHASE 368 — BROKER LATENCY & STABILITY MONITOR (READ-ONLY)

**Objective:**  
Measure basic latency and stability of Dhan API responses during the day.

**Inputs:**
- Access to existing broker helper module used in phases 205 etc.
- No new external dependencies.

**Outputs:**
- `storage/metrics/broker_latency_368.json`
- `reports/BROKER_LATENCY_REPORT_368.md`

**Core actions:**
- Using the already-authenticated broker client (context), perform:
  - 2–3 lightweight API calls:
    - e.g. quote for a stable symbol (NIFTY index),
    - maybe market depth, if cheap.
- For each call:
  - measure round-trip time,
  - check HTTP status and payload correctness.
- Append results to a latency history file.

**Why it helps:**
- Quantifies connection quality; important before any real trading.

**When to run:**  
- Live market hours only (skip if market closed or broker not logged in).  
- Parallel: YES.

---

## PHASE 369 — PIPELINE PROFILER: END-TO-END TIMING

**Objective:**  
Measure timing of critical blocks (OP1, OP2, OP3, signals generation) to detect bottlenecks.

**Inputs:**
- Existing logs, or direct wrapping of functions if feasible.
- System context (root path for logs).

**Outputs:**
- `storage/metrics/pipeline_profile_369.json`
- `reports/PIPELINE_PROFILE_369.md`

**Core actions:**
- Choose one of:
  - Parse the existing autorun log to extract START/END timestamps of key operations; or
  - Add timing wrappers for major steps (only if simple and safe).
- Compute average durations of:
  - Phase 220–260 block,
  - entire OP Cycle,
  - signal generation pipeline.
- Identify top 3 slowest components.

**Why it helps:**
- Ensures we stay within ultra-low-latency goals.

**When to run:**  
- HOURLY or once mid-session + EOD.  
- Parallel: YES.

---

## PHASE 370 — SIGNAL SCHEMA AUTO-REPAIR (NON-DESTRUCTIVE)

**Objective:**  
Detect and repair **schema mismatches** in signals CSVs into a clean version, without touching the originals.

**Inputs:**
- `storage/live/dhan_index_ai_signals.csv`
- `storage/live/dhan_index_ai_signals_curated.csv`
- `storage/live/dhan_index_ai_signals_with_forward.csv`
- Knowledge of expected core columns (agent must infer from existing pipeline and Phase 339).

**Outputs:**
- `storage/live/dhan_index_ai_signals_clean_370.csv`
- `storage/live/dhan_index_ai_signals_with_forward_clean_370.csv`
- `reports/SIGNAL_SCHEMA_AUTOREPAIR_370.md`
- `storage/metrics/signal_schema_repair_370.json`

**Core actions:**
- Load each CSV, with robust error handling.
- For each file:
  - Detect rows where column count != header length → mark as corrupted rows.
  - Drop corrupted rows into a separate quarantine CSV:
    - `storage/live/quarantine/dhan_index_ai_signals_badrows_370.csv`
  - Ensure all required core columns exist; if missing:
    - log ERROR in report, but still keep file; do not invent columns.
- Write cleaned versions with rows filtered and minimal type normalization.
- Document:
  - how many rows kept, how many quarantined,
  - per-file status.

**Why it helps:**
- Works together with Phases 339–340 validation gates: instead of only detecting, we now **offer cleaned inputs** for the future.

**When to run:**  
- PRE-MARKET and EOD (and maybe once mid-day if cheap).  
- Parallel: YES.

---

## PHASE 371 — SIGNAL DEDUPLICATION ANALYZER

**Objective:**  
Analyse and prepare a plan to resolve **duplicate signals** (same symbol/expiry/strike/timestamp).

**Inputs:**
- `storage/live/dhan_index_ai_signals_clean_370.csv` (if present, else fallback to original).
- Columns that identify uniqueness:
  - broker-specific instrument token or (symbol, expiry, strike, option_type, timestamp).

**Outputs:**
- `storage/metrics/signal_dedup_analysis_371.json`
- `reports/SIGNAL_DEDUP_ANALYSIS_371.md`

**Core actions:**
- Group by uniqueness key; count duplicates > 1.
- Compute:
  - how many groups have more than one row,
  - ratio of duplicates vs. unique items,
  - any conflicting signals (e.g., BUY and SELL at same timestamp for same instrument).
- Do not change data here; only analyse and report.

**Why it helps:**
- Gives clarity to support Phase 372 (actual deduping).

**When to run:**  
- After Phase 370, EOD.  
- Parallel: YES.

---

## PHASE 372 — SIGNAL DEDUPLICATION CLEANER (NON-DESTRUCTIVE)

**Objective:**  
Produce a **deduplicated version** of signals using clear rules, without destroying the originals.

**Inputs:**
- `storage/live/dhan_index_ai_signals_clean_370.csv`
- `storage/metrics/signal_dedup_analysis_371.json` (if available)

**Outputs:**
- `storage/live/dhan_index_ai_signals_dedup_372.csv`
- `reports/SIGNAL_DEDUP_CLEANER_372.md`
- `storage/metrics/signal_dedup_cleaner_372.json`

**Core actions:**
- For each group of duplicates:
  - If all signals same → keep latest or earliest (configurable, but consistent).
  - If conflicting signals → keep the one with stronger score/priority (if a score field exists) or latest timestamp; log this choice.
- Output a deduplicated CSV.
- Log:
  - how many rows removed,
  - how many conflicts resolved,
  - final unique count.

**Why it helps:**
- Supplies a high-quality, usable signal file for future trade planning and learning.

**When to run:**  
- After Phase 371, EOD.  
- Parallel: YES.

---

## PHASE 373 — CLEAN SIGNAL PIPELINE SUMMARY

**Objective:**  
Summarize the entire cleaned pipeline: original → clean → dedup → with_forward.

**Inputs:**
- Original & derived CSVs:
  - `dhan_index_ai_signals.csv`
  - `dhan_index_ai_signals_clean_370.csv`
  - `dhan_index_ai_signals_dedup_372.csv`
  - `dhan_index_ai_signals_with_forward.csv`
  - `dhan_index_ai_signals_with_forward_clean_370.csv` (if created)
- Metrics from 370–372.

**Outputs:**
- `reports/CLEAN_SIGNAL_PIPELINE_SUMMARY_373.md`
- `storage/metrics/clean_signal_pipeline_summary_373.json`

**Core actions:**
- Tabulate row counts across pipeline stages.
- Compute and report:
  - % rows quarantined,
  - % rows deduplicated,
  - final row count usable for learning/trade planning.
- Cross-check that final pipeline still covers all major indices and expiries.

**Why it helps:**
- Gives a single “before vs after” view of data quality improvements.

**When to run:**  
- EOD.  
- Parallel: YES.

---

## PHASE 374 — MODEL INPUT QUALITY GATE (READ-ONLY)

**Objective:**  
Decide whether **current cleaned data is good enough** to be used for training or trade planning.

**Inputs:**
- `storage/metrics/clean_signal_pipeline_summary_373.json`
- `storage/metrics/model_drift_363.json`
- `storage/metrics/live_accuracy_tracker_365.json`

**Outputs:**
- `storage/metrics/model_input_quality_gate_374.json`
- `reports/MODEL_INPUT_QUALITY_GATE_374.md`

**Core actions:**
- Compute a quality score using:
  - data completeness, quarantine rate, dedup rate,
  - drift level,
  - recent live accuracy.
- Classify result into:
  - `"USE_FOR_TRAINING"`,
  - `"USE_FOR_PAPER_TRADE_ONLY"`,
  - `"DO_NOT_USE"`.
- No automatic config changes here; only recommendations.

**Why it helps:**
- Acts as a hard gate before any future auto-training or real trading.

**When to run:**  
- EOD.  
- Parallel: YES.

---

## PHASE 375 — EOD MODEL & DATA HEALTH SUMMARY

**Objective:**  
Produce a final, human-reviewable summary combining all 361–374 metrics for the day.

**Inputs:**
- All JSON metrics from 361–374.

**Outputs:**
- `reports/EOD_MODEL_AND_DATA_HEALTH_375.md`
- Optional: append reference in a summary index:
  - `reports/EOD_SUMMARY_INDEX.md`

**Core actions:**
- Compile:
  - signal pipeline health,
  - forward calibration,
  - drift,
  - live accuracy,
  - dedup & schema repair stats,
  - model input quality gate decision.
- Highlight:
  - whether day is good candidate for training,
  - whether system is in GREEN/YELLOW/RED status overall.

**Why it helps:**
- Gives you and any reviewer an at-a-glance EOD status.

**When to run:**  
- Once per day, after market close.  
- Parallel: YES.

---

## PHASES 376–380 — BLOCK SELF-TEST & SAFETY

Design these as a **self-contained regression and safety harness** for this block.

### PHASE 376 — METRICS CONSISTENCY CHECKER

- Verify JSON files from 361–375 exist and are syntactically valid.
- Check that important fields (health scores, counts) are present.
- Output:
  - `reports/PHASE_361_375_METRICS_CONSISTENCY_376.md`
  - `storage/metrics/phase_361_375_metrics_consistency_376.json`

### PHASE 377 — DRY-RUN SAFETY REVALIDATION

- Confirm again:
  - `LIVE_TRADING_ENABLED = False`
  - `USE_LIVE_EXECUTION_ENGINE = False`
  - `AUTO_EXECUTE_TRADES = False`
- Cross-check with `system3_daily_heartbeat.json`.
- Output:
  - `reports/PHASE_377_SAFETY_REVALIDATION.md`

### PHASE 378 — PHASE 361–380 BLOCK REGRESSION TESTER

- Import all new phase modules (361–380).
- Run them in a controlled “regression” mode:
  - using existing data files,
  - ensuring no uncaught exceptions,
  - measuring approximate runtime.
- Output:
  - `reports/PHASES_361_380_BLOCK_TEST_378.md`
  - `storage/metrics/phases_361_380_block_test_378.json`

### PHASE 379 — ERROR/WARN AGGREGATOR

- Scan logs and metrics for this block for:
  - any ERROR,
  - repeated WARNs.
- Summarize per phase:
  - OK / WARN / ERROR,
  - brief reason.
- Output:
  - `reports/PHASES_361_380_ERROR_WARN_AGGREGATE_379.md`

### PHASE 380 — IMPLEMENTATION COMPLETENESS & INDEX FILE

- Generate:
  - `IMPLEMENTATION_COMPLETE_PHASES_361_380.md`
  - `PHASES_361_380_IMPLEMENTATION_INDEX.md`
  - `PHASES_361_380_QUICK_REFERENCE.md`
- These should follow the same style as the existing 311–330 and 331–360 index+summary files.

**Why 376–380 help:**
- Make the block self-validating.
- Provide the same kind of “proof of implementation” and easy review as prior blocks.

---

## INTEGRATION NOTES

- Register phases 361–380 in the same registry used by autorun master (e.g. mapping phase_number → callable).
- Schedule:
  - 361–365, 368–369 for HOURLY / intraday.
  - 366–367, 370–375 for EOD.
  - 376–380 can be run on demand or post-deployment.

## VALIDATION CHECKLIST FOR AGENT

After implementation, the agent must:

1. Run a **phases 361–380 block test** (Phase 378).
2. Confirm no unhandled exceptions.
3. Verify all expected output files exist.
4. Confirm safety flags remain DRY-RUN.
5. Generate final summary:
   - `IMPLEMENTATION_COMPLETE_PHASES_361_380.md`
   - `PHASES_361_380_IMPLEMENTATION_INDEX.md`
