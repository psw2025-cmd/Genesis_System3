@echo off
REM ====================================================================
REM AUTO FIX AND KEEP RUNNING - Does everything automatically
REM ====================================================================

cd /d "%~dp0"

echo Killing stuck processes...
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 3 /nobreak >nul

echo Starting trading system...
call venv\Scripts\activate.bat
start "Trading System" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python scripts\smart_live_chain_runner.py --refresh 5 --market-check 30 --no-websocket"

echo Starting monitor...
start "System Monitor" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python scripts\keep_monitoring.py"

echo.
echo System started and monitoring...
echo Both windows are running in background.
echo.
