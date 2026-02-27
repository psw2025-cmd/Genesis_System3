@echo off
REM ====================================================================
REM Run Paper Trading Monitor for 10 Minutes
REM ====================================================================

echo.
echo ====================================================================
echo   PAPER TRADING MONITOR - 10 MINUTES
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

echo Starting monitor for 10 minutes...
echo Press Ctrl+C to stop early
echo.

REM Run monitor (will run until Ctrl+C or script timeout)
python scripts\monitor_paper_trades.py

echo.
echo Monitor stopped.
pause
