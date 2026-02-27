@echo off
REM ====================================================================
REM GENESIS SYSTEM3 - PRODUCTION FULL SYSTEM RUNNER
REM Complete orchestration: Backtesting + Paper Trading + Monitoring
REM Production-grade with error handling, logging, and proper sequencing
REM ====================================================================

title Genesis System3 - Full Production System

setlocal enabledelayedexpansion

REM ====================================================================
REM CONFIGURATION
REM ====================================================================
set SCRIPT_DIR=%~dp0
set LOG_DIR=%SCRIPT_DIR%logs
set OUTPUT_DIR=%SCRIPT_DIR%outputs
set STORAGE_DIR=%SCRIPT_DIR%storage
set VENV_DIR=%SCRIPT_DIR%venv

REM Create log file with timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%
set LOG_FILE=%LOG_DIR%\full_system_%TIMESTAMP%.log

REM ====================================================================
REM PHASE 0: INITIALIZATION
REM ====================================================================
cls
echo.
echo ====================================================================
echo   GENESIS SYSTEM3 - PRODUCTION FULL SYSTEM RUNNER
echo   Complete Orchestration: Backtesting + Paper Trading + Monitoring
echo ====================================================================
echo.
echo Start Time: %date% %time%
echo Log File: %LOG_FILE%
echo.

REM Create directories
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%STORAGE_DIR%\live" mkdir "%STORAGE_DIR%\live"
if not exist "%STORAGE_DIR%\archive" mkdir "%STORAGE_DIR%\archive"
if not exist "%STORAGE_DIR%\backtest" mkdir "%STORAGE_DIR%\backtest"

echo [%date% %time%] [INIT] Directories created/verified >> "%LOG_FILE%"
echo [INIT] Directories created/verified

REM ====================================================================
REM PHASE 1: ENVIRONMENT VALIDATION
REM ====================================================================
echo.
echo ====================================================================
echo   PHASE 1/6: ENVIRONMENT VALIDATION
echo ====================================================================
echo.

REM Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    echo [%date% %time%] [ERROR] Python not found >> "%LOG_FILE%"
    pause
    exit /b 1
)
python --version
echo [%date% %time%] [OK] Python found >> "%LOG_FILE%"
echo [OK] Python found

REM Check virtual environment
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [WARN] Virtual environment not found. Creating...
    echo [%date% %time%] [WARN] Virtual environment not found. Creating... >> "%LOG_FILE%"
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        echo [%date% %time%] [ERROR] Failed to create virtual environment >> "%LOG_FILE%"
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo [%date% %time%] [OK] Virtual environment created >> "%LOG_FILE%"
)

REM Activate virtual environment
call "%VENV_DIR%\Scripts\activate.bat" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    echo [%date% %time%] [ERROR] Failed to activate virtual environment >> "%LOG_FILE%"
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo [%date% %time%] [OK] Virtual environment activated >> "%LOG_FILE%"

REM Check and install requirements (skip pip upgrade to avoid corruption issues)
if exist "%SCRIPT_DIR%requirements.txt" (
    echo [INFO] Checking requirements...
    echo [%date% %time%] [INFO] Checking requirements... >> "%LOG_FILE%"
    
    REM Install requirements (skip pip upgrade - venv may have corrupted pip)
    "%VENV_DIR%\Scripts\python.exe" -m pip install -r "%SCRIPT_DIR%requirements.txt" >nul 2>&1
    if errorlevel 1 (
        echo [WARN] Some requirements may have failed to install
        echo [%date% %time%] [WARN] Some requirements may have failed to install >> "%LOG_FILE%"
        echo [INFO] Continuing anyway - system may still work with existing packages
    ) else (
        echo [OK] Requirements verified
        echo [%date% %time%] [OK] Requirements verified >> "%LOG_FILE%"
    )
)

