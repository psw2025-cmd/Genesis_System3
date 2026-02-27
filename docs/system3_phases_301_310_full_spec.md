# System3 Phases 301–310 – Hybrid Block (Prediction + Data + Real-Time)
 
This document defines implementation-ready specifications for **System3 Phases 301–310**.  
All phases must:
 
- Be **DRY-RUN safe** (no live orders).  
- Integrate with existing **1–300** phases without modifying them.  
- Use existing paths: `storage/`, `logs/`, `docs/`, `config/`, `core/`.  
- Use **robust CSV loaders** (same style as 201–230: on_bad_lines="skip", min-rows checks).  
- NEVER break existing files; only append new columns / create new reports.
 
These phases build on earlier ones, especially:
 
- 201–230 (FS health, training, edge, threshold, drift, etc.)  
- 221 – Forward Return Calculator  
- 222 – Signal Edge Estimator  
- 223 – Threshold Optimizer  
- 220 – Correlation Map, 217 – Volatility Regimes, 212 – Label Quality, etc.
 
---
 
## PHASE 301 – Daily Live-vs-Forward Performance Tracker
 
**Goal:** Convert recent signals + forward returns into **real, money-like metrics** per underlying and signal type.
 
**Inputs:**
 
- `storage/live/angel_index_ai_signals_with_forward.csv`  
  - Produced by Phase 221.  
  - Contains at least:
    - `ts`, `underlying`, `strike`, `side` (CE/PE), `pred_label` (BUY/SELL/HOLD)  
    - `final_score`  
    - Forward return columns such as `fwd_ret_1`, `fwd_ret_3`, `fwd_ret_5` (or similar).
 
**Logic:**
 
1. Load the file with robust loader; if < 200 rows → phase = WARN, exit gracefully.
2. Filter to **recent window** (e.g., last trading day, or last N hours based on config).
3. For each combination:
   - `underlying` × `pred_label` (BUY/SELL only):
   - Compute:
     - count of signals  
     - mean forward return for each horizon  
     - median forward return  
     - hit rate (>0 forward return) per horizon  
     - worst and best forward return per horizon.
4. Aggregate also **global totals** across all underlyings for BUY and SELL separately.
5. Compute a simple **grade** per underlying (GOOD / NEUTRAL / POOR) based on EV and hit rate.
6. Produce a structured Python dict to return (for internal pipeline) with all these metrics.
 
**Outputs:**
 
- `logs/research/system3_daily_live_vs_forward_report.md`
  - Table per underlying & label:
    - `underlying`, `label`, `count`, `hit_rate_fwd1`, `hit_rate_fwd3`, `mean_fwd1`, `mean_fwd3`, `grade`.
- `storage/meta/system3_daily_performance_301.json`
  - JSON with full metrics structure, dates, and computation timestamp.
- Phase result: status OK/WARN depending on data sufficiency.
 
---
 
## PHASE 302 – Regime-Aware Performance Profiler
 
**Goal:** Combine **volatility regime** info with Phase 301 metrics to see where the system performs best.
 
**Inputs:**
 
- `storage/meta/system3_vol_regimes.csv` (from Phase 217)  
  - Contains: `date`, `underlying`, `vol_regime` in {LOW, NORMAL, HIGH}.
- `storage/meta/system3_daily_performance_301.json` (from Phase 301).
 
**Logic:**
 
1. Identify the **current/last trading date** and join Phase 301 metrics with the corresponding `vol_regime` per underlying.
2. For each underlying:
   - Take the latest regime (LOW/NORMAL/HIGH).
   - Attach performance metrics (mean EV, hit rate, grade).
3. For each regime category, compute aggregate stats:
   - Average hit rate for BUY/SELL signals over all underlyings in that regime.
   - Average EV for BUY/SELL.
4. Assign labels:
   - **REGIME_STRENGTH** = STRONG / MIXED / WEAK per regime based on EV + hit rate.
5. Return a summary object for internal consumption.
 
**Outputs:**
 
- `logs/research/system3_regime_performance_302.md`
  - Tables:
    - per underlying: regime + key metrics
    - per regime: aggregated metrics and REGIME_STRENGTH.
- `storage/meta/system3_regime_performance_302.json`
  - JSON with regime-level and underlying-level metrics.
- Phase status: WARN only if regimes file missing or no matching date.
 
---
 
## PHASE 303 – Intraday Edge Decay Analyzer
 
**Goal:** Understand how fast signal edge decays after it is generated (important for latency & holding period decisions).
 
**Inputs:**
 
- `storage/live/angel_index_ai_signals_with_forward.csv`
- Configuration (can be from an existing global config or local default):
  - List of forward horizons (e.g., 1, 3, 5 snapshots).
 
**Logic:**
 
1. Load recent signals (last trading day). Only BUY and SELL.
2. For each horizon `h`:
   - Compute mean and median forward return for BUY and SELL separately.
   - Compute **decay curve**: EV(h) as h increases.
