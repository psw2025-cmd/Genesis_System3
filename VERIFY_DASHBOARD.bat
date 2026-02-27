@echo off
REM Comprehensive Dashboard Verification
echo ========================================
echo Dashboard Verification Script
echo ========================================
echo.

REM Check if backend is running
echo Checking backend...
curl -s http://localhost:8000/api/health >nul 2>&1
if errorlevel 1 (
    echo ERROR: Backend is not running!
    echo Please start backend first:
    echo   RESTART_WITH_SSOT.bat
    pause
    exit /b 1
)

echo Backend is running.
echo.

REM Run verification
echo Running comprehensive verification...
echo.
python scripts\verify_dashboard_complete.py

if errorlevel 1 (
    echo.
    echo Verification failed. Check the output above.
    pause
    exit /b 1
) else (
    echo.
    echo ✅ All verification tests passed!
    echo.
    echo Dashboard is fully operational.
    pause
    exit /b 0
)
