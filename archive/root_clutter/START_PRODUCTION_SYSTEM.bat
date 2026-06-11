@echo off
REM ====================================================================
REM PRODUCTION READY PAPER TRADING SYSTEM
REM Complete end-to-end automation with live monitoring
REM ====================================================================

title Production Paper Trading System

cd /d "%~dp0"

echo.
echo ====================================================================
echo   PRODUCTION PAPER TRADING SYSTEM - STARTING
echo ====================================================================
echo.

REM Check venv
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Create directories
if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs
if not exist "storage\live" mkdir storage\live

echo [INFO] Virtual environment activated
echo [INFO] Directories checked
echo.

REM Pre-flight checks
echo [STEP 1/5] Running pre-flight checks...
venv\Scripts\python.exe scripts\production_readiness_check.py
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some pre-flight checks failed, but continuing...
)
echo.

REM Check market hours
echo [STEP 2/5] Checking market hours...
venv\Scripts\python.exe -c "import sys; from pathlib import Path; ROOT_DIR = Path('.').resolve(); sys.path.insert(0, str(ROOT_DIR)); from src.utils.market_hours import is_market_open; from datetime import datetime; import pytz; ist = pytz.timezone('Asia/Kolkata'); now = datetime.now(ist); open, reason = is_market_open(now); print('Market Status:', 'OPEN' if open else 'CLOSED'); print('Reason:', reason); exit(0 if open else 1)" 2>nul
set MARKET_STATUS=%ERRORLEVEL%

if %MARKET_STATUS% NEQ 0 (
    echo [INFO] Market is CLOSED - System will use simulation mode if needed
    set IGNORE_MARKET_HOURS=--ignore-market-hours
) else (
    echo [OK] Market is OPEN - Using live data
    set IGNORE_MARKET_HOURS=
)
echo.

REM Initialize PnL file if it doesn't exist
echo [STEP 3/5] Initializing data files...
if not exist "outputs\pnl_live.json" (
    echo {"timestamp":"","total_trades":0,"winning_trades":0,"losing_trades":0,"win_rate":0.0,"total_realized_pnl":0.0,"total_unrealized_pnl":0.0,"total_pnl":0.0,"open_positions":0} > "outputs\pnl_live.json"
    echo [OK] PnL file initialized
)
echo.

REM Start paper trading engine in background
echo [STEP 4/5] Starting paper trading engine (background)...
echo [INFO] Engine will run in minimized window
start /MIN "Paper Trading Engine" cmd /c "cd /d %~dp0 && call venv\Scripts\activate.bat && python scripts\run_live_chain.py --refresh 5 %IGNORE_MARKET_HOURS% --no-websocket >> logs\trading_engine.log 2>&1"

REM Wait for system to initialize
echo [INFO] Waiting for system to initialize (10 seconds)...
timeout /t 10 /nobreak >nul
echo.

REM Start profit monitor (this is what user sees)
echo [STEP 5/5] Starting Profit Monitor...
echo.
echo ====================================================================
echo   PROFIT MONITOR - LIVE DASHBOARD
echo   Auto-refresh: Every 5 seconds
echo   Press Ctrl+C to stop (trading engine will continue)
echo ====================================================================
echo.

venv\Scripts\python.exe scripts\profit_focused_monitor.py

REM Cleanup message
echo.
echo ====================================================================
echo   MONITOR STOPPED
echo ====================================================================
echo.
echo [INFO] Trading engine is still running in background
echo [INFO] To stop trading engine, close the minimized window
echo [INFO] Or run: taskkill /F /FI "WINDOWTITLE eq Paper Trading Engine*"
echo.
pause
