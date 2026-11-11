# System3 Directory Tree (3 Levels Deep)

**Project Root**: `C:\Genesis_System3`  
**Date**: 2025-11-30

---

## Core Structure

```
C:\Genesis_System3\
├── core\
│   ├── engine\                    # 130+ Python modules
│   │   ├── dhan_*.py             # Baseline trading modules
│   │   ├── system3_phase*.py      # Ultra phases 31-43
│   │   ├── ultra_*.py             # Ultra shadow modules
│   │   ├── dhan_trade_config.py  # Trade thresholds
│   │   ├── dhan_automation_config.py  # Automation settings
│   │   └── ...
│   ├── ultra\                     # Ultra phases 21-30, 46-55
│   │   ├── phase21_adaptive_risk_engine.py
│   │   ├── phase22_position_sizing.py
│   │   ├── phase23_volatility_impact.py
│   │   ├── phase24_confidence_drift.py
│   │   ├── phase25_stoploss_engine.py
│   │   ├── phase26_target_engine.py
│   │   ├── phase27_rr_balancer.py
│   │   ├── phase28_auto_corrector.py
│   │   ├── phase29_sensitivity.py
│   │   ├── phase30_calibration_engine.py
│   │   ├── phase46_meta_fusion.py
│   │   ├── phase47_confidence_vector.py
│   │   ├── phase48_error_scanner.py
│   │   ├── phase49_risk_regulator.py
│   │   ├── phase50_prediction_explainer.py
│   │   ├── phase51_probability_engine.py
│   │   ├── phase52_multi_broker.py
│   │   ├── phase53_monitoring_agent.py
│   │   ├── phase54_back_reconstruction.py
│   │   └── phase55_intelligence_dashboard.py
│   ├── models\
│   │   ├── dhan\             # Baseline models
│   │   │   ├── *_model.pkl
│   │   │   └── *_model_meta.json
│   │   ├── dhan_real_blended\  # Blended models
│   │   │   ├── *_blended_v3.pkl
│   │   │   └── *_blended_v3_meta.json
│   │   └── dhan_ultra\       # Ultra models
│   │       ├── *_ultra_model.pkl
│   │       └── *_ultra_model_meta.json
│   ├── config\
│   │   ├── system3_active_profile.json
│   │   └── system3_ultra_safety.json
│   ├── data\
│   │   ├── data_router.py
│   │   ├── history_fetcher.py
│   │   ├── live_fetcher.py
│   │   └── storage_manager.py
│   └── brokers\
│       └── dhan\
│           ├── broker.py
│           └── instruments.py
```

---

## Storage Structure

```
C:\Genesis_System3\
├── storage\
│   ├── training\                  # Training datasets
│   │   ├── *.csv
│   │   └── *.parquet
│   ├── live\                      # Live trading data
│   │   ├── dhan_index_ai_signals.csv
│   │   ├── dhan_index_ai_trades_plan.csv
│   │   ├── dhan_index_ai_pnl_log.csv
│   │   ├── dhan_index_ai_trades_exec_log.csv
│   │   └── dhan_index_options_watch.csv
│   ├── learning\                  # Real-data learning
│   │   ├── dhan_real_outcomes.csv
│   │   ├── real_signals_raw.csv
│   │   └── dhan_index_real_master_dataset.csv
│   ├── learning_ultra\           # Ultra learning data
│   │   ├── dhan_ultra_shadow_master.csv
│   │   └── dhan_ultra_shadow_master.parquet
│   ├── ultra\                    # Ultra phase outputs
│   │   ├── phase31_ultra_fused_decisions.csv
│   │   ├── phase35_decision_audit.csv
│   │   ├── phase37_policy_risk_dashboard.md
│   │   ├── ph46_ph55\            # Phases 46-55 outputs
│   │   │   ├── phase46_*.csv
│   │   │   ├── phase46_*.json
│   │   │   └── ... (20 files total)
│   │   └── ...
│   ├── reports\                  # Reports and summaries
│   │   ├── dhan_daily_learning_report_*.txt
│   │   ├── daily_report_*.txt
│   │   ├── real_learning_summary_*.csv
│   │   ├── rolling_learning_dashboard_*.csv
│   │   ├── feature_drift\
│   │   ├── real_learning_daily\
│   │   ├── threshold_reco\
│   │   └── ultra_obs\
│   ├── reports_ultra\            # Ultra-specific reports
│   │   ├── phase21_risk_evaluations.csv
│   │   ├── phase24_confidence_drift_report.json
│   │   ├── phase29_sensitivity_analysis.csv
│   │   └── ...
│   ├── config\                   # Configuration files
│   │   ├── dhan_blended_training_v3_config.json
│   │   ├── risk_profile_suggestions.json
│   │   ├── thresholds_*.json
│   │   └── system3_*.json
│   ├── snapshots\                # Model snapshots
│   │   └── YYYYMMDD_HHMMSS\
│   │       ├── models\
│   │       ├── configs\
│   │       └── snapshot_meta.json
│   ├── features\                 # Feature data
│   │   └── dhan_index_options_features.csv
│   ├── history\                  # Historical data
│   │   └── *.json
│   ├── instruments\              # Instrument data
│   │   └── OpenAPIScripMaster.json
│   └── logs_ultra\               # Ultra logs
│       └── *.log
```

---

## Documentation Structure

```
C:\Genesis_System3\
├── docs\
│   ├── system3_phases_*.md       # Phase documentation
│   ├── system3_ultra_*.md        # Ultra documentation
│   ├── system3_validation_*.md   # Validation reports
│   ├── system3_operational_*.md  # Operational guides
│   └── ... (108+ files)
```

---

## Scripts Structure

```
C:\Genesis_System3\
├── run_system3.py                # Baseline entry point
├── system3_ultra.py              # Ultra control panel
├── system3_ultra_validation.py   # Validation engine
├── system3_ultra_daily_runner.py # Daily automation
├── system3_ultra_weekly_runner.py # Weekly automation
├── system3_ultra_runtime_loops.py # Runtime loops
├── test_phases_*.py              # Phase test scripts
├── system3_ultra_daily_all.bat   # Daily batch script
├── system3_ultra_daily_all.ps1   # Daily PowerShell script
├── system3_ultra_master_monitor.bat # Master monitor
└── system3_verification_checklist.bat # Verification
```

---

## Logs Structure

```
C:\Genesis_System3\
├── logs\
│   ├── YYYY-MM-DD.log            # Daily logs
│   ├── YYYY-MM-DD\               # Daily subdirectories
│   │   └── app.log
│   └── ULTRA_PANEL_SPLIT_*\      # Ultra panel test logs
│       ├── opt_*.log
│       └── opt_*.txt
```

---

## Key Files Summary

### Entry Points
- `run_system3.py` - Baseline system
- `system3_ultra.py` - Ultra control panel

### Configuration
- `core/engine/dhan_trade_config.py` - Trade thresholds
- `core/engine/dhan_automation_config.py` - Automation settings
- `core/config/system3_ultra_safety.json` - Safety switches
- `storage/config/*.json` - Various configs

### Models
- `core/models/dhan/*.pkl` - Baseline models
- `core/models/dhan_real_blended/*.pkl` - Blended models
- `core/models/dhan_ultra/*.pkl` - Ultra models

### Data
- `storage/live/*.csv` - Live trading data
- `storage/learning/*.csv` - Learning data
- `storage/ultra/*` - Ultra outputs
- `storage/training/*.csv` - Training data

---

**Note**: This tree shows only key directories and files. Excludes `__pycache__`, large log files, and venv contents.

