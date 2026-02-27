@echo off
echo ======================================================================
echo STARTING DASHBOARD (Backend + Frontend)
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1] Starting Backend...
cd dashboard\backend
start "Dashboard Backend" cmd /k "title Dashboard Backend && python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 5 /nobreak >nul

echo [2] Starting Frontend...
cd ..\frontend
if not exist "node_modules" (
    echo    Installing dependencies...
    call npm install
)
start "Dashboard Frontend" cmd /k "title Dashboard Frontend && npm run dev -- --host 127.0.0.1"
timeout /t 10 /nobreak >nul

echo.
echo ======================================================================
echo DASHBOARD STARTING
echo ======================================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul
start http://localhost:3000

echo.
echo Check the command windows for startup messages.
echo Frontend should show: "Local: http://localhost:3000"
echo.
pause
