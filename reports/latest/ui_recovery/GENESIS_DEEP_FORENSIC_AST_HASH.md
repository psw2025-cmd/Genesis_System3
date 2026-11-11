# Deep forensic: Git NUL-path, SHA256, Python AST

Tracked paths: 3197; scanned files: 2150; Python parsed: 953; parse failures: 0; exact duplicate content groups: 5; repeated non-init basenames: 16; sensitive call sites: 628; scan errors: 0.

## Exact SHA-256 duplicate groups

### DUP-1
- config/runtime_flags.json
- runtime_flags.json

### DUP-2
- config/system3_config.json
- core/engine/config/system3_config.json

### DUP-3
- docs/Phases 311–330 = Integrity + Anti-corruption + Observability layer for System3.md
- docs/SYSTEM3_WARN_PHASES_ANALYSIS_20251205.md

### DUP-4
- docs/audits/system3_quant_lifecycle/sessions/20260816T123000Z/00_INSTRUCTION_SOURCE.md
- docs/chatgpt_instruction_for_cursar_2.md

### DUP-5
- docs/system3_phases_101_130_final_test_results - Copy.md
- docs/system3_phases_101_130_final_test_results.md

## Repeated filenames (non __init__.py)

### NAME-1
- .agy-proof/receipt.json
- .agy-proof/runs/2026-10-30T043400Z-acc25d6d452d4615852adea290a10fa8/receipt.json
- .agy-proof/runs/2026-10-30T043443Z-e0db2824c3e84ca8a32e6100760fd666/receipt.json
- .agy-proof/runs/2026-10-30T055731Z-52aead48e6f949f4a129d206ff704b3f/receipt.json
- .agy-proof/runs/2026-10-30T055823Z-8839d775f87d4f12a9009a37b9bc240d/receipt.json

### NAME-2
- .cursor/settings.json
- .vscode/settings.json

### NAME-3
- .vscode/tasks.json
- agent_memory/tasks.json

### NAME-4
- README.md
- dashboard/README.md
- docs/ultra_micro/README.md
- reports/latest/analyzer_paper_lifecycle_proof/README.md

### NAME-5
- config/kill_switch.json
- kill_switch.json

### NAME-6
- config/runtime_flags.json
- runtime_flags.json

### NAME-7
- config/system3_config.json
- core/engine/config/system3_config.json

### NAME-8
- core/engine/ensemble_predictor.py
- src/ml/ensemble_predictor.py

### NAME-9
- core/engine/greeks_engine/greeks_calculator.py
- dashboard/backend/greeks_calculator.py

### NAME-10
- dashboard/app.py
- dashboard/backend/app.py

### NAME-11
- dashboard/frontend/package-lock.json
- desktop_app/package-lock.json
- package-lock.json
- tools/playwright-setup/package-lock.json

### NAME-12
- dashboard/frontend/package.json
- desktop_app/package.json
- package.json
- tools/package.json
- tools/playwright-setup/package.json

### NAME-13
- reports/latest/analyzer_paper_lifecycle_proof/summary.json
- reports/latest/system3_auto_gates/summary.json

### NAME-14
- reports/latest/analyzer_paper_lifecycle_proof/summary.md
- reports/latest/system3_auto_gates/summary.md

### NAME-15
- scripts/performance_metrics.py
- src/analytics/performance_metrics.py

### NAME-16
- src/ranking/market_result_validator.py
- src/validation/market_result_validator.py

## Python syntax parse errors

