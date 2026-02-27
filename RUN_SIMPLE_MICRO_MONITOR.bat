@echo off
REM ====================================================================
REM SIMPLE MICRO-LEVEL MONITOR
REM Monitors system without starting it (assumes system is already running)
REM ====================================================================

title Simple Micro Monitor

cd /d "%~dp0"

echo.
echo ====================================================================
echo   SIMPLE MICRO-LEVEL MONITOR
echo   Monitoring all components, data flow, and auto-triggers
echo ====================================================================
echo.
echo This monitor assumes the trading system is already running.
echo If not, start it first using AUTO_MODE.bat or similar.
echo.
echo Press Ctrl+C to stop monitoring.
echo.
pause

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

if not exist "outputs" mkdir outputs

echo.
echo [INFO] Starting micro-level monitoring...
echo.

venv\Scripts\python.exe scripts\simple_micro_monitor.py

echo.
echo ====================================================================
echo   MONITORING COMPLETE
echo ====================================================================
echo.
pause
