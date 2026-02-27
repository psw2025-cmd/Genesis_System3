# System3 Ultra-Mode Master Plan  
### Phases 10–20 (Shadow / Ultra Pipeline)  
Profile: `ULTRA_DEV` (baseline fully protected)

> This file is written for Cursor Agent.  
> All changes are **additive only**. Existing baseline files, models, configs and menus must **not** be overwritten.

---

## 0. GLOBAL RULES FOR ULTRA MODE

### 0.1. Profiles and Directories

**Profiles**

- `BASELINE`  → current production profile (already built, FROZEN).
- `ULTRA_DEV` → new Ultra profile (shadow learning + experiments).

**New directories (must exist, create if missing)**

- Models (shadow):  
  `core/models/angel_one_ultra/`
- Ultra data (shadow learning):  
  `storage/ultra/`
- Ultra learning / research:  
  `storage/learning_ultra/`
- Ultra reports:  
  `storage/reports_ultra/`
- Ultra config:  
  `core/config/`

**Cursor Agent – Task 0.1**

1. Ensure these directories exist (create if needed, do not delete/modify old ones):

   - `core/models/angel_one_ultra/`
   - `storage/ultra/`
   - `storage/learning_ultra/`
   - `storage/reports_ultra/`

2. Do **not** delete or move any existing files.

**Validation**

- `dir core\models\angel_one_ultra`
- `dir storage\ultra`
- `dir storage\learning_ultra`
- `dir storage\reports_ultra`

You should see empty (or only new) folders. No baseline files moved or removed.

---

### 0.2. Ultra Safety Switches (HARD OFF)

Create one central safety file:

- `core/config/system3_ultra_safety.json`

**Required JSON structure (all `false` by default):**

