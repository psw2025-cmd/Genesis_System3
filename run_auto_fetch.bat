@echo off
REM Auto-fetch option chain - Hourly script for Windows Task Scheduler
REM This script runs the auto-fetch option chain script every hour

REM Change to project directory
cd /d C:\Genesis_System3
if errorlevel 1 (
    echo ERROR: Failed to change to project directory
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)

REM Run the auto-fetch script
python -m core.engine.auto_fetch_option_chain_hourly
set FETCH_RESULT=%errorlevel%

REM Deactivate virtual environment
deactivate

REM Log result to file
if not exist storage\logs mkdir storage\logs
echo %date% %time% - Auto-fetch completed with exit code %FETCH_RESULT% >> storage\logs\auto_fetch.log

REM Exit with same code as Python script
exit /b %FETCH_RESULT%
