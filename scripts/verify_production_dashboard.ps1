# Production Dashboard Verification - End-to-End
# Run from repo root: powershell -ExecutionPolicy Bypass -File scripts\verify_production_dashboard.ps1
#
# Prerequisites: Backend (8000) and Frontend (3000) must be running

$ErrorActionPreference = "Continue"
$base = "http://localhost:8000"
$frontend = "http://localhost:3000"
$failed = 0
$warnings = 0

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PRODUCTION DASHBOARD VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Bootstrap
Write-Host "[1] Bootstrap (ensure dirs + files)..." -ForegroundColor Yellow
$root = if ($PSScriptRoot) { (Get-Item $PSScriptRoot).Parent.FullName } else { (Get-Location).Path }
if (Test-Path (Join-Path $root "scripts\ensure_dirs_and_bootstrap.ps1")) {
    & powershell -ExecutionPolicy Bypass -File (Join-Path $root "scripts\ensure_dirs_and_bootstrap.ps1") | Out-Null
    Write-Host "    [OK] Bootstrap complete" -ForegroundColor Green
} else {
    Write-Host "    [WARN] Bootstrap script not found" -ForegroundColor Yellow
    $warnings++
}

# 2. Backend health
Write-Host "`n[2] Backend health..." -ForegroundColor Yellow
try {
    $r = Invoke-RestMethod -Uri "$base/api/health" -TimeoutSec 5
    if ($r.status -eq "ok") {
        Write-Host "    [OK] Backend responding" -ForegroundColor Green
    } else {
        Write-Host "    [WARN] Backend status: $($r.status)" -ForegroundColor Yellow
        $warnings++
    }
} catch {
    Write-Host "    [FAIL] Backend not responding: $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}

# 3. Security headers
Write-Host "`n[3] Security headers..." -ForegroundColor Yellow
try {
    $h = Invoke-WebRequest -Uri "$base/api/health" -UseBasicParsing -TimeoutSec 5
    $headers = @("X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection")
    $missing = $headers | Where-Object { -not $h.Headers[$_] }
    if ($missing.Count -eq 0) {
        Write-Host "    [OK] Security headers present" -ForegroundColor Green
    } else {
        Write-Host "    [WARN] Missing headers: $($missing -join ', ')" -ForegroundColor Yellow
        $warnings++
    }
} catch {
    Write-Host "    [SKIP] Could not check headers" -ForegroundColor Gray
}

# 4. Critical API endpoints
Write-Host "`n[4] Critical API endpoints..." -ForegroundColor Yellow
$endpoints = @(
    @{n="State"; u="$base/api/state"},
    @{n="Positions"; u="$base/api/positions"},
    @{n="Chain"; u="$base/api/chain/NIFTY"},
    @{n="ML"; u="$base/api/ml/compare"}
)
foreach ($ep in $endpoints) {
    try {
        $null = Invoke-RestMethod -Uri $ep.u -TimeoutSec 5
        Write-Host "    [OK] $($ep.n)" -ForegroundColor Green
    } catch {
        Write-Host "    [FAIL] $($ep.n): $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }
}

# 5. Frontend
Write-Host "`n[5] Frontend..." -ForegroundColor Yellow
try {
    $f = Invoke-WebRequest -Uri $frontend -UseBasicParsing -TimeoutSec 5
    if ($f.StatusCode -eq 200 -and $f.Content -match "root") {
        Write-Host "    [OK] Frontend responding" -ForegroundColor Green
    } else {
        Write-Host "    [WARN] Frontend returned $($f.StatusCode)" -ForegroundColor Yellow
        $warnings++
    }
} catch {
    Write-Host "    [FAIL] Frontend not responding: $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}

# 6. Production build
Write-Host "`n[6] Production build check..." -ForegroundColor Yellow
$distPath = Join-Path $root "dashboard\frontend\dist\index.html"
if (Test-Path $distPath) {
    Write-Host "    [OK] dist/index.html exists" -ForegroundColor Green
} else {
    Write-Host "    [INFO] Run: cd dashboard\frontend && npm run build" -ForegroundColor Gray
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
if ($failed -eq 0) {
    Write-Host "  Status: PASS" -ForegroundColor Green
    Write-Host "  Warnings: $warnings" -ForegroundColor $(if ($warnings -gt 0) { "Yellow" } else { "Green" })
    Write-Host "`n  Dashboard: $frontend" -ForegroundColor Gray
    Write-Host "  API Docs:  $base/docs" -ForegroundColor Gray
    exit 0
} else {
    Write-Host "  Status: FAIL ($failed critical)" -ForegroundColor Red
    Write-Host "  Ensure backend and frontend are running." -ForegroundColor Yellow
    exit 1
}
