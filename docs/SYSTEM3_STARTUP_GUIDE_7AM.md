# System3 Startup Guide - Starting at 7:24 AM
**Current Time**: 7:24 AM  
**Market Open**: 9:15 AM  
**Time Until Market**: ~1 hour 51 minutes

---

## ✅ Pre-Startup Verification

### 1. Shutdown Flag Check ✅
**Status**: ✅ **OK**
- Shutdown flag exists from **2025-12-03** (yesterday)
- **NOT today's date** - System will start correctly
- No blocking issues

### 2. Current Time vs Market Hours ✅
**Status**: ✅ **OK**
- Current: 7:24 AM
- Market Open: 9:15 AM
- **Autorun will wait until 9:15 AM** before starting autopilot
- Pre-market phases will run immediately

### 3. Critical Files ✅
**Status**: ✅ **ALL EXIST**
- `system3_autorun_master.py` ✅
- `system3_watchdog.py` ✅
- `system3_live_day_autopilot.py` ✅
- `START_AUTORUN_AND_WATCHDOG.bat` ✅

### 4. Safety Flags ✅
**Status**: ✅ **DRY-RUN CONFIRMED**
- `LIVE_TRADING_ENABLED = False` ✅
- `USE_LIVE_EXECUTION_ENGINE = False` ✅
- All safety checks will pass

---

## 🚀 Expected Behavior When You Start

### Immediate (7:24 AM - 9:15 AM)

1. **Watchdog Window Opens**
   - New window titled "System3 Watchdog"
   - Shows: "SYSTEM3 WATCHDOG - STARTING (HARDENED)"
   - Will monitor autorun master

2. **Autorun Master Window (Current Window)**
   - Shows: "SYSTEM3 AUTORUN MASTER - STARTING (HARDENED)"
   - Safety checks run (will pass)
   - Heartbeat thread starts
   - **Pre-market phases 201-310 run** (takes ~1-2 minutes)
   - Main loop starts, waiting for 9:15 AM

3. **What You'll See in Logs**:
   ```
   ======================================================================
   SYSTEM3 AUTORUN MASTER - STARTING (HARDENED)
   ======================================================================
   Date: 2025-12-04 07:24:XX
   ======================================================================
   
   SAFETY ENFORCEMENT CHECK
   ======================================================================
   LIVE_TRADING_ENABLED: False
   USE_LIVE_EXECUTION_ENGINE: False
   auto_execute_trades: False
   Ultra AUTO_EXECUTE_TRADES: False
   ======================================================================
   ✓ All safety checks passed - DRY-RUN mode confirmed
   ======================================================================
   
   Heartbeat thread started
   
   ======================================================================
   PRE-MARKET: Running phases 201-310
   ======================================================================
   [Phase execution logs...]
   
   [Main loop waiting for 9:15 AM...]
   ```

### At 9:15 AM (Market Open)

4. **Autopilot Starts Automatically**
   - Log shows: "9:15 AM: Starting DRY-RUN Autopilot"
   - OP2 Live Session begins
   - Signals generate every 30 seconds
   - Trade plans created (DRY-RUN only)

5. **During Market Hours (9:15 AM - 3:30 PM)**
   - Phases 220-260 run every 30 minutes
   - Curated file refreshes every 2 hours
   - OP cycles run hourly
   - Heartbeat updates every 60 seconds

### At 4:00 PM (Market Close)

6. **Clean Shutdown**
   - Signals archived at 3:30 PM
   - EOD Learning at 3:35 PM
   - Scheduled shutdown at 4:00 PM
   - Shutdown flag written
   - Watchdog detects shutdown flag and stops monitoring

---

## ✅ Verification Checklist (After Starting)

### Within 1 Minute of Starting:

- [ ] Watchdog window is open and showing logs
- [ ] Autorun master window is open and showing logs
- [ ] Safety checks show "DRY-RUN mode confirmed"
- [ ] Pre-market phases are running (or completed)
- [ ] No error messages in either window

### At 9:15 AM (Check Remotely if Possible):

- [ ] Autopilot started message appears
- [ ] OP2 Live Session started
- [ ] Signals are being generated
- [ ] Heartbeat is updating (check `system3_daily_heartbeat.json`)

### During Market Hours:

- [ ] System continues running without crashes
- [ ] Logs show periodic phase runs
- [ ] No critical errors in logs

---

## 🔍 How to Monitor While Away

### Option 1: Check Log Files
**Location**: `logs/`
- `system3_autorun_master_20251204.log` - Main autorun log
- `system3_watchdog_20251204.log` - Watchdog log
- `live_day_autopilot_20251204.log` - Autopilot log

**What to Look For**:
- ✅ "9:15 AM: Starting DRY-RUN Autopilot" (should appear at 9:15)
- ✅ Regular heartbeat updates
- ✅ Phase execution logs
- ❌ "ERROR" or "CRITICAL" messages

