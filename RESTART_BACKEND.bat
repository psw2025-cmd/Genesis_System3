@echo off
echo ======================================================================
echo RESTARTING BACKEND
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1] Stopping existing backend processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *backend*" 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
    echo    Killing process on port 8000: %%a
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo [2] Starting backend...
cd dashboard\backend
start "Dashboard Backend - Port 8000" cmd /k "title Dashboard Backend && python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 5 /nobreak >nul

echo [3] Verifying backend...
cd ..\..
timeout /t 3 /nobreak >nul
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Backend is running and responding
) else (
    echo    ⚠️ Backend may still be starting... check the window
)

echo.
echo ======================================================================
echo BACKEND RESTART COMPLETE
echo ======================================================================
echo.
echo Backend URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Check the backend window for startup messages.
echo.
pause
