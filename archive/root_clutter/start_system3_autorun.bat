@echo off
REM System3 Autorun Master Launcher
REM This batch file starts the System3 autorun master script

cd /d C:\Genesis_System3
set "PYTHON=C:\Genesis_System3\venv\Scripts\python.exe"

if not exist "%PYTHON%" (
	echo [ERROR] venv Python not found at %PYTHON%
	echo Please create/repair the virtual environment first.
	exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Enforce continuous heartbeat updates
set HEARTBEAT_CONTINUOUS=1
set HEARTBEAT_INTERVAL_SECONDS=60

REM Start the autorun master
"%PYTHON%" system3_autorun_master.py

REM If script exits, pause to see any errors
pause

