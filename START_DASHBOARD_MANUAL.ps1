# Manual Dashboard Start - Step by Step
# This script will guide you to start backend and frontend manually

$ErrorActionPreference = "Continue"
$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$VENV_DIR = Join-Path $ROOT_DIR "venv"
$BACKEND_DIR = Join-Path $ROOT_DIR "dashboard\backend"
$FRONTEND_DIR = Join-Path $ROOT_DIR "dashboard\frontend"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MANUAL DASHBOARD START GUIDE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if ports are free
Write-Host "[1/4] Checking ports..." -ForegroundColor Yellow
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue

if ($port8000) {
    Write-Host "  [WARN] Port 8000 is in use" -ForegroundColor Yellow
    Write-Host "    Backend may already be running, or another process is using it" -ForegroundColor Gray
    Write-Host "    Process ID: $($port8000.OwningProcess)" -ForegroundColor Gray
} else {
    Write-Host "  [OK] Port 8000 is free" -ForegroundColor Green
}

if ($port3000) {
    Write-Host "  [WARN] Port 3000 is in use" -ForegroundColor Yellow
    Write-Host "    Frontend may already be running, or another process is using it" -ForegroundColor Gray
    Write-Host "    Process ID: $($port3000.OwningProcess)" -ForegroundColor Gray
} else {
    Write-Host "  [OK] Port 3000 is free" -ForegroundColor Green
}

# Step 2: Check dependencies
Write-Host "`n[2/4] Checking dependencies..." -ForegroundColor Yellow
$pythonOk = Test-Path "$VENV_DIR\Scripts\python.exe"
$npmOk = Get-Command npm -ErrorAction SilentlyContinue

if ($pythonOk) {
    Write-Host "  [OK] Python venv ready" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Python venv not found" -ForegroundColor Red
    exit 1
}

if ($npmOk) {
    Write-Host "  [OK] npm found: $($npmOk.Source)" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] npm not found. Please install Node.js" -ForegroundColor Red
    Write-Host "    Download from: https://nodejs.org/" -ForegroundColor Gray
    exit 1
}

# Step 3: Provide manual start commands
Write-Host "`n[3/4] Manual Start Instructions" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You need to open 2 NEW PowerShell windows:" -ForegroundColor White
Write-Host ""
Write-Host "WINDOW 1 - Backend API:" -ForegroundColor Cyan
Write-Host "  Copy and paste these commands:" -ForegroundColor Gray
Write-Host ""
Write-Host "  cd '$BACKEND_DIR'" -ForegroundColor White
Write-Host "  ..\..\venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "  You should see:" -ForegroundColor Gray
Write-Host "    INFO:     Uvicorn running on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host ""
Write-Host "WINDOW 2 - Frontend Dashboard:" -ForegroundColor Cyan
Write-Host "  Copy and paste these commands:" -ForegroundColor Gray
Write-Host ""
Write-Host "  cd '$FRONTEND_DIR'" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "  You should see:" -ForegroundColor Gray
Write-Host "    VITE v5.x.x  ready in xxx ms" -ForegroundColor Green
Write-Host "    ➜  Local:   http://localhost:3000/" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 4: Offer to open windows
Write-Host "[4/4] Would you like me to open the windows for you?" -ForegroundColor Yellow
Write-Host ""
Write-Host "I can:" -ForegroundColor White
Write-Host "  1. Open a new PowerShell window for Backend (you run the commands)" -ForegroundColor Gray
Write-Host "  2. Open a new PowerShell window for Frontend (you run the commands)" -ForegroundColor Gray
Write-Host "  3. Just show me the commands (do nothing)" -ForegroundColor Gray
Write-Host ""
$choice = Read-Host "Enter choice (1, 2, or 3)"

switch ($choice) {
    "1" {
        Write-Host "`nOpening Backend window..." -ForegroundColor Green
        $backendScript = @"
cd '$BACKEND_DIR'
Write-Host 'Backend API - Run this command:' -ForegroundColor Cyan
Write-Host '..\..\venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000' -ForegroundColor White
"@
        $backendScript | Out-File -FilePath "$env:TEMP\backend_commands.ps1" -Encoding UTF8
        Start-Process powershell.exe -ArgumentList "-NoExit", "-File", "$env:TEMP\backend_commands.ps1"
        Write-Host "  [OK] Backend window opened" -ForegroundColor Green
    }
    "2" {
        Write-Host "`nOpening Frontend window..." -ForegroundColor Green
        $frontendScript = @"
cd '$FRONTEND_DIR'
Write-Host 'Frontend Dashboard - Run this command:' -ForegroundColor Cyan
Write-Host 'npm run dev' -ForegroundColor White
"@
        $frontendScript | Out-File -FilePath "$env:TEMP\frontend_commands.ps1" -Encoding UTF8
        Start-Process powershell.exe -ArgumentList "-NoExit", "-File", "$env:TEMP\frontend_commands.ps1"
        Write-Host "  [OK] Frontend window opened" -ForegroundColor Green
    }
    "3" {
        Write-Host "`nCommands are shown above. Copy and paste them into new PowerShell windows." -ForegroundColor Cyan
    }
    default {
        Write-Host "`nInvalid choice. Commands are shown above." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "After starting both:" -ForegroundColor Yellow
Write-Host "  1. Wait 10-15 seconds for services to start" -ForegroundColor White
Write-Host "  2. Open Chrome and go to: http://localhost:3000" -ForegroundColor White
Write-Host "  3. You should see the dashboard!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
