# Genesis System3 â€” 50 file mismatch forensic checks

Source: on-disk tracked code/docs. Checks are read-only, except reports written here. SHA-256 only for files <=2MB. Same size or same filename does not prove defect. Excludes secret-like filenames.

Scanned tracked, on-disk files: 
2148

| Check | Scope | Heuristic | Matches | Sample paths |
|---|---|---|---:|---|
| MM-001 | core/brokers/dhan | same_filename_multiple_paths | 0 |  |
| MM-002 | core/brokers/dhan | same_size_multiple_paths | 0 |  |
| MM-003 | core/brokers/dhan | zero_byte_files | 1 | core/brokers/dhan/init_legacy.py |
| MM-004 | core/brokers/dhan | tiny_source_under_100_bytes | 0 |  |
| MM-005 | core/brokers/dhan | oversized_source_over_100KB | 0 |  |
| MM-006 | core/brokers/dhan | backup_or_copy_suffix | 0 |  |
| MM-007 | core/brokers/dhan | legacy_or_deprecated_filename | 2 | core/brokers/dhan/broker_legacy.py ; core/brokers/dhan/init_legacy.py |
| MM-008 | core/brokers/dhan | test_or_mock_in_runtime_tree | 0 |  |
| MM-009 | core/brokers/dhan | mixed_case_name_collisions | 0 |  |
| MM-010 | core/brokers/dhan | duplicate_content_sha256 | 0 |  |
| MM-011 | core/data | same_filename_multiple_paths | 1 | core/data/__init__.py <> core/data/lake/__init__.py |
| MM-012 | core/data | same_size_multiple_paths | 0 |  |
| MM-013 | core/data | zero_byte_files | 2 | core/data/__init__ - Copy - Copy - Copy (3).py ; core/data/__init__.py |
| MM-014 | core/data | tiny_source_under_100_bytes | 0 |  |
| MM-015 | core/data | oversized_source_over_100KB | 0 |  |
| MM-016 | core/data | backup_or_copy_suffix | 1 | core/data/__init__ - Copy - Copy - Copy (3).py |
| MM-017 | core/data | legacy_or_deprecated_filename | 0 |  |
| MM-018 | core/data | test_or_mock_in_runtime_tree | 1 | core/data/selftest_storage.py |
| MM-019 | core/data | mixed_case_name_collisions | 0 |  |
| MM-020 | core/data | duplicate_content_sha256 | 0 |  |
| MM-021 | core/engine | same_filename_multiple_paths | 1 | core/engine/__init__.py <> core/engine/ai_model/__init__.py <> core/engine/breakout_model/__init__.py <> core/engine/entry_exit_engine/__init__.py <> core/engine/greeks_engine/__init__.py <> core/engine/momentum_model/__init__.py <> core/engine/scoring_engine/__init__.py <> core/engine/trend_model/__init__.py <> core/engine/volatility_model/__init__.py |
| MM-022 | core/engine | same_size_multiple_paths | 16 | core/engine/dhan_auto_threshold_adjuster.py <> core/engine/dhan_model_selector.py ; core/engine/system3_phase122_reserved.py <> core/engine/system3_phase123_reserved.py <> core/engine/system3_phase124_reserved.py <> core/engine/system3_phase125_reserved.py ; core/engine/system3_phase127_control_panel_stub.py <> core/engine/system3_phase128_control_panel_stub.py <> core/engine/system3_phase129_control_panel_stub.py <> core/engine/system3_phase130_control_panel_stub.py ; core/engine/system3_phase152_reserved_stub.py <> core/engine/system3_phase153_reserved_stub.py <> core/engine/system3_phase154_reserved_stub.py <> core/engine/system3_phase155_reserved_stub.py ; core/engine/system3_phase158_regime_stability.py <> core/engine/ultra_safety.py ; core/engine/system3_phase161_risk_attribution_analysis.py <> core/engine/system3_phase170_stability_metrics_summary.py |
| MM-023 | core/engine | zero_byte_files | 2 | core/engine/__init__.py ; core/engine/system3_phase368_broker_latency_monitor.py |
| MM-024 | core/engine | tiny_source_under_100_bytes | 2 | core/engine/storage/history/HEALTHCHECK_20251209_210028.json ; core/engine/storage/history/LIVE_BTCUSDT_20251209_210803.json |
| MM-025 | core/engine | oversized_source_over_100KB | 0 |  |
| MM-026 | core/engine | backup_or_copy_suffix | 29 | core/engine/ai_model/data_balancing_v2.py ; core/engine/ai_model/feature_engineering_v2.py ; core/engine/dhan_auto_threshold_adjuster.py ; core/engine/dhan_blended_model_trainer_v2.py ; core/engine/dhan_blended_training_v3.py ; core/engine/dhan_dataset_merger_real_synth_v1.py |
| MM-027 | core/engine | legacy_or_deprecated_filename | 0 |  |
| MM-028 | core/engine | test_or_mock_in_runtime_tree | 9 | core/engine/dhan_pnl_dummy_seed.py ; core/engine/dhan_synthetic_backtester.py ; core/engine/generate_synthetic_dhan_training.py ; core/engine/system3_phase197_micro_capital_test_plan.py ; core/engine/system3_phase307_live_vs_test_consistency.py ; core/engine/system3_phase376_self_test_suite.py |
| MM-029 | core/engine | mixed_case_name_collisions | 0 |  |
| MM-030 | core/engine | duplicate_content_sha256 | 0 |  |
| MM-031 | dashboard/backend | same_filename_multiple_paths | 1 | dashboard/backend/broker/__init__.py <> dashboard/backend/middleware/__init__.py <> dashboard/backend/routers/__init__.py <> dashboard/backend/sandbox/__init__.py <> dashboard/backend/services/__init__.py |
| MM-032 | dashboard/backend | same_size_multiple_paths | 0 |  |
| MM-033 | dashboard/backend | zero_byte_files | 0 |  |
| MM-034 | dashboard/backend | tiny_source_under_100_bytes | 5 | dashboard/backend/broker/__init__.py ; dashboard/backend/broker/dhan_auth.py ; dashboard/backend/middleware/__init__.py ; dashboard/backend/routers/__init__.py ; dashboard/backend/services/__init__.py |
| MM-035 | dashboard/backend | oversized_source_over_100KB | 1 | dashboard/backend/app.py |
| MM-036 | dashboard/backend | backup_or_copy_suffix | 1 | dashboard/backend/paper_pipeline_v8.py |
| MM-037 | dashboard/backend | legacy_or_deprecated_filename | 0 |  |
| MM-038 | dashboard/backend | test_or_mock_in_runtime_tree | 2 | dashboard/backend/backtest_service.py ; dashboard/backend/synthetic_data_generator.py |
| MM-039 | dashboard/backend | mixed_case_name_collisions | 0 |  |
| MM-040 | dashboard/backend | duplicate_content_sha256 | 0 |  |
| MM-041 | dashboard/frontend/src | same_filename_multiple_paths | 0 |  |
| MM-042 | dashboard/frontend/src | same_size_multiple_paths | 1 | dashboard/frontend/src/config.ts <> dashboard/frontend/src/lib/consoleHygiene.ts |
| MM-043 | dashboard/frontend/src | zero_byte_files | 0 |  |
| MM-044 | dashboard/frontend/src | tiny_source_under_100_bytes | 1 | dashboard/frontend/src/test-setup.ts |
| MM-045 | dashboard/frontend/src | oversized_source_over_100KB | 0 |  |
| MM-046 | dashboard/frontend/src | backup_or_copy_suffix | 0 |  |
| MM-047 | dashboard/frontend/src | legacy_or_deprecated_filename | 0 |  |
| MM-048 | dashboard/frontend/src | test_or_mock_in_runtime_tree | 0 |  |
| MM-049 | dashboard/frontend/src | mixed_case_name_collisions | 0 |  |
| MM-050 | dashboard/frontend/src | duplicate_content_sha256 | 0 |  |
