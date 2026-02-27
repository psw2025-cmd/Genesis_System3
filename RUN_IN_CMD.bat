@echo off
REM ====================================================================
REM RUN IN CMD - Proper execution in Command Prompt
REM ====================================================================

cd /d "%~dp0"

echo.
echo ====================================================================
echo   RUNNING TRADING ENGINE IN COMMAND PROMPT
echo ====================================================================
echo.

REM Kill existing
taskkill /F /FI "WINDOWTITLE eq Paper Trading Engine*" /T >nul 2>&1
timeout /t 1 /nobreak >nul

echo Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

echo.
echo Running Python script directly...
echo Command: python -u scripts\smart_live_chain_runner.py --refresh 5 --market-check 30 --no-websocket
echo.
echo ====================================================================
echo.

python -u scripts\smart_live_chain_runner.py --refresh 5 --market-check 30 --no-websocket

echo.
echo ====================================================================
echo   SCRIPT EXITED
echo ====================================================================
echo.
pause