```json
{
  "AUTO_EXECUTE_TRADES": false,
  "AUTO_UPDATE_THRESHOLDS": false,
  "AUTO_RETRAIN_MODELS": false,
  "AUTO_PROMOTE_MODELS": false,
  "AUTO_WRITE_CONFIG": false
}
Cursor Agent – Task 0.2

Create core/config/system3_ultra_safety.json with the exact structure above.

Add a small helper in a new module:

core/engine/ultra_safety.py

Functions:

load_ultra_safety() -> dict

is_ultra_enabled(flag_name: str) -> bool

Always default to False if something is missing or file not found.

Do not modify any existing baseline safety/config file.

Validation – Commands & Expected

Run:

python -c "from core.engine.ultra_safety import load_ultra_safety, is_ultra_enabled; print(load_ultra_safety()); print(is_ultra_enabled('AUTO_EXECUTE_TRADES'))"


Expected:

Printed dict with all 5 keys, all False.

Second line printed: False.

0.3. Profile Selector (Baseline vs Ultra)

Add/extend existing profile selector so that:

BASELINE uses:

models: core/models/angel_one/

configs: existing ones

ULTRA_DEV uses:

models: core/models/angel_one_ultra/

ultra data dirs: storage/ultra/, storage/learning_ultra/, storage/reports_ultra/

File to extend (if already present)

core/engine/angel_model_selector.py
or

If not present, create it with:

get_active_profile() -> str

get_model_dir(profile: str) -> str

get_storage_dirs(profile: str) -> dict

Cursor Agent – Task 0.3

Ensure angel_model_selector.py supports:

Profiles: "BASELINE", "ULTRA_DEV".

A simple config file:

core/config/system3_active_profile.json:

{
  "ACTIVE_PROFILE": "BASELINE"
}


Functions:

get_active_profile() – read JSON, default "BASELINE".

get_model_dir(profile=None) – return baseline or ultra model dir.

get_storage_dirs(profile=None) – include:

signals_dir

trades_dir

pnl_dir

learning_dir

reports_dir

For ULTRA_DEV, these should point to ultra paths (storage/ultra, storage/learning_ultra, storage/reports_ultra, etc.), but signals/trades/pnl can still refer to existing live logs if needed.

Do not change existing baseline defaults.

Validation

Run:

python -m core.engine.angel_model_selector


Expected:

Shows something like:

ACTIVE_PROFILE: BASELINE
BASELINE model dir: core/models/angel_one
ULTRA_DEV model dir: core/models/angel_one_ultra

Phase 10 – Shadow Real-Data Engine V1

Goal: build shadow learning datasets for Ultra profile using real signals, trade plans, PnL logs, outcomes.

New module:

core/engine/ultra_shadow_data_engine.py

10.1. Inputs

From baseline (already present):

Signals: storage/live/angel_index_ai_signals.csv

Trade plans: storage/live/angel_index_ai_trades_plan.csv

PnL log: storage/live/angel_index_ai_pnl_log.csv

Real master dataset (if exists): storage/learning/angel_index_real_master_dataset.parquet (optional)

10.2. Outputs (Ultra Shadow)

Shadow master dataset:
storage/learning_ultra/angel_ultra_shadow_master.parquet
storage/learning_ultra/angel_ultra_shadow_master.csv

Content:

One row per option leg instance with columns such as:

underlying

strike

side

ts

ltp

spot

signal

pred_label

score

confidence

sl_price, tp_price

exit_reason

pnl_pct

is_win (1/0)

is_loss (1/0)

is_misfire (signal vs outcome mismatch)

profile_source (e.g. "BASELINE")

10.3. Menu Entry

Add a new menu option (append after existing ones, do not renumber old ones):

In run_system3.py, add:

48) Ultra Shadow Data Engine (build shadow master dataset)


Mapped to:

python -m core.engine.ultra_shadow_data_engine

10.4. Cursor Agent – Task 10

Create core/engine/ultra_shadow_data_engine.py with:

build_shadow_master() function:

Load signals, trades, PnL (if exist).

Join them into a consolidated DataFrame.

Compute the extra columns (is_win, is_loss, is_misfire).

Save to both CSV and Parquet in storage/learning_ultra/.

main() function:

Print counts:

rows of signals

rows of trades

rows of PnL

final shadow rows

Save files.

Print success messages.

Wire option 48 in run_system3.py to call this main.

Do not modify existing Phase 7 master dataset module.

10.5. Validation – Commands & Expected

Command:

python -m core.engine.ultra_shadow_data_engine


Expected console:

Some lines like:

=== Ultra Shadow Data Engine ===
Loaded signals: 930
Loaded trade plans: 3
Loaded PnL log: 3
Final shadow rows: 3
[SAVE] shadow master CSV: storage/learning_ultra/angel_ultra_shadow_master.csv
[SAVE] shadow master PARQUET: storage/learning_ultra/angel_ultra_shadow_master.parquet


Files:

dir storage\learning_ultra\angel_ultra_shadow_master.*

Phase 11 – Ultra Feature Expander (50 → ~100 Features)

Goal: extend features for Ultra models only (shadow), not baseline.

New module:

core/engine/ultra_feature_engineering.py

11.1. Inputs

Synthetic + real/blended training (baseline version):

storage/training/angel_index_options_training.csv (synthetic)

storage/learning_ultra/angel_ultra_shadow_master.parquet (Phase 10)

11.2. Outputs

Ultra training dataset with extended features:

storage/training/angel_ultra_training.parquet

storage/training/angel_ultra_training.csv

11.3. Features (Examples)

Extend baseline 25+ features to ~100 by adding:

Multi–timeframe momentum: 1, 3, 5, 10 steps

Short / long volatility windows

Moneyness powers: squared, cube

Interaction features (moneyness × score, etc.)

Regime tags (high/low volatility flags)

Rolling hit rates per underlying (from shadow dataset)

Time of day features (slot encoding)

Exact implementation details can be internal; key requirement: do not reduce existing baseline features.

11.4. Menu Entry

Add:

49) Ultra Feature Expander (build ultra training set)

→ python -m core.engine.ultra_feature_engineering

11.5. Cursor Agent – Task 11

Create ultra_feature_engineering.py with:

build_ultra_training_dataset():

Load synthetic training CSV.

Load shadow master (Phase 10).

Merge/align columns.

Add extended features (new columns with prefix, e.g. u_ or ultra_).

Save as Parquet + CSV.

main() to print:

total rows (synthetic + shadow)

number of features

number of ultra-only features

Wire menu option 49 in run_system3.py.

Do not touch baseline training builder.

11.6. Validation

Command:

python -m core.engine.ultra_feature_engineering


Expected:

A summary like:

=== Ultra Feature Expander ===
Synthetic rows: 3000
Shadow rows: 3
Combined ultra rows: 3003
Base features: 25
Ultra extra features: 60
Total features: 85
[SAVE] Ultra training: storage/training/angel_ultra_training.parquet


File check:

dir storage\training\angel_ultra_training.*

Phase 12 – Shadow Model Trainer V3 (Ultra Models)

Goal: train Ultra shadow models separate from baseline.

New module:

core/engine/ultra_train_models.py

12.1. Inputs

Ultra training dataset:

storage/training/angel_ultra_training.parquet

12.2. Outputs

Ultra models (RF/XGB/Ensemble could be used, but separate):

Directory: core/models/angel_one_ultra/

Files per underlying, e.g.:

NIFTY_ultra_model.pkl

NIFTY_ultra_model_meta.json

etc. for all 5 underlyings.

12.3. Menu Entry

50) Train Ultra Shadow Models

→ python -m core.engine.ultra_train_models

12.4. Cursor Agent – Task 12

Create ultra_train_models.py with:

train_ultra_models():

Load ultra training dataset.

Split per underlying.

Train at least one strong model (RandomForest / XGBoost).

Log accuracy, precision/recall/f1.

Save models + meta into core/models/angel_one_ultra/.

main() that prints a summary like baseline training.

Use different filenames from baseline models to avoid overwrite.

12.5. Validation

Command:

python -m core.engine.ultra_train_models


Expected:

=== Ultra Shadow Model Training ===
[ULTRA TRAIN] NIFTY: samples=..., accuracy=...
...
[SAVE] NIFTY_ultra_model.pkl
...
=== ULTRA SUMMARY: ===
NIFTY: ...
BANKNIFTY: ...
...


File check:

dir core\models\angel_one_ultra

Phase 13 – Hyperparameter Space Explorer

Goal: offline hyperparameter exploration for Ultra models.

New module:

core/engine/ultra_hparam_explorer.py

13.1. Functionality

Uses storage/training/angel_ultra_training.parquet.

For each underlying:

Try multiple hyperparameter sets (small grid or random search).

Evaluate on validation split.

Save results in:

storage/reports_ultra/ultra_hparam_results_{underlying}.csv

No model overwrites; just report.

13.2. Menu Entry

51) Ultra Hyperparameter Explorer (report only)

13.3. Cursor Agent – Task 13

Implement run_explorer() in ultra_hparam_explorer.py.

Ensure no model file is written.

Write CSV reports with columns: underlying, model_type, params_json, accuracy, f1, timestamp.

13.4. Validation

Command:

python -m core.engine.ultra_hparam_explorer


Expect:

Console lines indicating tested combos.

CSV files created in storage/reports_ultra\.

Phase 14 – Risk Regime Model Splitter

Goal: classify regimes (low/medium/high volatility, trending vs ranging) and prepare concept for different Ultra models per regime.

New module:

core/engine/ultra_regime_classifier.py

14.1. Outputs

Regime labels added to ultra training data (not overwriting original):

storage/training/angel_ultra_training_with_regime.parquet

Regime distribution report:

storage/reports_ultra/ultra_regime_summary.csv

14.2. Menu Entry

52) Ultra Risk Regime Classifier (labels + report)

14.3. Cursor Agent – Task 14

Create ultra_regime_classifier.py:

label_regimes():

Load ultra training dataset.

Classify regime per row (e.g., based on volatility, momentum).

Add regime_label such as "LOW_VOL", "HIGH_VOL", "TREND_UP", "RANGE".

Save new Parquet file.

Generate summary counts per underlying + regime.

Do not train models here.

14.4. Validation

Command:

python -m core.engine.ultra_regime_classifier


Expect:

Print counts of each regime.

Report file created.

Phase 15 – Multi-Consensus Engine (Shadow)

Goal: combine predictions from multiple Ultra models & baseline model for analysis.

New module:

core/engine/ultra_multi_consensus.py

15.1. Inputs

Baseline models in core/models/angel_one/.

Ultra models in core/models/angel_one_ultra/.

Sample signals or shadow dataset snapshots.

15.2. Outputs

Consensus report:

storage/reports_ultra/ultra_consensus_sample.csv

Columns example:

underlying, strike, side, baseline_pred, ultra_pred, agree_flag, baseline_conf, ultra_conf, final_shadow_recommendation

15.3. Menu Entry

53) Ultra Multi-Consensus Analyzer (shadow)

15.4. Cursor Agent – Task 15

Implement:

run_consensus_sample():

Load a small sample from ultra training/shadow dataset.

Run baseline + ultra models.

Compare predictions.

Save CSV + print stats (agreement %, where ultra differs, etc).

Ensure no trade plan is generated here; this is analysis only.

15.5. Validation

Command:

python -m core.engine.ultra_multi_consensus


Expect:

Console summarizing agreement rate.

CSV report in storage/reports_ultra.

Phase 16 – Ultra Threshold Lab V2 (Shadow Only)

Goal: experiment thresholds on shadow PnL without changing real configs.

New module:

core/engine/ultra_threshold_lab.py

16.1. Inputs

Ultra shadow master dataset (Phase 10).

Possibly PnL logs for synthetic outcomes.

16.2. Outputs

Threshold experiment report:

storage/reports_ultra/ultra_threshold_grid_search.csv

16.3. Menu Entry

54) Ultra Threshold Lab (shadow analysis)

16.4. Cursor Agent – Task 16

Implement grid-search-like evaluation of different (conf_thresh, score_thresh) against is_win in shadow dataset.

Write results with columns:

underlying, conf_thresh, score_thresh, trades, win_rate, avg_pnl, sharpe_like, comment.

Do not change angel_trade_config.py or thresholds file.

16.5. Validation

Command:

python -m core.engine.ultra_threshold_lab


Expect:

CSV with multiple threshold combos per underlying.

Phase 17 – Ultra Prediction Engine (Shadow Live)

Goal: run Ultra models in parallel (shadow) with baseline signals for comparison.

New module:

core/engine/ultra_live_signals_shadow.py

17.1. Behavior

Reads latest snapshot (same _build_full_snapshot used by baseline).

For each leg:

Get baseline prediction (optional).

Get ultra prediction.

Print table with side-by-side predictions (shadow only).

Save results to:

storage/ultra/angel_ultra_live_shadow_signals.csv

17.2. Menu Entry

55) Ultra Live Signals (shadow, no trades)

17.3. Cursor Agent – Task 17

Implement run_ultra_live_shadow_once():

Single snapshot.

Optional: loop version with --loop argument (but default once).

Ensure:

No trade planning

No executor calls

Only write CSV & console.

17.4. Validation

Command:

python -m core.engine.ultra_live_signals_shadow


Expect:

A snapshot printout with baseline vs ultra columns.

CSV file created.

Phase 18 – Ultra Trade Simulator (Shadow, Offline)

Goal: simulate Ultra-only trades on historical snapshots, offline.

New module:

core/engine/ultra_trade_simulator.py

18.1. Inputs

Historical signals / snapshots.

Ultra models.

18.2. Outputs

Simulated trade plans (shadow only):

storage/ultra/angel_ultra_trade_plan_sim.csv

PnL log:

storage/ultra/angel_ultra_pnl_sim.csv

Summary report:

storage/reports_ultra/ultra_trade_sim_summary.csv

18.3. Menu Entry

56) Ultra Trade Simulator (shadow only)

18.4. Cursor Agent – Task 18

Implement:

Generate candidate trades using Ultra predictions + some threshold.

Simulate exits using future ltp from logs.

Compute PnL and summary.

DO NOT call actual executor or modify real trade plan.

18.5. Validation

Command:

python -m core.engine.ultra_trade_simulator


Expect:

Trades count summary.

Win-rate / avg PnL in summary CSV.

Phase 19 – Ultra PnL Analyzer

Goal: advanced analysis of Ultra simulator PnL.

New module:

core/engine/ultra_pnl_analyzer.py

19.1. Inputs

storage/ultra/angel_ultra_pnl_sim.csv

19.2. Outputs

Per-underlying PnL breakdown.

Time-of-day performance.

Drawdown curve stats.

Files:

storage/reports_ultra/ultra_pnl_report.csv

Optional charts / extended CSVs.

19.3. Menu Entry

57) Ultra PnL Analyzer (shadow only)

19.4. Cursor Agent – Task 19

Implement analysis of PnL simulation results.

Produce clear summary rows.

19.5. Validation

Command:

python -m core.engine.ultra_pnl_analyzer


Expect:

Console summary of trades, win%, avg PnL, max drawdown.

Phase 20 – Ultra Promotion System (Compare & Promote)

Goal: side-by-side comparison of Baseline vs Ultra models, and manual promotion only.

New module:

core/engine/ultra_promotion_manager.py

20.1. Capabilities

Display metrics:

Baseline vs Ultra:

training accuracy

shadow sim win rate

avg PnL

drawdown

If user types a strong explicit command, copy Ultra model to baseline directory.

20.2. Safety Rules

MUST respect safety switches:

If AUTO_PROMOTE_MODELS is False → disable auto promotion; only allow manual typed promotions.

Promotion command must be explicit, like:

PROMOTE_NIFTY

PROMOTE_BANKNIFTY

etc.

Print confirmation before copying.

20.3. Menu Entry

58) Ultra Promotion Manager (manual only)

20.4. Cursor Agent – Task 20

Implement:

show_comparison():

Read baseline & Ultra meta + reports.

Show side-by-side table.

interactive_promote():

Ask: "Type PROMOTE_NIFTY to copy Ultra NIFTY model to baseline, or ENTER to cancel: "

On correct text:

Check safety file: if AUTO_PROMOTE_MODELS is false:

still OK to manually promote, but log it clearly.

Copy core/models/angel_one_ultra/NIFTY_ultra_model.pkl → core/models/angel_one/NIFTY_model.pkl (or whichever baseline name is used).

Create log entry in e.g. storage/reports_ultra/ultra_promotion_log.txt.

Do not allow promotion without explicit typed keyword.

20.5. Validation

Command:

python -m core.engine.ultra_promotion_manager


Expect:

A comparison table printed.

If you just press ENTER at prompt, no file is copied.

If (later) you test promotion with keyword, then:

Model file should be replaced, and a promotion log should be written.

FINAL CHECKLIST (WHAT I WANT TO SEE FROM AGENT / SYSTEM AFTER PHASE 10–20)

When all phases are implemented, ideal verification outputs:

Directory structure

core/models/angel_one_ultra contains Ultra models.

storage/ultra, storage/learning_ultra, storage/reports_ultra populated with shadow data, sim and analysis.

Safety

core/config/system3_ultra_safety.json exists, all flags false.

No unexpected auto trades / auto config changes.

Menus

run_system3.py shows options 48–58 appended (no renumbering of old options).

Key commands run successfully

python -m core.engine.ultra_shadow_data_engine

python -m core.engine.ultra_feature_engineering

python -m core.engine.ultra_train_models

python -m core.engine.ultra_hparam_explorer

python -m core.engine.ultra_regime_classifier

python -m core.engine.ultra_multi_consensus

python -m core.engine.ultra_threshold_lab

python -m core.engine.ultra_live_signals_shadow

python -m core.engine.ultra_trade_simulator

python -m core.engine.ultra_pnl_analyzer

python -m core.engine.ultra_promotion_manager

Each should print a clear header and finish without errors.

Baseline untouched

Baseline models & configs still exist and work with existing menu options.

Ultra work is fully shadowed and controlled.