# 🔄 SYSTEM3 RESTART GUIDE - ULTRA MODEL FIX ACTIVATION

**Date**: 2025-12-08  
**Purpose**: Restart System3 to activate Ultra Model fix (40 features)  
**Expected Impact**: Fix Warning #3 (79% HOLD → ~50% HOLD)  
**Safety**: DRY-RUN mode, no real money risk

---

## 📋 QUICK START (3 STEPS)

### Step 1: Stop Current Autorun

If System3 autorun is currently running:

```
Press Ctrl+C in the terminal window
```

Wait for graceful shutdown (5-10 seconds)

### Step 2: Restart System3

Double-click or run:

```
SYSTEM3_DAILY_START.bat
```

Then select **Option 2** (Autorun Master)

### Step 3: Verify Fix Loaded

After next signal cycle (~30 min), run:

```
python check_fix_status.py
```

---

## 🔍 DETAILED RESTART PROCEDURE

### Pre-Restart Checklist

- [ ] Current autorun is running (if not, skip to restart)
- [ ] Note current time for next signal cycle
- [ ] Backup current logs (optional)

### Restart Steps

#### 1. **STOP CURRENT AUTORUN**

**If running in terminal:**

```
Press Ctrl+C
```

**If running as background process:**

```powershell
# Find process
tasklist | findstr python

# Kill process (replace PID)
taskkill /PID <process_id> /F
```

**Verify stopped:**

```powershell
tasklist | findstr python
# Should show no system3 processes
```

#### 2. **LAUNCH SYSTEM3**

**Option A: Using Batch File (Recommended)**

```
Double-click: SYSTEM3_DAILY_START.bat
Select: [2] Autorun Master
```

**Option B: Manual PowerShell**

```powershell
cd C:\Genesis_System3
.\venv\Scripts\Activate.ps1
python system3_autorun_master.py
```

**Option C: Using Alternative Batch**

```
DIAGNOSE_AND_RUN.bat
```

#### 3. **MONITOR STARTUP LOGS**

Watch for these messages in the terminal:

✅ **SUCCESS INDICATORS:**

```
[INFO] System3 Autorun Master starting...
[INFO] DRY-RUN mode active
[INFO] Waiting for next signal cycle...
```

❌ **ERROR INDICATORS:**

```
[ERROR] Failed to start
[ERROR] Import error
[ERROR] Configuration error
```

#### 4. **WAIT FOR NEXT SIGNAL CYCLE**

Signal cycles run every **30 minutes**:

- 09:15, 09:45, 10:15, 10:45, 11:15, 11:45
- 12:15, 12:45, 13:15, 13:45, 14:15, 14:45
- 15:15 (last cycle)

**Current time**: Check clock  
**Next cycle**: Wait for next :15 or :45 minute mark

#### 5. **VERIFY ULTRA MODEL FIX LOADED**

After signal cycle completes, run verification:

```powershell
python check_fix_status.py
```

**Expected Output:**

```
✅ ULTRA MODEL FIX VERIFICATION
================================

Signal Engine Status:
  ✅ Ultra Model features: LOADED (40 features)
  ✅ Feature count: 114 (was 74)
  ✅ Using: ULTRA_MODEL (not DELTA_FALLBACK)

Signal Distribution:
  HOLD: 45-55% (was 79%) ✅ IMPROVED
  SELL: 22-28% (was 14%)
  BUY: 22-28% (was 7%)

Verdict: ✅ FIX SUCCESSFULLY ACTIVATED
```

---

## 🎯 VERIFICATION CHECKLIST

### Immediate Verification (Right After Restart)

- [ ] **Process Running**

  ```powershell
  tasklist | findstr python
  # Should show python.exe process
  ```

- [ ] **Logs Being Written**

  ```powershell
  dir /O-D logs\
  # Should show recent log files
  ```

- [ ] **Heartbeat Active**

  ```powershell
  python -c "import json; print(json.load(open('system3_daily_heartbeat.json'))['status'])"
  # Should show: RUNNING
  ```

### Post-Signal-Cycle Verification (After 30 min)

- [ ] **New Signals Generated**

  ```powershell
  dir /O-D storage\live\angel_index_ai_signals_production.csv
  # Check timestamp is recent
  ```

- [ ] **Ultra Features Present**

  ```powershell
  python verify_ultra_features.py
  # Should show 40 Ultra features
  ```

- [ ] **Signal Distribution Improved**

  ```powershell
  python check_fix_status.py
  # HOLD should be < 60% (was 79%)
  ```

- [ ] **Logs Show Ultra Model Usage**

  ```powershell
  findstr /C:"USING_ULTRA_MODEL" logs\*.log
  # Should find matches
  ```

---

## 📊 EXPECTED IMPROVEMENTS

### Before Restart (OLD CODE)

