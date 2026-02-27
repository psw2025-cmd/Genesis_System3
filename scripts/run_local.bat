@echo off
REM ====================================================================
REM GENESIS SYSTEM3 - ONE-CLICK RUN SCRIPT (Windows)
REM ====================================================================
REM This script starts the complete system with all checks and fixes
REM ====================================================================

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0..
cd /d "%SCRIPT_DIR%"

echo.
echo ====================================================================
echo   GENESIS SYSTEM3 - ONE-CLICK STARTUP
echo ====================================================================
echo.

REM Step 1: Run doctor check
echo [1/4] Running system health check...
python scripts\doctor.py
if errorlevel 1 (
    echo.
    echo [WARNING] Some checks failed. Continuing anyway...
    echo.
)

REM Step 2: Install/verify dependencies
echo.
echo [2/4] Verifying dependencies...
if not exist "venv\Scripts\activate.bat" (
    echo   Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -q -r requirements.txt 2>nul
pip install -q uvicorn[standard] fastapi 2>nul

REM Step 3: Check and clear ports
echo.
echo [3/4] Checking ports...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
    echo   Killing process on port 8000 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000.*LISTENING"') do (
    echo   Killing process on port 3000 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

REM Step 4: Start services
echo.
echo [4/4] Starting services...
echo.

REM Start backend
echo   Starting backend (port 8000)...
start "Dashboard Backend" /MIN cmd /c "cd /d %SCRIPT_DIR%\dashboard\backend && call %SCRIPT_DIR%\venv\Scripts\activate.bat && python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 8 /nobreak >nul

REM Start frontend
echo   Starting frontend (port 3000)...
cd dashboard\frontend
if not exist "node_modules" (
    echo     Installing frontend dependencies...
    call npm install --quiet
)
start "Dashboard Frontend" /MIN cmd /c "cd /d %SCRIPT_DIR%\dashboard\frontend && npm run dev -- --host 127.0.0.1"
cd ..\..
timeout /t 12 /nobreak >nul

REM Verify and open
echo.
echo   Verifying services...
timeout /t 3 /nobreak >nul
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -UseBasicParsing -TimeoutSec 3; Write-Host '  [OK] Backend: RUNNING' -ForegroundColor Green } catch { Write-Host '  [WARN] Backend: Starting...' -ForegroundColor Yellow }" 2>nul
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:3000' -UseBasicParsing -TimeoutSec 3; Write-Host '  [OK] Frontend: RUNNING' -ForegroundColor Green } catch { Write-Host '  [WARN] Frontend: Starting...' -ForegroundColor Yellow }" 2>nul

echo.
echo ====================================================================
echo   SYSTEM STARTED
echo ====================================================================
echo.
echo   Dashboard: http://localhost:3000
echo   Backend API: http://localhost:8000
echo.
echo   Opening dashboard in Chrome...
timeout /t 2 /nobreak >nul

REM Open Chrome
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "http://localhost:3000"
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    start "" "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" "http://localhost:3000"
) else (
    echo   Please manually open: http://localhost:3000
)

echo.
echo   Services are running in minimized windows.
echo   Press any key to exit (services will continue)...
pause >nul

endlocal
