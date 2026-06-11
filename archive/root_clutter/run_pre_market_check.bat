@echo off
REM System3 Pre-Market Signal Dry-Run
REM Performs dry-run signal generation and safety checks before market opens

call C:\Genesis_System3\venv\Scripts\activate.bat
C:\Genesis_System3\venv\Scripts\python.exe core\validation\pre_market_signal_dryrun.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ================================================================================
    echo PRE-MARKET CHECK FAILED - DO NOT START MARKET SESSION
    echo ================================================================================
    exit /b 1
) else (
    echo.
    echo ================================================================================
    echo PRE-MARKET CHECK PASSED - Safe to start market session
    echo ================================================================================
    exit /b 0
)
