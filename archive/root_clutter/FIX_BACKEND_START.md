# Fix: Backend Start Issue

## Problem

The batch script `RESTART_WITH_SSOT.bat` was failing with:
- "The system cannot find the path specified"
- "ERROR: Error loading ASGI app. Could not import module 'app'"

## Root Cause

The `start` command in batch files doesn't preserve the directory context. When starting a new command window, it was running from `C:\Windows\system32` instead of the backend directory.

## Solution

Fixed the batch script to:
1. Use `pushd`/`popd` to properly change directories
2. Store the backend directory path in a variable
3. Use the full path in the `start` command

## Updated Script

The script now:
- Changes to the project root first (`cd /d "%~dp0"`)
- Verifies `dashboard\backend\app.py` exists
- Uses `pushd` to change to backend directory
- Starts uvicorn with the correct working directory
- Uses `popd` to return to project root

## How to Use

1. **Double-click:** `RESTART_WITH_SSOT.bat`
   - Or run from command prompt

2. **The script will:**
   - Kill existing backend processes
   - Clear port 8000
   - Start backend in the correct directory
   - Wait for initialization
   - Verify backend is running

3. **If it still fails:**
   - Check that `dashboard\backend\app.py` exists
   - Verify Python is in PATH
   - Check that uvicorn is installed: `pip install uvicorn[standard]`

## Manual Start (Alternative)

If the batch script still doesn't work, start manually:

```bash
cd C:\Genesis_System3\dashboard\backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Verification

After starting, check:
- Backend window shows: "Uvicorn running on http://0.0.0.0:8000"
- No import errors
- Can access: http://localhost:8000/api/state

---

**Status:** ✅ Fixed
