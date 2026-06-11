@echo off
REM ====================================================================
REM VERIFY TRI-STATE SYSTEM - Show proof it's working
REM ====================================================================

title Verify Tri-State System

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo.
echo Verifying tri-state system...
echo.

venv\Scripts\python.exe scripts\verify_tri_state_working.py

echo.
pause
