@echo off
REM Comprehensive Excel File Audit
REM Tests all sheets, cells, calculations, and virtual data

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo ================================================================================
echo   COMPREHENSIVE EXCEL AUDIT
echo ================================================================================
echo.

python scripts\comprehensive_excel_audit.py

echo.
echo ================================================================================
echo   AUDIT COMPLETE
echo ================================================================================
echo.

pause
