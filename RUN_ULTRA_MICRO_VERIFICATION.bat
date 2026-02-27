@echo off
REM ====================================================================
REM ULTRA-MICRO VERIFICATION - COMPLETE SYSTEM CHECK
REM Runs all verification tests and shows proof
REM ====================================================================

title Ultra-Micro Verification

cd /d "%~dp0"

echo.
echo ====================================================================
echo   ULTRA-MICRO LEVEL VERIFICATION
echo   Complete System Check with World-Class Comparison
echo ====================================================================
echo.

REM Check venv
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Create outputs directory
if not exist "outputs" mkdir outputs

echo [STEP 1/3] Running Ultra-Micro Component Verification...
echo.
venv\Scripts\python.exe scripts\ultra_micro_verification.py
echo.

echo [STEP 2/3] Running World-Class Best Practices Comparison...
echo.
venv\Scripts\python.exe scripts\world_class_comparison.py
echo.

echo [STEP 3/3] Generating Final Verification Report...
echo.

REM Check if reports were generated
if exist "outputs\ultra_micro_verification_report.json" (
    echo   [OK] Ultra-micro verification report generated
) else (
    echo   [WARNING] Verification report not found
)

if exist "outputs\world_class_comparison_report.json" (
    echo   [OK] World-class comparison report generated
) else (
    echo   [WARNING] Comparison report not found
)

echo.
echo ====================================================================
echo   VERIFICATION COMPLETE
echo ====================================================================
echo.
echo Reports saved in: outputs\
echo   - ultra_micro_verification_report.json
echo   - world_class_comparison_report.json
echo.
echo See ULTRA_MICRO_VERIFICATION_COMPLETE.md for summary
echo.
pause