3. Fit a very simple **decay descriptor**:
   - e.g., classify edge as:
     - “VERY_SHORT” (best EV at smallest horizon, then drops)
     - “MEDIUM” (EV stable for several horizons)
     - “LONG” (EV grows with horizon).
4. For each underlying, determine its **edge profile**: VERY_SHORT / MEDIUM / LONG.
5. Produce a recommended **holding horizon** per underlying and signal direction.
 
**Outputs:**
 
- `logs/research/system3_edge_decay_303.md`
  - Plot-like table: EV at each horizon, classification per underlying.
- `storage/meta/system3_edge_decay_profile_303.json`
  - Contains per underlying:
    - edge_profile, best_horizon, EV_by_horizon, timestamp.
 
---
 
## PHASE 304 – Dynamic Threshold Tuner (Safe Mode)
 
**Goal:** Propose **updated BUY/SELL thresholds** using Phase 222 + Phases 301–303, but DO NOT change live thresholds automatically.
 
**Inputs:**
 
- `storage/meta/system3_threshold_candidates.json` (from Phase 223).
- `storage/meta/system3_daily_performance_301.json` (Phase 301).
- `storage/meta/system3_regime_performance_302.json` (Phase 302, optional).
- `storage/meta/system3_edge_decay_profile_303.json` (Phase 303).
 
**Logic:**
 
1. Load candidate thresholds (e.g., several (buy, sell) pairs with stats).
2. For each candidate:
   - Estimate risk/benefit using:
     - EV (from Phase 222/301),
     - hit rate,
     - distribution across regimes,
     - edge decay behavior (short/medium/long).
3. Apply **safety rules**:
   - Never propose thresholds that would produce:
     - extremely high trade count AND poor EV,
     - extreme asymmetry (e.g., buy >> sell).
4. Select a **small set of recommended thresholds**:
   - e.g., 3 candidates labelled:
     - CONSERVATIVE,
     - BALANCED,
     - AGGRESSIVE.
5. DO NOT write into the live config.
   - Only write a “proposal” JSON + markdown with clear explanation.
 
**Outputs:**
 
- `storage/meta/system3_threshold_proposals_304.json`
  - Structure: list of candidates with:
    - `mode` (CONSERVATIVE/BALANCED/AGGRESSIVE),
    - `buy_threshold`, `sell_threshold`,
    - expected trade count, expected EV, expected hit rate.
- `logs/research/system3_threshold_tuner_304.md`
  - Human-readable description of each candidate and safety reasoning.
- Phase result: always DRY-RUN (no config change).
 
---
 
## PHASE 305 – Confidence Tier Tagger (High/Medium/Low)
 
**Goal:** Tag each past signal with a **confidence tier** based on score, edge, and context.
 
**Inputs:**
 
- Latest reconciled signals:
  - `storage/live/angel_index_ai_signals_reconciled.csv`  
    (or fall back to `angel_index_ai_signals_with_forward.csv` if reconciled file missing).
- Supporting metadata:
  - `storage/meta/system3_edge_decay_profile_303.json`
  - `storage/meta/system3_regime_performance_302.json`
 
**Logic:**
 
1. Load reconciled signals (robust loader).
2. For each row, compute a **confidence score** using:
   - absolute `final_score`,
   - regime strength for that underlying (from 302),
   - edge profile (short/medium/long, from 303),
   - availability of forward return evidence (from 301/221).
3. Convert numeric confidence score into discrete tier:
   - HIGH / MEDIUM / LOW, with transparent thresholds (documented).
4. Add a new column:
   - `confidence_tier` in {HIGH, MEDIUM, LOW}.
5. Write a new enriched file (DON’T overwrite original in place):
   - e.g., `storage/live/angel_index_ai_signals_confidence_tagged_305.csv`.
 
**Outputs:**
 
- `storage/live/angel_index_ai_signals_confidence_tagged_305.csv`  
  - Same columns as input + `confidence_tier`.
- `logs/ml/system3_confidence_tiering_305.md`
  - Summary:
    - distribution of tiers,
    - examples of HIGH and LOW rows,
    - per-underlying confidence mix.
 
---
 
## PHASE 306 – Real-Time Staleness & Latency Guard
 
**Goal:** Detect and mark **stale** or **delayed** snapshots; protect against using old data as if it were live.
 
**Inputs:**
 
- Latest live signals / snapshots:
  - `storage/live/angel_index_ai_signals.csv`
- System time (now) when phase is executed.
- Optional:
  - `logs/performance/system3_latency_profile.md` (Phase 227).
 
**Logic:**
 
1. Load recent portion of `angel_index_ai_signals.csv` (last N snapshots).
2. For each row:
   - Compute time delta: `now - ts`.
3. Decide staleness thresholds:
   - e.g., > 90 seconds = STALE, > 5 minutes = EXPIRED.
