# GENESIS SYSTEM3 LIVE DRY-RUN DAY PLAN

**Purpose:** Execute a full, production-like dress rehearsal of the complete System3 pipeline (Phases 1–380) in **DRY-RUN mode only**, demonstrating how data, signals, and decisions flow in real time without any live order execution.

**Target Date:** First available full market day (9:10 AM to 3:30 PM IST)

**Safety Status:** ✅ All safety flags remain FALSE (DRY-RUN mode enforced)
- `LIVE_TRADING_ENABLED = False`
- `USE_LIVE_EXECUTION_ENGINE = False`
- `auto_execute_trades = False`
- All AngelOne/Ultra live flags = False

---

## SECTION 1: PRE-MARKET CHECKLIST (8:45 AM – 9:00 AM IST)

### 1.1 System Startup & Health (8:45 AM)

**Run from `run_system3.py` menu:**
```
Option 2: Health Check
```
- **Expected Output:** System health report showing all components ready
- **Key Metrics to Verify:**
  - All file paths exist (live CSVs, logs, models, storage directories)
  - Safety flags confirmed as False
  - Broker configuration loaded (AngelOne credentials, instruments file)
  - DRY-RUN mode active

**Log File to Watch:**
```
logs/2025-12-XX.log
```

---

### 1.2 Data Pipeline Test (8:50 AM)

**Run from `run_system3.py` menu:**
```
Option 3: Test data pipeline (live + history)
```
- **Purpose:** Verify that live Angel One API can fetch real OHLC and instrument data
- **What It Checks:**
  - AngelOne connection working
  - Can fetch 5-min OHLC for NIFTY, BANKNIFTY, FINNIFTY
  - Historical data loading from disk
  - CSV writers are ready (will log data without executing trades)
- **Expected Output:** Sample price data for 3–5 indices printed to console

**CSV Files to Check After:**
```
storage/live/angel_index_ai_signals.csv (will be appended to during the day)
storage/live/angel_virtual_orders.csv (will log virtual orders only)
storage/live/angel_index_ai_pnl_log.csv (PnL tracking)
```

**Duration:** ~2–3 minutes

---

### 1.3 Verify Block Test Infrastructure (8:55 AM)

**Run from `run_system3.py` menu:**
```
Option 109: Run Phase Range
> 331-380
```
- **Purpose:** Quick sanity check that Phases 331–380 execute without errors
- **Expected Output:**
  ```
  === BATCH EXECUTION SUMMARY ===
  OK:    43/50
  WARN:  7/50 (all data-driven; acceptable)
  ERROR: 0/50
  ```
- **Known WARNs (Do NOT investigate; data quality expected):**
  - Phase 332, 334, 338–340, 343: Low signal volume (< 50 signals) – normal for DRY-RUN
  - Phase 367: Safety guardrails active (intentional by design)

**Duration:** ~1–2 minutes

---

## SECTION 2: MAIN LIVE TRADING WINDOW (9:10 AM – 3:30 PM IST)

### 2.1 PARALLEL LOOP 1: LIVE WATCH & SIGNAL GENERATION (9:10 AM – 3:20 PM)

**Start in BACKGROUND TERMINAL 1:**
```
run_system3.py > Option 11: Angel One LIVE AI signals (from models)
```

**What It Does:**
- Fetches live OHLC every 30 seconds from AngelOne API
- Generates AI signals using trained models (Phase 10–11 trained models)
- Creates synthetic trade plans (Phase 13 backtest logic) *DRY-RUN only*
- Logs all signals to `storage/live/angel_index_ai_signals.csv`
- **CRITICAL:** Does NOT place any real orders (DRY-RUN enforced)

**Key CSV Files Being Updated (Watch These):**
- `storage/live/angel_index_ai_signals.csv` – live signals from AI models
- `storage/live/angel_virtual_orders.csv` – simulated orders (no broker execution)
- `storage/live/angel_index_ai_trades_plan.csv` – trade plans generated

**Expected Behavior:**
- Every 30 seconds: New row appended to `angel_index_ai_signals.csv`
- Console output: `[AI] Snapshot #1, #2, #3, ... Signal count: X, Trade plan count: Y`
- Runs continuously for ~6 hours (until 3:20 PM)
- No errors expected; occasional WARNs about low volume = OK

**How to Monitor (Watch in Excel/VS Code):**
```
Refresh: storage/live/angel_index_ai_signals.csv every 5 minutes
Count rows: Should increase by ~12–20 rows per hour
Columns: underlying, symbol, signal, final_score, ts (verify present)
```

**Log File to Tail:**
```
tail -f logs/2025-12-XX.log
```

