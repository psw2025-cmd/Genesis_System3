@echo off
REM Monitor OptionChain Master Performance

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

python scripts\monitor_optionchain_performance.py

pause
