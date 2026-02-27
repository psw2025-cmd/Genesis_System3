SYSTEM3 – PHASES 331–360 IMPLEMENTATION SPEC

Block Type: Hybrid (Accuracy + Hardening + Safety + Automation)
Mode requirement: DRY-RUN ONLY (no real orders)

0. Global Rules for All New Phases (331–360)

Read-only + virtual-only for trading decisions

No phase may place real orders.

All “trade” actions must go through the existing virtual / paper-trade layer (virtual orders CSV / logs).

No new random file structure

All new code must live under existing structure (inspect project tree first).

Prefer:

phases/phase_33x_*.py

modules/accuracy/, modules/hardening/, modules/safety/, modules/automation/ if such folders already exist.

If a folder doesn’t exist, create it minimally and document.

All new config must be in existing config pattern

Use config/ directory and not hard-coded paths inside logic.

Example: if config/system3_config.json or .yaml exists, extend it instead of new scattered config files.

Logging

All phases must log via existing system3_logger (or the shared logging utility).

Prefix logs with [PH331], [PH332], etc. to allow grep.

Testing requirement

Each phase must have:

A unit-style test or a functional test helper (e.g. tests/test_phase_331.py or tools/run_phase_331_test.py).

A block test command for 331–360 combined (see Section 5).

All tests must run in DRY-RUN using recorded or local data only.

Phase registry

All phases 331–360 must be registered in the central phases registry (whatever is used for 201–310).

Example pattern (Copilot must confirm actual file):

config/system3_phases_registry.json

or system3_autorun_phases.py / system3_phase_registry.py

Each phase entry:

phase_number

module path

function name

mode: pre-market / live / post-market

category: accuracy / hardening / safety / automation

Phases are divided as:

331–342: Accuracy & Model Intelligence

343–350: Pipeline Hardening & WARN Killer

351–356: Safety & Audit Visibility (still DRY-RUN)

357–360: Automation / Self-healing helpers

1. Phases 331–342 — Accuracy & Model Intelligence
Phase 331 – Meta Signal Quality Scanner

Objective
Quantitatively score each live signal row for quality (data completeness, recency, volatility context) and write a signal_quality_score column.

Where / Files

Input: storage/live/angel_index_ai_signals_with_forward.csv

Output: same file (with new column, safe overwrite using temp file pattern).

New module: phases/phase_331_meta_signal_quality.py

Registry: add phase 331 entry.

Inputs

Live signals + forward returns CSV.

Config thresholds from config/system3_thresholds.json or similar (Copilot must reuse existing pattern).

Outputs

Updated CSV with numeric signal_quality_score (0–1).

Log summary: min/avg/max quality per run.

Logic (high level)

For each row:

Check NaNs in key columns (signal, underlying, entry_price, forward_return_*).

Check how recent timestamp is relative to current market time.

Factor volatility (if IV/ATR columns exist; if not, use proxy like high/low range).

Compute score using weighted formula (documented in code).

Write to new column; if any row completely broken, mark score=0.

Improves

Accuracy: signals can later be filtered or weighted by quality.

Safety: low-quality signals can be auto-deprioritized.

When to run

Live: every time curated or forward-return file is updated (hook into existing signal-refresh phases).

Parallel

Can run in parallel with other non-I/O heavy phases; depends mainly on CPU.

Phase 332 – Meta Feature Enrichment (Volatility & Trend Tags)

Objective
Add derived features for each signal: volatility regime, short/medium trend direction, and market regime labels.

Where / Files

Input/Output: storage/live/angel_index_ai_signals_with_forward.csv

New module: phases/phase_332_meta_feature_enrichment.py

Inputs

Historical candles for underlying index/option (from existing candle storage).

Current signals CSV.

Outputs

New columns, e.g.:

vol_regime (LOW/MED/HIGH)

short_trend (UP/DOWN/FLAT)

medium_trend

market_regime (RISK_ON/RISK_OFF/CHOPPY)

Logic

Use existing historical storage API (whatever data.storage uses).

Compute:

ATR or percent range over last N bars.

