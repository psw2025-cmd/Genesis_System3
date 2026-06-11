# PHASE 389-400: PRODUCTION-GRADE ML & SCORE PIPELINE UPGRADE

**Status:** READY FOR IMPLEMENTATION  
**Prerequisites:** Phases 381-388 (Ultra Models Integration) COMPLETE  
**Mode:** DRY-RUN ONLY (No live trading)  
**Python:** venv 3.10.11 @ `C:/Genesis_System3/venv/Scripts/python.exe`  
**Date:** December 8, 2025

---

## EXECUTIVE SUMMARY

### Mission
Upgrade System3's ML scoring pipeline from delta-based fallback (66.7% win rate) to production-grade ensemble ML (target 80-85% accuracy) through feature engineering, SMOTE balancing, XGBoost training, ensemble logic, and auto-retraining.

### Current State Analysis
- **Phase 381-388:** Ultra Models integrated (5/5 loadable, 100% smoke tests passed)
- **Current ML Status:** `train_ml_model()` returns None due to class imbalance and low feature variance
- **Current Fallback:** Delta-based scoring (66.7% win rate, 30% signal strength)
- **System Health:** 120 signals/3min, 28 approved orders, 0 errors, stable end-to-end
- **Limitation:** ML potential capped by data quality, not model sophistication

### Why Phase 389-400 Now?
1. Ultra Models (381-388) provide baseline pre-trained models
2. System stable and ready for advanced ML
3. Delta fallback working but performance-limited
4. Feature variance too low (80% zeros in current data)
5. Class imbalance unsolved (46% HOLD, 29% SELL, 24% BUY)
6. No ensemble logic or auto-retraining

### Expected Outcomes
- **Accuracy:** 60-70% immediately (beats 66.7% baseline), 80-85% after retraining cycles
- **Win Rate:** +10-20 percentage points improvement
- **Signal Quality:** Higher confidence scores, better risk-adjusted returns
- **Adaptability:** Self-improving system that learns from every trade
- **Production-Ready:** Full telemetry, drift detection, auto-retraining

---

## PHASE ARCHITECTURE

### Block 1: Data Quality & Feature Engineering (389-390)
**Purpose:** Solve low variance and class imbalance issues

```
Phase 389: Feature Engineering Upgrade
├─ Add 40+ high-variance features
├─ Greeks momentum, IV regimes, OI changes
├─ Multi-timeframe aggregates
└─ Output: Enhanced feature set

Phase 390: SMOTE Data Balancing
├─ Balance BUY/SELL/HOLD classes
├─ Generate synthetic training samples
├─ Stratified sampling
└─ Output: Balanced training dataset
```

### Block 2: Advanced Model Training (391-392)
**Purpose:** Train XGBoost and create ensemble

```
Phase 391: XGBoost Model Training
├─ Train per-underlying XGBoost models
├─ Hyperparameter optimization
├─ Validation on held-out test set
└─ Output: 5 XGBoost models (60-70% accuracy)

Phase 392: Ultra + ML + Delta Ensemble
├─ Weighted voting system
├─ Ultra Model (40%), XGBoost (40%), Delta (20%)
├─ Confidence-based routing
└─ Output: Ensemble predictor
```

### Block 3: Score Processing & Learning (393-394)
**Purpose:** Normalize scores and learn from outcomes

```
Phase 393: Score Normalization Engine
├─ Min-max scaling
├─ Z-score normalization
├─ Sorenson similarity
└─ Output: Stable probability scores

Phase 394: Real PnL Outcome Learning
├─ Extract outcomes from pnl_log.csv
├─ Weight real trades 3x synthetic
├─ Continuous learning loop
└─ Output: Updated models from real data
```

### Block 4: Production Infrastructure (395-397)
**Purpose:** Drift detection, auto-retraining, dynamic risk

```
Phase 395: Drift Detector Upgrade
├─ Statistical drift detection
├─ Regime change detection
├─ Auto-trigger retraining
└─ Output: Drift alerts & retrain triggers

Phase 396: Daily Auto-Retraining Engine
├─ EOD batch retraining
├─ Merge new trades
├─ Update ensemble models
└─ Output: Self-improving ML system

Phase 397: Probability-Based Risk Controller
├─ Dynamic thresholds per underlying
├─ NIFTY: 0.10, BANKNIFTY: 0.12, FINNIFTY: 0.15
├─ Confidence-based order approval
└─ Output: Smarter risk management
```

### Block 5: Validation & Monitoring (398-400)
**Purpose:** Validate ensemble and generate production readiness report

```
Phase 398: Paper Trading Validation Loop
├─ 30-snapshot live test
├─ Compare Ultra vs XGBoost vs Ensemble
├─ Win rate analysis
└─ Output: Performance comparison report

Phase 399: Scoring Telemetry v2.0
├─ 20+ metrics per signal
├─ Model usage tracking
├─ Score distribution analysis
└─ Output: Enhanced telemetry JSON

Phase 400: Production-Readiness Report
├─ ML accuracy summary
├─ Drift status
├─ Ensemble health
└─ Output: Go/No-Go decision
```

---

## DETAILED PHASE SPECIFICATIONS

### PHASE 389: Feature Engineering Upgrade

**File:** `core/engine/ai_model/feature_engineering_v2.py` (NEW)

**Purpose:** Add 40+ high-variance features to solve low feature variance issue (current: 80% zeros)

**Features to Add:**

#### 1. Greeks Momentum (8 features)
```python
# Delta momentum
df['delta_momentum_5'] = df['delta'].rolling(5).mean().diff()
df['delta_momentum_10'] = df['delta'].rolling(10).mean().diff()

# Gamma acceleration
df['gamma_acceleration'] = df['gamma'].rolling(5).mean().diff()

# Theta decay rate
df['theta_decay_rate'] = df['theta'].diff()

# Vega sensitivity
df['vega_change'] = df['vega'].diff()

# Greeks cross-products
df['delta_gamma_ratio'] = df['delta'] / (df['gamma'] + 1e-8)
df['vega_theta_ratio'] = df['vega'] / (abs(df['theta']) + 1e-8)
df['greeks_momentum_score'] = (
    df['delta_momentum_5'] + df['gamma_acceleration']
).clip(-1, 1)
```

