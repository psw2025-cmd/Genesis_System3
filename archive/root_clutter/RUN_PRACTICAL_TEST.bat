@echo off
REM ====================================================================
REM Run Complete Practical Test - Full System
REM ====================================================================

echo.
echo ====================================================================
echo   PRACTICAL TEST - COMPLETE SYSTEM RUN
echo ====================================================================
echo.

cd /d "%~dp0"

REM Activate venv
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

REM Clean old files
echo [1/4] Cleaning old output files...
if exist "outputs\paper_trades_live.csv" del "outputs\paper_trades_live.csv"
if exist "outputs\pnl_live.json" del "outputs\pnl_live.json"
if exist "outputs\positions_live.json" del "outputs\positions_live.json"
echo   Done.
echo.

REM Start simulation in background
echo [2/4] Starting simulation (5 minutes, TREND_UP scenario)...
start /MIN "Paper Trading Sim" cmd /c "cd /d %~dp0 && call venv\Scripts\activate.bat && python -m scripts.replay_test --scenario TREND_UP --duration 5 --refresh 5"
echo   Simulation started in background.
echo.

REM Wait for data
echo [3/4] Waiting for data generation (15 seconds)...
timeout /t 15 /nobreak >nul
echo   Done.
echo.

REM Show initial results
echo [4/4] Showing practical results...
echo.
python scripts\show_practical_results.py

echo.
echo ====================================================================
echo   Test is running. Monitor will show live updates.
echo   Simulation will run for 5 minutes.
echo ====================================================================
echo.
echo Press any key to start the monitor (10 minutes)...
pause >nul

REM Start monitor
echo.
echo Starting monitor for 10 minutes...
echo.
python scripts\monitor_10min.py

REM Final results
echo.
echo ====================================================================
echo   FINAL RESULTS
echo ====================================================================
echo.
python scripts\show_practical_results.py

echo.
echo ====================================================================
echo   Test Complete
echo ====================================================================
echo.
pause
