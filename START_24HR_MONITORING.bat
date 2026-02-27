@echo off
echo ========================================
echo STARTING 24-HOUR DASHBOARD MONITORING
echo ========================================
echo.
echo This will run continuously for 24 hours
echo Monitoring dashboard health, detecting issues,
echo auto-resolving problems, and tracking improvements.
echo.
echo Press Ctrl+C to stop monitoring
echo.
pause

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

REM Start monitoring
python scripts\dashboard_24hr_monitor.py

pause