#### 2. IV Regime Features (6 features)
```python
# IV percentiles
df['iv_percentile_75'] = df['iv'] > df['iv'].quantile(0.75)
df['iv_percentile_25'] = df['iv'] < df['iv'].quantile(0.25)
df['iv_regime_high'] = (df['iv'] > df['iv'].quantile(0.75)).astype(int)
df['iv_regime_low'] = (df['iv'] < df['iv'].quantile(0.25)).astype(int)

# IV change
df['iv_change'] = df['iv'].diff()
df['iv_acceleration'] = df['iv'].diff().diff()
```

#### 3. Price & Moneyness (8 features)
```python
# Moneyness
df['moneyness'] = df['strike'] / df['spot']
df['atm_distance'] = abs(df['strike'] - df['spot'])
df['atm_distance_pct'] = df['atm_distance'] / df['spot']

# Relative pricing
df['relative_price'] = df['ltp'] / df['strike']
df['price_momentum'] = df['ltp'].pct_change()
df['price_acceleration'] = df['ltp'].pct_change().diff()

# CE/PE spreads
ce_ltp = df[df['side'] == 'CE']['ltp'].mean()
pe_ltp = df[df['side'] == 'PE']['ltp'].mean()
df['ce_pe_spread'] = ce_ltp - pe_ltp
df['ce_pe_ratio'] = ce_ltp / (pe_ltp + 1e-8)
```

#### 4. Volume & OI Features (6 features)
```python
# Volume momentum
df['volume_momentum'] = df['volume'].pct_change()
df['volume_acceleration'] = df['volume'].pct_change().diff()

# OI momentum
df['oi_momentum'] = df['oi'].pct_change()
df['oi_acceleration'] = df['oi'].pct_change().diff()

# Volume-OI ratios
df['volume_oi_ratio'] = df['volume'] / (df['oi'] + 1e-8)
df['oi_buildup'] = (df['oi'].diff() > 0).astype(int)
```

#### 5. Time-Based Features (4 features)
```python
# Time to expiry
df['days_to_expiry'] = (pd.to_datetime(df['expiry']) - pd.to_datetime(df['ts'])).dt.days
df['time_decay_factor'] = 1.0 / (df['days_to_expiry'] + 1)
df['is_weekly_expiry'] = (df['days_to_expiry'] <= 7).astype(int)
df['is_monthly_expiry'] = (df['days_to_expiry'] > 7).astype(int)
```

#### 6. Multi-Timeframe Aggregates (8 features)
```python
# Rolling aggregates
for window in [5, 10, 20]:
    df[f'ltp_ma_{window}'] = df['ltp'].rolling(window).mean()
    df[f'volume_ma_{window}'] = df['volume'].rolling(window).mean()
    
# Trend strength
df['trend_strength_5'] = (df['ltp'] - df['ltp'].rolling(5).mean()) / df['ltp'].rolling(5).std()
df['trend_strength_10'] = (df['ltp'] - df['ltp'].rolling(10).mean()) / df['ltp'].rolling(10).std()
```

**Outputs:**
- `storage/metrics/feature_engineering_389.json` - Feature statistics
- `reports/FEATURE_ENGINEERING_389.md` - Feature importance analysis

**Success Criteria:**
- 40+ new features added
- Feature variance increased by 50%+
- Zero-valued features reduced from 80% to <30%

---

### PHASE 390: SMOTE Data Balancing

**File:** `core/engine/ai_model/smote_balancer.py` (NEW)

**Purpose:** Fix class imbalance (46% HOLD, 29% SELL, 24% BUY) using SMOTE

**Implementation:**

```python
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split

def balance_training_data_with_smote(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply SMOTE to balance BUY/SELL/HOLD classes.
    
    Current distribution:
    - BUY:  600 rows (24.8%)
    - SELL: 700 rows (29.0%)
    - HOLD: 1,116 rows (46.2%)
    
    Target distribution:
    - BUY:  ~1,000 rows (33%)
    - SELL: ~1,000 rows (33%)
    - HOLD: ~1,000 rows (33%)
    """
    # Extract features and labels
    feature_cols = [
        'delta', 'gamma', 'theta', 'vega', 'iv',
        'delta_momentum_5', 'gamma_acceleration', 'iv_change',
        'moneyness', 'atm_distance', 'volume_momentum', 'oi_momentum',
        'trend_strength_5', 'time_decay_factor'
        # ... all 40+ features
    ]
    
    X = df[feature_cols].fillna(0)
    y = df['signal'].map({'BUY': 1, 'SELL': -1, 'HOLD': 0})
    
    # Apply SMOTE
    smote = SMOTE(
        random_state=42,
        k_neighbors=5,
        sampling_strategy='auto'  # Balance to majority class
    )
    
    X_balanced, y_balanced = smote.fit_resample(X, y)
    
    # Create balanced dataframe
    df_balanced = pd.DataFrame(X_balanced, columns=feature_cols)
    df_balanced['signal'] = y_balanced.map({1: 'BUY', -1: 'SELL', 0: 'HOLD'})
    
    logger.info(f"SMOTE: {len(X)} → {len(X_balanced)} rows")
    logger.info(f"Class distribution: {df_balanced['signal'].value_counts().to_dict()}")
    
    return df_balanced
```

**Outputs:**
- `storage/datasets/smote_balanced_training_390.csv` - Balanced training data
- `storage/metrics/smote_balancing_390.json` - Before/after distribution
- `reports/SMOTE_BALANCING_390.md` - Balancing report

**Success Criteria:**
- All classes balanced to ~33% each
- Training data expanded from 2,416 to ~3,000+ rows
- No data leakage (SMOTE only on training set)

---

### PHASE 391: XGBoost Model Training

**File:** `core/engine/ai_model/xgboost_trainer.py` (NEW)

**Purpose:** Train XGBoost models per-underlying (better than RandomForest for imbalanced data)

**Implementation:**

