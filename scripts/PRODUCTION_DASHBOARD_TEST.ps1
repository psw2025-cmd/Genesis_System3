# Production Dashboard Testing Script
# Comprehensive testing with multiple users and data validation

$ErrorActionPreference = "Continue"
$ROOT_DIR = Split-Path -Parent $PSScriptRoot
$VENV_DIR = Join-Path $ROOT_DIR "venv"
$OUTPUTS_DIR = Join-Path $ROOT_DIR "outputs"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PRODUCTION DASHBOARD TESTING SUITE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if services are running
Write-Host "[1/6] Checking services..." -ForegroundColor Yellow
$backendOk = $false
$frontendOk = $false

try {
    $backend = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    if ($backend.StatusCode -eq 200) {
        $backendOk = $true
        Write-Host "  [OK] Backend running" -ForegroundColor Green
    }
} catch {
    Write-Host "  [FAIL] Backend not running" -ForegroundColor Red
    Write-Host "    Please start backend: cd dashboard\backend && ..\..\venv\Scripts\python.exe -m uvicorn app:app" -ForegroundColor Yellow
    exit 1
}

try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    if ($frontend.StatusCode -eq 200) {
        $frontendOk = $true
        Write-Host "  [OK] Frontend running" -ForegroundColor Green
    }
} catch {
    Write-Host "  [WARN] Frontend not running (optional for API tests)" -ForegroundColor Yellow
}

# Step 2: Test all API endpoints
Write-Host "`n[2/6] Testing API endpoints..." -ForegroundColor Yellow
$endpoints = @(
    "/api/health",
    "/api/qc",
    "/api/signal/top",
    "/api/positions",
    "/api/pnl",
    "/api/perf",
    "/api/chain/NIFTY",
    "/api/chain/BANKNIFTY"
)

$endpointResults = @{}
foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000$endpoint" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $endpointResults[$endpoint] = "PASS"
            Write-Host "  [OK] $endpoint" -ForegroundColor Green
        } else {
            $endpointResults[$endpoint] = "FAIL (Status: $($response.StatusCode))"
            Write-Host "  [FAIL] $endpoint - Status $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        $endpointResults[$endpoint] = "FAIL ($_)"
        Write-Host "  [FAIL] $endpoint - $_" -ForegroundColor Red
    }
}

# Step 3: Run data validation
Write-Host "`n[3/6] Running data validation against live sources..." -ForegroundColor Yellow
$validatorScript = Join-Path $ROOT_DIR "scripts\dashboard_data_validator.py"
if (Test-Path $validatorScript) {
    Write-Host "  Running validator..." -ForegroundColor Gray
    $validatorOutput = & "$VENV_DIR\Scripts\python.exe" $validatorScript 2>&1
    Write-Host $validatorOutput
    
    # Check validation results
    $validationDir = Join-Path $OUTPUTS_DIR "validation"
    if (Test-Path $validationDir) {
        $latestReport = Get-ChildItem $validationDir -Filter "dashboard_validation_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($latestReport) {
            $reportData = Get-Content $latestReport.FullName | ConvertFrom-Json
            Write-Host "  Validation Report:" -ForegroundColor Cyan
            Write-Host "    Total: $($reportData.total_validations)" -ForegroundColor White
            Write-Host "    Passed: $($reportData.passed)" -ForegroundColor Green
            Write-Host "    Failed: $($reportData.failed)" -ForegroundColor $(if ($reportData.failed -gt 0) { 'Red' } else { 'Green' })
            Write-Host "    Critical Issues: $($reportData.critical_issues)" -ForegroundColor $(if ($reportData.critical_issues -gt 0) { 'Red' } else { 'Green' })
        }
    }
} else {
    Write-Host "  [WARN] Validator script not found" -ForegroundColor Yellow
}

