@echo off
REM ====================================================================
REM RESTART FULLY AUTOMATED TRADING SYSTEM
REM Stops existing processes and restarts fresh
REM ====================================================================

title Restarting Automated Trading System

cd /d "%~dp0"

echo.
echo ====================================================================
echo   RESTARTING FULLY AUTOMATED TRADING SYSTEM
echo ====================================================================
echo.

REM Kill existing Python processes running run_live_chain.py
echo [INFO] Stopping existing processes...
taskkill /FI "WINDOWTITLE eq Paper Trading Engine*" /T /F >nul 2>&1
taskkill /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *run_live_chain*" /T /F >nul 2>&1
timeout /t 2 /nobreak >nul

echo [OK] Existing processes stopped
echo.

REM Wait a moment
timeout /t 1 /nobreak >nul

REM Start fresh
echo [INFO] Starting fresh system...
call START_FULLY_AUTOMATED_TRADING.bat