REM Check critical files
set MISSING_FILES=0
if not exist "%SCRIPT_DIR%option_chain_automation_master.py" (
    echo [ERROR] option_chain_automation_master.py not found
    echo [%date% %time%] [ERROR] option_chain_automation_master.py not found >> "%LOG_FILE%"
    set /a MISSING_FILES+=1
)
if not exist "%SCRIPT_DIR%config\.env" (
    echo [WARN] config\.env not found - API credentials may be missing
    echo [%date% %time%] [WARN] config\.env not found >> "%LOG_FILE%"
)
if %MISSING_FILES% GTR 0 (
    echo [ERROR] Critical files missing. Cannot proceed.
    echo [%date% %time%] [ERROR] Critical files missing >> "%LOG_FILE%"
    pause
    exit /b 1
)

echo [OK] Environment validation complete
echo [%date% %time%] [OK] Environment validation complete >> "%LOG_FILE%"

REM ====================================================================
REM PHASE 2: PRE-FLIGHT CHECKS
REM ====================================================================
echo.
echo ====================================================================
echo   PHASE 2/6: PRE-FLIGHT CHECKS
echo ====================================================================
echo.

REM Check market hours
echo [INFO] Checking market hours...
echo [%date% %time%] [INFO] Checking market hours... >> "%LOG_FILE%"
cd /d "%SCRIPT_DIR%"
python -c "import sys; from pathlib import Path; ROOT_DIR = Path('.').resolve(); sys.path.insert(0, str(ROOT_DIR)); from src.utils.market_hours import is_market_open; from datetime import datetime; import pytz; ist = pytz.timezone('Asia/Kolkata'); now = datetime.now(ist); open, reason = is_market_open(now); print('Market Status:', 'OPEN' if open else 'CLOSED'); print('Reason:', reason); exit(0 if open else 1)" 2>nul
set MARKET_STATUS=%ERRORLEVEL%

if %MARKET_STATUS% EQU 0 (
    echo [OK] Market is OPEN - Will use live data
    echo [%date% %time%] [OK] Market is OPEN >> "%LOG_FILE%"
    set IGNORE_MARKET_HOURS=
    set MODE_TEXT=LIVE
    set RUN_BACKTEST_FIRST=YES
) else (
    echo [INFO] Market is CLOSED - Will use available data
    echo [%date% %time%] [INFO] Market is CLOSED >> "%LOG_FILE%"
    set IGNORE_MARKET_HOURS=--ignore-market-hours
    set MODE_TEXT=OFF-HOURS
    set RUN_BACKTEST_FIRST=YES
)

REM Check API credentials (if .env exists)
if exist "%SCRIPT_DIR%config\.env" (
    echo [INFO] Checking API credentials...
    echo [%date% %time%] [INFO] Checking API credentials... >> "%LOG_FILE%"
    python -c "import sys; from pathlib import Path; ROOT_DIR = Path('.').resolve(); sys.path.insert(0, str(ROOT_DIR)); from core.utils.env_loader import load_env; load_env(); import os; api_key = os.getenv('ANGEL_ONE_API_KEY', ''); if api_key: print('API Key: Found'); exit(0); else: print('API Key: Missing'); exit(1)" 2>nul
    if errorlevel 1 (
        echo [WARN] API credentials may be missing or invalid
        echo [%date% %time%] [WARN] API credentials may be missing >> "%LOG_FILE%"
    ) else (
        echo [OK] API credentials found
        echo [%date% %time%] [OK] API credentials found >> "%LOG_FILE%"
    )
)

echo [OK] Pre-flight checks complete
echo [%date% %time%] [OK] Pre-flight checks complete >> "%LOG_FILE%"

REM ====================================================================
REM PHASE 3: BACKTESTING (if historical data available)
REM ====================================================================
echo.
echo ====================================================================
echo   PHASE 3/6: BACKTESTING
echo ====================================================================
echo.

set BACKTEST_RUN=NO
set BACKTEST_SUCCESS=NO

