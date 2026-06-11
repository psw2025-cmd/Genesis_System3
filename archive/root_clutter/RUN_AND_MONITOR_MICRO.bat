@echo off
REM ====================================================================
REM RUN AND MONITOR - MICRO LEVEL
REM Starts system, monitors everything, finds and fixes issues
REM ====================================================================

title Run and Monitor - Micro Level

cd /d "%~dp0"

echo.
echo ====================================================================
echo   RUN AND MONITOR - MICRO LEVEL
echo   Starting system and monitoring everything
echo ====================================================================
echo.
echo This will:
echo   1. Start trading system
echo   2. Monitor all components continuously
echo   3. Check for warnings/errors
echo   4. Verify data updates automatically
echo   5. Test auto-triggers
echo   6. Show proof everything works
echo.
echo Monitoring Duration: 10 minutes (configurable)
echo.
pause

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs

echo.
echo [INFO] Starting run and monitor...
echo.

venv\Scripts\python.exe scripts\run_and_monitor_micro.py --duration 10

echo.
echo ====================================================================
echo   MONITORING COMPLETE
echo ====================================================================
echo.
echo Check outputs\run_and_monitor_report.json for detailed report
echo.
pause
