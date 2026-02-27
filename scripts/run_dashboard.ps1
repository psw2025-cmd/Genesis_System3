# run_dashboard.ps1
# Single-command launcher for System3 Ultra Dashboard

$ErrorActionPreference = "Stop"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$ROOT_DIR = Split-Path -Parent $SCRIPT_DIR
$VENV_DIR = Join-Path $ROOT_DIR "venv"
$BACKEND_DIR = Join-Path $ROOT_DIR "dashboard\backend"
$FRONTEND_DIR = Join-Path $ROOT_DIR "dashboard\frontend"

Write-Host "========================================"
Write-Host "SYSTEM3 ULTRA DASHBOARD LAUNCHER"
Write-Host "========================================"

# Check prerequisites
Write-Host "`n[1/4] Checking prerequisites..."
& "$SCRIPT_DIR\check_dashboard_prereqs.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[FAIL] Prerequisites check failed - fix issues above"
    exit 1
}

# Setup backend venv
Write-Host "`n[2/4] Setting up backend..."
if (-not (Test-Path $VENV_DIR)) {
    Write-Host "  Creating virtual environment..."
    python -m venv $VENV_DIR
}

Write-Host "  Activating virtual environment..."
& "$VENV_DIR\Scripts\Activate.ps1"

Write-Host "  Installing backend dependencies..."
Set-Location $BACKEND_DIR
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt

# Setup frontend
Write-Host "`n[3/4] Setting up frontend..."
Set-Location $FRONTEND_DIR
if (-not (Test-Path "node_modules")) {
    Write-Host "  Installing frontend dependencies (this may take a minute)..."
    npm install --silent
}

# Start services
Write-Host "`n[4/4] Starting services..."
Write-Host "`n========================================"
Write-Host "DASHBOARD STARTING..."
Write-Host "========================================"
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:3000"
Write-Host "`nPress Ctrl+C to stop both services"
Write-Host "========================================`n"

# Start backend in background
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:BACKEND_DIR
    & "$using:VENV_DIR\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8000
}

# Start frontend
Set-Location $FRONTEND_DIR
npm run dev

# Cleanup on exit
Write-Host "`nStopping services..."
Stop-Job $backendJob
Remove-Job $backendJob