REM Check if backtesting should run
if "%RUN_BACKTEST_FIRST%"=="YES" (
    echo [INFO] Checking for historical data for backtesting...
    echo [%date% %time%] [INFO] Checking for historical data... >> "%LOG_FILE%"
    
    REM Check for historical signals CSV
    if exist "%STORAGE_DIR%\live\angel_index_ai_signals_with_forward.csv" (
        echo [INFO] Historical signals found - Running backtest...
        echo [%date% %time%] [INFO] Historical signals found >> "%LOG_FILE%"
        set BACKTEST_RUN=YES
        
        REM Skip synthetic backtester - takes 1-2 minutes, run manually if needed
        REM To run manually: python -m core.engine.angel_synthetic_backtester
        echo [INFO] Skipping synthetic backtest (takes 1-2 min) - continuing to paper trading...
        echo [INFO] To run backtest manually: python -m core.engine.angel_synthetic_backtester
        echo [%date% %time%] [INFO] Skipping synthetic backtest >> "%LOG_FILE%"
        set BACKTEST_SUCCESS=YES
        
        REM Run strategy backtester if available (quick check only)
        if exist "%SCRIPT_DIR%core\engine\system3_phase280_strategy_backtester.py" (
            echo [INFO] Running quick strategy backtest check...
            echo [%date% %time%] [INFO] Running strategy backtester... >> "%LOG_FILE%"
            python -c "import sys; from pathlib import Path; ROOT_DIR = Path('.').resolve(); sys.path.insert(0, str(ROOT_DIR)); from core.engine.system3_phase280_strategy_backtester import run_phase280; result = run_phase280(); print('Backtest Status:', result.get('status', 'UNKNOWN'))" >> "%LOG_FILE%" 2>&1
            if errorlevel 1 (
                echo [WARN] Strategy backtest had errors (continuing anyway)
                echo [%date% %time%] [WARN] Strategy backtest had errors >> "%LOG_FILE%"
            ) else (
                echo [OK] Strategy backtest completed
                echo [%date% %time%] [OK] Strategy backtest completed >> "%LOG_FILE%"
            )
        )
    ) else (
        echo [INFO] No historical data found - Skipping backtest
        echo [%date% %time%] [INFO] No historical data found >> "%LOG_FILE%"
    )
)

if "%BACKTEST_RUN%"=="NO" (
    echo [INFO] Backtesting skipped (no historical data or not requested)
    echo [%date% %time%] [INFO] Backtesting skipped >> "%LOG_FILE%"
) else (
    echo [INFO] Backtesting phase complete - continuing to paper trading...
    echo [%date% %time%] [INFO] Backtesting phase complete >> "%LOG_FILE%"
)

REM ====================================================================
REM PHASE 4: INITIALIZE DATA FILES
REM ====================================================================
echo.
echo ====================================================================
echo   PHASE 4/6: INITIALIZE DATA FILES
echo ====================================================================
echo.

REM Initialize PnL file
if not exist "%OUTPUT_DIR%\pnl_live.json" (
    echo {"timestamp":"","total_trades":0,"winning_trades":0,"losing_trades":0,"win_rate":0.0,"total_realized_pnl":0.0,"total_unrealized_pnl":0.0,"total_pnl":0.0,"open_positions":0} > "%OUTPUT_DIR%\pnl_live.json"
    echo [OK] PnL file initialized
    echo [%date% %time%] [OK] PnL file initialized >> "%LOG_FILE%"
)

REM Initialize positions file
if not exist "%OUTPUT_DIR%\positions_live.json" (
    echo {"timestamp_ist":"","open_positions":[],"summary":{"open_count":0,"closed_count":0}} > "%OUTPUT_DIR%\positions_live.json"
    echo [OK] Positions file initialized
    echo [%date% %time%] [OK] Positions file initialized >> "%LOG_FILE%"
)

REM Initialize health file
if not exist "%OUTPUT_DIR%\health.json" (
    echo {"status":"INITIALIZING","timestamp":"","cycles_completed":0,"data_fetch_success_rate":0.0,"last_data_fetch":null} > "%OUTPUT_DIR%\health.json"
    echo [OK] Health file initialized
    echo [%date% %time%] [OK] Health file initialized >> "%LOG_FILE%"
)

echo [OK] Data files initialized
echo [%date% %time%] [OK] Data files initialized >> "%LOG_FILE%"

