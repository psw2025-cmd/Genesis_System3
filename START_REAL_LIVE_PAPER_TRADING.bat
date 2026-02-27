@echo off
REM ====================================================================
REM START REAL LIVE PAPER TRADING
REM Uses REAL market data from Angel One API (NO simulation/virtual data)
REM ====================================================================

title Real Live Paper Trading - Angel One

echo.
echo ====================================================================
echo   REAL LIVE PAPER TRADING SYSTEM
echo   Using REAL Market Data (NO Simulation)
echo ====================================================================
echo.
echo IMPORTANT:
echo   - This uses REAL live market data from Angel One API
echo   - NO virtual/simulation data will be used
echo   - Market hours: 09:15 - 15:30 IST (Mon-Fri)
echo   - All trades are PAPER TRADES (simulated execution)
echo   - NO real capital at risk
echo.
echo ====================================================================
echo.

cd /d "%~dp0"

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
if not exist "storage\live" mkdir storage\live

echo [INFO] Virtual environment activated
echo [INFO] Directories checked
echo.

REM Check market hours (includes special trading days like Budget Day)
echo [INFO] Checking market hours...
venv\Scripts\python.exe scripts\test_special_trading_day.py 2>nul | findstr /C:"Market Status" /C:"Reason"

venv\Scripts\python.exe -c "import sys; from pathlib import Path; ROOT_DIR = Path('.').resolve(); sys.path.insert(0, str(ROOT_DIR)); from src.utils.market_hours import is_market_open; from datetime import datetime; import pytz; ist = pytz.timezone('Asia/Kolkata'); now = datetime.now(ist); open, reason = is_market_open(now); exit(0 if open else 1)" 2>nul

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARNING] Market is currently CLOSED
    echo.
    echo Options:
    echo   1. Wait for market to open (09:15 IST, Mon-Fri or Special Trading Days)
    echo   2. Continue anyway (will use last available data)
    echo.
    echo Note: Special trading days (like Budget Day) are automatically detected
    echo.
    set /p CONTINUE="Continue anyway? (y/n): "
    if /i not "%CONTINUE%"=="y" (
        echo.
        echo [INFO] Exiting. Run again when market is open.
        pause
        exit /b 0
    )
    echo.
    echo [INFO] Continuing with --ignore-market-hours flag...
    set IGNORE_MARKET_HOURS=--ignore-market-hours
) else (
    echo [OK] Market is OPEN (or Special Trading Day detected)
    set IGNORE_MARKET_HOURS=
)

echo.
echo ====================================================================
echo   STARTING REAL LIVE PAPER TRADING
echo ====================================================================
echo.
echo Configuration:
echo   - Data Source: REAL Angel One API (live market data)
echo   - Simulation Mode: DISABLED (sim_mode=False)
echo   - Paper Trading: ENABLED (no real capital)
echo   - Refresh Interval: 5 seconds
echo   - Indices: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX
echo.
echo Press Ctrl+C to stop
echo.
echo ====================================================================
echo.

REM Start real live paper trading (NO --sim-mode flag)
venv\Scripts\python.exe scripts\run_live_chain.py --refresh 5 %IGNORE_MARKET_HOURS%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Paper trading stopped with error
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo   PAPER TRADING STOPPED
echo ====================================================================
echo.
pause
