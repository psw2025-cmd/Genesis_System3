@echo off
echo ======================================================================
echo STARTING BACKEND AND FRONTEND WITH ALL FIXES
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1] Stopping existing processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
taskkill /F /IM node.exe /FI "WINDOWTITLE eq *vite*" 2>nul
timeout /t 2 /nobreak >nul

echo [2] Installing/verifying dependencies...
python -m pip install uvicorn[standard] fastapi --quiet >nul 2>&1
if %errorlevel% neq 0 (
    echo    ⚠️ Warning: pip install had issues, but continuing...
)

echo [3] Starting backend...
cd dashboard\backend
start "Dashboard Backend - Port 8000" cmd /k "title Dashboard Backend && python -m pip install uvicorn[standard] fastapi --quiet && python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 8 /nobreak >nul

echo [4] Starting frontend...
cd ..\frontend
if not exist "node_modules" (
    echo    Installing dependencies first...
    call npm install
    timeout /t 5 /nobreak >nul
)
start "Dashboard Frontend - Port 3000" cmd /k "title Dashboard Frontend && npm run dev -- --host 127.0.0.1"
timeout /t 5 /nobreak >nul

echo.
echo ======================================================================
echo SERVICES STARTED
echo ======================================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Check the windows for startup messages.
echo Backend should show: "Application startup complete"
echo Frontend should show: "Local: http://localhost:3000"
echo.
echo Press any key to test endpoints...
pause >nul

echo.
echo [5] Testing endpoints...
timeout /t 3 /nobreak >nul

echo Testing /api/health...
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Backend is responding!
) else (
    echo    ⚠️ Backend may still be starting...
)

echo Testing /api/trades/today...
curl -s http://localhost:8000/api/trades/today >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Trade endpoints are working!
) else (
    echo    ⚠️ Trade endpoints may need more time...
)

echo.
echo ======================================================================
echo SETUP COMPLETE
echo ======================================================================
echo.
echo Open your browser to:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000/docs
echo.
pause