```python
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score

def train_xgboost_per_underlying(
    df: pd.DataFrame,
    underlying: str,
    save_path: Path
) -> Optional[XGBClassifier]:
    """
    Train XGBoost model for specific underlying.
    
    Why XGBoost > RandomForest:
    - Handles class imbalance better (scale_pos_weight)
    - Built-in regularization (prevents overfitting)
    - Gradient boosting (learns from mistakes)
    - Better for sparse/tabular financial data
    """
    # Filter to underlying
    df_underlying = df[df['underlying'] == underlying].copy()
    
    if len(df_underlying) < 200:
        logger.warning(f"Insufficient data for {underlying}: {len(df_underlying)} rows")
        return None
    
    # Extract features and labels
    feature_cols = [col for col in df_underlying.columns 
                    if col not in ['signal', 'underlying', 'ts', 'expiry']]
    X = df_underlying[feature_cols].fillna(0)
    y = df_underlying['signal'].map({'BUY': 1, 'SELL': -1, 'HOLD': 0})
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
    
    # XGBoost with optimized hyperparameters
    model = XGBClassifier(
        n_estimators=200,           # More trees
        max_depth=5,                # Shallow (prevent overfit)
        learning_rate=0.05,         # Slow learning
        subsample=0.8,              # Row sampling
        colsample_bytree=0.8,       # Feature sampling
        scale_pos_weight=(y_train == 0).sum() / (y_train != 0).sum(),  # Handle imbalance
        reg_alpha=0.1,              # L1 regularization
        reg_lambda=1.0,             # L2 regularization
        random_state=42,
        eval_metric='mlogloss',
        use_label_encoder=False
    )
    
    # Train with early stopping
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        early_stopping_rounds=20,
        verbose=False
    )
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    logger.info(f"{underlying} XGBoost Accuracy: {accuracy:.3f}")
    logger.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")
    
    # Only save if accuracy > 55% (better than random)
    if accuracy > 0.55:
        model_path = save_path / f"{underlying}_xgboost_model.pkl"
        joblib.dump(model, model_path)
        logger.info(f"Saved XGBoost model: {model_path}")
        return model
    else:
        logger.warning(f"{underlying} accuracy too low ({accuracy:.3f}), not saving")
        return None
```

**Outputs:**
- `core/models/xgboost/NIFTY_xgboost_model.pkl` (and 4 others)
- `storage/metrics/xgboost_training_391.json` - Accuracy per underlying
- `reports/XGBOOST_TRAINING_391.md` - Training report with feature importances

**Success Criteria:**
- 5/5 XGBoost models trained (one per underlying)
- Average accuracy > 60% (beats 50% random, targets 70%)
- Feature importance analysis shows meaningful patterns

---

### PHASE 392: Ultra + ML + Delta Ensemble

**File:** `core/engine/ensemble_predictor.py` (NEW)

**Purpose:** Combine Ultra Models, XGBoost, and Delta fallback into weighted ensemble

**Implementation:**

```python
def predict_with_ensemble(
    df: pd.DataFrame,
    underlying: str,
    ultra_model: Any,
    xgboost_model: Any
) -> pd.DataFrame:
    """
    ENSEMBLE STRATEGY:
    1. Ultra Model (40% weight) - Pre-trained RandomForest
    2. XGBoost (40% weight) - Newly trained gradient boosting
    3. Delta Fallback (20% weight) - Always works
    
    Routing logic:
    - If Ultra Model confident (>0.7 prob) → Use Ultra
    - Else if XGBoost confident (>0.7 prob) → Use XGBoost
    - Else → Weighted average of all 3
    """
    scores = []
    confidences = []
    
    # Model 1: Ultra Model (RandomForest)
    try:
        ultra_pred = ultra_model.predict_proba(X)
        ultra_conf = ultra_pred.max(axis=1)
        ultra_score = ultra_pred[:, 1] - ultra_pred[:, 0]  # BUY prob - SELL prob
        
        scores.append(('ultra', ultra_score, 0.4))
        confidences.append(('ultra', ultra_conf.mean()))
        logger.info(f"Ultra model: confidence={ultra_conf.mean():.3f}")
    except Exception as e:
        logger.warning(f"Ultra model failed: {e}")
    
    # Model 2: XGBoost
    try:
        xgb_pred = xgboost_model.predict_proba(X)
        xgb_conf = xgb_pred.max(axis=1)
        xgb_score = xgb_pred[:, 1] - xgb_pred[:, 0]
        
        scores.append(('xgboost', xgb_score, 0.4))
        confidences.append(('xgboost', xgb_conf.mean()))
        logger.info(f"XGBoost model: confidence={xgb_conf.mean():.3f}")
    except Exception as e:
        logger.warning(f"XGBoost failed: {e}")
    
    # Model 3: Delta Fallback (always available)
    delta_score = compute_delta_scores(df)
    scores.append(('delta', delta_score, 0.2))
    confidences.append(('delta', 1.0))  # Always confident
    logger.info("Delta fallback active")
    
    # Confidence-based routing
    if len(confidences) >= 2:
        # Check if any model is highly confident
        for model_name, conf in confidences:
            if conf > 0.7 and model_name != 'delta':
                logger.info(f"Using {model_name} (high confidence: {conf:.3f})")
                # Use only this model
                model_scores = [s for name, s, w in scores if name == model_name][0]
                df['ai_score'] = model_scores.clip(-1.0, 1.0)
                df['ensemble_method'] = model_name
                return df
    
    # Weighted ensemble (no single model confident)
    ensemble_score = np.zeros(len(df))
    total_weight = sum(w for _, _, w in scores)
    
    for model_name, score_array, weight in scores:
        ensemble_score += (score_array * weight) / total_weight
    
    df['ai_score'] = ensemble_score.clip(-1.0, 1.0)
    df['ensemble_method'] = 'weighted_average'
    logger.info("Using weighted ensemble (no single confident model)")
    
    return df
```

**Integration into Signal Engine:**

```python
# In system3_signal_engine.py, modify Step 6 (AI Model Prediction):

# Try ensemble prediction
underlying = df["underlying"].iloc[0] if "underlying" in df.columns and len(df) > 0 else None

if underlying:
    # Load models
    ultra_model = load_ultra_model(underlying)
    xgboost_model = load_xgboost_model(underlying)
    
    if ultra_model or xgboost_model:
        df = predict_with_ensemble(df, underlying, ultra_model, xgboost_model)
        logger.info(f"USING_ENSEMBLE for {underlying} (method={df['ensemble_method'].iloc[0]})")
    else:
        # Pure delta fallback
        logger.info(f"USING_DELTA_FALLBACK for {underlying} (no models available)")
        df["ai_score"] = compute_delta_scores(df)
```

