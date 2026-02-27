# System3 Phases 10-20: Testing Guide

**Date**: 2024-12-29  
**Status**: 🧪 **READY FOR TESTING**

---

## ⚠️ Important: Run Commands in External Terminal

All commands must be run in your **external terminal with venv activated**:
```bash
# Activate venv first
C:\Genesis_System3> c:\Genesis_System3\venv\Scripts\activate.bat
(venv) C:\Genesis_System3>
```

---

## 📋 Testing Checklist

### Foundation Tests (Run First)

#### ✅ Test 1: Ultra Safety Switches
```bash
python -m core.engine.ultra_safety
```

**Expected Output**:
```
=== SYSTEM3 ULTRA SAFETY SWITCHES ===

Current Safety Settings:
  AUTO_EXECUTE_TRADES: False (❌ DISABLED)
  AUTO_UPDATE_THRESHOLDS: False (❌ DISABLED)
  AUTO_RETRAIN_MODELS: False (❌ DISABLED)
  AUTO_PROMOTE_MODELS: False (❌ DISABLED)
  AUTO_WRITE_CONFIG: False (❌ DISABLED)
```

**Status**: ⏳ Test this first

---

#### ✅ Test 2: Profile Selector
```bash
python -m core.engine.angel_model_selector
```

**Expected Output**:
```
=== SYSTEM3 LIVE PROFILES & MODEL SOURCES ===

Active Profile: BASELINE
...
=== PROFILE PATHS ===
Model Directory: core/models/angel_one
...
```

**Status**: ⏳ Test this second

---

#### ✅ Test 3: Directory Structure
```bash
dir core\models\angel_one_ultra
dir storage\ultra
dir storage\learning_ultra
dir storage\reports_ultra
dir core\config
```

**Expected**: All directories exist (may be empty)

**Status**: ⏳ Test this third

---

### Phase Tests (Run in Order)

#### ✅ Test 4: Phase 10 - Shadow Data Engine
```bash
python -m core.engine.ultra_shadow_data_engine
```

**Expected**:
- Loads signals/trades/PnL (if available)
- Builds shadow master dataset
- Saves to `storage/learning_ultra/angel_ultra_shadow_master.csv`

**Note**: May show "NO_DATA" if no baseline data exists (expected for fresh setup)

**Status**: ⏳ Test after foundation

---

#### ✅ Test 5: Phase 11 - Feature Expander
```bash
python -m core.engine.ultra_feature_engineering
```

**Expected**:
- Loads synthetic training CSV
- Loads shadow master (if Phase 10 completed)
- Adds Ultra features (~100 total)
- Saves to `storage/training/angel_ultra_training.csv`

**Prerequisites**: Synthetic training CSV must exist
```bash
# Generate if missing:
python -m core.engine.generate_synthetic_angel_training
```

**Status**: ⏳ Test after Phase 10

---

#### ✅ Test 6: Phase 12 - Model Trainer
```bash
python -m core.engine.ultra_train_models
```

**Expected**:
- Loads Ultra training dataset
- Trains models for all 5 underlyings
- Saves to `core/models/angel_one_ultra/*_ultra_model.pkl`
- Shows accuracy for each underlying

**Prerequisites**: Phase 11 must complete successfully

**Status**: ⏳ Test after Phase 11

---

#### ✅ Test 7: Phase 13 - Hyperparameter Explorer
```bash
python -m core.engine.ultra_hparam_explorer
```

**Expected**:
- Tests multiple hyperparameter combinations
- Saves results to `storage/reports_ultra/ultra_hparam_results_*.csv`
- Shows best parameters per underlying
- No model files written

**Prerequisites**: Phase 12 must complete successfully

**Status**: ⏳ Test after Phase 12

---

#### ✅ Test 8: Phase 14 - Regime Classifier
```bash
python -m core.engine.ultra_regime_classifier
```

