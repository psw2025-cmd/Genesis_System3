# System3 Ultra Control Panel - Menu Structure

**Date**: 2025-11-29  
**Version**: 1.0  
**Status**: Complete

---

## Overview

The System3 Ultra Control Panel (`system3_ultra.py`) provides a unified menu interface for all System3 operations, organized into logical sections.

**Total Menu Options**: 107+ (including operational phases and system tools)

---

## Menu Structure

### Operational Phases (OP1-OP6)

Quick shortcuts for common workflows:

| Option | Name | Module | Function |
|--------|------|--------|----------|
| OP1 | Pre-Market Diagnostic | `dhan_market_warmup_scanner` | `main()` |
| OP2 | Live Signal Generation | `dhan_live_ai_signals` | `main()` |
| OP3 | Trade Decision & Planning | `dhan_trade_decision` | `main()` |
| OP4 | Post-Market Analysis | `dhan_daily_learning_digest` | `main()` |
| OP5 | Weekly Governance Review | `system3_phase40_weekly_governance_pack` | `run_phase40_weekly_pack()` |
| OP6 | Ultra Experiments | (Menu) | - |

---

### Baseline Core Operations (1-50)

| Option | Name | Module | Function |
|--------|------|--------|----------|
| 1 | Core boot | `main_launcher` | `main()` |
| 2 | Health check | `health_check` | `main()` |
| 3 | Test data pipeline | `test_data_pipeline` | `main()` |
| 4 | Test Dhan API | `test_angelone_api` | `main()` |
| 5 | Test Dhan instruments | `test_angelone_instruments` | `main()` |
| 6 | Index options watch (single) | `dhan_options_watch` | `main()` |
| 7 | Index options LIVE watch loop | `dhan_options_watch_loop` | `main()` |
| 8 | Analyze index options log | `dhan_options_analyze` | `main()` |
| 9 | Build training dataset | `build_dhan_training_dataset` | `main()` |
| 10 | Train models | `train_dhan_models` | `main()` |
| 11 | LIVE AI signals | `dhan_live_ai_signals` | `main()` |
| 12 | Synthetic backtest (CONSERVATIVE) | `dhan_synthetic_backtester` | `run_backtest(profile="CONSERVATIVE")` |
| 13 | Synthetic backtest (DEV) | `dhan_synthetic_backtester` | `run_backtest(profile="DEV")` |
| 14 | Trade executor (DRY RUN) | `dhan_trade_executor` | `execute_dry_run()` |
| 15 | Daily PnL summary | `dhan_daily_pnl_summary` | `main()` |
| 16 | Intraday PnL monitor | `dhan_intraday_pnl_monitor` | `main()` |
| 17 | Daily report generator | `dhan_daily_report_generator` | `main()` |
| 18 | System health check | `dhan_watchdog_recovery` | `main()` |
| 19 | Auto threshold adjuster | `dhan_auto_threshold_adjuster` | `main()` |
| 20 | Confidence calibrator | `dhan_confidence_calibrator` | `main()` |
| 21 | Strategy optimizer | `dhan_strategy_optimizer` | `main()` |
| 22 | Advanced feature ranker | `dhan_feature_ranker` | `main()` |
| 23 | Blended model trainer | `dhan_blended_model_trainer` | `main()` |
| 24 | Market intelligence dashboard | `dhan_market_intelligence_dashboard` | `main()` |
| 25 | Action layer validator | `dhan_trade_validator_v2` | `main()` |
| 26 | Market profile analyzer | `dhan_market_profile` | `main()` |
| 27 | Safety layer V2 check | `dhan_safety_layer_v3` | `main()` |
| 28 | Real outcome logger | `dhan_real_outcome_logger` | `main()` |
| 29 | Signal vs outcome analyzer | `dhan_signal_outcome_analyzer` | `main()` |
| 30 | Misfire detector | `dhan_misfire_detector` | `main()` |
| 31 | Real threshold recommender | `dhan_real_threshold_recommender` | `main()` |
| 32 | Risk profile optimizer | `dhan_risk_profile_optimizer` | `main()` |
| 33 | Real data extractor | `dhan_real_data_extractor` | `main()` |
| 34 | Blended dataset builder | `dhan_blended_dataset_builder` | `main()` |
| 35 | Blended model trainer V2 | `dhan_blended_model_trainer_v2` | `main()` |
| 36 | Daily learning report | `dhan_daily_learning_report` | `main()` |
| 37 | Rolling 7-day dashboard | `dhan_rolling_learning_dashboard` | `main()` |
| 38 | Blended model trainer V2 (Enhanced) | `dhan_blended_model_trainer_v2` | `main()` |
| 39 | Ultra-Mode prep layer | `dhan_ultramode_prep` | `main()` |
| 40 | Daily auto-reports | `dhan_daily_auto_reports` | `main()` |
| 41 | Weekly summary report | `dhan_weekly_summary_report` | `main()` |
| 42 | Monday morning diagnostic | `dhan_monday_diagnostic` | `main()` |
| 43 | Report auto-scheduler | `dhan_report_scheduler` | `main()` |
| 44 | Live snapshot reasoner | `dhan_live_snapshot_reasoner` | `main()` |
| 45 | Outcome confidence analyzer | `dhan_outcome_confidence_analyzer` | `main()` |
| 46 | Adaptive volatility map | `dhan_adaptive_volatility_map` | `main()` |
| 47 | Safety layer V3 | `dhan_safety_layer_v3` | `main()` |
| 48 | Market warmup scanner | `dhan_market_warmup_scanner` | `main()` |
| 49 | Signal record buffer | `dhan_signal_record_buffer` | `main()` |
| 50 | Environment consistency checker | `dhan_env_consistency_checker` | `main()` |

