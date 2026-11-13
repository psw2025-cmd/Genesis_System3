# System3 Ultra: Promotion Eligibility Review Guide

**Date**: 2025-11-29  
**Current Status**: FINNIFTY eligible (1/5 underlyings)

---

## Current Promotion Status

### Eligible Underlying

**FINNIFTY**: ✅ **ELIGIBLE**

**Eligibility Criteria**:
- ✅ Ultra win rate: 10.0% (vs 0.0% baseline) - **+10.0% improvement**
- ✅ Ultra avg PnL: 2.00% (vs 0.00% baseline) - **+2.00% improvement**
- ✅ Ultra drawdown: <= baseline - **Risk controlled**

**Recommended Changes**:
1. Consider slightly tighter SL (reduce by 0.01)
2. Consider slightly higher TP (increase by 0.02)
3. Monitor for 7 days before full promotion

### Not Eligible Underlyings

- **NIFTY**: No comparison data available
- **BANKNIFTY**: No comparison data available
- **MIDCPNIFTY**: No comparison data available
- **SENSEX**: No comparison data available

---

## Review Process

### Step 1: Review Promotion Plan

```powershell
type storage\ultra\phase33_promotion_plan.md
```

**What to Check**:
- Eligibility status per underlying
- Reasoning for eligibility/not eligible
- Recommended changes (if eligible)

### Step 2: Verify Comparison Metrics

```powershell
type storage\ultra\phase32_ultra_vs_baseline_summary.md
```

**What to Check**:
- Baseline vs Ultra metrics
- Win rate comparison
- Avg PnL comparison
- Drawdown comparison

### Step 3: Review Audit Results

```powershell
type storage\ultra\phase35_decision_audit_report.md
```

**What to Check**:
- OK/WARN/BLOCK counts
- Any violations or issues
- Safety compliance

### Step 4: Review Governance Summary

```powershell
type storage\ultra\phase38_governance_summary.md
```

**What to Check**:
- Final recommendation
- Promotion readiness status
- Open issues
- GO/NO-GO guidance

---

## Promotion Decision Framework

### Approval Criteria

**Before approving promotion, verify**:

1. ✅ **Performance Metrics**:
   - Ultra win rate >= baseline + 5%
   - Ultra avg PnL >= baseline
   - Ultra drawdown <= baseline

2. ✅ **Data Sufficiency**:
   - Minimum 10 baseline trades for comparison
   - Minimum 7 days of data
   - Sufficient sample size

3. ✅ **Safety Compliance**:
   - All decisions OK (no WARN/BLOCK)
   - No safety violations
   - Risk flags appropriate

4. ✅ **Stability**:
   - Consistent performance over time
   - No sudden changes
   - Stable metrics

### Manual Approval Process

**⚠️ IMPORTANT**: All promotions require **explicit manual approval**. No automatic promotion occurs.

**Approval Steps**:

1. **Review All Data**:
   - Phase 33 promotion plan
   - Phase 32 comparison metrics
   - Phase 35 audit results
   - Phase 38 governance summary

2. **Verify Eligibility**:
   - Check all criteria met
   - Verify data quality
   - Confirm safety compliance

3. **Make Decision**:
   - **APPROVE**: If all criteria met and comfortable
   - **REJECT**: If any concerns or insufficient data
   - **DEFER**: If need more data or monitoring

4. **If APPROVE**:
   - Manually apply recommended changes
   - Update thresholds/configs manually
   - Monitor closely for 7 days
   - Review results after monitoring period

5. **Document Decision**:
   - Record approval/rejection
   - Note reasoning
   - Track outcomes

---

## FINNIFTY Promotion Review

### Current Status

**Underlying**: FINNIFTY  
**Status**: ✅ ELIGIBLE  
**Eligibility Date**: 2025-11-29

### Metrics Summary

| Metric | Baseline | Ultra | Delta | Status |
|--------|----------|-------|-------|--------|
| Win Rate | 0.0% | 10.0% | +10.0% | ✅ |
| Avg PnL | 0.00% | 2.00% | +2.00% | ✅ |
| Drawdown | 0.00% | <= baseline | Controlled | ✅ |

### Recommended Changes

1. **Stoploss Adjustment**:
   - Current: (from config)
   - Recommended: Reduce by 0.01
   - Action: Manual update required

2. **Target Adjustment**:
   - Current: (from config)
   - Recommended: Increase by 0.02
   - Action: Manual update required

3. **Monitoring Period**:
   - Duration: 7 days
   - Action: Monitor daily after promotion

### Review Checklist

- [ ] Review Phase 33 promotion plan details
- [ ] Verify Phase 32 comparison metrics
- [ ] Check Phase 35 audit results (all OK)
- [ ] Review Phase 38 governance summary
- [ ] Verify data sufficiency (3 baseline trades - may need more)
- [ ] Check safety compliance
- [ ] Review recommended changes
- [ ] Make approval decision
- [ ] Document decision

### Decision Options

**Option 1: APPROVE NOW**
- If comfortable with current metrics
- Apply recommended changes manually
- Monitor for 7 days

**Option 2: DEFER (Recommended)**
- Wait for more baseline trades (currently only 3)
- Collect more data (7+ days)
- Re-evaluate after sufficient data

**Option 3: REJECT**
- If not comfortable with metrics
- If data insufficient
- If safety concerns exist

---

## Promotion Implementation (If Approved)

### Step 1: Backup Current Config

```powershell
# Backup current thresholds
copy storage\config\thresholds_auto.json storage\config\thresholds_auto_backup_YYYYMMDD.json
```

### Step 2: Apply Recommended Changes

**Manual Steps**:
1. Open `storage/config/thresholds_auto.json`
2. Apply recommended SL/TP adjustments
3. Save changes
4. Document changes

### Step 3: Enable Monitoring

1. Run Phase 37 daily (Policy Monitor)
2. Run Phase 35 daily (Decision Auditor)
3. Run Phase 38 daily (Governance Summary)
4. Track shadow trades
5. Monitor performance metrics

### Step 4: Review After 7 Days

1. Compare performance vs baseline
2. Review audit results
3. Check for any issues
4. Make continuation decision

---

## Safety Reminders

⚠️ **CRITICAL SAFETY RULES**:

1. **No Automatic Promotion**: All promotions require manual approval
2. **No Config Auto-Update**: All config changes must be manual
3. **No Auto-Execution**: Shadow trades never executed automatically
4. **Always Backup**: Backup configs before any changes
5. **Monitor Closely**: Watch for 7 days after any changes
6. **Document Everything**: Record all decisions and outcomes

---

## Status: ⏸️ **AWAITING MANUAL REVIEW**

FINNIFTY is eligible but requires:
- Manual review of all metrics
- Manual approval decision
- Manual application of changes (if approved)
- 7-day monitoring period

**Next Action**: Review promotion plan and make manual decision.

