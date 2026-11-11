## System3 Training Data Pipeline & QC

This document describes how the System3 training data pipeline works after the
“training data hygiene” upgrade, and how to validate that it is production‑grade
for DRY‑RUN ML training.

### Data sources

- **Live history (raw)**: `storage/live/dhan_index_ai_signals.csv`
- **Archived days**: `storage/live/archive/*.csv`
- **Curated training dataset**: `storage/live/dhan_index_ai_signals_curated.csv`

The live engine (`system3_live_day_autopilot.py`) appends rows to
`dhan_index_ai_signals.csv` throughout the day. At the start of a new day,
`system3_prep_for_new_day.py` archives the previous file and (optionally)
builds a curated training dataset from recent archives.

### Robust loader: `load_training_data`

Location: `core/engine/ai_model/ml_predictor.py`

Function: `load_training_data(path: Path, min_samples: int) -> Optional[pd.DataFrame]`

Behavior:

- **Step 1 – fast parser**
  - Tries `pd.read_csv(path)` with the default C‑engine.
  - If it succeeds and `rows >= MIN_TRAINING_SAMPLES` (default 200):
    - Logs a message and returns the DataFrame.
  - If rows are too few, logs a warning and returns `None`.
- **Step 2 – robust parser (on failure)**
  - On any tokenizing/parsing error, retries with:
    - `engine="python"`
    - `on_bad_lines="skip"`
  - If it succeeds and `rows >= MIN_TRAINING_SAMPLES`:
    - Logs that some malformed lines were skipped and returns the DataFrame.
  - If still too few rows or another failure occurs, logs a warning and returns `None`.
- **Never raises** to callers; always returns either a valid DataFrame or `None`.

Diagnostics:

- Writes to both the main System3 logger and a dedicated loader log:
  - `logs/model_diagnostics/system3_training_data_loader_YYYYMMDD.log`
- Logs include:
  - File path.
  - Parser used (fast vs robust).
  - Row counts.
  - Warnings when training is skipped.

### Training source priority: curated > live

Location: `core/engine/ai_model/ml_predictor.py`

Constants:

- `CURATED_TRAINING_PATH = "storage/live/dhan_index_ai_signals_curated.csv"`
- `LIVE_TRAINING_PATH    = "storage/live/dhan_index_ai_signals.csv"`

Helper: `get_training_dataframe(prefer_curated: bool = True) -> Optional[pd.DataFrame]`

Priority logic:

1. If the **curated** file exists:
   - Call `load_training_data(CURATED_TRAINING_PATH)`.
   - If successful, log “Training ML model from curated history...” and return it.
   - If it fails or returns `None`, log a warning and fall back to the live CSV.
2. If the curated file is not usable, try the **live** CSV:
   - Call `load_training_data(LIVE_TRAINING_PATH)`.
   - If successful, log “Training ML model from live history...” and return it.
3. If both sources fail, log that no valid training data is available and return `None`.

The System3 signal engine (`core/engine/system3_signal_engine.py`) uses
`get_training_dataframe()` to obtain training history before calling
`train_ml_model(...)`. If `None` is returned, it uses a **delta‑based ai_score
fallback** and continues safely.

### Daily prep: archiving & curated dataset

Location: `system3_prep_for_new_day.py`

Responsibilities:

1. **Archive previous live history**
   - If `storage/live/dhan_index_ai_signals.csv` exists, it is moved to:
     - `storage/live/archive/dhan_index_ai_signals_YYYYMMDD_HHMMSS_before_new_day.csv`
   - Row count is estimated (with robust parsing) and logged.
2. **Optional curated export (enabled by default)**
   - Controlled by `ENABLE_CURATED_EXPORT = True` and `CURATED_LOOKBACK_DAYS`.
   - Scans `storage/live/archive/` for recent `dhan_index_ai_signals_*.csv` files.
   - Uses robust parsing (`engine="python", on_bad_lines="skip"`) to read each.
   - Concatenates them into a single DataFrame and drops rows missing
     essential columns (`ts`, `spot`, `underlying` when present).
   - Writes the result to:
     - `storage/live/dhan_index_ai_signals_curated.csv`
   - Logs the number of rows before/after cleaning, and the final curated row count.

Logging:

- Daily prep logs are written to:
  - `logs/system3_prep_for_new_day_YYYYMMDD.log`

### Training data inspector: `system3_inspect_training_data.py`

Script: `system3_inspect_training_data.py` (repo root)

Usage:

```bash
python system3_inspect_training_data.py
```

Behavior:

- Tries to load the **curated** CSV first (via `load_training_data`).
- If curated is unavailable/invalid, falls back to the **live** CSV.
- If both fail, prints a clear error and exits.
- On success, prints:
  - Path used (curated vs live).
  - Total row count.
  - Basic class distribution based on one of:
    - `direction`, `pred_label`, or `signal` (first one found).
  - Number and list of distinct `underlying` values.
  - A warning if row count is below `MIN_SAMPLES_WARNING` (default 200).

### QC checklist for operators

For each new DRY‑RUN day:

1. **Before market**
   - Run:
     - `python system3_prep_for_new_day.py`
   - Verify in the console + log that:
     - Yesterday’s `dhan_index_ai_signals.csv` was archived.
     - (Optional) A curated training dataset was built with a non‑zero row count.
2. **After some live history exists (mid‑day or EOD)**
   - Run:
     - `python system3_inspect_training_data.py`
   - Check:
     - Training data is loading without CSV tokenizing errors.
     - Row count is comfortably above the minimum (200+ rows).
     - Class distribution looks reasonable (not all in a single class).
3. **Model training during live run**
   - In `logs/model_diagnostics/system3_training_data_loader_YYYYMMDD.log`, confirm:
     - Training data is being loaded from curated or live history.
     - Fallback parser is used only occasionally (or never) once history is clean.

This pipeline keeps ML training **robust, DRY‑RUN‑only, and production‑grade** by
ensuring malformed CSV lines do not crash the model and by separating clean,
curated training history from the raw live signal log.


