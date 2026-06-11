# Dashboard Quick Start Guide

## 🚀 One-Click Start

**Just double-click:** `START_FULL_DASHBOARD_SYSTEM.bat`

That's it! The script does everything automatically.

---

## ✅ What The Script Does Automatically

### 1. Pre-Checks
- ✅ Checks Python is installed
- ✅ Checks Node.js is installed
- ✅ Checks npm is available
- ✅ Verifies virtual environment exists

### 2. Auto-Fixes
- ✅ Creates virtual environment if missing
- ✅ Installs all Python dependencies
- ✅ Installs all frontend dependencies
- ✅ Fixes data issues (spot prices, etc.)
- ✅ Updates CORS configuration
- ✅ Verifies all files exist

### 3. Starts Services
- ✅ Starts backend API (port 8000)
- ✅ Starts frontend dashboard (port 3000)
- ✅ Optionally starts trading system
- ✅ Opens dashboard in Chrome

### 4. Verification
- ✅ Verifies backend is responding
- ✅ Verifies frontend is responding
- ✅ Shows status of all services

---

## 📋 Usage Options

### Option 1: Dashboard Only (Default)
```batch
START_FULL_DASHBOARD_SYSTEM.bat
```
Starts backend + frontend only.

### Option 2: With Trading System
```batch
START_FULL_DASHBOARD_SYSTEM.bat --with-trading
```
Starts backend + frontend + trading system.

---

## 🔄 Updating The System

**To update all dependencies:**
```batch
UPDATE_DASHBOARD_SYSTEM.bat
```

This will:
- ✅ Update all Python packages
- ✅ Update all npm packages
- ✅ Run auto-fix script
- ✅ Verify everything works

---

## 🛠️ Manual Steps (If Needed)

The script handles everything, but if you need to do something manually:

### Start Backend Only
```powershell
cd C:\Genesis_System3\dashboard\backend
..\..\venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### Start Frontend Only
```powershell
cd C:\Genesis_System3\dashboard\frontend
npm run dev -- --host 0.0.0.0
```

### Start Trading System
```powershell
cd C:\Genesis_System3
.\venv\Scripts\python.exe option_chain_automation_master.py --sim --cycles 10
```

---

## 📊 What You'll See

### After Running The Script:

1. **Minimized Windows** (check taskbar):
   - "Dashboard Backend" - Backend API server
   - "Dashboard Frontend" - Frontend dev server
   - "Trading System" - (if started with --with-trading)

2. **Chrome Opens**:
   - Dashboard at http://localhost:3000
   - All tabs working
   - Real-time data updating

3. **Console Output**:
   - All checks passed
   - Services started
   - Status verified

---

## ⚠️ Troubleshooting

### Script Says "Python not found"
**Fix:** Install Python 3.10+ from https://www.python.org/

### Script Says "Node.js not found"
**Fix:** Install Node.js 18+ from https://nodejs.org/

### Port Already In Use
**Fix:** 
- Close the window using that port
- Or restart your computer
- Script will detect and warn you

### Dependencies Fail to Install
**Fix:**
- Check internet connection
- Run: `UPDATE_DASHBOARD_SYSTEM.bat`
- Or manually: `.\venv\Scripts\pip.exe install -r dashboard\backend\requirements.txt`

### Dashboard Doesn't Open
**Fix:**
- Manually open: http://localhost:3000
- Check if services are running (taskbar)
- Check logs in `logs\dashboard_startup_*.log`

---

## 🔍 Logs

All startup activities are logged to:
```
logs\dashboard_startup_YYYYMMDD_HHMMSS.log
```

Check this file if something doesn't work.

---

## 🎯 Summary

**Just run:** `START_FULL_DASHBOARD_SYSTEM.bat`

**Everything else is automatic!** 🚀

The script:
- ✅ Checks everything
- ✅ Fixes issues
- ✅ Installs dependencies
- ✅ Starts services
- ✅ Opens dashboard

**No manual steps needed!**
