# System3 Phases 10-20: Ultra-Mode Implementation Plan

**Analysis Date**: 2024-12-29  
**Status**: 📋 **PLANNING PHASE**

---

## Executive Summary

This document outlines the implementation plan for **System3 Ultra-Mode** - a complete shadow/experimental pipeline that runs parallel to the baseline system without interfering with production.

**Key Principles**:
- ✅ **Additive Only**: No overwrites of baseline files
- ✅ **Shadow Mode**: All Ultra operations are experimental
- ✅ **Safety First**: All auto-features disabled by default
- ✅ **Profile-Based**: BASELINE vs ULTRA_DEV profiles

---

## Implementation Structure

### Foundation Tasks (0.1-0.3)

**Task 0.1**: Create Ultra Directories
- `core/models/angel_one_ultra/` - Ultra models
- `storage/ultra/` - Ultra live data
- `storage/learning_ultra/` - Ultra learning data
- `storage/reports_ultra/` - Ultra reports
- `core/config/` - Ultra configs

**Task 0.2**: Ultra Safety Switches
- `core/config/system3_ultra_safety.json` - All flags false
- `core/engine/ultra_safety.py` - Safety helper module

**Task 0.3**: Profile Selector Extension
- Extend `angel_model_selector.py` for ULTRA_DEV profile
- `core/config/system3_active_profile.json` - Profile config

### Phase Implementation (10-20)

| Phase | Module | Menu Option | Status |
|-------|--------|-------------|--------|
| 10 | `ultra_shadow_data_engine.py` | 73 | ⏳ Pending |
| 11 | `ultra_feature_engineering.py` | 74 | ⏳ Pending |
| 12 | `ultra_train_models.py` | 75 | ⏳ Pending |
| 13 | `ultra_hparam_explorer.py` | 76 | ⏳ Pending |
| 14 | `ultra_regime_classifier.py` | 77 | ⏳ Pending |
| 15 | `ultra_multi_consensus.py` | 78 | ⏳ Pending |
| 16 | `ultra_threshold_lab.py` | 79 | ⏳ Pending |
| 17 | `ultra_live_signals_shadow.py` | 80 | ⏳ Pending |
| 18 | `ultra_trade_simulator.py` | 81 | ⏳ Pending |
| 19 | `ultra_pnl_analyzer.py` | 82 | ⏳ Pending |
| 20 | `ultra_promotion_manager.py` | 83 | ⏳ Pending |

---

## Detailed Phase Breakdown

### Phase 10: Shadow Real-Data Engine

**Purpose**: Build shadow learning datasets from real signals/trades/PnL

**Inputs**:
- `storage/live/angel_index_ai_signals.csv`
- `storage/live/angel_index_ai_trades_plan.csv`
- `storage/live/angel_index_ai_pnl_log.csv`

**Outputs**:
- `storage/learning_ultra/angel_ultra_shadow_master.parquet`
- `storage/learning_ultra/angel_ultra_shadow_master.csv`

**Key Features**:
- Consolidates real data into shadow master dataset
- Adds columns: `is_win`, `is_loss`, `is_misfire`
- Includes `profile_source` column

---

### Phase 11: Ultra Feature Expander

**Purpose**: Extend features from ~25 to ~100 for Ultra models

**Inputs**:
- `storage/training/angel_index_options_training.csv` (synthetic)
- `storage/learning_ultra/angel_ultra_shadow_master.parquet`

**Outputs**:
- `storage/training/angel_ultra_training.parquet`
- `storage/training/angel_ultra_training.csv`

**New Features**:
- Multi-timeframe momentum (1, 3, 5, 10 steps)
- Volatility windows (short/long)
- Moneyness powers (squared, cube)
- Interaction features
- Regime tags
- Rolling hit rates
- Time-of-day features

---

### Phase 12: Shadow Model Trainer

**Purpose**: Train Ultra models separate from baseline

**Inputs**:
- `storage/training/angel_ultra_training.parquet`

**Outputs**:
- `core/models/angel_one_ultra/*_ultra_model.pkl`
- `core/models/angel_one_ultra/*_ultra_model_meta.json`

**Models**: RandomForest / XGBoost / Ensemble

---

### Phase 13: Hyperparameter Explorer

**Purpose**: Offline hyperparameter exploration

**Inputs**:
- `storage/training/angel_ultra_training.parquet`

**Outputs**:
- `storage/reports_ultra/ultra_hparam_results_{underlying}.csv`

**Functionality**: Grid/random search, validation evaluation, reports only

---

### Phase 14: Risk Regime Classifier

**Purpose**: Classify market regimes (low/medium/high vol, trending/ranging)

**Inputs**:
- `storage/training/angel_ultra_training.parquet`

**Outputs**:
- `storage/training/angel_ultra_training_with_regime.parquet`
- `storage/reports_ultra/ultra_regime_summary.csv`

**Regime Labels**: LOW_VOL, HIGH_VOL, TREND_UP, RANGE

---

### Phase 15: Multi-Consensus Engine

**Purpose**: Compare Baseline vs Ultra predictions

**Inputs**:
- Baseline models + Ultra models
- Sample signals/snapshots

**Outputs**:
- `storage/reports_ultra/ultra_consensus_sample.csv`

**Columns**: baseline_pred, ultra_pred, agree_flag, final_recommendation

