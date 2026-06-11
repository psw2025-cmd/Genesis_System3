@echo off
REM System3 Pre-Market Health Check
REM Run this before starting the autorun system

cd /d C:\Genesis_System3
set "PYTHON=C:\Genesis_System3\venv\Scripts\python.exe"

if not exist "%PYTHON%" (
	echo [ERROR] venv Python not found at %PYTHON%
	echo Please create/repair the virtual environment first.
	exit /b 1
)

call venv\Scripts\activate.bat

echo ============================================
echo SYSTEM3 PRE-MARKET HEALTH CHECK
echo ============================================
echo.

"%PYTHON%" system3_premarket_health_check.py

echo.
echo ============================================
echo Health check complete. Review results above.
echo ============================================
pause

