@echo off
REM ====================================================================
REM COMPLETE PAPER TRADING SYSTEM - MULTI-DAY SUPPORT
REM Handles: Pre-trading validation, Trading, Post-trading cleanup
REM ====================================================================

title Paper Trading System - Complete

echo.
echo ====================================================================
echo   PAPER TRADING SYSTEM - COMPLETE AUTOMATION
echo   Multi-Day Support Enabled
echo ====================================================================
echo.

cd /d "%~dp0"

REM ====================================================================
REM PHASE 1: PRE-TRADING VALIDATION
REM ====================================================================
echo [PHASE 1/4] PRE-TRADING VALIDATION
echo --------------------------------------------------------------------

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
if not exist "storage\archive" mkdir storage\archive

echo [INFO] Running pre-trading validation...
python scripts\pre_trading_validation.py
if errorlevel 1 (
    echo.
    echo [ERROR] Pre-trading validation FAILED
    echo Please fix issues before proceeding
    pause
    exit /b 1
)

echo [OK] Pre-trading validation passed
echo.

REM ====================================================================
REM PHASE 2: MULTI-SESSION SETUP
REM ====================================================================
echo [PHASE 2/4] MULTI-SESSION SETUP
echo --------------------------------------------------------------------

REM Update multi-session state
python scripts\multi_session_handler.py
echo [OK] Multi-session handler initialized
echo.

REM ====================================================================
REM PHASE 3: START PAPER TRADING
REM ====================================================================
echo [PHASE 3/4] STARTING PAPER TRADING
echo --------------------------------------------------------------------

REM Check if base CSV exists
if not exist "storage\live\option_chain_ALL_INDICES.csv" (
    echo [WARN] Base CSV not found - system will use simulation data
    echo.
)

REM Get scenario from argument or use default
set SCENARIO=TREND_UP
if not "%1"=="" set SCENARIO=%1

set DURATION=10
if not "%2"=="" set DURATION=%2

set REFRESH=5
if not "%3"=="" set REFRESH=%3

echo [INFO] Configuration:
echo   Scenario: %SCENARIO%
echo   Duration: %DURATION% minutes
echo   Refresh: %REFRESH% seconds
echo.

REM Start simulation in background
echo [INFO] Starting simulation in background...
start /MIN "Paper Trading Sim" cmd /c "cd /d %~dp0 && call venv\Scripts\activate.bat && python -m scripts.replay_test --scenario %SCENARIO% --duration %DURATION% --refresh %REFRESH%"

REM Wait for initialization
echo [INFO] Waiting for simulation to initialize...
timeout /t 10 /nobreak >nul

REM Run end-to-end verification
echo [INFO] Running end-to-end verification...
python scripts\end_to_end_verification.py

echo.
echo ====================================================================
echo   PAPER TRADING STATUS MONITOR
echo   Updates every 5 seconds
echo   Press Ctrl+C to stop (cleanup will run automatically)
echo ====================================================================
echo.

REM Monitor loop with cleanup handler
:MONITOR_LOOP
cls
echo ====================================================================
echo   PAPER TRADING STATUS - %date% %time%
echo ====================================================================
echo.

python scripts\check_paper_trading_status.py 2>nul

REM Check if simulation process is still running
tasklist /FI "WINDOWTITLE eq Paper Trading Sim*" 2>nul | find /I "cmd.exe" >nul
if errorlevel 1 (
    echo.
    echo [INFO] Simulation has finished. Final results shown above.
    echo [INFO] Press any key to exit and run cleanup...
    timeout /t 10 /nobreak >nul
    goto cleanup
)

if errorlevel 1 (
    echo [INFO] Waiting for data...
    timeout /t 3 /nobreak >nul
) else (
    timeout /t 5 /nobreak >nul
)

goto MONITOR_LOOP

REM Cleanup handler (runs on Ctrl+C)

REM ====================================================================
REM PHASE 4: POST-TRADING CLEANUP (runs on Ctrl+C or exit)
REM ====================================================================
:cleanup
echo.
echo [PHASE 4/4] POST-TRADING CLEANUP
echo --------------------------------------------------------------------

REM Update multi-session state
python scripts\multi_session_handler.py

REM Archive session
python scripts\post_trading_cleanup.py --clear

echo.
echo ====================================================================
echo   SESSION COMPLETE
echo ====================================================================
echo.
echo Final Results:
python scripts\show_practical_results.py

echo.
pause
exit /b 0
