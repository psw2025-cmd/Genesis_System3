# System3 - Post-Monday Upgrade Pack

## Status: ✅ ALL MODULES PREPARED (DISABLED FOR SAFETY)

---

## 1. Auto Threshold Adjustment

### Module: `angel_auto_threshold_adjuster.py`
- **Menu**: Option 19
- **Function**: Analyzes real performance, generates threshold recommendations
- **Current Status**: Recommendations only (auto-adjust DISABLED)
- **Requirements**: Minimum 10 trades, 3+ days of data
- **Output**: `storage/config/thresholds_recommended.json`

### How It Works
1. Analyzes recent PnL data (last 7 days)
2. Computes win rate, avg PnL, total PnL
3. Analyzes signal distribution
4. Generates recommendations:
   - If win_rate > 60% and avg_pnl > 2%: Slight relaxation
   - If win_rate < 40% or avg_pnl < -1%: Tighten thresholds
   - Otherwise: Keep current

### Post-Monday Usage
```python
# After Monday, run:
python -m core.engine.angel_auto_threshold_adjuster

# Review recommendations in:
# storage/config/thresholds_recommended.json

# To enable auto-adjustment (future):
# Set auto_adjust_enabled = True in the module
```

---

## 2. Confidence & Score Calibration

### Module: `angel_confidence_calibrator.py`
- **Menu**: Option 20
- **Function**: Calibrates model confidence vs actual outcomes
- **Current Status**: Ready (waits for real data)
- **Output**: `storage/config/confidence_calibration.json`

### How It Works
1. Matches signals with PnL outcomes
2. Analyzes confidence distribution by outcome
3. Identifies confidence buckets that predict well
4. Recommends confidence threshold adjustments

### Post-Monday Usage
```python
# After collecting real data:
python -m core.engine.angel_confidence_calibrator

# Review calibration in:
# storage/config/confidence_calibration.json
```

---

## 3. Strategy Optimizer

### Module: `angel_strategy_optimizer.py`
- **Menu**: Option 21
- **Function**: Optimizes position sizing, risk management, allocation
- **Current Status**: Ready (waits for real data)
- **Output**: `storage/config/strategy_optimization.json`

### Optimizations Provided
1. **Position Sizing**: Kelly Criterion approximation
2. **Risk Management**: Stop-loss/target adjustments based on drawdown
3. **Portfolio Allocation**: Weight allocation across underlyings
4. **Entry Timing**: Analysis of exit reasons

### Post-Monday Usage
```python
# After collecting real data:
python -m core.engine.angel_strategy_optimizer

# Review optimizations in:
# storage/config/strategy_optimization.json
```

---

## 4. Advanced Feature Ranking

### Module: `angel_feature_ranker.py`
- **Menu**: Option 22
- **Function**: Ranks features beyond MI (correlation, stability, completeness)
- **Current Status**: Ready
- **Output**: `storage/training/feature_rankings/advanced_ranking_*.csv`

### Ranking Methods
1. **Correlation**: Correlation with label
2. **Variance**: Feature stability
3. **Completeness**: Non-zero ratio
4. **Combined Score**: Weighted combination

### Usage
```python
# Run advanced feature ranking:
python -m core.engine.angel_feature_ranker

# Results saved to:
# storage/training/feature_rankings/advanced_ranking_*.csv
```

---

## 5. Blended Model Training

### Module: `angel_blended_model_trainer.py`
- **Menu**: Option 23
- **Function**: Blends synthetic + real training data
- **Current Status**: Ready (waits for real data)
- **Output**: `storage/training/angel_index_options_blended_training.csv`

### How It Works
1. Loads synthetic training data
2. Loads real training data (from live signals)
3. Blends based on weights (default: 40% synthetic, 60% real)
4. Creates blended dataset for retraining

### Post-Monday Usage
```python
# After Monday, build real training data first:
python -m core.engine.build_angel_training_dataset  # Menu 9

# Then blend:
python -m core.engine.angel_blended_model_trainer  # Menu 23

# Retrain models with blended data:
python -m core.engine.train_angel_models  # Menu 10
```

---

## 6. Enhanced Signal Scoring

