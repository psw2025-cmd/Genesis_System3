# 🔄 PHASE 201 AUTO-TRIGGER INTEGRATION

## Overview

**Phase 201: Curated Refresh** has been integrated into the BAT file as a **FULLY AUTOMATED CONDITIONAL TRIGGER**.

When snapshot data is detected as stale (>1 day old), Phase 201 automatically executes without any manual intervention.

---

## What is Phase 201?

**Phase 201: Curated Refresh** is a critical data preparation phase that:

1. **Archives old live signals**
   - Takes existing live signal CSV files
   - Moves them to timestamped archive folder
   - Preserves historical record

2. **Cleans malformed rows**
   - Scans storage/live/archive directory
   - Removes rows with missing essential columns (ts, spot, underlying)
   - Ensures data integrity

3. **Builds curated training dataset**
   - Combines archived signals from last 5 days
   - Creates consolidated training data
   - Ready for ML model consumption

---

## Integration Location

### In BAT File: Phase 2 (System Health Check & Auto-Healing)

**File:** `START_AUTORUN_AND_WATCHDOG.bat`

**Section:** Phase 2, Data Freshness Check

```batch
if "%DATA_CHECK%"=="STALE_DATA" (
    echo ⚠️  STALE DATA DETECTED - Triggering Phase 201: Curated Refresh...
    echo.
    echo Running: python system3_prep_for_new_day.py (Phase 201)
    echo   ├─ Archive old live signals
    echo   ├─ Clean malformed rows from history
    echo   └─ Build curated training dataset from last 5 days
    echo.
    python system3_prep_for_new_day.py
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ✅ PHASE 201 COMPLETE - Data refreshed successfully
        echo   ├─ Live signals archived
        echo   ├─ History cleaned
        echo   └─ Curated training dataset built
    ) else (
        echo.
        echo ⚠️  PHASE 201 ENCOUNTERED ISSUES
        echo   System will continue with existing data
        echo   Check logs/system3_prep_for_new_day_*.log for details
    )
)
```

---

## Auto-Trigger Conditions

| Condition | Trigger | Action |
|-----------|---------|--------|
| **Data age = 0 days (today)** | ❌ NO | Continue to next checks |
| **Data age = 1 day** | ✅ YES | Execute Phase 201 |
| **Data age = 5 days** | ✅ YES | Execute Phase 201 |
| **Data age = 10+ days** | ✅ YES | Execute Phase 201 |

**Logic:**
```
if latest_snapshot_date < today:
    → TRIGGER PHASE 201
else:
    → SKIP (data is current)
```

---

## When Phase 201 Auto-Triggers

### Scenario 1: System Boot with Old Data
```
Time: 08:00 AM
Latest snapshot: 2025-11-30 (Nov 30)
Current date: 2025-12-05 (Dec 5)
Data age: 5 days

→ Phase 2 runs
→ Detects: DATA_CHECK = "STALE_DATA"
→ Auto-triggers Phase 201
→ Archives old signals, cleans history, builds curated dataset
→ System continues with fresh data
```

### Scenario 2: System Boot with Current Data
```
Time: 09:30 AM
Latest snapshot: 2025-12-05 (Dec 5)
Current date: 2025-12-05 (Dec 5)
Data age: 0 days

→ Phase 2 runs
→ Detects: DATA_CHECK NOT "STALE_DATA"
→ Skips Phase 201
→ System continues immediately
```

### Scenario 3: Multiple Runs in Same Day
```
1st run: 08:00 AM (snapshot: Dec 5 at 8:00 AM)
→ Phase 2: Data age = 0, skip Phase 201

2nd run: 02:00 PM (snapshot: Dec 5 at 8:00 AM)
→ Phase 2: Data age = 0, skip Phase 201

3rd run: 08:01 AM next day (snapshot: Dec 5)
→ Phase 2: Data age = 1 day, trigger Phase 201
→ Archives signals, cleans, builds curated dataset
```

---

## Phase 201 Execution Details

### Input
```
Directory: storage/live/archive/
Files: angel_index_ai_signals_*.csv
Lookback: 5 days
```

### Processing
```
1. Scan archive directory for recent CSVs
2. Select files from last 5 days
3. Load each CSV (skip bad rows automatically)
4. Concatenate all dataframes
5. Drop rows missing essential columns (ts, spot, underlying)
6. Write to curated training path
```

### Output
```
File: core/engine/ai_model/curated_training_data.csv
Logs: logs/system3_prep_for_new_day_YYYYMMDD.log
Log entries:
  - [INFO] CSVs processed
  - [INFO] Row counts before/after cleaning
  - [OK] Final dataset written with row count
```

---

## Trigger Detection Logic

The BAT file uses this Python logic to detect if Phase 201 should trigger:

