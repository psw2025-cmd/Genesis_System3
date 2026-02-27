@echo off
echo ======================================================================
echo FIXING UVICORN INSTALLATION AND STARTING SERVICES
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1] Installing uvicorn and fastapi...
python -m pip install uvicorn[standard] fastapi --quiet
if %errorlevel% neq 0 (
    echo    ⚠️ Warning: Installation had issues
    pause
)

echo [2] Verifying installation...
python -c "import uvicorn; print('✅ uvicorn installed')" 2>nul
if %errorlevel% neq 0 (
    echo    ❌ uvicorn still not found!
    echo    Trying alternative installation...
    python -m pip install --upgrade pip
    python -m pip install uvicorn[standard] fastapi
    pause
)

echo [3] Stopping existing processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
taskkill /F /IM node.exe /FI "WINDOWTITLE eq *vite*" 2>nul
timeout /t 2 /nobreak >nul

echo [4] Checking port 8000...
netstat -ano | findstr ":8000.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo    Port 8000 is in use, killing processes...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

echo [5] Starting backend...
cd dashboard\backend
start "Dashboard Backend - Port 8000" cmd /k "title Dashboard Backend && python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 8 /nobreak >nul

echo [6] Starting frontend...
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
echo.
pause