**Outputs:**
- `storage/metrics/ensemble_performance_392.json` - Model usage distribution
- `reports/ENSEMBLE_PERFORMANCE_392.md` - Ensemble analysis

**Success Criteria:**
- Ensemble accuracy > max(ultra, xgboost, delta) accuracies
- Confidence-based routing working (logs show method used)
- Graceful degradation to delta fallback

---

### PHASE 393: Score Normalization Engine

**File:** `core/engine/score_normalizer.py` (NEW)

**Purpose:** Normalize ensemble scores to stable probability distributions

**Implementation:**

```python
def normalize_scores(df: pd.DataFrame, method: str = 'minmax') -> pd.DataFrame:
    """
    Normalize ai_score to stable probability range.
    
    Methods:
    1. min-max: Scale to [0, 1]
    2. z-score: Standardize to mean=0, std=1
    3. sorenson: Sorenson similarity for probabilistic interpretation
    """
    if method == 'minmax':
        # Scale to [0, 1]
        score_min = df['ai_score'].min()
        score_max = df['ai_score'].max()
        df['ai_score_normalized'] = (
            (df['ai_score'] - score_min) / (score_max - score_min + 1e-8)
        )
    
    elif method == 'zscore':
        # Z-score normalization
        score_mean = df['ai_score'].mean()
        score_std = df['ai_score'].std()
        df['ai_score_normalized'] = (
            (df['ai_score'] - score_mean) / (score_std + 1e-8)
        ).clip(-3, 3) / 6 + 0.5  # Scale to [0, 1]
    
    elif method == 'sorenson':
        # Sorenson similarity (probabilistic)
        df['ai_score_normalized'] = (
            df['ai_score'] + 1.0
        ) / 2.0  # Map [-1, 1] to [0, 1]
    
    # Interpret as probabilities
    df['buy_probability'] = df['ai_score_normalized']
    df['sell_probability'] = 1 - df['ai_score_normalized']
    
    return df
```

**Outputs:**
- `storage/metrics/score_normalization_393.json` - Distribution statistics
- `reports/SCORE_NORMALIZATION_393.md` - Before/after analysis

**Success Criteria:**
- Scores distributed evenly across [0, 1] range
- BUY signals have buy_probability > 0.6
- SELL signals have sell_probability > 0.6

---

### PHASE 394: Real PnL Outcome Learning

**File:** `core/engine/pnl_outcome_learner.py` (NEW)

**Purpose:** Learn from real trading outcomes (solve "model has no profitable pattern data")

**Implementation:**

```python
def learn_from_real_pnl_outcomes(
    curated_df: pd.DataFrame,
    pnl_log_path: Path
) -> pd.DataFrame:
    """
    Extract real trade outcomes and merge into training data.
    
    Strategy:
    1. Load pnl_log.csv (real trades with outcomes)
    2. Match trades to curated signals
    3. Update labels based on profitability
    4. Weight real trades 3x synthetic
    """
    # Load PnL log
    pnl_df = pd.read_csv(pnl_log_path)
    
    # Extract profitable trades
    pnl_df['outcome'] = pnl_df['pnl_pct'].apply(
        lambda x: 'BUY' if x > 0 else 'SELL'
    )
    
    # Match to curated signals
    enhanced_df = curated_df.copy()
    enhanced_df['weight'] = 1.0  # Default weight
    
    for _, trade in pnl_df.iterrows():
        # Find matching signal
        match = enhanced_df[
            (enhanced_df['underlying'] == trade['underlying']) &
            (enhanced_df['strike'] == trade['strike']) &
            (enhanced_df['side'] == trade['side'])
        ].tail(1)
        
        if not match.empty:
            # Update label and weight
            enhanced_df.loc[match.index, 'signal'] = trade['outcome']
            enhanced_df.loc[match.index, 'weight'] = 3.0  # Real trades worth 3x
            
            logger.info(f"Updated signal for {trade['underlying']} {trade['strike']} "
                       f"{trade['side']} with outcome {trade['outcome']}")
    
    real_count = (enhanced_df['weight'] == 3.0).sum()
    logger.info(f"Learned from {real_count} real trades (weighted 3x)")
    
    return enhanced_df
```

**Outputs:**
- `storage/datasets/pnl_enhanced_training_394.csv` - Enhanced training data
- `storage/metrics/pnl_learning_394.json` - Real trades learned
- `reports/PNL_OUTCOME_LEARNING_394.md` - Learning analysis

**Success Criteria:**
- All real trades from pnl_log.csv incorporated
- Real trades weighted 3x synthetic
- Model accuracy improves after retraining with real outcomes

---

### PHASE 395: Drift Detector Upgrade

**File:** `core/engine/drift_detector_v2.py` (MODIFY existing phase 334 logic)

**Purpose:** Detect statistical drift and regime changes, trigger auto-retraining

**Implementation:**

```python
from scipy import stats

def detect_model_drift(
    recent_predictions: pd.DataFrame,
    baseline_predictions: pd.DataFrame,
    threshold: float = 0.05
) -> Dict[str, Any]:
    """
    Detect drift using Kolmogorov-Smirnov test.
    
    Drift types:
    1. Prediction drift: Score distribution changed
    2. Feature drift: Input features changed
    3. Performance drift: Accuracy dropped
    """
    drift_detected = False
    drift_details = {}
    
    # 1. Prediction drift (KS test on score distribution)
    ks_stat, p_value = stats.ks_2samp(
        recent_predictions['ai_score'],
        baseline_predictions['ai_score']
    )
    
    if p_value < threshold:
        drift_detected = True
        drift_details['prediction_drift'] = {
            'ks_statistic': ks_stat,
            'p_value': p_value,
            'severity': 'high' if p_value < 0.01 else 'medium'
        }
    
    # 2. Feature drift (compare feature distributions)
    feature_drifts = []
    for col in ['delta', 'gamma', 'theta', 'iv']:
        ks_stat, p_value = stats.ks_2samp(
            recent_predictions[col],
            baseline_predictions[col]
        )
        if p_value < threshold:
            feature_drifts.append(col)
    
    if feature_drifts:
        drift_detected = True
        drift_details['feature_drift'] = {
            'drifted_features': feature_drifts,
            'count': len(feature_drifts)
        }
    
    # 3. Performance drift (accuracy drop)
    if 'actual_outcome' in recent_predictions.columns:
        recent_accuracy = (
            recent_predictions['predicted'] == recent_predictions['actual_outcome']
        ).mean()
        baseline_accuracy = (
            baseline_predictions['predicted'] == baseline_predictions['actual_outcome']
        ).mean()
        
        if recent_accuracy < baseline_accuracy * 0.9:  # 10% drop
            drift_detected = True
            drift_details['performance_drift'] = {
                'recent_accuracy': recent_accuracy,
                'baseline_accuracy': baseline_accuracy,
                'drop_pct': (1 - recent_accuracy / baseline_accuracy) * 100
            }
    
    # Trigger retraining if drift detected
    if drift_detected:
        logger.warning(f"DRIFT DETECTED: {drift_details}")
        trigger_auto_retrain()
    
    return {
        'drift_detected': drift_detected,
        'details': drift_details,
        'timestamp': datetime.utcnow().isoformat()
    }
```

