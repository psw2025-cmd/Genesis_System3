# Start Full System with Dashboard - Production Ready
# Starts trading system + dashboard backend + frontend + monitoring

$ErrorActionPreference = "Continue"
$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$VENV_DIR = Join-Path $ROOT_DIR "venv"
$BACKEND_DIR = Join-Path $ROOT_DIR "dashboard\backend"
$FRONTEND_DIR = Join-Path $ROOT_DIR "dashboard\frontend"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GENESIS SYSTEM3 - FULL SYSTEM STARTUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Track processes
$processes = @{}

# Cleanup function
function Stop-AllProcesses {
    Write-Host "`n[CLEANUP] Stopping all processes..." -ForegroundColor Yellow
    foreach ($key in $processes.Keys) {
        if ($processes[$key] -and -not $processes[$key].HasExited) {
            Stop-Process -Id $processes[$key].Id -Force -ErrorAction SilentlyContinue
            Write-Host "  Stopped: $key" -ForegroundColor Green
        }
    }
}

Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Stop-AllProcesses } | Out-Null

# Step 1: Check prerequisites
Write-Host "[1/5] Checking prerequisites..." -ForegroundColor Yellow
$pythonOk = Get-Command python -ErrorAction SilentlyContinue
$nodeOk = Get-Command node -ErrorAction SilentlyContinue

if (-not $pythonOk) {
    Write-Host "  [FAIL] Python not found" -ForegroundColor Red
    exit 1
}
if (-not $nodeOk) {
    Write-Host "  [FAIL] Node.js not found" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] Prerequisites met" -ForegroundColor Green

# Step 2: Start trading system (if not running)
Write-Host "`n[2/5] Starting trading system..." -ForegroundColor Yellow
$tradingRunning = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
if (-not $tradingRunning) {
    Write-Host "  Starting option chain automation..." -ForegroundColor Cyan
    $tradingScript = @"
import sys
import os
sys.path.insert(0, r'$ROOT_DIR')
os.chdir(r'$ROOT_DIR')
from option_chain_automation_master import OptionChainAutomationMaster
import asyncio

master = OptionChainAutomationMaster()
asyncio.run(master.run())
"@
    $tradingScript | Out-File -FilePath "$env:TEMP\trading_start.py" -Encoding UTF8
    
    $processes['trading'] = Start-Process -FilePath "$VENV_DIR\Scripts\python.exe" `
        -ArgumentList "$env:TEMP\trading_start.py" `
        -WindowStyle Normal `
        -PassThru
    
    Write-Host "  [OK] Trading system started (PID: $($processes['trading'].Id))" -ForegroundColor Green
    Start-Sleep -Seconds 5
} else {
    Write-Host "  [INFO] Trading system already running" -ForegroundColor Cyan
}

# Step 3: Start dashboard backend
Write-Host "`n[3/5] Starting dashboard backend..." -ForegroundColor Yellow
$backendRunning = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if (-not $backendRunning) {
    Write-Host "  Starting backend API..." -ForegroundColor Cyan
    $backendScript = @"
import sys
import os
sys.path.insert(0, r'$BACKEND_DIR')
os.chdir(r'$BACKEND_DIR')
from app import app
import uvicorn
print('Backend starting on http://127.0.0.1:8000')
uvicorn.run(app, host='127.0.0.1', port=8000, log_level='info')
"@
    $backendScript | Out-File -FilePath "$env:TEMP\backend_start.py" -Encoding UTF8
    
    $processes['backend'] = Start-Process -FilePath "$VENV_DIR\Scripts\python.exe" `
        -ArgumentList "$env:TEMP\backend_start.py" `
        -WindowStyle Normal `
        -PassThru
    
    Write-Host "  [OK] Backend started (PID: $($processes['backend'].Id))" -ForegroundColor Green
    Start-Sleep -Seconds 8
} else {
    Write-Host "  [INFO] Backend already running" -ForegroundColor Cyan
}

# Step 4: Start dashboard frontend
Write-Host "`n[4/5] Starting dashboard frontend..." -ForegroundColor Yellow
$frontendRunning = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if (-not $frontendRunning) {
    Write-Host "  Starting frontend dev server..." -ForegroundColor Cyan
    Push-Location $FRONTEND_DIR
    
    if (-not (Test-Path "node_modules")) {
        Write-Host "  Installing frontend dependencies..." -ForegroundColor Gray
        npm install --silent 2>&1 | Out-Null
    }
    
    $processes['frontend'] = Start-Process -FilePath "npm" `
        -ArgumentList "run", "dev", "--", "--host", "127.0.0.1", "--port", "3000" `
        -WindowStyle Normal `
        -PassThru
    
    Pop-Location
    Write-Host "  [OK] Frontend started (PID: $($processes['frontend'].Id))" -ForegroundColor Green
    Start-Sleep -Seconds 10
} else {
    Write-Host "  [INFO] Frontend already running" -ForegroundColor Cyan
}

# Step 5: Start monitoring script
Write-Host "`n[5/5] Starting data monitoring..." -ForegroundColor Yellow
$monitorScript = Join-Path $ROOT_DIR "scripts\dashboard_monitor.ps1"
if (Test-Path $monitorScript) {
    $processes['monitor'] = Start-Process -FilePath "powershell.exe" `
        -ArgumentList "-ExecutionPolicy", "Bypass", "-File", $monitorScript `
        -WindowStyle Minimized `
        -PassThru
    
    Write-Host "  [OK] Monitor started (PID: $($processes['monitor'].Id))" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Monitor script not found" -ForegroundColor Yellow
}

# Verify all services
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "SYSTEM STATUS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check backend
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    if ($health.StatusCode -eq 200) {
        Write-Host "  Backend API: RUNNING" -ForegroundColor Green
    }
} catch {
    Write-Host "  Backend API: NOT RESPONDING" -ForegroundColor Red
}

# Check frontend
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    if ($frontend.StatusCode -eq 200) {
        Write-Host "  Frontend Dashboard: RUNNING" -ForegroundColor Green
    }
} catch {
    Write-Host "  Frontend Dashboard: NOT RESPONDING" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "  Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Open dashboard in browser
Start-Sleep -Seconds 3
$chromePaths = @(
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "${env:LOCALAPPDATA}\Google\Chrome\Application\chrome.exe"
)

foreach ($chromePath in $chromePaths) {
    if (Test-Path $chromePath) {
        Start-Process -FilePath $chromePath -ArgumentList "http://localhost:3000"
        break
    }
}

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 5
        # Check if processes are still running
        foreach ($key in $processes.Keys) {
            if ($processes[$key] -and $processes[$key].HasExited) {
                Write-Host "[WARN] $key process exited!" -ForegroundColor Yellow
            }
        }
    }
} catch {
    Write-Host "`nStopping all services..." -ForegroundColor Yellow
    Stop-AllProcesses
}
