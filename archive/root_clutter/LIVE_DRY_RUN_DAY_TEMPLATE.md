# LIVE DRY-RUN DAY REPORT TEMPLATE

**Use this template to capture and document results from a full live DRY-RUN day.**

---

## SESSION INFORMATION

| Field | Value |
|-------|-------|
| **Test Date** | YYYY-MM-DD |
| **Day of Week** | (Monday / Tuesday / ... / Friday) |
| **Start Time (IST)** | HH:MM AM |
| **End Time (IST)** | HH:MM PM |
| **Total Duration** | X hours Y minutes |
| **Tester Name** | (Your name) |
| **System Version** | System3 Phases 1–380 |
| **Mode** | DRY-RUN (Virtual execution only) |
| **Log File** | logs/live_dress_rehearsal/live_dry_run_YYYYMMDD_HHMMSS.log |

---

## PRE-MARKET VERIFICATION (8:45 AM – 9:10 AM)

### Safety Checks

| Check | Status | Notes |
|-------|--------|-------|
| LIVE_TRADING_ENABLED = False | ☐ PASS ☐ FAIL | Expected: False |
| USE_LIVE_EXECUTION_ENGINE = False | ☐ PASS ☐ FAIL | Expected: False |
| auto_execute_trades = False | ☐ PASS ☐ FAIL | Expected: False |
| AngelOne credentials loaded | ☐ PASS ☐ FAIL | Check logs for login |
| Models file exist (trained) | ☐ PASS ☐ FAIL | Count: __ files |
| Data pipeline working | ☐ PASS ☐ FAIL | Can fetch live OHLC |
| Phases 331–380 block test pass | ☐ PASS ☐ FAIL | Expected: 43 OK / 7 WARN / 0 ERROR |

**Pre-Market Status:** ☐ READY ☐ ISSUES FOUND

**Issues Found (if any):**
```
(Describe any issues found in pre-market checks)
```

---

## MAIN TRADING WINDOW (9:10 AM – 3:20 PM)

### Option 11: LIVE AI Signals Loop

| Metric | Value | Notes |
|--------|-------|-------|
| **Loop Start Time (IST)** | HH:MM AM | When did "Option 11" start? |
| **Loop Stop Time (IST)** | HH:MM PM | When did you press Ctrl+C? |
| **Duration** | X hours | Actual time running |
| **Total Snapshots Generated** | __ count | Lines appended to CSV |
| **Total Signals Generated** | __ count | From option 11 output or CSV count |
| **Avg Signals per Hour** | __ count | Total signals / duration |

**CSV File Sizes (at 3:20 PM):**

| File | Row Count | Last Updated | Notes |
|------|-----------|---------------|-------|
| `angel_index_ai_signals.csv` | __ rows | HH:MM | Verify column count = 5 |
| `angel_virtual_orders.csv` | __ rows | HH:MM | Verify column count = 15 |
| `angel_index_ai_trades_plan.csv` | __ rows | HH:MM | Verify column count present |
| `angel_index_ai_pnl_log.csv` | __ rows | HH:MM | Verify column count = 15 |

**Data Quality Check:**

- ☐ All timestamps within market hours (9:15 AM – 3:30 PM IST)
- ☐ No null values in critical columns (underlying, signal, final_score)
- ☐ Signal values in expected range (CALL, PUT, HOLD, etc.)
- ☐ Scores in [0.0, 1.0] range
- ☐ No duplicate timestamps (within 1-second precision)

---

### Option 12: Synthetic Backtest (CONSERVATIVE)

**Run Time:** HH:MM AM/PM  
**Duration:** __ minutes  

| Metric | Value | Notes |
|--------|-------|-------|
| **Backtest Start Date** | YYYY-MM-DD | |
| **Backtest End Date** | YYYY-MM-DD | |
| **Trades Analyzed** | __ count | Total virtual trades |
| **Winning Trades** | __ count | (winning count) |
| **Losing Trades** | __ count | (losing count) |
| **Win Rate** | __% | (winning / total) × 100 |
| **Net P&L** | ₹__ | (simulated, DRY-RUN only) |
| **Max Favorable P&L** | ₹__ | Best single trade |
| **Max Adverse P&L** | ₹__ | Worst single trade |
| **Max Drawdown** | ₹__ | Peak-to-trough loss |
| **Profit Factor** | __.__ | (gross profit / gross loss) |

