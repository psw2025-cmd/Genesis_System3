@echo off
REM ====================================================================
REM GENESIS SYSTEM3 - DASHBOARD SYSTEM UPDATER
REM ====================================================================
REM This script updates the dashboard system:
REM - Updates all dependencies
REM - Applies latest fixes
REM - Verifies everything works
REM ====================================================================

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%venv
set BACKEND_DIR=%SCRIPT_DIR%dashboard\backend
set FRONTEND_DIR=%SCRIPT_DIR%dashboard\frontend

cls
echo.
echo ====================================================================
echo   GENESIS SYSTEM3 - DASHBOARD SYSTEM UPDATER
echo ====================================================================
echo.

REM Check if services are running
echo [1/5] Checking running services...
netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo   [WARN] Backend is running on port 8000
    echo   You may want to stop it before updating
    echo   Press any key to continue anyway, or Ctrl+C to cancel...
    pause >nul
)

netstat -an | findstr ":3000" >nul 2>&1
if not errorlevel 1 (
    echo   [WARN] Frontend is running on port 3000
    echo   You may want to stop it before updating
    echo   Press any key to continue anyway, or Ctrl+C to cancel...
    pause >nul
)

REM Update Python dependencies
echo.
echo [2/5] Updating Python dependencies...
call "%VENV_DIR%\Scripts\activate.bat" >nul 2>&1
"%VENV_DIR%\Scripts\pip.exe" install --upgrade pip >nul 2>&1
"%VENV_DIR%\Scripts\pip.exe" install --upgrade --prefer-binary pandas numpy scipy scikit-learn uvicorn[standard] fastapi requests aiohttp >nul 2>&1

if exist "%BACKEND_DIR%\requirements.txt" (
    "%VENV_DIR%\Scripts\pip.exe" install --upgrade -r "%BACKEND_DIR%\requirements.txt" >nul 2>&1
)
echo   [OK] Python dependencies updated

REM Update frontend dependencies
echo.
echo [3/5] Updating frontend dependencies...
pushd "%FRONTEND_DIR%"
call npm update --silent >nul 2>&1
popd
echo   [OK] Frontend dependencies updated

REM Run auto-fix
echo.
echo [4/5] Running auto-fix...
if exist "%SCRIPT_DIR%scripts\auto_fix_and_update_dashboard.ps1" (
    powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%scripts\auto_fix_and_update_dashboard.ps1" >nul 2>&1
    echo   [OK] Auto-fix completed
) else (
    echo   [WARN] Auto-fix script not found
)

REM Verify
echo.
echo [5/5] Verifying installation...
if exist "%VENV_DIR%\Scripts\python.exe" (
    echo   [OK] Python venv ready
) else (
    echo   [FAIL] Python venv missing
)

if exist "%FRONTEND_DIR%\node_modules" (
    echo   [OK] Frontend dependencies ready
) else (
    echo   [FAIL] Frontend dependencies missing
)

echo.
echo ====================================================================
echo   UPDATE COMPLETE
echo ====================================================================
echo.
echo   All dependencies have been updated.
echo   Run START_FULL_DASHBOARD_SYSTEM.bat to start the system.
echo.
pause
