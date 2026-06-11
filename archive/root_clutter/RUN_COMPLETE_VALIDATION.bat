@echo off
REM Complete System Validation - Finds ALL Issues

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo ================================================================================
echo   COMPLETE SYSTEM VALIDATION
echo ================================================================================
echo.

echo [STEP 1] Fixing Import Paths...
python scripts\fix_all_imports.py

echo.
echo [STEP 2] Finding All Issues...
python scripts\find_all_issues.py

echo.
echo [STEP 3] Complete System Validation...
python scripts\complete_system_validator.py

echo.
echo [STEP 4] Comprehensive System Test...
python scripts\comprehensive_system_test.py

echo.
echo ================================================================================
echo   VALIDATION COMPLETE
echo ================================================================================
echo.

pause