---

### 2.2 PARALLEL LOOP 2: PERIODIC SYNTHETICS & ANALYSIS (9:30 AM, 12:00 PM, 3:00 PM)

**Run at these times from TERMINAL 2:**

**9:30 AM (First backtest after 1 hour of signals):**
```
run_system3.py > Option 12: Synthetic backtest (CONSERVATIVE)
```
- **Purpose:** Test that backtester can process the signals generated so far
- **Expected Output:** Backtest report showing virtual P&L, win rate, drawdown
- **Duration:** ~2–3 minutes

**12:00 PM (Mid-day snapshot):**
```
run_system3.py > Option 29: Signal vs outcome analyzer
```
- **Purpose:** Compare early signals against real market moves (as they happen)
- **Expected Output:** Accuracy, hit rate for the morning signals
- **Duration:** ~2–3 minutes

**3:00 PM (End-of-day analysis):**
```
run_system3.py > Option 28: Real outcome logger (test)
```
- **Purpose:** Manually log final market outcomes for all signals
- **Expected Output:** Outcome log stored in CSV
- **Duration:** ~2–3 minutes

---

### 2.3 PARALLEL LOOP 3: SAFETY & QUALITY GATES (Every 60 minutes)

**Run at 10:00 AM, 11:00 AM, 12:00 PM, 1:00 PM, 2:00 PM, 3:00 PM from TERMINAL 3:**

**Option A: Safety Layer Check (every hour on the hour)**
```
run_system3.py > Option 27: Safety Layer V2 Check
```
- **What It Checks:**
  - Overtrade detector: Confirms no excessive virtual orders
  - Signal quality meter: Quality of AI signals generated
  - Execution guardrail: Confirms DRY-RUN still active, no real execution paths triggered
  - Market regime classifier: Current market condition assessment
- **Expected Output:** All checks PASS; safety flags remain False
- **Duration:** ~1 minute per check

**Option B: Model Drift Monitor (mid-morning, mid-afternoon)**
```
run_system3.py > Option 60: Feature drift analyzer
```
- **What It Checks:** Whether live data features are drifting from training data
- **Expected Output:** Drift report; should be minimal for single-day backtest
- **Duration:** ~2 minutes

---

## SECTION 3: POST-MARKET WRAP-UP (3:20 PM – 4:00 PM IST)

### 3.1 Generate End-of-Day Reports (3:20 PM – 3:40 PM)

**Run in sequence from TERMINAL 4:**

**Step 1: Daily Learning Report (3:20 PM)**
```
run_system3.py > Option 36: Daily learning report
```
- **Output File:** `logs/angel_daily_learning_YYYY-MM-DD.md`
- **Contains:** Today's signal accuracy, model performance, issues observed
- **Duration:** ~2 minutes

**Step 2: Rolling 7-Day Dashboard (3:25 PM)**
```
run_system3.py > Option 37: Rolling 7-day learning dashboard
```
- **Output File:** `reports/rolling_7day_dashboard.md`
- **Contains:** Week-to-date trends, consistency checks
- **Duration:** ~2 minutes

**Step 3: Daily Auto-Reports (3:30 PM)**
```
run_system3.py > Option 40: Daily auto-reports (Generate All)
```
- **Output Files:** Multiple CSVs and MDs in `reports/` directory
- **Contains:** PnL summary, signal distribution, execution stats
- **Duration:** ~3 minutes

---

### 3.2 Validation & Archival (3:40 PM – 4:00 PM)

**Manual Steps:**

1. **Verify No Real Orders Were Placed:**
   ```
   Check: storage/live/angel_virtual_orders.csv
   Count rows: Should match "Option 14" virtual execution count
   Verify: All orders are SIMULATED, not on AngelOne broker
   ```

2. **Collect Key Metrics:**
   - Total signals generated: `wc -l storage/live/angel_index_ai_signals.csv`
   - Virtual orders placed: `wc -l storage/live/angel_virtual_orders.csv`
   - Backtest profit/loss: Check Option 12/13 output
   - Accuracy (signals vs real moves): Check Option 29 output
   - Safety checks passed: Check Option 27 output (should be all PASS)

3. **Archive the Day's Data:**
   ```
   Create folder: storage/archive/YYYY-MM-DD_dress_rehearsal/
   Copy:
     - storage/live/*.csv (snapshots of all live CSVs)
     - logs/2025-12-XX.log (full day's execution log)
     - reports/*YYYY-MM-DD*.md (all generated reports)
   ```

---

## SECTION 4: FILES TO MONITOR DURING THE DAY

### 4.1 CSVs Being Written (Watch These in Real Time)

