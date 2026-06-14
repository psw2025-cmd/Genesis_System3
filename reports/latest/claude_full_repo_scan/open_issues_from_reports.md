# Existing Proof Report Snapshot

## `docs/project_control/SYSTEM3_MASTER_STATUS.md`
```
# System3 Master Status

Generated UTC: 2026-06-11T17:10:55.741392+00:00

## Current verified status

- Master verdict: `TRADE_READY_BLOCKED`
- Trade ready: `False`
- Live trading enabled: `False`
- Mode: `Analyzer/Paper only`

## Gate results

| Gate | Status | Pass |
|---|---|---:|
| `safety_and_secrets` | `FAIL` | `False` |
| `repo_authority_and_duplicate_control` | `PASS_WITH_WARNINGS` | `True` |
| `deployment_and_endpoint_proof` | `PASS_WITH_WARNINGS` | `True` |
| `fresh_data_automation_proof` | `PASS_WITH_WARNINGS` | `True` |
| `model_training_load_proof` | `PASS_WITH_WARNINGS` | `True` |
| `recent_backtest_walkforward_proof` | `PASS_WITH_WARNINGS` | `True` |
| `analyzer_paper_lifecycle_proof` | `PASS_WITH_WARNINGS` | `True` |
| `dashboard_truth_proof` | `PASS_WITH_WARNINGS` | `True` |

## Open blockers

- `safety_and_secrets:forbidden_secret_style_files_tracked`
- `safety_and_secrets:possible_secret_like_content_in_tracked_text`

## Operating rule

- Analyzer/Paper mode only.
- Live trading remains disabled.
- Do not commit private keys, broker credentials, `.env`, OTP, TOTP, PIN, or passwords.
- Auto-fix may repair safe proof/report/config issues only; it must not bypass broker login, secrets, live trading safety, or unknown position-state blocks.

## Next automatic work queue

1. Keep this master control-plane workflow scheduled and green.
2. Run secure fresh broker data proof in broker-enabled runtime.
3. Run model-load/training proof with metrics.
4. Run recent backtest/walk-forward proof with costs/slippage.
5. Run analyzer paper lifecycle proof: signal → order → fill/sim-fill → exit → P&L.
6. Run dashboard API/browser truth proof.
7. Accumulate multi-day stability before any live enablement checklist.

```
## `reports/latest/full_repo_verification/summary.json`
```
{
  "blockers": [
    "workflow_push_without_rebase_detected"
  ],
  "command_summary": {
    "failed": 0,
    "passed": 214,
    "timed_out": 0,
    "total": 214
  },
  "critical_missing_count": 0,
  "generated_utc": "2026-06-11T20:18:47.306337+00:00",
  "mode": "Analyzer/Paper only; live trading disabled",
  "runner": {
    "cwd": "/home/runner/work/Genesis_System3/Genesis_System3",
    "platform": "Linux-6.17.0-1018-azure-x86_64-with-glibc2.39",
    "python": "3.12.3 (main, Mar 23 2026, 19:04:32) [GCC 13.3.0]"
  },
  "static_scan_counts": {
    "hardcoded_localhost_mentions": 234,
    "live_mode_mentions": 533,
    "todo_fixme_mentions": 38,
    "workflow_push_without_rebase": 16
  },
  "tracked_file_count": 3711,
  "trade_ready": false,
  "verdict": "FULL_REPO_VERIFICATION_COMPLETE_WITH_BLOCKERS"
}

```
## `reports/latest/safety_and_secrets/summary.json`
```
{
  "auto_repair_allowed": false,
  "blockers": [
    "forbidden_secret_style_files_tracked",
    "possible_secret_like_content_in_tracked_text"
  ],
  "evidence": {
    "render_safety": {
      "live_trading_default_zero_or_false": true,
      "mentions_live_trading_enabled": true,
      "mentions_public_backend_url": false,
      "mentions_system3_mode": true,
      "render_yaml_exists": true
    },
    "requirements_contains_logzero": true,
    "requirements_contains_smartapi_python": true,
    "secret_content_finding_count": 4,
    "secret_content_findings": [
      {
        "file": "config/.env.example",
        "pattern": "(?i)(api[_-]?key|secret[_-]?key|client[_-]?secret|totp|otp|pin|password)\\s*[:=]\\"
      },
      {
        "file": "core/brokers/angel_one/broker.py",
        "pattern": "(?i)(api[_-]?key|secret[_-]?key|client[_-]?secret|totp|otp|pin|password)\\s*[:=]\\"
      },
      {
        "file": "dashboard/frontend/dist/assets/index-D39Quml5.js",
        "pattern": "(?i)(api[_-]?key|secret[_-]?key|client[_-]?secret|totp|otp|pin|password)\\s*[:=]\\"
      },
      {
        "file": "docs/ANGEL_BROKER_API_AND_TOTP_ANALYSIS.md",
        "pattern": "(?i)(api[_-]?key|secret[_-]?key|client[_-]?secret|totp|otp|pin|password)\\s*[:=]\\"
      }
    ],
    "secret_style_filename_count": 2,
    "secret_style_filenames": [
      "config/.env.example",
      "reports/latest/safety_and_secrets/summary.json"
    ],
    "tracked_file_count": 3705
  },
  "gate": "safety_and_secrets",
  "next_action": "Keep Analyzer/Paper mode. If any secret finding appears, remove it outside automation and rotate credentials.",
  "pass": false,
  "status": "FAIL",
  "warnings": []
}

```
## `reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json`
```
{
  "backtest_candidate_count": 265,
  "blockers": [
    "fresh_training_not_proven",
    "recent_backtest_not_proven",
    "live_market_analyzer_paper_trade_not_proven",
    "full_working_dashboard_not_proven"
  ],
  "dashboard_candidate_count": 66,
  "data_history_candidate_count": 236,
  "model_training_candidate_count": 224,
  "paper_analyzer_candidate_count": 176,
  "proven_backtest_recent": false,
  "proven_dashboard_full_ui_live": false,
  "proven_live_market_paper_trade_today": false,
  "proven_model_training_fresh": false,
  "render_live_trading_disabled": true,
  "runtime_backend_present": true,
  "smartapi_dependency_present": true,
  "trade_ready": false,
  "verdict": "NOT_TRADE_READY_UNTIL_BLOCKERS_PROVEN_CLEAR"
}

```
## `reports/latest/proof_status_matrix/proof_status_matrix.json`
```
{
  "generated_utc": "2026-06-11T17:10:55.740920+00:00",
  "mode": "Analyzer/Paper only; live trading disabled",
  "optional_missing_count": 0,
  "pending_count": 0,
  "published_count": 8,
  "required_missing_count": 0,
  "rows": [
    {
      "blockers": [
        "forbidden_secret_style_files_tracked",
        "possible_secret_like_content_in_tracked_text"
      ],
      "name": "safety_and_secrets",
      "pass": false,
      "path": "reports/latest/safety_and_secrets/summary.json",
      "required": true,
      "status": "FAIL",
      "warnings": []
    },
    {
      "blockers": [],
      "name": "repo_authority_and_duplicate_control",
      "pass": true,
      "path": "reports/latest/repo_authority_and_duplicate_control/summary.json",
      "required": true,
      "status": "PASS_WITH_WARNINGS",
      "warnings": [
        "duplicate_basename_candidates_need_runtime_classification"
      ]
    },
    {
      "blockers": [],
      "name": "deployment_and_endpoint_proof",
      "pass": true,
      "path": "reports/latest/deployment_and_endpoint_proof/summary.json",
      "required": true,
      "status": "PASS_WITH_WARNINGS",
      "warnings": [
        "public_backend_url_not_configured_endpoint_live_probe_skipped"
      ]
    },
    {
      "blockers": [],
      "name": "fresh_data_automation_proof",
      "pass": true,
      "path": "reports/latest/fresh_data_automation_proof/summary.json",
      "required": true,
      "status": "PASS_WITH_WARNINGS",
      "warnings": [
        "binance_crypto_data_candidates_not_proven",
        "angel_broker_secrets_not_available_to_ci_data_live_probe_skipped"
      ]
    },
    {
      "blockers": [],
      "name": "model_training_load_proof",
      "pass": true,
      "path": "reports/latest/model_training_load_proof/summary.json",
      "required": true,
      "status": "PASS_WITH_WARNINGS",
      "warnings": [
        "fresh_training_accuracy_metrics_not_proven",
        "model_promotion_remains_blocked_without_policy"
      ]
    },
    {
      "blockers": [],
      "name": "recent_backtest_walkforward_proof",
      "pass": true,
      "path": "reports/latest/recent_backtest_walkforward_proof/summary.json",
      "required": true,
      "status": "PASS_WITH_WARNINGS",
      "warnings": [
        "recent_costed_walkforward_result_not_proven"
      ]
    },
    {
      "blockers": [],
      "name": "analyzer_paper_lifecycle_proof",
      "pass": true,
      "path": "reports/latest/analyzer_paper_lifecycle_proof/summary.json",
      "required": true,
      "status": "PASS_WITH_WARNINGS",
      "warnings": [
        "full_signal_to_exit_pnl_lifecycle_not_proven"
      ]
    },
    {
      "blockers": [],
      "name": "dashboard_truth_proof",
      "pass": true,
      "path": "reports/latest/dashboard_truth_proof/summary.json",
      "required": true,
      "status": "PASS_WITH_WARNINGS",
      "warnings": [
        "browser_screenshot_truth_not_proven_in_ci"
      ]
    }
  ],
  "trade_ready": false,
  "verdict": "TRADE_READY_BLOCKED"
}

```
## `reports/latest/fresh_data_automation_proof/summary.json`
```
{
  "auto_repair_allowed": true,
  "blockers": [],
  "evidence": {
    "angel_india_candidate_count": 392,
    "angel_india_candidates_sample": [
      "\"docs/Phases 311\\342\\200\\223330 = Integrity + Anti-corruption + Observability layer for System3.md\"",
      "CHANGELOG.md",
      "MONITOR_OPTIONCHAIN.bat",
      "OPTIONCHAIN_MASTER_GUIDE.md",
      "OPTIONS_TRADING_OPTIMIZATION_PLAN.md",
      "OPTION_CHAIN_AUTOMATION_README.md",
      "OptionChain_Master_v3_AI_FINAL.csv",
      "OptionChain_Master_v3_AI_FINAL.xlsx",
      "PHASE_392_ENSEMBLE_INTEGRATION.md",
      "START_OPTION_CHAIN_AUTOMATION.bat",
      "SYSTEM3_ANGEL_ONE_ROADMAP.md",
      "UPDATE_OPTIONCHAIN_MASTER.bat",
      "WORLD_CLASS_OPTION_CHAIN_SYSTEM_COMPLETE.md",
      "config/angel_automation_config.json",
      "core/broker/angel_live_order_wrapper.py",
      "core/brokers/angel_one/__init__.py",
      "core/brokers/angel_one/broker.py",
      "core/brokers/angel_one/instruments.py",
      "core/engine/angel_adaptive_volatility_map.py",
      "core/engine/angel_alerting_system.py",
      "core/engine/angel_auto_threshold_adjuster.py",
      "core/engine/angel_automation_config.py",
      "core/engine/angel_blended_dataset_builder.py",
      "core/engine/angel_blended_model_trainer.py",
      "core/engine/angel_blended_model_trainer_v2.py",
      "core/engine/angel_blended_training_orchestrator_dryrun.py",
      "core/engine/angel_blended_training_v3.py",
      "core/engine/angel_breakout_predictor.py",
      "core/engine/angel_confidence_calibrator.py",
      "core/engine/angel_confidence_score_fusion.py",
      "core/engine/angel_daily_auto_reports.py",
      "core/engine/angel_daily_learning_digest.py",
      "core/engine/angel_daily_learning_report.py",
      "core/engine/angel_daily_pnl_summary.py",
      "core/engine/angel_daily_report_generator.py",
      "core/engine/angel_dataset_merger_real_synth_v1.py",
      "core/engine/angel_dynamic_sl_tp.py",
      "core/engine/angel_enhanced_signal_scorer.py",
      "core/engine/angel_entry_optimizer.py",
      "core/engine/angel_env_consistency_checker.py",
      "core/engine/angel_execution_guardrail.py",
      "core/engine/angel_execution_readiness_auditor.py",
      "core/engine/angel_executor_live_prep.py",
      "core/engine/angel_exit_optimizer.py",
      "core/engine/angel_failure_point_predictor.py",
      "core/engine/angel_feature_drift_analyzer.py",
      "core/engine/angel_feature_importance.py",
      "core/engine/angel_feature_ranker.py",
      "core/engine/angel_features.py",
      "core/engine/angel_intraday_pnl_monitor.py",
      "core/engine/angel_iv_estimator.py",
      "core/engine/angel_latency_drift_observatory.py",
      "core/engine/angel_live_ai_signals.py",
      "core/engine/angel_live_ai_signals_v2.py",
      "core/engine/angel_live_signals.py",
      "core/engine/angel_live_snapshot_reasoner.py",
      "core/engine/angel_market_intelligence_dashboard.py",
      "core/engine/angel_market_profile.py",
      "core/engine/angel_market_regime_classifier.py",
      "core/engine/angel_market_regime_recorder.py",
      "core/engine/angel_market_warmup_scanner.py",
      "core/engine/angel_microtrend_recognizer.py",
      "core/engine/angel_misfire_classifier_v2.py",
      "core/engine/angel_misfire_detector.py",
      "core/engine/angel_model_selector.py",
      "core/engine/angel_monday_diagnostic.py",
      "core/engine/angel_multi_model_agreement.py",
      "core/engine/angel_multi_resolution_labels.py",
      "core/engine/angel_multi_timeframe_confirmation.py",
      "core/engine/angel_options_analyze.py",
      "core/engine/angel_options_watch.py",
      "core/engine/angel_options_watch_loop.py",
      "core/engine/angel_outcome_confidence_analyzer.py",
      "core/engine/angel_outcome_placeholder_generator.py",
      "core/engine/angel_overtrade_detector.py",
      "core/engine/angel_performance_consistency_checker.py",
      "core/engine/angel_pnl_dummy_seed.py",
      "core/engine/angel_pnl_simulator.py",
      "core/engine/angel_premium_spot_classifier.py",
      "core/engine/angel_real_data_capture_starter.py"
    ],
    "binance_crypto_candidate_count": 0,
    "binance_crypto_candidates_sample": [],
    "data_candidate_count": 500,
    "data_candidates_sample": [
      "\"docs/Phases 311\\342\\200\\223330 = Integrity + Anti-corruption + Observability layer for System3.md\"",
      ".github/workflows/external-data-yahoo-proof.yml",
      "CHANGELOG.md",
      "COMPREHENSIVE_CSV_VERIFICATION_REPORT.md",
      "CSV_DATA_STATUS_REPORT_20251208.md",
      "CSV_FILES_COMPLETE_VERIFICATION.md",
      "CSV_FILES_FINAL_REPORT.md",
      "CSV_FILES_VERIFICATION_AND_FIXES.md",
      "CSV_FIXES_AND_WARNINGS_FINAL_SUMMARY.md",
      "CSV_VERIFICATION_COMPLETE.md",
      "DATA_COMPLETENESS_FIX_COMPLETE.md",
      "DIAGNOSTIC_PHASES_1_200_DATA.json",
      "LIVE_CHAIN_ISSUES_AND_RECOMMENDATIONS.md",
      "MONITOR_OPTIONCHAIN.bat",
      "OPTIONCHAIN_MASTER_GUIDE.md"
```
## `reports/latest/model_training_load_proof/summary.json`
```
{
  "auto_repair_allowed": false,
  "blockers": [],
  "evidence": {
    "candidate_count": 225,
    "candidates_sample": [
      ".github/workflows/model-backtest-readiness.yml",
      "ACTION_PLAN_ML_TRAINING.md",
      "CHARTS_MODEL_FIXES_SUMMARY.md",
      "ML_TRAINING_FALLBACK_EXPLAINED.md",
      "PERFORMANCE_PREDICTION_IMPROVEMENTS.md",
      "PHASE249_LSTM_TRAINING_COMPLETE.md",
      "PHASE_381_388_ULTRA_MODELS_PLAN.md",
      "PHASE_391_XGBOOST_TRAINING.md",
      "QUICK_IMPLEMENTATION_ULTRA_MODELS.md",
      "SYSTEM3_MODEL_AUDIT.md",
      "SYSTEM3_PHASES_361_365_HEALTH_AND_ACCURACY_REPORT.md",
      "ULTRA_MODEL_FEATURE_FIX_SUMMARY.md",
      "advanced_prediction_enhancer.py",
      "core/engine/ai_model/__init__.py",
      "core/engine/ai_model/data_balancing_v2.py",
      "core/engine/ai_model/feature_engineering_v2.py",
      "core/engine/ai_model/ml_predictor.py",
      "core/engine/ai_model/smote_balancer.py",
      "core/engine/ai_model/xgboost_trainer.py",
      "core/engine/angel_blended_model_trainer.py",
      "core/engine/angel_blended_model_trainer_v2.py",
      "core/engine/angel_blended_training_orchestrator_dryrun.py",
      "core/engine/angel_blended_training_v3.py",
      "core/engine/angel_breakout_predictor.py",
      "core/engine/angel_confidence_calibrator.py",
      "core/engine/angel_failure_point_predictor.py",
      "core/engine/angel_feature_drift_analyzer.py",
      "core/engine/angel_latency_drift_observatory.py",
      "core/engine/angel_model_selector.py",
      "core/engine/angel_multi_model_agreement.py",
      "core/engine/breakout_model/__init__.py",
      "core/engine/breakout_model/breakout_detector.py",
      "core/engine/build_angel_training_dataset.py",
      "core/engine/ensemble_predictor.py",
      "core/engine/generate_synthetic_angel_training.py",
      "core/engine/momentum_model/__init__.py",
      "core/engine/momentum_model/momentum_analyzer.py",
      "core/engine/scoring_engine/threshold_calibrator.py",
      "core/engine/system3_phase159_threshold_drift.py",
      "core/engine/system3_phase169_confidence_calibration.py",
      "core/engine/system3_phase169_confidence_calibration_analysis.py",
      "core/engine/system3_phase181_config_drift_detection.py",
      "core/engine/system3_phase183_model_performance_tracking.py",
      "core/engine/system3_phase192_model_comparison_report.py",
      "core/engine/system3_phase206_model_compatibility.py",
      "core/engine/system3_phase211_feature_drift.py",
      "core/engine/system3_phase213_training_window.py",
      "core/engine/system3_phase249_lstm_forward_predictor.py",
      "core/engine/system3_phase249_model_loader.py",
      "core/engine/system3_phase251_model_drift_tracker.py",
      "core/engine/system3_phase252_model_retraining_scheduler.py",
      "core/engine/system3_phase253_shadow_model_validator.py",
      "core/engine/system3_phase254_production_model_switcher.py",
      "core/engine/system3_phase255_model_performance_logger.py",
      "core/engine/system3_phase273_model_ensemble_builder.py",
      "core/engine/system3_phase283_drift_monitor.py",
      "core/engine/system3_phase296_model_performance_report.py",
      "core/engine/system3_phase327_predictive_failure_scout.py",
      "core/engine/system3_phase334_model_drift_snapshot.py",
      "core/engine/system3_phase335_model_drift_analyzer.py",
      "core/engine/system3_phase341_model_drift_detector_v2.py",
      "core/engine/system3_phase34_ultra_shadow_exec.py",
      "core/engine/system3_phase362_forward_calibrator.py",
      "core/engine/system3_phase363_model_drift_checker.py",
      "core/engine/system3_phase365_accuracy_tracker.py",
      "core/engine/system3_phase381_ultra_models_scanner.py",
      "core/engine/system3_phase382_ultra_models_validator.py",
      "core/engine/system3_phase391_xgboost_training.py",
      "core/engine/system3_phase39_shadow_campaign.py",
      "core/engine/train_angel_models.py",
      "core/engine/trend_model/__init__.py",
      "core/engine/trend_model/trend_analyzer.py",
      "core/engine/ultra_live_signals_shadow.py",
      "core/engine/ultra_models_loader.py",
      "core/engine/ultra_shadow_data_engine.py",
      "core/engine/ultra_train_models.py",
      "core/engine/volatility_model/__init__.py",
      "core/engine/volatility_model/volatility_analyzer.py",
      "core/execution/order_models.py",
      "core/models/__init__.py",
      "core/models/angel_one/BANKNIFTY_lstm_meta.json",
      "core/models/angel_one/BANKNIFTY_lstm_model.pth",
      "core/models/angel_one/BANKNIFTY_model.pkl",
      "core/models/angel_one/BANKNIFTY_model_meta.json",
      "core/models/angel_one/BANKNIFTY_rf.pkl",
      "core/models/angel_one/BANKNIFTY_rf_meta.json",
      "core/models/angel_one/FINNIFTY_lstm_meta.json",
      "core/models/angel_one/FINNIFTY_lstm_model.pth",
      "core/models/angel_one/FINNIFTY_model.pkl",
      "core/models/angel_one/FINNIFTY_model_meta.json",
      "core/models/angel_one/F
```
## `reports/latest/recent_backtest_walkforward_proof/summary.json`
```
{
  "auto_repair_allowed": false,
  "blockers": [],
  "evidence": {
    "candidate_count": 280,
    "candidates_sample": [
      "\"docs/System3 Phases 10\\342\\200\\22320 \\342\\200\\223 Ultra Mode Validation & Usage Plan (Safe  Read-Only).md\"",
      ".github/workflows/model-backtest-readiness.yml",
      ".github/workflows/safe-dryrun-validation-execution.yml",
      "ANALYSIS_COMPLETE_PHASE239_VALIDATION.md",
      "BACKTEST_SKIP_FIX.md",
      "BATCH_FILE_BACKTEST_FIX.md",
      "BROKER_CREDENTIALS_VALIDATION_COMPLETE.md",
      "COMPLETE_PHASE_ORCHESTRATION_STRATEGY.md",
      "COMPLETE_VALIDATION_AND_CONFIRMATION.md",
      "COMPLETE_VALIDATION_REPORT.md",
      "COMPREHENSIVE_VALIDATION_REPORT.md",
      "COMPREHENSIVE_VALIDATION_TEST_RESULTS.md",
      "DOCUMENTATION_INDEX_PRODUCTION_VALIDATION.md",
      "FINAL_COMPLETE_VALIDATION_SUMMARY.md",
      "FINAL_PHASE220_DETAILED_VALIDATION.md",
      "FINAL_PHASE221_FORWARD_RETURNS_VALIDATION.md",
      "FINAL_PHASE239_PNL_ENRICHMENT_VALIDATION.md",
      "FINAL_PNL_PIPELINE_HEALTH_REPORT.md",
      "FINAL_PRODUCTION_VALIDATION_AND_BUILD_COMPLETE.md",
      "FINAL_VALIDATION_COMPLETE.md",
      "FINAL_VALIDATION_CONFIRMATION.md",
      "FINAL_VALIDATION_REPORT.md",
      "FINAL_VALIDATION_SUMMARY.md",
      "FINAL_VALIDATION_SUMMARY_AND_RESULTS.txt",
      "GENESIS_VALIDATION_CONTROLLER_SUMMARY.md",
      "HARDENING_VALIDATION_REPORT.md",
      "OPTIMIZED_STRATEGY_IMPLEMENTATION.md",
      "PAPER_TRADING_SETUP_VALIDATION.md",
      "PERFORMANCE_ANALYSIS_AND_OPTIMIZATION_REPORT.md",
      "PERFORMANCE_IMPROVEMENTS_SUMMARY.md",
      "PERFORMANCE_PREDICTION_IMPROVEMENTS.md",
      "PHASE220_VALIDATION.md",
      "PHASE221_FORWARD_RETURNS_VALIDATION.md",
      "PHASE239_PNL_ENRICHMENT_VALIDATION.md",
      "POST_VALIDATION_BUILD_PLAN.md",
      "PRODUCTION_BUILD_VALIDATION_COMPLETE.md",
      "PRODUCTION_VALIDATION_COMPLETE.md",
      "PRODUCTION_VALIDATION_GUIDE.md",
      "PRODUCTION_VALIDATION_REPORT.json",
      "RUN_COMPLETE_VALIDATION.bat",
      "RUN_PERFORMANCE_ANALYSIS.bat",
      "SYSTEM3_COMPREHENSIVE_PRODUCTION_VALIDATION_SUMMARY.md",
      "SYSTEM3_FINAL_PHASE239_VALIDATION.md",
      "SYSTEM3_FINAL_RUNTIME_VALIDATION.md",
      "SYSTEM3_FULL_VALIDATION_REPORT_20251206.md",
      "SYSTEM3_MASTER_VALIDATION_REPORT.md",
      "SYSTEM3_PHASE304_305_239_FIX_VALIDATION.md",
      "SYSTEM3_PHASES_1_200_FIX_VALIDATION.md",
      "SYSTEM3_PNL_RUNTIME_VALIDATION_TODAY.md",
      "SYSTEM3_PREMARKET_VALIDATION_REPORT.md",
      "SYSTEM3_PRE_AUTORUN_VALIDATION_COMPLETE.md",
      "SYSTEM3_VALIDATION_CONSOLE_OUTPUT.txt",
      "SYSTEM3_VALIDATION_REPORTS_INDEX.md",
      "SYSTEM_PERFORMANCE_FIXES.md",
      "VALIDATION_AND_IMPROVEMENT_SUMMARY.md",
      "VALIDATION_COMPLETE.md",
      "VALIDATION_COMPLETE_100_PERCENT.md",
      "VALIDATION_FIXES_AND_STATUS.md",
      "VALIDATION_REPORT.md",
      "ZERO_ERRORS_VALIDATION_COMPLETE.md",
      "analyze_forward_returns.py",
      "complete_end_to_end_validation.py",
      "comprehensive_pre_build_validation.py",
      "comprehensive_production_validation.py",
      "core/engine/angel_daily_pnl_summary.py",
      "core/engine/angel_intraday_pnl_monitor.py",
      "core/engine/angel_performance_consistency_checker.py",
      "core/engine/angel_pnl_dummy_seed.py",
      "core/engine/angel_pnl_simulator.py",
      "core/engine/angel_strategy_optimizer.py",
      "core/engine/angel_synthetic_backtester.py",
      "core/engine/storage/metrics/ensemble_performance_392.json",
      "core/engine/system3_phase118_daily_live_pnl_snapshot.py",
      "core/engine/system3_phase142_slippage_calculator.py",
      "core/engine/system3_phase144_pnl_vs_execution_scenario.py",
      "core/engine/system3_phase166_underlying_performance.py",
      "core/engine/system3_phase166_underlying_performance_comparison.py",
      "core/engine/system3_phase177_performance_trends.py",
      "core/engine/system3_phase183_model_performance_tracking.py",
      "core/engine/system3_phase188_underlying_performance_trends.py",
      "core/engine/system3_phase221_forward_returns.py",
      "core/engine/system3_phase249_lstm_forward_predictor.py",
      "core/engine/system3_phase255_model_performance_logger.py",
      "core/engine/system3_phase263_advanced_pnl_attribution.py",
      "core/engine/system3_phase270_regime_performance_comparison.py",
      "core/engine/system3_phase280_strategy_backtester.py",
      "core/engine/system3_phase281_realtime_performance_monitor.py",
      "core/engine/system3_phase286_performance_degradation_detector.py",
      "core/engine/system3_phase291_daily_performance_report.py",
      "core/engine/system3_phase294_strategy_performance_report.py",
      "core/engine/system3_phase296_model_performance_report.py",
      "core/engine/system3_phase301_daily_live_vs_forward.py",
      "core/engine/system3_phase302_regime_performance.py",
      "core/engine/system3_phase304_forward_returns.py",
      "core/engine/system3_p
```
## `reports/latest/analyzer_paper_lifecycle_proof/summary.json`
```
{
  "auto_repair_allowed": false,
  "blockers": [],
  "evidence": {
    "candidate_count": 170,
    "candidates_sample": [
      "AUTOMATED_PAPER_TRADING_COMPLETE_ANALYSIS.md",
      "CHANGES_MADE_PAPER_TRADING_SETUP.md",
      "COMPLETE_PAPER_TRADING_GUIDE.md",
      "FINAL_AUTOMATED_PAPER_TRADING_REPORT.md",
      "LIVE_PAPER_TRADING_GUIDE.md",
      "PAPER_TRADING_ACTIVATION_GUIDE.md",
      "PAPER_TRADING_COMPLETE_SUMMARY.md",
      "PAPER_TRADING_DOCUMENTATION_INDEX.md",
      "PAPER_TRADING_IMPLEMENTATION_COMPLETE.md",
      "PAPER_TRADING_LIVE_MARKET_HOURS_GUIDE.md",
      "PAPER_TRADING_ONE_PAGER.md",
      "PAPER_TRADING_QUICK_START.md",
      "PAPER_TRADING_SETUP_VALIDATION.md",
      "PAPER_TRADING_SMOKE_TEST_RESULTS.md",
      "QUICK_START_PAPER_TRADING.md",
      "README_PAPER_TRADING_SETUP.md",
      "RUN_LIVE_PAPER_TRADING_GUIDE.md",
      "START_HERE_PAPER_TRADING.md",
      "START_PAPER_TRADING.bat",
      "START_PAPER_TRADING_COMPLETE.bat",
      "START_REAL_LIVE_PAPER_TRADING.bat",
      "TODAYS_MARKET_TRADES_REPORT.md",
      "TRADER_USER_GUIDE.md",
      "TRADER_USER_TEST_GUIDE.md",
      "TRADE_TIMING_ANALYSIS.md",
      "comprehensive_multi_trader_test.py",
      "config/live_trade_config.json",
      "config/live_trade_config.py",
      "core/broker/angel_live_order_wrapper.py",
      "core/config/live_trade_config_loader.py",
      "core/engine/angel_feature_drift_analyzer.py",
      "core/engine/angel_market_regime_recorder.py",
      "core/engine/angel_outcome_confidence_analyzer.py",
      "core/engine/angel_overtrade_detector.py",
      "core/engine/angel_signal_outcome_analyzer.py",
      "core/engine/angel_trade_config.py",
      "core/engine/angel_trade_decision.py",
      "core/engine/angel_trade_executor.py",
      "core/engine/angel_trade_lifecycle_logger.py",
      "core/engine/angel_trade_rules.py",
      "core/engine/angel_trade_validator_v2.py",
      "core/engine/momentum_model/momentum_analyzer.py",
      "core/engine/system3_phase101_live_trade_config_check.py",
      "core/engine/system3_phase102_order_ledger_schema.py",
      "core/engine/system3_phase103_order_ledger_support.py",
      "core/engine/system3_phase104_tradeplan_to_orders.py",
      "core/engine/system3_phase108_order_status_refresher.py",
      "core/engine/system3_phase163_trade_frequency.py",
      "core/engine/system3_phase163_trade_frequency_analysis.py",
      "core/engine/system3_phase185_trade_execution_summary.py",
      "core/engine/system3_phase210_timegap_analyzer.py",
      "core/engine/system3_phase219_breakout_analyzer.py",
      "core/engine/system3_phase261_portfolio_risk_analyzer.py",
      "core/engine/system3_phase265_execution_quality_analyzer.py",
      "core/engine/system3_phase267_drawdown_analyzer.py",
      "core/engine/system3_phase275_position_sizing_optimizer.py",
      "core/engine/system3_phase297_trade_execution_report.py",
      "core/engine/system3_phase319_position_state_consistency_checker.py",
      "core/engine/system3_phase324_warn_error_cluster_analyzer.py",
      "core/engine/system3_phase329_changeset_and_version_recorder.py",
      "core/engine/system3_phase335_model_drift_analyzer.py",
      "core/engine/system3_phase83_tick_to_trade_latency.py",
      "core/engine/system3_phase86_position_sizing.py",
      "core/engine/trend_model/trend_analyzer.py",
      "core/engine/ultra_pnl_analyzer.py",
      "core/engine/ultra_trade_simulator.py",
      "core/engine/volatility_model/volatility_analyzer.py",
      "core/execution/order_models.py",
      "core/ultra/phase22_position_sizing.py",
      "dashboard/backend/order_management.py",
      "dashboard/backend/position_reconciliation.py",
      "dashboard/backend/trade_journal.py",
      "dashboard/backend/trade_logger.py",
      "dashboard/frontend/src/components/PaperTrading.tsx",
      "docs/CURRENT_STATUS_PAPER_TRADING.md",
      "docs/FINAL_PAPER_TRADING_REPORT.md",
      "docs/PAPER_TRADING_INTEGRATION_COMPLETE.md",
      "docs/PAPER_TRADING_STATUS_UPDATE.md",
      "inspect_enriched_and_orders.py",
      "paper_pnl_summary.json",
      "paper_trading_smoke_test.py",
      "reports/archive/lifecycle_reconciliation/20260608/lifecycle_summary.md",
      "reports/archive/lifecycle_reconciliation/20260608/mismatch_report.md",
      "reports/archive/lifecycle_reconciliation/20260608/open_closed_positions.csv",
      "reports/archive/lifecycle_reconciliation/20260608/pnl_reconciliation.csv",
      "reports/archive/lifecycle_reconciliation/20260608/signal_order_trade_join.csv",
      "reports/archive/lifecycle_reconciliation/20260608/source_manifest.json",
      "reports/archive/lifecycle_reconciliation/20260608/status.json",
      "reports/latest/analyzer_paper_lifecycle_proof/README.md",
      "reports/latest/analyzer_paper_lifecycle_proof/summary.json",
      "reports/latest/full_repo_verification/commands/py_compile_031_comprehensive_multi_trader_test.stderr.txt",
      "reports/latest/full_repo_verification/c
```
## `reports/latest/dashboard_truth_proof/summary.json`
```
{
  "auto_repair_allowed": true,
  "blockers": [],
  "evidence": {
    "api_db_report_reconciliation_proven": false,
    "backend_file_count": 23,
    "browser_visual_truth_proven": false,
    "compile_results": [
      {
        "compile_pass": true,
        "error": null,
        "exists": true,
        "file": "dashboard/backend/app.py"
      },
      {
        "compile_pass": true,
        "error": null,
        "exists": true,
        "file": "dashboard/backend/backtesting.py"
      }
    ],
    "dashboard_endpoint_coverage_keys": [
      "base_url",
      "by_category",
      "core_ok",
      "fail_count",
      "generated_utc",
      "note",
      "ok_count",
      "results",
      "total_endpoints_tested"
    ],
    "dashboard_endpoint_coverage_report_present": true,
    "dashboard_file_count": 66,
    "frontend_file_count": 36
  },
  "gate": "dashboard_truth_proof",
  "next_action": "Run dashboard endpoint coverage plus browser screenshot proof; dashboard must show blockers and never claim ready until gates pass.",
  "pass": true,
  "status": "PASS_WITH_WARNINGS",
  "warnings": [
    "browser_screenshot_truth_not_proven_in_ci"
  ]
}

```