**Backtest Result:** ☐ PASS ☐ FAIL  

**Notes:**
```
(Any issues, interesting patterns, or anomalies observed)
```

---

### Option 27: Safety Layer Checks (Hourly – 10:00 AM, 12:00 PM, 2:00 PM)

**Check Time 1: 10:00 AM**

| Component | Status | Notes |
|-----------|--------|-------|
| Overtrade Detector | ☐ PASS ☐ FAIL | Virtual orders < 50/hour |
| Signal Quality Meter | ☐ PASS ☐ FAIL | Confidence > 0.5 |
| Execution Guardrail | ☐ PASS ☐ FAIL | All safety flags False |
| Market Regime Classifier | ☐ PASS ☐ FAIL | Regime detected |

**Check Time 2: 12:00 PM**

| Component | Status | Notes |
|-----------|--------|-------|
| Overtrade Detector | ☐ PASS ☐ FAIL | Virtual orders < 50/hour |
| Signal Quality Meter | ☐ PASS ☐ FAIL | Confidence > 0.5 |
| Execution Guardrail | ☐ PASS ☐ FAIL | All safety flags False |
| Market Regime Classifier | ☐ PASS ☐ FAIL | Regime detected |

**Check Time 3: 2:00 PM**

| Component | Status | Notes |
|-----------|--------|-------|
| Overtrade Detector | ☐ PASS ☐ FAIL | Virtual orders < 50/hour |
| Signal Quality Meter | ☐ PASS ☐ FAIL | Confidence > 0.5 |
| Execution Guardrail | ☐ PASS ☐ FAIL | All safety flags False |
| Market Regime Classifier | ☐ PASS ☐ FAIL | Regime detected |

**Overall Safety Status:** ☐ ALL PASS ☐ ISSUES FOUND

---

### Option 28–29: Real Outcome Logging & Signal Accuracy

**Run Time:** HH:MM PM (around 3:00 PM)  

| Metric | Value | Notes |
|--------|-------|-------|
| **Signals with Outcomes Captured** | __ / __ | (count / total signals) |
| **Signals with Real Price Data** | __ / __ | Market close prices matched |
| **Accuracy (Win Rate)** | __% | (correct signals / total) |
| **Hit Rate (Directional)** | __% | Predicted direction matched actual |
| **False Signal Rate** | __% | (100% - accuracy) |

**Outcome Log File:** `storage/live/angel_index_ai_pnl_log.csv`

**Quality Check:**

- ☐ Outcome column populated
- ☐ Exit prices match market close
- ☐ P&L calculations correct
- ☐ No missing outcome data

---

## END-OF-DAY REPORTS (3:20 PM – 3:40 PM)

### Option 36: Daily Learning Report

**Generated:** ☐ YES ☐ NO  
**File:** `logs/angel_daily_learning_YYYY-MM-DD.md`  
**Size:** __ KB  

**Report Contents (verify all present):**
- ☐ Signal statistics (count, distribution by index)
- ☐ Model performance metrics
- ☐ Top performing trades
- ☐ Worst performing trades
- ☐ Identified issues or anomalies
- ☐ Recommendations for next day

**Key Findings:**
```
(Summarize main points from learning report)
```

---

### Option 37: Rolling 7-Day Dashboard

**Generated:** ☐ YES ☐ NO  
**File:** `reports/rolling_7day_dashboard.md`  
**Size:** __ KB  

**Dashboard Contents (verify all present):**
- ☐ 7-day signal trends
- ☐ Daily accuracy trend
- ☐ Model consistency metrics
- ☐ Week-to-date performance
- ☐ Comparison with baseline

---

### Option 40: Daily Auto-Reports (All Reports)

**Generated:** ☐ YES ☐ NO  
**Files Created:** __ count  

