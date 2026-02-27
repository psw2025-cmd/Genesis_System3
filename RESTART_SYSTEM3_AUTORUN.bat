@echo off
REM System3 Autorun - Restart Script (After Fixes)
REM This restarts both master and watchdog with the fixed code

cd /d C:\Genesis_System3

set "PYTHON=C:\Genesis_System3\venv\Scripts\python.exe"

if not exist "%PYTHON%" (
	echo [ERROR] venv Python not found at %PYTHON%
	echo Please create/repair the virtual environment first.
	exit /b 1
)

echo ============================================
echo SYSTEM3 AUTORUN - RESTARTING WITH FIXES
echo ============================================
echo.
echo Stopping any existing processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
echo.
echo Starting watchdog in new window...
start "System3 Watchdog" cmd /k "cd /d C:\Genesis_System3 && venv\Scripts\activate.bat && \"%PYTHON%\" system3_watchdog.py"
timeout /t 3 /nobreak >nul
echo.
echo Starting master in current window...
echo.
echo ============================================
echo MASTER WILL START NOW
echo ============================================
echo.
echo Watchdog is running in a separate window.
echo This window will run the master script.
echo.
echo Press Ctrl+C to stop the master.
echo.
echo ============================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start master
"%PYTHON%" system3_autorun_master.py

pause