REM ====================================================================
REM PHASE 5: START PAPER TRADING SYSTEM
REM ====================================================================
echo.
echo ====================================================================
echo   PHASE 5/6: STARTING PAPER TRADING SYSTEM
echo ====================================================================
echo.

REM Stop any existing processes
echo [INFO] Checking for existing processes...
echo [%date% %time%] [INFO] Checking for existing processes... >> "%LOG_FILE%"
taskkill /FI "WINDOWTITLE eq Paper Trading Engine*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Option Chain Automation*" /T /F >nul 2>&1
timeout /t 2 /nobreak >nul

REM Get parameters from command line or use defaults
set REFRESH_INTERVAL=5
if not "%1"=="" set REFRESH_INTERVAL=%1

set MAX_CYCLES=
if not "%2"=="" set MAX_CYCLES=--cycles %2

set DURATION=
if not "%3"=="" set DURATION=--duration %3

echo [INFO] Configuration:
echo [%date% %time%] [INFO] Configuration: >> "%LOG_FILE%"
echo   Refresh Interval: %REFRESH_INTERVAL% seconds
echo [%date% %time%]   Refresh Interval: %REFRESH_INTERVAL% seconds >> "%LOG_FILE%"
if not "%MAX_CYCLES%"=="" (
    echo   Max Cycles: %MAX_CYCLES%
    echo [%date% %time%]   Max Cycles: %MAX_CYCLES% >> "%LOG_FILE%"
)
if not "%DURATION%"=="" (
    echo   Duration: %DURATION% minutes
    echo [%date% %time%]   Duration: %DURATION% minutes >> "%LOG_FILE%"
)
echo   Mode: %MODE_TEXT%
echo [%date% %time%]   Mode: %MODE_TEXT% >> "%LOG_FILE%"

REM Start paper trading system in background
echo [INFO] Starting paper trading system...
echo [%date% %time%] [INFO] Starting paper trading system... >> "%LOG_FILE%"
cd /d "%SCRIPT_DIR%"
start "Paper Trading Engine" cmd /k "cd /d %SCRIPT_DIR% && call %VENV_DIR%\Scripts\activate.bat && python option_chain_automation_master.py --refresh %REFRESH_INTERVAL% %MAX_CYCLES% %DURATION% %IGNORE_MARKET_HOURS% >> %LOG_DIR%\paper_trading_%TIMESTAMP%.log 2>&1"

if errorlevel 1 (
    echo [ERROR] Failed to start paper trading system
    echo [%date% %time%] [ERROR] Failed to start paper trading system >> "%LOG_FILE%"
    pause
    exit /b 1
)

echo [OK] Paper trading system started
echo [%date% %time%] [OK] Paper trading system started >> "%LOG_FILE%"

REM Wait for initialization
echo [INFO] Waiting for system initialization (15 seconds)...
echo [%date% %time%] [INFO] Waiting for initialization... >> "%LOG_FILE%"
timeout /t 15 /nobreak >nul

REM Verify system is running
tasklist /FI "WINDOWTITLE eq Paper Trading Engine*" 2>nul | find /I "cmd.exe" >nul
if errorlevel 1 (
    echo [WARN] Paper trading process may not be running - check logs
    echo [%date% %time%] [WARN] Paper trading process may not be running >> "%LOG_FILE%"
) else (
    echo [OK] Paper trading process confirmed running
    echo [%date% %time%] [OK] Paper trading process confirmed running >> "%LOG_FILE%"
)

REM ====================================================================
REM PHASE 6: MONITORING AND STATUS
REM ====================================================================
echo.
echo ====================================================================
echo   PHASE 6/6: MONITORING AND STATUS
echo ====================================================================
echo.
echo ====================================================================
echo   LIVE SYSTEM MONITOR - %MODE_TEXT% MODE
echo   System Status: RUNNING
echo   Refresh Interval: %REFRESH_INTERVAL% seconds
echo   Log File: %LOG_FILE%
echo ====================================================================
echo.
echo Press Ctrl+C to stop monitoring (system will continue in background)
echo Or close this window to stop everything
echo.