Short trend using EMA crossover or last N close slope.

Medium trend from longer window.

Classify regimes based on thresholds from config.

Append columns to CSV.

Improves

Accuracy: models get richer, context-aware inputs.

Profit: helps avoid taking trades in bad regimes (choppy).

When

Live: after Phase 331; attached in same refresh cycle.

Parallel

Sequential after 331 (depends on its output).

Phase 333 – Adaptive Threshold Engine v2

Objective
Automatically tune buy/sell/hold thresholds based on recent forward-return distribution and signal-quality distribution.

Where / Files

New module: phases/phase_333_adaptive_threshold_engine_v2.py

Config: extend config/system3_thresholds.json with:

adaptive_thresholds.enabled

min/max ranges per metric.

Inputs

Last N days of forward-return data from:

storage/live/history/angel_index_ai_signals_with_forward_*.csv (or equivalent).

Current thresholds from config.

Outputs

Updated effective thresholds in memory + optional write to a “runtime thresholds” file:

storage/live/runtime_thresholds.json

Log message: current vs adjusted thresholds.

Logic

Load recent forward returns.

Compute percentiles (e.g. 60th, 70th, 80th) for positive and negative returns.

Propose new buy/sell thresholds within min/max allowed bound from config.

Apply smoothing (e.g. exponential moving average) to avoid sudden jumps.

WRITE ONLY to runtime thresholds (not hard-coded config) to keep safety.

Improves

Accuracy: thresholds adapt to current market.

Profit: reacts to changing volatility regimes.

When

Post-market: initial compute.

Live: optionally at 2-hour intervals (but must be cached, not heavy).

Parallel

Can run in background; no direct coupling.

Phase 334 – Meta Model Health Snapshot

Objective
Build a lightweight, live “model health” snapshot: last train time, number of features, input drift signal, and a simple “health score”.

Where / Files

Existing model info: check models/ or storage/models/.

New module: phases/phase_334_model_health_snapshot.py

Output file: storage/live/model_health_snapshot.json

Inputs

Model files (pickle or parquet).

Metadata files from existing training process (if present).

Recent input feature distribution from signals CSV.

Outputs

JSON with fields like:

model_name

last_train_time

feature_count

input_drift_score

health_score (0–1)

Log: summary including health score.

Logic

Inspect model metadata (Copilot must parse existing training files).

Compare feature means/std against training baseline (if baseline saved).

Compute simple drift metric and overall health.

Persist snapshot JSON for monitoring and future safety phases.

Improves

Safety: warnings if model is outdated or heavily drifted.

Accuracy: gives visibility to retrain triggers.

When

Post-market primarily; optional daily pre-market refresh.

Parallel

Independent; read-only.

Phase 335 – Forward-Return Stability Analyzer

Objective
Evaluate how stable forward returns are over rolling windows per symbol/expiry and flag unstable configurations.

Where / Files

Input: storage/live/angel_index_ai_signals_with_forward.csv + history.

New module: phases/phase_335_forward_return_stability.py

Output: storage/live/forward_return_stability_report.csv

Inputs

Forward-return history per underlying/option.

Config thresholds for stability (variance, kurtosis).

Outputs

CSV with:

symbol, expiry, stability_score, trade_allowed (bool).

Logs: top unstable symbols.

Logic

For each symbol/expiry:

Compute variance / standard deviation of forward returns.

Optionally compute Sharpe-style metric.

Map to stability_score (0–1).

If stability below threshold, set trade_allowed=false.

Improves

Accuracy / profit: avoid noisy, unstable combinations.

Safety: reduces random behavior.

When

Post-market: daily, used next day by signal filter.

Parallel

Yes, offline computation.

Phase 336 – Signal Consistency Checker (Cross-Model Check)

Objective
Cross-check signals from multiple models or views (if available) and identify conflicting signals.

Where / Files

Inputs:

Main signals CSV.

If a second model or variant exists (e.g. angel_index_ai_signals_modelB.csv), incorporate.

New module: phases/phase_336_signal_consistency_checker.py

Output: storage/live/signal_consistency_report.csv

