## System3 Signal Engine Upgrade – Summary

### Files changed

- `core/engine/ai_model/ml_predictor.py`
- `core/engine/system3_signal_engine.py`
- `core/engine/scoring_engine/signal_scorer.py` (weights / thresholds already in place)
- `system3_signal_test_mode.py` (new, root)
- `system3_signal_test_mode.bat` (new, root)

### ML predictor (`ml_predictor.py`)

- **Features used** (training and prediction):
  - Base: `delta, gamma, theta, vega, rsi, macd, macd_histogram, iv_percentile, iv_rank, volatility_score, breakout_score, momentum_score, trend_score, multi_tf_trend_score`.
  - New derived: `moneyness` from `spot` and `strike`, `time_to_expiry` from `expiry` vs `ts`.
- **Training logic**:
  - Filters to recent history using `ts` and `days_back`.
  - Builds target as forward `%` change in `spot`, ignoring very small moves (`abs(change) < 0.0005`).
  - Requires at least **50** samples; otherwise training is skipped and the caller falls back to delta-based `ai_score`.
  - Uses XGBoost or RandomForest with moderate depth and `class_weight="balanced"` where available.
- **Diagnostics**:
  - Logs class distribution via `Counter(y)`.
  - Logs top feature importances when `feature_importances_` is available.
  - Writes a structured diagnostics file under `logs/ml_diagnostics/ml_train_YYYYMMDD_HHMMSS.log` with:
    - Timestamp, sample count, class counts, top feature importances.
- **Prediction path**:
  - Uses the extended feature set (`moneyness`, `time_to_expiry` included).
  - If all probabilities are identical across rows, falls back to a delta-based `ai_score` (scaled to ±0.3).
  - Otherwise maps `ml_probability` into `ai_score` with a modest scale and clips to `[-1, +1]`.

### Signal engine (`system3_signal_engine.py`)

- **Short-history loader**:
  - `load_recent_signal_history(SIGNALS_CSV, max_rows=5000)` reads the last up to 5000 rows from `storage/live/dhan_index_ai_signals.csv`, parses timestamps if present, and returns a DataFrame or `None`.
- **Short-history feature computation**:
  - `compute_short_history_features(history_df, snapshot_df, min_history_points=5)`:
    - Groups `history_df` by `(underlying, strike, side)`.
    - For each group with enough points, uses the last up to 20 rows to compute:
      - `short_return = (last_price / first_price) - 1`, bounded via `tanh`.
      - `short_vol = std(returns)` scaled to a 0–2 range and clipped.
      - `short_momentum = last_step_price_diff`, scaled relative to price and passed through `tanh`.
    - Attaches `short_return`, `short_vol`, `short_momentum` to the current snapshot rows keyed by `(underlying, strike, side)`.
- **Integration into component scores**:
  - At the start of `process_snapshot`, after ensuring required columns, the snapshot is enriched:
    - `hist_df = load_recent_signal_history(SIGNALS_CSV, max_rows=5000)`
    - `df = compute_short_history_features(hist_df, df, min_history_points=5)`
  - **Trend score**:
    - Base from moneyness: `(spot - strike) / strike`, inverted for PE, clipped to `[-1, +1]`.
    - Blends base with `short_return` when available: `trend_score = 0.5 * base + 0.5 * short_return`.
    - `multi_tf_trend_score` and an RSI proxy (`rsi`) are derived from `trend_score`.
  - **Volatility score**:
    - Uses existing IV features via `compute_volatility_features` and `detect_volatility_regime`.
    - If still near zero, combines:
      - `vol_from_iv` from `iv_percentile`.
      - `vol_from_hist` from `short_vol` scaled into 0–1.
    - Result stored in `volatility_score`, clipped to `[-1, +1]`.
  - **Momentum score**:
    - Base from option time value (`ltp - intrinsic`) mapped to `[-1, +1]`.
    - Blends base with `short_momentum` when available: `momentum_score = 0.5 * base + 0.5 * short_momentum`, clipped to `[-1, +1]`.

### Scoring & thresholds (`signal_scorer.py`)

- **Weights**:
  - `greeks_score`: 0.20  
  - `trend_score`: 0.20  
  - `volatility_score`: 0.15  
  - `breakout_score`: 0.15  
  - `momentum_score`: 0.15  
  - `ai_score`: 0.15  
- **Thresholds**:
  - Base: `buy_threshold = 0.40`, `sell_threshold = -0.40`.
  - Dynamic per-row adjustment using `iv_rank` when present:
    - `factor = 0.8 + 0.4 * (iv_rank / 100.0)` (0.8x to 1.2x).
    - Per-row thresholds: `buy_thr_row = buy_threshold * factor`, `sell_thr_row = sell_threshold * factor`.
- Signals are generated using these adjusted thresholds, and `signal_strength` is based on `|final_score|`.

### Test mode (`system3_signal_test_mode.py`)

- **Purpose**:
  - DRY-RUN analysis of recent signals from `storage/live/dhan_index_ai_signals.csv` with no trading or broker interaction.
- **CLI options**:
  - `--lookback-snapshots` (int, default 20): approximate number of recent snapshots to examine.
  - `--underlyings` (string, default `NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY,SENSEX`): comma-separated list.
- **Behavior**:
  - Loads the signals CSV, sorts by timestamp (`ts`) when available, and tails approximately `lookback_snapshots * 100` rows.
  - Filters by requested underlyings.
  - Prints to console:
    - Score distributions for `final_score`, `greeks_score`, `trend_score`, `volatility_score`, `momentum_score`, `breakout_score`, `ai_score` (when present).
    - BUY/SELL/HOLD counts based on the `signal` column.
    - Top 5 BUY candidates (by descending `final_score`) and top 5 SELL candidates (by ascending `final_score`), including key fields such as `ts`, `underlying`, `strike`, `side`, `ltp`, `spot`, and component scores when available.
- **Logging**:
  - Writes a brief summary to `logs/signal_test_mode_YYYYMMDD_HHMM.log`:
    - Timestamp, lookback, underlyings, row count, and signal counts (if available).
- **Safety**:
  - Script is strictly read-only; does not touch any live trading flags or execution modules.

### How to run

- **Live DRY-RUN session (existing)**:
  - `system3_live_day_autopilot.bat`
  - This runs pre-market checks, live Dhan DRY-RUN loop, intraday monitors, and EOD wrap-up.
- **Signal test mode (new)**:
  - `system3_signal_test_mode.bat`
    - Activates `venv` and runs `python system3_signal_test_mode.py --lookback-snapshots 30`.
  - Or directly:
    - `python system3_signal_test_mode.py --lookback-snapshots 30`

Running a short live session followed by test mode should now show:

- Non-zero distributions for `trend_score`, `volatility_score`, and `momentum_score` on instruments with recent movement.
- `ai_score` that varies across instruments and snapshots (no longer a uniform value).
- Explicit BUY/SELL/HOLD counts and, when present, top BUY/SELL candidates.


