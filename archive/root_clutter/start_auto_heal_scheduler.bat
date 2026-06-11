@echo off
REM Start Auto-Heal Scheduler
REM Runs continuously with automatic healing

echo ======================================================================
echo SYSTEM3 AUTO-HEAL SCHEDULER
echo ======================================================================
echo.
echo Starting continuous auto-heal monitoring...
echo Press Ctrl+C to stop
echo.

set "PYTHON=%~dp0venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo [ERROR] venv Python not found at %PYTHON%
    echo Please create/repair the virtual environment first.
    exit /b 1
)

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Run scheduler
"%PYTHON%" system3_auto_heal_scheduler.py

echo.
echo ======================================================================
echo SCHEDULER STOPPED
echo ======================================================================
echo.

pause
