@echo off
REM System3 Daily Safety Checklist
REM Orchestrates all pre-market safety checks before starting market session

echo ================================================================================
echo SYSTEM3 DAILY SAFETY CHECKLIST
echo ================================================================================
echo.
echo This script runs all pre-market safety checks in order.
echo DO NOT START MARKET SESSION if any check fails.
echo.
echo ================================================================================
echo.

call C:\Genesis_System3\venv\Scripts\activate.bat

REM Step 1: Static threshold sanity check
echo [1/3] Running static threshold sanity check...
echo --------------------------------------------------------------------------------
C:\Genesis_System3\venv\Scripts\python.exe core\validation\validate_live_thresholds.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ================================================================================
    echo CHECK 1 FAILED - DO NOT START MARKET SESSION
    echo ================================================================================
    exit /b 1
)
echo.

REM Step 2: Pre-market signal dry-run
echo [2/3] Running pre-market signal dry-run...
echo --------------------------------------------------------------------------------
C:\Genesis_System3\venv\Scripts\python.exe core\validation\pre_market_signal_dryrun.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ================================================================================
    echo CHECK 2 FAILED - DO NOT START MARKET SESSION
    echo ================================================================================
    exit /b 1
)
echo.

REM Step 3: Signal engine self-test
echo [3/3] Running signal engine self-test...
echo --------------------------------------------------------------------------------
C:\Genesis_System3\venv\Scripts\python.exe core\engine\system3_signal_engine_self_test.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ================================================================================
    echo CHECK 3 FAILED - DO NOT START MARKET SESSION
    echo ================================================================================
    exit /b 1
)
echo.

REM All checks passed
echo ================================================================================
echo ALL CHECKS PASSED - SAFE TO START MARKET SESSION
echo ================================================================================
echo.
echo You can now run: START_AUTORUN_AND_WATCHDOG.bat
echo.
exit /b 0

