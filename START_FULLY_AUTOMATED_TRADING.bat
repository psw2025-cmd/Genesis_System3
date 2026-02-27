@echo off
REM ====================================================================
REM FULLY AUTOMATED PAPER TRADING SYSTEM
REM Runs everything in background - User only sees profit and trades
REM ====================================================================

title Fully Automated Paper Trading - Profit Monitor

cd /d "%~dp0"

REM Check venv
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

REM Create directories
if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs
if not exist "storage\live" mkdir storage\live

echo.
echo ====================================================================
echo   FULLY AUTOMATED PAPER TRADING SYSTEM
echo   Profit-Focused Dashboard
echo ====================================================================
echo.
echo [INFO] Starting automated system...
echo [INFO] All background processes will run automatically
echo [INFO] You will only see: PnL, Trades, and Profit
echo.

REM Start paper trading in background (minimized) - disable WebSocket for reliability
echo [INFO] Starting background trading engine...
echo [INFO] Using REST API only (WebSocket disabled for reliability)
start /MIN "Paper Trading Engine" cmd /c "cd /d %~dp0 && venv\Scripts\python.exe scripts\run_live_chain.py --refresh 5 --ignore-market-hours --no-websocket >> logs\trading_engine.log 2>&1"

REM Wait a moment for system to initialize
timeout /t 5 /nobreak >nul

REM Start the profit-focused monitor (this is what user sees)
echo [INFO] Starting Profit Monitor...
echo [INFO] This window shows: PnL, Trades, Profit
echo.
timeout /t 2 /nobreak >nul

venv\Scripts\python.exe scripts\profit_focused_monitor.py

pause
