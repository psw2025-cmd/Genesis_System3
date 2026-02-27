@echo off
REM Run daily health monitoring; appends to proof/MONITORING_LOG_YYYYMMDD.txt
cd /d "%~dp0.."
python scripts\monitor_health.py
exit /b %ERRORLEVEL%
