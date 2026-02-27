# Start Full System with Dashboard
# Kills everything and starts fresh: Trading System + Dashboard

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
Set-Location $rootDir

Write-Host "=== SYSTEM3 FULL SYSTEM STARTUP (WITH DASHBOARD) ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill everything
Write-Host "[STEP 1] Killing all existing processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
    $_.Path -like "*Genesis_System3*" -or 
    $_.CommandLine -like "*option_chain*" -or 
    $_.CommandLine -like "*uvicorn*" 
} | Stop-Process -Force -ErrorAction SilentlyContinue

Get-Process node -ErrorAction SilentlyContinue | Where-Object { 
    $_.Path -like "*Genesis_System3*" 
} | Stop-Process -Force -ErrorAction SilentlyContinue

# Kill processes on ports
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($port8000) { Stop-Process -Id $port8000.OwningProcess -Force -ErrorAction SilentlyContinue }
if ($port3000) { Stop-Process -Id $port3000.OwningProcess -Force -ErrorAction SilentlyContinue }

Start-Sleep -Seconds 3
Write-Host "  ✅ All processes killed" -ForegroundColor Green
Write-Host ""

# Step 2: Check Python
Write-Host "[STEP 2] Checking Python..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\python.exe") {
    $python = "venv\Scripts\python.exe"
    Write-Host "  ✅ Using venv Python" -ForegroundColor Green
} else {
    $python = "python"
    Write-Host "  ✅ Using system Python" -ForegroundColor Yellow
}

# Step 3: Start Main Trading System
Write-Host ""
Write-Host "[STEP 3] Starting Main Trading System..." -ForegroundColor Yellow
$tradingScript = @"
cd '$rootDir'
& '$python' option_chain_automation_master.py --refresh 5
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $tradingScript -WindowStyle Normal
Write-Host "  ✅ Trading system starting in new window" -ForegroundColor Green
Start-Sleep -Seconds 3

# Step 4: Install dashboard dependencies if needed
Write-Host ""
Write-Host "[STEP 4] Checking dashboard dependencies..." -ForegroundColor Yellow
Set-Location "dashboard\backend"
if (-not (Test-Path "..\..\venv\Scripts\python.exe")) {
    Write-Host "  ⚠️  Venv not found, using system Python" -ForegroundColor Yellow
    $python = "python"
} else {
    $python = "..\..\venv\Scripts\python.exe"
}

try {
    & $python -c "import fastapi, uvicorn" 2>&1 | Out-Null
    Write-Host "  ✅ Backend dependencies OK" -ForegroundColor Green
} catch {
    Write-Host "  Installing backend dependencies..." -ForegroundColor Yellow
    & $python -m pip install -q -r requirements.txt 2>&1 | Out-Null
    Write-Host "  ✅ Backend dependencies installed" -ForegroundColor Green
}

Set-Location "..\frontend"
if (-not (Test-Path "node_modules")) {
    Write-Host "  Installing frontend dependencies..." -ForegroundColor Yellow
    npm install --silent 2>&1 | Out-Null
    Write-Host "  ✅ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ✅ Frontend dependencies OK" -ForegroundColor Green
}

Set-Location $rootDir

# Step 5: Start Dashboard Backend
Write-Host ""
Write-Host "[STEP 5] Starting Dashboard Backend..." -ForegroundColor Yellow
$backendScript = @"
cd '$rootDir\dashboard\backend'
& '$python' -m uvicorn app:app --host 127.0.0.1 --port 8000
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript -WindowStyle Minimized
Write-Host "  ✅ Backend starting on port 8000" -ForegroundColor Green
Start-Sleep -Seconds 5

# Step 6: Start Dashboard Frontend
Write-Host ""
Write-Host "[STEP 6] Starting Dashboard Frontend..." -ForegroundColor Yellow
$frontendScript = @"
cd '$rootDir\dashboard\frontend'
npm run dev -- --host 127.0.0.1 --port 3000
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript -WindowStyle Normal
Write-Host "  ✅ Frontend starting on port 3000" -ForegroundColor Green
Start-Sleep -Seconds 8

# Step 7: Verify
Write-Host ""
Write-Host "[STEP 7] Verifying services..." -ForegroundColor Yellow
$allOk = $true

# Check trading system (check for health.json updates)
Start-Sleep -Seconds 5
$healthFile = Join-Path $rootDir "outputs\health.json"
if (Test-Path $healthFile) {
    $healthAge = (Get-Item $healthFile).LastWriteTime
    $ageSec = (Get-Date) - $healthAge
    if ($ageSec.TotalSeconds -lt 30) {
        Write-Host "  ✅ Trading System: RUNNING (health.json updated)" -ForegroundColor Green
    } else {
        Write-Host "  ⏳ Trading System: Starting... (wait for health.json update)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⏳ Trading System: Starting... (health.json not found yet)" -ForegroundColor Yellow
}

# Check backend
try {
    $b = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✅ Backend API: RUNNING" -ForegroundColor Green
} catch {
    Write-Host "  ⏳ Backend API: Starting... (may take 10-15 seconds)" -ForegroundColor Yellow
    $allOk = $false
}

# Check frontend
try {
    $f = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    Write-Host "  ✅ Frontend Dashboard: RUNNING" -ForegroundColor Green
} catch {
    Write-Host "  ⏳ Frontend Dashboard: Starting... (may take 10-15 seconds)" -ForegroundColor Yellow
    $allOk = $false
}

Write-Host ""
Write-Host "=== STARTUP COMPLETE ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services:" -ForegroundColor White
Write-Host "  1. Main Trading System: Running in PowerShell window" -ForegroundColor White
Write-Host "  2. Dashboard Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  3. Dashboard Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access Dashboard:" -ForegroundColor Yellow
Write-Host "  Open browser: http://localhost:3000" -ForegroundColor White
Write-Host ""
if ($allOk) {
    Write-Host "✅ All services are running!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some services are still starting - wait 10-15 seconds" -ForegroundColor Yellow
    Write-Host "   Check PowerShell windows for any errors" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
