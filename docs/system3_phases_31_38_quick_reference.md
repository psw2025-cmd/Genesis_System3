# System3 Ultra Phases 31-38: Quick Reference Guide

**Last Updated**: 2025-11-29

---

## Menu Options

| Option | Phase | Description | When to Run |
|--------|-------|-------------|-------------|
| 94 | 31 | Ultra Decision Fusion | After market close, or when new signals available |
| 95 | 32 | Ultra vs Baseline Comparator | After Phase 31, to compare performance |
| 96 | 33 | Ultra Promotion Planner | After Phase 32, to check eligibility |
| 97 | 34 | Ultra Live Shadow Comparison | During market hours, to log shadow trades |
| 98 | 35 | Ultra Decision Auditor | Daily, to check safety compliance |
| 99 | 36 | Ultra Continuous Learning Cycle | Weekly, to run full learning cycle |
| 100 | 37 | Ultra Policy & Risk Monitor | Daily, for system health check |
| 101 | 38 | Ultra Governance Summary | Daily, for board-level overview |

---

## Daily Workflow

### Morning (Pre-Market)
```powershell
# Quick health check
python -m core.engine.system3_phase37_policy_risk_monitor
python -m core.engine.system3_phase38_governance_summary
```

### During Market
```powershell
# Monitor live signals (Menu 11)
# Check shadow trades periodically
type storage\live\angel_index_ai_ultra_trades_shadow.csv
```

### After Market Close
```powershell
# Full daily cycle
python -m core.engine.system3_phase31_ultra_fusion
python -m core.engine.system3_phase32_ultra_vs_baseline
python -m core.engine.system3_phase35_ultra_auditor
python -m core.engine.system3_phase38_governance_summary
```

---

## Key Files to Monitor

### Input Files
- `storage/live/angel_index_ai_signals.csv` - Live signals
- `storage/live/angel_index_ai_trades_plan.csv` - Baseline trades
- `storage/live/angel_index_ai_pnl_log.csv` - Baseline PnL

### Output Files
- `storage/ultra/phase31_ultra_fused_decisions.csv` - Fused decisions
- `storage/ultra/phase33_promotion_plan.json` - Promotion plan
- `storage/live/angel_index_ai_ultra_trades_shadow.csv` - Shadow trades
- `storage/ultra/phase35_decision_audit_report.md` - Audit results
- `storage/ultra/phase38_governance_summary.md` - Governance summary

---

## Quick Commands

### Check Latest Decisions
```powershell
python -m core.engine.system3_phase31_ultra_fusion
type storage\ultra\phase31_ultra_fused_decisions.csv | Select-Object -First 10
```

### Check Shadow Trades
```powershell
type storage\live\angel_index_ai_ultra_trades_shadow.csv
```

### Check Promotion Status
```powershell
python -m core.engine.system3_phase33_promotion_planner
type storage\ultra\phase33_promotion_plan.md
```

### Check System Health
```powershell
python -m core.engine.system3_phase37_policy_risk_monitor
python -m core.engine.system3_phase38_governance_summary
```

### Run Monitoring Script
**Recommended**: Use batch file (double-click or run from CMD):
```cmd
monitor_ultra_system.bat
```

**Alternative**: Run PowerShell script:
```powershell
powershell -ExecutionPolicy Bypass -File .\monitor_ultra_system.ps1
```

**Note**: If Windows asks "How do you want to open this file?" when double-clicking `.ps1`, use the `.bat` file instead.

### Run Full Test Suite
```powershell
python test_phases_31_38.py
```

---

## Current Status

- **All Phases**: ✅ Operational
- **Shadow Trades**: 0 (expected with conservative signals)
- **Promotion Eligibility**: FINNIFTY (1/5) - Awaiting manual review
- **Audit Status**: All OK (930/930)
- **System Mode**: Read-Only (Safe)

---

## Safety Reminders

- ✅ No automatic promotion
- ✅ No automatic config changes
- ✅ No automatic trade execution
- ✅ All changes require manual approval
- ✅ All writes to `storage/ultra/` (isolated)

---

## Support

For issues or questions:
1. Check `docs/system3_phases_31_38_operational_guide.md`
2. Review `docs/system3_phases_31_38_test_results.md`
3. Check error logs in `storage/ultra/phaseXX_error_*.md`

