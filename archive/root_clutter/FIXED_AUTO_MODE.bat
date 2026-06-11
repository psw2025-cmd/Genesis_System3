@echo off
REM ====================================================================
REM GENESIS SYSTEM3 - FIXED AUTO MODE (WITH VISIBLE OUTPUT)
REM Complete automated trading system with all features
REM ====================================================================

title Genesis System3 - Auto Mode (Fixed)

cd /d "%~dp0"

echo.
echo ====================================================================
echo   GENESIS SYSTEM3 - UNIFIED AUTO MODE (FIXED)
echo   Complete Automated Trading System
echo ====================================================================
echo.
echo This system will:
echo   [1] Validate environment and components
echo   [2] Auto-detect market hours
echo   [3] Start trading engine (background)
echo   [4] Start Excel auto-updater (background)
echo   [5] Launch live monitor dashboard
echo.
echo Press Ctrl+C to stop monitoring (trading continues)
echo.
timeout /t 3 /nobreak >nul

REM ====================================================================
REM STEP 1: Environment Setup
REM ====================================================================
echo.
echo [STEP 1/6] Environment Setup...
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
REM STEP 2: Pre-Flight Checks
REM ====================================================================
echo.
echo [STEP 2/6] Pre-Flight Checks...
echo.

REM Check if production readiness check exists
if exist "scripts\production_readiness_check.py" (
    venv\Scripts\python.exe scripts\production_readiness_check.py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo   [OK] Pre-flight checks passed
    ) else (
        echo   [WARNING] Some pre-flight checks failed, continuing...
    )
) else (
    echo   [INFO] Pre-flight check script not found, skipping...
)

REM ====================================================================
REM STEP 3: Market Hours Detection
REM ====================================================================
echo.
echo [STEP 3/6] Market Hours Detection...
echo.

venv\Scripts\python.exe -c "import sys; from pathlib import Path; ROOT_DIR = Path('.').resolve(); sys.path.insert(0, str(ROOT_DIR)); from src.utils.market_hours import is_market_open; from datetime import datetime; import pytz; ist = pytz.timezone('Asia/Kolkata'); now = datetime.now(ist); open, reason = is_market_open(now); print('Market Status:', 'OPEN' if open else 'CLOSED'); print('Reason:', reason); exit(0 if open else 1)" 2>nul
set MARKET_STATUS=%ERRORLEVEL%

if %MARKET_STATUS% EQU 0 (
    echo   [OK] Market is OPEN - Using live data
    set IGNORE_MARKET_HOURS=
    set MODE_TEXT=LIVE
) else (
    echo   [INFO] Market is CLOSED - Will use available data
    set IGNORE_MARKET_HOURS=--ignore-market-hours
    set MODE_TEXT=OFF-HOURS
)

REM ====================================================================
REM STEP 4: Initialize Data Files
REM ====================================================================
echo.
echo [STEP 4/6] Initializing Data Files...
echo.

REM Initialize PnL file if it doesn't exist
if not exist "outputs\pnl_live.json" (
    echo {"timestamp":"","total_trades":0,"winning_trades":0,"losing_trades":0,"win_rate":0.0,"total_realized_pnl":0.0,"total_unrealized_pnl":0.0,"total_pnl":0.0,"open_positions":0} > "outputs\pnl_live.json"
    echo   [OK] PnL file initialized
)

REM Initialize positions file if it doesn't exist
if not exist "outputs\positions_live.json" (
    echo {"timestamp_ist":"","open_positions":[],"summary":{"open_count":0,"closed_count":0}} > "outputs\positions_live.json"
    echo   [OK] Positions file initialized
)

REM ====================================================================
REM STEP 5: Start Background Services
REM ====================================================================
echo.
echo [STEP 5/6] Starting Background Services...
echo.

REM Stop any existing trading engine processes
taskkill /F /FI "WINDOWTITLE eq Paper Trading Engine*" /T /F >nul 2>&1
timeout /t 1 /nobreak >nul

REM Start smart trading engine with auto-switch (visible window, not minimized)
echo   [INFO] Starting smart trading engine with auto-switch...
echo   [INFO] Engine will auto-detect market and switch between virtual/live data
echo   [INFO] You should see output immediately in the new window
echo.

REM Create a batch file that will run in the new window to ensure output
echo @echo off > "%TEMP%\run_trading_engine.bat"
echo cd /d "%~dp0" >> "%TEMP%\run_trading_engine.bat"
echo echo. >> "%TEMP%\run_trading_engine.bat"
echo echo ==================================================================== >> "%TEMP%\run_trading_engine.bat"
echo echo   PAPER TRADING ENGINE - STARTING >> "%TEMP%\run_trading_engine.bat"
echo echo ==================================================================== >> "%TEMP%\run_trading_engine.bat"
echo echo. >> "%TEMP%\run_trading_engine.bat"
echo call "%~dp0venv\Scripts\activate.bat" >> "%TEMP%\run_trading_engine.bat"
echo echo Virtual environment activated >> "%TEMP%\run_trading_engine.bat"
echo echo. >> "%TEMP%\run_trading_engine.bat"
echo echo Running Python script... >> "%TEMP%\run_trading_engine.bat"
echo echo. >> "%TEMP%\run_trading_engine.bat"
echo python -u "%~dp0scripts\smart_live_chain_runner.py" --refresh 5 --market-check 30 --no-websocket >> "%TEMP%\run_trading_engine.bat"
echo echo. >> "%TEMP%\run_trading_engine.bat"
echo echo Script finished. >> "%TEMP%\run_trading_engine.bat"
echo pause >> "%TEMP%\run_trading_engine.bat"

start "Paper Trading Engine" cmd /k "%TEMP%\run_trading_engine.bat"

if %ERRORLEVEL% NEQ 0 (
    echo   [ERROR] Failed to start trading engine!
    pause
    exit /b 1
)
echo   [OK] Smart trading engine started (visible window)
echo   [INFO] Check the "Paper Trading Engine" window - you should see output now

REM Start Excel updater if script exists
if exist "scripts\auto_update_excel.py" (
    echo   [INFO] Starting Excel auto-updater (background)...
    start /MIN "Excel Updater" cmd /c "cd /d %~dp0 && call venv\Scripts\activate.bat && python scripts\auto_update_excel.py >> logs\excel_updater.log 2>&1"
    echo   [OK] Excel updater started
) else (
    echo   [INFO] Excel updater script not found, skipping...
)

REM Wait for system to initialize
echo   [INFO] Waiting for system initialization (10 seconds)...
timeout /t 10 /nobreak >nul

REM ====================================================================
REM STEP 6: Launch Monitor Dashboard
REM ====================================================================
echo.
echo [STEP 6/6] Launching Monitor Dashboard...
echo.
echo ====================================================================
echo   LIVE TRADING MONITOR - %MODE_TEXT% MODE
echo   Auto-refresh: Every 5 seconds
echo   Press Ctrl+C to stop monitoring (trading continues)
echo ====================================================================
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
    echo   [INFO] Trading engine is running in background
    echo   [INFO] Check logs\trading_engine.log for status
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
echo [INFO] Trading engine is still running in background
echo [INFO] To stop trading engine:
echo       1. Close the minimized "Paper Trading Engine" window
echo       2. Or run: taskkill /F /FI "WINDOWTITLE eq Paper Trading Engine*"
echo.
echo [INFO] To restart system: Run AUTO_MODE.bat again
echo.
pause
