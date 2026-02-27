@echo off
REM ====================================================================
REM Simple Paper Trading - Single Window
REM Runs simulation and shows status
REM ====================================================================

echo.
echo ====================================================================
echo   PAPER TRADING SYSTEM - SIMPLE MODE
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

echo Starting simulation...
echo Press Ctrl+C to stop
echo.

REM Run simulation (will show output)
python -m scripts.replay_test --scenario TREND_UP --duration 10 --refresh 5

pause
