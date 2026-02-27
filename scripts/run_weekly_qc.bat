@echo off
REM Run weekly QC audit; archives to proof/qc_audit_YYYYMMDD.json
cd /d "%~dp0.."
python scripts\run_weekly_qc_audit.py
exit /b %ERRORLEVEL%
