@echo off
echo ======================================================================
echo STARTING DASHBOARD FRONTEND
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1] Checking if frontend is already running...
netstat -ano | findstr ":3000" >nul 2>&1
if %errorlevel% equ 0 (
    echo    Frontend is already running on port 3000
    echo    Opening browser...
    start http://localhost:3000
    pause
    exit /b 0
)

echo [2] Navigating to frontend directory...
cd dashboard\frontend

echo [3] Checking dependencies...
if not exist "node_modules" (
    echo    Installing dependencies (this may take a few minutes)...
    call npm install
    if %errorlevel% neq 0 (
        echo    ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [4] Starting frontend server...
start "Dashboard Frontend - Port 3000" cmd /k "title Dashboard Frontend && npm run dev -- --host 127.0.0.1"

echo.
echo ======================================================================
echo FRONTEND STARTING
echo ======================================================================
echo.
echo Waiting for frontend to start (10 seconds)...
timeout /t 10 /nobreak >nul

echo.
echo Opening browser...
start http://localhost:3000

echo.
echo ======================================================================
echo FRONTEND STARTED
echo ======================================================================
echo.
echo Frontend URL: http://localhost:3000
echo.
echo Check the "Dashboard Frontend" window for startup messages.
echo You should see: "Local: http://localhost:3000"
echo.
echo If you see errors, check:
echo   1. Node.js is installed (run: node --version)
echo   2. npm is installed (run: npm --version)
echo   3. Dependencies are installed (node_modules folder exists)
echo.
pause
