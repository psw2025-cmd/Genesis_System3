# Smoke test for Genesis System3 Dashboard
# Run from repo root: powershell -File scripts\smoke_test_dashboard.ps1
$ErrorActionPreference = "Continue"
$failed = 0

Write-Host "=== Genesis System3 Dashboard Smoke Test ===" -ForegroundColor Cyan

# Backend health
try {
    $r = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 5
    if ($r.status -eq "ok") {
        Write-Host "[PASS] Backend /api/health" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Backend /api/health - status: $($r.status)" -ForegroundColor Red
        $failed++
    }
} catch {
    Write-Host "[FAIL] Backend /api/health - $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}

# Backend state
try {
    $r = Invoke-RestMethod -Uri "http://localhost:8000/api/state" -TimeoutSec 5
    Write-Host "[PASS] Backend /api/state" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Backend /api/state - $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}

# Frontend (optional - may not be running)
try {
    $r = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 3
    if ($r.StatusCode -eq 200) {
        Write-Host "[PASS] Frontend http://localhost:3000" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Frontend returned $($r.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[SKIP] Frontend not running (optional)" -ForegroundColor Gray
}

Write-Host ""
if ($failed -eq 0) {
    Write-Host "Smoke test PASSED" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Smoke test FAILED ($failed checks)" -ForegroundColor Red
    exit 1
}
