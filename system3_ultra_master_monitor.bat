@echo off
REM System3 Ultra: Master Monitoring & Operations Script (Batch Wrapper)
REM This batch file runs the comprehensive PowerShell monitoring script

echo ============================================================
echo SYSTEM3 ULTRA: MASTER MONITORING ^& OPERATIONS
echo ============================================================
echo.

REM Check if venv is activated, if not activate it
if not defined VIRTUAL_ENV (
    echo [INFO] Activating virtual environment...
    call "C:\Genesis_System3\venv\Scripts\activate.bat"
)

REM Run the PowerShell script with menu mode
powershell -ExecutionPolicy Bypass -File "%~dp0system3_ultra_master_monitor.ps1" -Mode menu

pause

