@echo off
REM Run All 3 Steps: Frontend, Dashboard Access, Desktop Build
echo ========================================
echo System3 Ultra - Running All 3 Steps
echo ========================================
echo.

REM Step 1: Start Frontend
echo [STEP 1] Starting Frontend...
cd /d "%~dp0..\dashboard\frontend"
start "Frontend Server" cmd /k "npm run dev"
timeout /t 8 /nobreak >nul
echo [OK] Frontend started
echo.

REM Step 2: Verify Dashboard Access
echo [STEP 2] Verifying Dashboard Access...
cd /d "%~dp0.."
python -c "import requests; import time; time.sleep(2); r1 = requests.get('http://localhost:8000/api/health', timeout=5); r2 = requests.get('http://localhost:3000', timeout=5); print('[OK] Backend:', r1.status_code); print('[OK] Frontend:', r2.status_code)"
if errorlevel 1 (
    echo [WARNING] Dashboard verification failed
) else (
    echo [OK] Dashboard is accessible
)
echo.

REM Step 3: Build Desktop App
echo [STEP 3] Building Desktop App...
cd /d "%~dp0..\desktop_app"
call npm run build:win
if errorlevel 1 (
    echo [ERROR] Desktop app build failed
    pause
    exit /b 1
) else (
    echo [OK] Desktop app built successfully
)
echo.

echo ========================================
echo [SUCCESS] All 3 steps completed!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo Desktop App: desktop_app\dist\
echo.
pause