**Expected**:
- Classifies regimes (LOW_VOL, HIGH_VOL, TREND_UP, etc.)
- Saves regime-labeled dataset
- Generates regime summary report

**Prerequisites**: Phase 11 must complete successfully

**Status**: ⏳ Test after Phase 11

---

#### ✅ Test 9: Phase 15 - Multi-Consensus
```bash
python -m core.engine.ultra_multi_consensus
```

**Expected**:
- Compares Baseline vs Ultra predictions
- Saves consensus report
- Shows agreement rate percentage

**Prerequisites**: Phase 10 and Phase 12 must complete successfully

**Status**: ⏳ Test after Phase 12

---

#### ✅ Test 10: Phase 16 - Threshold Lab
```bash
python -m core.engine.ultra_threshold_lab
```

**Expected**:
- Grid searches threshold combinations
- Saves results to `storage/reports_ultra/ultra_threshold_grid_search.csv`
- Shows best thresholds per underlying
- No config changes

**Prerequisites**: Phase 10 must complete successfully

**Status**: ⏳ Test after Phase 10

---

#### ✅ Test 11: Phase 17 - Live Signals Shadow
```bash
python -m core.engine.ultra_live_signals_shadow
```

**Expected**:
- Connects to broker (may fail if offline)
- Builds live snapshot
- Runs Baseline + Ultra predictions
- Saves shadow signals to `storage/ultra/angel_ultra_live_shadow_signals.csv`

**Prerequisites**: Phase 12 must complete, broker connection required

**Note**: May fail if broker not connected (expected in offline testing)

**Status**: ⏳ Test after Phase 12 (requires broker)

---

#### ✅ Test 12: Phase 18 - Trade Simulator
```bash
python -m core.engine.ultra_trade_simulator
```

**Expected**:
- Simulates trades from shadow signals
- Generates trade plans and PnL
- Saves to `storage/ultra/angel_ultra_trade_plan_sim.csv`
- Shows summary per underlying

**Prerequisites**: Phase 10 or Phase 17 must complete successfully

**Status**: ⏳ Test after Phase 10 or Phase 17

---

#### ✅ Test 13: Phase 19 - PnL Analyzer
```bash
python -m core.engine.ultra_pnl_analyzer
```

**Expected**:
- Analyzes PnL simulation results
- Generates comprehensive report
- Per-underlying and time-of-day breakdowns
- Saves to `storage/reports_ultra/ultra_pnl_report.csv`

**Prerequisites**: Phase 18 must complete successfully

**Status**: ⏳ Test after Phase 18

---

#### ✅ Test 14: Phase 20 - Promotion Manager
```bash
python -m core.engine.ultra_promotion_manager
```

**Expected**:
- Shows Baseline vs Ultra comparison table
- Prompts for manual promotion
- Requires explicit keyword (e.g., "PROMOTE_NIFTY")
- No auto-promotion (safety enforced)

**Prerequisites**: Phase 12 must complete successfully

**Status**: ⏳ Test after Phase 12

---

## 🚀 Quick Test Sequence

### Minimal Test (Foundation Only)
```bash
# 1. Safety switches
python -m core.engine.ultra_safety

# 2. Profile selector
python -m core.engine.angel_model_selector

# 3. Check directories
dir core\models\angel_one_ultra
dir storage\ultra
dir storage\learning_ultra
dir storage\reports_ultra
```

### Full Test Sequence (All Phases)
```bash
# Foundation
python -m core.engine.ultra_safety
python -m core.engine.angel_model_selector

# Phase 10
python -m core.engine.ultra_shadow_data_engine

# Phase 11 (requires synthetic training)
python -m core.engine.generate_synthetic_angel_training  # If missing
python -m core.engine.ultra_feature_engineering

# Phase 12
python -m core.engine.ultra_train_models

# Phase 13-16 (can run in parallel after prerequisites)
python -m core.engine.ultra_hparam_explorer
python -m core.engine.ultra_regime_classifier
python -m core.engine.ultra_multi_consensus
python -m core.engine.ultra_threshold_lab

# Phase 17 (requires broker - may skip if offline)
python -m core.engine.ultra_live_signals_shadow

# Phase 18-19
python -m core.engine.ultra_trade_simulator
python -m core.engine.ultra_pnl_analyzer

# Phase 20
python -m core.engine.ultra_promotion_manager
```

