# System3 Phase → File Mapping

**Date**: 2025-11-30  
**Purpose**: Map phase numbers to script paths, outputs, and logs

---

## Phase File Mapping Table

| Phase | Description | Script Path | Function | Output Files | Log Files |
|-------|-------------|-------------|----------|--------------|-----------|
| **10** | Ultra Shadow Data Engine | `core/engine/ultra_shadow_data_engine.py` | `main` | `storage/learning_ultra/angel_ultra_shadow_master.parquet`<br>`storage/learning_ultra/angel_ultra_shadow_master.csv` | - |
| **11** | Ultra Feature Expander | `core/engine/ultra_feature_engineering.py` | `main` | `storage/training/angel_ultra_training.parquet`<br>`storage/training/angel_ultra_training.csv` | - |
| **12** | Train Ultra Shadow Models | `core/engine/ultra_train_models.py` | `main` | `core/models/angel_one_ultra/*.pkl`<br>`core/models/angel_one_ultra/*_meta.json` | - |
| **13** | Ultra Hyperparameter Explorer | `core/engine/ultra_hparam_explorer.py` | `main` | `storage/reports_ultra/ultra_hparam_results_{underlying}.csv` | - |
| **14** | Ultra Risk Regime Classifier | `core/engine/ultra_regime_classifier.py` | `main` | `storage/training/angel_ultra_training_with_regime.parquet`<br>`storage/reports_ultra/ultra_regime_summary.csv` | - |
| **15** | Ultra Multi-Consensus Analyzer | `core/engine/ultra_multi_consensus.py` | `main` | `storage/reports_ultra/ultra_consensus_sample.csv` | - |
| **16** | Ultra Threshold Lab | `core/engine/ultra_threshold_lab.py` | `main` | `storage/reports_ultra/ultra_threshold_grid_search.csv` | - |
| **17** | Ultra Live Signals (Shadow) | `core/engine/ultra_live_signals_shadow.py` | `main` | `storage/ultra/angel_ultra_live_shadow_signals.csv` | - |
| **18** | Ultra Trade Simulator | `core/engine/ultra_trade_simulator.py` | `main` | `storage/ultra/angel_ultra_trade_plan_sim.csv`<br>`storage/ultra/angel_ultra_pnl_sim.csv`<br>`storage/reports_ultra/ultra_trade_sim_summary.csv` | - |
| **19** | Ultra PnL Analyzer | `core/engine/ultra_pnl_analyzer.py` | `main` | `storage/reports_ultra/ultra_pnl_report.csv` | - |
| **20** | Ultra Promotion Manager | `core/engine/ultra_promotion_manager.py` | `main` | `storage/reports_ultra/ultra_promotion_report.json` | - |
| **21** | Adaptive Risk Engine (ARE) | `core/ultra/phase21_adaptive_risk_engine.py` | `run_phase21_adaptive_risk` | `storage/reports_ultra/phase21_risk_evaluations.csv` | - |
| **22** | Dynamic Position Sizing Engine | `core/ultra/phase22_position_sizing.py` | `run_phase22_position_sizing` | - | - |
| **23** | Volatility Regime Impact Engine | `core/ultra/phase23_volatility_impact.py` | `run_phase23_volatility_impact` | - | - |
| **24** | Confidence Drift Analyzer | `core/ultra/phase24_confidence_drift.py` | `run_phase24_confidence_drift` | `storage/reports_ultra/phase24_confidence_drift_report.json` | - |
| **25** | Adaptive Stoploss Engine (ASE) | `core/ultra/phase25_stoploss_engine.py` | `run_phase25_stoploss_engine` | - | - |
| **26** | Adaptive Target Engine (ATE) | `core/ultra/phase26_target_engine.py` | `run_phase26_target_engine` | - | - |
| **27** | Risk-Reward Balancer | `core/ultra/phase27_rr_balancer.py` | `run_phase27_rr_balancer` | - | - |
| **28** | Failure-Mode Auto-Corrector | `core/ultra/phase28_auto_corrector.py` | `run_phase28_auto_corrector` | `storage/reports_ultra/phase28_auto_correction_report.json` | - |
| **29** | Sensitivity Analyzer | `core/ultra/phase29_sensitivity.py` | `run_phase29_sensitivity` | `storage/reports_ultra/phase29_sensitivity_analysis.csv`<br>`storage/reports_ultra/phase29_sensitivity_summary.json` | - |
| **30** | Real-Time Calibration Engine (RTCE) | `core/ultra/phase30_calibration_engine.py` | `run_phase30_calibration` | `storage/reports_ultra/phase30_calibration_results.csv` | - |
| **31** | Ultra Decision Fusion Layer | `core/engine/system3_phase31_ultra_fusion.py` | `run_phase31_fusion` | `storage/ultra/phase31_ultra_fused_decisions.csv`<br>`storage/ultra/phase31_ultra_fused_decisions_summary.json` | - |
| **32** | Ultra vs Baseline Comparator | `core/engine/system3_phase32_ultra_vs_baseline.py` | `run_phase32_comparison` | `storage/ultra/phase32_ultra_vs_baseline_comparison.csv`<br>`storage/ultra/phase32_ultra_vs_baseline_summary.md` | - |
| **33** | Ultra Promotion Planner | `core/engine/system3_phase33_promotion_planner.py` | `run_phase33_promotion_planner` | `storage/ultra/phase33_promotion_plan.json`<br>`storage/ultra/phase33_promotion_plan.md` | - |
| **34** | Ultra Live Shadow Comparison | `core/engine/system3_phase34_ultra_shadow_exec.py` | `run_phase34_shadow_once` | `storage/live/angel_index_ai_ultra_trades_shadow.csv` | - |
| **35** | Ultra Decision Auditor | `core/engine/system3_phase35_ultra_auditor.py` | `run_phase35_audit` | `storage/ultra/phase35_decision_audit.csv`<br>`storage/ultra/phase35_decision_audit_report.md` | - |
| **36** | Ultra Continuous Learning Cycle (CULL) | `core/engine/system3_phase36_cull_orchestrator.py` | `run_phase36_cull_full_cycle` | `storage/ultra/phase36_cull_execution_log.md` | - |
| **37** | Ultra Policy & Risk Monitor | `core/engine/system3_phase37_policy_risk_monitor.py` | `run_phase37_policy_risk_dashboard` | `storage/ultra/phase37_policy_risk_dashboard.md` | - |
| **38** | Ultra Governance Summary | `core/engine/system3_phase38_governance_summary.py` | `run_phase38_governance_summary` | `storage/ultra/phase38_governance_summary.md` | - |
| **39** | Ultra Shadow Campaign Manager | `core/engine/system3_phase39_shadow_campaign.py` | `run_phase39_shadow_campaign` | `storage/live/angel_index_ai_ultra_trades_shadow.csv` | `storage/logs_ultra/system3_phases_39_45.log` |
| **40** | Weekly Ultra vs Baseline Governance Pack | `core/engine/system3_phase40_weekly_governance_pack.py` | `run_phase40_weekly_pack` | `storage/ultra/weekly_governance_pack_*.md` | - |
| **41** | Ultra Promotion Execution Framework | `core/engine/system3_phase41_promotion_executor.py` | `run_phase41_promotion_executor` | - | - |
| **42** | Model Snapshot & Rollback Manager | `core/engine/system3_phase42_snapshot_manager.py` | `run_phase42_snapshot_create` | `storage/snapshots/YYYYMMDD_HHMMSS/` | - |
| **43** | Environment & Broker Guard | `core/engine/system3_phase43_env_guard.py` | `run_phase43_env_guard` | - | - |
| **46** | Ultra Meta Fusion Model | `core/ultra/phase46_meta_fusion.py` | `run_phase46_meta_fusion` | `storage/ultra/ph46_ph55/phase46_meta_fusion_predictions.csv`<br>`storage/ultra/ph46_ph55/phase46_meta_fusion_weights.json` | - |
| **47** | 7D Confidence Vector Engine | `core/ultra/phase47_confidence_vector.py` | `run_phase47_confidence_vector` | `storage/ultra/ph46_ph55/phase47_confidence_vector_7d.csv`<br>`storage/ultra/ph46_ph55/phase47_confidence_trends.json` | - |
| **48** | Real Market Error Scanner | `core/ultra/phase48_error_scanner.py` | `run_phase48_error_scanner` | `storage/ultra/ph46_ph55/phase48_error_scan_report.csv`<br>`storage/ultra/ph46_ph55/phase48_error_patterns.json` | - |
| **49** | Smart Risk Regulator (AI Suggestions Only) | `core/ultra/phase49_risk_regulator.py` | `run_phase49_risk_regulator` | `storage/ultra/ph46_ph55/phase49_risk_suggestions.json`<br>`storage/ultra/ph46_ph55/phase49_risk_analysis.md` | - |
| **50** | Ultra Prediction Explainer | `core/ultra/phase50_prediction_explainer.py` | `run_phase50_prediction_explainer` | `storage/ultra/ph46_ph55/phase50_prediction_explanations.csv`<br>`storage/ultra/ph46_ph55/phase50_feature_importance.json` | - |
| **51** | Real-Time Probability Engine | `core/ultra/phase51_probability_engine.py` | `run_phase51_probability_engine` | `storage/ultra/ph46_ph55/phase51_probability_distributions.csv`<br>`storage/ultra/ph46_ph55/phase51_probability_forecasts.json` | - |
| **52** | Multi-Broker Abstraction (Shadow-Only) | `core/ultra/phase52_multi_broker.py` | `run_phase52_multi_broker` | `storage/ultra/ph46_ph55/phase52_broker_abstraction_test.json`<br>`storage/ultra/ph46_ph55/phase52_broker_compatibility.md` | - |
| **53** | Ultra Monitoring AI Agent | `core/ultra/phase53_monitoring_agent.py` | `run_phase53_monitoring_agent` | `storage/ultra/ph46_ph55/phase53_monitoring_report.md`<br>`storage/ultra/ph46_ph55/phase53_agent_suggestions.json` | - |
| **54** | Real Outcome Back-Reconstruction | `core/ultra/phase54_back_reconstruction.py` | `run_phase54_back_reconstruction` | `storage/ultra/ph46_ph55/phase54_reconstruction_report.csv`<br>`storage/ultra/ph46_ph55/phase54_what_if_analysis.json` | - |
| **55** | Ultra Intelligence Dashboard | `core/ultra/phase55_intelligence_dashboard.py` | `run_phase55_intelligence_dashboard` | `storage/ultra/ph46_ph55/phase55_intelligence_dashboard.md`<br>`storage/ultra/ph46_ph55/phase55_dashboard_data.json` | - |

---

## Output Directory Summary

### Storage Locations

- **`storage/ultra/`** - Main Ultra outputs (phases 31-43, 46-55)
- **`storage/ultra/ph46_ph55/`** - Phases 46-55 specific outputs
- **`storage/reports_ultra/`** - Ultra reports (phases 21-30)
- **`storage/learning_ultra/`** - Ultra learning data (phase 10)
- **`storage/training/`** - Training data (phases 11-12)
- **`storage/live/`** - Live trading data (phases 34, 39)
- **`storage/snapshots/`** - Model snapshots (phase 42)
- **`storage/logs_ultra/`** - Ultra logs (phase 39)

---

## Notes

- Phases 1-9: Baseline phases (not mapped here)
- Phases 44-45: Reserved for future use
- All paths are relative to project root: `C:\Genesis_System3`
- Most phases have no dedicated log files (logging to console/storage/ultra)

---

**Last Updated**: 2025-11-30

