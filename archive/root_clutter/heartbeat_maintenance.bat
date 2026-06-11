@echo off
REM Heartbeat maintenance: freshness check + archive snapshot
REM Schedule this via Windows Task Scheduler (e.g., every 5 minutes for freshness; hourly for archive)

setlocal
cd /d C:\Genesis_System3

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Freshness check (fails non-zero if stale)
python check_heartbeat_freshness.py --threshold-seconds 180
if %ERRORLEVEL% NEQ 0 (
    echo Heartbeat freshness check failed. See output above.
)

REM Archive snapshot (optional retention via env HEARTBEAT_ARCHIVE_RETENTION_DAYS)
python archive_heartbeat.py

endlocal