**Outputs:**
- `storage/metrics/drift_detection_395.json` - Drift status
- `reports/DRIFT_DETECTION_395.md` - Drift analysis
- Auto-trigger retraining when drift detected

**Success Criteria:**
- Drift detection functional (KS test, feature drift, performance drift)
- Auto-retraining triggered when drift > threshold
- False positive rate < 5%

---

### PHASE 396: Daily Auto-Retraining Engine

**File:** `core/engine/auto_retrain_scheduler.py` (NEW)

**Purpose:** EOD batch retraining pipeline (how top firms run production ML)

**Implementation:**

```python
def run_daily_auto_retrain():
    """
    Daily auto-retraining pipeline.
    
    Schedule: Every day at 18:00 IST (after market close)
    
    Steps:
    1. Load today's new trades
    2. Merge into training dataset
    3. Retrain all models (Ultra, XGBoost)
    4. Validate new models
    5. Deploy if validation passes
    6. Archive old models
    """
    logger.info("=" * 60)
    logger.info("DAILY AUTO-RETRAIN STARTED")
    logger.info("=" * 60)
    
    # Step 1: Load new trades
    pnl_log = load_pnl_log()
    last_retrain = load_last_retrain_timestamp()
    new_trades = pnl_log[pnl_log['ts'] > last_retrain]
    
    if len(new_trades) < 10:  # Minimum threshold
        logger.info(f"Insufficient new trades ({len(new_trades)}), skipping retrain")
        return
    
    logger.info(f"Found {len(new_trades)} new trades since last retrain")
    
    # Step 2: Merge into training dataset
    curated_df = load_curated_dataset()
    enhanced_df = learn_from_real_pnl_outcomes(curated_df, pnl_log)
    
    # Step 3: Retrain models
    for underlying in ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX']:
        logger.info(f"Retraining {underlying}...")
        
        # Retrain XGBoost
        xgb_model = train_xgboost_per_underlying(enhanced_df, underlying, MODELS_DIR)
        
        if xgb_model:
            # Validate on held-out test set
            validation_accuracy = validate_model(xgb_model, enhanced_df, underlying)
            
            # Deploy if accuracy > threshold
            if validation_accuracy > 0.55:
                deploy_model(xgb_model, underlying, 'xgboost')
                logger.info(f"✓ {underlying} XGBoost deployed (accuracy={validation_accuracy:.3f})")
            else:
                logger.warning(f"✗ {underlying} validation failed (accuracy={validation_accuracy:.3f})")
    
    # Step 4: Update retrain timestamp
    save_last_retrain_timestamp(datetime.utcnow())
    
    logger.info("=" * 60)
    logger.info("DAILY AUTO-RETRAIN COMPLETED")
    logger.info("=" * 60)
```

**Scheduler Integration:**

```python
# In tools/schedule_auto_retrain.py (NEW)

import schedule
import time

def schedule_daily_retrain():
    """
    Run auto-retraining every day at 18:00 IST.
    """
    schedule.every().day.at("18:00").do(run_daily_auto_retrain)
    
    logger.info("Auto-retrain scheduler started (daily at 18:00 IST)")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
```

**Outputs:**
- `storage/metrics/auto_retrain_396_{date}.json` - Daily retrain log
- `reports/AUTO_RETRAIN_396_{date}.md` - Retrain report
- `core/models/archive/` - Archived old models

**Success Criteria:**
- Daily retraining runs automatically at 18:00 IST
- Models improve over time (accuracy trending up)
- Old models archived (not deleted)

---

### PHASE 397: Probability-Based Risk Controller

**File:** `core/engine/risk_controller_v2.py` (MODIFY existing risk control logic)

**Purpose:** Dynamic thresholds per underlying (smarter than fixed 0.12)

**Implementation:**

```python
# Dynamic thresholds based on underlying volatility
DYNAMIC_THRESHOLDS = {
    'NIFTY': {
        'min_score': 0.10,          # Less volatile → lower threshold
        'confidence_threshold': 0.60,
        'max_quantity': 50
    },
    'BANKNIFTY': {
        'min_score': 0.12,          # More volatile → higher threshold
        'confidence_threshold': 0.65,
        'max_quantity': 40
    },
    'FINNIFTY': {
        'min_score': 0.15,          # Most volatile → highest threshold
        'confidence_threshold': 0.70,
        'max_quantity': 30
    },
    'MIDCPNIFTY': {
        'min_score': 0.13,
        'confidence_threshold': 0.65,
        'max_quantity': 35
    },
    'SENSEX': {
        'min_score': 0.10,
        'confidence_threshold': 0.60,
        'max_quantity': 45
    }
}

def apply_dynamic_risk_control(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply per-underlying risk thresholds.
    
    Logic:
    1. Check underlying-specific min_score
    2. Check model confidence
    3. Adjust quantity based on confidence
    """
    for idx, row in df.iterrows():
        underlying = row['underlying']
        score = row['ai_score']
        confidence = row.get('buy_probability', 0.5)
        
        # Get dynamic thresholds
        thresholds = DYNAMIC_THRESHOLDS.get(underlying, DYNAMIC_THRESHOLDS['NIFTY'])
        
        # Apply min score check
        if abs(score) < thresholds['min_score']:
            df.loc[idx, 'approved'] = False
            df.loc[idx, 'rejection_reason'] = f"Score {abs(score):.3f} < threshold {thresholds['min_score']}"
            continue
        
        # Apply confidence check
        if confidence < thresholds['confidence_threshold']:
            df.loc[idx, 'approved'] = False
            df.loc[idx, 'rejection_reason'] = f"Confidence {confidence:.3f} < threshold {thresholds['confidence_threshold']}"
            continue
        
        # Adjust quantity based on confidence
        base_quantity = thresholds['max_quantity']
        adjusted_quantity = int(base_quantity * confidence)
        df.loc[idx, 'quantity'] = max(adjusted_quantity, 10)  # Minimum 10
        df.loc[idx, 'approved'] = True
    
    return df
```

