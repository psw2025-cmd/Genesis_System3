# Cursor Agent - Batch 4 Implementation Instructions

## Mode: Micro-Instruction Format

Each module below includes:
- Exact file path
- Function signatures
- Code structure
- Expected outputs
- Validation checks

---

## BATCH 4 - MODULE A: Live Market Intelligence Layer

### A1. Real-Time Volatility Detection

**File**: `core/engine/dhan_volatility_detector.py`

**Functions to implement**:
```python
def detect_volatility_regime(df_signals: pd.DataFrame, window: int = 5) -> pd.DataFrame
def compute_volatility_shock(spot_series: pd.Series, threshold: float = 2.0) -> bool
def classify_volatility_state(df: pd.DataFrame) -> str  # Returns: "LOW", "NORMAL", "HIGH", "EXTREME"
```

**Expected Output**:
- DataFrame with columns: `volatility_regime`, `vol_shock_flag`, `vol_state`
- Console: `[VOL] Detected {regime} volatility regime`

**Validation**:
- Check window >= 3
- Verify spot_series is numeric
- Ensure output DataFrame has same length as input

---

### A2. Microtrend Recognition

**File**: `core/engine/dhan_microtrend_recognizer.py`

**Functions to implement**:
```python
def detect_microtrend(df_signals: pd.DataFrame, lookback: int = 3) -> pd.DataFrame
def compute_trend_strength(price_series: pd.Series) -> float  # Returns 0.0 to 1.0
def classify_trend_direction(df: pd.DataFrame) -> str  # Returns: "UP", "DOWN", "SIDEWAYS"
```

**Expected Output**:
- DataFrame with columns: `microtrend`, `trend_strength`, `trend_direction`
- Console: `[TREND] Detected {direction} trend, strength={strength:.2f}`

**Validation**:
- Verify lookback >= 2
- Check price_series has sufficient data
- Ensure trend_strength in [0.0, 1.0]

---

### A3. Breakout Prediction Engine

**File**: `core/engine/dhan_breakout_predictor.py`

**Functions to implement**:
```python
def predict_breakout(df_signals: pd.DataFrame, resistance: float, support: float) -> Dict[str, Any]
def compute_breakout_probability(price: float, resistance: float, support: float, volatility: float) -> float
def detect_breakout_signal(df: pd.DataFrame) -> pd.DataFrame
```

**Expected Output**:
- Dict with: `breakout_probability`, `breakout_direction`, `breakout_signal`
- DataFrame with column: `breakout_signal` (values: "UP", "DOWN", "NONE")

**Validation**:
- Verify resistance > support
- Check probability in [0.0, 1.0]
- Ensure signal values are valid

---

### A4. Synthetic IV Estimator Refinement

**File**: `core/engine/dhan_iv_estimator.py`

**Functions to implement**:
```python
def estimate_synthetic_iv(ltp: float, spot: float, strike: float, time_to_expiry: float, option_type: str) -> float
def refine_iv_estimate(df_signals: pd.DataFrame) -> pd.DataFrame
def compute_iv_rank(iv: float, iv_history: pd.Series) -> float  # Returns percentile rank
```

**Expected Output**:
- DataFrame with columns: `synthetic_iv`, `iv_rank`, `iv_percentile`
- Console: `[IV] Estimated IV={iv:.2f}%, rank={rank:.1f}%`

**Validation**:
- Verify all inputs are positive
- Check IV in reasonable range [0.01, 5.0]
- Ensure rank in [0.0, 100.0]

---

### A5. Risk-Event Scanner

**File**: `core/engine/dhan_risk_event_scanner.py`

**Functions to implement**:
```python
def scan_risk_events(df_signals: pd.DataFrame, threshold_pct: float = 1.0) -> pd.DataFrame
def detect_big_move(spot_change_pct: float, threshold: float) -> bool
def classify_risk_level(df: pd.DataFrame) -> str  # Returns: "LOW", "MEDIUM", "HIGH", "CRITICAL"
```