```python
import os
from datetime import datetime

snapshot_dir = 'storage/snapshots/'
if os.path.exists(snapshot_dir):
    files = sorted(os.listdir(snapshot_dir), reverse=True)
    if files:
        latest = files[0]
        date_str = latest[:8]  # Extract YYYYMMDD
        snapshot_date = datetime.strptime(date_str, '%Y%m%d')
        age_days = (datetime.now() - snapshot_date).days
        
        # TRIGGER DECISION
        if age_days > 0:
            print('STALE_DATA')  # → Phase 201 will trigger
        else:
            print('CURRENT')      # → Phase 201 will skip
```

---

## Error Handling

### If Phase 201 Fails
```
PHASE 201 ENCOUNTERED ISSUES
  System will continue with existing data
  Check logs/system3_prep_for_new_day_*.log for details
```

**Non-blocking:** System continues to Phase 3 (safety verification) even if Phase 201 fails

**Logging:** Detailed error messages written to daily prep log

### Common Issues
- Missing archive directory → Skipped gracefully
- No archived files → Skipped gracefully
- Bad CSV rows → Automatically skipped with `on_bad_lines='skip'`
- Insufficient disk space → Phase 1 would have detected this

---

## Manual Phase 201 Execution

If you want to manually trigger Phase 201 without waiting for stale data:

```powershell
cd C:\Genesis_System3
python system3_prep_for_new_day.py
```

Or via BAT file (which will auto-trigger if needed):

```powershell
.\START_AUTORUN_AND_WATCHDOG.bat
```

---

## Monitoring Phase 201 Execution

While Phase 201 is running, check the log file:

```powershell
Get-Content logs\system3_prep_for_new_day_*.log -Wait -Tail 20
```

**Example log output:**
```
[INFO] Building curated training dataset from archive files:
  - storage/live/archive/angel_index_ai_signals_20251205_1430.csv
  - storage/live/archive/angel_index_ai_signals_20251204_1530.csv
  - storage/live/archive/angel_index_ai_signals_20251203_1430.csv
[INFO] Curated dataset rows before dropna: 1245
[INFO] Curated dataset rows after dropna: 1089
[OK] Curated training dataset written to: core/engine/ai_model/curated_training_data.csv (rows=1089)
```

---

## Phase 201 + AI Controller Flow

### Complete Startup Sequence

```
User Action:
    ↓
    .\START_AUTORUN_AND_WATCHDOG.bat
    ↓
PHASE 1: Environment Validation & Auto-Repair
    ├─ Check venv
    ├─ Activate venv
    ├─ Check AI Controller exists
    └─ Auto-install missing dependencies
    ↓
PHASE 2: System Health Check & Auto-Healing
    ├─ Check data freshness
    │   └─ If age > 0 days:
    │       ├─ PHASE 201: Archive old signals
    │       ├─ PHASE 201: Clean malformed rows
    │       ├─ PHASE 201: Build curated dataset
    │       └─ Logs written to daily prep log
    ├─ Check heartbeat
    ├─ Check disk space
    └─ Run auto-heal diagnostics
    ↓
PHASE 3: Safety Verification
    └─ Verify LIVE_TRADING_ENABLED = False
    ↓
PHASE 4: Launch AI Controller with Continuous Monitoring
    ├─ Start watchdog
    ├─ Launch AI Controller (with fresh curated data from Phase 201)
    └─ Monitor every 30 seconds
    ↓
SYSTEM AUTONOMOUS
    └─ AI Controller makes decisions using Phase 201 curated data
```

---

## Why Phase 201 is Critical

**Without Phase 201:**
- Live signals accumulate in storage/live/
- History never cleaned
- Duplicate/conflicting data in training set
- ML model trained on dirty data
- Decision quality degrades

**With Phase 201:**
- Old signals archived automatically
- Malformed rows removed automatically
- Clean training dataset created automatically
- ML model trained on curated data
- Decision quality maintained

**Frequency:** Auto-triggers daily (whenever data is detected as stale)

---

## Documentation Files

- **BAT File:** `START_AUTORUN_AND_WATCHDOG.bat` (Phase 2 section)
- **Phase Implementation:** `system3_prep_for_new_day.py`
- **Log Output:** `logs/system3_prep_for_new_day_YYYYMMDD.log`

---

## Summary

| Aspect | Details |
|--------|---------|
| **Phase Name** | Phase 201: Curated Refresh |
| **Trigger** | Data age > 1 day (auto-detected) |
| **Location** | Phase 2 of START_AUTORUN_AND_WATCHDOG.bat |
| **File** | system3_prep_for_new_day.py |
| **Actions** | Archive signals, clean history, build curated dataset |
| **Frequency** | Auto-triggers when stale data detected |
| **Manual Required** | Zero (fully automated) |
| **Failure Handling** | Non-blocking, system continues |
| **Logging** | logs/system3_prep_for_new_day_*.log |

---

**STATUS: PHASE 201 FULLY INTEGRATED AS AUTO-TRIGGER** ✅
