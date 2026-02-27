# System3 Phases 201–400 – Full-Pass Implementation Specification
This document defines concrete, implementation-ready specifications for **System3 Phases 201–400**.
Each phase has:
- A clear objective
- Concrete actions/tasks
- Expected outputs / artifacts
- Integration notes where relevant

---
## PHASE 201 – Filesystem Integrity Verifier
- Scan all core System3 directories (root, `core/`, `phases/`, `config/`, `storage/`, `logs/`, `docs/`).
- Verify that mandatory folders exist; auto-create missing **non-critical** directories.
- List missing **critical** files/folders in a markdown report at `logs/system3_fs_integrity_report.md`.
- Return a phase result dict with `status` (OK/WARN/ERROR) and `missing_critical_count`.

## PHASE 202 – Permission Self-Repair
- Attempt read/write test on key directories: `storage/`, `logs/`, `models/` (if present).
- On permission failure, attempt to adjust Windows ACL for the current user (non-destructive).
- If ACL repair fails, create a **fallback storage clone** under `storage_fallback/` and record mapping.
- Log all actions to `logs/system3_permissions_self_repair.log` with before/after status.

## PHASE 203 – Config Consistency Check
- Enumerate all `*.json` files under `config/` and `core/config/` (if present).
- For each file: verify it is valid JSON; on parse errors, back up the original and rewrite minimal default schema.
- Validate presence of required top-level keys per known config types (e.g., `live_trade_config`, `ultra_safety`).
- Write a consolidated report at `logs/config/system3_config_consistency_report.md`.

## PHASE 204 – Python Environment Validator
- Check that the active interpreter is Python **3.10+** and record `sys.version` to a report.
- Attempt imports for all required core packages (pandas, numpy, requests, sklearn, xgboost, etc.).
- Generate or update an `install_requirements.bat` script that installs any missing packages with `pip`.
- If critical libraries are missing, mark phase status as `WARN` and list them in `logs/env/system3_env_validator.log`.

## PHASE 205 – Broker Credential Self-Tester
- Load AngelOne credentials from the existing config location (without printing secrets to logs).
- Perform a safe, read-only API call (e.g., profile or exchange info) to validate connectivity.
- Perform a read-only public call to Binance (if enabled in config) and confirm reachability.
- Mask all sensitive fields before logging and write results to `logs/brokers/system3_broker_selftest.log`.

## PHASE 206 – Model Compatibility Checker
- Scan `models/` for known PKL artifacts (e.g., option models, signal models).
- For each model, check an embedded `model_version` or metadata key against a central engine version constant.
- If mismatched, schedule or trigger a model rebuild job (via a queue file in `storage/model_jobs/`).
- Report compatible vs incompatible models in `logs/models/system3_model_compatibility_report.md`.

## PHASE 207 – Hotfix Registry Manager
- Maintain a JSON registry `storage/meta/system3_hotfix_registry.json` listing all applied hotfix IDs.
- On each run, verify that registry entries still correspond to existing code changes or patches.
- Remove obsolete hotfix entries and mark deprecated patches as `retired` in the registry.
- Log a summary of newly applied, active, and retired hotfixes to `logs/meta/system3_hotfix_registry.log`.

## PHASE 208 – Signal Consistency Engine
- Load recent signals from `storage/live/angel_index_ai_signals.csv` (using robust parser).
- Validate that no row has impossible combinations (e.g., `BUY` with negative `final_score` far below sell threshold).
- Detect contradictory signals for the same `(ts, underlying, strike, side)` and auto-correct based on scoring rules.
- Write a consistency summary to `logs/signals/system3_signal_consistency_report.md` and return counts of fixed rows.

## PHASE 209 – Training Data Duplicate Purger
- Load curated training data from `storage/live/angel_index_ai_signals_curated.csv`.
- Identify duplicates based on composite key `(ts, underlying, strike, side, expiry)`.
- Keep only the most recent row per key (e.g., latest `ts` or file-order) and drop older duplicates.
- Rewrite the curated file with deduplicated rows and log purged counts to `logs/data_cleaning/system3_duplicate_purger.log`.

## PHASE 210 – Historical Timegap Analyzer
- Load historical signals or candle snapshots and sort by `ts`.
- Compute gaps between consecutive timestamps; detect gaps greater than a configurable threshold (default 2 minutes).
- Mark those intervals in a separate JSON or CSV `storage/meta/system3_timegap_flags.csv` with reason codes.
- Summarize the number and size of gaps in `logs/history/system3_timegap_analyzer_report.md`.

## PHASE 211 – Feature Drift Monitor
- Load recent training features (from curated file or feature store).
- Compute rolling means/standard deviations for key numeric features (delta, gamma, IV, etc.) and compare vs historical baselines.
- Flag features whose distribution has shifted beyond a configured threshold (e.g., 3σ).
- Write drift diagnostics to `logs/ml/system3_feature_drift_report.md`.

## PHASE 212 – Label Quality Inspector
- Analyze distribution of `pred_label` (BUY/SELL/HOLD) over recent history to detect severe imbalance.
- Check consistency between label and realized movement (if forward returns are available).
- Produce a table of label counts, imbalance ratios, and suspected noisy labels.
- Save the report to `logs/ml/system3_label_quality_report.md`.

## PHASE 213 – Training Window Selector
- From archives, build candidate training windows (e.g., last 5, 10, 20 days).
- Evaluate each window for minimum row counts, label diversity, and absence of large data gaps.
- Select a preferred window and write its boundaries to `storage/meta/system3_training_window.json`.
- Log evaluation metrics per window to `logs/ml/system3_training_window_selection.log`.