**Expected Output**:
- DataFrame with columns: `risk_event_flag`, `risk_level`, `big_move_detected`
- Console: `[RISK] Risk level: {level}, big move: {detected}`

**Validation**:
- Check threshold > 0
- Verify risk_level in valid set
- Ensure boolean flags are correct type

---

## BATCH 4 - MODULE B: ACTION Layer (Pre-LIVE Mode)

### B1. Trade Lifecycle Validator V2

**File**: `core/engine/dhan_trade_validator_v2.py`

**Functions to implement**:
```python
def validate_trade_lifecycle(trade_id: str, lifecycle_log: pd.DataFrame) -> Dict[str, Any]
def check_lifecycle_completeness(events: List[str]) -> bool
def detect_lifecycle_anomalies(trade_row: pd.Series) -> List[str]
```

**Expected Output**:
- Dict with: `valid`, `missing_events`, `anomalies`, `completeness_score`
- Console: `[VALIDATOR V2] Trade {id}: {valid}, completeness={score:.2f}`

**Validation**:
- Verify trade_id exists
- Check events list is not empty
- Ensure completeness_score in [0.0, 1.0]

---

### B2. Entry Optimizer

**File**: `core/engine/dhan_entry_optimizer.py`

**Functions to implement**:
```python
def optimize_entry_timing(df_signals: pd.DataFrame, lookback: int = 5) -> pd.DataFrame
def compute_optimal_entry_price(current_price: float, bid: float, ask: float) -> float
def suggest_entry_strategy(signal_row: pd.Series) -> str  # Returns: "MARKET", "LIMIT", "WAIT"
```

**Expected Output**:
- DataFrame with columns: `optimal_entry_price`, `entry_strategy`, `entry_timing_score`
- Console: `[ENTRY] Optimal entry: {price:.2f}, strategy: {strategy}`

**Validation**:
- Verify ask >= bid
- Check entry_price in [bid, ask] range
- Ensure strategy in valid set

---

### B3. Exit Optimizer

**File**: `core/engine/dhan_exit_optimizer.py`

**Functions to implement**:
```python
def optimize_exit_timing(trade_row: pd.Series, current_pnl: float, target: float, sl: float) -> Dict[str, Any]
def compute_trailing_stop(current_price: float, entry_price: float, trailing_pct: float) -> float
def suggest_exit_strategy(trade_data: Dict[str, Any]) -> str  # Returns: "HOLD", "TAKE_PROFIT", "STOP_LOSS", "TRAILING"
```

**Expected Output**:
- Dict with: `exit_strategy`, `exit_price`, `trailing_stop_price`, `exit_timing`
- Console: `[EXIT] Strategy: {strategy}, price: {price:.2f}`

**Validation**:
- Verify current_pnl is numeric
- Check exit_price > 0
- Ensure strategy in valid set

---

### B4. Dynamic SL/TP Engine

**File**: `core/engine/dhan_dynamic_sl_tp.py`

**Functions to implement**:
```python
def compute_dynamic_sl_tp(entry_price: float, volatility: float, atr: float, risk_reward: float = 2.0) -> Dict[str, float]
def adjust_sl_tp_dynamically(trade_row: pd.Series, market_data: pd.DataFrame) -> Dict[str, float]
def compute_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series
```

**Expected Output**:
- Dict with: `dynamic_sl`, `dynamic_tp`, `atr_value`, `adjustment_reason`
- Console: `[DYNAMIC] SL={sl:.2f}, TP={tp:.2f}, ATR={atr:.2f}`

**Validation**:
- Verify risk_reward >= 1.0
- Check SL < entry_price < TP (for long)
- Ensure ATR > 0

---

### B5. Confidence-Score Fusion Layer

**File**: `core/engine/dhan_confidence_score_fusion.py`

**Functions to implement**:
```python
def fuse_confidence_score(confidence: float, score: float, weights: Dict[str, float]) -> float
def compute_fusion_rank(df_signals: pd.DataFrame) -> pd.DataFrame
def normalize_fusion_scores(scores: pd.Series) -> pd.Series
```

