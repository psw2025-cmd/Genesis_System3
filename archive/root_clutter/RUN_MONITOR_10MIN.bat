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
echo.
echo The monitor will show:
echo   - Live PnL updates
echo   - Open positions
echo   - Recent trades
echo   - Trade signals
echo.
echo Updates every 3 seconds
echo Press Ctrl+C to stop early
echo.
echo ====================================================================
echo.

REM Run monitor
python scripts\monitor_10min.py

echo.
echo ====================================================================
echo   Monitor completed
echo ====================================================================
echo.
pause
