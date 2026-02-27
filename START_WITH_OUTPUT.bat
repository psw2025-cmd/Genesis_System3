@echo off
REM ====================================================================
REM START WITH OUTPUT - Ensures console output is visible
REM ====================================================================

title Start Trading System with Output

cd /d "%~dp0"

echo.
echo ====================================================================
echo   STARTING TRADING SYSTEM WITH CONSOLE OUTPUT
echo ====================================================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

REM Kill any existing processes
taskkill /F /FI "WINDOWTITLE eq Paper Trading Engine*" /T >nul 2>&1
timeout /t 2 /nobreak >nul

call venv\Scripts\activate.bat

if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs

echo [INFO] Starting trading system...
echo [INFO] You should see output immediately in the window
echo.

REM Start with explicit Python execution
start "Paper Trading Engine" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python -u scripts\smart_live_chain_runner.py --refresh 5 --market-check 30 --no-websocket"

echo [OK] Trading system started
echo [INFO] Check the "Paper Trading Engine" window for output
echo [INFO] You should see startup messages immediately
echo.
echo If window is blank, wait 10 seconds for initialization
echo.
pause
