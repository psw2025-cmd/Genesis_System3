# System3 Phase Index - Ultra Micro Detail
**Generated**: 2025-12-04  
**Total Phases Documented**: 310+ phases

---

## Phase Ranges Overview

| Range | Count | Status | Diagnostic Script | Loading Method |
|-------|-------|--------|-------------------|----------------|
| 1-100 | 100 | ✅ Implemented | Various | Mixed |
| 101-200 | 100 | ✅ Implemented | Various | Mixed |
| 201-230 | 30 | ✅ In Autorun | `system3_phase_201_230_diagnostics.py` | PHASE_IMPORTS |
| 231-260 | 30 | ✅ In Autorun | `system3_phase_231_260_diagnostics.py` | PHASE_MODULES |
| 261-300 | 40 | ✅ In Autorun | `system3_phase_261_300_diagnostics.py` | PHASE_MODULES |
| 301-310 | 10 | ✅ In Autorun | `system3_phases_301_310_diagnostics.py` | PHASE_MODULES |

**Total Phases in Autorun**: 110 phases (201-310)

---

## Phases 201-230 (Ultra Micro Detail)

| Phase | Module Name | Function | Purpose | Status |
|-------|-------------|----------|---------|--------|
| 201 | `system3_phase201_filesystem_integrity` | `run_phase201()` | Filesystem integrity checks | ✅ |
| 202 | `system3_phase202_permissions_self_repair` | `run_phase202()` | Permission repair | ✅ |
| 203 | `system3_phase203_config_consistency` | `run_phase203()` | Config validation | ✅ |
| 204 | `system3_phase204_python_env_validator` | `run_phase204()` | Python environment check | ✅ |
| 205 | `system3_phase205_broker_selftest` | `run_phase205()` | Broker connectivity test | ✅ |
| 206 | `system3_phase206_model_compatibility` | `run_phase206()` | Model compatibility check | ✅ |
| 207 | `system3_phase207_hotfix_registry` | `run_phase207()` | Hotfix management | ✅ |
| 208 | `system3_phase208_signal_consistency` | `run_phase208()` | Signal consistency check | ✅ |
| 209 | `system3_phase209_duplicate_purger` | `run_phase209()` | Remove duplicate signals | ✅ |
| 210 | `system3_phase210_timegap_analyzer` | `run_phase210()` | Time gap analysis | ✅ |
| 211 | `system3_phase211_feature_drift` | `run_phase211()` | Feature drift detection | ✅ |
| 212 | `system3_phase212_label_quality` | `run_phase212()` | Label quality check | ✅ |
| 213 | `system3_phase213_training_window` | `run_phase213()` | Training window selection | ✅ |
| 214 | `system3_phase214_hyperparam_snapshot` | `run_phase214()` | Hyperparameter snapshot | ✅ |
| 215 | `system3_phase215_overfit_sentinel` | `run_phase215()` | Overfitting detection | ✅ |
| 216 | `system3_phase216_greeks_audit` | `run_phase216()` | Greeks validation | ✅ |
| 217 | `system3_phase217_vol_regime` | `run_phase217()` | Volatility regime detection | ✅ |
| 218 | `system3_phase218_momentum_scanner` | `run_phase218()` | Momentum pattern detection | ✅ |
| 219 | `system3_phase219_breakout_analyzer` | `run_phase219()` | Breakout pattern analysis | ✅ |
| 220 | `system3_phase220_correlation_map` | `run_phase220()` | Correlation matrix | ✅ |
| 221 | `system3_phase221_forward_returns` | `run_phase221()` | **Forward returns calculation** | ✅ |
| 222 | `system3_phase222_signal_edge` | `run_phase222()` | **Signal edge estimation** | ✅ |
| 223 | `system3_phase223_threshold_optimizer` | `run_phase223()` | Threshold optimization | ✅ |
| 224 | `system3_phase224_score_attribution` | `run_phase224()` | Score attribution analysis | ✅ |
| 225 | `system3_phase225_label_reconciliation` | `run_phase225()` | Label reconciliation | ✅ |
| 226 | `system3_phase226_feature_importance` | `run_phase226()` | Feature importance | ✅ |
| 227 | `system3_phase227_latency_profiler` | `run_phase227()` | Latency profiling | ✅ |
| 228 | `system3_phase228_snapshot_coverage` | `run_phase228()` | Snapshot coverage analysis | ✅ |
| 229 | `system3_phase229_schema_guard` | `run_phase229()` | Schema validation | ✅ |
| 230 | `system3_phase230_ai_fallback_audit` | `run_phase230()` | AI fallback audit | ✅ |

**Key Phases**:
- **Phase 221**: Calculates forward returns (1, 3, 5 snapshots) from curated signals
- **Phase 222**: Estimates signal edge (EV tables) from forward returns
- **Phase 223**: Optimizes thresholds based on EV analysis

---

## Phases 231-260 (Ultra Micro Detail)

**Loading**: Via `system3_phase_231_260_diagnostics.py` → `PHASE_MODULES` dict

**Key Phases** (from file listing):
- 231-260: Various analysis and optimization phases
- All loaded dynamically from diagnostic script

**Execution**: Every 30 minutes during market hours (phases 220-260)

---

## Phases 261-300 (Ultra Micro Detail)

**Loading**: Via `system3_phase_261_300_diagnostics.py` → `PHASE_MODULES` dict

