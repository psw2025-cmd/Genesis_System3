@echo off
REM ====================================================================
REM FULL SYSTEM RUN AND MONITOR - MICRO LEVEL
REM Starts system, monitors everything, finds issues, provides proof
REM ====================================================================

title Full System Run and Monitor

cd /d "%~dp0"

echo.
echo ====================================================================
echo   FULL SYSTEM RUN AND MONITOR - MICRO LEVEL
echo ====================================================================
echo.
echo This will:
echo   1. Start trading system in background
echo   2. Monitor all components continuously
echo   3. Check for warnings/errors
echo   4. Verify data updates automatically
echo   5. Test auto-triggers
echo   6. Show proof everything works
echo.
echo Monitoring Duration: 10 minutes
echo.
pause

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs

echo.
echo [STEP 1] Starting trading system...
echo.

REM Start trading system in background (new window)
start "Trading System" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python scripts\smart_live_chain_runner.py --refresh 5 --market-check 30 --no-websocket"

echo [INFO] Trading system started in separate window
echo [INFO] Waiting for initialization (20 seconds)...
timeout /t 20 /nobreak >nul

echo.
echo [STEP 2] Starting micro-level monitoring...
echo [INFO] This will monitor for 10 minutes and check everything
echo.

venv\Scripts\python.exe scripts\simple_micro_monitor.py

echo.
echo ====================================================================
echo   MONITORING COMPLETE
echo ====================================================================
echo.
echo Check the outputs directory for any reports
echo.
pause
