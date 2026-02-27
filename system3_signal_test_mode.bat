@echo off
cd /d C:\Genesis_System3

set "PYTHON=C:\Genesis_System3\venv\Scripts\python.exe"

if not exist "%PYTHON%" (
	echo [ERROR] venv Python not found at %PYTHON%
	echo Please create/repair the virtual environment first.
	exit /b 1
)

echo ============================================
echo SYSTEM3 SIGNAL TEST MODE (DRY-RUN ANALYSIS)
echo ============================================
echo.

call venv\Scripts\activate

"%PYTHON%" system3_signal_test_mode.py --lookback-snapshots 30

echo.
echo ===== SIGNAL TEST MODE FINISHED =====
echo Check logs\signal_test_mode_YYYYMMDD_HHMM.log for details.
echo.
pause