| CSV File | Written By | Update Frequency | Expected Rows/Hour |
|----------|-----------|-----------------|-------------------|
| `storage/live/angel_index_ai_signals.csv` | Phase 11 (LIVE signals) | Every 30 sec | 120 rows |
| `storage/live/angel_virtual_orders.csv` | Phase 14 (DRY trade executor) | Varies by signal | 5–20 rows |
| `storage/live/angel_index_ai_pnl_log.csv` | Phase 15–16 (PnL tracking) | Every 5 min | 60–80 rows |
| `storage/live/angel_index_ai_trades_plan.csv` | Phase 13 (backtest) | Varies | 5–50 rows |

**How to Monitor:**
```
# In VS Code terminal 4:
while True; do
  echo "=== $(date) ==="
  wc -l storage/live/*.csv
  sleep 300
done
```

---

### 4.2 Log Files to Tail

**Main execution log:**
```
logs/2025-12-XX.log
```
- **Watch for:** `[ERROR]` entries (none expected), `[WARN]` entries (data-quality WARNs OK)

**Block test log (if re-running phases):**
```
logs/block_test_331_360_*.log
```

**Report output:**
```
reports/*YYYY-MM-DD*.md (new reports generated hourly)
```

---

### 4.3 Health Check Indicators (Success Criteria)

✅ **System is healthy if, by end of day:**

1. **Signal Generation:** ≥ 400 signals generated (40+ per hour × 10 hours)
2. **No Errors:** 0 `[ERROR]` entries in main log
3. **Safety Passed:** Option 27 (Safety Layer Check) shows all PASS
4. **Backtest Ran:** Option 12/13 synthetic backtest completes without crashes
5. **Reports Generated:** All daily reports (Options 36, 37, 40) complete successfully
6. **No Real Orders:** `angel_virtual_orders.csv` contains ONLY simulated orders, no broker execution
7. **Data Consistency:** All timestamps in CSVs are within market hours (9:15 AM – 3:30 PM IST)

---

## SECTION 5: EXPECTED CONSOLE OUTPUT EXAMPLES

### Signal Generation Loop (Option 11)
```
[INFO] Starting Angel One LIVE AI signals loop...
Initializing AngelOne broker...
Login OK.

[AI] Snapshot #1 ...
  -> Built snapshot: 3 indices, 87 rows
  -> Running Phase 11 (signal generation)...
  -> Generated 12 signals (4 BANKNIFTY, 5 NIFTY, 3 FINNIFTY)
Sleeping for 30 seconds...

[AI] Snapshot #2 ...
  -> Built snapshot: 3 indices, 87 rows
  -> Running Phase 11 (signal generation)...
  -> Generated 15 signals (5 BANKNIFTY, 6 NIFTY, 4 FINNIFTY)
Sleeping for 30 seconds...
```

### Backtest Run (Option 12)
```
Running synthetic backtest [CONSERVATIVE]...

[INFO] Loaded trade plan: 47 trades
[INFO] Backtesting (CONSERVATIVE profile)...
[RESULTS SUMMARY]
Total trades: 47
Winning trades: 28 (59.6%)
Losing trades: 19 (40.4%)
Net P&L: +₹4,250 (DRY, simulated)
Max drawdown: -₹850
Win/Loss ratio: 1.47x
Duration: ~2 min

Test result: PASS
```

### Safety Check (Option 27)
```
=== SAFETY LAYER V2 - COMPLETE CHECK ===

[OVERTRADE DETECTOR]
Total virtual orders: 143
Avg per hour: 14.3
Status: ✓ PASS (below 50/hour limit)

[SIGNAL QUALITY METER]
Avg confidence: 0.72 / 1.0
High-confidence signals: 89/143 (62.2%)
Status: ✓ PASS

[EXECUTION GUARDRAIL]
LIVE_TRADING_ENABLED: False ✓
USE_LIVE_EXECUTION_ENGINE: False ✓
auto_execute_trades: False ✓
Status: ✓ PASS

[MARKET REGIME CLASSIFIER]
Current regime: Normal volatility
Confidence: 0.85
Status: ✓ PASS
```

---

## SECTION 6: TROUBLESHOOTING & QUICK FIXES

### Issue: Signals not being generated
**Cause:** AngelOne API not responding  
**Fix:**
```
1. Check internet connection
2. Verify AngelOne login credentials in config/
3. Run Option 4 (Test Angel One API) manually
4. Restart Option 11 loop
```