**Expected Output**:
- DataFrame with columns: `fused_score`, `fusion_rank`, `normalized_fusion`
- Console: `[FUSION] Fused score: {score:.3f}, rank: {rank}`

**Validation**:
- Verify weights sum to 1.0
- Check fused_score in reasonable range
- Ensure rank is integer

---

### B6. Multi-Model Agreement Filter

**File**: `core/engine/dhan_multi_model_agreement.py`

**Functions to implement**:
```python
def check_model_agreement(predictions: List[str], confidences: List[float]) -> Dict[str, Any]
def compute_agreement_score(predictions: List[str]) -> float
def filter_by_agreement(df_signals: pd.DataFrame, min_agreement: float = 0.7) -> pd.DataFrame
```

**Expected Output**:
- Dict with: `agreement_score`, `agreed_prediction`, `agreement_level`
- DataFrame filtered to high-agreement signals only
- Console: `[AGREEMENT] Score: {score:.2f}, level: {level}`

**Validation**:
- Verify predictions list not empty
- Check agreement_score in [0.0, 1.0]
- Ensure min_agreement in [0.0, 1.0]

---

## BATCH 4 - MODULE C: Market-Profile Layer

### C1. Multi-Timeframe Profile Mapping

**File**: `core/engine/dhan_market_profile.py`

**Functions to implement**:
```python
def build_timeframe_profile(df_signals: pd.DataFrame, timeframe_min: int) -> pd.DataFrame
def compute_profile_levels(df: pd.DataFrame, num_levels: int = 5) -> Dict[str, List[float]]
def classify_price_location(price: float, profile_levels: Dict[str, List[float]]) -> str
```

**Expected Output**:
- DataFrame with columns: `profile_1min`, `profile_3min`, `profile_5min`, `price_location`
- Dict with: `support_levels`, `resistance_levels`, `poc_level` (Point of Control)
- Console: `[PROFILE] Price location: {location}, POC: {poc:.2f}`

**Validation**:
- Verify timeframe_min in [1, 5, 15, 30]
- Check profile_levels dict has required keys
- Ensure price_location in valid set

---

### C2. Premium-to-Spot Behavior Classifier

**File**: `core/engine/dhan_premium_spot_classifier.py`

**Functions to implement**:
```python
def classify_premium_spot_behavior(ltp: float, spot: float, strike: float, moneyness: float) -> str
def compute_premium_spot_correlation(df_signals: pd.DataFrame, window: int = 5) -> float
def detect_premium_spot_divergence(df: pd.DataFrame) -> pd.DataFrame
```

**Expected Output**:
- DataFrame with columns: `premium_spot_behavior`, `correlation`, `divergence_flag`
- Behavior values: "NORMAL", "PREMIUM_LEADING", "SPOT_LEADING", "DIVERGENT"
- Console: `[BEHAVIOR] Classification: {behavior}, correlation: {corr:.3f}`

**Validation**:
- Verify correlation in [-1.0, 1.0]
- Check behavior in valid set
- Ensure divergence_flag is boolean

---

### C3. Multi-Timeframe Confirmation Logic

**File**: `core/engine/dhan_multi_timeframe_confirmation.py`

**Functions to implement**:
```python
def check_multi_timeframe_confirmation(df_signals: pd.DataFrame, timeframes: List[int]) -> pd.DataFrame
def compute_confirmation_score(signals_by_timeframe: Dict[int, str]) -> float
def filter_confirmed_signals(df: pd.DataFrame, min_confirmation: float = 0.6) -> pd.DataFrame
```

**Expected Output**:
- DataFrame with columns: `confirmation_score`, `confirmed_signal`, `timeframe_agreement`
- Console: `[CONFIRMATION] Score: {score:.2f}, confirmed: {confirmed}`

**Validation**:
- Verify timeframes list not empty
- Check confirmation_score in [0.0, 1.0]
- Ensure confirmed_signal is boolean

---

## BATCH 4 - MODULE D: Safety Layer V2

### D1. Over-Trade Detector