### Option 2: Check Heartbeat File
**Location**: `system3_daily_heartbeat.json`

**What to Check**:
- `timestamp` should be recent (< 2 minutes old during market hours)
- `status` should be "running"
- `autopilot_running` should be `true` after 9:15 AM

### Option 3: Check Signal Files
**Location**: `storage/live/`
- `angel_index_ai_signals.csv` - Should have new rows after 9:15 AM
- `angel_index_ai_signals_curated.csv` - Should update periodically

---

## ⚠️ Potential Issues & Solutions

### Issue 1: Shutdown Flag Blocks Start
**Symptom**: Autorun master exits immediately with "Shutdown flag detected"

**Solution**: 
- Check `system3_shutdown_flag.json`
- If `shutdown_date` is today, delete the file
- Restart autorun

**Your Status**: ✅ **OK** - Shutdown flag is from yesterday, not today

### Issue 2: Autopilot Doesn't Start at 9:15 AM
**Symptom**: System running but no autopilot start message

**Possible Causes**:
- System time is incorrect
- Not a weekday (Saturday/Sunday)
- Autopilot already running flag stuck

**Solution**: Check logs for error messages, verify system time

### Issue 3: Watchdog Keeps Restarting Master
**Symptom**: Master keeps crashing and restarting

**Solution**: 
- Check logs for error messages
- Watchdog will restart master during market hours (expected)
- If outside market hours, check shutdown flag

**Your Status**: ✅ **OK** - Watchdog will only restart during market hours (9:15 AM - 4:00 PM)

### Issue 4: No Signals Generated
**Symptom**: Autopilot running but no signals in CSV

**Possible Causes**:
- All signals are HOLD (expected with conservative thresholds)
- SmartAPI connection issue
- Data source unavailable

**Solution**: Check autopilot logs for specific errors

---

## 📊 Expected Timeline

| Time | Event | What Happens |
|------|-------|--------------|
| **7:24 AM** | You start autorun | Watchdog + Master start |
| **7:24-7:26 AM** | Pre-market phases | Phases 201-310 run |
| **7:26-9:15 AM** | Waiting period | System waits for market open |
| **9:15 AM** | Market opens | Autopilot starts automatically |
| **9:15 AM - 3:30 PM** | Market hours | Signals generate, phases run |
| **3:30 PM** | Archive signals | Signals archived |
| **3:35 PM** | EOD Learning | End-of-day learning runs |
| **4:00 PM** | Shutdown | Clean shutdown, flag written |

---

## ✅ Final Pre-Start Checklist

Before running `START_AUTORUN_AND_WATCHDOG.bat`:

- [x] ✅ Shutdown flag is from yesterday (not today)
- [x] ✅ Current time is 7:24 AM (before market open)
- [x] ✅ All critical files exist
- [x] ✅ Safety flags are correct (DRY-RUN)
- [x] ✅ Health check passed (from earlier)
- [x] ✅ Disk space sufficient (146.49 GB free)
- [x] ✅ Internet connectivity confirmed

**Status**: ✅ **ALL CHECKS PASS - READY TO START**

---

## 🚀 Start Command

**Double-click or run**:
```
START_AUTORUN_AND_WATCHDOG.bat
```

**Or from command line**:
```batch
cd C:\Genesis_System3
START_AUTORUN_AND_WATCHDOG.bat
```

---

## 📝 Post-Start Verification (Quick Check)

After starting, verify these within 1 minute:

1. **Two windows should be open**:
   - "System3 Watchdog" window (new window)
   - Autorun master window (current window)

2. **Both should show logs**:
   - Watchdog: "SYSTEM3 WATCHDOG - STARTING"
   - Master: "SYSTEM3 AUTORUN MASTER - STARTING"

3. **Master should show**:
   - "✓ All safety checks passed - DRY-RUN mode confirmed"
   - "Heartbeat thread started"
   - "PRE-MARKET: Running phases 201-310"

4. **No error messages** in either window

If all above are ✅, system is running correctly and will start autopilot at 9:15 AM automatically.

---

## 🎯 Summary

**Current Status**: ✅ **READY TO START**

**What Will Happen**:
1. System starts now (7:24 AM)
2. Pre-market phases run immediately
3. System waits until 9:15 AM
4. Autopilot starts automatically at 9:15 AM
5. Runs until 4:00 PM shutdown
6. Clean shutdown with flag written

**You Can Safely**:
- Leave the system running
- Close laptop (if configured to run on battery/sleep)
- Check logs later to verify everything worked

**System is autonomous and will handle everything automatically.**

---

**Guide Generated**: 2025-12-04 07:24 AM  
**Status**: ✅ **READY TO START - ALL SYSTEMS GO**