**Outputs:**
- `storage/metrics/dynamic_risk_397.json` - Threshold usage statistics
- `reports/DYNAMIC_RISK_397.md` - Risk analysis per underlying

**Success Criteria:**
- Approval rates vary by underlying (NIFTY > BANKNIFTY > FINNIFTY)
- High-confidence signals get larger quantities
- Rejection reasons logged explicitly

---

### PHASE 398: Paper Trading Validation Loop

**File:** `tools/paper_trading_validation_398.py` (NEW)

**Purpose:** 30-snapshot live test comparing Ultra vs XGBoost vs Ensemble

**Implementation:**

```python
def run_paper_trading_validation(num_snapshots: int = 30):
    """
    Run 30 snapshots and compare model performance.
    
    Test scenarios:
    1. Ultra Model only
    2. XGBoost only
    3. Ensemble (all 3)
    4. Delta fallback only
    """
    results = {
        'ultra': [],
        'xgboost': [],
        'ensemble': [],
        'delta': []
    }
    
    for i in range(num_snapshots):
        logger.info(f"Snapshot {i+1}/{num_snapshots}")
        
        # Run signal engine with each method
        for method in ['ultra', 'xgboost', 'ensemble', 'delta']:
            signals = run_signal_engine(method=method)
            
            # Calculate metrics
            metrics = {
                'signals_generated': len(signals),
                'approved_orders': (signals['approved'] == True).sum(),
                'avg_score': signals['ai_score'].mean(),
                'avg_confidence': signals.get('buy_probability', pd.Series([0.5])).mean(),
                'buy_signals': (signals['signal'] == 'BUY').sum(),
                'sell_signals': (signals['signal'] == 'SELL').sum()
            }
            
            results[method].append(metrics)
    
    # Compare performance
    comparison = pd.DataFrame({
        method: {
            'avg_signals': np.mean([r['signals_generated'] for r in results[method]]),
            'avg_approved': np.mean([r['approved_orders'] for r in results[method]]),
            'avg_score': np.mean([r['avg_score'] for r in results[method]])
        }
        for method in results.keys()
    })
    
    logger.info(f"Validation Results:\n{comparison}")
    
    return comparison
```

**Outputs:**
- `storage/metrics/paper_trading_validation_398.json` - Test results
- `reports/PAPER_TRADING_VALIDATION_398.md` - Performance comparison

**Success Criteria:**
- Ensemble performs best (highest avg_score, most approved orders)
- XGBoost > Ultra > Delta
- No crashes or errors in 30 snapshots

---

### PHASE 399: Scoring Telemetry v2.0

**File:** `core/engine/scoring_telemetry_v2.py` (UPGRADE Phase 385 logic)

**Purpose:** Enhanced telemetry with 20+ metrics per signal

**Metrics to Track:**

```python
TELEMETRY_METRICS = {
    # Model usage
    'model_used': ['ultra', 'xgboost', 'ensemble', 'delta'],
    'ensemble_method': ['weighted_average', 'ultra_confident', 'xgboost_confident'],
    
    # Scores
    'ai_score': float,
    'ai_score_normalized': float,
    'buy_probability': float,
    'sell_probability': float,
    
    # Confidence
    'ultra_confidence': float,
    'xgboost_confidence': float,
    'ensemble_confidence': float,
    
    # Features
    'delta': float,
    'gamma': float,
    'iv': float,
    'moneyness': float,
    
    # Outcomes
    'approved': bool,
    'rejection_reason': str,
    'quantity': int,
    
    # Timing
    'prediction_time_ms': float,
    'feature_engineering_time_ms': float
}
```

**Outputs:**
- `storage/metrics/scoring/signal_{timestamp}.json` - Per-signal telemetry
- `storage/metrics/scoring_telemetry_399_daily.json` - Daily aggregate
- `reports/SCORING_TELEMETRY_399.md` - Telemetry analysis

**Success Criteria:**
- 20+ metrics tracked per signal
- Telemetry files generated for every signal
- Dashboard-ready JSON format

---

### PHASE 400: Production-Readiness Report

**File:** `core/engine/production_readiness_gate.py` (NEW)

**Purpose:** Final go/no-go decision for production deployment

**Checks:**