# Step 4: Run multi-user test
Write-Host "`n[4/6] Running multi-user concurrent test..." -ForegroundColor Yellow
$multiUserScript = Join-Path $ROOT_DIR "scripts\multi_user_dashboard_test.py"
if (Test-Path $multiUserScript) {
    Write-Host "  Starting 5 concurrent users for 30 seconds..." -ForegroundColor Gray
    $multiUserOutput = & "$VENV_DIR\Scripts\python.exe" $multiUserScript 2>&1
    Write-Host $multiUserOutput
    
    # Check multi-user test results
    $testReports = Get-ChildItem $validationDir -Filter "multi_user_test_*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($testReports) {
        $testData = Get-Content $testReports.FullName | ConvertFrom-Json
        Write-Host "  Multi-User Test Results:" -ForegroundColor Cyan
        Write-Host "    Users: $($testData.num_users)" -ForegroundColor White
        Write-Host "    Total Requests: $($testData.total_requests)" -ForegroundColor White
        Write-Host "    Error Rate: $([math]::Round($testData.error_rate, 2))%" -ForegroundColor $(if ($testData.error_rate -lt 1) { 'Green' } else { 'Yellow' })
        Write-Host "    Avg Response Time: $([math]::Round($testData.avg_response_time_ms, 2))ms" -ForegroundColor White
    }
} else {
    Write-Host "  [WARN] Multi-user test script not found" -ForegroundColor Yellow
}

# Step 5: Performance test
Write-Host "`n[5/6] Running performance test..." -ForegroundColor Yellow
$performanceResults = @{}
$numRequests = 100
$successCount = 0
$totalTime = 0
$minTime = [double]::MaxValue
$maxTime = 0

Write-Host "  Making $numRequests requests to /api/health..." -ForegroundColor Gray
for ($i = 1; $i -le $numRequests; $i++) {
    try {
        $startTime = Get-Date
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalMilliseconds
        
        if ($response.StatusCode -eq 200) {
            $successCount++
            $totalTime += $duration
            if ($duration -lt $minTime) { $minTime = $duration }
            if ($duration -gt $maxTime) { $maxTime = $duration }
        }
    } catch {
        # Failed request
    }
    
    if ($i % 20 -eq 0) {
        Write-Host "    Progress: $i/$numRequests" -ForegroundColor Gray
    }
}

if ($successCount -gt 0) {
    $avgTime = $totalTime / $successCount
    $performanceResults = @{
        "success_rate" = ($successCount / $numRequests * 100)
        "avg_response_time_ms" = [math]::Round($avgTime, 2)
        "min_response_time_ms" = [math]::Round($minTime, 2)
        "max_response_time_ms" = [math]::Round($maxTime, 2)
    }
    
    Write-Host "  Performance Results:" -ForegroundColor Cyan
    Write-Host "    Success Rate: $([math]::Round($performanceResults.success_rate, 2))%" -ForegroundColor $(if ($performanceResults.success_rate -ge 99) { 'Green' } else { 'Yellow' })
    Write-Host "    Avg Response: $($performanceResults.avg_response_time_ms)ms" -ForegroundColor White
    Write-Host "    Min Response: $($performanceResults.min_response_time_ms)ms" -ForegroundColor White
    Write-Host "    Max Response: $($performanceResults.max_response_time_ms)ms" -ForegroundColor White
}

# Step 6: Generate comprehensive report
Write-Host "`n[6/6] Generating comprehensive report..." -ForegroundColor Yellow
$reportPath = Join-Path $OUTPUTS_DIR "dashboard_production_test_report.json"
$report = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    backend_status = if ($backendOk) { "RUNNING" } else { "STOPPED" }
    frontend_status = if ($frontendOk) { "RUNNING" } else { "STOPPED" }
    endpoint_results = $endpointResults
    performance = $performanceResults
}

$report | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportPath -Encoding UTF8
Write-Host "  [OK] Report saved: $reportPath" -ForegroundColor Green

# Final summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TESTING COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
if ($backendOk) {
    Write-Host "  Backend: RUNNING" -ForegroundColor Green
} else {
    Write-Host "  Backend: STOPPED" -ForegroundColor Red
}
if ($frontendOk) {
    Write-Host "  Frontend: RUNNING" -ForegroundColor Green
} else {
    Write-Host "  Frontend: STOPPED" -ForegroundColor Yellow
}
Write-Host "  Endpoints Tested: $($endpoints.Count)"
Write-Host "  Endpoints Passed: $(($endpointResults.Values | Where-Object { $_ -eq 'PASS' }).Count)"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review validation reports in: outputs\validation\" -ForegroundColor White
Write-Host "  2. Check multi-user test results for consistency issues" -ForegroundColor White
Write-Host "  3. Verify performance meets requirements (<100ms avg)" -ForegroundColor White
Write-Host "  4. Fix any critical issues found in validation" -ForegroundColor White
Write-Host ""
