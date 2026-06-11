@echo off
REM Run Auto-Heal Comprehensive Test Suite
REM Tests all auto-healing functionality

echo ======================================================================
echo SYSTEM3 AUTO-HEAL COMPREHENSIVE TEST SUITE
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

REM Run test suite
"%PYTHON%" test_auto_heal_comprehensive.py

echo.
echo ======================================================================
echo TEST SUITE COMPLETE
echo ======================================================================
echo.

pause
