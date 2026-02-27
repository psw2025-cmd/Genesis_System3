@echo off
REM ====================================================================
REM START PAPER TRADING - Main Entry Point
REM Complete end-to-end automation
REM ====================================================================

title Paper Trading System

echo.
echo ====================================================================
echo   PAPER TRADING SYSTEM - STARTING
echo ====================================================================
echo.

cd /d "%~dp0"

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

echo [INFO] Virtual environment activated
echo [INFO] Directories checked
echo.

REM Check if base CSV exists (optional)
if not exist "option_chain_ALL_INDICES.csv" (
    echo [WARN] option_chain_ALL_INDICES.csv not found
    echo [INFO] System will use simulation data
    echo.
)

echo [INFO] Starting simulation...
echo [INFO] Duration: 10 minutes
echo [INFO] Refresh: 5 seconds
echo.

REM Start simulation in background (non-blocking)
start /MIN "Paper Trading Sim" cmd /c "cd /d %~dp0 && call venv\Scripts\activate.bat && python -m scripts.replay_test --scenario TREND_UP --duration 10 --refresh 5"

REM Wait for simulation to initialize
echo [INFO] Waiting for simulation to initialize...
timeout /t 8 /nobreak >nul

echo [INFO] Simulation started in background
echo [INFO] Starting status monitor...
echo.
echo ====================================================================
echo   PAPER TRADING STATUS MONITOR
echo   Updates every 5 seconds
echo   Press Ctrl+C to stop monitoring (simulation continues)
echo ====================================================================
echo.

REM Run monitor with auto-refresh
:MONITOR_LOOP
cls
echo ====================================================================
echo   PAPER TRADING STATUS - %date% %time%
echo ====================================================================
echo.

python scripts\check_paper_trading_status.py 2>nul

if errorlevel 1 (
    echo [INFO] Waiting for data...
    timeout /t 3 /nobreak >nul
) else (
    timeout /t 5 /nobreak >nul
)

goto MONITOR_LOOP
