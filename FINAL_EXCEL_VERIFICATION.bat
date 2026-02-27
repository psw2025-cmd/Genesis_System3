@echo off
REM Final End-to-End Excel Verification
REM Tests everything with virtual live data

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo ================================================================================
echo   FINAL EXCEL VERIFICATION - VIRTUAL LIVE DATA TEST
echo ================================================================================
echo.

python scripts\final_excel_verification.py

echo.
echo ================================================================================
echo   VERIFICATION COMPLETE
echo ================================================================================
echo.
echo Test Excel file: outputs\OptionChain_Master_VIRTUAL_TEST.xlsx
echo Production Excel: outputs\OptionChain_Master_v3_AI_FINAL.xlsx
echo.
echo Open the Excel files to verify all sheets, cells, and calculations!
echo.

pause
