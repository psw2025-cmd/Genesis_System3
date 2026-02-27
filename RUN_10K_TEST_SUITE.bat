@echo off
REM Run Comprehensive 10,000+ Test Suite

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo ================================================================================
echo   COMPREHENSIVE 10,000+ TEST SUITE
echo ================================================================================
echo.
echo This will run 10,000+ tests to validate the entire system...
echo.

python scripts\comprehensive_10k_test_suite.py

echo.
echo ================================================================================
echo   TEST SUITE COMPLETE
echo ================================================================================
echo.

pause
