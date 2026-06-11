# System3 – Angel One Index Options Pipeline

## 1. Current Components

- run_system3.py main menu + options 1–11
- core/engine/generate_synthetic_angel_training.py
- core/engine/train_angel_models.py
- core/engine/offline_angel_ai_test.py
- wait_and_run_live_watch.py (scheduler)
- core/engine/angel_options_watch.py (menu 6 – single snapshot)
- core/engine/angel_options_watch_loop.py (menu 7 – LIVE watch loop)
- core/engine/angel_options_analyze.py (menu 8 – simple analysis / signals)
- core/engine/build_angel_training_dataset.py (menu 9 – build training dataset)
- core/engine/angel_live_signals.py (menu 11 – LIVE AI signals from models)

## 2. Offline Synthetic Pipeline

```text
generate_synthetic_angel_training.py
    -> storage/training/angel_index_options_training.csv
    -> angel_feature_importance.py
    -> storage/training/feature_importance_*.csv
    -> train_angel_models.py
    -> core/models/angel_one/*_model.pkl
    -> offline_angel_ai_test.py
```

- generate_synthetic_angel_training.py creates synthetic training rows with labels.
- angel_feature_importance.py computes MI per feature per underlying.
- train_angel_models.py trains models using MI-selected features.
- Models + meta saved under core/models/angel_one/.

## 3. Live Market Pipeline

```text
run_system3.py (menu 6) -> core/engine/angel_options_watch.py
    (single Angel One index options snapshot)

run_system3.py (menu 7) or wait_and_run_live_watch.py
    -> core/engine/angel_options_watch_loop.py
    -> storage/live/angel_index_options_watch.csv
    -> core/engine/angel_options_analyze.py (menu 8)
    -> storage/features/angel_index_options_features.csv
    -> core/engine/build_angel_training_dataset.py (menu 9)
    -> storage/training/angel_index_options_training.csv

run_system3.py (menu 11)
    -> core/engine/angel_live_signals.py
    -> uses core/models/angel_one/*_model.pkl
    -> prints / logs LIVE AI signals
```

## 4. AI Models & Accuracy

Current offline performance (synthetic training + MI-selected features):

| Underlying  | Train/Test Accuracy | Notes                                |
|------------|----------------------|--------------------------------------|
| NIFTY      | ≈ 0.98–0.99          | [DONE] MI features, synthetic data   |
| BANKNIFTY  | ≈ 1.00               | [DONE] MI features, synthetic data   |
| FINNIFTY   | ≈ 1.00               | [DONE] MI features, synthetic data   |
| MIDCPNIFTY | ≈ 1.00               | [DONE] MI features, synthetic data   |
| SENSEX     | ≈ 0.99               | [DONE] MI features, synthetic data   |

- [DONE] Synthetic index options training generator
- [DONE] Mutual Information (MI) feature importance per underlying
- [DONE] Angel One index options model training (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX)

## 5. Ultra Integration Phases 31-38 (COMPLETE)

### Status: ✅ **ALL 8 PHASES COMPLETE AND VALIDATED**

**Completion Date**: 2025-11-29  
**Test Results**: 8/8 phases passing (100%)

**Implemented Phases**:
- ✅ Phase 31: Ultra Decision Fusion (Menu: 94)
- ✅ Phase 32: Ultra vs Baseline Comparator (Menu: 95)
- ✅ Phase 33: Ultra Promotion Planner (Menu: 96)
- ✅ Phase 34: Ultra Live Shadow Comparison (Menu: 97)
- ✅ Phase 35: Ultra Decision Auditor (Menu: 98)
- ✅ Phase 36: Ultra Continuous Learning Cycle - CULL (Menu: 99)
- ✅ Phase 37: Ultra Policy & Risk Monitor (Menu: 100)
- ✅ Phase 38: Ultra Governance Summary (Menu: 101)

**Key Features**:
- Decision fusion combining all Ultra outputs
- Baseline comparison for performance evaluation
- Promotion planning (suggestions only, no auto-promotion)
- Shadow trading (logged but never executed)
- Decision auditing against safety limits
- Full learning cycle orchestration
- Policy and risk monitoring
- Board-level governance reporting

**Safety Guarantees**:
- ✅ Ultra-Isolated (no baseline overwrites)
- ✅ Baseline-Protected (all writes to `storage/ultra/`)
- ✅ Read-Only (no auto-execution, no auto-promotion)
- ✅ Error Handling (all exceptions caught and logged)

**Documentation**:
- `docs/system3_phases_31_38_blueprint.md` - Implementation blueprint
- `docs/system3_phases_31_38_complete.md` - Completion documentation
- `docs/system3_phases_31_38_success_report.md` - Success report

## 5.1. Ultra Rollout & Safety Shell Phases 39-45 (COMPLETE)

