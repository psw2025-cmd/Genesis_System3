@echo off
cd /d C:\Genesis_System3
set "PYTHON=C:\Genesis_System3\venv\Scripts\python.exe"

if not exist "%PYTHON%" (
	echo [ERROR] venv Python not found at %PYTHON%
	echo Please create/repair the virtual environment first.
	exit /b 1
)

call venv\Scripts\activate.bat
"%PYTHON%" core\engine\system3_phase223_threshold_optimizer.py
pause

