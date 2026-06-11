# 🔧 VENV RECOVERY GUIDE

**Purpose:** Step-by-step instructions to fix a broken venv when `START_AUTORUN_AND_WATCHDOG.bat` fails.

**When to use:** When you see errors like:
- `ModuleNotFoundError: No module named 'pandas'`
- `No module named 'psutil'`
- `Invalid distribution -ip`
- Venv sanity check fails with "FAIL"

---

## ⚠️ IMPORTANT: When to Stop & Call for Help

If you've followed these steps and the venv still won't work after 2 attempts, **do NOT continue**. This indicates a deeper system issue. Contact support.

---

## Step 1: Kill All Python Processes

This ensures no venv files are locked and can be safely deleted.

### Windows PowerShell (Recommended)
```powershell
# Kill all python.exe processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Verify they're gone
Get-Process python -ErrorAction SilentlyContinue
# (Should return nothing)

# Wait 2 seconds to ensure cleanup
Start-Sleep -Seconds 2
```

### Windows Command Prompt (Alternative)
```batch
taskkill /IM python.exe /F
timeout /t 2
```

### Verification
Open Task Manager (`Ctrl+Shift+Esc`) and search for "python". No processes should appear.

---

## Step 2: Delete the Broken Venv

```powershell
# Set the path
$VENV_PATH = "C:\Genesis_System3\venv"

# Delete with force
if (Test-Path $VENV_PATH) {
    Remove-Item -Path $VENV_PATH -Recurse -Force
    Write-Host "✅ Deleted: $VENV_PATH"
} else {
    Write-Host "⚠️  Venv not found at $VENV_PATH"
}

# Verify it's gone
if (Test-Path $VENV_PATH) {
    Write-Host "❌ FAILED: Venv still exists. Retry step 1 (kill python processes)."
} else {
    Write-Host "✅ Confirmed: Venv deleted."
}
```

---

## Step 3: Recreate the Venv

```powershell
# Navigate to project root
cd C:\Genesis_System3

# Create fresh venv
python -m venv venv

# Verify it was created
if (Test-Path "C:\Genesis_System3\venv\Scripts\python.exe") {
    Write-Host "✅ Venv created successfully at venv\Scripts\python.exe"
} else {
    Write-Host "❌ FAILED: Venv creation did not work."
    Write-Host "Ensure Python 3.10+ is installed and accessible."
    exit 1
}
```

**Troubleshooting:**
- If you see `error: 'python' is not recognized as an internal or external command`, Python is not in PATH.
  - Install Python 3.10+ from python.org (check "Add Python to PATH" during install).
  - Or use the full path: `C:\Python310\python.exe -m venv venv`

---

## Step 4: Install Critical Dependencies

```powershell
# Use the fresh venv python to install
$PIP = "C:\Genesis_System3\venv\Scripts\pip.exe"

Write-Host "Installing pandas..."
& $PIP install pandas

Write-Host "Installing psutil..."
& $PIP install psutil

Write-Host "Installing numpy..."
& $PIP install numpy

Write-Host "Installing additional deps from requirements.txt..."
& $PIP install -r requirements.txt

Write-Host "✅ Dependencies installed."
```

**If pip install fails:**
```powershell
# Upgrade pip itself first
& "C:\Genesis_System3\venv\Scripts\python.exe" -m pip install --upgrade pip

# Then retry the installs
```

---

## Step 5: Verify the Venv is Healthy

```powershell
# Run the sanity check tool
cd C:\Genesis_System3
python tools/system3_venv_sanity_check.py --report

# Expected output:
# ✅ PASS: Venv is healthy. Safe to start autorun + watchdog.
# Report written: C:\Genesis_System3\VENV_SANITY_STATUS.md
```

**If you see PASS:** ✅ Continue to Step 6.

**If you see FAIL:** ❌ Review `VENV_SANITY_STATUS.md` for details and contact support.

---

## Step 6: Start the System

```powershell
cd C:\Genesis_System3
.\START_AUTORUN_AND_WATCHDOG.bat
```

Expected output:
```
================================================
SYSTEM3 AUTORUN + WATCHDOG
================================================
One-click start | Fully autonomous | DRY-RUN enforced
================================================

================================================
PHASE 1: ENVIRONMENT VALIDATION AND AUTO-REPAIR
================================================

OK Virtual environment located
OK Virtual environment activated
OK Python environment ready
OK pandas present
OK psutil present
OK numpy present
OK joblib present
OK python-dotenv present
OK Core scripts present

...rest of phases...
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError" even after rebuild

**Cause:** Packages not installed correctly, or PATH issue.

**Solution:**
1. Verify pip is from venv:
   ```powershell
   C:\Genesis_System3\venv\Scripts\python.exe -m pip --version
   # Should show: pip X.Y.Z from C:\Genesis_System3\venv\lib\site-packages\pip
   ```

2. If path is wrong, pip is corrupted. Delete venv and restart from Step 2.

---

### Issue: "VIRTUAL_ENV not set"

**Cause:** The BAT file did not activate the venv correctly.

**Solution:**
1. Ensure `venv\Scripts\activate.bat` exists:
   ```powershell
   Test-Path C:\Genesis_System3\venv\Scripts\activate.bat
   # Should return True
   ```

2. If missing, the venv was not created properly. Restart from Step 2.

---

### Issue: "Delete venv fails with 'file in use'"

**Cause:** Python processes still holding locks.

**Solution:**
1. Run **Step 1** again more forcefully:
   ```powershell
   # Kill by process name
   taskkill /IM python.exe /F /T
   
   # Kill by PID (if you know it)
   Stop-Process -Id 1234 -Force
   
   # Wait longer
   Start-Sleep -Seconds 5
   ```

2. Check for any IDE windows (VS Code, PyCharm) keeping the venv open. Close them.

3. Retry Step 2.

---

### Issue: "Cannot create venv: 'python' not found"

**Cause:** Python not in system PATH.

**Solution:**
1. Install Python 3.10 or later from [python.org](https://www.python.org)
   - **Crucial:** Check "Add Python to PATH" during installation.

2. Verify Python is accessible:
   ```powershell
   python --version
   # Should show: Python 3.10.X or higher
   ```

3. Retry Step 3.

---

## Success Checklist

After completing all steps, verify:

- [ ] No `python.exe` processes in Task Manager
- [ ] `C:\Genesis_System3\venv\Scripts\python.exe` exists
- [ ] Sanity check passes: `VENV_SANITY_STATUS.md` shows ✅ PASS
- [ ] `START_AUTORUN_AND_WATCHDOG.bat` runs without errors
- [ ] Heartbeat file updates: `system3_daily_heartbeat.json` has recent timestamp
- [ ] Logs written: `logs\system3_autorun_master_*.log` contains entries

---

## Prevention

To avoid needing recovery in the future:

1. **Do NOT manually delete or modify `venv/`** unless following this guide.
2. **Do NOT use system python** for Genesis System3 scripts.
3. **Always use `START_AUTORUN_AND_WATCHDOG.bat`** to launch (never call Python manually).
4. **Monitor logs** regularly for warnings about missing dependencies.

---

## Questions or Issues?

If any step fails or is unclear, collect these files and contact support:
- `VENV_SANITY_STATUS.md` (latest report)
- `logs/system3_autorun_master_*.log` (latest log)
- `state/venv_sanity_check.json` (technical details)
- Screenshot of the error message

---

**Last Updated:** 2025-12-08  
**Applicable To:** System3 Autorun + Watchdog
