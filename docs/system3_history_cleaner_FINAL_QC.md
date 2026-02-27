## System3 History Cleaner – Final QC Summary

### Files and modules involved

- **New module**: `core/tools/system3_history_cleaner.py`
  - Functions:
    - `get_header_and_width(path: str) -> tuple[list[str], int]`
    - `clean_csv_file(path: str, backup: bool = True) -> dict`
    - `clean_all_history_files() -> list[dict]`
  - Logs to: `logs/system3_history_cleaner_YYYYMMDD.log`

- **Updated script**: `system3_prep_for_new_day.py`
  - Now imports and calls `clean_all_history_files()` via
    `run_history_cleanup_phase()`.
  - Order of operations:
    1. Archive previous `storage/live/angel_index_ai_signals.csv`.
    2. **History cleanup phase** – clean malformed rows in:
       - `storage/live/angel_index_ai_signals.csv`
       - All `*.csv` under `storage/live/archive/`
    3. Optional curated training export from recent archives.
  - Logs to: `logs/system3_prep_for_new_day_YYYYMMDD.log`

### What the cleaner does

For each CSV:

- Reads the header and determines the expected column count.
- Streams through the file with `csv.reader`:
  - **Keeps**: header row and any data row where `len(row) == expected_width`.
  - **Drops**: any row with the wrong number of columns (e.g. the old “line 32”
    issue where the C‑parser saw 75 fields instead of 72).
- Backs up the original as `*.bak` and overwrites the CSV with the cleaned
  content.
- Returns and logs a summary:

```text
path=... | status=cleaned | total=<rows> | kept=<rows> | dropped=<rows> | width=<expected_width>
```

### Expected cleaning behaviour

- **Live file**: `storage/live/angel_index_ai_signals.csv`
- **Archived files**: `storage/live/archive/*.csv`

For both the current live file and at least one archived file (containing the
old malformed “line 32”), the cleaner will report `dropped_rows >= 1`, removing
those structurally invalid rows permanently.

### Post‑cleanup validation (what to run)

From `C:\Genesis_System3` in the venv:

1. **Run daily prep with cleanup**:

   ```bash
   python system3_prep_for_new_day.py
   ```

   - Check `logs/system3_prep_for_new_day_YYYYMMDD.log` for:
     - Archive summary of the previous `angel_index_ai_signals.csv`.
     - `=== HISTORY CLEANUP PHASE: CLEANING MALFORMED ROWS ===` with per‑file
       summaries and non‑zero `dropped_rows` where malformed rows existed.

2. **Inspect training data**:

   ```bash
   python system3_inspect_training_data.py
   ```

   - Expected:
     - No CSV tokenizing errors (training loader uses cleaned files).
     - A valid row count (may be slightly lower than before cleanup).
     - Class distribution may still be all `HOLD` for now (this is a data/label
       issue, not structural).

3. **Run signal test‑mode**:

   ```bash
   python system3_signal_test_mode.py --lookback-snapshots 200 --auto-thresholds
   ```

   - Expected:
     - No warnings about malformed lines being skipped.
     - Normal summary of score distributions and BUY/SELL/HOLD counts.

### Final notes

- The history cleaner is **fully DRY‑RUN safe**: it only touches CSV history
  files, never any live trading flags or execution modules.
- With this in place, System3 now has a **stable, self‑cleaning training data
  pipeline**:
  - Malformed legacy rows are removed once via the cleaner.
  - Future days start from a clean file (via `system3_prep_for_new_day.py`).
  - ML training and test‑mode scripts operate on structurally valid CSVs.