### Module: `angel_enhanced_signal_scorer.py`
- **Function**: Multi-factor signal scoring
- **Status**: Ready (integrated into pipeline)
- **Components**:
  - Confidence (30%)
  - Expected move (25%)
  - Moneyness (15%)
  - Volatility (10%)
  - Momentum (10%)
  - Risk-reward (10%)

### Usage
```python
from core.engine.angel_enhanced_signal_scorer import get_enhanced_scorer

scorer = get_enhanced_scorer()
score_data = scorer.compute_enhanced_score(signal_row)
# Returns: base_score, enhanced_score, risk_adjusted_score, components
```

---

## 7. Alerting System

### Module: `angel_alerting_system.py`
- **Function**: Monitors system, generates alerts
- **Status**: Ready
- **Output**: `storage/live/system_alerts.log`

### Alert Categories
- **PIPELINE**: Stale signals, data issues
- **TRADE**: Unusual trade patterns
- **RISK**: Limit breaches
- **SYSTEM**: Health issues
- **PERFORMANCE**: Performance degradation

### Alert Levels
- **INFO**: Informational
- **WARNING**: Needs attention
- **CRITICAL**: Immediate action required

---

## 8. LIVE Mode Preparation

### Module: `angel_executor_live_prep.py`
- **Function**: Prepares for LIVE order execution
- **Status**: Infrastructure ready (DISABLED)
- **Safety**: Requires explicit enablement

### Readiness Checks
1. Auto-execution enabled in config
2. Safety validator available
3. Broker connection validated
4. Daily limits configured

### Post-Monday Path
1. Test in paper trading first
2. Validate order placement
3. Enable LIVE mode gradually
4. Monitor closely

---

## Post-Monday Workflow

### Day 1 (Monday) - Data Collection
1. Run menu 11 (LIVE AI signals) during market hours
2. Monitor signals and trade plans
3. Execute trades manually (menu 14 - DRY RUN)
4. End of day: Run menu 15 (PnL summary), menu 17 (report)

### Day 2 (Tuesday) - Analysis
1. Run menu 19 (threshold adjuster) - get recommendations
2. Run menu 20 (confidence calibrator) - analyze confidence
3. Run menu 21 (strategy optimizer) - optimize strategy
4. Review all recommendations

### Day 3-5 (Wednesday-Friday) - Optimization
1. Adjust thresholds based on recommendations
2. Run menu 23 (blended trainer) - create blended dataset
3. Retrain models (menu 10) with blended data
4. Gradually enable automation if performance is good

### Week 2+ - Full Automation
1. Enable auto-execution (with safety checks)
2. Enable auto PnL simulation
3. Monitor and adjust continuously
4. Prepare for LIVE mode (when ready)

---

## Safety Guarantees

### Monday Configuration
- ✅ Auto-execution: DISABLED
- ✅ Auto PnL simulation: DISABLED
- ✅ Execution mode: DRY RUN only
- ✅ Conservative thresholds: conf=0.80, score=0.30
- ✅ Safety limits: 20 trades/day, 5 per underlying
- ✅ Full logging: Complete audit trail

### Post-Monday Safety
- All optimization modules generate recommendations only
- No automatic changes without review
- Manual approval required for threshold adjustments
- LIVE mode requires explicit enablement
- All changes logged and auditable

---

## Module Status Summary

| Module | Status | Post-Monday Ready |
|--------|--------|-------------------|
| Auto Threshold Adjuster | ✅ Ready | ✅ Yes |
| Confidence Calibrator | ✅ Ready | ✅ Yes |
| Strategy Optimizer | ✅ Ready | ✅ Yes |
| Advanced Feature Ranker | ✅ Ready | ✅ Yes |
| Blended Model Trainer | ✅ Ready | ✅ Yes |
| Enhanced Signal Scorer | ✅ Ready | ✅ Yes |
| Alerting System | ✅ Ready | ✅ Yes |
| LIVE Mode Prep | ✅ Ready | ✅ Yes |

---

**All Post-Monday upgrade modules are prepared and ready.**
**System remains in conservative mode for Monday's live trading.**

