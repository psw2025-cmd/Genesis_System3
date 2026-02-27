@echo off
REM ====================================================================
REM Complete Paper Trading System - Single Batch File
REM Runs simulation + monitoring automatically
REM ====================================================================

echo.
echo ====================================================================
echo   PAPER TRADING SYSTEM - COMPLETE AUTOMATION
echo ====================================================================
echo.

REM Set working directory
cd /d "%~dp0"

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please create venv first: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if required files exist
if not exist "option_chain_ALL_INDICES.csv" (
    echo WARNING: option_chain_ALL_INDICES.csv not found!
    echo System will use simulation data.
    echo.
)

REM Create outputs directory if it doesn't exist
if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs

echo.
echo [1/3] Starting simulation in background...
echo.

REM Start simulation in a new window (non-blocking)
start "Paper Trading Simulation" cmd /k "venv\Scripts\activate.bat && python -m scripts.replay_test --scenario TREND_UP --duration 10 --refresh 5"

REM Wait a few seconds for simulation to initialize
timeout /t 5 /nobreak >nul

echo [2/3] Waiting for simulation to initialize...
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Starting live monitor...
echo.
echo ====================================================================
echo   MONITORING PAPER TRADING - Press Ctrl+C to stop
echo ====================================================================
echo.

REM Run monitor in current window
python scripts\monitor_paper_trades.py

REM If monitor exits, show status
echo.
echo ====================================================================
echo   Simulation is still running in background window
echo   To stop simulation, close the "Paper Trading Simulation" window
echo ====================================================================
echo.

pause
