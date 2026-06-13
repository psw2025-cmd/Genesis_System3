# System3 Ultra Phases 31-38: Operational Guide

**Date**: 2025-11-29  
**Status**: ✅ **Production Ready (Read-Only Mode)**

---

## Quick Start Guide

### Daily Operations Checklist

**Morning (Pre-Market)**:
1. ✅ Run Phase 37: Policy & Risk Monitor (Menu: 100)
   - Review safety settings
   - Check shadow trade activity
   - Verify audit results

2. ✅ Run Phase 38: Governance Summary (Menu: 101)
   - Review overall system status
   - Check promotion readiness
   - Review open issues

**During Market Hours**:
1. ✅ Monitor live signals (Menu: 11)
   - Watch for BUY signals with high confidence
   - Check if shadow trades are being generated

2. ✅ Run Phase 34: Live Shadow Comparison (Menu: 97)
   - Check if Ultra shadow trades are being logged
   - Verify shadow trades match expected criteria

**After Market Close**:
1. ✅ Run Phase 31: Ultra Decision Fusion (Menu: 94)
   - Generate latest fused decisions
   - Review final_action distribution

2. ✅ Run Phase 32: Ultra vs Baseline Comparator (Menu: 95)
   - Compare Ultra vs baseline performance
   - Review metrics and differences

3. ✅ Run Phase 35: Ultra Decision Auditor (Menu: 98)
   - Check for any WARN or BLOCK decisions
   - Review audit report for issues

4. ✅ Run Phase 36: CULL Orchestrator (Menu: 99)
   - Execute full learning cycle
   - Review execution log

5. ✅ Run Phase 38: Governance Summary (Menu: 101)
   - Review final recommendation
   - Check promotion readiness

---

## Monitoring Real Signals

### What to Watch For

1. **BUY Signals with SAFE Risk**:
   - When `final_action` = BUY_CE, STRONG_BUY_CE, BUY_PE, or STRONG_BUY_PE
   - AND `final_risk_flag` = SAFE
   - These will create shadow trades in Phase 34

2. **Shadow Trade Activity**:
   - Check `storage/live/dhan_index_ai_ultra_trades_shadow.csv`
   - Monitor growth of shadow trades
   - Compare with baseline trades

3. **Decision Distribution**:
   - Run Phase 31 to see distribution of final_action
   - Monitor shift from HOLD to BUY signals
   - Track risk flag distribution

### Monitoring Commands

```powershell
# Check latest fused decisions
python -m core.engine.system3_phase31_ultra_fusion
type storage\ultra\phase31_ultra_fused_decisions.csv | Select-Object -First 20

# Check shadow trades
type storage\live\dhan_index_ai_ultra_trades_shadow.csv

# Check audit results
python -m core.engine.system3_phase35_ultra_auditor
type storage\ultra\phase35_decision_audit_report.md
```

---

## Reviewing Promotion Eligibility

### Current Status

**FINNIFTY**: ✅ **ELIGIBLE** (1/5 underlyings)

**Eligibility Criteria Met**:
- Ultra win rate: 10.0% (vs 0.0% baseline) ✅
- Ultra avg PnL: 2.00% (vs 0.00% baseline) ✅
- Ultra drawdown: <= baseline ✅

**Recommended Changes**:
1. Consider slightly tighter SL (reduce by 0.01)
2. Consider slightly higher TP (increase by 0.02)
3. Monitor for 7 days before full promotion

### Review Process

1. **Check Promotion Plan**:
   ```powershell
   type storage\ultra\phase33_promotion_plan.md
   ```

2. **Review Governance Summary**:
   ```powershell
   type storage\ultra\phase38_governance_summary.md
   ```

3. **Verify Comparison Data**:
   ```powershell
   type storage\ultra\phase32_ultra_vs_baseline_summary.md
   ```

4. **Manual Approval Required**:
   - Review all metrics
   - Verify Ultra performance
   - Wait 7-day monitoring period
   - Explicit manual approval before any changes

### Promotion Decision Workflow

```
1. Review Phase 33 promotion plan
   ↓
2. Verify Phase 32 comparison metrics
   ↓
3. Check Phase 35 audit results
   ↓
4. Review Phase 38 governance summary
   ↓
5. Manual decision: APPROVE or REJECT
   ↓
6. If APPROVE: Manually apply recommended changes
   ↓
7. Monitor for 7 days
   ↓
8. Evaluate results
```

**⚠️ IMPORTANT**: No automatic promotion occurs. All changes require manual approval.

---

## System Monitoring

### Health Checks

**Daily Health Check**:
```powershell
# 1. Check system status
python -m core.engine.system3_phase37_policy_risk_monitor

# 2. Check governance summary
python -m core.engine.system3_phase38_governance_summary

# 3. Verify all output files exist
dir storage\ultra\phase*.csv
dir storage\ultra\phase*.md
dir storage\ultra\phase*.json
```

