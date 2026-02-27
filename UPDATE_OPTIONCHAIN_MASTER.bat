@echo off
REM Automated OptionChain Master Update Script
REM Fetches fresh data, rebuilds Excel, verifies, and shows performance

cd /d "%~dp0"

echo ================================================================================
echo   OPTIONCHAIN MASTER - AUTOMATED UPDATE
echo ================================================================================
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

REM Run update script
echo Starting update process...
echo.

python scripts\update_optionchain_master.py %*

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================================
    echo   UPDATE COMPLETED SUCCESSFULLY
    echo ================================================================================
    echo.
    echo Excel file location: outputs\OptionChain_Master_v3_AI_FINAL.xlsx
    echo.
) else (
    echo.
    echo ================================================================================
    echo   UPDATE COMPLETED WITH ERRORS
    echo ================================================================================
    echo.
)

pause
