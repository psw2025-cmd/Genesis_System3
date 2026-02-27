@echo off
REM Comprehensive Performance Analysis & 10K Strategy Optimization

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo ================================================================================
echo   COMPREHENSIVE PERFORMANCE ANALYSIS
echo ================================================================================
echo.

python scripts\comprehensive_performance_analysis.py

echo.
echo ================================================================================
echo   ANALYSIS COMPLETE
echo ================================================================================
echo.
echo Report saved to: outputs\performance_analysis_report.txt
echo.

pause
