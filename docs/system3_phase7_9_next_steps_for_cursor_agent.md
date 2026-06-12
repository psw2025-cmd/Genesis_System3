System3 – Phase 7–9 Next Steps (for Cursor Agent)
Context

Baseline System3 (81+ modules, 47 menu options) is frozen in Safe Mode.

All Phase 1–6 modules (Real-Market Prep, Real Learning Cycle, Conservative Orchestration, Post-Monday Optimization, Ultra Safety & Intelligence, Ultra Observability) are documented and claimed as implemented.

Auto-execution, auto-update, and Ultra-Mode are disabled; everything is DRY-RUN and additive.

Next steps must:

Respect the baseline freeze (no destructive edits to existing engine modules, models, or configs).

Be additive: new modules, new configs, new reports.

Push System3 towards real-data learning and retraining, not just more synthetic logic.

Keep safety first: no real trades, no auto-changes to thresholds or configs.

The plan is broken into three new phases:

Phase 7 – Real-Data Dataset Consolidation

Phase 8 – Real-Data / Blended Model Training Lane

Phase 9 – Live-Mode Beta Track (but still DRY RUN)

For each phase:

Part A: What Cursor agent must implement (files, functions, structure).

Part B: What I want Pritam to run and share as verification.

Phase 7 – Real-Data Dataset Consolidation
Goal

Create a single, canonical “master dataset” for training and analysis that combines:

Live signals

Trade plans

PnL outcomes

Real outcome logs

into a clean, versioned dataset.

This will be the base for Phase 8 retraining.

Phase 7 – Agent Tasks (Code & Files)

New Engine Module: Real Master Dataset Builder

File: core/engine/dhan_real_master_dataset.py

Mode: READ/WRITE, but only into /storage/learning/ (no changes to training CSV used by baseline).

Responsibilities:

Read the following (if they exist):

storage/live/dhan_index_ai_signals.csv

storage/live/dhan_index_ai_trades_plan.csv

storage/live/dhan_index_ai_pnl_log.csv