Inputs

Multiple signal sources (Copilot must inspect current code for multi-model outputs).

Config for conflict severity.

Outputs

Per-row consistency classification:

CONSISTENT_STRONG, CONSISTENT_WEAK, CONFLICTING, UNKNOWN.

Summary logs (counts per category).

Logic

For each symbol/contract/time:

Compare signals from different models.

Compute a consistency label and optional score.

Improves

Accuracy: prefer trades where models agree.

Safety: highlight ambiguous situations.

When

Live: after signals are generated, before trade-planning.

Parallel

Sequential after base signals produced.

Phase 337 – Market Regime Adaptive Weighting

Objective
Adjust signal weights and trade priority based on detected market regime (from Phase 332).

Where / Files

Input: enriched signals CSV (after Phase 332).

New module: phases/phase_337_market_regime_weighting.py

Inputs

market_regime column from Phase 332.

Config: regime-specific multipliers (e.g. risk_on vs risk_off).

Outputs

New column: regime_weight (0–2, for example).

Optional final_signal_score combining quality + regime.

Logic

For each row:

Map regime to multiplier (risk_on -> >1, risk_off -> <1).

Multiply base signal confidence with regime_weight.

Persist.

Improves

Profit: ride good regimes more aggressively; reduce exposure on bad regimes.

Risk: automatically down-weight in dangerous periods.

When

Live: before OP3 trade plan.

Parallel

After 331/332.

Phase 338 – Dynamic Position Sizing Advisor (Paper Only)

Objective
Suggest recommended position sizes per signal under DRY-RUN only.

Where / Files

Input: enriched signals CSV.

New module: phases/phase_338_position_sizing_advisor.py

Output: add suggested_qty column and a summary file: storage/live/position_sizing_advice.csv.

Inputs

Account “virtual capital” config.

Risk-per-trade config (e.g. 0.5–1%).

Outputs

Suggested quantity per trade.

Logs: total predicted exposure.

Logic

Use risk-per-trade × capital / expected stop distance (or ATR proxy).

Respect max open positions limits from existing configs.

Improves

Profit: consistent sizing improves PnL profile.

Safety: avoids oversizing.

When

Live: before virtual trade generation.

Parallel

After 337.

Phase 339 – Virtual Trade Outcome Simulator (Intraday)

Objective
Using current day intraday moves, simulate potential outcomes of open paper positions to measure intraday risk and PL variance.

Where / Files

Inputs:

Virtual orders log (file used today for DRY-RUN).

Intraday candles from storage.

New: phases/phase_339_virtual_outcome_simulator.py

Output: storage/live/virtual_outcome_snapshot.csv

Inputs

Open paper trades.

Latest intraday prices.

Outputs

Simulated PnL at multiple future points (e.g. +15m, +30m, +1h scenarios).

Log summary: “If current trend continues, worst-case PnL would be X, best-case Y”.

Improves

Safety: early detection of concentration risk.

Accuracy: feedback loop for risk module.

When

Live: once per hour or per OP cycle.

Parallel

Independent; read-only.

Phase 340 – Feature Importance Monitor

Objective
Track live feature importance (from model) and detect if critical features become unstable or missing.

Where / Files

Existing model (e.g. XGBoost / tree-based model).

New: phases/phase_340_feature_importance_monitor.py

Output: storage/live/feature_importance_snapshot.csv + feature_importance_trend.csv.

Inputs

Model object (supports feature_importances or equivalent).

Mapping from feature names to CSV columns.

Outputs

Sorted list of top features.

Trend over days for top N features.

Logic

Extract feature importance from model.

Check that the top features exist and are stable.

If a key feature is missing or constant, log WARN.

Improves

Accuracy: ensures model is using meaningful features.

Safety: quickly shows if pipeline broke a key feature.

When

Post-market: once per day.

Parallel

Independent.

Phase 341 – Model Drift Detector v2 (Rolling Window)

Objective
Quantify drift between training distribution and recent live data in higher detail, triggering WARN / ALERT flags.

Where / Files