**File**: `core/engine/dhan_overtrade_detector.py`

**Functions to implement**:
```python
def detect_overtrading(exec_log: pd.DataFrame, time_window_min: int = 60) -> Dict[str, Any]
def compute_trade_frequency(trades: pd.DataFrame, window: int) -> float
def check_overtrade_risk(underlying: str, recent_trades: int, limit: int) -> bool
```

**Expected Output**:
- Dict with: `is_overtrading`, `trade_frequency`, `risk_level`, `recommendation`
- Console: `[OVERTRADE] Risk: {risk}, frequency: {freq:.2f} trades/hour`

**Validation**:
- Verify time_window_min > 0
- Check trade_frequency >= 0
- Ensure risk_level in valid set

---

### D2. Signal Quality Meter

**File**: `core/engine/dhan_signal_quality_meter.py`

**Functions to implement**:
```python
def measure_signal_quality(signal_row: pd.Series) -> Dict[str, Any]
def compute_quality_score(confidence: float, score: float, moneyness: float, volatility: float) -> float
def classify_quality_level(quality_score: float) -> str  # Returns: "POOR", "FAIR", "GOOD", "EXCELLENT"
```

**Expected Output**:
- Dict with: `quality_score`, `quality_level`, `quality_factors`, `recommendation`
- Console: `[QUALITY] Score: {score:.2f}, level: {level}`

**Validation**:
- Verify quality_score in [0.0, 1.0]
- Check quality_level in valid set
- Ensure all factors are numeric

---

### D3. Execution Guardrail

**File**: `core/engine/dhan_execution_guardrail.py`

**Functions to implement**:
```python
def validate_execution_request(trade_row: pd.Series, current_market: pd.DataFrame) -> Dict[str, Any]
def check_price_slippage(entry_price: float, current_price: float, max_slippage_pct: float = 2.0) -> bool
def enforce_execution_limits(underlying: str, daily_count: int, limit: int) -> bool
```

**Expected Output**:
- Dict with: `execution_allowed`, `validation_checks`, `slippage_check`, `limit_check`
- Console: `[GUARDRAIL] Execution: {allowed}, slippage: {slippage:.2f}%`

**Validation**:
- Verify max_slippage_pct > 0
- Check execution_allowed is boolean
- Ensure all checks are boolean

---

### D4. Market Regime Classifier

**File**: `core/engine/dhan_market_regime_classifier.py`

**Functions to implement**:
```python
def classify_market_regime(df_signals: pd.DataFrame) -> str
def compute_regime_features(spot_series: pd.Series, vol_series: pd.Series) -> Dict[str, float]
def adjust_strategy_for_regime(regime: str, current_strategy: Dict[str, Any]) -> Dict[str, Any]
```

**Expected Output**:
- String: "TRENDING_UP", "TRENDING_DOWN", "RANGING", "VOLATILE", "CALM"
- Dict with: `regime_features`, `strategy_adjustments`
- Console: `[REGIME] Current regime: {regime}, adjustments: {adjustments}`

**Validation**:
- Verify regime in valid set
- Check regime_features dict has required keys
- Ensure strategy_adjustments is dict

---

## INTEGRATION INSTRUCTIONS

### Wire into Menu
**File**: `run_system3.py`

**Add menu options**:
- 24: Market Intelligence Dashboard
- 25: ACTION Layer Validator
- 26: Market Profile Analyzer
- 27: Safety Layer V2 Check

**Handler pattern**:
```python
elif choice == "24":
    from core.engine.dhan_market_intelligence_dashboard import main as market_intel_main
    market_intel_main()
```

---

## VALIDATION CHECKLIST

For each module:
- [ ] File created at exact path
- [ ] All functions implemented with exact signatures
- [ ] Expected outputs match specification
- [ ] Console logs match format
- [ ] Validation checks pass
- [ ] Integrated into menu (if applicable)
- [ ] No linter errors
- [ ] Tested with sample data

---

**Status**: Ready for Cursor Agent implementation
**Mode**: Micro-instruction format active

