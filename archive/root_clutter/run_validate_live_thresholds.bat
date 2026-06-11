@echo off
REM System3 Static Threshold Sanity Check
REM Validates live thresholds JSON and verifies signal counts

call C:\Genesis_System3\venv\Scripts\activate.bat
C:\Genesis_System3\venv\Scripts\python.exe core\validation\validate_live_thresholds.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ================================================================================
    echo VALIDATION FAILED - DO NOT START MARKET SESSION
    echo ================================================================================
    exit /b 1
) else (
    echo.
    echo ================================================================================
    echo VALIDATION PASSED - Thresholds are safe
    echo ================================================================================
    exit /b 0
)

