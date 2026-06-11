@echo off
REM ====================================================================
REM MICRO-LEVEL MONITOR - Runs system and monitors everything
REM ====================================================================

title Micro-Level Monitor

cd /d "%~dp0"

echo.
echo ====================================================================
echo   MICRO-LEVEL MONITORING SYSTEM
echo   Monitoring all components, data flow, and auto-triggers
echo ====================================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs

echo [INFO] Starting smart trading engine first...
echo [INFO] This will run in background to generate data
echo.

REM Start smart trading engine in background (visible window)
start "Paper Trading Engine" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python scripts\smart_live_chain_runner.py --refresh 5 --market-check 30 --no-websocket"

echo [INFO] Waiting for system to initialize (15 seconds)...
timeout /t 15 /nobreak >nul

echo.
echo [INFO] Starting micro-level monitoring...
echo [INFO] This will monitor for 5 minutes and check everything
echo [INFO] Looking for warnings, errors, and verifying auto-triggers
echo.
echo ====================================================================
echo.

venv\Scripts\python.exe scripts\micro_level_monitor.py --duration 5 --interval 10

echo.
echo ====================================================================
echo   MONITORING COMPLETE
echo ====================================================================
echo.
echo Check outputs\micro_monitoring_report.json for detailed report
echo.
pause
