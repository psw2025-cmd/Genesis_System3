# Quick Fix: Backend Start Issue ✅

## Problem Fixed

The batch script was failing because the `start` command wasn't preserving the working directory. 

## ✅ Solution Applied

Updated `RESTART_WITH_SSOT.bat` to:
1. Use `pushd`/`popd` for proper directory handling
2. Store backend directory path before starting
3. Use full path in the `start` command

## 🚀 Try Again

**Run the fixed script:**
```bash
RESTART_WITH_SSOT.bat
```

**Or start manually:**
```bash
cd C:\Genesis_System3\dashboard\backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## ✅ What Should Happen

1. Script changes to project root
2. Kills existing processes
3. Clears port 8000
4. Changes to `dashboard\backend` directory
5. Starts uvicorn with correct working directory
6. Backend window shows: "Uvicorn running on http://0.0.0.0:8000"

## 🔍 Verify It Works

After starting, check:
- ✅ No "Could not import module 'app'" error
- ✅ Backend shows "Uvicorn running on http://0.0.0.0:8000"
- ✅ Can access: http://localhost:8000/api/state
- ✅ SSOT endpoint returns JSON

---

**The script is now fixed. Try running it again!**
