# System3 Pre-Market Checklist - Execution Guide
**Date**: 2025-12-04  
**Purpose**: Comprehensive 20-point validation before market open

---

## Quick Start

**Run the checklist**:
```batch
C:\Genesis_System3\venv\Scripts\python.exe system3_premarket_checklist.py
```

Or use the batch file:
```batch
run_premarket_checklist.bat
```

---

## Checklist Overview

The script performs 20 comprehensive checks:

1. ✅ SmartAPI Login (dry-run)
2. ✅ Internet Stability
3. ✅ Heartbeat Freshness (< 60 seconds)
4. ✅ Watchdog Running
5. ✅ Autorun Master Running
6. ✅ Storage CSVs Exist (non-zero signals)
7. ✅ Curated Signals Not Corrupted
8. ✅ No CSV Parsing Errors
9. ✅ Phase Scheduler IST Aligned
10. ✅ Shutdown Flag Check
11. ✅ No Crash Logs (last 24h)
12. ✅ Next_Run Timestamps Match Schedule
13. ✅ AngelOne Data Extractor
14. ✅ PnL Simulator Loads CSV
15. ✅ Options Chain Retrieval
16. ✅ EV Tables Exist
17. ✅ Threshold Proposer Model
18. ✅ Autopilot Encoding Layer
19. ✅ Strike Decision Logic
20. ✅ Candidate Trade Score > 0.01

---

## Expected Results

### Pre-Market (Before Autorun Starts)

**Expected Failures** (non-blocking):
- Check 3: Heartbeat Freshness - Will be stale (OK, updates on start)
- Check 4: Watchdog Running - Not running yet (OK, starts with batch file)
- Check 5: Autorun Master Running - Not running yet (OK, starts with batch file)
- Check 20: Candidate Trade Score - May be low if no signals yet (OK)

**Expected Passes**:
- Check 1: SmartAPI Login - May fail if not installed (non-blocking for DRY-RUN)
- Check 2: Internet Stability - Should pass
- Check 6-7: CSV Files - Should exist if signals were generated
- Check 8: CSV Parsing - Should pass (errors handled gracefully)
- Check 9: Phase Scheduler - Should pass (IST timezone in code)
- Check 10: Shutdown Flag - Should pass (from yesterday)
- Check 11: Crash Logs - Should pass (no recent crashes)
- Check 13-19: Code/File Checks - Should pass (files exist)

---

## Auto-Repair Features

The script attempts automatic diagnosis and repair for:

1. **Missing Files**: Reports location and suggests regeneration
2. **Stale Data**: Identifies and suggests refresh
3. **Import Errors**: Reports missing dependencies
4. **CSV Issues**: Confirms graceful error handling
5. **Process Checks**: Notes expected state before autorun

---

## Final Report

After execution, the script generates:
- **Console Output**: Real-time check results
- **Report File**: `docs/SYSTEM3_PREMARKET_CHECKLIST_REPORT.md`

**Report includes**:
- Summary (passed/failed counts)
- Detailed results for each check
- Repairs applied (if any)
- Final verdict (READY / NOT READY)

---

## Manual Execution

If the script cannot run due to terminal issues, manually verify:

### Critical Checks (Must Pass):
1. **Internet**: Ping 8.8.8.8
2. **Shutdown Flag**: Check `system3_shutdown_flag.json` date (should be yesterday)
3. **CSV Files**: Verify `storage/live/angel_index_ai_signals.csv` exists
4. **Safety Flags**: Verify `config/live_trade_config.py` has `LIVE_TRADING_ENABLED = False`

### Non-Critical Checks (Warnings OK):
- Watchdog/Autorun not running (expected before start)
- Heartbeat stale (expected before start)
- Low candidate scores (expected if no signals yet)

---

## Troubleshooting

### If Check Fails:
1. Read the "Details" message
2. Check the "Repair" suggestion
3. Apply the repair manually if needed
4. Re-run the check

### Common Issues:
- **SmartAPI not installed**: Non-blocking for DRY-RUN mode
- **CSV files missing**: Will be created when signals generate
- **Processes not running**: Expected before autorun starts
- **Stale heartbeat**: Expected, updates on autorun start

---

**Last Updated**: 2025-12-04