---

### Real-Data Learning Cycle (51-64)

| Option | Name | Module | Function |
|--------|------|--------|----------|
| 51 | Real data capture starter | `dhan_real_data_capture_starter` | `main()` |
| 52 | Real signal collector V2 | `dhan_real_signal_collector_v2` | `main()` |
| 53 | Outcome placeholder generator | `dhan_outcome_placeholder_generator` | `main()` |
| 54 | Market regime recorder | `dhan_market_regime_recorder` | `main()` |
| 55 | Unified outcome logger V3 | `dhan_unified_outcome_logger_v3` | `main()` |
| 56 | Misfire classifier V2 | `dhan_misfire_classifier_v2` | `main()` |
| 57 | Daily learning digest | `dhan_daily_learning_digest` | `main()` |
| 58 | Real threshold recommender V3 | `dhan_real_threshold_reco_v3` | `main()` |
| 59 | Risk profile optimizer V3 | `dhan_risk_profile_optimizer_v3` | `main()` |
| 60 | Feature drift analyzer | `dhan_feature_drift_analyzer` | `main()` |
| 61 | Performance consistency checker | `dhan_performance_consistency_checker` | `main()` |
| 62 | Dataset merger (Real + Synthetic) | `dhan_dataset_merger_real_synth_v1` | `main()` |
| 63 | Blended training orchestrator (Dry-Run) | `dhan_blended_training_orchestrator_dryrun` | `main()` |
| 64 | Ultra-Mode readiness report | `dhan_ultra_mode_readiness_report` | `main()` |

---

### Ultra Observability (65-69)

| Option | Name | Module | Function |
|--------|------|--------|----------|
| 65 | Ultra health tree | `dhan_ultra_health_tree` | `main()` |
| 66 | Latency drift observatory | `dhan_latency_drift_observatory` | `main()` |
| 67 | Failure point predictor | `dhan_failure_point_predictor` | `main()` |
| 68 | Execution readiness auditor | `dhan_execution_readiness_auditor` | `main()` |
| 69 | Ultra dashboard (Read-Only) | `dhan_ultra_dashboard_readonly` | `main()` |

---

### Master Dataset & Model Tools (70-72)

| Option | Name | Module | Function |
|--------|------|--------|----------|
| 70 | Build real master dataset | `dhan_real_master_dataset` | `main()` |
| 71 | Train real+synthetic blended models (V3) | `dhan_blended_training_v3` | `main()` |
| 72 | Show live profiles & model sources | `dhan_model_selector` | `main()` |

---

### Ultra Shadow Data & Features (73-79)

| Option | Name | Module | Function |
|--------|------|--------|----------|
| 73 | Ultra shadow data engine | `ultra_shadow_data_engine` | `main()` |
| 74 | Ultra feature expander | `ultra_feature_engineering` | `main()` |
| 75 | Train Ultra shadow models | `ultra_train_models` | `main()` |
| 76 | Ultra hyperparameter explorer | `ultra_hparam_explorer` | `main()` |
| 77 | Ultra risk regime classifier | `ultra_regime_classifier` | `main()` |
| 78 | Ultra multi-consensus analyzer | `ultra_multi_consensus` | `main()` |
| 79 | Ultra threshold lab | `ultra_threshold_lab` | `main()` |

---

### Ultra Live & Simulation (80-83)

| Option | Name | Module | Function |
|--------|------|--------|----------|
| 80 | Ultra live signals (Shadow) | `ultra_live_signals_shadow` | `main()` |
| 81 | Ultra trade simulator | `ultra_trade_simulator` | `main()` |
| 82 | Ultra PnL analyzer | `ultra_pnl_analyzer` | `main()` |
| 83 | Ultra promotion manager | `ultra_promotion_manager` | `main()` |

---

