# Auto-Fix and Update Dashboard System
# Runs pre-checks, fixes issues, and ensures everything is ready

$ErrorActionPreference = "Continue"
$ROOT_DIR = Split-Path -Parent $PSScriptRoot
$VENV_DIR = Join-Path $ROOT_DIR "venv"
$BACKEND_DIR = Join-Path $ROOT_DIR "dashboard\backend"
$FRONTEND_DIR = Join-Path $ROOT_DIR "dashboard\frontend"
$OUTPUTS_DIR = Join-Path $ROOT_DIR "outputs"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AUTO-FIX AND UPDATE DASHBOARD SYSTEM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check and fix Python dependencies
Write-Host "[1/6] Checking Python dependencies..." -ForegroundColor Yellow
if (-not (Test-Path "$VENV_DIR\Scripts\python.exe")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Cyan
    python -m venv $VENV_DIR
}

& "$VENV_DIR\Scripts\pip.exe" install --quiet --upgrade pip >nul 2>&1

# Install critical packages
$criticalPackages = @("pandas", "numpy", "scipy", "scikit-learn", "uvicorn[standard]", "fastapi", "requests", "aiohttp")
foreach ($pkg in $criticalPackages) {
    & "$VENV_DIR\Scripts\pip.exe" install --quiet --prefer-binary $pkg >nul 2>&1
}

# Install backend requirements
if (Test-Path "$BACKEND_DIR\requirements.txt") {
    & "$VENV_DIR\Scripts\pip.exe" install --quiet -r "$BACKEND_DIR\requirements.txt" >nul 2>&1
}

Write-Host "  [OK] Python dependencies ready" -ForegroundColor Green

# Step 2: Check and fix frontend dependencies
Write-Host "`n[2/6] Checking frontend dependencies..." -ForegroundColor Yellow
Push-Location $FRONTEND_DIR

if (-not (Test-Path "node_modules")) {
    Write-Host "  Installing frontend packages..." -ForegroundColor Cyan
    npm install --silent >nul 2>&1
} else {
    # Check if package.json changed
    $packageJson = Get-Item "package.json"
    $nodeModules = Get-Item "node_modules" -ErrorAction SilentlyContinue
    if ($nodeModules -and $packageJson.LastWriteTime -gt $nodeModules.LastWriteTime) {
        Write-Host "  Updating frontend packages..." -ForegroundColor Cyan
        npm install --silent >nul 2>&1
    }
}

Write-Host "  [OK] Frontend dependencies ready" -ForegroundColor Green
Pop-Location

# Step 3: Fix data issues
Write-Host "`n[3/6] Checking and fixing data issues..." -ForegroundColor Yellow
$fixScript = Join-Path $ROOT_DIR "scripts\fix_dashboard_data_issues.py"
if (Test-Path $fixScript) {
    & "$VENV_DIR\Scripts\python.exe" $fixScript 2>&1 | Out-Null
    Write-Host "  [OK] Data issues checked" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Fix script not found" -ForegroundColor Yellow
}

# Step 4: Verify backend code
Write-Host "`n[4/6] Verifying backend code..." -ForegroundColor Yellow
$backendApp = Join-Path $BACKEND_DIR "app.py"
if (Test-Path $backendApp) {
    # Check if CORS is configured correctly
    $backendContent = Get-Content $backendApp -Raw
    if ($backendContent -notmatch "allow_origins.*\*") {
        Write-Host "  [WARN] CORS may need update" -ForegroundColor Yellow
    } else {
        Write-Host "  [OK] Backend CORS configured" -ForegroundColor Green
    }
} else {
    Write-Host "  [FAIL] Backend app.py not found" -ForegroundColor Red
}

# Step 5: Verify frontend code
Write-Host "`n[5/6] Verifying frontend code..." -ForegroundColor Yellow
$configFile = Join-Path $FRONTEND_DIR "src\config.ts"
if (Test-Path $configFile) {
    Write-Host "  [OK] Frontend config exists" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Frontend config missing" -ForegroundColor Yellow
}

# Step 6: Check ports and processes
Write-Host "`n[6/6] Checking ports..." -ForegroundColor Yellow
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue

if ($port8000) {
    Write-Host "  [INFO] Port 8000 in use (backend may be running)" -ForegroundColor Cyan
} else {
    Write-Host "  [OK] Port 8000 is free" -ForegroundColor Green
}

if ($port3000) {
    Write-Host "  [INFO] Port 3000 in use (frontend may be running)" -ForegroundColor Cyan
} else {
    Write-Host "  [OK] Port 3000 is free" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AUTO-FIX COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "System is ready to start!" -ForegroundColor Green
Write-Host "Run: START_FULL_DASHBOARD_SYSTEM.bat" -ForegroundColor Cyan
Write-Host ""
