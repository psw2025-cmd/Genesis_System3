@echo off
REM System3 Ultra: Daily All-In-One Health & Backup Script (Batch Wrapper)

echo ============================================================
echo SYSTEM3 ULTRA: DAILY ALL-IN-ONE HEALTH ^& BACKUP
echo ============================================================
echo.

REM Check if venv is activated, if not activate it
if not defined VIRTUAL_ENV (
    echo [INFO] Activating virtual environment...
    call "%~dp0venv\Scripts\activate.bat"
)

REM Run the PowerShell script
powershell -ExecutionPolicy Bypass -File "%~dp0system3_ultra_daily_all.ps1"

pause