storage/learning/real_outcomes/*.csv (if Real Outcome Logger already writes per-day files)

Join them into a row-per-trade dataset with columns such as:

ts_entry, ts_exit

underlying, expiry, strike, side

signal_label, pred_label, true_label (if available)

confidence, score

entry_ltp, exit_ltp

pnl_pct, exit_reason

market_regime, vol_regime (if available from volatility/regime modules)

Output:

Master Parquet:
storage/learning/dhan_index_real_master_dataset.parquet

Master CSV:
storage/learning/dhan_index_real_master_dataset.csv

Handle missing files gracefully:

If some inputs are missing, log a warning and still build whatever partial dataset is possible.

New Menu Option: Build Real Master Dataset

File to update: run_system3.py

Add a menu option, e.g.:

Option 48 – Build Real Master Dataset

When selected:

Call a main() function in dhan_real_master_dataset.py that:

Logs which source files were found.

Logs number of trades and rows written to the master dataset.

Writes both CSV + Parquet.

Basic Checks inside the module

Ensure:

No changes to existing training CSV:
storage/training/dhan_index_options_training.csv

No deletion of any existing logs.

All new outputs are restricted to storage/learning/.

Phase 7 – What I Want Pritam To Run & Share

After Cursor agent finishes Phase 7:

Activate venv and run:

(venv) PS C:\Genesis_System3> python run_system3.py


Choose the new menu option 48 – “Build Real Master Dataset”.

Then run:

(venv) PS C:\Genesis_System3> python -m core.engine.dhan_real_master_dataset


(if there is a standalone main() in that module; if menu already calls it, just the menu run is enough.)

Share back in chat:

The console output from:

menu 48 run

direct module run (if any)

A brief dir listing:

(venv) PS C:\Genesis_System3> dir storage\learning


Optional: first 10 lines of the CSV:

(venv) PS C:\Genesis_System3> python -c "import pandas as pd; df=pd.read_csv(r'storage\learning\dhan_index_real_master_dataset.csv'); print(df.head(10).to_string())"


I will use this to confirm:

Schema is as expected.

There are no crashes when some logs are missing.

The dataset is suitable for training.

Phase 8 – Real / Blended Model Training Lane
Goal

Introduce a separate “real/blended” model lane that uses:

Synthetic training data (baseline)

Real master dataset from Phase 7

to create new models without touching the frozen baseline models.

Baseline models must remain untouched in:

core/models/dhan/*.pkl (existing files)

All new models should be saved into new directories / filenames.

Phase 8 – Agent Tasks (Code & Files)

New Engine Module: Blended Training V3

File: core/engine/dhan_blended_training_v3.py

Responsibilities:

Read:

Baseline synthetic training CSV:
storage/training/dhan_index_options_training.csv

Real master dataset:
storage/learning/dhan_index_real_master_dataset.parquet
(fallback to CSV if parquet missing)

For each underlying:

Combine rows:

Synthetic subset (e.g., up to N rows per underlying, configurable)

Real rows (full or capped, configurable)

Construct feature matrix using the same feature set as current models:

Use same feature engineering pipeline already documented (moneyness, atm_dist, ce_pe_ratio, etc.).

Train new models with a clear naming convention, e.g.:

Path: core/models/dhan_real_blended/

Filenames: NIFTY_model_blended_v3.pkl, etc.

Save meta JSON:

Example: NIFTY_model_blended_v3_meta.json
with fields: training_data_sources, num_real_rows, num_synth_rows, train_date, metrics.

No overwrite of baseline models

Ensure module never writes to:

core/models/dhan/NIFTY_model.pkl or similar.

Only writes new files in a dedicated directory:

core/models/dhan_real_blended/

New Menu Option: Blended Retrain (V3)

File: run_system3.py

Add a new option, e.g.:

Option 49 – Train Real+Synthetic Blended Models (V3)

When selected:

Call main() in dhan_blended_training_v3.py.

Print:

Number of rows used per underlying.

Accuracy / F1 on validation split.

Paths of saved .pkl and .json files.

Optional config file

New file: storage/config/dhan_blended_training_v3_config.json

Fields:

max_synthetic_rows_per_underlying

max_real_rows_per_underlying

validation_split

If file missing, use safe defaults and log a warning.

Phase 8 – What I Want Pritam To Run & Share

After Cursor agent completes Phase 8:

Run:

(venv) PS C:\Genesis_System3> python run_system3.py


Choose menu 49 – Train Real+Synthetic Blended Models (V3).

Share back in chat:

The full console output of the blended training:

Per underlying: rows used, accuracy, F1, save paths.

A dir listing of the new model directory:

(venv) PS C:\Genesis_System3> dir core\models\dhan_real_blended


Optional (if easy): the content of one meta file, e.g.:

(venv) PS C:\Genesis_System3> type core\models\dhan_real_blended\NIFTY_model_blended_v3_meta.json


I will validate:

That new models are additive, not overwriting baseline.

That real rows are actually used.

That accuracy is reasonable and metrics are recorded.

Phase 9 – Live-Mode Beta Track (DRY RUN ONLY)
Goal

Prepare a separate Live-Mode Beta configuration that:

Uses blended models (from Phase 8) for inference.

Remains DRY RUN and fully safe.

Can be toggled via config without modifying baseline behavior.

No real trade execution; still only logs trade plans and simulated results.

Phase 9 – Agent Tasks (Code & Files)

New Config: Live Beta Profile

File: storage/config/system3_live_beta_profile.json

Content (example fields):

enabled: false (default)

use_blended_models: true

max_trades_per_day: 10

max_trades_per_underlying: 3

execution_mode: "DRY_RUN_ONLY"

min_confidence: 0.75 (slightly lower than production 0.80)

min_score: 0.25

All fields are read-only hints; no auto-write, only read.

New Engine Adapter: Model Selector

File: core/engine/dhan_model_selector.py

Responsibilities:

Read system3_live_beta_profile.json.

For each underlying:

If use_blended_models and blended file exists:

Load *_model_blended_v3.pkl (real+synthetic).

Else:

Fall back to baseline *_model.pkl.

Expose helper function(s), e.g.:

load_models_for_profile(profile_name: str) -> Dict[str, Any]

profiles: "BASELINE", "LIVE_BETA"

Integrate model selector into LIVE AI signals (non-destructive)

File: core/engine/dhan_live_ai_signals.py

Add a non-default path:

Default behavior (current baseline) unchanged.

If an optional flag/profile is set (e.g., via environment variable or small config flag), use dhan_model_selector to load models:

"BASELINE" vs "LIVE_BETA".

Important:

Do not change the default Monday behavior.

Only allow Live Beta profile via:

Command-line argument or

Small config flag in a safe JSON, disabled by default.

New Menu Option: Show Live Profiles & Active Profile

File: run_system3.py

Add a menu option, e.g.:

50 – Show Live Profiles & Model Sources

When selected:

Print:

Active profile: "BASELINE" or "LIVE_BETA".

For each underlying:

Which model file is loaded (*_model.pkl or *_model_blended_v3.pkl).

Which thresholds are in effect (from config).

Phase 9 – What I Want Pritam To Run & Share

After Cursor agent completes Phase 9:

Run menu:

(venv) PS C:\Genesis_System3> python run_system3.py


First, keep everything default (so profile should be BASELINE).

Choose menu 50 – Show Live Profiles & Model Sources.

Share the output: it should show BASELINE + baseline model files.

Prepare for a controlled Live Beta test (still DRY RUN):

Manually edit storage/config/system3_live_beta_profile.json:

Set "enabled": true.

Run menu 50 again and share output:

It should now show LIVE_BETA profile and model paths pointing to *_model_blended_v3.pkl.

Optional: run a single snapshot of live signals under LIVE_BETA profile:

(venv) PS C:\Genesis_System3> python -m core.engine.dhan_live_ai_signals


(if there is a way to set profile via env/config; Cursor agent must document that in the module docstring.)

Share:

First 20–30 lines of the AI SIGNALS SNAPSHOT under LIVE_BETA profile.

I will confirm:

That switching profiles does not break anything.

That LIVE_BETA is still DRY RUN.

That models are correctly swapped between baseline and blended, without overwrite.

Final Notes to Cursor Agent

Do not modify or overwrite:

Existing engine modules listed in baseline freeze docs.

Existing model files in core/models/dhan/.

Existing configs that control Monday behavior.

All new logic must be:

Additive.

Clearly separated by filenames and directories.

Guarded by configs (default = safe/baseline mode).

For every new module, include:

if __name__ == "__main__": main() entrypoint.

A short docstring explaining:

Purpose.

Inputs (files used).

Outputs (files written).

Any environment/config flags.

If you paste this MD into a new file and give it to the Cursor agent, it can follow these phases.

After each phase (7, 8, 9), follow the “What I want Pritam to run & share” section and send me those outputs; I will then confirm correctness and suggest any further tuning.