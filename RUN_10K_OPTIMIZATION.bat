@echo off
REM 10,000 Strategy Optimization
REM Tests different combinations to find best profit generation

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo ================================================================================
echo   10,000 STRATEGY OPTIMIZATION
echo ================================================================================
echo.
echo This will test 10,000 different strategy combinations to find the best
echo profit generation approach. This may take 10-30 minutes.
echo.
echo Press Ctrl+C to cancel, or wait 5 seconds to continue...
timeout /t 5 /nobreak >nul

python scripts\optimize_10k_strategies.py

echo.
echo ================================================================================
echo   OPTIMIZATION COMPLETE
echo ================================================================================
echo.
echo Results saved to: outputs\strategy_optimization_results.json
echo.

pause
