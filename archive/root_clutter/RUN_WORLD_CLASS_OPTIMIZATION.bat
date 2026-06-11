@echo off
REM World-Class Optimization - Highest Level Performance Testing

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo ================================================================================
echo   WORLD-CLASS OPTIMIZATION - HIGHEST LEVEL
echo ================================================================================
echo.
echo This will test multiple advanced techniques to find the best configuration.
echo This may take 5-10 minutes.
echo.
echo Press Ctrl+C to cancel, or wait 3 seconds to continue...
timeout /t 3 /nobreak >nul

python scripts\world_class_optimizer.py

echo.
echo ================================================================================
echo   OPTIMIZATION COMPLETE
echo ================================================================================
echo.
echo Results saved to: outputs\world_class_optimization_results.json
echo.

pause
