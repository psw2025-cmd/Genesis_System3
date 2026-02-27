@echo off
REM 1-Month All-Day Trading Simulation
REM Tests optimized strategy over 30 trading days

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo ================================================================================
echo   1-MONTH ALL-DAY TRADING SIMULATION
echo ================================================================================
echo.
echo This will simulate 30 trading days with the optimized strategy.
echo This may take 10-30 minutes depending on system performance.
echo.
echo Press Ctrl+C to cancel, or wait 5 seconds to continue...
timeout /t 5 /nobreak >nul

python scripts\simulate_1month_trading.py

echo.
echo ================================================================================
echo   SIMULATION COMPLETE
echo ================================================================================
echo.
echo Results saved to: outputs\1month_simulation_results.json
echo.

pause
