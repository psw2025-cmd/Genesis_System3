@echo off
REM ====================================================================
REM START LIVE PAPER TRADING MONITOR
REM Real-time dashboard showing data fetch, trading activity, and performance
REM ====================================================================

title Live Paper Trading Monitor

echo.
echo ====================================================================
echo   LIVE PAPER TRADING MONITOR
echo   Real-time Dashboard
echo ====================================================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo [INFO] Starting live monitor...
echo [INFO] This will show:
echo   - Real-time data fetching status
echo   - Paper trading activity
echo   - PnL and performance metrics
echo   - System health
echo   - Production readiness check
echo.
echo Press Ctrl+C to stop
echo.
timeout /t 2 /nobreak >nul

venv\Scripts\python.exe scripts\live_paper_trading_monitor.py

pause
