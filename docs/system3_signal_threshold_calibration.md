## System3 Signal Threshold Calibration – DRY-RUN Utilities

### 1. New-day prep script

- **File**: `system3_prep_for_new_day.py`
- **Purpose**:
  - Archives the current live signals CSV:
    - From `storage/live/angel_index_ai_signals.csv`
    - To `storage/live/archive/angel_index_ai_signals_YYYYMMDD_HHMMSS_before_new_day.csv`
  - Prepares the system for a fresh DRY-RUN day without mixing old scores.

**Example usage**:

```bash
cd C:\Genesis_System3
python system3_prep_for_new_day.py
```

The script prints whether the CSV was found and, if so, the source and archived destination paths.

### 2. Threshold calibrator

- **File**: `core/engine/scoring_engine/threshold_calibrator.py`
- **Function**: `suggest_thresholds_from_history(csv_path, lookback_rows=2000, buy_quantile=0.85, sell_quantile=0.15)`

**Behavior**:

- Reads up to the last `lookback_rows` rows from a signals CSV.
- Uses the distribution of `final_score` (or `expected_move_score` if needed) to compute:
  - `raw_buy = quantile(buy_quantile)`
  - `raw_sell = quantile(sell_quantile)`
- Clamps both to the `[-1.0, +1.0]` range and returns:

```python
{
  "buy": float,
  "sell": float,
  "rows_used": int,
  "raw_buy": float | None,
  "raw_sell": float | None,
  "reason": str,
}
```

If not enough data is available or the CSV cannot be read, it falls back to defaults:
`buy = 0.40`, `sell = -0.40`.

### 3. Signal test mode with auto-thresholds

- **File**: `system3_signal_test_mode.py`
- **Purpose**:
  - Offline DRY-RUN analysis of recent signals from `storage/live/angel_index_ai_signals.csv`.
  - Optional auto-thresholds based on historical `final_score`.

**Key CLI options**:

- `--lookback-snapshots` (int, default 20):
  - Approximate number of recent snapshots to analyse (used as row lookback in calibration).
- `--auto-thresholds`:
  - When set, uses `suggest_thresholds_from_history` to calibrate BUY/SELL thresholds for analysis.

**Flow when `--auto-thresholds` is used**:

1. Loads and filters recent rows from `storage/live/angel_index_ai_signals.csv`.
2. Calls `suggest_thresholds_from_history` with:

   ```python
   csv_path = ROOT_DIR / "storage" / "live" / "angel_index_ai_signals.csv"
   calib = suggest_thresholds_from_history(csv_path, lookback_rows=lookback_snapshots)
   ```

3. Prints a summary, for example (example output):

```text
[AUTO-THRESHOLDS] rows_used=600, raw_buy=0.43, raw_sell=-0.38, buy=0.43, sell=-0.38, reason=ok
```

4. Recomputes `signal` locally using these thresholds:
   - `BUY` if `final_score > buy`
   - `SELL` if `final_score < sell`
   - `HOLD` otherwise
5. Prints final BUY/SELL/HOLD counts and top candidates for this analysis only (no CSV updates).

### 4. End-to-end DRY-RUN workflow (example)

#### 1) Prep for a new day (archives old CSV)

```bash
cd C:\Genesis_System3
python system3_prep_for_new_day.py
```

#### 2) Run DRY-RUN autopilot during market hours

```bash
system3_live_day_autopilot.bat
```

Let this run long enough to collect new live signals in `storage/live/angel_index_ai_signals.csv`.

#### 3) After some data is collected, run test mode with auto-thresholds

```bash
python system3_signal_test_mode.py --lookback-snapshots 200 --auto-thresholds
```

**Example (fabricated) output**:

```text
[AUTO-THRESHOLDS] rows_used=600, raw_buy=0.43, raw_sell=-0.38, buy=0.43, sell=-0.38, reason=ok

=== SCORE DISTRIBUTIONS ===
final_score      : min=-0.812, max= 0.921, mean= 0.037, std= 0.271
trend_score      : min=-0.742, max= 0.801, mean= 0.012, std= 0.233
volatility_score : min=-0.554, max= 0.672, mean= 0.018, std= 0.197
momentum_score   : min=-0.631, max= 0.689, mean= 0.021, std= 0.205
ai_score         : min=-0.903, max= 0.887, mean= 0.004, std= 0.312

=== SIGNAL COUNTS (analysis) ===
BUY: 24
SELL: 18
HOLD: 158
```

> **Note**: The numbers above are illustrative only, not from your live system.


