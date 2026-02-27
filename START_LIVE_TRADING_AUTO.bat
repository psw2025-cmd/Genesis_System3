@echo off
REM ================================================================================
REM   START LIVE TRADING - FULLY AUTOMATED SINGLE-CLICK SOLUTION
REM   Auto-detects market hours, starts paper trading, updates Excel, monitors
REM ================================================================================
title LIVE TRADING SYSTEM - AUTO MODE

cd /d "%~dp0"

echo ================================================================================
echo   LIVE TRADING SYSTEM - FULLY AUTOMATED
echo ================================================================================
echo.
echo This will:
echo   1. Check and activate virtual environment
echo   2. Validate all components
echo   3. Auto-detect market hours
echo   4. Start paper trading automatically
echo   5. Auto-update Excel with live data
echo   6. Monitor everything continuously
echo.
echo Press Ctrl+C to stop anytime
echo.
pause

REM Activate virtual environment
echo.
echo [STEP 1] Activating Virtual Environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo   [OK] Virtual environment activated
) else (
    echo   [ERROR] Virtual environment not found!
    echo   Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo   [OK] Virtual environment created and activated
)

REM Pre-trading validation
echo.
echo [STEP 2] Pre-Trading Validation...
python scripts\pre_trading_validation.py
if errorlevel 1 (
    echo   [ERROR] Pre-trading validation failed!
    echo   Please check the errors above.
    pause
    exit /b 1
)
echo   [OK] All validations passed

REM Multi-session handling
echo.
echo [STEP 3] Multi-Session Setup...
python scripts\multi_session_handler.py
if errorlevel 1 (
    echo   [WARNING] Multi-session setup had issues, continuing anyway...
)

REM Check market hours
echo.
echo [STEP 4] Checking Market Hours...
python -c "from src.utils.market_hours import is_market_open; from datetime import datetime; import pytz; ist=pytz.timezone('Asia/Kolkata'); now=datetime.now(ist); open, reason=is_market_open(now); print('Market Status:', 'OPEN' if open else 'CLOSED'); print('Reason:', reason); print('Current Time:', now.strftime('%%Y-%%m-%%d %%H:%%M:%%S IST')); exit(0 if open else 1)"
set MARKET_STATUS=%ERRORLEVEL%

if %MARKET_STATUS%==0 (
    echo   [OK] Market is OPEN - Starting live trading
    set START_TRADING=1
    set USE_SIM=0
) else (
    echo   [INFO] Market is CLOSED - Using simulation mode
    set START_TRADING=1
    set USE_SIM=1
    echo   [INFO] System will auto-switch to live mode when market opens
)

REM Start paper trading in background
echo.
echo [STEP 5] Starting Paper Trading System...
echo   [INFO] This will run in the background
echo   [INFO] Monitor will show live updates

REM Start paper trading based on market status
if %USE_SIM%==1 (
    echo   [INFO] Starting in SIMULATION mode (market closed)
    start /B python scripts\run_live_chain.py --sim-mode
) else (
    echo   [INFO] Starting in LIVE mode (market open)
    start /B python scripts\run_live_chain.py
)

REM Wait a moment for system to initialize
timeout /t 5 /nobreak >nul

REM Start Excel updater in background (runs every 5 minutes)
echo.
echo [STEP 6] Starting Excel Auto-Updater...
echo   [INFO] Excel will auto-update every 5 minutes

start /B python scripts\auto_update_excel.py

REM Start live monitor
echo.
echo [STEP 7] Starting Live Monitor...
echo   [INFO] Press Ctrl+C to stop monitoring (trading will continue)
echo.

python scripts\monitor_live_simulation.py

REM Cleanup on exit
echo.
echo ================================================================================
echo   STOPPING SYSTEM...
echo ================================================================================
echo.

REM Stop background processes
taskkill /F /IM python.exe /FI "WINDOWTITLE eq LIVE TRADING*" 2>nul

REM Post-trading cleanup
echo [CLEANUP] Running post-trading cleanup...
python scripts\post_trading_cleanup.py

echo.
echo ================================================================================
echo   SYSTEM STOPPED
echo ================================================================================
echo.
pause
