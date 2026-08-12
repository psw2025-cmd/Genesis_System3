# start_dashboard_live.ps1
# Local read-only dashboard launcher. Production authority remains Google Cloud.

$ErrorActionPreference = "Stop"
$ROOT_DIR = Split-Path -Parent $PSScriptRoot
$VENV_DIR = Join-Path $ROOT_DIR "venv"
$FRONTEND_DIR = Join-Path $ROOT_DIR "dashboard\frontend"

Write-Host "========================================"
Write-Host "STARTING SYSTEM3 PUBLIC READ-ONLY DASHBOARD"
Write-Host "========================================"

$pythonExe = Join-Path $VENV_DIR "Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = (Get-Command python -ErrorAction Stop).Source
}
$nodeOk = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeOk) {
    Write-Host "[FAIL] Node.js not found"
    exit 1
}

$env:ANALYZE_MODE = "1"
$env:SYSTEM3_MODE = "ANALYZER"
$env:LIVE_TRADING_ENABLED = "0"
$env:SYSTEM3_LIVE_TRADING_ALLOWED = "0"
$env:AUTO_EXECUTE_TRADES = "0"

Write-Host "`n[1/2] Starting secure backend wrapper..."
Start-Process -FilePath $pythonExe `
    -ArgumentList "-m", "uvicorn", "dashboard.backend.secure_app:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info" `
    -WorkingDirectory $ROOT_DIR `
    -WindowStyle Normal `
    -PassThru | Out-Null
Write-Host "  [OK] Backend starting through dashboard.backend.secure_app"

Write-Host "`n[2/2] Starting frontend..."
Push-Location $FRONTEND_DIR
if (-not (Test-Path "node_modules")) {
    npm install --silent
}
Start-Process -FilePath "npm" `
    -ArgumentList "run", "dev", "--", "--host", "127.0.0.1", "--port", "3000" `
    -WindowStyle Normal `
    -PassThru | Out-Null
Pop-Location

Start-Sleep -Seconds 3
Write-Host ""
Write-Host "Frontend UI: http://localhost:3000"
Write-Host "Backend API: http://localhost:8000"
Write-Host "Dashboard visibility: PUBLIC / READ-ONLY"
Write-Host "LIVE: OFF / LOCKED"
