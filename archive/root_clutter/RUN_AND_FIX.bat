@echo off
REM ====================================================================
REM RUN AND FIX - Comprehensive test and fix script
REM ====================================================================

title Run and Fix Trading Engine

cd /d "%~dp0"

echo.
echo ====================================================================
echo   RUNNING AND FIXING TRADING ENGINE
echo ====================================================================
echo.

REM Kill existing processes
echo [1/5] Killing existing processes...
taskkill /F /FI "WINDOWTITLE eq Paper Trading Engine*" /T >nul 2>&1
timeout /t 1 /nobreak >nul
echo   [OK] Processes killed
echo.

REM Test Python script directly
echo [2/5] Testing Python script directly...
cd /d "%~dp0"
call venv\Scripts\activate.bat
echo   Running test script...
python test_runner_direct.py
set TEST_RESULT=%ERRORLEVEL%
if %TEST_RESULT% EQU 0 (
    echo   [OK] Test passed
) else (
    echo   [ERROR] Test failed with code %TEST_RESULT%
    echo   [INFO] Check output above for errors
    pause
    exit /b 1
)
echo.

REM Start the actual system
echo [3/5] Starting trading engine in new window...
start "Paper Trading Engine" cmd /k "cd /d %~dp0 && run_trading_engine.bat"
echo   [OK] Window opened
echo.

REM Wait a bit
echo [4/5] Waiting 15 seconds for initialization...
timeout /t 15 /nobreak >nul
echo   [OK] Wait complete
echo.

REM Check if files are updating
echo [5/5] Checking if system is running...
if exist "outputs\chain_raw_live.csv" (
    echo   [OK] chain_raw_live.csv exists
    for %%F in ("outputs\chain_raw_live.csv") do (
        set FILE_TIME=%%~tF
        echo   File timestamp: %%~tF
    )
) else (
    echo   [WARNING] chain_raw_live.csv not found
)

echo.
echo ====================================================================
echo   CHECK THE "Paper Trading Engine" WINDOW
echo   It should show continuous output and cycles
echo ====================================================================
echo.
pause
