# System3 Authority Runtime Map

Generated UTC: 2026-05-28T16:01:27.172268+00:00

## Scope

Report-only Phase C map. No trading logic, secrets, .env, broker config, database, dashboard UI, or model artifacts changed.

## Authoritative Candidates

- **master_menu_orchestrator**: `run_system3.py`
- **training_dataset_builder**: `core/engine/build_angel_training_dataset.py`
- **model_training**: `core/engine/train_angel_models.py`
- **baseline_model_artifacts_expected**: `core/models/angel_one/{UNDERLYING}_model.pkl and {UNDERLYING}_model_meta.json`
- **live_signal_runtime**: `core/engine/angel_live_ai_signals.py`
- **default_enhanced_signal_engine**: `core/engine/system3_signal_engine.py`
- **synthetic_backtest_candidate**: `core/engine/angel_synthetic_backtester.py`
- **dashboard_backend_candidate**: `dashboard/backend/app.py`
- **dashboard_prediction_status_candidate**: `dashboard/backend/performance_predictor.py`

## Not Yet Proven

- actual model artifact files exist and are fresh
- training data file exists and is fresh
- walk-forward backtest exists and is reproducible
- cost/slippage/spread-aware benchmark is active
- dashboard displays model version/accuracy from real backend truth
- synthetic/fallback data is blocked from production truth display
- which model path is active when enhanced signal engine succeeds

## Candidate File Evidence

### `run_system3.py`

- exists: `True`
- size_bytes: `48516`
- categories:
  - master_entry: if __name__, show_menu, launch, main()
  - training_dataset: build
  - prediction_runtime: predict, run_once_with_snapshot
  - backtesting: backtest, synthetic, profile
  - dashboard: dashboard, performance
  - fallback_risk: synthetic, default
  - paper_live_safety: DRY RUN, live, broker, safety, guard
- parse_error: `invalid non-printable character U+FEFF (<unknown>, line 1)`

### `system3_ultra.py`

- exists: `True`
- size_bytes: `32217`
- categories:
  - master_entry: if __name__, show_menu, launch, main()
  - training_dataset: build
  - prediction_runtime: predict
  - backtesting: backtest, synthetic, profile
  - dashboard: dashboard, performance
  - fallback_risk: synthetic, default
  - paper_live_safety: DRY RUN, live, auto_execute, broker, safety, guard
- imports_sample: `sys, os, pathlib.Path, datetime.datetime, typing.Dict, typing.Any, typing.Optional, typing.Callable, traceback, core.engine.ultra_safety.load_ultra_safety, core.engine.ultra_safety.is_ultra_enabled, core.engine.angel_automation_config.AUTOMATION_CONFIG, core.engine.ultra_safety.main, system3_ultra_validation.run_full_validation`
- functions_sample: `_log, _check_safety, _safe_execute, _safe_execute_main, _safe_execute_phase, show_menu, handle_operational_phase, handle_baseline_core, handle_learning_cycle, handle_ultra_observability, handle_master_dataset, handle_ultra_shadow, handle_ultra_live, handle_ultra_phases_21_30, handle_ultra_phases_31_38, handle_ultra_phases_39_45, handle_ultra_phases_46_55, handle_ultra_phases_76_100, handle_system_tools, main`

### `core/engine/build_angel_training_dataset.py`

- exists: `True`
- size_bytes: `8314`
- categories:
  - master_entry: if __name__, main()
  - training_dataset: training.csv, build, label_3class, forward return, fwd_ret
  - paper_live_safety: live
- imports_sample: `os, sys, datetime.datetime, pandas, core.utils.logger.logger`
- functions_sample: `_load_live_data, _add_core_features, _add_ce_pe_pair_features, _add_forward_returns, _add_labels, main, _label5, _label3`

### `core/engine/train_angel_models.py`

