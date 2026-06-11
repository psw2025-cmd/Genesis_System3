# Paper Trading Setup Validation Checklist

Run this checklist to confirm everything is ready for paper trading on live market hours.

## Pre-Start Validation

### ✓ Step 1: Verify Configuration Flags
```powershell
# Run this command:
python -c "from config.live_trade_config import LIVE_TRADING_ENABLED, USE_LIVE_EXECUTION_ENGINE; print(f'LIVE={LIVE_TRADING_ENABLED}, EXEC_ENGINE={USE_LIVE_EXECUTION_ENGINE}')"

# Expected output:
# LIVE=False, EXEC_ENGINE=False

# If you see True for either → STOP, do not proceed
```

**Expected**: Both False ✓

### ✓ Step 2: Verify Python Environment
```powershell
# Check Python version
python --version

# Expected: Python 3.10.x or higher ✓
```

### ✓ Step 3: Check Required Directories Exist
```powershell
# These directories should exist:
Test-Path storage/live
Test-Path storage/meta
Test-Path storage/logs
Test-Path logs
Test-Path core/engine
Test-Path core/validation

# All should return: True
```

**Expected**: All return True ✓

### ✓ Step 4: Verify Signal Configuration
```powershell
# Thresholds file should exist:
Test-Path storage/meta/system3_live_thresholds.json

# Should return: True
```

**Expected**: True ✓

### ✓ Step 5: Run Pre-Market Validation
```powershell
# This tests the entire paper trading pipeline:
python core/validation/pre_market_signal_dryrun.py

# Should show:
# ✓ Thresholds loaded
# ✓ Signals available
# ✓ Safety checks passed
```

**Expected**: All checks pass ✓

### ✓ Step 6: Verify Execution Bridge
```powershell
# Test Phase 106 (Paper Trading Engine):
python -c "from core.engine.system3_phase106_dryrun_execution_bridge import run_phase106; result = run_phase106(); print(f\"Status: {result['status']}, Details: {result['details']}\")"

# Should show:
# Status: OK or WARN (depends on ledger data)
```

**Expected**: OK or WARN (not ERROR) ✓

### ✓ Step 7: Run Full Startup Verification
```powershell
python system3_startup_verification.py

# Should show:
# ✅ LIVE_TRADING_ENABLED: False (DRY-RUN mode)
# ✅ USE_LIVE_EXECUTION_ENGINE: False (DRY-RUN mode)
# ✅ STARTUP VERIFICATION: READY TO START
```

**Expected**: All checks pass ✓

---

## Configuration Review

### ✓ Step 8: Verify Config File Content

Open and review: `config/live_trade_config.py`

Should contain:
```python
LIVE_TRADING_ENABLED = False           # ← This MUST be False
USE_LIVE_EXECUTION_ENGINE = False      # ← This MUST be False
```

**Expected**: Both False ✓

### ✓ Step 9: Check Trade Limits
In `config/live_trade_config.py`, verify reasonable limits:

```python
MAX_LIVE_TRADES_PER_DAY = 10           # ← Reasonable for testing
MAX_LIVE_TRADES_PER_UNDERLYING = 3     # ← Prevents concentration
MAX_RISK_PER_TRADE_RUPEES = 2000       # ← Conservative for paper testing
```

**Expected**: Limits are conservative ✓

### ✓ Step 10: Verify Market Timings

In `config/live_trade_config.py`, should show:
```python
MARKET_OPEN_TIME = "09:15"
MARKET_CLOSE_TIME = "15:30"
```

**Expected**: Matches NSE market hours ✓

---

## Environment & Dependencies

### ✓ Step 11: Verify venv is Activated
```powershell
# You should see (venv) in your PowerShell prompt
# Or check:
pip list | Select-String pandas,numpy,scikit-learn

# Should show these packages installed
```

**Expected**: venv is active, packages installed ✓

### ✓ Step 12: Check Log Directory Permissions
```powershell
# Should be able to create logs:
New-Item -Path logs -Name test_write.txt -ItemType File
Remove-Item -Path logs/test_write.txt -Force

# Should succeed without errors
```

**Expected**: Can write to logs directory ✓

### ✓ Step 13: Check Storage Directory Permissions
```powershell
# Should be able to create files:
New-Item -Path storage/live -Name test_write.csv -ItemType File
Remove-Item -Path storage/live/test_write.csv -Force

# Should succeed without errors
```

**Expected**: Can write to storage directory ✓

---

## Paper Trading Specifics

### ✓ Step 14: Verify Phase 106 Path
```powershell
# Paper trading execution bridge should exist:
Test-Path core/engine/system3_phase106_dryrun_execution_bridge.py

# Should return: True
```

**Expected**: True ✓

### ✓ Step 15: Verify Phase 107 Path (Should be skipped)
```powershell
# Live trading engine should exist (but won't run):
Test-Path core/engine/system3_phase107_live_execution_engine.py

# Should return: True (exists but won't execute)
```

**Expected**: True ✓

---

## Final Pre-Start Check

### ✓ Step 16: Complete System Readiness
```powershell
python system3_startup_verification.py

# Final output should be:
# ============================================================
# ✅ STARTUP VERIFICATION: READY TO START
# ============================================================
# You can now run: START_AUTORUN_AND_WATCHDOG.bat
# Expected behavior:
# 1. Watchdog will start in a new window
# 2. Autorun master will start in current window
# 3. Pre-market phases will run
# 4. System will wait until 9:15 AM (or start immediately if market open)
```

