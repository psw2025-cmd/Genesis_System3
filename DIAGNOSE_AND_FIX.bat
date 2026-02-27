@echo off
REM ====================================================================
REM DIAGNOSE AND FIX - Check what's wrong and fix it
REM ====================================================================

title Diagnose and Fix

cd /d "%~dp0"

echo.
echo ====================================================================
echo   DIAGNOSE AND FIX SYSTEM
echo ====================================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

if not exist "outputs" mkdir outputs

echo [STEP 1] Checking current file status...
echo.

venv\Scripts\python.exe scripts\check_system_status.py

echo.
echo [STEP 2] Checking for running Python processes...
echo.

tasklist /FI "IMAGENAME eq python.exe" /FO TABLE

echo.
echo [STEP 3] Recommendations:
echo.
echo If files are STALE or NOT UPDATING:
echo   1. Close any existing "Trading System" windows
echo   2. Run FULL_SYSTEM_RUN_AND_MONITOR.bat again
echo   3. Wait for files to start updating (should happen within 60 seconds)
echo.
echo If system appears stuck:
echo   1. Check the "Trading System" window for error messages
echo   2. Look for API connection errors
echo   3. Verify market hours (system uses virtual data when market closed)
echo.
pause