## Sensitive call site sample (full JSON includes all)
- core/data/datasource_manager.py:217 read_csv
- core/data/instruments_cache.py:35 read_csv
- core/engine/ai_model/data_balancing_v2.py:54 read_csv
- core/engine/ai_model/feature_engineering_v2.py:455 to_csv
- core/engine/ai_model/feature_engineering_v2.py:446 read_csv
- core/engine/ai_model/ml_predictor.py:98 read_csv
- core/engine/ai_model/ml_predictor.py:117 read_csv
- core/engine/ai_model/smote_balancer.py:270 to_csv
- core/engine/ai_model/smote_balancer.py:245 read_csv
- core/engine/ai_model/smote_balancer.py:243 read_csv
- core/engine/ai_model/xgboost_trainer.py:82 read_csv
- core/engine/ai_model/xgboost_trainer.py:88 read_csv
- core/engine/ai_model/xgboost_trainer.py:94 read_csv
- core/engine/build_dhan_training_dataset.py:269 to_csv
- core/engine/build_dhan_training_dataset.py:23 read_csv
- core/engine/dhan_adaptive_volatility_map.py:37 read_csv
- core/engine/dhan_alerting_system.py:89 read_csv
- core/engine/dhan_alerting_system.py:117 read_csv
- core/engine/dhan_auto_threshold_adjuster.py:53 read_csv
- core/engine/dhan_auto_threshold_adjuster.py:115 read_csv
- core/engine/dhan_blended_dataset_builder.py:114 to_csv
- core/engine/dhan_blended_dataset_builder.py:40 read_csv
- core/engine/dhan_blended_dataset_builder.py:49 read_csv
- core/engine/dhan_blended_model_trainer.py:90 to_csv
- core/engine/dhan_blended_model_trainer.py:58 read_csv
- core/engine/dhan_blended_model_trainer.py:67 read_csv
- core/engine/dhan_blended_model_trainer_v2.py:180 read_csv
- core/engine/dhan_blended_model_trainer_v2.py:35 read_csv
- core/engine/dhan_blended_model_trainer_v2.py:120 read_csv
- core/engine/dhan_blended_training_orchestrator_dryrun.py:44 read_csv
- core/engine/dhan_blended_training_v3.py:79 read_csv
- core/engine/dhan_blended_training_v3.py:101 read_csv
- core/engine/dhan_blended_training_v3.py:95 read_csv
- core/engine/dhan_confidence_calibrator.py:59 read_csv
- core/engine/dhan_confidence_calibrator.py:60 read_csv
- core/engine/dhan_daily_pnl_summary.py:44 read_csv
- core/engine/dhan_daily_pnl_summary.py:59 read_csv
- core/engine/dhan_daily_report_generator.py:103 read_csv
- core/engine/dhan_daily_report_generator.py:139 read_csv
- core/engine/dhan_daily_report_generator.py:175 read_csv
- core/engine/dhan_dataset_merger_real_synth_v1.py:127 to_csv
- core/engine/dhan_dataset_merger_real_synth_v1.py:159 read_csv
- core/engine/dhan_dataset_merger_real_synth_v1.py:50 read_csv
- core/engine/dhan_dataset_merger_real_synth_v1.py:67 read_csv
- core/engine/dhan_execution_guardrail.py:114 read_csv
- core/engine/dhan_feature_drift_analyzer.py:51 read_csv
- core/engine/dhan_feature_drift_analyzer.py:52 read_csv
- core/engine/dhan_feature_drift_analyzer.py:180 to_csv
- core/engine/dhan_feature_importance.py:142 to_csv
- core/engine/dhan_feature_importance.py:186 to_csv
- core/engine/dhan_feature_importance.py:37 read_csv
- core/engine/dhan_feature_ranker.py:41 read_csv
- core/engine/dhan_feature_ranker.py:89 to_csv
- core/engine/dhan_intraday_pnl_monitor.py:33 read_csv
- core/engine/dhan_intraday_pnl_monitor.py:60 read_csv
- core/engine/dhan_latency_drift_observatory.py:45 read_csv
- core/engine/dhan_live_ai_signals.py:291 to_csv
- core/engine/dhan_live_ai_signals.py:435 read_csv
- core/engine/dhan_live_signals.py:79 read_csv
- core/engine/dhan_live_snapshot_reasoner.py:86 read_csv
- core/engine/dhan_market_intelligence_dashboard.py:39 read_csv
- core/engine/dhan_market_regime_recorder.py:53 read_csv
- core/engine/dhan_market_regime_recorder.py:132 read_csv
- core/engine/dhan_market_regime_recorder.py:96 to_csv
- core/engine/dhan_market_regime_recorder.py:91 read_csv
- core/engine/dhan_misfire_classifier_v2.py:142 to_csv
- core/engine/dhan_misfire_classifier_v2.py:40 read_csv
- core/engine/dhan_misfire_classifier_v2.py:136 read_csv
- core/engine/dhan_misfire_detector.py:129 to_csv
- core/engine/dhan_misfire_detector.py:123 read_csv
- core/engine/dhan_options_analyze.py:223 to_csv
- core/engine/dhan_options_analyze.py:23 read_csv
- core/engine/dhan_outcome_placeholder_generator.py:43 read_csv
- core/engine/dhan_outcome_placeholder_generator.py:74 to_csv
- core/engine/dhan_outcome_placeholder_generator.py:104 read_csv
- core/engine/dhan_performance_consistency_checker.py:47 read_csv
- core/engine/dhan_pnl_dummy_seed.py:26 read_csv
- core/engine/dhan_pnl_dummy_seed.py:85 to_csv
- core/engine/dhan_pnl_simulator.py:202 to_csv
- core/engine/dhan_pnl_simulator.py:50 read_csv
- core/engine/dhan_pnl_simulator.py:56 read_csv
- core/engine/dhan_real_data_capture_starter.py:58 to_csv
- core/engine/dhan_real_data_capture_starter.py:88 read_csv
- core/engine/dhan_real_data_capture_starter.py:53 read_csv
- core/engine/dhan_real_data_extractor.py:146 to_csv
- core/engine/dhan_real_data_extractor.py:44 read_csv
- core/engine/dhan_real_master_dataset.py:200 to_csv
- core/engine/dhan_real_master_dataset.py:66 read_csv
- core/engine/dhan_real_master_dataset.py:79 read_csv
- core/engine/dhan_real_master_dataset.py:92 read_csv
- core/engine/dhan_real_master_dataset.py:105 read_csv
- core/engine/dhan_real_outcome_logger.py:87 to_csv
- core/engine/dhan_real_outcome_logger.py:105 read_csv
- core/engine/dhan_real_outcome_logger.py:82 read_csv
- core/engine/dhan_real_signal_collector_v2.py:86 to_csv
- core/engine/dhan_real_signal_collector_v2.py:117 read_csv
- core/engine/dhan_real_signal_collector_v2.py:53 read_csv
- core/engine/dhan_real_signal_collector_v2.py:73 read_csv
- core/engine/dhan_real_threshold_reco_v3.py:54 read_csv
- core/engine/dhan_risk_profile_optimizer_v3.py:47 read_csv

## Scan errors
