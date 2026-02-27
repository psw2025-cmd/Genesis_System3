@echo off
REM ====================================================================
REM TEST TRI-STATE SYSTEM - 5 Minute Test
REM ====================================================================

title Test Tri-State System

cd /d "%~dp0"

echo.
echo ====================================================================
echo   TRI-STATE SYSTEM TEST
echo ====================================================================
echo.
echo This will test the tri-state system for 5 minutes:
echo   - LIVE mode (if market open)
echo   - SIMULATION mode (if market closed + sim enabled)
echo   - MARKET_CLOSED mode (if market closed + sim disabled)
echo.
echo Duration: 5 minutes
echo.
pause

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

if not exist "outputs" mkdir outputs
if not exist "config" mkdir config

echo.
echo [INFO] Starting 5-minute test...
echo.

venv\Scripts\python.exe scripts\test_tri_state_system.py

echo.
echo ====================================================================
echo   TEST COMPLETE
echo ====================================================================
echo.
echo Check outputs\chain_raw_live.csv for updates
echo Check logs for SIM_MODE messages
echo.
pause
