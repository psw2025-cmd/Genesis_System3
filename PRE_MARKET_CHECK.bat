@echo off
REM ================================================================================
REM   PRE-MARKET CHECK - Run this before market opens
REM ================================================================================
title PRE-MARKET CHECK

cd /d "%~dp0"

echo ================================================================================
echo   PRE-MARKET CHECK
echo ================================================================================
echo.
echo This will verify everything is ready for live trading
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo.
python scripts\pre_market_check.py

echo.
pause
