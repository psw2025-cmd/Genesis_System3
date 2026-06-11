@echo off
REM Comprehensive System Test - End-to-End Validation

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo ================================================================================
echo   COMPREHENSIVE SYSTEM TEST
echo ================================================================================
echo.

python scripts\comprehensive_system_test.py

echo.
echo ================================================================================
echo   TEST COMPLETE
echo ================================================================================
echo.

pause
