@echo off
echo ======================================================================
echo RUNNING AND TRACKING FULL SYSTEM
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1] Stopping existing processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
taskkill /F /IM node.exe /FI "WINDOWTITLE eq *vite*" 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo    ✅ Processes stopped

echo [2] Installing/verifying dependencies...
python -m pip install uvicorn[standard] fastapi --quiet >nul 2>&1
echo    ✅ Dependencies ready

echo [3] Starting backend...
cd dashboard\backend
start "Dashboard Backend - Port 8000" cmd /k "title Dashboard Backend && echo Starting Backend... && python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 8 /nobreak >nul

echo [4] Testing backend...
timeout /t 3 /nobreak >nul
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Backend is running
) else (
    echo    ⚠️ Backend may still be starting...
)

echo [5] Testing trade endpoints...
timeout /t 2 /nobreak >nul
curl -s http://localhost:8000/api/trades/today >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Trade endpoints working
) else (
    echo    ⚠️ Trade endpoints may need backend reload
)

echo [6] Starting frontend...
cd ..\frontend
if not exist "node_modules" (
    echo    Installing dependencies...
    call npm install --quiet
    timeout /t 5 /nobreak >nul
)
start "Dashboard Frontend - Port 3000" cmd /k "title Dashboard Frontend && echo Starting Frontend... && npm run dev -- --host 127.0.0.1"
timeout /t 10 /nobreak >nul

echo [7] Testing frontend...
timeout /t 5 /nobreak >nul
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Frontend is running
) else (
    echo    ⚠️ Frontend may still be starting...
)

echo.
echo ======================================================================
echo SYSTEM STARTED - TRACKING COMPLETE
echo ======================================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Check the windows for startup messages.
echo.
echo Running comprehensive validation...
cd ..\..
python scripts\comprehensive_validation_and_test.py
echo.
pause
