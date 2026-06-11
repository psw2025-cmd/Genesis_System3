@echo off
REM System3 Ultra: Daily Quick Check (2-3 minutes)
REM Quick health check for daily monitoring

echo ============================================================
echo SYSTEM3 ULTRA: DAILY QUICK CHECK
echo ============================================================
echo.

REM Check if venv is activated, if not activate it
if not defined VIRTUAL_ENV (
    echo [INFO] Activating virtual environment...
    call "C:\Genesis_System3\venv\Scripts\activate.bat"
)

REM Run the PowerShell script in daily mode
powershell -ExecutionPolicy Bypass -File "%~dp0system3_ultra_master_monitor.ps1" -Mode daily

pause

