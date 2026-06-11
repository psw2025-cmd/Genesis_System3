@echo off
REM ====================================================================
REM FORCE RESTART AND VERIFY - Kill stuck processes and restart fresh
REM ====================================================================

title Force Restart and Verify

cd /d "%~dp0"

echo.
echo ====================================================================
echo   FORCE RESTART AND VERIFY
echo ====================================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

echo [STEP 1] Killing any stuck Python processes...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul
echo [OK] Processes killed
echo.

echo [STEP 2] Starting trading system fresh...
echo.

call venv\Scripts\activate.bat

if not exist "outputs" mkdir outputs

REM Start trading system in new window
start "Trading System" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python scripts\smart_live_chain_runner.py --refresh 5 --market-check 30 --no-websocket"

echo [OK] Trading system started in separate window
echo.

echo [STEP 3] Waiting for initialization (30 seconds)...
timeout /t 30 /nobreak >nul
echo.

echo [STEP 4] Verifying files are updating...
echo.

REM Check if file exists and get initial timestamp
if not exist "outputs\chain_raw_live.csv" (
    echo [ERROR] chain_raw_live.csv not found after 30 seconds
    echo [ACTION] Check Trading System window for errors
    pause
    exit /b 1
)

for %%F in ("outputs\chain_raw_live.csv") do set "INITIAL_TIME=%%~tF"
echo [INFO] Initial file time: %INITIAL_TIME%
echo [INFO] Monitoring for 15 seconds...
echo.

timeout /t 15 /nobreak >nul

REM Check if updated
for %%F in ("outputs\chain_raw_live.csv") do (
    if "%%~tF" NEQ "%INITIAL_TIME%" (
        echo.
        echo ====================================================================
        echo   ✅ SUCCESS - SYSTEM IS WORKING!
        echo ====================================================================
        echo.
        echo [RESULT] File updated during monitoring period
        echo [TIME] New timestamp: %%~tF
        echo [SIZE] %%~zF bytes
        echo.
        echo System is now updating files correctly!
        echo.
    ) else (
        echo.
        echo ====================================================================
        echo   ⚠️  WARNING - SYSTEM NOT UPDATING
        echo ====================================================================
        echo.
        echo [RESULT] File did NOT update in 15 seconds
        echo [TIME] Still at: %%~tF
        echo.
        echo [TROUBLESHOOTING]
        echo   1. Check "Trading System" window for error messages
        echo   2. Look for API connection errors
        echo   3. System may need more time - wait another 30 seconds
        echo   4. If market is closed, virtual data may update slower
        echo.
        echo [ACTION] Check the Trading System window now!
        echo.
    )
)

echo ====================================================================
echo.
pause
