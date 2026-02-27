@echo off
REM ====================================================================
REM ULTRA-MICRO VERIFICATION - WITH VISIBLE OUTPUT
REM ====================================================================

title Ultra-Micro Verification

cd /d "%~dp0"

echo.
echo ====================================================================
echo   ULTRA-MICRO VERIFICATION - RUNNING NOW
echo ====================================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

if not exist "outputs" mkdir outputs

echo [STEP 1] Running Component Verification...
echo.
venv\Scripts\python.exe scripts\ultra_micro_verification.py
echo.
echo [STEP 1] Complete
echo.

echo [STEP 2] Running World-Class Comparison...
echo.
venv\Scripts\python.exe scripts\world_class_comparison.py
echo.
echo [STEP 2] Complete
echo.

echo [STEP 3] Checking Generated Reports...
echo.
if exist "outputs\ultra_micro_verification_report.json" (
    echo   [OK] Verification report: outputs\ultra_micro_verification_report.json
    for %%F in ("outputs\ultra_micro_verification_report.json") do echo      Size: %%~zF bytes, Modified: %%~tF
) else (
    echo   [WARNING] Verification report not found
)

if exist "outputs\world_class_comparison_report.json" (
    echo   [OK] Comparison report: outputs\world_class_comparison_report.json
    for %%F in ("outputs\world_class_comparison_report.json") do echo      Size: %%~zF bytes, Modified: %%~tF
) else (
    echo   [WARNING] Comparison report not found
)

echo.
echo ====================================================================
echo   VERIFICATION COMPLETE
echo ====================================================================
echo.
pause
