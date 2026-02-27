# System3 Ultra: Daily Operations Checklist

**Date**: 2025-11-29  
**Purpose**: Daily operational checklist for System3 Ultra Phases 31-38

---

## 🌅 Morning Checklist (Pre-Market)

### 1. System Health Check
- [ ] Run Phase 37: Policy & Risk Monitor (Menu: 100)
  ```powershell
  python -m core.engine.system3_phase37_policy_risk_monitor
  ```
- [ ] Review policy dashboard
  ```powershell
  type storage\ultra\phase37_policy_risk_dashboard.md
  ```
- [ ] Verify safety settings are correct

### 2. Governance Review
- [ ] Run Phase 38: Governance Summary (Menu: 101)
  ```powershell
  python -m core.engine.system3_phase38_governance_summary
  ```
- [ ] Review final recommendation
  ```powershell
  type storage\ultra\phase38_governance_summary.md
  ```
- [ ] Check for open issues

### 3. Quick Status
- [ ] Verify all output files exist
- [ ] Check for any error logs
- [ ] Confirm system is ready

**Time Required**: ~2-3 minutes

---

## 📊 During Market Hours

### 1. Monitor Live Signals
- [ ] Check if Menu 11 is running (live AI signals)
- [ ] Monitor signal generation
- [ ] Watch for BUY signals

### 2. Check Shadow Trades
- [ ] Run Phase 34: Live Shadow Comparison (Menu: 97)
  ```powershell
  python -m core.engine.system3_phase34_ultra_shadow_exec
  ```
- [ ] Review shadow trades
  ```powershell
  type storage\live\angel_index_ai_ultra_trades_shadow.csv
  ```
- [ ] Compare with baseline trades

### 3. Monitor Decision Distribution
- [ ] Run Phase 31: Ultra Decision Fusion (Menu: 94)
  ```powershell
  python -m core.engine.system3_phase31_ultra_fusion
  ```
- [ ] Check final_action distribution
- [ ] Monitor shift from HOLD to BUY

**Time Required**: ~5-10 minutes (periodic checks)

---

## 🌆 After Market Close

### 1. Generate Fused Decisions
- [ ] Run Phase 31: Ultra Decision Fusion (Menu: 94)
  ```powershell
  python -m core.engine.system3_phase31_ultra_fusion
  ```
- [ ] Review distribution summary
- [ ] Check for any BUY signals

### 2. Compare Performance
- [ ] Run Phase 32: Ultra vs Baseline Comparator (Menu: 95)
  ```powershell
  python -m core.engine.system3_phase32_ultra_vs_baseline
  ```
- [ ] Review comparison summary
  ```powershell
  type storage\ultra\phase32_ultra_vs_baseline_summary.md
  ```
- [ ] Check metrics and differences

### 3. Audit Decisions
- [ ] Run Phase 35: Ultra Decision Auditor (Menu: 98)
  ```powershell
  python -m core.engine.system3_phase35_ultra_auditor
  ```
- [ ] Review audit report
  ```powershell
  type storage\ultra\phase35_decision_audit_report.md
  ```
- [ ] Check for WARN or BLOCK decisions

### 4. Review Promotion Eligibility
- [ ] Run Phase 33: Ultra Promotion Planner (Menu: 96)
  ```powershell
  python -m core.engine.system3_phase33_promotion_planner
  ```
- [ ] Review promotion plan
  ```powershell
  type storage\ultra\phase33_promotion_plan.md
  ```
- [ ] Check eligibility changes

### 5. Final Governance Review
- [ ] Run Phase 38: Governance Summary (Menu: 101)
  ```powershell
  python -m core.engine.system3_phase38_governance_summary
  ```
- [ ] Review final recommendation
- [ ] Check promotion readiness

**Time Required**: ~10-15 minutes

---

## 📅 Weekly Checklist

### 1. Full Learning Cycle
- [ ] Run Phase 36: CULL Orchestrator (Menu: 99)
  ```powershell
  python -m core.engine.system3_phase36_cull_orchestrator
  ```
- [ ] Review execution log
  ```powershell
  type storage\ultra\phase36_cull_execution_log.md
  ```
- [ ] Check all steps completed

### 2. Comprehensive Review
- [ ] Review all weekly metrics
- [ ] Compare week-over-week performance
- [ ] Evaluate promotion eligibility
- [ ] Review any issues or concerns

**Time Required**: ~20-30 minutes

---

## 🚨 Alert Conditions

### Immediate Attention Required

1. **Audit Warnings/Blocks**:
   - If Phase 35 shows WARN or BLOCK decisions
   - Action: Review audit report immediately
   - Check which safety limits violated

2. **Shadow Trade Spike**:
   - If shadow trades increase suddenly
   - Action: Review shadow trade quality
   - Verify risk flags are appropriate

3. **Promotion Eligibility Change**:
   - If new underlyings become eligible
   - Action: Review promotion plan
   - Follow promotion review process

4. **System Errors**:
   - If any phase fails to run
   - Action: Check error logs
   - Review troubleshooting guide

---

## 📋 Quick Reference

### Menu Options
- 94: Phase 31 - Decision Fusion
- 95: Phase 32 - Baseline Comparator
- 96: Phase 33 - Promotion Planner
- 97: Phase 34 - Shadow Comparison
- 98: Phase 35 - Decision Auditor
- 99: Phase 36 - CULL Orchestrator
- 100: Phase 37 - Policy Monitor
- 101: Phase 38 - Governance Summary

### Key Files
- Fused Decisions: `storage/ultra/phase31_ultra_fused_decisions.csv`
- Shadow Trades: `storage/live/angel_index_ai_ultra_trades_shadow.csv`
- Promotion Plan: `storage/ultra/phase33_promotion_plan.md`
- Audit Report: `storage/ultra/phase35_decision_audit_report.md`
- Governance: `storage/ultra/phase38_governance_summary.md`

### Monitoring Script
**Recommended**: Use batch file (double-click or run from CMD):
```cmd
monitor_ultra_system.bat
```

**Alternative**: Run PowerShell script:
```powershell
powershell -ExecutionPolicy Bypass -File .\monitor_ultra_system.ps1
```

---

## ✅ Daily Completion

At end of day, verify:
- [ ] All morning checks completed
- [ ] All after-market checks completed
- [ ] No errors or warnings
- [ ] All output files generated
- [ ] System status documented

---

**Status**: ✅ **READY FOR DAILY USE**

