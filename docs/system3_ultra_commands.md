# System3 Ultra Control Panel - Commands Reference

**Date**: 2025-11-29  
**Version**: 1.0  
**Status**: Complete

---

## Quick Start

```bash
# Activate virtual environment
venv\Scripts\activate

# Launch System3 Ultra Control Panel
python system3_ultra.py
```

---

## Common Commands

### Pre-Market
```bash
# Pre-market diagnostic
python system3_ultra.py
# Select: OP1

# Or directly:
python -m core.engine.angel_market_warmup_scanner
```

### Live Trading Session
```bash
# Start live signal generation
python system3_ultra.py
# Select: OP2 or 11

# Or directly:
python -m core.engine.angel_live_ai_signals
```

### Post-Market
```bash
# Post-market analysis
python system3_ultra.py
# Select: OP4

# Or directly:
python -m core.engine.angel_daily_learning_digest
```

### Weekly Review
```bash
# Weekly governance review
python system3_ultra.py
# Select: OP5 or 103

# Or directly:
python -m core.engine.system3_phase40_weekly_governance_pack
```

---

## Direct Module Execution

### Baseline Core
```bash
# Train models
python -m core.engine.train_angel_models

# Synthetic backtest
python -m core.engine.angel_synthetic_backtester

# Daily PnL summary
python -m core.engine.angel_daily_pnl_summary
```

### Ultra Shadow
```bash
# Shadow data engine
python -m core.engine.ultra_shadow_data_engine

# Ultra feature engineering
python -m core.engine.ultra_feature_engineering

# Train Ultra models
python -m core.engine.ultra_train_models
```

### Ultra Phases 21-30
```bash
# Phase 21: Adaptive Risk Engine
python -m core.ultra.phase21_adaptive_risk_engine

# Phase 30: Calibration Engine
python -m core.ultra.phase30_calibration_engine
```

### Ultra Phases 31-38
```bash
# Phase 31: Decision Fusion
python -c "from core.engine.system3_phase31_ultra_fusion import run_phase31_fusion; run_phase31_fusion()"

# Phase 35: Decision Auditor
python -c "from core.engine.system3_phase35_ultra_auditor import run_phase35_audit; run_phase35_audit()"

# Phase 37: Policy Monitor
python -c "from core.engine.system3_phase37_policy_risk_monitor import run_phase37_policy_risk_dashboard; run_phase37_policy_risk_dashboard()"
```

### Ultra Phases 39-45
```bash
# Phase 39: Shadow Campaign
python -c "from core.engine.system3_phase39_shadow_campaign import run_phase39_shadow_campaign; run_phase39_shadow_campaign()"

# Phase 42: Snapshot Manager
python -c "from core.engine.system3_phase42_snapshot_manager import run_phase42_snapshot_create; run_phase42_snapshot_create()"

# Phase 43: Environment Guard
python -c "from core.engine.system3_phase43_env_guard import run_phase43_env_guard; run_phase43_env_guard()"
```

---

## Runtime Scripts

### Daily Runner
```bash
python system3_ultra_daily_runner.py
```

### Weekly Runner
```bash
python system3_ultra_weekly_runner.py
```

### Runtime Loops
```bash
python system3_ultra_runtime_loops.py
```

---

## Validation

### Full Validation
```bash
python system3_ultra_validation.py
```

### Safety Check
```bash
python system3_ultra.py
# Select: S

# Or directly:
python -m core.engine.ultra_safety
```

---

## Logs

### View Latest Logs
```bash
python system3_ultra.py
# Select: L
```

### View Log File Directly
```bash
type storage\logs_ultra\system3_ultra_YYYYMMDD.log
```

---

## Help

### Documentation
```bash
python system3_ultra.py
# Select: H
```

### Documentation Files
- `docs/system3_ultra_menu_structure.md`
- `docs/system3_ultra_safety_matrix.md`
- `docs/system3_ultra_commands.md` (this file)
- `docs/system3_ultra_launch_flow.md`

---

**Last Updated**: 2025-11-29  
**Status**: Complete

