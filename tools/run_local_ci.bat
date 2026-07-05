@echo off
REM Local CI — replaces GitHub Actions (no billing)
cd /d "%~dp0.."
set SYSTEM3_LOCAL=1
set SYSTEM3_API_BASE=http://127.0.0.1:8000
set LIVE_TRADING_ENABLED=0
set SYSTEM3_LIVE_TRADING_ALLOWED=0

if not exist "venv\Scripts\python.exe" (
    echo Creating venv...
    python -m venv venv
    venv\Scripts\pip.exe install -q -r dashboard\backend\requirements.txt 2>nul
)

venv\Scripts\python.exe tools\local_ci_runner.py %*
set RC=%ERRORLEVEL%
echo.
echo Report: reports\latest\local_ci\summary.md
exit /b %RC%
