# Complete Dashboard Startup Script
# Starts backend and frontend with proper error handling

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
Set-Location $rootDir

Write-Host "=== SYSTEM3 ULTRA DASHBOARD - COMPLETE STARTUP ===" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1] Checking Python..." -ForegroundColor Yellow
try {
    if (Test-Path "venv\Scripts\python.exe") {
        $python = "venv\Scripts\python.exe"
        Write-Host "  ✅ Using venv Python" -ForegroundColor Green
    } else {
        $python = "python"
        Write-Host "  ✅ Using system Python" -ForegroundColor Yellow
    }
    $pyVersion = & $python --version 2>&1
    Write-Host "  Version: $pyVersion" -ForegroundColor White
} catch {
    Write-Host "  ❌ Python not found!" -ForegroundColor Red
    exit 1
}

# Check Node
Write-Host ""
Write-Host "[2] Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Node.js not found!" -ForegroundColor Red
    exit 1
}

# Install backend dependencies
Write-Host ""
Write-Host "[3] Installing backend dependencies..." -ForegroundColor Yellow
Set-Location "dashboard\backend"
try {
    & $python -m pip install -q -r requirements.txt 2>&1 | Out-Null
    Write-Host "  ✅ Backend dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Some dependencies may be missing" -ForegroundColor Yellow
}

# Install frontend dependencies
Write-Host ""
Write-Host "[4] Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location "..\frontend"
if (-not (Test-Path "node_modules")) {
    npm install --silent 2>&1 | Out-Null
    Write-Host "  ✅ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ✅ Frontend dependencies already installed" -ForegroundColor Green
}

Set-Location $rootDir

# Kill existing processes
Write-Host ""
Write-Host "[5] Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn*" -or $_.Path -like "*dashboard*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process node -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*Genesis_System3*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "  ✅ Cleanup complete" -ForegroundColor Green

# Start backend
Write-Host ""
Write-Host "[6] Starting backend..." -ForegroundColor Yellow
$backendScript = @"
cd '$rootDir\dashboard\backend'
& '$python' -m uvicorn app:app --host 127.0.0.1 --port 8000
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript -WindowStyle Minimized
Start-Sleep -Seconds 5

# Start frontend
Write-Host ""
Write-Host "[7] Starting frontend..." -ForegroundColor Yellow
$frontendScript = @"
cd '$rootDir\dashboard\frontend'
npm run dev -- --host 127.0.0.1 --port 3000
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript -WindowStyle Normal
Start-Sleep -Seconds 8

# Verify
Write-Host ""
Write-Host "[8] Verifying services..." -ForegroundColor Yellow
$backendOk = $false
$frontendOk = $false

try {
    $b = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 5
    $backendOk = $true
    Write-Host "  ✅ Backend: RUNNING" -ForegroundColor Green
} catch {
    Write-Host "  ⏳ Backend: Starting... (may take 10-15 seconds)" -ForegroundColor Yellow
}

try {
    $f = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    $frontendOk = $true
    Write-Host "  ✅ Frontend: RUNNING" -ForegroundColor Green
} catch {
    Write-Host "  ⏳ Frontend: Starting... (may take 10-15 seconds)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== DASHBOARD STARTUP COMPLETE ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor White
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
if ($backendOk -and $frontendOk) {
    Write-Host "✅ Both services are running!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Services are starting - wait 10-15 seconds and refresh" -ForegroundColor Yellow
    Write-Host "   Check PowerShell windows for any errors" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