- exists: `True`
- size_bytes: `9776`
- categories:
  - master_entry: if __name__, main()
  - training_dataset: training.csv, label_3class
  - model_training: fit(, GradientBoostingClassifier, joblib.dump, accuracy_score, classification_report
  - model_artifact: .pkl, _model_meta.json, MODELS_DIR
  - prediction_runtime: predict
  - fallback_risk: fallback, sample
  - paper_live_safety: live
- imports_sample: `os, sys, json, datetime.datetime, pandas, sklearn.model_selection.train_test_split, sklearn.ensemble.GradientBoostingClassifier, sklearn.metrics.classification_report, sklearn.metrics.accuracy_score, joblib, core.engine.angel_multi_resolution_labels.generate_labels, core.utils.logger.logger`
- functions_sample: `_load_top_features_map, _load_training_data, _prepare_features_labels, _train_model_for_underlying, main`

### `core/engine/angel_live_ai_signals.py`

- exists: `True`
- size_bytes: `15511`
- categories:
  - master_entry: if __name__, main()
  - training_dataset: build
  - model_artifact: .pkl, _model_meta.json, joblib.load, MODELS_DIR
  - prediction_runtime: predict, predict_proba, run_once_with_snapshot, run_signal_engine
  - backtesting: profile
  - fallback_risk: fallback, default
  - paper_live_safety: DRY RUN, live, auto_execute
- imports_sample: `os, json, pathlib.Path, typing.Dict, typing.Any, numpy, pandas, joblib, core.utils.logger.logger, core.engine.angel_trade_decision, core.engine.angel_automation_config.AUTOMATION_CONFIG, core.engine.angel_trade_executor.execute_dry_run, core.engine.angel_trade_lifecycle_logger.get_lifecycle_logger, core.engine.angel_trade_lifecycle_logger.generate_trade_id, core.engine.angel_model_selector.load_models_for_profile, core.engine.angel_model_selector.get_active_profile, core.engine.system3_signal_engine.run_signal_engine`
- functions_sample: `_project_root, load_models_and_meta, _ensure_features_for_df, predict_for_snapshot_df, append_signals_to_csv, run_once_with_snapshot, main`

### `core/engine/system3_signal_engine.py`

- exists: `True`
- size_bytes: `44329`
- categories:
  - master_entry: if __name__
  - training_dataset: build
  - prediction_runtime: predict, run_signal_engine
  - fallback_risk: fallback, sample, default
  - paper_live_safety: live, safety, guard
- imports_sample: `sys, pandas, numpy, pathlib.Path, typing.Dict, typing.Any, typing.Optional, datetime.datetime, core.utils.logger.logger, core.engine.greeks_engine.compute_greeks_for_df, core.engine.trend_model.compute_trend_features, core.engine.trend_model.compute_multi_timeframe_trend, core.engine.volatility_model.compute_volatility_features, core.engine.volatility_model.detect_volatility_regime, core.engine.breakout_model.detect_breakouts, core.engine.momentum_model.compute_momentum_features, core.engine.entry_exit_engine.compute_entry_signals, core.engine.entry_exit_engine.compute_exit_signals, core.engine.entry_exit_engine.compute_dynamic_sl_tp, core.engine.scoring_engine.compute_final_score`
- functions_sample: `load_recent_signal_history, compute_short_history_features, process_snapshot, append_signals_to_csv, run_signal_engine, map_signal`

### `core/engine/ai_model/__init__.py`

- exists: `True`
- size_bytes: `415`
- categories:
  - prediction_runtime: predict
  - paper_live_safety: live
- imports_sample: `ml_predictor.train_ml_model, ml_predictor.predict_direction, ml_predictor.load_training_data, ml_predictor.get_training_dataframe, ml_predictor.CURATED_TRAINING_PATH, ml_predictor.LIVE_TRAINING_PATH`

### `core/engine/ai_model/ml_predictor.py`

- exists: `True`
- size_bytes: `15454`
- categories:
  - model_training: fit(
  - prediction_runtime: predict, predict_proba
  - fallback_risk: fallback, sample
  - paper_live_safety: live
- imports_sample: `numpy, pandas, typing.Dict, typing.Any, typing.Optional, pathlib.Path, joblib, datetime.datetime, datetime.timedelta, collections.Counter, logging, core.utils.logger.logger, xgboost.XGBClassifier, sklearn.ensemble.RandomForestClassifier`
- functions_sample: `_get_loader_logger, load_training_data, get_training_dataframe, prepare_features_for_ml, train_ml_model, predict_direction`

### `core/engine/ultra_models_loader.py`

- exists: `True`
- size_bytes: `9625`
- categories:
  - master_entry: if __name__
  - model_artifact: .pkl, joblib.load, MODELS_DIR
  - prediction_runtime: predict, predict_proba
  - fallback_risk: fallback
  - paper_live_safety: safety
- imports_sample: `pathlib.Path, joblib, logging, typing.Dict, typing.Any, typing.Optional, datetime.datetime, os`
- functions_sample: `load_ultra_model, get_ultra_model_metadata, load_ultra_models_all, get_all_ultra_models_inventory, verify_ultra_models_health`

### `core/engine/angel_model_selector.py`

- exists: `True`
- size_bytes: `10847`
- categories:
  - master_entry: if __name__, main()
  - model_artifact: .pkl, _model_meta.json, joblib.load, MODELS_DIR
  - backtesting: profile
  - fallback_risk: fallback, default
  - paper_live_safety: live
- imports_sample: `joblib, json, pathlib.Path, typing.Dict, typing.Any, typing.Optional, core.engine.angel_trade_config.DEFAULT_THRESHOLDS`
- functions_sample: `load_profile_config, get_active_profile, get_model_dir, get_storage_dirs, load_models_for_profile, get_profile_thresholds, show_profile_info, main`

### `core/engine/angel_synthetic_backtester.py`

- exists: `True`
- size_bytes: `22730`
- categories:
  - master_entry: if __name__
  - training_dataset: build
  - model_artifact: .pkl, _model_meta.json, joblib.load, MODELS_DIR
  - prediction_runtime: predict, predict_proba
  - backtesting: backtest, synthetic, profile
  - fallback_risk: fallback, synthetic, default
  - paper_live_safety: live
- imports_sample: `os, json, time, math, pathlib.Path, datetime.datetime, datetime.timedelta, numpy, pandas, joblib, core.engine.train_angel_models.ROOT_DIR, core.engine.angel_trade_config.DEFAULT_THRESHOLDS, core.engine.angel_live_ai_signals.load_models_and_meta, core.engine.angel_live_ai_signals._ensure_features_for_df`
- functions_sample: `generate_synthetic_intraday_paths, load_models, run_models_on_snapshot, select_trades_from_signals, simulate_trade_pnl, run_backtest`

### `core/engine/angel_feature_ranker.py`

- exists: `True`
- size_bytes: `4130`
- categories:
  - master_entry: if __name__, main()
  - training_dataset: training.csv
- imports_sample: `os, pandas, numpy, pathlib.Path, typing.Dict, typing.List`
- functions_sample: `main, __init__, rank_features_advanced, rank_all_underlyings`
- classes_sample: `AdvancedFeatureRanker`

### `core/engine/ensemble_predictor.py`

- exists: `True`
- size_bytes: `19579`
- categories:
  - master_entry: if __name__
  - model_training: accuracy_score
  - model_artifact: .pkl, joblib.load
  - prediction_runtime: predict, predict_proba
  - dashboard: performance
  - fallback_risk: fallback, sample, default
- imports_sample: `pandas, numpy, typing.Optional, typing.Dict, typing.Any, typing.Tuple, typing.List, pathlib.Path, datetime.datetime, datetime.timedelta, collections.deque, logging, joblib, json, lightgbm, catboost, sklearn.ensemble.RandomForestClassifier, torch, json`
- functions_sample: `load_ultra_model, load_xgboost_model, load_lightgbm_model, load_catboost_model, load_randomforest_model, load_neural_net_model, compute_delta_scores, get_model_predictions, prepare_features_for_prediction, predict_with_ensemble, run_phase_392, __init__, update_performance, get_dynamic_weights`
- classes_sample: `DynamicWeightTracker`

### `dashboard/backend/app.py`

- exists: `True`
- size_bytes: `149026`
- categories:
  - master_entry: if __name__
  - model_training: fit(
  - prediction_runtime: predict
  - backtesting: backtest, synthetic, profile
  - dashboard: FastAPI, app =, api/state, dashboard, performance
  - fallback_risk: fallback, synthetic, sample, default
  - paper_live_safety: paper, live, broker
- imports_sample: `os, sys, json, asyncio, hashlib, re, time, pathlib.Path, typing.Dict, typing.List, typing.Optional, typing.Any, datetime.datetime, datetime.timedelta, pytz, fastapi.FastAPI, fastapi.WebSocket, fastapi.WebSocketDisconnect, fastapi.HTTPException, fastapi.middleware.cors.CORSMiddleware`
- functions_sample: `set_event_loop, redact_secrets, scan_secrets, init_db, ingest_cycle_metrics, log_event, on_modified, run_validation`
- classes_sample: `OutputFileHandler, HealthResponse, RunnerStartRequest`

### `dashboard/backend/performance_predictor.py`

- exists: `True`
- size_bytes: `13818`
- categories:
  - model_training: fit(
  - prediction_runtime: predict
  - dashboard: performance
  - fallback_risk: fallback, default
  - paper_live_safety: live, broker
- imports_sample: `json, math, datetime.datetime, datetime.timedelta, typing.Dict, typing.List, typing.Optional, typing.Tuple, typing.Any, pathlib.Path, pytz`
- functions_sample: `get_performance_predictor, __init__, predict_profit, _calculate_hours_to_expiry, _predict_from_history, _predict_from_volatility, _calculate_confidence, _calculate_risk_metrics, validate_profit, predict_portfolio_performance, update_prediction_history`
- classes_sample: `PerformancePredictor`

### `dashboard/frontend/package.json`

- exists: `True`
- size_bytes: `641`
- categories:
  - training_dataset: build
  - dashboard: dashboard

### `.github/workflows/ci.yml`

- exists: `True`
- size_bytes: `2350`
- categories:
  - training_dataset: build
  - dashboard: dashboard
  - paper_live_safety: guard

### `.github/workflows/qa.yml`

- exists: `True`
- size_bytes: `1653`
- categories:
  - paper_live_safety: safety

### `.github/workflows/cd.yml`

- exists: `True`
- size_bytes: `3609`
- categories:
  - training_dataset: build
  - backtesting: profile
  - dashboard: dashboard
  - paper_live_safety: guard

## Extra Relevant Files

- `advanced_prediction_enhancer.py` | categories=master_entry,model_artifact,prediction_runtime,fallback_risk,paper_live_safety
- `analyze_signals.py` | categories=paper_live_safety
- `audit_signals_archive.py` | categories=paper_live_safety
- `core/engine/ai_model/xgboost_trainer.py` | categories=master_entry,model_training,model_artifact,prediction_runtime,dashboard,fallback_risk,paper_live_safety
- `core/engine/angel_blended_dataset_builder.py` | categories=master_entry,training_dataset,backtesting,fallback_risk
- `core/engine/angel_blended_model_trainer.py` | categories=master_entry,training_dataset,backtesting,dashboard,fallback_risk,paper_live_safety
- `core/engine/angel_blended_model_trainer_v2.py` | categories=master_entry,training_dataset,model_training,model_artifact,backtesting,fallback_risk,paper_live_safety
- `core/engine/angel_breakout_predictor.py` | categories=master_entry,prediction_runtime
- `core/engine/angel_dataset_merger_real_synth_v1.py` | categories=master_entry,training_dataset,backtesting,fallback_risk
- `core/engine/angel_enhanced_signal_scorer.py` | categories=dashboard,fallback_risk
- `core/engine/angel_failure_point_predictor.py` | categories=master_entry,training_dataset,model_artifact,prediction_runtime,dashboard,paper_live_safety
- `core/engine/angel_live_ai_signals_v2.py` | categories=master_entry,prediction_runtime,fallback_risk,paper_live_safety
- `core/engine/angel_live_signals.py` | categories=master_entry,training_dataset,model_artifact,prediction_runtime,fallback_risk,paper_live_safety
- `core/engine/angel_market_intelligence_dashboard.py` | categories=master_entry,prediction_runtime,backtesting,dashboard,fallback_risk,paper_live_safety
- `core/engine/angel_multi_model_agreement.py` | categories=master_entry,prediction_runtime
- `core/engine/angel_real_master_dataset.py` | categories=master_entry,training_dataset,fallback_risk,paper_live_safety
- `core/engine/angel_real_signal_collector_v2.py` | categories=master_entry,paper_live_safety
- `core/engine/angel_rolling_learning_dashboard.py` | categories=master_entry,dashboard
- `core/engine/angel_signal_outcome_analyzer.py` | categories=master_entry,training_dataset
- `core/engine/angel_signal_quality_meter.py` | categories=master_entry
- `core/engine/angel_signal_record_buffer.py` | categories=master_entry,prediction_runtime
- `core/engine/angel_ultra_dashboard_readonly.py` | categories=master_entry,training_dataset,prediction_runtime,dashboard,paper_live_safety
- `core/engine/scoring_engine/signal_scorer.py` | categories=training_dataset,fallback_risk
- `core/engine/system3_phase178_system_health_dashboard.py` | categories=master_entry,dashboard
- `core/engine/system3_phase183_model_performance_tracking.py` | categories=master_entry,dashboard
- `core/engine/system3_phase184_signal_quality_metrics.py` | categories=master_entry
- `core/engine/system3_phase192_model_comparison_report.py` | categories=master_entry
- `core/engine/system3_phase193_system_status_dashboard.py` | categories=master_entry,dashboard
- `core/engine/system3_phase206_model_compatibility.py` | categories=master_entry,training_dataset,model_artifact
- `core/engine/system3_phase208_signal_consistency.py` | categories=master_entry,paper_live_safety
- `core/engine/system3_phase222_signal_edge.py` | categories=master_entry,training_dataset,fallback_risk,paper_live_safety
- `core/engine/system3_phase249_lstm_forward_predictor.py` | categories=master_entry,training_dataset,model_artifact,prediction_runtime,fallback_risk,paper_live_safety
- `core/engine/system3_phase249_model_loader.py` | categories=master_entry
- `core/engine/system3_phase251_model_drift_tracker.py` | categories=master_entry,training_dataset,model_artifact,dashboard,fallback_risk,paper_live_safety
- `core/engine/system3_phase252_model_retraining_scheduler.py` | categories=master_entry,paper_live_safety
- `core/engine/system3_phase253_shadow_model_validator.py` | categories=master_entry,model_artifact,prediction_runtime,paper_live_safety
- `core/engine/system3_phase254_production_model_switcher.py` | categories=master_entry,model_artifact,paper_live_safety
- `core/engine/system3_phase255_model_performance_logger.py` | categories=master_entry,prediction_runtime,dashboard,paper_live_safety
- `core/engine/system3_phase264_signal_quality_metrics.py` | categories=master_entry,training_dataset,paper_live_safety
- `core/engine/system3_phase273_model_ensemble_builder.py` | categories=master_entry,training_dataset
- `core/engine/system3_phase280_strategy_backtester.py` | categories=master_entry,backtesting,paper_live_safety
- `core/engine/system3_phase285_health_dashboard_generator.py` | categories=master_entry,dashboard,paper_live_safety
- `core/engine/system3_phase296_model_performance_report.py` | categories=master_entry,dashboard,paper_live_safety
- `core/engine/system3_phase308_daily_dashboard.py` | categories=training_dataset,dashboard,paper_live_safety
- `core/engine/system3_phase318_signal_outlier_detector.py` | categories=master_entry
- `core/engine/system3_phase327_predictive_failure_scout.py` | categories=master_entry,prediction_runtime
- `core/engine/system3_phase331_signal_integrity.py` | categories=master_entry,training_dataset,paper_live_safety
- `core/engine/system3_phase332_signal_volume_coverage.py` | categories=master_entry,paper_live_safety
- `core/engine/system3_phase333_signal_consistency.py` | categories=master_entry,training_dataset,fallback_risk,paper_live_safety
- `core/engine/system3_phase334_model_drift_snapshot.py` | categories=master_entry,training_dataset,dashboard,fallback_risk,paper_live_safety
- `core/engine/system3_phase335_model_drift_analyzer.py` | categories=master_entry,training_dataset,dashboard,paper_live_safety
- `core/engine/system3_phase338_signal_outcome_correlation.py` | categories=master_entry,training_dataset,prediction_runtime,paper_live_safety
- `core/engine/system3_phase339_daily_signal_pipeline_summary.py` | categories=master_entry,training_dataset,paper_live_safety
- `core/engine/system3_phase340_signal_pipeline_regression_guard.py` | categories=master_entry,training_dataset,fallback_risk,paper_live_safety
- `core/engine/system3_phase341_model_drift_detector_v2.py` | categories=master_entry,backtesting,fallback_risk,paper_live_safety
- `core/engine/system3_phase343_signals_freshness_enforcer.py` | categories=master_entry,paper_live_safety
- `core/engine/system3_phase361_signal_pipeline_snapshot.py` | categories=master_entry,fallback_risk,paper_live_safety
- `core/engine/system3_phase363_model_drift_checker.py` | categories=master_entry,training_dataset,dashboard,paper_live_safety
- `core/engine/system3_phase364_health_dashboard_feed.py` | categories=master_entry,training_dataset,dashboard,paper_live_safety
- `core/engine/system3_phase370_signal_schema_normalizer.py` | categories=master_entry,training_dataset,paper_live_safety
- `core/engine/system3_phase371_signal_duplicate_scanner.py` | categories=master_entry,paper_live_safety
- `core/engine/system3_phase372_signal_conflict_resolver.py` | categories=master_entry,paper_live_safety
- `core/engine/system3_phase373_signal_clean_curated_builder.py` | categories=master_entry,training_dataset,paper_live_safety
- `core/engine/system3_phase374_signal_history_freshness_checker.py` | categories=master_entry,paper_live_safety
- `core/engine/system3_phase375_signal_data_quality_summary.py` | categories=master_entry,training_dataset
- `core/engine/system3_phase381_ultra_models_scanner.py` | categories=master_entry,fallback_risk,paper_live_safety
- `core/engine/system3_phase382_ultra_models_validator.py` | categories=master_entry,prediction_runtime,backtesting,fallback_risk,paper_live_safety
- `core/engine/system3_phase383_ultra_backtest_sampler.py` | categories=master_entry,prediction_runtime,backtesting,dashboard,fallback_risk,paper_live_safety
- `core/engine/system3_phase91_live_dashboard.py` | categories=master_entry,backtesting,dashboard,paper_live_safety
- `core/engine/system3_signal_engine_self_test.py` | categories=master_entry,fallback_risk,paper_live_safety
- `core/engine/ultra_live_signals_shadow.py` | categories=master_entry,training_dataset,model_artifact,prediction_runtime,paper_live_safety
- `core/engine/ultra_train_models.py` | categories=master_entry,training_dataset,model_training,model_artifact,prediction_runtime,backtesting,fallback_risk,paper_live_safety
- `core/tools/clean_angel_signals_csv.py` | categories=master_entry,training_dataset,prediction_runtime,paper_live_safety
- `core/ultra/phase50_prediction_explainer.py` | categories=master_entry,prediction_runtime,backtesting,fallback_risk,paper_live_safety
- `core/ultra/phase55_intelligence_dashboard.py` | categories=master_entry,prediction_runtime,dashboard,fallback_risk,paper_live_safety
- `core/validation/post_close_signal_audit.py` | categories=master_entry,fallback_risk,paper_live_safety
- `core/validation/pre_market_signal_dryrun.py` | categories=master_entry,paper_live_safety
- `dashboard/backend/backtesting.py` | categories=backtesting
- `evaluate_phase249_models.py` | categories=master_entry,training_dataset,model_artifact,prediction_runtime,fallback_risk,paper_live_safety
- `fix_ultra_model_feature_mismatch.py` | categories=master_entry,model_training,model_artifact,prediction_runtime,fallback_risk
- `live_trading_dashboard.py` | categories=master_entry,training_dataset,prediction_runtime,dashboard,paper_live_safety
- `model_training_v2.py` | categories=master_entry,training_dataset,model_training,model_artifact,prediction_runtime,fallback_risk
- `rebuild_complete_signals.py` | categories=master_entry,training_dataset,model_artifact,prediction_runtime,backtesting,fallback_risk,paper_live_safety
- `scripts/analyze_dashboard_content.py` | categories=master_entry,dashboard,paper_live_safety
- `scripts/build_advanced_excel_with_ai_predictions.py` | categories=master_entry,training_dataset,prediction_runtime,dashboard,fallback_risk,paper_live_safety
- `scripts/comprehensive_dashboard_test.py` | categories=master_entry,dashboard,fallback_risk,paper_live_safety
- `scripts/comprehensive_dashboard_validation.py` | categories=master_entry,backtesting,dashboard,fallback_risk,paper_live_safety
- `scripts/comprehensive_dashboard_verification.py` | categories=master_entry,dashboard,paper_live_safety
- `scripts/dashboard_24hr_monitor.py` | categories=master_entry,dashboard,fallback_risk
- `scripts/dashboard_content_analysis.py` | categories=master_entry,backtesting,dashboard,fallback_risk,paper_live_safety
- `scripts/dashboard_continuous_improvement.py` | categories=master_entry,backtesting,dashboard,fallback_risk
- `scripts/dashboard_data_validator.py` | categories=master_entry,dashboard,fallback_risk,paper_live_safety
- `scripts/dashboard_online_verifier.py` | categories=master_entry,dashboard,paper_live_safety
- `scripts/enhance_optionchain_with_predictions.py` | categories=master_entry,training_dataset,prediction_runtime,fallback_risk,paper_live_safety
- `scripts/fix_dashboard_data_issues.py` | categories=master_entry,dashboard,paper_live_safety
- `scripts/full_dashboard_test_and_analyze.py` | categories=master_entry,dashboard,paper_live_safety
- `scripts/multi_user_dashboard_test.py` | categories=master_entry,dashboard,fallback_risk
- `scripts/multi_user_dashboard_verification.py` | categories=master_entry,prediction_runtime,dashboard,fallback_risk
- `scripts/run_dashboard_full_test.py` | categories=master_entry,backtesting,dashboard,fallback_risk,paper_live_safety
- `scripts/test_all_dashboard_tabs.py` | categories=master_entry,dashboard,paper_live_safety
- `scripts/test_performance_prediction.py` | categories=master_entry,prediction_runtime,dashboard
- `scripts/verify_dashboard_complete.py` | categories=master_entry,backtesting,dashboard,fallback_risk,paper_live_safety
- `src/ml/ensemble_predictor.py` | categories=model_training,model_artifact,prediction_runtime,dashboard,fallback_risk
- `system3_debug_signals_pipeline.py` | categories=master_entry,prediction_runtime,fallback_risk,paper_live_safety
- `system3_model_fitness_audit.py` | categories=training_dataset,paper_live_safety
- `system3_model_lab.py` | categories=training_dataset,paper_live_safety
- `system3_phase331_signal_integrity.py` | categories=paper_live_safety
- `system3_signal_test_mode.py` | categories=master_entry,fallback_risk,paper_live_safety
- `test_system3_signal_engine.py` | categories=master_entry,prediction_runtime,fallback_risk
- `tests/test_forward_signal_integrity.py` | categories=master_entry,training_dataset,paper_live_safety
- `tmp_profile_signals.py` | categories=master_entry,backtesting,paper_live_safety
- `tools/playwright_dashboard_verification.py` | categories=master_entry,dashboard,fallback_risk
- `validate_signal_files.py` | categories=master_entry,training_dataset,prediction_runtime,paper_live_safety

## Next Safe Implementation

Create a benchmark leaderboard framework before changing model logic.
The framework must compare models using walk-forward validation, accuracy, precision/recall, P&L after costs, slippage/spread sensitivity, and model version.
No model should be promoted without passing this benchmark.
