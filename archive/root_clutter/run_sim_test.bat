@echo off
REM Simulation Test Runner - Windows Batch File
REM This script runs all simulation scenarios

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

REM Run all scenarios
python -m scripts.replay_test --all-scenarios --duration 10 --refresh 5
set RESULT=%errorlevel%

REM Deactivate virtual environment
deactivate

REM Exit with same code as Python script
exit /b %RESULT%