---

## 📊 Expected File Structure After Testing

```
core/
  models/
    angel_one_ultra/
      NIFTY_ultra_model.pkl
      NIFTY_ultra_model_meta.json
      ... (other underlyings)

storage/
  ultra/
    angel_ultra_live_shadow_signals.csv
    angel_ultra_trade_plan_sim.csv
    angel_ultra_pnl_sim.csv

  learning_ultra/
    angel_ultra_shadow_master.csv
    angel_ultra_shadow_master.parquet

  reports_ultra/
    ultra_hparam_results_*.csv
    ultra_regime_summary.csv
    ultra_consensus_sample.csv
    ultra_threshold_grid_search.csv
    ultra_trade_sim_summary.csv
    ultra_pnl_report.csv
    ultra_promotion_log.txt

  training/
    angel_ultra_training.csv
    angel_ultra_training.parquet
    angel_ultra_training_with_regime.parquet
```

---

## ✅ Success Criteria

### Foundation Tests
- [ ] Safety switches all show False
- [ ] Profile selector shows BASELINE profile
- [ ] All Ultra directories exist

### Phase Tests
- [ ] Phase 10: Shadow master dataset created
- [ ] Phase 11: Ultra training dataset with extended features
- [ ] Phase 12: Ultra models trained and saved
- [ ] Phase 13: Hyperparameter results saved
- [ ] Phase 14: Regime classification completed
- [ ] Phase 15: Consensus report generated
- [ ] Phase 16: Threshold grid search completed
- [ ] Phase 17: Shadow signals saved (if broker available)
- [ ] Phase 18: Trade simulation completed
- [ ] Phase 19: PnL analysis report generated
- [ ] Phase 20: Promotion manager shows comparison

---

## 🐛 Troubleshooting

### Issue: "NO_DATA" in Phase 10
**Solution**: Run baseline data collection first:
```bash
python -m core.engine.generate_synthetic_angel_training
```

### Issue: "Module not found" errors
**Solution**: Ensure you're in the project root and venv is activated:
```bash
cd C:\Genesis_System3
c:\Genesis_System3\venv\Scripts\activate.bat
```

### Issue: Broker connection fails (Phase 17)
**Solution**: This is expected if broker is offline. Phase 17 can be skipped or tested later when broker is available.

### Issue: Missing dependencies
**Solution**: Install required packages:
```bash
pip install pandas numpy scikit-learn joblib pyarrow
```

---

## 📝 Test Results Template

After running tests, document results:

```
### Test Results - [Date]

Foundation Tests:
- [ ] Test 1: ✅/❌
- [ ] Test 2: ✅/❌
- [ ] Test 3: ✅/❌

Phase Tests:
- [ ] Phase 10: ✅/❌
- [ ] Phase 11: ✅/❌
- [ ] Phase 12: ✅/❌
- [ ] Phase 13: ✅/❌
- [ ] Phase 14: ✅/❌
- [ ] Phase 15: ✅/❌
- [ ] Phase 16: ✅/❌
- [ ] Phase 17: ✅/❌/⏭️ (skipped - broker offline)
- [ ] Phase 18: ✅/❌
- [ ] Phase 19: ✅/❌
- [ ] Phase 20: ✅/❌

Issues Found:
- None / [List issues]

Status: ✅ ALL TESTS PASSED / ⚠️ SOME ISSUES FOUND
```

---

**Status**: 🧪 **READY FOR TESTING**

Run all commands in your external terminal with venv activated!