4. For each underlying:
   - Compute latest timestamp and latency.
5. Generate:
   - A **per-underlying staleness classification** (FRESH/STALE/EXPIRED).
6. Write a CSV flags file:
   - With columns: `underlying`, `last_ts`, `latency_seconds`, `staleness_state`.
7. This phase does not change signals; it only produces metadata flags.
 
**Outputs:**
 
- `storage/meta/system3_staleness_flags_306.csv`
- `logs/performance/system3_staleness_guard_306.md`
  - Per-underlying staleness summary and any extreme latency.
 
---
 
## PHASE 307 – Live vs Backtest Consistency Checker
 
**Goal:** Ensure that **live DRY-RUN behavior** matches what backtest/test-mode would do under the same thresholds.
 
**Inputs:**
 
- Live signals:
  - `storage/live/angel_index_ai_signals.csv`
- Test-mode output (can be regenerated on demand or cached):
  - `logs/signals/system3_signal_test_mode_last_run.md`  
    (or equivalent summary file).
- Thresholds currently in use (from config or meta JSON).
 
**Logic:**
 
1. Identify a common time window (e.g., last X snapshots) for comparison.
2. For that window:
   - Recompute (or read from test-mode) predicted BUY/SELL/HOLD for each row.
   - Compare with what live DRY-RUN stored in `angel_index_ai_signals.csv` as `pred_label`.
3. Compute:
   - Match rate = % of rows where live label == test-mode label.
   - Any systematic bias (e.g., live always HOLD while test-mode sees BUY/SELL).
4. If mismatch rate > threshold (e.g., > 10%):
   - Log WARN with examples (show 5–10 mismatched rows).
5. Produce structured JSON with summary metrics.
 
**Outputs:**
 
- `logs/validation/system3_live_vs_test_consistency_307.md`
  - Contains match rate, mismatch examples, and conclusion.
- `storage/meta/system3_live_vs_test_consistency_307.json`
  - Contains numeric metrics and detection flags.
- Phase status:
  - OK if match rate acceptable,
  - WARN if high mismatch, ERROR only on structural failure.
 
---
 
## PHASE 308 – Daily PnL & Accuracy Dashboard Generator (Research View)
 
**Goal:** Produce a **single daily dashboard** summarizing PnL-like metrics, accuracy, and confidence tiers.
 
**Inputs:**
 
- `storage/live/angel_index_ai_signals_with_forward.csv`
- `storage/live/angel_index_ai_signals_confidence_tagged_305.csv`
- `storage/meta/system3_daily_performance_301.json`
- `storage/meta/system3_regime_performance_302.json`
- `storage/meta/system3_live_vs_test_consistency_307.json`
 
**Logic:**
 
1. For the last trading day:
   - Compute:
     - overall hit rate (BUY, SELL),
     - EV by underlying and signal type,
     - EV by confidence tier (HIGH/MEDIUM/LOW),
     - consistency score (from Phase 307),
     - regime performance summary.
2. Aggregate all metrics into a single dashboard view.
3. Include visual indicators (✅/⚠️/❌) for key metrics.

**Outputs:**

- `logs/research/system3_daily_dashboard_308.md`
  - Comprehensive daily dashboard with all metrics, charts (text-based), and recommendations.
- `storage/meta/system3_daily_dashboard_308.json`
  - JSON with all dashboard metrics for programmatic access.

---

## PHASE 309 – Schedule Hints Generator

**Goal:** Analyze phase execution patterns and suggest optimal scheduling for phases 301–310.

**Inputs:**

- Phase execution logs (if available):
  - `logs/system3_autophase_engine.log`
- Phase dependencies (from registry or spec files).

**Logic:**

1. Analyze which phases depend on others (e.g., 302 needs 301, 304 needs 301–303).
2. Estimate execution time per phase (if logs available).
3. Suggest optimal execution order and timing:
   - Post-market vs intraday,
   - Batch vs sequential,
   - Priority levels.
4. Generate scheduling recommendations.

**Outputs:**

- `logs/performance/system3_schedule_hint_report_309.md`
  - Recommended schedule for phases 301–310.
- `storage/meta/system3_schedule_hints_309.json`
  - JSON with scheduling recommendations.

---

## PHASE 310 – Ultra Health Monitor

**Goal:** Overall health check for phases 301–310 and their integration with the system.

**Inputs:**

- All outputs from phases 301–309.
- Phase registry status.

**Logic:**

1. Check that all phases 301–310 are implemented and registered.
2. Verify all expected output files exist.
3. Check data freshness (when were outputs last updated).
4. Compute overall health score (0–100).
5. Identify any critical issues or missing dependencies.

**Outputs:**

- `logs/system3_ultra_health_310.md`
  - Health report for phases 301–310.
- `storage/meta/system3_ultra_health_310.json`
  - JSON with health metrics and status.
 