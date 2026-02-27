@echo off
REM Run Auto-Heal Orchestrator
REM Detects and fixes common issues automatically

echo ======================================================================
echo SYSTEM3 AUTO-HEAL ORCHESTRATOR
echo ======================================================================
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

REM Run auto-heal
"%PYTHON%" -m core.engine.system3_auto_heal_orchestrator

echo.
echo ======================================================================
echo AUTO-HEAL COMPLETE
echo ======================================================================
echo.

pause