**Reports Generated (check which exist):**
- ☐ PnL summary (virtual)
- ☐ Signal distribution
- ☐ Execution statistics
- ☐ Error log summary
- ☐ Daily digest

**Total Report Size:** __ MB  

---

## DATA INTEGRITY VERIFICATION (3:40 PM – 4:00 PM)

### CSV Consistency

| File | Rows | Columns | Timestamps Valid | Notes |
|------|------|---------|-----------------|-------|
| signals.csv | __ | 5 | ☐ YES ☐ NO | Should be 9:15 AM – 3:30 PM |
| orders.csv | __ | 15 | ☐ YES ☐ NO | Should be 9:15 AM – 3:30 PM |
| pnl_log.csv | __ | 15 | ☐ YES ☐ NO | Should be 9:15 AM – 3:30 PM |
| trades_plan.csv | __ | ? | ☐ YES ☐ NO | Should be 9:15 AM – 3:30 PM |

**Overall Consistency:** ☐ PASS ☐ FAIL

---

### Log File Validation

**Main Log File:** `logs/YYYY-MM-DD.log`  
**File Size:** __ MB  

**Log Analysis:**

```bash
# Verify using command line:
grep "[ERROR]" logs/YYYY-MM-DD.log | wc -l
```

| Item | Count | Status |
|------|-------|--------|
| [ERROR] entries | __ | ☐ Should be 0 |
| [WARN] entries | __ | ☐ OK (data-driven WARNs acceptable) |
| [INFO] entries | __ | ☐ Should be > 1000 |

**Critical Errors Found (if any):**
```
(List any actual errors found in logs)
```

---

### No Real Orders Verification

**Verify using command line:**

```bash
# Check that all orders are DRY-RUN (simulated)
grep "ORDER_ID" storage/live/angel_virtual_orders.csv | head -5
```

- ☐ All orders have "SIMULATED" or "DRY-RUN" marker
- ☐ No real AngelOne order IDs in CSV
- ☐ No real broker confirmations in logs
- ☐ Manually verify: Check AngelOne app – NO new orders placed

**Confirmation:** ☐ NO REAL ORDERS WERE PLACED ✅

---

## OVERALL ASSESSMENT

### Success Criteria Met

| Criterion | Status | Notes |
|-----------|--------|-------|
| ≥ 400 signals generated | ☐ YES ☐ NO | Actual: __ signals |
| 0 [ERROR] in logs | ☐ YES ☐ NO | Actual: __ errors |
| Safety checks all PASS | ☐ YES ☐ NO | From Option 27 |
| No real orders | ☐ YES ☐ NO | Verified |
| All reports generated | ☐ YES ☐ NO | Count: __ reports |
| Data consistency verified | ☐ YES ☐ NO | All CSVs valid |
| Backtest ran successfully | ☐ YES ☐ NO | P&L: ₹__ |

### Overall Result

**Live DRY-RUN Day Status:**

- ☐ ✅ SUCCESSFUL (All criteria met, system ready)
- ☐ ⚠️ PARTIAL (Some issues, but non-critical)
- ☐ ❌ FAILED (Critical issues found, needs investigation)

---

## ISSUES & OBSERVATIONS

### Critical Issues (if any)

```
(List any critical issues that prevent system from working)

Issue #1:
  Description: 
  Root Cause:
  Resolution:
  Status: [RESOLVED / PENDING]

Issue #2:
  ...
```

### Warnings & Non-Critical Issues

```
(List any warnings or minor issues observed)

Warning #1:
  Description:
  Severity: [HIGH / MEDIUM / LOW]
  Action: [INVESTIGATE / MONITOR / IGNORE]

Warning #2:
  ...
```

### Anomalies Observed

```
(Unusual patterns, unexpected behavior, or surprises)

Anomaly #1:
  What: 
  Possible Cause:
  Investigation Needed: [YES / NO]

Anomaly #2:
  ...
```

---

## PERFORMANCE METRICS SUMMARY

