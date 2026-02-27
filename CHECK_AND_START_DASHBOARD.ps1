# Comprehensive Dashboard Check and Start Script
# Verifies backend, frontend, and opens in Chrome

$ErrorActionPreference = "Continue"
$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$VENV_DIR = Join-Path $ROOT_DIR "venv"
$BACKEND_DIR = Join-Path $ROOT_DIR "dashboard\backend"
$FRONTEND_DIR = Join-Path $ROOT_DIR "dashboard\frontend"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DASHBOARD COMPREHENSIVE CHECK & START" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Track processes
$backendProcess = $null
$frontendProcess = $null

# Cleanup function
function Cleanup-Processes {
    Write-Host "`n[CLEANUP] Stopping processes..." -ForegroundColor Yellow
    if ($backendProcess -and -not $backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "  Backend stopped" -ForegroundColor Green
    }
    if ($frontendProcess -and -not $frontendProcess.HasExited) {
        Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "  Frontend stopped" -ForegroundColor Green
    }
}

# Register cleanup
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Cleanup-Processes } | Out-Null

# Step 1: Check Python and venv
Write-Host "[1/8] Checking Python environment..." -ForegroundColor Yellow
if (-not (Test-Path "$VENV_DIR\Scripts\python.exe")) {
    Write-Host "  [FAIL] Virtual environment not found at $VENV_DIR" -ForegroundColor Red
    Write-Host "  Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $VENV_DIR
    if (-not (Test-Path "$VENV_DIR\Scripts\python.exe")) {
        Write-Host "  [FAIL] Failed to create venv" -ForegroundColor Red
        exit 1
    }
}
Write-Host "  [OK] Python venv found" -ForegroundColor Green

# Step 2: Install backend dependencies
Write-Host "`n[2/8] Checking backend dependencies..." -ForegroundColor Yellow
Push-Location $BACKEND_DIR
& "$VENV_DIR\Scripts\pip.exe" install --quiet -q -r requirements.txt 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [WARN] Some dependencies may have issues, continuing..." -ForegroundColor Yellow
} else {
    Write-Host "  [OK] Backend dependencies installed" -ForegroundColor Green
}
Pop-Location

# Step 3: Check if backend is already running
Write-Host "`n[3/8] Checking backend status..." -ForegroundColor Yellow
$existingBackend = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($existingBackend) {
    Write-Host "  [INFO] Backend already running on port 8000" -ForegroundColor Cyan
    $backendRunning = $true
} else {
    Write-Host "  [INFO] Starting backend server..." -ForegroundColor Cyan
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
    
    $backendProcess = Start-Process -FilePath "$VENV_DIR\Scripts\python.exe" `
        -ArgumentList "$env:TEMP\dashboard_backend_start.py" `
        -WindowStyle Normal `
        -PassThru
    
    Write-Host "  [INFO] Backend process started (PID: $($backendProcess.Id))" -ForegroundColor Cyan
    Write-Host "  Waiting for backend to start..." -ForegroundColor Gray
    Start-Sleep -Seconds 8
    $backendRunning = $false
}

# Step 4: Test backend health
Write-Host "`n[4/8] Testing backend health endpoint..." -ForegroundColor Yellow
$maxRetries = 5
$retryCount = 0
$backendOk = $false

while ($retryCount -lt $maxRetries) {
    try {
        $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        if ($healthResponse.StatusCode -eq 200) {
            $healthData = $healthResponse.Content | ConvertFrom-Json
            Write-Host "  [OK] Backend health: 200" -ForegroundColor Green
            Write-Host "    Status: $($healthData.status)" -ForegroundColor Gray
            Write-Host "    Timestamp: $($healthData.timestamp)" -ForegroundColor Gray
            $backendOk = $true
            break
        }
    } catch {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Write-Host "  Retry $retryCount/$maxRetries..." -ForegroundColor Gray
            Start-Sleep -Seconds 2
        } else {
            Write-Host "  [FAIL] Backend not responding after $maxRetries retries" -ForegroundColor Red
            Write-Host "    Error: $_" -ForegroundColor Red
        }
    }
}

if (-not $backendOk) {
    Write-Host "`n[FAIL] Backend health check failed. Please check backend logs." -ForegroundColor Red
    Cleanup-Processes
    exit 1
}

# Step 5: Test all API endpoints
Write-Host "`n[5/8] Testing API endpoints..." -ForegroundColor Yellow
$endpoints = @(
    @{Path="/api/health"; Name="Health"},
    @{Path="/api/qc"; Name="QC"},
    @{Path="/api/signal/top"; Name="Signal"},
    @{Path="/api/positions"; Name="Positions"},
    @{Path="/api/pnl"; Name="PnL"},
    @{Path="/api/perf"; Name="Performance"}
)

$endpointsOk = $true
foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000$($endpoint.Path)" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "  [OK] $($endpoint.Name): 200" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] $($endpoint.Name): Status $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  [WARN] $($endpoint.Name): $_" -ForegroundColor Yellow
        # Don't fail - some endpoints may return errors if no data
    }
}

