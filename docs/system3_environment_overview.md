# System3 Environment Overview

**Date**: 2025-11-30  
**Project**: System3 Ultra - Angel One Index Options Trading System

---

## Project Root Path

```
C:\Genesis_System3
```

---

## Virtual Environment Path

```
C:\Genesis_System3\venv
```

**Activation**:
- Windows: `venv\Scripts\activate.bat`
- PowerShell: `venv\Scripts\Activate.ps1`

---

## Main Entry Scripts

### Primary Entry Points

1. **`run_system3.py`**
   - Baseline System3 entry point
   - Path: `C:\Genesis_System3\run_system3.py`

2. **`system3_ultra.py`**
   - System3 Ultra Control Panel
   - Master entry point for all operations (baseline + ultra)
   - Path: `C:\Genesis_System3\system3_ultra.py`
   - Provides unified menu interface with 100+ options

### Supporting Scripts

- `system3_ultra_daily_runner.py` - Daily automation runner
- `system3_ultra_weekly_runner.py` - Weekly automation runner
- `system3_ultra_runtime_loops.py` - Runtime loop handlers
- `system3_ultra_validation.py` - Validation engine
- `test_phases_46_55.py` - Phase 46-55 test script
- `test_phases_39_45.py` - Phase 39-45 test script
- `test_phases_31_38.py` - Phase 31-38 test script

---

## Core Engine Module Root

```
C:\Genesis_System3\core\engine\
```

**Contains**: 130+ Python modules for:
- Baseline trading operations
- Ultra phase implementations (31-43)
- Feature engineering
- Model training
- Signal generation
- Trade execution
- PnL simulation
- Risk management

---

## Core Ultra Module Root

```
C:\Genesis_System3\core\ultra\
```

**Contains**: Ultra phase implementations (21-30, 46-55)
- Adaptive risk engines
- Position sizing
- Volatility impact
- Confidence drift
- Stoploss/target engines
- Meta fusion
- Probability engines
- Monitoring agents

---

## Key Config Files

### Trade Configuration

**`core\engine\angel_trade_config.py`**
- Trade thresholds (min_confidence, min_abs_score)
- Position sizing parameters
- Target/stop-loss percentages
- Max trades per day/underlying

### Automation Configuration

**`core\engine\angel_automation_config.py`**
- Auto-execute trades (default: False)
- Auto-simulate PnL (default: False)
- Auto-update thresholds (default: False)
- Auto-retrain models (default: False)

### Ultra Safety Configuration

**`core\config\system3_ultra_safety.json`**
- Ultra safety switches
- Auto-execute controls
- Auto-update controls
- Auto-promotion controls

### Active Profile Configuration

**`core\config\system3_active_profile.json`**
- Current active profile (BASELINE/ULTRA_DEV)
- Profile-specific settings

### Storage Config Files

**`storage\config\`** directory contains:
- `angel_blended_training_v3_config.json` - Blended training config
- `risk_profile_suggestions.json` - Risk profile suggestions
- `strategy_optimization.json` - Strategy optimization settings
- `system3_env_config.json` - Environment configuration
- `system3_live_beta_profile.json` - Live beta profile
- `thresholds_auto.json` - Auto-tuned thresholds
- `thresholds_real_suggestions.json` - Real-data threshold suggestions
- `thresholds_recommended.json` - Recommended thresholds
- `ultra_shadow_campaign_config.json` - Shadow campaign config

---

## Model Directories

### Baseline Models

```
C:\Genesis_System3\core\models\angel_one\
```
- Contains: 10 files (5 .pkl models + 5 .json metadata)
- Underlyings: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX

### Blended Models

```
C:\Genesis_System3\core\models\angel_one_real_blended\
```
- Contains: 10 files (5 .pkl models + 5 .json metadata)
- Real + synthetic blended models

### Ultra Models

```
C:\Genesis_System3\core\models\angel_one_ultra\
```
- Contains: 10 files (5 .pkl models + 5 .json metadata)
- Ultra-mode models

---

## Storage Directories

### Training Data

```
C:\Genesis_System3\storage\training\
```
- Training datasets (CSV, Parquet)

### Live Data

```
C:\Genesis_System3\storage\live\
```
- Live signals: `angel_index_ai_signals.csv`
- Trade plans: `angel_index_ai_trades_plan.csv`
- PnL logs: `angel_index_ai_pnl_log.csv`
- Execution logs: `angel_index_ai_trades_exec_log.csv`

### Learning Data

```
C:\Genesis_System3\storage\learning\
```
- Real outcomes: `angel_real_outcomes.csv`
- Real signals: `real_signals_raw.csv`
- Master dataset: `angel_index_real_master_dataset.csv`

### Ultra Data

```
C:\Genesis_System3\storage\ultra\
```
- Ultra phase outputs (CSV, JSON, MD)
- Phase-specific directories (e.g., `ph46_ph55/`)

### Reports

```
C:\Genesis_System3\storage\reports\
```
- Daily reports
- Learning summaries
- Feature drift analysis
- Threshold recommendations

---

## Log Directories

### Application Logs

```
C:\Genesis_System3\logs\
```
- Daily logs: `YYYY-MM-DD.log`
- Daily subdirectories: `YYYY-MM-DD/`
- Ultra panel test logs: `ULTRA_PANEL_SPLIT_*/`

### Ultra Logs

```
C:\Genesis_System3\storage\logs_ultra\
```
- Ultra-specific logs
- Phase execution logs

---

## Documentation Directory

```
C:\Genesis_System3\docs\
```
- Contains: 108+ markdown documentation files
- Phase documentation
- Validation reports
- Operational guides
- Architecture documentation

---

## Quick Reference

### Activate Environment
```bash
cd C:\Genesis_System3
venv\Scripts\activate.bat
```

### Run System3 Ultra
```bash
python system3_ultra.py
```

### Run Baseline System3
```bash
python run_system3.py
```

### Run Validation
```bash
python system3_ultra_validation.py
```

---

**Last Updated**: 2025-11-30