New: phases/phase_341_model_drift_detector_v2.py

Input:

Baseline training stats (Copilot must find where training pipeline stores them).

Recent live features from signals CSV.

Output:

storage/live/model_drift_report.csv

Drift flags in model_health_snapshot.json (Phase 334).

Inputs

Baseline mean/std per feature.

Last N live samples.

Outputs

Per-feature drift scores.

Overall drift index.

Logic

Compute standardized differences, KL-divergence or similar metric.

If drift index > threshold, set drift_warning flag.

Improves

Accuracy: indicates when retrain is necessary.

Safety: prevents stale model usage.

When

Post-market daily; optionally weekly deep analysis.

Parallel

Extra but not heavy.

Phase 342 – Live Prediction Performance Estimator (Paper)

Objective
During DRY-RUN, estimate real-time model performance using ongoing forward returns and virtual PnL.

Where / Files

Inputs:

Virtual PnL log.

Forward returns.

New: phases/phase_342_live_performance_estimator.py

Output: storage/live/live_performance_snapshot.json

Inputs

All paper trade outcomes so far today.

Realized forward returns for executed signals.

Outputs

Metrics:

Hit-rate

Avg return per trade

Max drawdown

Realized vs predicted direction

Logs key stats.

Logic

Compute rolling performance metrics.

Expose them for monitoring dashboard / Colab GENI monitor.

Improves

Accuracy monitoring.

Safety: makes sure we don’t go live without robust paper track record.

When

Live: at each OP cycle (hourly).

Parallel

Only reads; safe.

2. Phases 343–350 — Pipeline Hardening & WARN Killer

These phases focus on your existing WARN-heavy zones (220–270, signals CSV missing/empty, etc.).

Phase 343 – Signals Existence & Freshness Enforcer

Objective
Guarantee that angel_index_ai_signals.csv and angel_index_ai_signals_with_forward.csv always exist and are fresh enough, or else force OP3 into NO-TRADE with clear logs.

Where / Files

New: phases/phase_343_signals_freshness_enforcer.py

Inputs

Paths to signals and forward CSV.

Config:

max_signal_age_minutes

min_row_count

Outputs

If missing/stale:

Create safe empty files with headers.

Update a status JSON: storage/live/signal_status.json with flags:

ok, stale, missing, zero_rows.

Logs: clear WARN reasoning.

Improves

Stability: no blind WARN; deterministic behavior when signals are bad.

When

Pre-market & each OP cycle before OP3.

Parallel

Must run before trade-plan phases.

Phase 344 – Pipeline Schema Guard (Live CSVs)

Objective
Validate that all live CSVs used by the signal/trade pipeline match expected schema (columns, types).

Where / Files

Schema definition file: config/system3_live_schema.json (create if not present).

New: phases/phase_344_pipeline_schema_guard.py

Inputs

List of critical CSVs:

angel_index_ai_signals.csv

angel_index_ai_signals_with_forward.csv

curated, pnl, virtual orders, etc.

Outputs

Schema validation report: storage/live/schema_validation_report.csv

Logs per file with PASS/WARN.

Improves

Stability: prevents silent schema drift.

Safety: earlier detection of broken upstream steps.

When

Pre-market and before OP cycle.

Parallel

Independent.

Phase 345 – WARN Phase Root-Cause Tracker

Objective
Convert generic “Phase XXX: WARN” into a structured root-cause report per phase.

Where / Files

New: phases/phase_345_warn_root_cause_tracker.py

Output:

logs/warn_root_cause_log.csv

JSON summary: storage/live/warn_summary.json

Inputs

Autorun logs (today’s file).

Optional direct hooks from phases to a centralized warn-report helper.

Outputs

Per-phase WARN:

phase_number

timestamp

root_cause_code

short description.

Aggregated counts per day.

Improves

Debuggability; makes future hardening easier.

Allows Copilot or GENI agent to see where to focus.

When

Post-market: parse logs.

Optional Live: small hook to append WARN entry when a phase sets WARN.

Parallel

Off-line.

Phase 346 – Live Data Integrity Checker (Option Chain Feeds)