# Step 6: Check Node.js and npm
Write-Host "`n[6/8] Checking Node.js and npm..." -ForegroundColor Yellow
$nodeOk = Get-Command node -ErrorAction SilentlyContinue
$npmOk = Get-Command npm -ErrorAction SilentlyContinue

if (-not $nodeOk) {
    Write-Host "  [FAIL] Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    Write-Host "    Download from: https://nodejs.org/" -ForegroundColor Gray
    Cleanup-Processes
    exit 1
}
if (-not $npmOk) {
    Write-Host "  [FAIL] npm not found" -ForegroundColor Red
    Cleanup-Processes
    exit 1
}

$nodeVersion = node --version
$npmVersion = npm --version
Write-Host "  [OK] Node.js: $nodeVersion" -ForegroundColor Green
Write-Host "  [OK] npm: $npmVersion" -ForegroundColor Green

# Step 7: Install frontend dependencies and start frontend
Write-Host "`n[7/8] Setting up frontend..." -ForegroundColor Yellow
Push-Location $FRONTEND_DIR

if (-not (Test-Path "node_modules")) {
    Write-Host "  Installing frontend dependencies (this may take a minute)..." -ForegroundColor Cyan
    npm install 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [WARN] npm install had some issues, continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "  [OK] Frontend dependencies installed" -ForegroundColor Green
    }
} else {
    Write-Host "  [OK] Frontend dependencies already installed" -ForegroundColor Green
}

# Check if frontend is already running
$existingFrontend = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($existingFrontend) {
    Write-Host "  [INFO] Frontend already running on port 3000" -ForegroundColor Cyan
    $frontendRunning = $true
} else {
    Write-Host "  Starting frontend dev server..." -ForegroundColor Cyan
    $frontendProcess = Start-Process -FilePath "npm" `
        -ArgumentList "run", "dev", "--", "--host", "127.0.0.1", "--port", "3000" `
        -WindowStyle Normal `
        -PassThru
    
    Write-Host "  [INFO] Frontend process started (PID: $($frontendProcess.Id))" -ForegroundColor Cyan
    Write-Host "  Waiting for frontend to start..." -ForegroundColor Gray
    Start-Sleep -Seconds 10
    $frontendRunning = $false
}

Pop-Location

# Step 8: Test frontend
Write-Host "`n[8/8] Testing frontend..." -ForegroundColor Yellow
$maxRetries = 5
$retryCount = 0
$frontendOk = $false

while ($retryCount -lt $maxRetries) {
    try {
        $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($frontendResponse.StatusCode -eq 200) {
            Write-Host "  [OK] Frontend: 200" -ForegroundColor Green
            $frontendOk = $true
            break
        }
    } catch {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Write-Host "  Retry $retryCount/$maxRetries..." -ForegroundColor Gray
            Start-Sleep -Seconds 3
        } else {
            Write-Host "  [WARN] Frontend not responding (may still be starting)" -ForegroundColor Yellow
        }
    }
}

# Final summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DASHBOARD STATUS SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API:" -ForegroundColor White
Write-Host "  Status: $(if ($backendOk) { 'RUNNING' -ForegroundColor Green } else { 'FAILED' -ForegroundColor Red })" -ForegroundColor $(if ($backendOk) { 'Green' } else { 'Red' })
Write-Host "  URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend Dashboard:" -ForegroundColor White
Write-Host "  Status: $(if ($frontendOk) { 'RUNNING' -ForegroundColor Green } else { 'STARTING...' -ForegroundColor Yellow })" -ForegroundColor $(if ($frontendOk) { 'Green' } else { 'Yellow' })
Write-Host "  URL: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

# Open in Chrome
if ($frontendOk) {
    Write-Host "Opening dashboard in Google Chrome..." -ForegroundColor Cyan
    $chromePaths = @(
        "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "${env:LOCALAPPDATA}\Google\Chrome\Application\chrome.exe"
    )
    
    $chromeFound = $false
    foreach ($chromePath in $chromePaths) {
        if (Test-Path $chromePath) {
            Start-Process -FilePath $chromePath -ArgumentList "http://localhost:3000"
            Write-Host "  [OK] Opened http://localhost:3000 in Chrome" -ForegroundColor Green
            $chromeFound = $true
            break
        }
    }
    
    if (-not $chromeFound) {
        Write-Host "  [WARN] Chrome not found in standard locations" -ForegroundColor Yellow
        Write-Host "  Please manually open: http://localhost:3000" -ForegroundColor Cyan
    }
} else {
    Write-Host "Frontend is still starting. Please wait and then open:" -ForegroundColor Yellow
    Write-Host "  http://localhost:3000" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 5
        # Check if processes are still running
        if ($backendProcess -and $backendProcess.HasExited) {
            Write-Host "[WARN] Backend process exited!" -ForegroundColor Yellow
        }
        if ($frontendProcess -and $frontendProcess.HasExited) {
            Write-Host "[WARN] Frontend process exited!" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    Cleanup-Processes
}