### Signal Generation

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Signals | __ | ≥ 400 | ☐ PASS ☐ FAIL |
| Avg per Hour | __ | ≥ 40 | ☐ PASS ☐ FAIL |
| Signals with High Confidence (> 0.7) | __% | ≥ 50% | ☐ PASS ☐ FAIL |
| Index Distribution (NIFTY : BANKNIFTY : FINNIFTY) | : : | Balanced | ☐ PASS ☐ FAIL |

### Execution Quality

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Virtual Orders Placed | __ | ≥ 50 | ☐ PASS ☐ FAIL |
| Avg Virtual Order per Hour | __ | ≤ 50 | ☐ PASS ☐ FAIL |
| Backtest Accuracy | __% | ≥ 50% | ☐ PASS ☐ FAIL |
| Backtest Win Rate | __% | ≥ 40% | ☐ PASS ☐ FAIL |

### Safety & Reliability

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| System Uptime | __% | 100% | ☐ PASS ☐ FAIL |
| Safety Checks Passed | __ / 4 | 4 / 4 | ☐ PASS ☐ FAIL |
| Real Orders Placed | __ | 0 | ☐ PASS ☐ FAIL |
| Data Corruption | __ | 0 | ☐ PASS ☐ FAIL |

---

## LESSONS LEARNED & RECOMMENDATIONS

### What Went Well

```
(Positive observations and successes)

1. 

2. 

3. 
```

### What Could Be Improved

```
(Areas for optimization or enhancement)

1. 

2. 

3. 
```

### Changes for Next Live Day

```
(Specific actionable improvements for the next dress rehearsal)

1. 

2. 

3. 
```

### Confidence Level for Next Phase (Phases 381–400)

**Based on this live DRY-RUN day:**

- ☐ HIGH CONFIDENCE (System working perfectly, ready for 381–400)
- ☐ MEDIUM CONFIDENCE (System mostly working, minor issues to fix first)
- ☐ LOW CONFIDENCE (Major issues found, needs investigation before 381–400)

**Justification:**
```
(Explain why you have this confidence level)
```

---

## DATA ARCHIVAL

### Archive Location

```
storage/archive/YYYY-MM-DD_dress_rehearsal/
```

### Files Archived

- ☐ `angel_index_ai_signals.csv` (snapshot)
- ☐ `angel_virtual_orders.csv` (snapshot)
- ☐ `angel_index_ai_pnl_log.csv` (snapshot)
- ☐ `angel_index_ai_trades_plan.csv` (snapshot)
- ☐ `logs/YYYY-MM-DD.log` (full day's log)
- ☐ `logs/angel_daily_learning_YYYY-MM-DD.md` (learning report)
- ☐ `reports/rolling_7day_dashboard.md` (7-day dashboard)
- ☐ All other generated reports (__.md files)

**Archive Size:** __ MB  
**Archive Verified:** ☐ YES ☐ NO

---

## SIGN-OFF

### Tester Verification

**I verify that:**
- ☐ All pre-market checks completed
- ☐ Live DRY-RUN executed for full session (9:10 AM – 3:20 PM)
- ☐ All data has been captured and verified
- ☐ No real orders were placed on any broker
- ☐ All safety flags remained False throughout
- ☐ This report accurately reflects the day's execution

**Tester Name:** ________________________  
**Signature:** ________________________  
**Date:** ________________________  
**Time:** ________________________  

### System Status Statement

```
Based on this live DRY-RUN dress rehearsal:

✅ SYSTEM3 PHASES 1–380 ARE OPERATING CORRECTLY

The complete pipeline (signal generation → backtesting → 
reporting) executed successfully in DRY-RUN mode with no 
live order execution. All safety guards remained active. 
The system is ready for:

[ ] Additional live DRY-RUN days (confidence building)
[ ] Design and implementation of Phases 381–400
[ ] Planning for production promotion with risk oversight

Next Steps:
- Review all generated reports and logs
- Archive this day's data
- Incorporate lessons learned
- Schedule next live DRY-RUN day (optional)
- Begin Phase 381–400 design (when ready)
```

---

**End of Report Template**

*Template Created: 2025-12-07*  
*Status: Ready to be filled with real data from live DRY-RUN day*  
*Safety Mode: DRY-RUN (All Flags False)*

