@echo off
REM System3 Ultra: Full Daily Check (10-15 minutes)
REM Complete after-market review

echo ============================================================
echo SYSTEM3 ULTRA: FULL DAILY CHECK
echo ============================================================
echo.

REM Check if venv is activated, if not activate it
if not defined VIRTUAL_ENV (
    echo [INFO] Activating virtual environment...
    call "C:\Genesis_System3\venv\Scripts\activate.bat"
)

REM Run the PowerShell script in full mode
powershell -ExecutionPolicy Bypass -File "%~dp0system3_ultra_master_monitor.ps1" -Mode full

pause