```
Signal Distribution:
  HOLD: 79% ❌ Too high
  SELL: 14%
  BUY: 7%

Features: 74 columns
Model: DELTA_FALLBACK (degraded mode)
Warnings: Feature mismatch errors
```

### After Restart (NEW CODE)

```
Signal Distribution:
  HOLD: 45-55% ✅ Balanced
  SELL: 22-28%
  BUY: 22-28%

Features: 114 columns (74 + 40 Ultra)
Model: ULTRA_MODEL (full mode)
Warnings: None
```

---

## 🚨 TROUBLESHOOTING

### Issue 1: Restart Fails to Start

**Symptoms:**

- Batch file exits immediately
- Python errors on startup
- Import errors

**Solutions:**

```powershell
# Check virtual environment
.\venv\Scripts\Activate.ps1
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
where python
```

### Issue 2: Ultra Features Not Loading

**Symptoms:**

- Still seeing DELTA_FALLBACK in logs
- Feature count still 74
- HOLD % still 79%

**Solutions:**

```powershell
# Verify patch was applied
python verify_ultra_features.py

# Re-apply patch if needed
python fix_ultra_model_feature_mismatch.py

# Force restart
taskkill /F /IM python.exe
SYSTEM3_DAILY_START.bat
```

### Issue 3: Signal Cycle Not Running

**Symptoms:**

- No new signals after 30 min
- Logs show "Waiting..."
- CSV files not updating

**Solutions:**

```powershell
# Check market hours (9:15 AM - 3:30 PM IST)
# Check if it's a trading day (Mon-Fri, not holiday)

# Force manual signal generation
python system3_production_pipeline_clean.py

# Check kill switch
type config\kill_switch.json
# Should show: {"enabled": false}
```

### Issue 4: High Memory/CPU Usage

**Symptoms:**

- System slow after restart
- Multiple Python processes
- High RAM usage

**Solutions:**

```powershell
# Kill duplicate processes
tasklist | findstr python
taskkill /F /IM python.exe

# Restart cleanly
SYSTEM3_DAILY_START.bat
```

---

## 📝 POST-RESTART MONITORING

### First Hour After Restart

Monitor these metrics:

1. **Signal Generation** (every 30 min)
   - Check CSV timestamp updates
   - Verify signal count (should be ~100 per cycle)

2. **Feature Count**
   - Run: `python verify_ultra_features.py`
   - Should show 114 features (74 + 40)

3. **Signal Distribution**
   - Run: `python check_fix_status.py`
   - HOLD should drop from 79% to ~50%

4. **Error Logs**
   - Check: `logs\*.log`
   - Should NOT see "Feature mismatch" errors

### First Day After Restart

Track these improvements:

1. **Signal Quality**
   - HOLD %: Target 45-55% (was 79%)
   - BUY %: Target 22-28% (was 7%)
   - SELL %: Target 22-28% (was 14%)

2. **Order Approval Rate**
   - Rejection rate: Target < 30% (was 37.8%)
   - Approved orders: Target > 70%

3. **Model Performance**
   - Using ULTRA_MODEL: 100% of time
   - Using DELTA_FALLBACK: 0% of time

---

## ✅ SUCCESS CRITERIA

### Restart is Successful If

- [x] System3 autorun process is running
- [x] Logs show "USING_ULTRA_MODEL" (not FALLBACK)
- [x] Feature count is 114 (not 74)
- [x] HOLD % drops below 60% (from 79%)
- [x] No "Feature mismatch" errors in logs
- [x] Signals generated every 30 minutes
- [x] CSV files updating with recent timestamps

### Fix is Activated If

- [x] Signal distribution improved (HOLD < 60%)
- [x] Ultra features present in signals CSV
- [x] Model using ULTRA_MODEL mode
- [x] Warning #3 resolved (signal imbalance)

---

## 🔗 RELATED DOCUMENTS

- **Ultra Model Fix Details**: `ULTRA_MODEL_FEATURE_FIX_SUMMARY.md`
- **4 Warnings Analysis**: `4_WARNINGS_DETAILED_BREAKDOWN.md`
- **Restart Required**: `RESTART_REQUIRED.md`
- **Verification Script**: `check_fix_status.py`
- **Feature Verification**: `verify_ultra_features.py`

---

## 📞 QUICK REFERENCE COMMANDS

```powershell
# Stop autorun
Ctrl+C (in terminal)

# Restart
SYSTEM3_DAILY_START.bat → Option 2

# Verify fix
python check_fix_status.py

# Check logs
dir /O-D logs\

# Check signals
dir /O-D storage\live\*.csv

# Check process
tasklist | findstr python

# Force kill
taskkill /F /IM python.exe
```

---

**Status**: Ready for restart  
**Next Action**: Stop current autorun → Restart → Verify  
**Timeline**: 5 min restart + 30 min wait + 2 min verify = ~37 min total