Objective
Verify that live option chain data from AngelOne (or cached local source) is internally consistent (no impossible values, mis-sorted strikes, etc.).

Where / Files

Input: option chain JSON/CSV used by signal engine (Copilot must inspect data fetch module).

New: phases/phase_346_live_data_integrity_checker.py

Output: storage/live/live_data_integrity_report.csv

Inputs

Raw chain data as stored during OP2.

Config for bounds (e.g. max bid/ask spread, non-negative OI).

Outputs

Row-level integrity flags.

If too many rows fail, set global flag in signal_status.json.

Improves

Stability and safety: avoids trading on corrupted live data.

When

Live: after each major chain refresh.

Parallel

Post-fetch, pre-signal generation.

Phase 347 – Historical Cache Sanity Check

Objective
Ensure historical candle/option cache used by System3 is complete (no missing days/bars where needed).

Where / Files

Input: parquet/JSON cache directories (Copilot must use the same as main data.storage).

New: phases/phase_347_historical_cache_sanity.py

Output: storage/live/historical_cache_report.csv

Inputs

List of tracked symbols.

Config for maximum allowed gaps.

Outputs

Per-symbol missing segments, gap counts.

WARNING if major gaps found.

Improves

Accuracy: training & backtest rely on clean history.

Hardening: prevents silent partial data use.

When

Post-market daily; optionally weekly deep scan.

Parallel

Heavy but offline.

Phase 348 – Virtual Orders Schema & Lifecycle Guard

Objective
Guard the full lifecycle of virtual / paper orders (creation, update, close) for consistency.

Where / Files

Existing virtual orders file (Copilot must use current path).

New: phases/phase_348_virtual_orders_guard.py

Output: storage/live/virtual_orders_validation_report.csv

Inputs

Today’s virtual orders log.

PnL log.

Outputs

Flags for:

orphan positions

missing close entries

negative quantities, duplicate IDs

Logs any anomalies.

Improves

Safety: ensures DRY-RUN PnL is correct.

Debugging: catches pipeline mistakes.

When

Post-market EOD; optionally mid-day.

Parallel

Independent.

Phase 349 – Phase Dependency Map & Guard

Objective
Make phase dependencies explicit (which phase requires which files/outputs) and detect if a dependency failed earlier.

Where / Files

New: phases/phase_349_phase_dependency_guard.py

Config: config/system3_phase_dependencies.json

Inputs

Static dependency definitions per phase.

Daily phase results (OK/WARN per phase).

Outputs

If a dependency WARNs, dependent phases auto-downgrade or skip with structured message.

storage/live/phase_dependency_status.json

Improves

Stability: no phase blindly running when prerequisites are broken.

Safety: cascade of WARN instead of silent misbehavior.

When

Live & pre-market: before running each phase (via lightweight helper).

Part of autorun harness.

Parallel

Lightweight, integrated in scheduler.

Phase 350 – WARN-to-Task Converter (Human + Agent Task Queue)

Objective
Convert WARN events into structured “tasks” that Copilot/GENI can later pick and fix.

Where / Files

New: phases/phase_350_warn_task_converter.py

Input:

warn_root_cause_log.csv

Output:

storage/live/warn_task_queue.json

Inputs

Root-cause records from Phase 345.

Outputs

JSON list of tasks, each with:

task_id

phase

root_cause_code

priority

recommended_action (text template for human/agent).

Improves

Automation: structured backlog of what needs fixing.

Maintenance speed.

When

Post-market daily.

Parallel

Offline.

3. Phases 351–356 — Safety & Audit Visibility (DRY-RUN)
Phase 351 – Trading Mode Audit Logger

Objective
Explicitly log trading mode (DRY-RUN vs LIVE) into heartbeat and daily audit files, every session.

Where / Files

Modify: existing heartbeat writer module and/or system3_daily_heartbeat.json writer.

New: phases/phase_351_trading_mode_audit.py

Inputs

Config flags: LIVE_TRADING_ENABLED, USE_LIVE_EXECUTION_ENGINE, auto_execute_trades.

