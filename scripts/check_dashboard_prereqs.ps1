# check_dashboard_prereqs.ps1
# Check prerequisites for dashboard

$ErrorActionPreference = "Continue"
$allOk = $true

Write-Host "========================================"
Write-Host "DASHBOARD PREREQUISITES CHECK"
Write-Host "========================================"

# Check Python
Write-Host "`n[1/5] Checking Python..."
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Python found: $pythonVersion"
} else {
    Write-Host "  [FAIL] Python not found"
    Write-Host "  Fix: Install Python 3.8+ from https://www.python.org/downloads/"
    $allOk = $false
}

# Check Node.js
Write-Host "`n[2/5] Checking Node.js..."
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Node.js found: $nodeVersion"
} else {
    Write-Host "  [FAIL] Node.js not found"
    Write-Host "  Fix: Install Node.js 18+ from https://nodejs.org/"
    $allOk = $false
}

# Check npm
Write-Host "`n[3/5] Checking npm..."
$npmVersion = npm --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] npm found: $npmVersion"
} else {
    Write-Host "  [FAIL] npm not found"
    Write-Host "  Fix: npm comes with Node.js - reinstall Node.js"
    $allOk = $false
}

# Check ports
Write-Host "`n[4/5] Checking ports..."
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue

if ($port8000) {
    Write-Host "  [WARN] Port 8000 is in use (backend)"
    Write-Host "  Fix: Stop the process using port 8000 or change backend port"
} else {
    Write-Host "  [OK] Port 8000 available (backend)"
}

if ($port3000) {
    Write-Host "  [WARN] Port 3000 is in use (frontend)"
    Write-Host "  Fix: Stop the process using port 3000 or change frontend port"
} else {
    Write-Host "  [OK] Port 3000 available (frontend)"
}

# Check venv
Write-Host "`n[5/5] Checking virtual environment..."
$venvPath = Join-Path $PSScriptRoot "..\venv"
if (Test-Path $venvPath) {
    Write-Host "  [OK] Virtual environment found at $venvPath"
} else {
    Write-Host "  [WARN] Virtual environment not found"
    Write-Host "  Fix: Run: python -m venv venv"
}

Write-Host "`n========================================"
if ($allOk) {
    Write-Host "STATUS: All prerequisites OK"
    exit 0
} else {
    Write-Host "STATUS: Some prerequisites missing - see fixes above"
    exit 1
}