**Key Phases** (from file listing):
- 261: Portfolio Risk Analyzer
- 262: Multi-Timeframe Consistency
- 263: Advanced PnL Attribution
- 264: Signal Quality Metrics
- 265: Execution Quality Analyzer
- 266: Capital Efficiency Tracker
- 267: Drawdown Analyzer
- 268: Sharpe Ratio Calculator
- 269: Winrate by Time
- 270: Regime Performance Comparison
- 271: Hyperparameter Search
- 272: Feature Selection Optimizer
- 273: Model Ensemble Builder
- 274: Threshold Auto Tuner
- 275: Position Sizing Optimizer
- 276: Risk Reward Optimizer
- 277: Entry Timing Optimizer
- 278: Exit Timing Optimizer
- 279: Portfolio Rebalancer
- 280: Strategy Backtester
- 281: Realtime Performance Monitor
- 282: Anomaly Detector
- 283: Drift Monitor
- 284: Alert Aggregator
- 285: Health Dashboard Generator
- 286: Performance Degradation Detector
- 287: Resource Usage Monitor
- 288: Latency Monitor
- 289: Error Rate Tracker
- 290: System Health Score
- 291: Daily Performance Report
- 292: Weekly Summary Report
- 293: Monthly Analytics Report
- 294: Strategy Performance Report
- 295: Risk Metrics Report
- 296: Model Performance Report
- 297: Trade Execution Report
- 298: System Status Report
- 299: Master Summary Report
- 300: Phase Completion Validator

---

## Phases 301-310 (Ultra Micro Detail)

| Phase | Module Name | Function | Purpose | Status |
|-------|-------------|----------|---------|--------|
| 301 | `system3_phase301_daily_live_vs_forward` | `run_phase301()` | Compare live vs forward returns | ✅ |
| 302 | `system3_phase302_regime_performance` | `run_phase302()` | Regime-based performance | ✅ |
| 303 | `system3_phase303_edge_decay` | `run_phase303()` | Signal edge decay analysis | ✅ |
| 304 | `system3_phase304_threshold_tuner` | `run_phase304()` | **Threshold tuning** | ✅ |
| 305 | `system3_phase305_confidence_tier` | `run_phase305()` | Confidence tier analysis | ✅ |
| 306 | `system3_phase306_staleness_guard` | `run_phase306()` | Data staleness detection | ✅ |
| 307 | `system3_phase307_live_vs_test_consistency` | `run_phase307()` | Live vs test consistency | ✅ |
| 308 | `system3_phase308_daily_dashboard` | `run_phase308()` | Daily dashboard generation | ✅ |
| 309 | `system3_phase309_schedule_hints` | `run_phase309()` | Schedule optimization hints | ✅ |
| 310 | `system3_phase310_ultra_health` | `run_phase310()` | Ultra health check | ✅ |

**Key Phase**:
- **Phase 304**: Threshold tuner - proposes optimal BUY/SELL thresholds

---

## Phase Execution Schedule (Ultra Micro)

### Pre-Market (Once at Startup)
- **Range**: Phases 201-310
- **Time**: Runs immediately when autorun master starts
- **Duration**: ~1-2 minutes
- **Results**: Typically 44 OK, 45 WARN, 0 ERROR, 21 SKIPPED

### During Market Hours (Every 30 Minutes)
- **Range**: Phases 220-260
- **Time**: Every 30 minutes (e.g., 9:15, 9:45, 10:15, ...)
- **Condition**: Only during market hours (09:15-15:30 IST)
- **Results**: Typically 6-7 OK, 13-14 WARN, 0 ERROR, 21 SKIPPED

### Periodic Tasks
- **Curated Refresh**: Every 2 hours (phases 220-260 context)
- **OP Cycles**: Every hour (OP1, OP2, OP3)

---

## Phase Status Distribution

**Typical Pre-Market Run**:
- ✅ **OK**: 44 phases (40%)
- ⚠️ **WARN**: 45 phases (41%) - Expected, non-blocking
- ❌ **ERROR**: 0 phases (0%) - **ZERO ERRORS** ✅
- ⏭️ **SKIPPED**: 21 phases (19%) - Not implemented or conditional

**Typical Intraday Run** (220-260):
- ✅ **OK**: 6-7 phases
- ⚠️ **WARN**: 13-14 phases
- ❌ **ERROR**: 0 phases
- ⏭️ **SKIPPED**: 21 phases

---

## Phase Dependencies (Ultra Micro)

### Critical Dependency Chain

```
Phase 221 (Forward Returns)
    ↓
Phase 222 (Signal Edge)
    ↓
Phase 304 (Threshold Tuner)
    ↓
Live Signal Engine (Uses thresholds)
```

### Data Flow Between Phases

1. **Phase 221** reads: `dhan_index_ai_signals_curated.csv`
2. **Phase 221** writes: `dhan_index_ai_signals_with_forward.csv`
3. **Phase 222** reads: `dhan_index_ai_signals_with_forward.csv`
4. **Phase 222** writes: `logs/research/system3_signal_edge_report.md`
5. **Phase 304** reads: `system3_signal_edge_report.md`
6. **Phase 304** writes: `storage/meta/system3_live_thresholds.json`

---

## Individual Phase Documentation

See `phases/` directory for ultra-micro documentation of each phase:
- `phase_001_ultra_micro.md` through `phase_310_ultra_micro.md`

Each file contains:
- Complete function list with line numbers
- Class definitions
- All imports
- Input files
- Output files
- Dependencies
- Code snippets

---

**Documentation Generated**: 2025-12-04  
**Status**: ✅ **PHASE INDEX COMPLETE**