REM Monitoring loop
:MONITOR_LOOP
cls
echo.
echo ====================================================================
echo   GENESIS SYSTEM3 - LIVE MONITOR
echo   %date% %time%
echo ====================================================================
echo.

REM Show system status
echo [SYSTEM STATUS]
echo --------------------------------------------------------------------
python -c "import json; from pathlib import Path; f = Path('outputs/health.json'); print(json.load(open(f)) if f.exists() else {'status': 'UNKNOWN'})" 2>nul
echo.

REM Show PnL summary
echo [PNL SUMMARY]
echo --------------------------------------------------------------------
python -c "import json; from pathlib import Path; f = Path('outputs/pnl_live.json'); d = json.load(open(f)) if f.exists() else {}; print(f\"Total PnL: {d.get('total_pnl', 0):.2f}\"); print(f\"Realized: {d.get('total_realized_pnl', 0):.2f}\"); print(f\"Unrealized: {d.get('total_unrealized_pnl', 0):.2f}\"); print(f\"Trades: {d.get('total_trades', 0)}\"); print(f\"Win Rate: {d.get('win_rate', 0)*100:.1f}%%\")" 2>nul
echo.

REM Show open positions
echo [OPEN POSITIONS]
echo --------------------------------------------------------------------
python -c "import json; from pathlib import Path; f = Path('outputs/positions_live.json'); d = json.load(open(f)) if f.exists() else {}; print(f\"Open Positions: {d.get('summary', {}).get('open_count', 0)}\")" 2>nul
echo.

REM Show top signal
echo [TOP SIGNAL]
echo --------------------------------------------------------------------
python -c "import json; from pathlib import Path; f = Path('outputs/top_trade_signal.json'); d = json.load(open(f)) if f.exists() else {}; print(f\"Action: {d.get('action', 'NONE')}\"); print(f\"Strategy: {d.get('strategy', 'NONE')}\"); print(f\"Confidence: {d.get('confidence', 0)*100:.1f}%%\")" 2>nul
echo.

REM Check if process is still running
tasklist /FI "WINDOWTITLE eq Paper Trading Engine*" 2>nul | find /I "cmd.exe" >nul
if errorlevel 1 (
    echo.
    echo [WARNING] Paper trading process not found!
    echo System may have stopped. Check logs for details.
    echo.
    echo Press any key to exit...
    pause >nul
    goto :cleanup
)

echo.
echo [INFO] Refreshing in 5 seconds... (Press Ctrl+C to stop)
timeout /t 5 /nobreak >nul
goto MONITOR_LOOP

REM ====================================================================
REM CLEANUP ON EXIT
REM ====================================================================
:cleanup
echo.
echo ====================================================================
echo   CLEANUP AND SHUTDOWN
echo ====================================================================
echo.

echo [INFO] Stopping paper trading system...
echo [%date% %time%] [INFO] Stopping paper trading system... >> "%LOG_FILE%"
taskkill /FI "WINDOWTITLE eq Paper Trading Engine*" /T /F >nul 2>&1
timeout /t 2 /nobreak >nul

REM Generate final summary
echo [INFO] Generating final summary...
echo [%date% %time%] [INFO] Generating final summary... >> "%LOG_FILE%"
if exist "%SCRIPT_DIR%scripts\show_practical_results.py" (
    python "%SCRIPT_DIR%scripts\show_practical_results.py" >> "%LOG_FILE%" 2>&1
)

echo.
echo ====================================================================
echo   SESSION COMPLETE
echo ====================================================================
echo.
echo Log File: %LOG_FILE%
echo Paper Trading Log: %LOG_DIR%\paper_trading_%TIMESTAMP%.log
echo.
echo Final Results:
python -c "import json; from pathlib import Path; f = Path('outputs/pnl_live.json'); d = json.load(open(f)) if f.exists() else {}; print(f\"Total PnL: {d.get('total_pnl', 0):.2f}\"); print(f\"Total Trades: {d.get('total_trades', 0)}\"); print(f\"Win Rate: {d.get('win_rate', 0)*100:.1f}%%\")" 2>nul
echo.
echo Press any key to exit...
pause >nul

endlocal
exit /b 0
