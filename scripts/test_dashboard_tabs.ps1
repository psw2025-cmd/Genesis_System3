# Dashboard Tab API Test - Verifies each tab's backend endpoints
# Run from repo root with backend running: powershell -File scripts\test_dashboard_tabs.ps1
$base = "http://localhost:8000"
$script:failed = 0
$script:passed = 0

function Test-Endpoint {
    param($name, $url, $method = "GET", $body = $null)
    try {
        if ($method -eq "GET") {
            $r = Invoke-RestMethod -Uri $url -TimeoutSec 5 -ErrorAction Stop
        } else {
            $r = Invoke-RestMethod -Uri $url -Method $method -Body ($body | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 5 -ErrorAction Stop
        }
        $script:passed++
        Write-Host "[PASS] $name" -ForegroundColor Green
        return $true
    } catch {
        $script:failed++
        Write-Host "[FAIL] $name - $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

Write-Host "`n=== Dashboard Tab API Tests ===" -ForegroundColor Cyan

# Overview
Test-Endpoint "Overview/Health" "$base/api/health" | Out-Null
Test-Endpoint "Overview/State" "$base/api/state" | Out-Null
Test-Endpoint "Overview/Perf" "$base/api/perf" | Out-Null

# Chain
Test-Endpoint "Chain" "$base/api/chain/NIFTY" | Out-Null

# Signals
Test-Endpoint "Signals/Top" "$base/api/signal/top" | Out-Null
Test-Endpoint "Signals/QC" "$base/api/qc" | Out-Null

# Trading
Test-Endpoint "Trading/Positions" "$base/api/positions" | Out-Null
Test-Endpoint "Trading/PnL" "$base/api/pnl" | Out-Null

# Alerts
Test-Endpoint "Alerts/Recent" "$base/api/alerts/recent?limit=10" | Out-Null

# Risk
Test-Endpoint "Risk/CheckLimits" "$base/api/risk/check-limits" "POST" @{max_positions=5; max_exposure=100000} | Out-Null

# Charts
Test-Endpoint "Charts/Heatmap" "$base/api/charting/heatmap/NIFTY" | Out-Null

# ML
Test-Endpoint "ML/Performance" "$base/api/ml/performance" | Out-Null
Test-Endpoint "ML/Compare" "$base/api/ml/compare" | Out-Null

# Model
Test-Endpoint "Model/Logs" "$base/api/logs/tail?lines=5" | Out-Null
Test-Endpoint "Model/Secrets" "$base/api/audit/secrets" | Out-Null

# Control
Test-Endpoint "Control/Runner" "$base/api/runner/status" | Out-Null
Test-Endpoint "Control/Learning" "$base/api/learning/status" | Out-Null
Test-Endpoint "Control/Validation" "$base/api/validation/status" | Out-Null

# Agent
Test-Endpoint "Agent/Memory" "$base/api/agent/memory" | Out-Null
Test-Endpoint "Agent/Issues" "$base/api/agent/issues" | Out-Null

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
if ($script:failed -eq 0) {
    Write-Host "All $($script:passed) endpoint checks PASSED" -ForegroundColor Green
    exit 0
} else {
    Write-Host "$($script:failed) endpoint(s) FAILED" -ForegroundColor Red
    exit 1
}
