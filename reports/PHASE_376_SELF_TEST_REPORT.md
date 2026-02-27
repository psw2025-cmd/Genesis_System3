# System3 Phase 376 - Self-Test Suite Report

**Generated:** 2025-12-09T21:05:58.074895

## Executive Summary

- **Total Tests:** 49
- **Passed:** 49 [OK]
- **Failed:** 0 [FAIL]
- **Pass Rate:** 100.0%

## Test Results by Category

### Phase Execution Test

- Passed: 15
- Failed: 0

**Phase Details:**
- Phase 361: PASS (0.141s)
- Phase 362: PASS (0.047s)
- Phase 363: PASS (0.047s)
- Phase 364: PASS (0.031s)
- Phase 365: PASS (0.174s)
- Phase 366: PASS (0.094s)
- Phase 367: PASS (0.078s)
- Phase 368: PASS (0.031s)
- Phase 369: PASS (0.016s)
- Phase 370: PASS (0.266s)
- Phase 371: PASS (0.156s)
- Phase 372: PASS (0.125s)
- Phase 373: PASS (0.119s)
- Phase 374: PASS (0.023s)
- Phase 375: PASS (0.109s)

### JSON Output Test

- Passed: 8
- Failed: 0

**File Details:**
- accuracy_tracker_365.json: PASS (1385 bytes)
- broker_latency_368.json: PASS (1726 bytes)
- dashboard_feed_364.json: PASS (10877 bytes)
- model_drift_363.json: PASS (620 bytes)
- pipeline_profile_369.json: PASS (1115 bytes)
- safety_guardrails_367.json: PASS (1617 bytes)
- schema_normalization_370.json: PASS (14353 bytes)
- strategy_ensemble_366.json: PASS (1165 bytes)

### CSV File Test

- Passed: 4
- Failed: 0

**File Details:**
- angel_index_ai_signals.csv: PASS (132 bytes)
- angel_index_ai_signals_curated.csv: PASS (309768 bytes)
- angel_index_ai_signals_with_forward.csv: PASS (314784 bytes)
- angel_virtual_orders.csv: PASS (541780 bytes)

### Safety Flag Test

- Passed: 3
- Failed: 0

**Safety Checks:**
- config/angel_automation_config.json:auto_execute_trades: PASS (value=False)
- config/live_trade_config.json:LIVE_TRADING_ENABLED: PASS (value=False)
- core/config/system3_ultra_safety.json:AUTO_EXECUTE_TRADES: PASS (value=False)

### No Live Trading Test

- Passed: 10
- Failed: 0

**Phase Details:**
- Phase system3_phase361_signal_pipeline_snapshot.py: PASS
- Phase system3_phase362_forward_calibrator.py: PASS
- Phase system3_phase363_model_drift_checker.py: PASS
- Phase system3_phase364_health_dashboard_feed.py: PASS
- Phase system3_phase365_accuracy_tracker.py: PASS
- Phase system3_phase366_strategy_ensemble_evaluator.py: PASS
- Phase system3_phase367_safety_guardrail_recommender.py: PASS
- Phase system3_phase368_broker_latency_monitor.py: PASS
- Phase system3_phase369_pipeline_profiler.py: PASS
- Phase system3_phase36_cull_orchestrator.py: PASS

### Performance Test

- Passed: 9
- Failed: 0

**Phase Details:**
- Phase 363: PASS (0.016s)
- Phase 364: PASS (0.047s)
- Phase 365: PASS (0.094s)
- Phase 370: PASS (0.250s)
- Phase 371: PASS (0.172s)
- Phase 372: PASS (0.125s)
- Phase 373: PASS (0.102s)
- Phase 374: PASS (0.010s)
- Phase 375: PASS (0.089s)

## Overall Status

[OK] ALL TESTS PASSED - System3 phases 361-375 are validated and production-ready