### Key Metrics to Monitor

1. **Decision Distribution** (Phase 31):
   - Track HOLD vs BUY ratio
   - Monitor risk flag distribution
   - Watch for increase in BUY signals

2. **Shadow Trade Activity** (Phase 34):
   - Count of shadow trades per day
   - Compare with baseline trades
   - Monitor shadow trade quality

3. **Audit Results** (Phase 35):
   - OK/WARN/BLOCK counts
   - Watch for increase in WARN/BLOCK
   - Review violation patterns

4. **Promotion Eligibility** (Phase 33):
   - Track eligible underlyings
   - Monitor eligibility changes
   - Review recommended changes

5. **Governance Status** (Phase 38):
   - Final recommendation status
   - Open issues count
   - Promotion readiness

---

## Troubleshooting

### No Shadow Trades Generated

**Symptom**: `dhan_index_ai_ultra_trades_shadow.csv` is empty

**Possible Causes**:
1. No BUY signals generated (all HOLD)
2. BUY signals have RISKY/BLOCKED risk flags
3. Confidence thresholds too high

**Actions**:
1. Check Phase 31 fused decisions distribution
2. Review risk flag distribution
3. Check signal confidence levels
4. Verify fusion logic thresholds

### All Decisions HOLD

**Symptom**: Phase 31 shows 100% HOLD

**Possible Causes**:
1. Conservative thresholds (confidence >= 0.70)
2. Low signal confidence
3. Risk flags blocking trades

**Actions**:
1. Review signal confidence distribution
2. Check risk flag distribution
3. Consider adjusting fusion thresholds (if needed)
4. Monitor for signal quality improvement

### Promotion Eligibility Issues

**Symptom**: No underlyings eligible or unexpected eligibility

**Actions**:
1. Review Phase 32 comparison metrics
2. Verify baseline PnL data
3. Check eligibility criteria
4. Review Phase 33 promotion plan reasoning

### Audit Warnings/Blocks

**Symptom**: Phase 35 shows WARN or BLOCK decisions

**Actions**:
1. Review audit report for details
2. Check which safety limits were violated
3. Review decision details
4. Adjust thresholds if needed (manual only)

---

## File Locations Reference

### Input Files
- Live Signals: `storage/live/dhan_index_ai_signals.csv`
- Baseline Trades: `storage/live/dhan_index_ai_trades_plan.csv`
- Baseline PnL: `storage/live/dhan_index_ai_pnl_log.csv`
- Ultra Artifacts: `storage/reports_ultra/phase21_*.csv`, `phase24_*.json`, etc.

### Output Files
- Phase 31: `storage/ultra/phase31_ultra_fused_decisions.csv`
- Phase 32: `storage/ultra/phase32_ultra_vs_baseline_summary.md`
- Phase 33: `storage/ultra/phase33_promotion_plan.json` + `.md`
- Phase 34: `storage/live/dhan_index_ai_ultra_trades_shadow.csv`
- Phase 35: `storage/ultra/phase35_decision_audit_report.md`
- Phase 36: `storage/ultra/phase36_cull_execution_log.md`
- Phase 37: `storage/ultra/phase37_policy_risk_dashboard.md`
- Phase 38: `storage/ultra/phase38_governance_summary.md`

---

## Best Practices

### 1. Regular Monitoring
- Run Phase 37 (Policy Monitor) daily
- Run Phase 38 (Governance Summary) daily
- Review Phase 35 (Auditor) after market close

### 2. Signal Quality
- Monitor Phase 31 distribution regularly
- Watch for shift from HOLD to BUY
- Track confidence and score trends

### 3. Shadow Trade Analysis
- Compare shadow trades with baseline
- Monitor shadow trade performance (when PnL available)
- Review shadow trade patterns

### 4. Promotion Review
- Review Phase 33 plan weekly
- Verify eligibility criteria
- Wait for sufficient data before promotion

### 5. Safety First
- Always review audit results
- Check for WARN/BLOCK decisions
- Never skip safety checks

---

## Quick Reference: Menu Options

```
94) Ultra Phase 31: Decision Fusion
95) Ultra Phase 32: vs Baseline Comparator
96) Ultra Phase 33: Promotion Planner
97) Ultra Phase 34: Live Shadow Comparison
98) Ultra Phase 35: Decision Auditor
99) Ultra Phase 36: Continuous Learning Cycle (CULL)
100) Ultra Phase 37: Policy & Risk Monitor
101) Ultra Phase 38: Governance Summary
```

---

## Status: ✅ **READY FOR OPERATIONAL USE**

All phases are operational and ready for daily monitoring and use.

