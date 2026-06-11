# Cleanup and Start - Simple Guide
# Closes unnecessary windows and starts the system cleanly

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CLEANUP AND START GUIDE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Close unnecessary PowerShell windows
Write-Host "[1/4] Closing unnecessary windows..." -ForegroundColor Yellow
Write-Host "  Please close all PowerShell windows manually:" -ForegroundColor White
Write-Host "    - Right-click on PowerShell icons in taskbar" -ForegroundColor Gray
Write-Host "    - Select 'Close window' for each" -ForegroundColor Gray
Write-Host "    - Keep only THIS window open" -ForegroundColor Gray
Write-Host ""
$response = Read-Host "  Press ENTER when done closing windows"

# Step 2: Check dependencies
Write-Host "`n[2/4] Checking dependencies..." -ForegroundColor Yellow
$venvDir = Join-Path $PSScriptRoot "venv"
$pythonExe = Join-Path $venvDir "Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "  [FAIL] Python venv not found" -ForegroundColor Red
    exit 1
}

# Check uvicorn
$uvicornCheck = & $pythonExe -c "import uvicorn; print('OK')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Installing missing dependencies..." -ForegroundColor Cyan
    & "$venvDir\Scripts\pip.exe" install --quiet uvicorn[standard] fastapi 2>&1 | Out-Null
    Write-Host "  [OK] Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  [OK] Dependencies ready" -ForegroundColor Green
}

# Step 3: Check ports
Write-Host "`n[3/4] Checking ports..." -ForegroundColor Yellow
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue

if ($port8000) {
    Write-Host "  [WARN] Port 8000 already in use (backend may be running)" -ForegroundColor Yellow
    Write-Host "    If you want to restart, close the process first" -ForegroundColor Gray
}
if ($port3000) {
    Write-Host "  [WARN] Port 3000 already in use (frontend may be running)" -ForegroundColor Yellow
    Write-Host "    If you want to restart, close the process first" -ForegroundColor Gray
}

# Step 4: Start system
Write-Host "`n[4/4] Ready to start system..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Choose an option:" -ForegroundColor Cyan
Write-Host "  1. Start FULL system (trading + dashboard)" -ForegroundColor White
Write-Host "  2. Start ONLY dashboard (backend + frontend)" -ForegroundColor White
Write-Host "  3. Just show me what to do manually" -ForegroundColor White
Write-Host ""
$choice = Read-Host "Enter choice (1, 2, or 3)"

switch ($choice) {
    "1" {
        Write-Host "`nStarting FULL system..." -ForegroundColor Green
        & "$PSScriptRoot\START_FULL_SYSTEM_WITH_DASHBOARD.ps1"
    }
    "2" {
        Write-Host "`nStarting dashboard only..." -ForegroundColor Green
        & "$PSScriptRoot\CHECK_AND_START_DASHBOARD.ps1"
    }
    "3" {
        Write-Host "`n========================================" -ForegroundColor Cyan
        Write-Host "MANUAL STARTUP GUIDE" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Open 3 separate PowerShell windows:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "WINDOW 1 - Dashboard Backend:" -ForegroundColor Cyan
        Write-Host "  cd C:\Genesis_System3\dashboard\backend" -ForegroundColor White
        Write-Host "  ..\..\venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000" -ForegroundColor White
        Write-Host ""
        Write-Host "WINDOW 2 - Dashboard Frontend:" -ForegroundColor Cyan
        Write-Host "  cd C:\Genesis_System3\dashboard\frontend" -ForegroundColor White
        Write-Host "  npm run dev" -ForegroundColor White
        Write-Host ""
        Write-Host "WINDOW 3 - Trading System (Optional):" -ForegroundColor Cyan
        Write-Host "  cd C:\Genesis_System3" -ForegroundColor White
        Write-Host "  .\venv\Scripts\python.exe option_chain_automation_master.py --sim --cycles 10" -ForegroundColor White
        Write-Host ""
        Write-Host "Then open: http://localhost:3000" -ForegroundColor Green
    }
    default {
        Write-Host "Invalid choice. Run script again." -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DONE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
