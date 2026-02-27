@echo off
REM ================================================================================
REM   START REAL LIVE TRADING - Real Market Data & Paper Trading
REM ================================================================================
title REAL LIVE TRADING - Live Market

cd /d "%~dp0"

echo ================================================================================
echo   REAL LIVE MARKET TRADING
echo ================================================================================
echo.
echo This will:
echo   1. Test real data fetch from live market
echo   2. Verify all columns are present
echo   3. Start real paper trading with live market data
echo.
echo WARNING: This uses REAL market data (not simulation)
echo.
pause

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo.
echo [STEP] Testing Real Data Fetch and Starting Trading...
echo.

python scripts\start_real_live_trading.py

echo.
echo ================================================================================
echo   TRADING COMPLETE
echo ================================================================================
echo.
pause
