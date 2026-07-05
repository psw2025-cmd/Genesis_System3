@echo off
REM ====================================================================
REM Genesis System3 — LOCAL STACK (no GitHub / no Codespaces / no Render)
REM Backend + worker + dashboard at http://localhost:8000/ui
REM ====================================================================
setlocal enabledelayedexpansion

set ROOT=%~dp0..
cd /d "%ROOT%"

set SYSTEM3_LOCAL=1
set SYSTEM3_API_BASE=http://127.0.0.1:8000
set SYSTEM3_MODE=analyzer
set ANALYZE_MODE=1
set LIVE_TRADING_ENABLED=0
set SYSTEM3_LIVE_TRADING_ALLOWED=0
set SYSTEM3_REAL_ONLY=1

echo.
echo ====================================================================
echo   GENESIS SYSTEM3 — LOCAL LAPTOP STACK
echo ====================================================================
echo.

REM --- venv ---
if not exist "venv\Scripts\python.exe" (
    echo [1/6] Creating venv...
    python -m venv venv
)
set PY=venv\Scripts\python.exe
set PIP=venv\Scripts\pip.exe

echo [2/6] Installing backend dependencies...
"%PIP%" install -q --upgrade pip 2>nul
if exist "dashboard\backend\requirements.txt" (
    "%PIP%" install -q -r dashboard\backend\requirements.txt 2>nul
) else (
    "%PIP%" install -q uvicorn[standard] fastapi python-dotenv 2>nul
)

echo [3/6] Syncing Dhan instrument master (if missing)...
if not exist "storage\instruments\master_meta.json" (
    "%PY%" scripts\sync_dhan_instruments_master.py --force 2>nul
) else (
    echo   instruments cache present — skip
)

echo [4/6] Freeing port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo [5/6] Starting backend + cloud worker...
start "System3 Backend" /MIN cmd /c "cd /d %ROOT% && set SYSTEM3_LOCAL=1&& set LIVE_TRADING_ENABLED=0&& set SYSTEM3_REAL_ONLY=1&& venv\Scripts\python.exe -m uvicorn dashboard.backend.app:app --host 127.0.0.1 --port 8000"
start "System3 Worker" /MIN cmd /c "cd /d %ROOT% && set SYSTEM3_LOCAL=1&& set LIVE_TRADING_ENABLED=0&& set CLOUD_WORKER=1&& venv\Scripts\python.exe scripts\cloud_worker.py"

echo [6/6] Waiting for health...
set READY=0
for /L %%i in (1,1,30) do (
    powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health' -UseBasicParsing -TimeoutSec 3; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
    if not errorlevel 1 (
        set READY=1
        goto :healthy
    )
    timeout /t 2 /nobreak >nul
)
:healthy

echo.
if "!READY!"=="1" (
    echo   [OK] Backend healthy at http://127.0.0.1:8000
) else (
    echo   [WARN] Backend slow to start — check minimized "System3 Backend" window
)

echo.
echo   Dashboard UI:  http://127.0.0.1:8000/ui
echo   API docs:      http://127.0.0.1:8000/docs
echo   API health:    http://127.0.0.1:8000/api/health
echo.

if /I "%~1"=="--no-open" goto :done
if /I "%~2"=="--no-open" goto :done
if /I "%~3"=="--no-open" goto :done
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "http://127.0.0.1:8000/ui"
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    start "" "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" "http://127.0.0.1:8000/ui"
) else (
    start "" "http://127.0.0.1:8000/ui"
)

:done
if /I "%~1"=="--no-pause" exit /b 0
if /I "%~2"=="--no-pause" exit /b 0
if /I "%~3"=="--no-pause" exit /b 0
echo   Backend + worker run in minimized windows. Close those to stop.
pause >nul
endlocal
