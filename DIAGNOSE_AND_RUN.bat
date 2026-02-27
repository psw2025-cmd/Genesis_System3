@echo off
REM ====================================================================
REM COMPREHENSIVE DIAGNOSE AND RUN
REM ====================================================================

title Diagnose and Run Trading System

cd /d "%~dp0"

echo.
echo ====================================================================
echo   COMPREHENSIVE DIAGNOSTIC AND RUN
echo ====================================================================
echo.

REM Step 1: Kill existing
echo [1/6] Killing existing processes...
taskkill /F /FI "WINDOWTITLE eq Paper Trading Engine*" /T >nul 2>&1
timeout /t 1 /nobreak >nul
echo   [OK]
echo.

REM Step 2: Test Python
echo [2/6] Testing Python...
venv\Scripts\python.exe --version
if %ERRORLEVEL% NEQ 0 (
    echo   [ERROR] Python not found!
    pause
    exit /b 1
)
echo   [OK]
echo.

REM Step 3: Test script syntax
echo [3/6] Testing script syntax...
venv\Scripts\python.exe -m py_compile scripts\smart_live_chain_runner.py
if %ERRORLEVEL% NEQ 0 (
    echo   [ERROR] Syntax error in script!
    pause
    exit /b 1
)
echo   [OK]
echo.

REM Step 4: Test import
echo [4/6] Testing import...
venv\Scripts\python.exe -c "import sys; sys.path.insert(0, '.'); exec('try:\n from scripts.smart_live_chain_runner import SmartLiveChainRunner\n print(\"  [OK] Import successful\")\nexcept Exception as e:\n print(f\"  [ERROR] Import failed: {e}\")\n import traceback\n traceback.print_exc()\n')" 2>&1
echo.

REM Step 5: Run script for 10 seconds
echo [5/6] Running script for 10 seconds (test)...
echo   Starting in new window...
start "Test Run" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && echo Testing script... && timeout /t 2 /nobreak >nul && python -u scripts\smart_live_chain_runner.py --refresh 5 --market-check 30 --no-websocket && echo Script finished && pause"
timeout /t 12 /nobreak >nul
echo   [OK] Check the Test Run window
echo.

REM Step 6: Start full system
echo [6/6] Starting full AUTO_MODE system...
echo   This will open the Paper Trading Engine window
echo   Check that window for continuous output
echo.
timeout /t 3 /nobreak >nul

call AUTO_MODE.bat

echo.
echo ====================================================================
echo   DIAGNOSTIC COMPLETE
echo ====================================================================
echo.
echo Check the windows that opened:
echo   1. Test Run window - should show script output
echo   2. Paper Trading Engine window - should show continuous cycles
echo.
pause
