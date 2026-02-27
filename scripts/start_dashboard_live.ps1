# start_dashboard_live.ps1
# Quick launcher to start dashboard for live viewing

$ErrorActionPreference = "Continue"
$ROOT_DIR = Split-Path -Parent $PSScriptRoot
$VENV_DIR = Join-Path $ROOT_DIR "venv"
$BACKEND_DIR = Join-Path $ROOT_DIR "dashboard\backend"
$FRONTEND_DIR = Join-Path $ROOT_DIR "dashboard\frontend"

Write-Host "========================================"
Write-Host "STARTING DASHBOARD FOR LIVE VIEWING"
Write-Host "========================================"

# Check prerequisites
Write-Host "`n[1/3] Checking prerequisites..."
$pythonOk = Get-Command python -ErrorAction SilentlyContinue
$nodeOk = Get-Command node -ErrorAction SilentlyContinue

if (-not $pythonOk) {
    Write-Host "  [FAIL] Python not found"
    exit 1
}
if (-not $nodeOk) {
    Write-Host "  [FAIL] Node.js not found"
    exit 1
}
Write-Host "  [OK] Prerequisites met"

# Start backend
Write-Host "`n[2/3] Starting backend..."
Push-Location $BACKEND_DIR

# Activate venv and start backend
$backendScript = @"
import sys
import os
sys.path.insert(0, r'$BACKEND_DIR')
os.chdir(r'$BACKEND_DIR')
from app import app
import uvicorn
print('Backend starting on http://127.0.0.1:8000')
print('API docs: http://127.0.0.1:8000/docs')
uvicorn.run(app, host='127.0.0.1', port=8000, log_level='info')
"@

$backendScript | Out-File -FilePath "$env:TEMP\dashboard_backend_start.py" -Encoding UTF8

Start-Process -FilePath "$VENV_DIR\Scripts\python.exe" `
    -ArgumentList "$env:TEMP\dashboard_backend_start.py" `
    -WindowStyle Normal `
    -PassThru | Out-Null

Pop-Location
Write-Host "  [OK] Backend starting (check new window)"

# Start frontend
Write-Host "`n[3/3] Starting frontend..."
Push-Location $FRONTEND_DIR

# Ensure dependencies installed
if (-not (Test-Path "node_modules")) {
    Write-Host "  [INFO] Installing frontend dependencies (first time only)..."
    npm install --silent
}

Start-Process -FilePath "npm" `
    -ArgumentList "run", "dev", "--", "--host", "127.0.0.1", "--port", "3000" `
    -WindowStyle Normal `
    -PassThru | Out-Null

Pop-Location
Write-Host "  [OK] Frontend starting (check new window)"

# Wait a moment
Start-Sleep -Seconds 3

Write-Host "`n========================================"
Write-Host "DASHBOARD STARTED!"
Write-Host "========================================"
Write-Host ""
Write-Host "Open in browser:"
Write-Host "  Frontend UI: http://localhost:3000"
Write-Host "  Backend API: http://localhost:8000"
Write-Host "  API Docs:   http://localhost:8000/docs"
Write-Host ""
Write-Host "Press Ctrl+C in the backend/frontend windows to stop"
Write-Host "========================================"
