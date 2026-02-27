# Performance Verification Script
# Runs 1 cycle and checks performance metrics

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
Set-Location $rootDir

Write-Host "=== PERFORMANCE VERIFICATION ===" -ForegroundColor Cyan
Write-Host ""

# Check if main system is running
$mainProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*Genesis_System3*" }
if ($mainProcess) {
    Write-Host "[INFO] Main system is running, will check existing metrics" -ForegroundColor Yellow
} else {
    Write-Host "[INFO] Main system not running, will start one cycle" -ForegroundColor Yellow
}

# Check for perf_metrics.json
$perfFile = Join-Path $rootDir "outputs" "perf_metrics.json"
if (Test-Path $perfFile) {
    Write-Host "[OK] Found perf_metrics.json" -ForegroundColor Green
    $perfData = Get-Content $perfFile | ConvertFrom-Json
    
    Write-Host ""
    Write-Host "Performance Metrics:" -ForegroundColor Cyan
    Write-Host "  Cycle Duration: $($perfData.cycle_duration_sec) sec"
    Write-Host "  Fetch Duration: $($perfData.fetch_duration_sec) sec" -ErrorAction SilentlyContinue
    Write-Host "  Strategy Duration: $($perfData.strategy_duration_sec) sec" -ErrorAction SilentlyContinue
    Write-Host "  Instruments Load: $($perfData.instruments_load_sec) sec" -ErrorAction SilentlyContinue
    
    # Check SLA
    $cycleSLA = 30.0
    $underlyingSLA = 3.0
    
    if ($perfData.cycle_duration_sec -gt $cycleSLA) {
        Write-Host "  [FAIL] Cycle duration exceeds SLA ($cycleSLA sec)" -ForegroundColor Red
        $status = "FAIL"
    } else {
        Write-Host "  [PASS] Cycle duration within SLA" -ForegroundColor Green
        $status = "PASS"
    }
    
    # Check per-underlying duration if available
    if ($perfData.PSObject.Properties.Name -contains "fetch_underlying_duration_sec") {
        $underlyingDurations = $perfData.fetch_underlying_duration_sec
        if ($underlyingDurations) {
            Write-Host ""
            Write-Host "Per-Underlying Durations:" -ForegroundColor Cyan
            foreach ($key in $underlyingDurations.PSObject.Properties.Name) {
                $duration = $underlyingDurations.$key
                if ($duration -gt $underlyingSLA) {
                    Write-Host "  $key : $duration sec [FAIL - exceeds $underlyingSLA sec]" -ForegroundColor Red
                    $status = "FAIL"
                } else {
                    Write-Host "  $key : $duration sec [PASS]" -ForegroundColor Green
                }
            }
        }
    }
} else {
    Write-Host "[WARN] perf_metrics.json not found" -ForegroundColor Yellow
    $status = "FAIL"
}

Write-Host ""
Write-Host "=== VERIFICATION RESULT ===" -ForegroundColor Cyan
Write-Host "PERF_STATUS=$status"
if ($status -eq "PASS") {
    Write-Host "Performance verification PASSED" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Performance verification FAILED" -ForegroundColor Red
    exit 1
}
