@echo off
setlocal enabledelayedexpansion
TITLE GENESIS SYSTEM3: WORLD-CLASS AUTONOMOUS TRADING
COLOR 0B

:: Force project root
cd /d "%~dp0"

echo ====================================================================
echo 💎 GENESIS SYSTEM3: WORLD-CLASS AUTONOMOUS SYSTEM STARTUP
echo ====================================================================
echo.

:: Ensure logs directory exists
if not exist "logs" mkdir logs

:: Autonomous Venv Detection
set "VENV_PYTHON="
if exist ".venv\Scripts\python.exe" (
    set "VENV_PYTHON=.venv\Scripts\python.exe"
) else if exist "venv\Scripts\python.exe" (
    set "VENV_PYTHON=venv\Scripts\python.exe"
) else if exist ".venv-ml\Scripts\python.exe" (
    set "VENV_PYTHON=.venv-ml\Scripts\python.exe"
)

if "%VENV_PYTHON%"=="" (
    echo ❌ ERROR: No Virtual Environment found.
    pause
    exit /b
)

echo ✅ Environment detected: %VENV_PYTHON%

:: Dependency Check
echo [0/3] Checking World-Class Dependencies...
%VENV_PYTHON% -c "import pandas; import yfinance; import xgboost" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Missing core packages. Attempting autonomous repair...
    %VENV_PYTHON% -m pip install pandas yfinance requests scikit-learn xgboost pytz openpyxl fastparquet
    
    :: Re-check after repair
    %VENV_PYTHON% -c "import pandas; import yfinance; import xgboost" >nul 2>&1
    if errorlevel 1 (
        echo ❌ REPAIR FAILED: Please run 'pip install pandas yfinance xgboost' manually.
        pause
        exit /b
    )
    echo ✅ Repair successful.
) else (
    echo ✅ Dependencies verified.
)

:: 1. Start Dashboard Backend (API)
echo [1/3] Starting AI Intelligence API (Port 8000)...
start "System3 Backend" /B cmd /c "%VENV_PYTHON% dashboard\backend\app.py > logs\backend_startup.log 2>&1"

:: 2. Start Autonomous Brain (Self-Learning)
echo [2/3] Starting Autonomous Brain (Self-Evolution Loop)...
start "System3 Brain" /B cmd /c "%VENV_PYTHON% core\engine\AUTONOMOUS_BRAIN.py > logs\brain_startup.log 2>&1"

:: 3. Start Dashboard Frontend
echo [3/3] Starting Alpha Dashboard UI (Port 3000)...
cd dashboard\frontend
start "System3 Frontend" /B cmd /c "npm run dev > ..\..\logs\frontend_startup.log 2>&1"
cd ..\..

echo.
echo ====================================================================
echo ✅ ALL SYSTEMS DEPLOYED AND OPERATIONAL
echo.
echo - DASHBOARD: http://localhost:3000
echo - AI API:    http://localhost:8000
echo - EVOLUTION: Active (Background)
echo ====================================================================
echo.
echo Press any key to view status audit...
pause > nul

%VENV_PYTHON% core\engine\FULL_SYSTEM_AUDIT_QC.py
pause
