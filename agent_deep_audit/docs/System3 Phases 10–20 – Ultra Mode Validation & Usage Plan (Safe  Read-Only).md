System3 Phases 10–20 – Ultra Mode Validation & Usage Plan (Safe / Read-Only)

Scope: This plan assumes baseline profile remains frozen and protected.
All Ultra work must stay in separate folders and must never overwrite baseline models, data, or configs. 

system3_phases_10_20_final_test…

0. Global Safety Rules (for all phases)

Agent – ALWAYS enforce:

Do NOT modify or delete:

core/models/dhan/*.pkl

core/models/dhan/*_meta.json

Existing files under storage/training/dhan_index_options_training*

Existing configs under storage/config/ (only read)

All Ultra work must stay under:

core/models/dhan_ultra/

storage/learning_ultra/

storage/reports_ultra/

storage/training/dhan_ultra_*

No auto-promotion to LIVE.

Promotion to baseline must remain manual only and gated by explicit keyword confirmation (already implemented by Promotion Manager).

No broker calls inside these phases unless explicitly mentioned (Phase 17 is allowed to touch broker; others are offline).

At the end of all phases, baseline behavior must be unchanged when running:

python run_system3.py
# Using BASELINE profile and menu 11 (LIVE AI signals, DRY RUN)

Phase 10 – Shadow Data Engine

Goal: Build a shadow dataset from existing signals/trade/PnL logs that is safe for Ultra experimentation.

10.1 Files & Modules

Module: core/engine/dhan_ultra_shadow_data.py

Input sources (read-only):

storage/live/dhan_index_ai_signals.csv

storage/live/dhan_index_ai_trades_plan.csv

storage/live/dhan_index_ai_pnl_log.csv

Output (Ultra-only):

storage/learning_ultra/dhan_ultra_shadow_master.csv

storage/learning_ultra/dhan_ultra_shadow_master.parquet

10.2 Expected Behavior

Join signals, trade plans, and PnL logs into a single consolidated master dataset:

Core columns: ts, underlying, strike, side, ltp, spot, pred_label, signal, score, conf, entry_price, exit_price, pnl_pct, exit_reason, etc.

Handle small datasets gracefully (even with only 3 rows).

Do not crash if trade or PnL files are missing; just log a warning and continue with what’s available.

10.3 Command
python -m core.engine.dhan_ultra_shadow_data

10.4 Agent – Confirmation to show

After implementation and run, show:

The final head() of dhan_ultra_shadow_master.csv (first ~5 rows).

print(df.shape) for the master dataset (should show something like (3, N) for current environment).

dir storage\learning_ultra\dhan_ultra_shadow_master.* output to confirm both CSV & Parquet exist.

Phase 11 – Feature Expander (Ultra Features)

Goal: Build rich Ultra feature set on top of shadow data, without touching baseline feature pipeline.

11.1 Files & Modules

Module: core/engine/dhan_ultra_feature_expander.py

Input:

storage/learning_ultra/dhan_ultra_shadow_master.parquet

Output:

storage/training/dhan_ultra_training.csv

storage/training/dhan_ultra_training.parquet

11.2 Features

In addition to baseline features, compute Ultra-only features such as:

Expanded moneyness & distance:

moneyness, atm_dist_abs, atm_dist_pct

Multi-step momentum:

spot_chg_1_pct, spot_chg_3_pct, spot_chg_5_pct

ltp_chg_1_pct, ltp_chg_3_pct, ltp_chg_5_pct

Rolling vols:

spot_roll_std_5, spot_roll_std_10

ltp_roll_std_5, ltp_roll_std_10

Regime proxy features:

vol_regime_hint, trend_regime_hint

Microtrend & premium behavior:

premium_slope_3, premium_slope_5

premium_accel_3, premium_accel_5

Risk/structure features:

rr_ratio_hint, premium_strength, spot_leads_premium, premium_leads_spot

Total: expect ~40–52 features per row (22 baseline-style + extra Ultra).

11.3 Command
python -m core.engine.dhan_ultra_feature_expander

11.4 Agent – Confirmation to show

print(df.shape) for dhan_ultra_training.parquet (rows, columns).

print(sorted(df.columns.tolist())) (ensure new Ultra features appear).

Count features:

Number of columns (should be around 40–52).

Confirm file presence:

dir storage\training\dhan_ultra_training.*

Phase 12 – Ultra Model Trainer

Goal: Train Ultra models for each underlying using the extended Ultra training dataset, fully isolated.

12.1 Files & Modules

Module: core/engine/dhan_ultra_model_trainer.py

Input:

storage/training/dhan_ultra_training.parquet

Output:

core/models/dhan_ultra/*_ultra_model.pkl

core/models/dhan_ultra/*_ultra_model_meta.json

12.2 Behavior

For each underlying (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX):

Filter data by underlying.

Ensure all three label classes present (BUY_CE, BUY_PE, HOLD).

Train using a robust classifier (e.g., Gradient Boosting / XGBoost / RandomForest – already wired).

Train/test split, compute metrics.

Save:

Model file under dhan_ultra/.

Meta file with:

underlying

accuracy

features_list

timestamp

training_rows

12.3 Command
python -m core.engine.dhan_ultra_model_trainer

12.4 Agent – Confirmation to show

Training log showing accuracy per underlying (target: ~99–100% on synthetic+shadow).

Directory listing:

dir core\models\dhan_ultra


Print one sample meta JSON (e.g., NIFTY_ultra_model_meta.json) showing:

accuracy

feature count

underlying

Phase 13 – Hyperparameter Explorer

Goal: Explore different hyperparameters for Ultra models and log results only (no overwrite of actual Ultra models).

13.1 Files & Modules

Module: core/engine/dhan_ultra_hparam_explorer.py

Input:

storage/training/dhan_ultra_training.parquet

Output:

storage/reports_ultra/ultra_hparam_results_<UNDERLYING>.csv (one per underlying)

13.2 Behavior

For each underlying:

Try several hyperparameter sets (e.g., different depths, estimators, learning rates).

Train quickly and compute:

Accuracy

Precision/recall per class

Overfit indicators (train vs test).

Save results into per-underlying CSV report.

Do not write any model files in this phase.

13.3 Command
python -m core.engine.dhan_ultra_hparam_explorer

13.4 Agent – Confirmation to show

dir storage\reports_ultra\ultra_hparam_results_*.csv

head -n 10 (or first few rows) of one report (e.g. NIFTY).

Confirm no new files created in core/models/dhan_ultra/ during this step.

Phase 14 – Regime Classifier

Goal: Tag each Ultra training row with a market regime (e.g., HIGH_VOL_TREND_UP, HIGH_VOL_RANGE, etc.) and save a regime-labeled dataset.

14.1 Files & Modules

Module: core/engine/dhan_ultra_regime_classifier.py

Input:

storage/training/dhan_ultra_training.parquet

Output:

storage/training/dhan_ultra_training_with_regime.parquet

storage/reports_ultra/ultra_regime_summary.csv

14.2 Behavior

Use vol and trend proxies (already implemented) to classify rows into regimes, such as:

LOW_VOL_TREND_UP

LOW_VOL_TREND_DOWN

HIGH_VOL_TREND_UP

HIGH_VOL_TREND_DOWN

HIGH_VOL_RANGE

etc.

Save summary with:

regime, count, pct

14.3 Command
python -m core.engine.dhan_ultra_regime_classifier

14.4 Agent – Confirmation to show

print(df['regime'].value_counts(normalize=True).head()) for the regime-labeled dataset.

Show ultra_regime_summary.csv first 10 lines.

Confirm file presence:

dir storage\training\dhan_ultra_training_with_regime.parquet
dir storage\reports_ultra\ultra_regime_summary.csv

Phase 15 – Multi-Consensus (Baseline vs Ultra)

Goal: Compare baseline vs Ultra predictions on the same sample rows to measure agreement and potential Ultra improvements.

15.1 Files & Modules

Module: core/engine/dhan_ultra_multi_consensus.py

Inputs:

Baseline models: core/models/dhan/*.pkl

Ultra models: core/models/dhan_ultra/*_ultra_model.pkl

A subset of dhan_ultra_training_with_regime.parquet

Output:

storage/reports_ultra/ultra_consensus_sample.csv

15.2 Behavior

For a sample of rows per underlying:

Compute baseline prediction + Ultra prediction.

Store:

baseline_pred, baseline_conf

ultra_pred, ultra_conf

agreement_flag

Save consensus sample CSV.

15.3 Command
python -m core.engine.dhan_ultra_multi_consensus

15.4 Agent – Confirmation to show

head() of ultra_consensus_sample.csv.

A small pivot / counts:

agreement_flag value counts.

Confirm both baseline and Ultra models loaded in logs without error.

Phase 16 – Threshold Lab (Ultra Threshold Grid Search)

Goal: Try multiple threshold combinations on Ultra predictions and identify good candidates (for offline analysis only).

16.1 Files & Modules

Module: core/engine/dhan_ultra_threshold_lab.py

Inputs:

dhan_ultra_training_with_regime.parquet

Ultra models

Output:

storage/reports_ultra/ultra_threshold_grid_search.csv

16.2 Behavior

For each underlying:

Test grid of:

conf_thresh (e.g., 0.60–0.95)

score_thresh (e.g., 0.10–0.60)

Compute:

Hit rate

Trade frequency

Approx PnL proxy (based on labels)

Save results per underlying into one combined CSV.

16.3 Command
python -m core.engine.dhan_ultra_threshold_lab

16.4 Agent – Confirmation to show

head() of ultra_threshold_grid_search.csv.

Count of rows per underlying.

Confirm no config files were modified.

Phase 17 – Live Signals Shadow (Broker-Dependent, Optional)

Goal: When broker is online, run Ultra shadow inference on live snapshots in parallel (no trade execution).

17.1 Files & Modules

Module: core/engine.ultra_live_signals_shadow

Inputs:

Live snapshots sourced via existing pipeline (same as baseline live signals).

Ultra models.

Outputs:

e.g. storage/live/dhan_ultra_live_shadow_signals.csv (or similar).

17.2 Behavior

For each live snapshot:

Compute Ultra prediction; log alongside baseline.

No trading; logging only.

17.3 Command
python -m core.engine.ultra_live_signals_shadow

17.4 Agent – Confirmation to show

One sample snapshot block printed with Ultra predictions.

CSV log file head.

Confirm there is no order placement or any API call for trades.

Phase 18 – Ultra Trade Simulator (Offline, Ultra Only)

Goal: Simulate Ultra-only trades using the Ultra shadow master dataset, with Ultra thresholds and features.

18.1 Files & Modules

Module: core/engine.dhan_ultra_trade_simulator

Input:

storage/learning_ultra/dhan_ultra_shadow_master.parquet

Output:

storage/learning_ultra/dhan_ultra_trade_sim_results.csv (or similar)

18.2 Behavior

If dataset is small (like 3 rows), it may find 0 trades (expected).

When more data exists:

Apply Ultra thresholds.

Simulate entries/exits using shadow timeline.

Save trade list + synthetic PnL.

18.3 Command
python -m core.engine.dhan_ultra_trade_simulator

18.4 Agent – Confirmation to show

Log messages showing:

Total signals.

How many passed thresholds.

If zero trades, confirm “No eligible trades” message (expected with tiny dataset).

If trades exist, head() of simulation CSV.

Phase 19 – PnL Analyzer (Ultra Simulation)

Goal: Analyze results of Phase 18 simulation.

19.1 Files & Modules

Module: core/engine.dhan_ultra_pnl_analyzer

Input:

dhan_ultra_trade_sim_results.csv

Output:

Summary printed to console.

Possibly storage/reports_ultra/ultra_pnl_summary.csv.

19.2 Behavior

If simulation file missing → log expected message and exit gracefully.

If present:

Compute win rate, avg PnL, distribution, regime stats.

19.3 Command
python -m core.engine.dhan_ultra_pnl_analyzer

19.4 Agent – Confirmation to show

If no simulation file: log line saying so.

If present: printed summary table (by underlying).

Confirm no changes to live PnL logs or baseline reports.

Phase 20 – Promotion Manager (Manual, Safety-Gated)

Goal: Compare Baseline vs Ultra models and provide a manual, keyword-gated mechanism to promote Ultra to baseline (for future, not now).

20.1 Files & Modules

Module: core/engine.dhan_ultra_promotion_manager

Inputs:

Baseline models + metadata.

Ultra models + metadata.

For now, NO actual file copy should happen unless an explicit promotion keyword is passed (and we are not using it right now).

20.2 Behavior

Show comparison table:

Underlying

Baseline accuracy (if available in meta, else 0 or N/A)

Ultra accuracy

Notes

Promotion path:

Require explicit keyword (e.g., PROMOTE_ULTRA_TO_BASELINE_I_UNDERSTAND_THE_RISK) to perform any file copy.

In safe mode: no promotions must be executed.

20.3 Command
python -m core.engine.dhan_ultra_promotion_manager

20.4 Agent – Confirmation to show

Printed comparison table: baseline vs Ultra metrics.

Confirm:

No baseline files changed.

No files copied to core/models/dhan/ in current run (since no keyword provided).

dir core\models\dhan before & after → identical.

Final Checklist for Agent

After completing Phases 10–20:

Run all phase commands once in order:

python -m core.engine.dhan_ultra_shadow_data
python -m core.engine.dhan_ultra_feature_expander
python -m core.engine.dhan_ultra_model_trainer
python -m core.engine.dhan_ultra_hparam_explorer
python -m core.engine.dhan_ultra_regime_classifier
python -m core.engine.dhan_ultra_multi_consensus
python -m core.engine.dhan_ultra_threshold_lab
# (Optional, broker-dependent)
# python -m core.engine.ultra_live_signals_shadow
python -m core.engine.dhan_ultra_trade_simulator
python -m core.engine.dhan_ultra_pnl_analyzer
python -m core.engine.dhan_ultra_promotion_manager


Prepare a short execution summary:

Which commands ran.

Any commands that behaved as “no trades / no data” due to small dataset.

Confirm no baseline overwrite.

Confirm that:

Baseline run still behaves exactly as before:

python run_system3.py
# Use BASELINE profile, menu 11, DRY RUN


No unintended config/model changes occurred outside Ultra folders.

If all confirmations match the expectations above, System3 Ultra Phases 10–20 are validated and safe for experimental use, while baseline remains fully protected.