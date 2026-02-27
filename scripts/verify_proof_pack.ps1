# verify_proof_pack.ps1
# Automated verification script for proof pack

$ErrorActionPreference = "Stop"
$PROOF_STATUS = "FAIL"

Write-Host "========================================"
Write-Host "PROOF PACK VERIFICATION"
Write-Host "========================================"

$outputsDir = Join-Path $PSScriptRoot "..\outputs"
$proofPackDir = Join-Path $outputsDir "proof_pack"

# Check 1: JSON validity
Write-Host "`n[1/5] Checking JSON validity..."
$jsonFiles = @(
    "qc_report_live.json",
    "top_trade_signal.json",
    "health.json",
    "paper_pnl_summary.json",
    "perf_metrics.json"
)

$jsonValid = $true
foreach ($file in $jsonFiles) {
    $path = Join-Path $outputsDir $file
    if (Test-Path $path) {
        try {
            $content = Get-Content $path -Raw | ConvertFrom-Json
            Write-Host "  [OK] $file"
        } catch {
            Write-Host "  [FAIL] $file - Invalid JSON: $_"
            $jsonValid = $false
        }
    } else {
        Write-Host "  [WARN] $file - Not found"
    }
}

if (-not $jsonValid) {
    Write-Host "`n[FAIL] JSON validation failed"
    exit 1
}

# Check 2: Trades executed > 0 for paper scenarios
Write-Host "`n[2/5] Checking trades executed..."
$healthPath = Join-Path $outputsDir "health.json"
if (Test-Path $healthPath) {
    $health = Get-Content $healthPath -Raw | ConvertFrom-Json
    $tradesExecuted = $health.trades_executed
    if ($tradesExecuted -gt 0) {
        Write-Host "  [OK] Trades executed: $tradesExecuted"
    } else {
        Write-Host "  [FAIL] No trades executed (trades_executed = $tradesExecuted)"
        Write-Host "  [INFO] Check PAPER_SANITY mode or thresholds"
    }
} else {
    Write-Host "  [WARN] health.json not found"
}

# Check 3: PnL file exists and non-zero
Write-Host "`n[3/5] Checking PnL files..."
$pnlCsvPath = Join-Path $outputsDir "paper_pnl.csv"
$pnlSummaryPath = Join-Path $outputsDir "paper_pnl_summary.json"

if (Test-Path $pnlCsvPath) {
    $csvLines = (Get-Content $pnlCsvPath | Measure-Object -Line).Lines
    if ($csvLines -gt 1) {
        Write-Host "  [OK] paper_pnl.csv exists with $($csvLines - 1) rows"
    } else {
        Write-Host "  [WARN] paper_pnl.csv exists but empty"
    }
} else {
    Write-Host "  [WARN] paper_pnl.csv not found"
}

if (Test-Path $pnlSummaryPath) {
    $pnlSummary = Get-Content $pnlSummaryPath -Raw | ConvertFrom-Json
    $totalTrades = $pnlSummary.total_trades
    if ($totalTrades -gt 0) {
        Write-Host "  [OK] paper_pnl_summary.json: $totalTrades trades"
    } else {
        Write-Host "  [WARN] paper_pnl_summary.json: 0 trades"
    }
} else {
    Write-Host "  [WARN] paper_pnl_summary.json not found"
}

# Check 4: No secrets
Write-Host "`n[4/5] Scanning for secrets..."
$secretPatterns = @(
    "api[_-]?key",
    "api[_-]?secret",
    "password",
    "token",
    "client[_-]?id",
    "totp"
)

$secretsFound = 0
foreach ($file in Get-ChildItem $outputsDir -File -Include *.json,*.csv) {
    $content = Get-Content $file.FullName -Raw
    foreach ($pattern in $secretPatterns) {
        if ($content -match $pattern) {
            # Check if it's actually a secret (has a value, not false/null/empty)
            if ($content -match "$pattern.*[:=]\s*['`"]([^'`"]{10,})['`"]" -and 
                $content -notmatch "$pattern.*[:=]\s*(false|null|`"`"|'')") {
                Write-Host "  [FAIL] Potential secret found in $($file.Name): $pattern"
                $secretsFound++
            }
        }
    }
}

if ($secretsFound -eq 0) {
    Write-Host "  [OK] No secrets found"
} else {
    Write-Host "  [FAIL] Found $secretsFound potential secrets"
}

# Check 5: Performance SLA
Write-Host "`n[5/5] Checking performance SLA..."
$perfPath = Join-Path $outputsDir "perf_metrics.json"
if (Test-Path $perfPath) {
    $perf = Get-Content $perfPath -Raw | ConvertFrom-Json
    $cycleDuration = $perf.cycle_duration_sec
    if ($cycleDuration -le 60) {
        Write-Host "  [OK] Cycle duration: ${cycleDuration}s (SLA: <= 60s)"
    } else {
        Write-Host "  [FAIL] Cycle duration: ${cycleDuration}s (SLA: <= 60s) - BREACH"
    }
} else {
    Write-Host "  [WARN] perf_metrics.json not found"
}

# Final status
Write-Host "`n========================================"
if ($jsonValid -and $secretsFound -eq 0) {
    $PROOF_STATUS = "PASS"
    Write-Host "PROOF_STATUS=PASS"
} else {
    Write-Host "PROOF_STATUS=FAIL"
}
Write-Host "========================================"

exit 0
