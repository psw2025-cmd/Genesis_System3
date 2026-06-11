@echo off
REM Test Excel with Virtual Live Data
REM Generates realistic data and shows Excel working

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo ================================================================================
echo   TESTING EXCEL WITH VIRTUAL LIVE DATA
echo ================================================================================
echo.

python scripts\test_excel_with_virtual_live_data.py

echo.
echo ================================================================================
echo   TEST COMPLETE
echo ================================================================================
echo.
echo Excel file created: outputs\OptionChain_Master_VIRTUAL_TEST.xlsx
echo.
echo Open this file to see virtual live data with all calculations working!
echo.

pause
