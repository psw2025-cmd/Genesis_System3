@echo off
REM ====================================================================
REM SMART AUTO MODE - Full Automation with Auto-Switch
REM Auto-detects market, switches between virtual/live data
REM Window stays visible, no disappearing
REM ====================================================================

title Genesis System3 - Smart Auto Mode

cd /d "%~dp0"

echo.
echo ====================================================================
echo   GENESIS SYSTEM3 - SMART AUTO MODE
echo   Full Automation with Auto-Switch
echo ====================================================================
echo.
echo Features:
echo   [1] Auto-detects market status (LIVE or CLOSED)
echo   [2] Uses virtual data when market closed
echo   [3] Auto-switches to live data when market opens
echo   [4] Window stays visible (no disappearing)
echo   [5] Continuous monitoring and switching
echo   [6] Optimized performance
echo.
echo Press Ctrl+C to stop
echo.
timeout /t 3 /nobreak >nul

REM ====================================================================
REM STEP 1: Environment Setup
REM ====================================================================
echo.
echo [STEP 1/5] Environment Setup...
echo.

REM Check venv
if not exist "venv\Scripts\python.exe" (
    echo   [ERROR] Virtual environment not found!
    echo   Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo   [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo   [OK] Virtual environment created
)

REM Activate venv
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo   [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)
echo   [OK] Virtual environment activated

REM Create directories
if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs
if not exist "storage\live" mkdir storage\live
echo   [OK] Directories ready

REM ====================================================================
REM STEP 2: Test Smart Auto-Switch System
REM ====================================================================
echo.
echo [STEP 2/5] Testing Smart Auto-Switch System...
echo.

venv\Scripts\python.exe scripts\smart_market_auto_switch.py
if %ERRORLEVEL% NEQ 0 (
    echo   [WARNING] Auto-switch test had issues, but continuing...
)
echo   [OK] Auto-switch system ready

REM ====================================================================
REM STEP 3: Initialize Data Files
REM ====================================================================
echo.
echo [STEP 3/5] Initializing Data Files...
echo.

if not exist "outputs\pnl_live.json" (
    echo {"timestamp":"","total_trades":0,"winning_trades":0,"losing_trades":0,"win_rate":0.0,"total_realized_pnl":0.0,"total_unrealized_pnl":0.0,"total_pnl":0.0,"open_positions":0} > "outputs\pnl_live.json"
    echo   [OK] PnL file initialized
)

if not exist "outputs\positions_live.json" (
    echo {"timestamp_ist":"","open_positions":[],"summary":{"open_count":0,"closed_count":0}} > "outputs\positions_live.json"
    echo   [OK] Positions file initialized
)

if not exist "outputs\market_status.json" (
    echo {"mode":"UNKNOWN","is_open":false} > "outputs\market_status.json"
    echo   [OK] Market status file initialized
)

REM ====================================================================
REM STEP 4: Start Smart Trading Engine (VISIBLE WINDOW)
REM ====================================================================
echo.
echo [STEP 4/5] Starting Smart Trading Engine...
echo.
echo   [INFO] Engine will run in VISIBLE window (not minimized)
echo   [INFO] Auto-detects market and switches modes automatically
echo   [INFO] Uses virtual data when market closed
echo   [INFO] Auto-switches to live data when market opens
echo.

REM Stop any existing processes
taskkill /FI "WINDOWTITLE eq Paper Trading Engine*" /T /F >nul 2>&1
timeout /t 1 /nobreak >nul

REM Start smart runner in VISIBLE window (not /MIN)
start "Paper Trading Engine" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python scripts\smart_live_chain_runner.py --refresh 5 --market-check 30 --no-websocket"
if %ERRORLEVEL% NEQ 0 (
    echo   [ERROR] Failed to start trading engine!
    pause
    exit /b 1
)
echo   [OK] Smart trading engine started (visible window)

REM Wait for initialization
echo   [INFO] Waiting for system initialization (10 seconds)...
timeout /t 10 /nobreak >nul

REM ====================================================================
REM STEP 5: Launch Monitor Dashboard
REM ====================================================================
echo.
echo [STEP 5/5] Launching Monitor Dashboard...
echo.
echo ====================================================================
echo   PROFIT MONITOR - LIVE DASHBOARD
echo   Auto-refresh: Every 5 seconds
echo   Press Ctrl+C to stop monitoring
echo ====================================================================
echo.
echo [INFO] Trading engine is running in separate visible window
echo [INFO] Monitor shows real-time PnL and trades
echo.

REM Check which monitor script to use
if exist "scripts\profit_focused_monitor.py" (
    venv\Scripts\python.exe scripts\profit_focused_monitor.py
) else if exist "scripts\monitor_live_simulation.py" (
    venv\Scripts\python.exe scripts\monitor_live_simulation.py
) else if exist "scripts\live_paper_trading_monitor.py" (
    venv\Scripts\python.exe scripts\live_paper_trading_monitor.py
) else (
    echo   [ERROR] No monitor script found!
    echo   [INFO] Trading engine is running in visible window
    echo   [INFO] Check the "Paper Trading Engine" window for status
    pause
    exit /b 1
)

REM ====================================================================
REM Cleanup on Exit
REM ====================================================================
echo.
echo ====================================================================
echo   MONITOR STOPPED
echo ====================================================================
echo.
echo [INFO] Trading engine is still running in visible window
echo [INFO] To stop: Close the "Paper Trading Engine" window
echo [INFO] Or run: taskkill /F /FI "WINDOWTITLE eq Paper Trading Engine*"
echo.
echo [INFO] To restart: Run SMART_AUTO_MODE.bat again
echo.
pause