---

### Phase 16: Ultra Threshold Lab

**Purpose**: Experiment thresholds on shadow PnL

**Inputs**:
- `storage/learning_ultra/angel_ultra_shadow_master.parquet`

**Outputs**:
- `storage/reports_ultra/ultra_threshold_grid_search.csv`

**Functionality**: Grid search (conf_thresh, score_thresh) vs is_win

---

### Phase 17: Ultra Prediction Engine (Shadow Live)

**Purpose**: Run Ultra models in parallel with baseline for comparison

**Inputs**:
- Live snapshots (same as baseline)

**Outputs**:
- `storage/ultra/angel_ultra_live_shadow_signals.csv`

**Functionality**: Side-by-side baseline vs ultra predictions, shadow only

---

### Phase 18: Ultra Trade Simulator

**Purpose**: Simulate Ultra-only trades on historical snapshots

**Inputs**:
- Historical signals/snapshots
- Ultra models

**Outputs**:
- `storage/ultra/angel_ultra_trade_plan_sim.csv`
- `storage/ultra/angel_ultra_pnl_sim.csv`
- `storage/reports_ultra/ultra_trade_sim_summary.csv`

**Functionality**: Offline simulation, no real trades

---

### Phase 19: Ultra PnL Analyzer

**Purpose**: Advanced analysis of Ultra simulator PnL

**Inputs**:
- `storage/ultra/angel_ultra_pnl_sim.csv`

**Outputs**:
- `storage/reports_ultra/ultra_pnl_report.csv`

**Analysis**: Per-underlying, time-of-day, drawdown curves

---

### Phase 20: Ultra Promotion System

**Purpose**: Compare Baseline vs Ultra, manual promotion only

**Inputs**:
- Baseline models + Ultra models + reports

**Outputs**:
- Comparison table (console)
- Promotion log (if promoted)

**Safety**: Requires explicit keyword (e.g., "PROMOTE_NIFTY"), respects safety switches

---

## Implementation Order

### Batch 1: Foundation (Tasks 0.1-0.3)
1. Create directories
2. Create safety switches
3. Extend profile selector

### Batch 2: Data Pipeline (Phases 10-11)
4. Shadow data engine
5. Feature expander

### Batch 3: Model Training (Phases 12-13)
6. Shadow model trainer
7. Hyperparameter explorer

### Batch 4: Analysis Tools (Phases 14-16)
8. Regime classifier
9. Multi-consensus engine
10. Threshold lab

### Batch 5: Live Shadow (Phases 17-19)
11. Live signals shadow
12. Trade simulator
13. PnL analyzer

### Batch 6: Promotion (Phase 20)
14. Promotion manager

---

## Safety Guarantees

### All Phases Must:
- ✅ Not overwrite baseline files
- ✅ Use separate Ultra directories
- ✅ Respect safety switches
- ✅ Be shadow/experimental only
- ✅ Not trigger real trades
- ✅ Not auto-update configs

### Safety Switches (All False by Default):
- `AUTO_EXECUTE_TRADES`: false
- `AUTO_UPDATE_THRESHOLDS`: false
- `AUTO_RETRAIN_MODELS`: false
- `AUTO_PROMOTE_MODELS`: false
- `AUTO_WRITE_CONFIG`: false

---

## Menu Integration

**New Menu Options**: 73-83 (11 new options)

**Current Last Option**: 72 (Show Live Profiles)

**New Options**:
- 73: Ultra Shadow Data Engine
- 74: Ultra Feature Expander
- 75: Train Ultra Shadow Models
- 76: Ultra Hyperparameter Explorer
- 77: Ultra Risk Regime Classifier
- 78: Ultra Multi-Consensus Analyzer
- 79: Ultra Threshold Lab
- 80: Ultra Live Signals (Shadow)
- 81: Ultra Trade Simulator
- 82: Ultra PnL Analyzer
- 83: Ultra Promotion Manager

---

## File Structure

### New Directories
```
core/
  models/
    angel_one_ultra/          # Ultra models
  config/                     # Ultra configs
  engine/
    ultra_*.py                # 11 new Ultra modules

storage/
  ultra/                      # Ultra live data
  learning_ultra/             # Ultra learning data
  reports_ultra/              # Ultra reports
```

### New Files (Estimated)
- **Config Files**: 2 (safety.json, active_profile.json)
- **Engine Modules**: 12 (ultra_safety.py + 11 phase modules)
- **Total**: ~14 new files

---

## Validation Checklist

### After Each Phase:
- [ ] Module runs without errors
- [ ] Output files created in correct Ultra directories
- [ ] Baseline files untouched
- [ ] Menu option added and working
- [ ] Safety switches respected

### Final Verification:
- [ ] All 11 phases implemented
- [ ] All directories created
- [ ] All menu options working
- [ ] Baseline system still functional
- [ ] Safety switches all false
- [ ] Profile selector supports ULTRA_DEV

---

## Next Steps

1. **Start with Foundation** (Tasks 0.1-0.3)
2. **Implement in Batches** (as outlined above)
3. **Test Each Phase** before moving to next
4. **Verify Safety** at each step
5. **Document Results** as we go

---

**Status**: Ready to begin implementation  
**Estimated Phases**: 11 phases + 3 foundation tasks = 14 total tasks  
**Safety**: All auto-features disabled by default