**Expected**: "READY TO START" message ✓

---

## Quick Verification Script

Run this all-in-one check:

```powershell
# Save as: check_paper_trading.ps1

Write-Host "=== PAPER TRADING SETUP VALIDATION ===" -ForegroundColor Green
Write-Host ""

# Check 1: Config flags
Write-Host "1. Checking config flags..." -ForegroundColor Cyan
$result = python -c "from config.live_trade_config import LIVE_TRADING_ENABLED, USE_LIVE_EXECUTION_ENGINE; print(f'{LIVE_TRADING_ENABLED},{USE_LIVE_EXECUTION_ENGINE}')" 2>$null
$flags = $result -split ','
if ($flags[0] -eq 'False' -and $flags[1] -eq 'False') {
    Write-Host "   ✓ Config flags correct (LIVE=False, EXEC_ENGINE=False)" -ForegroundColor Green
} else {
    Write-Host "   ✗ Config flags WRONG! Do not proceed." -ForegroundColor Red
    exit 1
}

# Check 2: Directories
Write-Host "2. Checking required directories..." -ForegroundColor Cyan
$dirs = @('storage/live', 'storage/meta', 'storage/logs', 'logs', 'core/engine', 'core/validation')
$allExist = $true
foreach ($dir in $dirs) {
    if (Test-Path $dir) {
        Write-Host "   ✓ $dir" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $dir MISSING" -ForegroundColor Red
        $allExist = $false
    }
}
if (-not $allExist) { exit 1 }

# Check 3: Thresholds
Write-Host "3. Checking configuration files..." -ForegroundColor Cyan
if (Test-Path storage/meta/system3_live_thresholds.json) {
    Write-Host "   ✓ Thresholds configured" -ForegroundColor Green
} else {
    Write-Host "   ✗ Thresholds missing" -ForegroundColor Red
    exit 1
}

# Check 4: Phase files
Write-Host "4. Checking phase implementations..." -ForegroundColor Cyan
if (Test-Path core/engine/system3_phase106_dryrun_execution_bridge.py) {
    Write-Host "   ✓ Phase 106 (Paper Trading) exists" -ForegroundColor Green
} else {
    Write-Host "   ✗ Phase 106 missing" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== ✓ ALL CHECKS PASSED ===" -ForegroundColor Green
Write-Host "You can now run: .\START_AUTORUN_AND_WATCHDOG.bat" -ForegroundColor Green
```

Run it:
```powershell
PowerShell -ExecutionPolicy Bypass -File check_paper_trading.ps1
```

---

## After Starting Paper Trading

### ✓ Step 17: Monitor First Run
1. Start the system: `.\START_AUTORUN_AND_WATCHDOG.bat`
2. Watch for: "✓ All safety checks passed - DRY-RUN mode confirmed"
3. Watch for: "Waiting for market open..." or "Market hours detected"
4. If error: Check `logs/system3_master_*.log`

### ✓ Step 18: Monitor Execution
1. Watch `logs/phase106_dryrun_execution.log` for trade simulation
2. Check `storage/live/live_orders_ledger.csv` for order tracking
3. Confirm simulated trades are appearing

### ✓ Step 19: Validation Success Criteria
- ✓ System starts without errors
- ✓ "DRY-RUN mode confirmed" message appears
- ✓ Phase 106 executes during market hours
- ✓ Simulated orders appear in ledger
- ✓ No real orders sent to broker
- ✓ System shuts down gracefully at 4:00 PM

---

## Troubleshooting

### Issue: "LIVE_TRADING_ENABLED is True"
**Fix**: Edit `config/live_trade_config.py` and set `LIVE_TRADING_ENABLED = False`

### Issue: "USE_LIVE_EXECUTION_ENGINE is True"
**Fix**: Edit `config/live_trade_config.py` and set `USE_LIVE_EXECUTION_ENGINE = False`

### Issue: "Thresholds file not found"
**Fix**: Run Phase 223 to generate thresholds:
```powershell
python core/engine/system3_phase223_thresholds_generator.py
```

### Issue: "Pre-market validation failed"
**Fix**: Run manually to diagnose:
```powershell
python core/validation/pre_market_signal_dryrun.py
```

### Issue: "Cannot write to logs"
**Fix**: Check folder permissions:
```powershell
# Get full control
icacls logs /grant $env:USERNAME:(F) /t
icacls storage /grant $env:USERNAME:(F) /t
```

---

## Summary

| Check | Status | Action |
|-------|--------|--------|
| Config flags | LIVE=False, EXEC=False | ✓ Done |
| Directories exist | All 6 present | ✓ Done |
| Thresholds configured | File exists | ✓ Done |
| Phase 106 available | File exists | ✓ Done |
| Python environment | 3.10+ with venv | ✓ Done |
| Permissions | Can write logs/storage | ✓ Done |
| Startup verification | All pass | ✓ Done |

✅ **System is ready for paper trading on live market hours!**

---

**Next**: Run `.\START_AUTORUN_AND_WATCHDOG.bat` during market hours (9:15 AM - 3:30 PM)
