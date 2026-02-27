@echo off
REM ====================================================================
REM Paper Trading with Auto Status Updates
REM Runs simulation and shows status every 10 seconds
REM ====================================================================

echo.
echo ====================================================================
echo   PAPER TRADING SYSTEM - WITH STATUS UPDATES
echo ====================================================================
echo.

cd /d "%~dp0"

REM Activate venv
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

REM Create directories
if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs

echo Starting simulation in background...
echo.

REM Start simulation in background
start /B python -m scripts.replay_test --scenario TREND_UP --duration 10 --refresh 5

REM Wait for initialization
timeout /t 8 /nobreak >nul

echo Simulation started!
echo Showing status updates every 10 seconds...
echo Press Ctrl+C to stop
echo.

:LOOP
cls
echo ====================================================================
echo   PAPER TRADING STATUS - %date% %time%
echo ====================================================================
echo.

REM Show status
python scripts\check_paper_trading_status.py

echo.
echo Next update in 10 seconds... (Press Ctrl+C to stop)
timeout /t 10 /nobreak >nul

goto LOOP