Outputs

Extra fields in heartbeat:

trading_mode (DRY_RUN, LIVE, MIXED)

Audit log: logs/trading_mode_audit.log.

Improves

Safety: always know actual mode used.

Audit: proof you were paper only.

When

Pre-market and whenever mode config is loaded.

Parallel

Lightweight.

Phase 352 – Risk Limits Snapshot & Enforcement Skeleton (Paper)

Objective
Take current configured risk limits (max daily loss, per-trade risk, max open positions) and snapshot them; enforce in DRY-RUN by blocking virtual trades if exceeded.

Where / Files

New: phases/phase_352_risk_limits_snapshot.py

Input:

Risk config file (existing).

Output:

storage/live/risk_limits_snapshot.json

Inputs

Config for risk.

Live virtual PnL and open positions.

Outputs

Snapshot JSON.

Logs if any limit breached -> set no_new_trades=true in a runtime flag file, e.g. storage/live/runtime_flags.json.

Improves

Safety: risk control in DRY-RUN to validate behavior before real trading.

When

Live: every OP cycle (post-PnL calculation).

Parallel

Quick, can be inserted in OP3 pre-trade planning.

Phase 353 – Broker Connectivity Health Monitor (Read-Only)

Objective
Monitor AngelOne API connectivity and record any outages or latency spikes.

Where / Files

New: phases/phase_353_broker_connectivity_monitor.py

Input: existing API wrapper logs or a small ping call.

Output: storage/live/broker_connectivity_log.csv

Inputs

Small heartbeat request or ping.

Timing measurements.

Outputs

rows: timestamp, ping_ms, status (OK/WARN/ERROR).

Improves

Safety: know when broker side is unstable.

Decision: avoid trading at times of broker issues.

When

Live: periodic (e.g., every 15–30 min).

Parallel

Lightweight.

Phase 354 – Virtual vs Theoretical Fill Check

Objective
Validate that virtual order fills are realistic given live bid/ask spreads.

Where / Files

New: phases/phase_354_virtual_fill_realism_checker.py

Inputs:

Live bid/ask for options.

Virtual order execution prices.

Output: storage/live/virtual_fill_realism_report.csv

Inputs

Each virtual fill with price.

Corresponding live quotes.

Outputs

Flag unrealistic fills (e.g., better than best bid/ask by too much).

Logs summary.

Improves

Safety: ensures DRY-RUN PnL is not “too optimistic”.

Accuracy: sets realistic expectations for live.

When

Post-market daily.

Parallel

Offline.

Phase 355 – Paper Trading Audit Trail Generator

Objective
Generate a consolidated day-end audit trail of all paper trades and signals that led to them.

Where / Files

New: phases/phase_355_paper_trading_audit_trail.py

Inputs:

Signals CSV.

Virtual orders log.

PnL file.

Output:

storage/live/audit/paper_trading_audit_<date>.csv

Inputs

All relevant trading data for the day.

Outputs

For each trade:

entry signal details

rationale fields (confidence, regime, size)

outcome

Log summary of performance.

Improves

Auditability.

Explains “why” each trade was taken (for you + future agents).

When

Post-market, part of EOD learning pipeline.

Parallel

EOD offline.

Phase 356 – Safety Dashboard Snapshot (JSON for GENI/Colab)

Objective
Produce a single JSON snapshot combining safety, risk, drift, and connectivity for monitoring dashboards/Colab GENI monitor.

Where / Files

New: phases/phase_356_safety_dashboard_snapshot.py

Input:

model_health_snapshot.json

model_drift_report.csv

broker_connectivity_log.csv

risk_limits_snapshot.json

signal_status.json

Output:

storage/live/safety_dashboard_snapshot.json

Inputs

All safety-related JSON/CSV produced by earlier phases.

Outputs

JSON with:

model_health

drift_status

risk_limits

connectivity_status

signal_status

For GENI/Colab to visualize.

Improves

Visibility: one file for complete safety status.

Useful for remote monitoring.

When

Live: each OP cycle.

Parallel

Aggregation-only.