### Status: ✅ **ALL 7 PHASES IMPLEMENTED**

**Completion Date**: 2025-11-29  
**Implementation Status**: 7/7 phases implemented (100%)

**Implemented Phases**:
- ✅ Phase 39: Ultra Shadow Campaign Manager (Menu: 102)
- ✅ Phase 40: Weekly Governance Pack (Menu: 103)
- ✅ Phase 41: Promotion Executor - Staging Only (Menu: 104)
- ✅ Phase 42: Snapshot & Rollback Manager (Menu: 105, 106)
- ✅ Phase 43: Environment & Broker Guard (Menu: 107)
- ✅ Phase 44: Daily All-In-One Script (OS-level)
- ✅ Phase 45: Documentation & Index Consolidation

**Key Features**:
- Shadow campaign orchestration
- Weekly governance pack aggregation
- Safe promotion staging (never baseline)
- Baseline snapshot and rollback
- Environment and broker separation
- Daily all-in-one health checks
- Comprehensive documentation

**Safety Guarantees**:
- ✅ Ultra-Isolated (no baseline overwrites)
- ✅ Baseline-Protected (snapshots before any changes)
- ✅ Staging-Only (promotion copies to staging, never baseline)
- ✅ Read-Only (all phases read-only by default)
- ✅ Manual-Only (all promotions require explicit approval)

**Documentation**:
- `docs/system3_phases_39_45_ultra_rollout_plan.md` - Implementation plan
- `docs/system3_ultra_master_index.md` - Master index
- `docs/system3_ultra_daily_routine.md` - Daily routine guide
- `docs/system3_phases_39_45_completion_summary.md` - Completion summary
- `docs/system3_phases_39_45_daily_playbook.md` - Daily playbook

## 6. Pending & Planned Upgrades

### ✅ Completed (Batch 1-3)
- [x] Synthetic training generator with advanced features
- [x] Model training with MI-based feature selection
- [x] Offline AI test sampling
- [x] Feature importance analysis (MI)
- [x] MI-based feature selection in training
- [x] Trade decision layer with rule engine
- [x] Offline PnL simulator
- [x] Live AI signals engine
- [x] Trade executor (DRY RUN)
- [x] Daily PnL summary tool
- [x] Intraday PnL monitor
- [x] Daily report generator
- [x] System health watchdog
- [x] Trade lifecycle logger
- [x] Safety validator
- [x] Auto threshold adjuster (recommendations only)
- [x] Confidence calibrator
- [x] Strategy optimizer
- [x] Advanced feature ranker
- [x] Blended model trainer (prepared)
- [x] Enhanced signal scorer
- [x] Alerting system

### 🔄 Post-Monday (Ready but Disabled)
- [ ] Auto-threshold adjustment (infrastructure ready, disabled)
- [ ] LIVE mode executor (infrastructure ready, disabled)
- [ ] Auto PnL simulation (infrastructure ready, disabled)
- [ ] Real data model retraining
- [ ] Threshold optimization on real outcomes

### 📋 Future Enhancements

- [DONE] Synthetic training generator
- [DONE] MI feature importance per underlying
- [DONE] MI-based feature selection in training
- [DONE] Baseline RF models for all five indices
- [DONE] Live AI signals (menu 11) – prediction + logging
- [IN PROGRESS] Trade decision layer (ranking, targets, SL, trade log)
- [IN PROGRESS] Offline PnL simulator for AI trade plans
- [PENDING] Real BUY_CE / BUY_PE trades in live market
- [PENDING] PnL simulator on real trades
- [TODO] Auto-tune thresholds (confidence, score, ATM distance) using PnL statistics
- [TODO] Auto-trade logic (order placement + stoploss execution)
- [TODO] Dashboard visualisation
- [TODO] Replace synthetic data with real Angel live history when available

## 6. Live AI Signals & Trade Decision Layer

- [DONE] Live AI signals engine (menu 11) – models → predictions → signals CSV.
- [DONE] Trade decision layer – convert signals into structured trade plans (entry, target, SL, risk).
- [DONE] PnL simulator (offline) – reconstruct hypothetical trades and compute PnL.
- [DONE] Daily PnL summary tool (menu 15).
- [TODO] Auto-execution layer – actual order placement via Angel SmartAPI (infrastructure ready, disabled).
- [PENDING] Real BUY_CE / BUY_PE trades in live market (monitoring)
- [PENDING] PnL simulator on real trades (when trades available)

## 7. Trade PnL Simulator (Offline)

- [DONE] Read AI signals + trade plans and reconstruct hypothetical trades.
- [DONE] Compute exit reason (TP / SL / TIMEOUT) and PnL % for each trade.
- [DONE] Daily summary (per underlying) with hit-rate, average gain, average loss, and max drawdown.
- [DONE] Auto-calibration hooks (threshold tuner - recommendations only).


