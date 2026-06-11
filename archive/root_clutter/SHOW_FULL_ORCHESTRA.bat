@echo off
echo ================================================================================
echo   SHOWING FULL ORCHESTRA - COMPLETE SYSTEM DEMONSTRATION
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
echo [STEP 1] Running Full Orchestra Display...
echo.
python scripts\show_full_orchestra.py

echo.
echo ================================================================================
echo   DISPLAY COMPLETE
echo ================================================================================
echo.
pause