```python
def generate_production_readiness_report() -> Dict[str, Any]:
    """
    Comprehensive production readiness assessment.
    
    Go/No-Go criteria:
    1. Model accuracy > 60%
    2. Ensemble working (all 3 models available)
    3. No drift detected
    4. Paper trading win rate > baseline
    5. Auto-retraining functional
    6. Telemetry capturing all metrics
    7. Safety flags still False
    """
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {},
        'overall_status': 'unknown'
    }
    
    # Check 1: Model accuracy
    xgb_accuracy = load_latest_model_accuracy('xgboost')
    report['checks']['model_accuracy'] = {
        'value': xgb_accuracy,
        'threshold': 0.60,
        'status': 'pass' if xgb_accuracy > 0.60 else 'fail'
    }
    
    # Check 2: Ensemble availability
    ultra_available = count_available_ultra_models()
    xgb_available = count_available_xgboost_models()
    report['checks']['ensemble_availability'] = {
        'ultra_models': ultra_available,
        'xgboost_models': xgb_available,
        'status': 'pass' if (ultra_available >= 3 and xgb_available >= 3) else 'warn'
    }
    
    # Check 3: Drift detection
    drift_status = load_latest_drift_status()
    report['checks']['drift_status'] = {
        'drift_detected': drift_status['drift_detected'],
        'status': 'pass' if not drift_status['drift_detected'] else 'warn'
    }
    
    # Check 4: Paper trading performance
    paper_results = load_paper_trading_results()
    baseline_win_rate = 0.667
    paper_win_rate = paper_results.get('win_rate', 0)
    report['checks']['paper_trading'] = {
        'win_rate': paper_win_rate,
        'baseline': baseline_win_rate,
        'improvement': paper_win_rate - baseline_win_rate,
        'status': 'pass' if paper_win_rate > baseline_win_rate else 'warn'
    }
    
    # Check 5: Auto-retraining
    last_retrain = load_last_retrain_timestamp()
    hours_since_retrain = (datetime.utcnow() - last_retrain).total_seconds() / 3600
    report['checks']['auto_retrain'] = {
        'last_retrain': last_retrain.isoformat(),
        'hours_since': hours_since_retrain,
        'status': 'pass' if hours_since_retrain < 48 else 'warn'
    }
    
    # Check 6: Telemetry
    telemetry_files = count_telemetry_files_today()
    report['checks']['telemetry'] = {
        'files_today': telemetry_files,
        'status': 'pass' if telemetry_files > 0 else 'fail'
    }
    
    # Check 7: Safety flags
    safety_status = verify_safety_configs()
    report['checks']['safety_flags'] = {
        'live_trading_enabled': safety_status['live_trading_enabled'],
        'dry_run_enabled': safety_status['dry_run_enabled'],
        'status': 'pass' if not safety_status['live_trading_enabled'] else 'fail'
    }
    
    # Overall decision
    all_checks = [c['status'] for c in report['checks'].values()]
    if all(s == 'pass' for s in all_checks):
        report['overall_status'] = 'GO'
        report['recommendation'] = 'READY FOR PRODUCTION (DRY-RUN)'
    elif 'fail' in all_checks:
        report['overall_status'] = 'NO-GO'
        report['recommendation'] = 'FIX CRITICAL ISSUES BEFORE DEPLOYMENT'
    else:
        report['overall_status'] = 'GO WITH CAUTION'
        report['recommendation'] = 'SAFE TO DEPLOY, MONITOR WARNINGS'
    
    return report
```

**Outputs:**
- `storage/metrics/production_readiness_400.json` - Final report
- `reports/PRODUCTION_READINESS_400.md` - Human-readable report

**Success Criteria:**
- All checks pass or warn (no fails)
- Overall status = GO or GO WITH CAUTION
- Safety flags verified False

---

## SAFETY CONSTRAINTS

### Files That MUST NOT Be Modified
```
❌ core/config/live_trade_config.py (LIVE_TRADING_ENABLED must stay False)
❌ core/config/angel_automation_config.json (DRY_RUN must stay true)
❌ core/config/system3_ultra_safety.json (AUTO_EXECUTE must stay false)
❌ Any phase files 1-380 (read-only)
❌ Broker integration modules (read-only)
❌ Order execution modules (read-only)
```

### Allowed Modifications
```
✅ core/engine/ai_model/*.py (NEW: feature engineering, SMOTE, XGBoost trainer)
✅ core/engine/ensemble_predictor.py (NEW)
✅ core/engine/score_normalizer.py (NEW)
✅ core/engine/pnl_outcome_learner.py (NEW)
✅ core/engine/drift_detector_v2.py (MODIFY Phase 334)
✅ core/engine/auto_retrain_scheduler.py (NEW)
✅ core/engine/risk_controller_v2.py (MODIFY existing)
✅ core/engine/scoring_telemetry_v2.py (UPGRADE Phase 385)
✅ core/engine/production_readiness_gate.py (NEW)
✅ core/engine/system3_signal_engine.py (MODIFY Step 6 AI prediction logic)
✅ core/engine/system3_phase389_*.py (NEW, 12 files)
✅ storage/metrics/*.json (NEW)
✅ reports/*.md (NEW)
```

---

## TESTING STRATEGY

### Block Test Script: `tools/run_phases_389_400_block_test.py`

```python
"""
Block Test for System3 Phases 389-400

Executes all 12 phases sequentially and generates pass/fail summary.

Usage:
    C:/Genesis_System3/venv/Scripts/python.exe tools/run_phases_389_400_block_test.py
"""

def run_block_test_389_400():
    """Run all phases 389-400 and generate summary."""
    phase_functions = [
        (389, "Feature Engineering", run_phase_389),
        (390, "SMOTE Balancing", run_phase_390),
        (391, "XGBoost Training", run_phase_391),
        (392, "Ensemble Creation", run_phase_392),
        (393, "Score Normalization", run_phase_393),
        (394, "PnL Learning", run_phase_394),
        (395, "Drift Detection", run_phase_395),
        (396, "Auto-Retraining", run_phase_396),
        (397, "Dynamic Risk", run_phase_397),
        (398, "Paper Validation", run_phase_398),
        (399, "Telemetry v2", run_phase_399),
        (400, "Production Gate", run_phase_400)
    ]
    
    results = []
    
    for phase_id, phase_name, phase_func in phase_functions:
        print(f"Phase {phase_id} ({phase_name})".ljust(40), end="")
        
        try:
            result = phase_func()
            status = result.get("status", "error")
            
            if status == "ok":
                print(": OK")
                results.append({"phase": phase_id, "status": "PASS"})
            elif status == "warn":
                print(": WARN")
                results.append({"phase": phase_id, "status": "WARN"})
            else:
                print(": FAIL")
                results.append({"phase": phase_id, "status": "FAIL"})
        
        except Exception as e:
            print(f": ERROR ({str(e)})")
            results.append({"phase": phase_id, "status": "ERROR"})
    
    # Summary
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    warn_count = sum(1 for r in results if r["status"] == "WARN")
    fail_count = sum(1 for r in results if r["status"] in ["FAIL", "ERROR"])
    
    print("\n" + "=" * 60)
    print(f"OVERALL: {pass_count}/12 PASS, {warn_count}/12 WARN, {fail_count}/12 FAIL")
    
    if fail_count == 0:
        print("STATUS: ALL PHASES COMPLETE")
        return 0
    else:
        print("STATUS: SOME PHASES FAILED")
        return 1

if __name__ == "__main__":
    exit_code = run_block_test_389_400()
    sys.exit(exit_code)
```

---

## IMPLEMENTATION TIMELINE

### Week 1 (Phases 389-392): Core ML Upgrade
**Time:** 20-30 hours

