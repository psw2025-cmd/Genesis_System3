# System3 Verification Checklist - Manual Guide

**Date**: 2025-11-29  
**Purpose**: Step-by-step manual verification for all phases

---

## Quick Start

**Automated Script**:
```bash
system3_verification_checklist.bat
```

**OR run manually** (commands below):

---

## Verification Checklist

### ✅ VERIFICATION 1: Core Status + Menu

**Commands**:
```bash
python check_system3_status.py
python run_system3.py
```

**Expected**:
- ✅ 40+ menu items listed
- ✅ No errors
- ✅ Safe mode flags: `auto_execute_trades: False`
- ✅ Ultra-Mode: Read-Only ACTIVE

**Confirm**:
- [ ] Status check shows 107 menu options
- [ ] Auto-execution is DISABLED
- [ ] All directories exist
- [ ] All models present (5 models)

---

### ✅ VERIFICATION 2: Models + Training Health

**Commands**:
```bash
python -m core.engine.train_dhan_models
python -m core.engine.offline_dhan_ai_test
```

**Expected**:
- ✅ 5 models train or load successfully
- ✅ Accuracies ~98–100%
- ✅ Offline test prints sample predictions

**Confirm**:
- [ ] All 5 models trained/loaded
- [ ] NIFTY accuracy: ~1.0000
- [ ] BANKNIFTY accuracy: ~0.98
- [ ] FINNIFTY accuracy: ~0.99
- [ ] MIDCPNIFTY accuracy: ~0.98
- [ ] SENSEX accuracy: ~0.99
- [ ] Sample predictions generated for all underlyings

---

### ✅ VERIFICATION 3: Live Pipeline (DRY-RUN)

**Commands**:
```bash
# Check module exists
python -c "from core.engine.dhan_live_ai_signals import main; print('OK')"

# Check automation config
python -c "from core.engine.dhan_automation_config import AUTOMATION_CONFIG; print('Auto-execute:', AUTOMATION_CONFIG.auto_execute_trades)"
```

**Expected**:
- ✅ Module exists and imports
- ✅ `auto_execute_trades: False`

**Note**: Full live loop (menu 11) runs indefinitely, so we only verify the module exists.

**Confirm**:
- [ ] Live signals module exists
- [ ] Auto-execution is DISABLED
- [ ] Module can be imported

---

### ✅ VERIFICATION 4: Backtester + PnL

**Commands**:
```bash
python -m core.engine.dhan_synthetic_backtester
python -m core.engine.dhan_daily_pnl_summary
```

**Expected**:
- ✅ Backtester prints signal statistics
- ✅ Distribution shown (BUY_CE, BUY_PE, HOLD)
- ✅ PnL summary runs (even if 0 trades)

**Confirm**:
- [ ] Backtester generates signals
- [ ] Signal distribution printed
- [ ] PnL summary executes
- [ ] No crashes

---

### ✅ VERIFICATION 5: Monitoring + Governance

**Commands**:
```bash
python -m core.engine.system3_phase35_ultra_auditor
python -m core.engine.system3_phase37_policy_risk_monitor
python -m core.engine.system3_phase38_governance_summary
```

**Expected**:
- ✅ Decision auditor: OK/WARN/BLOCK counts
- ✅ Policy dashboard: `storage/ultra/phase37_policy_risk_dashboard.md`
- ✅ Governance summary: `storage/ultra/phase38_governance_summary.md`

**Confirm**:
- [ ] Decision Auditor: Reports OK/WARN/BLOCK counts
- [ ] Policy dashboard file created
- [ ] Governance summary file created
- [ ] All reports readable

---

### ✅ VERIFICATION 6: Ultra Phases 39-45

**Commands**:
```bash
python verify_phases_39_45.py
```

**Expected**:
- ✅ All 8 checks pass
- ✅ No baseline files modified
- ✅ All safety guarantees confirmed

**Confirm**:
- [ ] Phase 39: PASS
- [ ] Phase 40: PASS
- [ ] Phase 41: PASS
- [ ] Phase 42: PASS
- [ ] Phase 43: PASS
- [ ] Phase 44: PASS
- [ ] Phase 45: PASS
- [ ] Safety Guarantees: PASS

---

## Additional Phase-Specific Verifications

### Phases 39-45 Individual Tests

```bash
# Phase 39: Shadow Campaign
python -m core.engine.system3_phase39_shadow_campaign

# Phase 40: Weekly Governance Pack
python -m core.engine.system3_phase40_weekly_governance_pack

# Phase 41: Promotion Executor (will fail without prerequisites - expected)
python -m core.engine.system3_phase41_promotion_executor

# Phase 42: Snapshot Manager
python -m core.engine.system3_phase42_snapshot_manager create
python -m core.engine.system3_phase42_snapshot_manager list

# Phase 43: Environment Guard
python -m core.engine.system3_phase43_env_guard
```

---

## Expected Output Files

After running all verifications, check for:

### Core Files
- ✅ `storage/live/dhan_index_ai_signals.csv`
- ✅ `storage/live/dhan_index_ai_trades_plan.csv`
- ✅ `storage/live/dhan_index_ai_pnl_log.csv`

### Ultra Files
- ✅ `storage/ultra/phase35_decision_audit.csv`
- ✅ `storage/ultra/phase35_decision_audit_report.md`
- ✅ `storage/ultra/phase37_policy_risk_dashboard.md`
- ✅ `storage/ultra/phase38_governance_summary.md`
- ✅ `storage/ultra/phase39_shadow_campaign_summary_*.md` (if Phase 39 run)
- ✅ `storage/ultra/weekly_packs/YYYYWW/weekly_governance_pack.md` (if Phase 40 run)
- ✅ `storage/snapshots/YYYYMMDD_HHMMSS/` (if Phase 42 run)
- ✅ `storage/ultra/phase43_env_guard_report.md` (if Phase 43 run)

### Config Files
- ✅ `storage/config/ultra_shadow_campaign_config.json`
- ✅ `storage/config/system3_env_config.json`

---

## Verification Summary Template

After running all verifications, document:

```
Date: YYYY-MM-DD
Verification Run: [Automated/Manual]

Results:
[ ] Verification 1: Core Status - PASS/FAIL
[ ] Verification 2: Models & Training - PASS/FAIL
[ ] Verification 3: Live Pipeline - PASS/FAIL
[ ] Verification 4: Backtester & PnL - PASS/FAIL
[ ] Verification 5: Monitoring & Governance - PASS/FAIL
[ ] Verification 6: Ultra Phases 39-45 - PASS/FAIL

Issues Found:
- [List any issues]

Status: READY / NOT READY
```

---

## Quick Reference

**One-Click Validation**:
```bash
system3_full_validation.bat
```

**Full Verification Checklist**:
```bash
system3_verification_checklist.bat
```

**Individual Phase Verification**:
```bash
python verify_phases_39_45.py
```

---

**Last Updated**: 2025-11-29  
**Status**: Ready for use

