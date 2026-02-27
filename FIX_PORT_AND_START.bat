@echo off
echo ======================================================================
echo FIXING PORT 8000 ISSUE AND STARTING SERVICES
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1] Checking and clearing port 8000...
netstat -ano | findstr ":8000.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo    Port 8000 is in use, killing processes...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
        echo    Killing PID %%a...
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 3 /nobreak >nul
    echo    ✅ Port cleared
) else (
    echo    ✅ Port 8000 is available
)

echo [2] Installing/verifying uvicorn...
python -m pip install uvicorn[standard] fastapi --quiet >nul 2>&1

echo [3] Starting backend...
cd dashboard\backend
start "Dashboard Backend - Port 8000" cmd /k "title Dashboard Backend && python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 8 /nobreak >nul

echo [4] Starting frontend...
cd ..\frontend
if not exist "node_modules" (
    echo    Installing dependencies...
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
echo.
pause
