@echo off
REM System3 Live Day Autopilot - Batch Wrapper
REM Single-button full-day autopilot for System3 (DRY-RUN ONLY)

echo ============================================================
echo SYSTEM3 LIVE DAY AUTOPILOT
echo ============================================================
echo.
echo [SAFETY] DRY-RUN MODE ONLY - No real trading
echo.

set "PYTHON=%~dp0venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo [ERROR] venv Python not found at %PYTHON%
    echo Please create/repair the virtual environment first.
    exit /b 1
)

REM Check if venv is activated, if not activate it
if not defined VIRTUAL_ENV (
    echo [INFO] Activating virtual environment...
    call "%~dp0venv\Scripts\activate.bat"
)

REM Change to project root
cd /d "%~dp0"

REM Run the autopilot script
echo [INFO] Starting autopilot...
echo.
"%PYTHON%" system3_live_day_autopilot.py

echo.
echo ============================================================
echo Autopilot finished
echo ============================================================
pause

