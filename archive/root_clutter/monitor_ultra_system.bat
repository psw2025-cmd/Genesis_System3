@echo off
REM System3 Ultra: Daily Monitoring Script (Batch Wrapper)
REM This batch file runs the PowerShell monitoring script

echo ============================================================
echo SYSTEM3 ULTRA: DAILY MONITORING CHECK
echo ============================================================
echo.

REM Check if venv is activated, if not activate it
if not defined VIRTUAL_ENV (
    echo [INFO] Activating virtual environment...
    call "C:\Genesis_System3\venv\Scripts\activate.bat"
)

REM Run the PowerShell script
powershell -ExecutionPolicy Bypass -File "%~dp0monitor_ultra_system.ps1"

pause