## PHASE 214 – Model Hyperparameter Snapshotter
- For each active ML model, record current hyperparameters into `storage/meta/system3_model_hparams.json`.
- Include model type, feature list, and any training configuration (max_depth, n_estimators, etc.).
- When models are retrained, update this snapshot to preserve a history of changes.
- Generate a markdown summary at `logs/ml/system3_hyperparam_history.md`.

## PHASE 215 – Model Overfit Sentinel
- Evaluate each model on an internal validation split using stored metrics (if available).
- Flag models with large gaps between training and validation performance beyond a configurable threshold.
- Record suspected overfitting cases and recommend actions (retrain, regularize, reduce complexity).
- Log findings to `logs/ml/system3_overfit_sentinel_report.md`.

## PHASE 216 – Greeks Calculation Auditor
- Verify numerical stability of delta, gamma, theta, vega calculations using sample instruments.
- Compare internal Greeks to a reference approximation (e.g., Black-Scholes) for sanity checks.
- Flag instruments whose Greeks deviate beyond tolerance from the reference model.
- Output a summary to `logs/risk/system3_greeks_audit_report.md`.

## PHASE 217 – Volatility Regime Classifier
- Compute IV rank/percentile for major underlyings using recent implied volatility history.
- Classify each underlying each day into regimes: LOW, NORMAL, HIGH volatility.
- Store regime labels in `storage/meta/system3_vol_regimes.csv` keyed by date and underlying.
- Log regime transitions and counts to `logs/risk/system3_vol_regime_report.md`.

## PHASE 218 – Momentum Pattern Scanner
- Run simple momentum indicators (ROC, EMA crossover, RSI) on key underlyings using historical prices.
- Flag strong bullish/bearish momentum patterns according to pre-defined rules.
- Store detected patterns with timestamps in `storage/meta/system3_momentum_patterns.csv`.
- Summarize daily pattern counts and examples in `logs/research/system3_momentum_scan_report.md`.

## PHASE 219 – Breakout Structure Analyzer
- Detect support/resistance levels using recent highs/lows and volume (if available).
- Mark potential breakout/breakdown zones and align them with option strikes.
- Export breakout structures to `storage/meta/system3_breakout_zones.json`.
- Log important breakout candidates to `logs/research/system3_breakout_analyzer.log`.

## PHASE 220 – Cross-Underlying Correlation Map
- Compute rolling correlations between major indices (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX).
- Detect periods of unusually high or low correlation and flag them as special regimes.
- Store correlation matrices in `storage/meta/system3_correlation_matrices.npz` or CSV.
- Write a readable summary to `logs/research/system3_correlation_report.md`.

## PHASE 221 – Forward Return Calculator
- Use archived price data to compute forward returns (e.g., next 1, 3, 5 snapshots) for past signals.
- Attach forward return metrics to historical signals for label quality and edge analysis.
- Save enriched data to `storage/live/angel_index_ai_signals_with_forward.csv`.

## PHASE 222 – Signal Edge Estimator
- Estimate expected value (EV) of BUY/SELL signals based on forward returns by score decile.
- Produce EV tables per underlying and score bucket.
- Log results to `logs/research/system3_signal_edge_report.md`.

## PHASE 223 – Threshold Optimizer
- Using historical data, optimize BUY/SELL thresholds to maximize chosen objective (e.g., Sharpe, hit rate).
- Propose candidate thresholds for production and store them in `storage/meta/system3_threshold_candidates.json`.
- Log optimization process and metrics to `logs/research/system3_threshold_optimizer.log`.

## PHASE 224 – Score Component Attribution
- Decompose final_score into contributions from greeks_score, ai_score, trend_score, etc.
- Analyze which components drive most of the final decision across instruments and time.
- Save attribution statistics to `logs/research/system3_score_component_attribution.md`.

## PHASE 225 – Label Reconciliation Engine
- Rebuild labels for historical rows using a consistent rule set and forward returns.
- Compare old vs rebuilt labels and quantify discrepancies.
- Optionally write a reconciled dataset for retraining at `storage/live/angel_index_ai_signals_reconciled.csv`.

## PHASE 226 – Feature Importance Tracker
- Compute feature importances from current models and store in `storage/meta/system3_feature_importances.json`.
- Track how importance ranks change over time and mark unstable features.
- Log top-10 most important features per model to `logs/ml/system3_feature_importance_report.md`.

## PHASE 227 – Data Latency Profiler
- Measure delay between market timestamps and ingestion/processing times.
- Compute statistics of latency per snapshot and per underlying.
- Log latency distribution to `logs/performance/system3_latency_profile.md`.

## PHASE 228 – Snapshot Coverage Auditor
- For each expected time bucket in trading hours, verify whether a snapshot was processed.
- Count missing or delayed snapshots and mark them in `storage/meta/system3_snapshot_coverage.csv`.
- Write a human-readable summary to `logs/performance/system3_snapshot_coverage_report.md`.

## PHASE 229 – Data Shape and Schema Guard
- Verify that incoming CSV/JSON files match expected schemas (columns and dtypes).
- Auto-add missing optional columns with defaults, and block if critical columns are missing.
- Log schema mismatches and auto-fixes to `logs/data/system3_schema_guard.log`.

## PHASE 230 – AI Fallback Behavior Auditor
- Review logs to count how often delta-based ai_score fallback is used vs full ML model.
- Identify reasons for fallback usage (e.g., lack of curated data, load errors).
- Save a summary to `logs/ml/system3_ai_fallback_audit.md` with recommendations.

