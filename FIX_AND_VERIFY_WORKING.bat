@echo off
REM ====================================================================
REM FIX AND VERIFY WORKING - Complete fix with verification
REM ====================================================================

title Fix and Verify Working

cd /d "%~dp0"

echo.
echo ====================================================================
echo   FIXING SYSTEM - KILLING STUCK PROCESSES
echo ====================================================================
echo.

REM Kill all Python processes
echo [1/5] Killing all Python processes...
taskkill /F /IM python.exe /T 2>nul
timeout /t 3 /nobreak >nul
echo [OK] All processes killed
echo.

REM Activate venv
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

if not exist "outputs" mkdir outputs

echo [2/5] Starting trading system with verbose logging...
echo.

REM Start with explicit output redirection to see what's happening
start "Trading System - VERBOSE" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python scripts\smart_live_chain_runner.py --refresh 5 --market-check 30 --no-websocket 2>&1 | more"

echo [OK] Trading system started
echo [INFO] Check the "Trading System - VERBOSE" window for activity
echo.

echo [3/5] Waiting for initialization (45 seconds)...
echo [INFO] System needs time to:
echo        - Connect to broker API
echo        - Initialize expiries
echo        - Start first data fetch
echo.
timeout /t 45 /nobreak >nul
echo.

echo [4/5] Checking if files exist...
if not exist "outputs\chain_raw_live.csv" (
    echo [WARNING] chain_raw_live.csv not found yet
    echo [ACTION] Check Trading System window for errors
    echo [ACTION] Wait 30 more seconds and check again
    goto :verify
)

echo [OK] chain_raw_live.csv exists
echo.

:verify
echo [5/5] Verifying files are updating (15 seconds)...
echo.

REM Get initial timestamp
for %%F in ("outputs\chain_raw_live.csv") do (
    set "INITIAL_TIME=%%~tF"
    set "INITIAL_SIZE=%%~zF"
    echo [INFO] Initial state: %%~tF, %%~zF bytes
)

echo [INFO] Monitoring for 15 seconds...
timeout /t 15 /nobreak >nul

REM Check if updated
for %%F in ("outputs\chain_raw_live.csv") do (
    if "%%~tF" NEQ "%INITIAL_TIME%" (
        echo.
        echo ====================================================================
        echo   ✅ SUCCESS - SYSTEM IS WORKING!
        echo ====================================================================
        echo.
        echo [RESULT] File updated during monitoring
        echo [TIME]   %%~tF (was %INITIAL_TIME%)
        echo [SIZE]   %%~zF bytes (was %INITIAL_SIZE% bytes)
        echo.
        echo System is now updating files correctly!
        echo You can now run the monitor to verify everything works.
        echo.
    ) else (
        echo.
        echo ====================================================================
        echo   ⚠️  SYSTEM NOT UPDATING YET
        echo ====================================================================
        echo.
        echo [RESULT] File did NOT update in 15 seconds
        echo [TIME]   Still at: %%~tF
        echo.
        echo [TROUBLESHOOTING]
        echo   1. Check "Trading System - VERBOSE" window
        echo   2. Look for error messages (API errors, connection errors)
        echo   3. If you see "Fetching data..." messages, system is working
        echo   4. If window is blank, system may be stuck
        echo   5. Wait 30 more seconds - initialization can take time
        echo.
        echo [ACTION] Check the Trading System window NOW!
        echo          Look for messages like:
        echo          - "Fetching data for NIFTY..."
        echo          - "Exported X contracts..."
        echo          - "Cycle completed"
        echo.
    )
)

echo ====================================================================
echo.
echo [NEXT STEPS]
echo   1. Check the "Trading System - VERBOSE" window
echo   2. If you see activity, wait 30 more seconds
echo   3. Run CHECK_STATUS_NOW.bat again to verify
echo   4. If still not working, check for API errors in the window
echo.
pause