### Ultra Risk-Adaptive Intelligence (84-93)

| Option | Name | Module | Function |
|--------|------|--------|----------|
| 84 | Phase 21: Adaptive Risk Engine (ARE) | `core.ultra.phase21_adaptive_risk_engine` | `main()` |
| 85 | Phase 22: Dynamic Position Sizing | `core.ultra.phase22_position_sizing` | `main()` |
| 86 | Phase 23: Volatility Regime Impact | `core.ultra.phase23_volatility_impact` | `main()` |
| 87 | Phase 24: Confidence Drift Analyzer | `core.ultra.phase24_confidence_drift` | `main()` |
| 88 | Phase 25: Adaptive Stoploss Engine (ASE) | `core.ultra.phase25_stoploss_engine` | `main()` |
| 89 | Phase 26: Adaptive Target Engine (ATE) | `core.ultra.phase26_target_engine` | `main()` |
| 90 | Phase 27: Risk-Reward Balancer | `core.ultra.phase27_rr_balancer` | `main()` |
| 91 | Phase 28: Failure-Mode Auto-Corrector | `core.ultra.phase28_auto_corrector` | `main()` |
| 92 | Phase 29: Sensitivity Analyzer | `core.ultra.phase29_sensitivity` | `main()` |
| 93 | Phase 30: Real-Time Calibration Engine (RTCE) | `core.ultra.phase30_calibration_engine` | `main()` |

---

### Ultra Integration & Governance (94-101)

| Option | Name | Module | Function |
|--------|------|--------|----------|
| 94 | Phase 31: Decision Fusion | `system3_phase31_ultra_fusion` | `run_phase31_fusion()` |
| 95 | Phase 32: vs Baseline Comparator | `system3_phase32_ultra_vs_baseline` | `run_phase32_comparison()` |
| 96 | Phase 33: Promotion Planner | `system3_phase33_promotion_planner` | `run_phase33_promotion_planner()` |
| 97 | Phase 34: Live Shadow Comparison | `system3_phase34_ultra_shadow_exec` | `run_phase34_shadow_once()` |
| 98 | Phase 35: Decision Auditor | `system3_phase35_ultra_auditor` | `run_phase35_audit()` |
| 99 | Phase 36: Continuous Learning Cycle (CULL) | `system3_phase36_cull_orchestrator` | `run_phase36_cull_full_cycle()` |
| 100 | Phase 37: Policy & Risk Monitor | `system3_phase37_policy_risk_monitor` | `run_phase37_policy_risk_dashboard()` |
| 101 | Phase 38: Governance Summary | `system3_phase38_governance_summary` | `run_phase38_governance_summary()` |

---

### Ultra Rollout & Safety (102-107)

| Option | Name | Module | Function |
|--------|------|--------|----------|
| 102 | Phase 39: Shadow Campaign | `system3_phase39_shadow_campaign` | `run_phase39_shadow_campaign()` |
| 103 | Phase 40: Weekly Governance Pack | `system3_phase40_weekly_governance_pack` | `run_phase40_weekly_pack()` |
| 104 | Phase 41: Prepare Ultra Promotion (Staging) | `system3_phase41_promotion_executor` | `run_phase41_promotion_executor()` |
| 105 | Phase 42: Take Baseline Snapshot | `system3_phase42_snapshot_manager` | `run_phase42_snapshot_create()` |
| 106 | Phase 42: List / View Snapshots | `system3_phase42_snapshot_manager` | `run_phase42_snapshot_list()` |
| 107 | Phase 43: Environment & Broker Guard | `system3_phase43_env_guard` | `run_phase43_env_guard()` |

---

### System Tools

| Option | Name | Description |
|--------|------|-------------|
| S | Safety Status Check | Display current safety switch status |
| V | Run Full Validation | Execute full validation engine |
| L | View Latest Logs | Display last 50 lines of log file |
| H | Help / Documentation | Show documentation file locations |
| 0 | Exit | Exit the control panel |

---

## Safety Notes

### All Operations Are:
- ✅ **Ultra-Isolated**: No baseline files modified
- ✅ **Baseline-Protected**: All writes go to Ultra directories
- ✅ **Read-Only**: No automatic config changes
- ✅ **Shadow-Mode**: No real trades executed
- ✅ **Manual Promotion**: Requires explicit approval

### Safety Checks Performed:
1. Auto-execution status
2. Auto-simulate PnL status
3. Ultra auto-execute status
4. Ultra auto-update status
5. Ultra auto-retrain status
6. Ultra auto-promote status

---

## Module Paths

All modules are located in:
- **Baseline**: `core/engine/`
- **Ultra Phases 21-30**: `core/ultra/`
- **Ultra Phases 31-45**: `core/engine/`

---

**Last Updated**: 2025-11-29  
**Status**: Complete

