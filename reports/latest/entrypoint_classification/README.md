# Entrypoint Classification Proof

Generated UTC: 2026-06-07T11:33:38.113080+00:00

## Top training candidates

- `advanced_prediction_enhancer.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, output_report_markers
- `core/engine/ai_model/feature_engineering_v2.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, output_report_markers
- `core/engine/ai_model/smote_balancer.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, output_report_markers
- `core/engine/ai_model/xgboost_trainer.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, output_report_markers
- `core/engine/angel_blended_training_orchestrator_dryrun.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, output_report_markers
- `core/engine/angel_blended_training_v3.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, output_report_markers
- `core/engine/angel_confidence_calibrator.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, output_report_markers
- `core/engine/angel_failure_point_predictor.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, output_report_markers
- `core/engine/angel_feature_drift_analyzer.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, live_guard_marker
- `core/engine/angel_latency_drift_observatory.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, output_report_markers

## Top backtest candidates

- `final_system_validation_test.py` — score `9` — syntax_ok, has_main, safe_cli_or_dryrun_markers, live_guard_marker, output_report_markers
- `production_grade_validation.py` — score `9` — syntax_ok, has_main, safe_cli_or_dryrun_markers, live_guard_marker, output_report_markers
- `system3_pre_autorun_validation.py` — score `9` — syntax_ok, has_main, safe_cli_or_dryrun_markers, live_guard_marker, output_report_markers
- `tools/compute_mark_to_market_pnl.py` — score `9` — syntax_ok, has_main, safe_cli_or_dryrun_markers, argparse, output_report_markers
- `complete_end_to_end_validation.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, output_report_markers
- `core/engine/angel_performance_consistency_checker.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, output_report_markers
- `core/engine/system3_phase342_live_performance_estimator.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, output_report_markers
- `core/engine/system3_phase366_strategy_ensemble_evaluator.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, output_report_markers
- `core/engine/system3_phase378_performance_optimizer.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, output_report_markers
- `core/validation/pre_market_signal_dryrun.py` — score `8` — syntax_ok, has_main, safe_cli_or_dryrun_markers, output_report_markers

## Rule

Do not execute broker/live actions. First run top candidates only in dry-run/read-only/analyzer mode.