4. Phases 357–360 — Automation & Self-Healing Helpers
Phase 357 – Log Noise Filter & Structurer

Objective
Reduce log noise, categorize messages, and keep structured summary for agents.

Where / Files

New: phases/phase_357_log_noise_filter.py

Input: today’s runtime log(s).

Output:

storage/live/log_summary_structured.json

Inputs

Autorun + autopilot logs.

Outputs

Aggregated counts:

INFO/WARN/ERROR

top repeated messages.

Short summary text for human/agent.

Improves

Automation: makes log analysis easier for agents.

Maintenance.

When

Post-market; optional mid-day.

Parallel

Offline.

Phase 358 – Auto-Checklist Generator from WARNs

Objective
Convert current WARNs (and tasks from Phase 350) into a simple daily checklist file.

Where / Files

New: phases/phase_358_auto_checklist_generator.py

Inputs:

warn_task_queue.json

log_summary_structured.json

Output:

storage/live/system3_daily_checklist.md

Inputs

Task queue + log summary.

Outputs

Markdown checklist with:

 high-priority tasks

 medium

 low

Sorted by severity.

Improves

Automation & workflow clarity.

When

Post-market.

Parallel

Offline.

Phase 359 – Self-Healing Suggestion Engine (Read-Only)

Objective
Analyze WARNs + dependency map and produce suggestions (not actual code changes) for future auto-fix agents.

Where / Files

New: phases/phase_359_self_healing_suggestions.py

Inputs:

phase_dependency_status.json

warn_task_queue.json

schema_validation_report.csv

Output:

storage/live/self_healing_suggestions.json

Inputs

Structural information about failures.

Outputs

Suggestions:

e.g., “Phase 261 WARN usually due to missing column X in signals CSV; consider adding schema guard or auto-fill default 0.”

No direct code modifications.

Improves

Automation planning: foundation for future auto-code tools.

When

Post-market.

Parallel

Offline.

Phase 360 – DRY-RUN Readiness Gate for Live Trading

Objective
Evaluate whether the system meets required conditions to even consider moving from DRY-RUN to LIVE (in future).

Where / Files

New: phases/phase_360_dry_run_readiness_gate.py

Inputs:

live_performance_snapshot.json

safety_dashboard_snapshot.json

paper_trading_audit_trail.csv

Output:

storage/live/dry_run_readiness_report.json

Inputs

Performance, safety, audit metrics.

Outputs

ready_for_live: true/false

reasons, unmet conditions (e.g., “min 30 green days required, currently 12”).

Improves

Safety: objective gate before live deployment.

Planning: you know when the system is mature.

When

Post-market.

Parallel

Aggregation-only.

5. Block Test & Validation Plan for 331–360

Copilot must implement and then run:

5.1. Per-Phase Quick Test

For each new phase 33X:

Create a small test harness:

Either tests/test_phase_33X.py or tools/run_phase_33X_test.py.

Test should:

Load sample or latest real files from storage/.

Run the main run_phase_33X() function.

Assert:

No exception raised.

Expected output file / columns exist.

5.2. Block Test – Accuracy/Hardening/Safety/Automation

Create one script:

tools/run_phases_331_360_block_test.py

Steps:

Ensure mode is DRY-RUN (check config).

Run in order: 331–360 for yesterday’s data (if possible) to avoid live dependence.

Log results to:

logs/block_test_331_360.log

Print final summary:

count OK / WARN / ERROR.

If any ERROR: exit non-zero for CI-like behavior.

5.3. Manual Acceptance Checklist (for you)

After Copilot implements:

Code inspection

Check each new phase file exists.

Confirm imports are from existing System3 modules (no random packages).

Dry-run tests

Run:

python tools/run_phases_331_360_block_test.py

Confirm:

No ERRORS.

WARNs only where expected (e.g. missing baseline data).

Log verification

Open logs/block_test_331_360.log:

Search for [PH331] etc. to ensure each phase logged.

Safety

Confirm trading_mode appears in heartbeat JSON.

Confirm readiness gate (Phase 360) created the report.