- **Day 1-2:** Feature Engineering (Phase 389) - 8 hours
- **Day 2-3:** SMOTE Balancing (Phase 390) - 4 hours
- **Day 3-5:** XGBoost Training (Phase 391) - 8 hours
- **Day 5-7:** Ensemble Creation (Phase 392) - 8 hours

### Week 2 (Phases 393-397): Production Infrastructure
**Time:** 20-25 hours

- **Day 8-9:** Score Normalization (Phase 393) - 4 hours
- **Day 9-10:** PnL Learning (Phase 394) - 6 hours
- **Day 10-11:** Drift Detection Upgrade (Phase 395) - 6 hours
- **Day 12-13:** Auto-Retraining Engine (Phase 396) - 6 hours
- **Day 13-14:** Dynamic Risk Controller (Phase 397) - 4 hours

### Week 3 (Phases 398-400): Validation & Deployment
**Time:** 15-20 hours

- **Day 15-16:** Paper Trading Validation (Phase 398) - 8 hours
- **Day 16-17:** Telemetry v2 (Phase 399) - 4 hours
- **Day 17-18:** Production Readiness (Phase 400) - 4 hours
- **Day 18-21:** Block testing, debugging, documentation - 8 hours

**Total Time Estimate:** 55-75 hours (2-3 weeks full-time)

---

## SUCCESS METRICS

### Phase 389-392 (Core ML)
- ✅ Feature count increased from 10 to 50+
- ✅ Feature variance increased by 50%+
- ✅ Class balance achieved (33/33/33)
- ✅ XGBoost accuracy > 60% (5/5 models)
- ✅ Ensemble accuracy > max(ultra, xgboost, delta)

### Phase 393-397 (Infrastructure)
- ✅ Scores normalized to [0, 1] range
- ✅ Real trades incorporated (4+ from pnl_log)
- ✅ Drift detection working (KS test functional)
- ✅ Auto-retraining runs daily at 18:00 IST
- ✅ Dynamic thresholds applied per underlying

### Phase 398-400 (Validation)
- ✅ Paper trading win rate > 66.7% baseline
- ✅ 30 snapshots run without errors
- ✅ Telemetry capturing 20+ metrics
- ✅ Production readiness status = GO

### Overall System
- ✅ ML model training NO LONGER returns None
- ✅ Ensemble used for 80%+ of signals
- ✅ Delta fallback used for <20% of signals
- ✅ Target accuracy 70-80% (vs current 66.7%)
- ✅ Self-improving system (learns daily)

---

## ROLLBACK PLAN

### If Issues Arise

#### Option 1: Revert to Ultra Models Only (Phase 381-388)
```python
# In system3_signal_engine.py, disable ensemble:
# ensemble_model = load_ensemble(underlying)  # DISABLED
ultra_model = load_ultra_model(underlying)
if ultra_model:
    df = predict_direction(ultra_model, df)
else:
    df["ai_score"] = compute_delta_scores(df)  # Delta fallback
```

#### Option 2: Disable Specific Phase
```python
# Disable SMOTE balancing (Phase 390):
# df_balanced = balance_training_data_with_smote(df)  # DISABLED
df_balanced = df  # Use unbalanced data

# Disable auto-retraining (Phase 396):
# schedule.every().day.at("18:00").do(run_daily_auto_retrain)  # DISABLED
```

#### Option 3: Full Revert to Phase 388 State
```powershell
git checkout core/engine/system3_signal_engine.py
git checkout core/engine/ensemble_predictor.py
# etc.
```

**Result:** System reverts to Ultra Models + Delta fallback (Phase 381-388 complete state)

---

## DEPLOYMENT CHECKLIST

### Pre-Implementation
- [ ] Phase 381-388 verified complete
- [ ] Ultra models loadable (5/5)
- [ ] Current system generating 120 signals/3min
- [ ] Safety flags verified False
- [ ] Python venv active (3.10.11)

### During Implementation (Phases 389-400)
- [ ] Phase 389: Feature engineering complete (50+ features)
- [ ] Phase 390: SMOTE balancing working (33/33/33)
- [ ] Phase 391: XGBoost models trained (5/5, >60% accuracy)
- [ ] Phase 392: Ensemble predictor functional
- [ ] Phase 393: Score normalization working
- [ ] Phase 394: PnL learning integrated
- [ ] Phase 395: Drift detector upgraded
- [ ] Phase 396: Auto-retraining scheduler active
- [ ] Phase 397: Dynamic risk controller deployed
- [ ] Phase 398: Paper trading validation passed
- [ ] Phase 399: Telemetry v2 capturing metrics
- [ ] Phase 400: Production readiness = GO

### Post-Implementation
- [ ] Block test passed (12/12 phases OK/WARN)
- [ ] Safety flags still False
- [ ] No live trading enabled
- [ ] DRY-RUN enforced
- [ ] Documentation updated
- [ ] Implementation summary generated

---

## FINAL RECOMMENDATION

**PROCEED WITH PHASE 389-400 IMPLEMENTATION**

### Why This is the Correct Next Step:

1. **Phase 381-388 Complete:** Ultra Models integrated and tested
2. **System Stable:** 120 signals/3min, 0 errors, healthy pipeline
3. **Performance Ceiling:** Delta fallback capped at 66.7%, need ML upgrade
4. **Data Issues Diagnosed:** Low variance, class imbalance, no real outcomes
5. **Agent Capability Proven:** Phases 381-388 implemented at production grade
6. **Clear Roadmap:** 12 phases, 2-3 weeks, measurable success metrics

### Expected Impact:

- **Immediate (Week 1):** XGBoost models trained, 60-70% accuracy
- **Medium-term (Week 2):** Ensemble deployed, 70-80% accuracy
- **Long-term (Week 3+):** Self-improving system, 80-85% accuracy

### Risk Mitigation:

- All safety flags remain False (DRY-RUN only)
- Rollback to Phase 388 available at any time
- Incremental implementation (test each phase)
- Block test validates entire pipeline

---

**STATUS:** READY FOR AGENT IMPLEMENTATION AT PRODUCTION GRADE

**Next Action:** Agent begins Phase 389 (Feature Engineering Upgrade)

---

**Master Plan Generated:** December 8, 2025  
**Agent:** GitHub Copilot (Claude Sonnet 4.5)  
**Python Environment:** venv 3.10.11  
**Mode:** DRY-RUN ONLY (No live trading)
