@echo off
REM Live Option Chain Runner - Windows Batch File
REM This script runs the live option chain system

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

REM Run the live chain script
python -m scripts.run_live_chain %*
set RESULT=%errorlevel%

REM Deactivate virtual environment
deactivate

REM Exit with same code as Python script
exit /b %RESULT%
