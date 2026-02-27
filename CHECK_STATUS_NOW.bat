@echo off
REM ====================================================================
REM CHECK STATUS NOW - Simple status check
REM ====================================================================

title Check Status Now

cd /d "%~dp0"

echo.
echo ====================================================================
echo   CURRENT SYSTEM STATUS
echo ====================================================================
echo.

if not exist "outputs\chain_raw_live.csv" (
    echo [STATUS] chain_raw_live.csv: MISSING
    echo [ACTION] Trading system not running or not started yet
    goto :end
)

for %%F in ("outputs\chain_raw_live.csv") do (
    set "FILETIME=%%~tF"
    echo [FILE] chain_raw_live.csv
    echo [TIME] Last Modified: %%~tF
    echo [SIZE] %%~zF bytes
)

echo.
echo [CHECKING] Waiting 10 seconds to see if file updates...
echo.

REM Get initial timestamp
for %%F in ("outputs\chain_raw_live.csv") do set "INITIAL_TIME=%%~tF"

timeout /t 10 /nobreak >nul

REM Check if updated
for %%F in ("outputs\chain_raw_live.csv") do (
    if "%%~tF" NEQ "%INITIAL_TIME%" (
        echo [RESULT] ✅ FILE IS UPDATING - System is working!
    ) else (
        echo [RESULT] ⚠️  FILE NOT UPDATING - System may be stuck
        echo.
        echo [TROUBLESHOOTING]
        echo   1. Check the "Trading System" window for errors
        echo   2. Look for connection errors or API issues
        echo   3. System may be in initialization (wait 30 more seconds)
        echo   4. If market is closed, system uses virtual data (may be slower)
    )
)

:end
echo.
echo ====================================================================
echo.
pause
