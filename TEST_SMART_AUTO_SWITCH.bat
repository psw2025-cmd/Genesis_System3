@echo off
REM ====================================================================
REM TEST SMART AUTO-SWITCH SYSTEM
REM Verifies market detection and auto-switching works
REM ====================================================================

title Test Smart Auto-Switch

cd /d "%~dp0"

echo.
echo ====================================================================
echo   TESTING SMART AUTO-SWITCH SYSTEM
echo ====================================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo [TEST 1] Market Detection Test...
echo.
venv\Scripts\python.exe scripts\test_smart_auto_switch.py
echo.

echo [TEST 2] Smart Auto-Switch System Test...
echo.
venv\Scripts\python.exe scripts\smart_market_auto_switch.py
echo.

echo ====================================================================
echo   TEST COMPLETE
echo ====================================================================
echo.
pause
