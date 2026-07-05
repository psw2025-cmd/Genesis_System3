@echo off
REM One-shot: sync Render secrets -> verify -> NSE health -> restart backend
setlocal
cd /d "%~dp0.."

if exist ".secrets\render_api_key" (
    echo [1/5] Syncing DHAN_* from Render...
    venv\Scripts\python.exe tools\sync_render_secrets.py
) else (
    echo [1/5] Skip Render sync - no .secrets\render_api_key
    echo       Create: echo YOUR_RND_KEY ^> .secrets\render_api_key
)

echo [2/5] Verify local env...
venv\Scripts\python.exe tools\verify_local_env.py

echo [3/5] NSE option-chain health (v3 API)...
venv\Scripts\python.exe tools\fetch_nse_option_chain.py --symbol NIFTY --out state\nse_health_latest.json
if errorlevel 1 (
    echo WARNING: NSE fetch failed - dashboard will use Dhan/bhavcopy fallbacks
)

echo [4/5] Restart backend on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING" 2^>nul') do taskkill /F /PID %%a >nul 2>&1
timeout /t 2 /nobreak >nul
start "System3 Backend" /MIN cmd /c "cd /d ""%CD%"" && venv\Scripts\python.exe -m uvicorn dashboard.backend.app:app --host 127.0.0.1 --port 8000"

echo [5/5] Waiting for health...
timeout /t 12 /nobreak >nul
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/broker/status' -UseBasicParsing -TimeoutSec 15).Content | ConvertFrom-Json | Select-Object connected,error | Format-List } catch { Write-Host 'broker status: timeout' }"

echo.
echo Dashboard: http://127.0.0.1:8000/ui
endlocal
