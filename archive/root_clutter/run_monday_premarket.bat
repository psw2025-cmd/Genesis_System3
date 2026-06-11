@echo off
REM GENESIS System3 - Monday Pre-Market Sequence Launcher
REM Activates venv and runs automated pre-market validation

echo ====================================
echo GENESIS System3
echo Monday Pre-Market Sequence
echo ====================================
echo.

cd /d C:\Genesis_System3
set "PYTHON=C:\Genesis_System3\venv\Scripts\python.exe"

if not exist "%PYTHON%" (
	echo [ERROR] venv Python not found at %PYTHON%
	echo Please create/repair the virtual environment first.
	exit /b 1
)

call venv\Scripts\activate.bat

echo Starting pre-market sequence...
echo.

"%PYTHON%" system3_monday_premarket_sequence.py

echo.
echo ====================================
echo Sequence Complete
echo ====================================
echo Check the MONDAY_PREMARKET_EXECUTION_SUMMARY_*.md file for results
echo.

pause
