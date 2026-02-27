@echo off
REM ====================================================================
REM QUICK DIAGNOSTIC - Check system status and restart if needed
REM ====================================================================

title Quick Diagnostic

cd /d "%~dp0"

echo.
echo ====================================================================
echo   QUICK SYSTEM DIAGNOSTIC
echo ====================================================================
echo.

REM Check if process is running
echo [1] Checking background process...
tasklist /FI "WINDOWTITLE eq Paper Trading Engine*" 2>nul | find /I "cmd.exe" >nul
if %errorlevel% == 0 (
    echo     ✅ Background process is running
) else (
    echo     ❌ Background process NOT running
    echo     [INFO] Will restart system...
    goto restart
)

REM Check file freshness
echo.
echo [2] Checking file freshness...
python -c "import os, time; from pathlib import Path; f=Path('outputs/chain_raw_live.csv'); age=(time.time()-f.stat().st_mtime)/60 if f.exists() else 999; print(f'    chain_raw_live.csv: {age:.1f} min old')"

REM Check log for errors
echo.
echo [3] Checking recent log entries...
if exist "logs\trading_engine.log" (
    echo     Last 3 lines:
    powershell -Command "Get-Content 'logs\trading_engine.log' -Tail 3 | ForEach-Object { Write-Host \"      $_\" }"
) else (
    echo     ⚠️  Log file not found
)

echo.
echo ====================================================================
echo   RECOMMENDATION
echo ====================================================================
echo.
echo If files are stale (^>2 min old), restart the system:
echo   RESTART_SYSTEM.bat
echo.
pause
exit /b 0

:restart
echo.
echo [INFO] Restarting system...
call RESTART_SYSTEM.bat
exit /b 0
