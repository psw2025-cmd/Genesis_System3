@echo off
REM System3 AngelOne DRY-RUN Autopilot Day - Single Button Launcher

cd /d C:\Genesis_System3

set "PYTHON=C:\Genesis_System3\venv\Scripts\python.exe"

if not exist "%PYTHON%" (
	echo [ERROR] venv Python not found at %PYTHON%
	echo Please create/repair the virtual environment first.
	exit /b 1
)

echo ============================================================
echo SYSTEM3 ANGELONE DRY-RUN AUTOPILOT DAY
echo ============================================================
echo.
echo [SAFETY] DRY-RUN MODE ONLY - NO REAL TRADES
echo.

echo Activating venv...
call venv\Scripts\activate

echo.
echo Starting System3 AngelOne DRY-RUN Autopilot Day...
echo (Duration: 360 minutes)
echo.

"%PYTHON%" system3_live_day_autopilot.py --duration-minutes 360

echo.
echo ===== AUTOPILOT SESSION ENDED =====
echo Check logs\live_day_autopilot_YYYYMMDD.log and other autopilot logs for details.
echo.
pause


