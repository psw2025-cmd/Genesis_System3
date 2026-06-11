@echo off
REM ====================================================================
REM PRODUCTION SYSTEM - ONE CLICK START
REM ====================================================================

title Production Paper Trading System

cd /d "%~dp0"

echo.
echo ====================================================================
echo   GENESIS SYSTEM3 - PRODUCTION READY
echo ====================================================================
echo.
echo Starting production system...
echo.

REM Check venv
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Create directories
if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs

echo [OK] Environment ready
echo.

REM Start trading engine in background
echo [INFO] Starting trading engine (background)...
start /MIN "Paper Trading Engine" cmd /c "cd /d %~dp0 && call venv\Scripts\activate.bat && python scripts\run_live_chain.py --refresh 5 --ignore-market-hours --no-websocket >> logs\trading_engine.log 2>&1"

REM Wait for initialization
echo [INFO] Initializing system (10 seconds)...
timeout /t 10 /nobreak >nul

REM Start profit monitor
echo [INFO] Starting profit monitor...
echo.
echo ====================================================================
echo   PROFIT MONITOR - LIVE DASHBOARD
echo   Auto-refresh: Every 5 seconds
echo   Press Ctrl+C to stop
echo ====================================================================
echo.

venv\Scripts\python.exe scripts\profit_focused_monitor.py

echo.
echo ====================================================================
echo   SYSTEM STOPPED
echo ====================================================================
echo.
pause