### Issue: Virtual orders not logging
**Cause:** DRY-RUN mode may be disabled  
**Fix:**
```
1. Stop execution (Ctrl+C)
2. Open core/execution/angel_trade_executor.py
3. Verify: LIVE_TRADING_ENABLED = False
4. Verify: auto_execute_trades = False
5. Restart Option 11
```

### Issue: Backtest crashes
**Cause:** Invalid trade plan format  
**Fix:**
```
1. Check storage/live/angel_index_ai_trades_plan.csv exists
2. Run Option 13 (DEV backtest) instead (more lenient)
3. Check logs/ for specific error
```

### Issue: Reports not generating
**Cause:** Missing input CSVs  
**Fix:**
```
1. Ensure Option 11 (LIVE signals) is still running
2. Wait at least 30 minutes for data to accumulate
3. Check storage/live/ directory has all required CSVs
4. Try Option 36 manually again
```

---

## SECTION 7: TIME ESTIMATE & SCHEDULING

| Time | Task | Duration | Terminal |
|------|------|----------|----------|
| 8:45 AM | Option 2 (Health Check) | 2 min | 1 |
| 8:50 AM | Option 3 (Test data pipeline) | 3 min | 1 |
| 8:55 AM | Option 109 (Phase 331–380 test) | 2 min | 1 |
| **9:10 AM** | **Option 11 (START LIVE SIGNALS)** | **6 hours** | **1 (bg)** |
| 9:30 AM | Option 12 (Synthetic backtest) | 3 min | 2 |
| 12:00 PM | Option 29 (Signal vs outcome) | 3 min | 2 |
| 1:00 PM | Option 27 (Safety Layer check) | 1 min | 3 |
| 2:00 PM | Option 27 (Safety Layer check) | 1 min | 3 |
| 3:00 PM | Option 28 (Outcome logger) | 3 min | 2 |
| 3:20 PM | **STOP** Option 11 (Ctrl+C) | – | 1 |
| 3:20 PM | Option 36 (Daily learning report) | 2 min | 4 |
| 3:25 PM | Option 37 (7-day dashboard) | 2 min | 4 |
| 3:30 PM | Option 40 (Auto-reports) | 3 min | 4 |
| 3:40 PM | Verify & Archive | 15 min | Manual |

**Total Active Time:** ~45 minutes  
**Total Idle Time:** ~6.5 hours (Options 11 in background)

---

## SECTION 8: SUCCESS CRITERIA & SIGN-OFF

### Final Checklist (3:40 PM)

- [ ] No `[ERROR]` entries in main log
- [ ] ≥ 400 signals generated throughout the day
- [ ] ≥ 50 virtual orders logged (DRY-RUN, no broker execution)
- [ ] Option 27 (Safety checks) shows all PASS
- [ ] Option 12/13 backtest executed without crashes
- [ ] Options 36, 37, 40 (reports) completed successfully
- [ ] No real orders placed on AngelOne broker
- [ ] Data in all CSVs is consistent and timestamped correctly

### Sign-Off Statement

**IF ALL ABOVE ITEMS ARE CHECKED:**
```
✅ LIVE DRY-RUN DRESS REHEARSAL SUCCESSFUL

System3 Phases 1–380 are production-ready and behave correctly 
under real market data in DRY-RUN mode. No live execution occurred. 
All safety guards remained active throughout the day.

Ready to proceed with:
1. Additional live DRY-RUN days (for confidence building)
2. Design and implementation of Phases 381–400
3. Planning for production promotion with risk oversight
```

---

## APPENDIX A: KEY CONFIGURATION FILES TO VERIFY

Before the test day, confirm these are set correctly:

```
config/angel_auth_config.json         → AngelOne login credentials
config/angel_instruments.csv           → All 3 indices present (NIFTY, BANKNIFTY, FINNIFTY)
config/automation_config.json          → auto_execute_trades = false
config/system3_trading_config.json     → LIVE_TRADING_ENABLED = false
core/execution/angel_trade_executor.py → DRY_RUN = True
```

---

## APPENDIX B: ADDITIONAL READING

- **Phase 11 (LIVE Signals):** `core/engine/angel_live_ai_signals.py`
- **Phase 14 (Trade Executor):** `core/engine/angel_trade_executor.py`
- **Phase 12–13 (Backtester):** `core/engine/angel_synthetic_backtester.py`
- **Phase 27 (Safety Layer):** `core/engine/angel_overtrade_detector.py` + others
- **Latest Block Test Results:** `logs/block_test_331_360_*.log` (most recent)
- **Full Phase Registry:** Run Option 110 (List All Phases)

---

**End of Document**

*Created: 2025-12-07*  
*Status: READY FOR EXECUTION*  
*Safety Mode: DRY-RUN (All Flags False)*
