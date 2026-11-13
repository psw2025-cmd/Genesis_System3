# DHAN 100-command forensic inventory

Generated from 100 distinct path/inventory checks on C:\Genesis_System3_clean. Read-only repo inspection; writes only to reports/latest/ui_recovery. These checks prove presence/tracked state, NOT live Dhan functionality.

## Counts
- PRESENT: 90
- TRACKED_MISSING: 8
- NOT_FOUND: 2

## Exact results
| ID | Area | Relative path | Status | Evidence |
|---|---|---|---|---|
| FC-001 | broker | core/brokers/dhan/dhan_readonly.py | PRESENT | bytes=29034 |
| FC-002 | broker | core/brokers/dhan/cloud_token_provider.py | PRESENT | bytes=9033 |
| FC-003 | broker | core/brokers/dhan/token_manager.py | PRESENT | bytes=3591 |
| FC-004 | broker | core/brokers/dhan/token_watchdog.py | PRESENT | bytes=918 |
| FC-005 | broker | core/brokers/dhan | PRESENT | 16 direct files |
| FC-006 | market | core/data/datasource_manager.py | PRESENT | bytes=27399 |
| FC-007 | market | core/data/dhan_option_chain_parser.py | PRESENT | bytes=8291 |
| FC-008 | market | core/data/dhan_master_cache.py | PRESENT | bytes=8372 |
| FC-009 | market | core/data/live_fetcher.py | PRESENT | bytes=258 |
| FC-010 | market | core/data | PRESENT | 15 direct files |
| FC-011 | feed | core/brokers/dhan/market_ltp.py | PRESENT | bytes=20233 |
| FC-012 | feed | core/brokers/dhan/instruments.py | PRESENT | bytes=4168 |
| FC-013 | feed | core/brokers/dhan/equity_fo_universe.py | PRESENT | bytes=11577 |
| FC-014 | feed | core/brokers/dhan/dhan_payload_normalizer.py | PRESENT | bytes=4903 |
| FC-015 | feed | core/brokers/dhan | PRESENT | 16 direct files |
| FC-016 | backend | dashboard/backend/app.py | PRESENT | bytes=503880 |
| FC-017 | backend | dashboard/backend/chain_adapter.py | PRESENT | bytes=14883 |
| FC-018 | backend | dashboard/backend/contract_gain_scanner.py | PRESENT | bytes=24610 |
| FC-019 | backend | dashboard/backend/equity_option_scanner.py | PRESENT | bytes=13198 |
| FC-020 | backend | dashboard/backend | PRESENT | 76 direct files |
| FC-021 | orders | dashboard/backend/order_gateway.py | PRESENT | bytes=9284 |
| FC-022 | orders | dashboard/backend/order_management.py | PRESENT | bytes=5117 |
| FC-023 | orders | dashboard/backend/paper_pipeline_v8.py | PRESENT | bytes=22760 |
| FC-024 | orders | dashboard/backend/trade_journal.py | PRESENT | bytes=4224 |
| FC-025 | orders | dashboard/backend | PRESENT | 76 direct files |
| FC-026 | ui | dashboard/frontend/src/config.ts | PRESENT | bytes=1599 |
| FC-027 | ui | dashboard/frontend/src/hooks/useData.ts | PRESENT | bytes=38243 |
| FC-028 | ui | dashboard/frontend/src/hooks/useWebSocket.ts | PRESENT | bytes=7799 |
| FC-029 | ui | dashboard/frontend/src/hooks/useWebSocketProd.ts | PRESENT | bytes=8214 |
| FC-030 | ui | dashboard/frontend/src | PRESENT | 9 direct files |
| FC-031 | docs | docs/DHAN_BROKER_API_ANALYSIS.md | PRESENT | bytes=20885 |
| FC-032 | docs | docs/SYSTEM3_DHAN_TOKEN_UPDATE_NOTE.md | PRESENT | bytes=1913 |
| FC-033 | docs | docs/BROKER_RECURRENCE_FORENSIC_CHECKLIST.md | PRESENT | bytes=11844 |
| FC-034 | docs | docs/OPTION_CHAIN_MISSING_DATA_REPORT.md | PRESENT | bytes=12952 |
| FC-035 | docs | docs | PRESENT | 510 direct files |
| FC-036 | scripts | scripts/verify_dhan_readonly.py | PRESENT | bytes=7397 |
| FC-037 | scripts | scripts/dhan_startup_check.py | PRESENT | bytes=1167 |
| FC-038 | scripts | scripts/system3_dhan_token_issuer_forensics.py | PRESENT | bytes=7880 |
| FC-039 | scripts | scripts/gcp_dhan_token_rotation_job.py | PRESENT | bytes=3702 |
| FC-040 | scripts | scripts | PRESENT | 421 direct files |
| FC-041 | tests | tests/test_dhan_only_chain_guard.py | PRESENT | bytes=2195 |
| FC-042 | tests | tests/test_dhan_option_chain_parser.py | PRESENT | bytes=5384 |
| FC-043 | tests | tests/test_dhan_single_token_authority.py | PRESENT | bytes=10149 |
| FC-044 | tests | tests/test_dhan_readonly_request_contract.py | PRESENT | bytes=9351 |
| FC-045 | tests | tests | PRESENT | 124 direct files |
| FC-046 | reports | reports/latest/dhan_parity/DHAN_LIVE_PARITY_ISSUES.md | TRACKED_MISSING |  |
| FC-047 | reports | reports/latest/dhan_token_issuer_forensics/summary.json | TRACKED_MISSING |  |
| FC-048 | reports | reports/latest/dhan_option_chain_schema_audit/summary.md | TRACKED_MISSING |  |
| FC-049 | reports | reports/latest/dhan_advance_platform_verification/summary.md | TRACKED_MISSING |  |
| FC-050 | reports | reports/latest | PRESENT | 2 direct files |
| FC-051 | engine | core/engine/dhan_real_data_extractor.py | PRESENT | bytes=5319 |
| FC-052 | engine | core/engine/dhan_real_outcome_logger.py | PRESENT | bytes=5183 |
| FC-053 | engine | core/engine/dhan_trade_executor.py | PRESENT | bytes=5220 |
| FC-054 | engine | core/engine/dhan_synthetic_backtester.py | PRESENT | bytes=23356 |
| FC-055 | engine | core/engine | PRESENT | 444 direct files |
| FC-056 | config | config/dhan_automation_config.json | PRESENT | bytes=170 |
| FC-057 | config | config/system3_broker_config.yml | PRESENT | bytes=608 |
| FC-058 | config | config/runtime_flags.json | PRESENT | bytes=533 |
| FC-059 | config | config/kill_switch.json | PRESENT | bytes=568 |
| FC-060 | config | config | PRESENT | 24 direct files |
| FC-061 | safety | core/brokers/dhan/broker_legacy.py | PRESENT | bytes=1012 |
| FC-062 | safety | core/brokers/dhan/preflight.py | PRESENT | bytes=1328 |
| FC-063 | safety | core/brokers/dhan/cloud_status_probe.py | PRESENT | bytes=18256 |
| FC-064 | safety | core/brokers/dhan/first_rejection_trace.py | PRESENT | bytes=2852 |
| FC-065 | safety | core/brokers/dhan | PRESENT | 16 direct files |
| FC-066 | history | core/data/history_fetcher.py | PRESENT | bytes=5962 |
| FC-067 | history | core/data/nse_provider.py | PRESENT | bytes=6742 |
| FC-068 | history | core/data/nse_session.py | PRESENT | bytes=587 |
| FC-069 | history | core/data/dhan_option_chain_parser.py | PRESENT | bytes=8291 |
| FC-070 | history | core/data | PRESENT | 15 direct files |
| FC-071 | rest | src/dhan/expiry_selector.py | PRESENT | bytes=8808 |
| FC-072 | rest | src/dhan/live_chain_rest.py | PRESENT | bytes=5513 |
| FC-073 | rest | src/dhan/live_chain_ws.py | PRESENT | bytes=1235 |
| FC-074 | rest | src/dhan/missing.py | NOT_FOUND |  |
| FC-075 | rest | src/dhan | PRESENT | 3 direct files |
| FC-076 | frontend | dashboard/frontend/src/components/MarketTopCePeTable.tsx | PRESENT | bytes=13248 |
| FC-077 | frontend | dashboard/frontend/src/components/PaperTrading.tsx | PRESENT | bytes=24879 |
| FC-078 | frontend | dashboard/frontend/src/components/ChainAnalytics.tsx | PRESENT | bytes=9722 |
| FC-079 | frontend | dashboard/frontend/src/components/Alerts.tsx | PRESENT | bytes=4271 |
| FC-080 | frontend | dashboard/frontend/src/components | PRESENT | 54 direct files |
| FC-081 | audit | docs/OPTION_CHAIN_TEST_CHECKLIST.md | PRESENT | bytes=5823 |
| FC-082 | audit | docs/OPTION_CHAIN_VERIFICATION_REPORT.md | PRESENT | bytes=5964 |
| FC-083 | audit | docs/BROKER_SETUP.md | PRESENT | bytes=2127 |
| FC-084 | audit | docs/ALL_INDICES_OPTION_CHAIN_FETCH.md | PRESENT | bytes=7648 |
| FC-085 | audit | docs | PRESENT | 510 direct files |
| FC-086 | pipeline | core/engine/dhan_blended_model_trainer.py | PRESENT | bytes=4309 |
| FC-087 | pipeline | core/engine/dhan_pnl_simulator.py | PRESENT | bytes=6349 |
| FC-088 | pipeline | core/engine/dhan_signal_outcome_analyzer.py | PRESENT | bytes=8303 |
| FC-089 | pipeline | core/engine/dhan_execution_guardrail.py | PRESENT | bytes=4222 |
| FC-090 | pipeline | core/engine | PRESENT | 444 direct files |
| FC-091 | jobs | scripts/dhan_token_auto_refresh.py | PRESENT | bytes=1191 |
| FC-092 | jobs | scripts/dhan_watchdog_runner.py | PRESENT | bytes=739 |
| FC-093 | jobs | scripts/sync_dhan_instruments_master.py | PRESENT | bytes=4456 |
| FC-094 | jobs | scripts/dhan_full_api_test.py | PRESENT | bytes=13760 |
| FC-095 | jobs | scripts | PRESENT | 421 direct files |
| FC-096 | evidence | reports/latest/dhan_parity/api_chain_NIFTY.json | TRACKED_MISSING |  |
| FC-097 | evidence | reports/latest/dhan_parity/api_broker_status.json | TRACKED_MISSING |  |
| FC-098 | evidence | reports/latest/dhan_parity/api_health.json | TRACKED_MISSING |  |
| FC-099 | evidence | reports/latest/dhan_parity/DHAN_PARITY_LIVE_COMPARE.json | TRACKED_MISSING |  |
| FC-100 | evidence | reports/latest/dhan_parity | NOT_FOUND |  |
