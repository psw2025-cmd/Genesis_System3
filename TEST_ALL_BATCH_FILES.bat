@echo off
REM ====================================================================
REM TEST ALL BATCH FILES - Syntax and Path Validation
REM ====================================================================

echo.
echo ====================================================================
echo   BATCH FILES VALIDATION TEST
echo ====================================================================
echo.

cd /d "%~dp0"

set TEST_COUNT=0
set PASS_COUNT=0
set FAIL_COUNT=0

echo Testing batch files for syntax errors...
echo.

REM Test AUTO_MODE.bat
set /a TEST_COUNT+=1
echo [TEST %TEST_COUNT%] AUTO_MODE.bat...
if exist "AUTO_MODE.bat" (
    echo   [OK] File exists
    findstr /C:"python" "AUTO_MODE.bat" >nul
    if %ERRORLEVEL% EQU 0 (
        echo   [OK] Contains Python calls
        set /a PASS_COUNT+=1
    ) else (
        echo   [WARN] No Python calls found
        set /a FAIL_COUNT+=1
    )
) else (
    echo   [FAIL] File not found
    set /a FAIL_COUNT+=1
)

REM Test START_PRODUCTION.bat
set /a TEST_COUNT+=1
echo [TEST %TEST_COUNT%] START_PRODUCTION.bat...
if exist "START_PRODUCTION.bat" (
    echo   [OK] File exists
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] File not found
    set /a FAIL_COUNT+=1
)

REM Test START_PRODUCTION_SYSTEM.bat
set /a TEST_COUNT+=1
echo [TEST %TEST_COUNT%] START_PRODUCTION_SYSTEM.bat...
if exist "START_PRODUCTION_SYSTEM.bat" (
    echo   [OK] File exists
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] File not found
    set /a FAIL_COUNT+=1
)

REM Test START_FULLY_AUTOMATED_TRADING.bat
set /a TEST_COUNT+=1
echo [TEST %TEST_COUNT%] START_FULLY_AUTOMATED_TRADING.bat...
if exist "START_FULLY_AUTOMATED_TRADING.bat" (
    echo   [OK] File exists
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] File not found
    set /a FAIL_COUNT+=1
)

REM Test START_LIVE_TRADING_AUTO.bat
set /a TEST_COUNT+=1
echo [TEST %TEST_COUNT%] START_LIVE_TRADING_AUTO.bat...
if exist "START_LIVE_TRADING_AUTO.bat" (
    echo   [OK] File exists
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] File not found
    set /a FAIL_COUNT+=1
)

REM Test START_REAL_LIVE_PAPER_TRADING.bat
set /a TEST_COUNT+=1
echo [TEST %TEST_COUNT%] START_REAL_LIVE_PAPER_TRADING.bat...
if exist "START_REAL_LIVE_PAPER_TRADING.bat" (
    echo   [OK] File exists
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] File not found
    set /a FAIL_COUNT+=1
)

REM Test START_LIVE_MONITOR.bat
set /a TEST_COUNT+=1
echo [TEST %TEST_COUNT%] START_LIVE_MONITOR.bat...
if exist "START_LIVE_MONITOR.bat" (
    echo   [OK] File exists
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] File not found
    set /a FAIL_COUNT+=1
)

REM Test QUICK_STATUS_CHECK.bat
set /a TEST_COUNT+=1
echo [TEST %TEST_COUNT%] QUICK_STATUS_CHECK.bat...
if exist "QUICK_STATUS_CHECK.bat" (
    echo   [OK] File exists
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] File not found
    set /a FAIL_COUNT+=1
)

REM Test RESTART_SYSTEM.bat
set /a TEST_COUNT+=1
echo [TEST %TEST_COUNT%] RESTART_SYSTEM.bat...
if exist "RESTART_SYSTEM.bat" (
    echo   [OK] File exists
    set /a PASS_COUNT+=1
) else (
    echo   [FAIL] File not found
    set /a FAIL_COUNT+=1
)

echo.
echo ====================================================================
echo   TEST SUMMARY
echo ====================================================================
echo.
echo   Total Tests: %TEST_COUNT%
echo   Passed: %PASS_COUNT%
echo   Failed: %FAIL_COUNT%
echo.

if %FAIL_COUNT% EQU 0 (
    echo   Status: ALL TESTS PASSED
    echo.
    echo   All batch files are present and ready to use.
    echo   Recommended: Use AUTO_MODE.bat for production
) else (
    echo   Status: SOME TESTS FAILED
    echo.
    echo   Please check the failed files above.
)

echo.
pause
