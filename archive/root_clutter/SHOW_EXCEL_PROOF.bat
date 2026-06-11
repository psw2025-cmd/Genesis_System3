@echo off
echo ================================================================================
echo   SHOWING EXCEL PROOF - VERIFICATION FROM ACTUAL FILE
echo ================================================================================
echo.

cd /d "%~dp0"

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo.
python scripts\verify_excel_output.py

echo.
pause
