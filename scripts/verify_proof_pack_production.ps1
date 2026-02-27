# scripts/verify_proof_pack_production.ps1
# Production-Grade Proof Pack Verifier
# Usage: powershell -ExecutionPolicy Bypass -File scripts\verify_proof_pack_production.ps1

$ErrorActionPreference = "Stop"
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "================================================================================"
Write-Host "GENESIS SYSTEM3 - PRODUCTION-GRADE PROOF PACK VERIFIER"
Write-Host "================================================================================"
Write-Host ""

# Change to project root
Set-Location $PSScriptRoot\..
$projectRoot = Get-Location

# Find latest run folder or use default proof_pack
$proofPackDir = ".\outputs\proof_pack"
$latestRun = Get-ChildItem $proofPackDir -Directory -Filter "RUN_*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($latestRun) {
    $runFolder = $latestRun.FullName
    Write-Host "[INFO] Using latest run folder: $($latestRun.Name)"
} else {
    # Fallback to old structure
    $runFolder = $proofPackDir
    Write-Host "[INFO] Using default proof_pack folder"
}

$allPassed = $true
$failures = @()
$warnings = @()

# Function to check file exists and is valid JSON
function Test-JsonFile {
    param([string]$Path, [string]$Scenario)
    
    if (-not (Test-Path $Path)) {
        $script:allPassed = $false
        $script:failures += "$Scenario`: File not found: $(Split-Path $Path -Leaf)"
        return $null
    }
    
    try {
        $content = Get-Content $Path -Raw -Encoding UTF8
        $json = $content | ConvertFrom-Json
        return $json
    } catch {
        $script:allPassed = $false
        $script:failures += "$Scenario`: Invalid JSON in $(Split-Path $Path -Leaf): $_"
        return $null
    }
}

# Function to check required keys
function Test-RequiredKeys {
    param([object]$Obj, [string[]]$RequiredKeys, [string]$Scenario, [string]$File)
    
    foreach ($key in $RequiredKeys) {
        if (-not $Obj.PSObject.Properties.Name -contains $key) {
            $script:allPassed = $false
            $script:failures += "$Scenario`: Missing required key '$key' in $File"
        }
    }
}

# Function to verify scenario
function Verify-Scenario {
    param(
        [string]$ScenarioName,
        [string]$ScenarioDir,
        [hashtable]$ExpectedOutcomes
    )
    
    Write-Host "[VERIFY] Checking $ScenarioName scenario..."
    
    if (-not (Test-Path $ScenarioDir)) {
        $script:allPassed = $false
        $script:failures += "$ScenarioName`: Directory not found"
        Write-Host "[FAIL] $ScenarioName directory not found"
        return
    }
    
    # Check required files
    $requiredFiles = @('health.json', 'qc_report_live.json', 'top_trade_signal.json', 
                       'chain_raw_live.csv', 'underlying_rank_live.csv')
    
    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $ScenarioDir $file
        if (-not (Test-Path $filePath)) {
            $script:allPassed = $false
            $script:failures += "$ScenarioName`: Required file missing: $file"
            Write-Host "[FAIL] $ScenarioName`: $file not found"
        }
    }
    
    # Verify health.json
    $healthPath = Join-Path $ScenarioDir "health.json"
    $health = Test-JsonFile -Path $healthPath -Scenario $ScenarioName
    if ($health) {
        Test-RequiredKeys -Obj $health -RequiredKeys @('timestamp', 'is_running', 'mode') -Scenario $ScenarioName -File "health.json"
        
        # Check expected outcomes
        if ($ExpectedOutcomes.ContainsKey('trades_executed')) {
            if ($health.trades_executed -ne $ExpectedOutcomes.trades_executed) {
                $script:allPassed = $false
                $script:failures += "$ScenarioName`: trades_executed=$($health.trades_executed) (expected $($ExpectedOutcomes.trades_executed))"
            }
        }
        
        if ($ExpectedOutcomes.ContainsKey('current_positions')) {
            if ($health.current_positions -ne $ExpectedOutcomes.current_positions) {
                $script:allPassed = $false
                $script:failures += "$ScenarioName`: current_positions=$($health.current_positions) (expected $($ExpectedOutcomes.current_positions))"
            }
        }
    }
    
    # Verify qc_report_live.json
    $qcPath = Join-Path $ScenarioDir "qc_report_live.json"
    $qc = Test-JsonFile -Path $qcPath -Scenario $ScenarioName
    if ($qc) {
        Test-RequiredKeys -Obj $qc -RequiredKeys @('status', 'mode', 'timestamp', 'qc_passed') -Scenario $ScenarioName -File "qc_report_live.json"
        
        # Check expected QC outcome
        if ($ExpectedOutcomes.ContainsKey('qc_passed')) {
            if ($qc.qc_passed -ne $ExpectedOutcomes.qc_passed) {
                $script:allPassed = $false
                $script:failures += "$ScenarioName`: qc_passed=$($qc.qc_passed) (expected $($ExpectedOutcomes.qc_passed))"
            }
        }
        
        if ($ExpectedOutcomes.ContainsKey('qc_status')) {
            if ($qc.status -ne $ExpectedOutcomes.qc_status) {
                $script:allPassed = $false
                $script:failures += "$ScenarioName`: qc status=$($qc.status) (expected $($ExpectedOutcomes.qc_status))"
            }
        }
    }
    
    # Verify top_trade_signal.json
    $signalPath = Join-Path $ScenarioDir "top_trade_signal.json"
    $signal = Test-JsonFile -Path $signalPath -Scenario $ScenarioName
    if ($signal) {
        Test-RequiredKeys -Obj $signal -RequiredKeys @('action', 'mode', 'timestamp', 'confidence') -Scenario $ScenarioName -File "top_trade_signal.json"
        
        # Check expected action
        if ($ExpectedOutcomes.ContainsKey('action')) {
            if ($signal.action -ne $ExpectedOutcomes.action) {
                $script:allPassed = $false
                $script:failures += "$ScenarioName`: action=$($signal.action) (expected $($ExpectedOutcomes.action))"
            }
        }
        
        # Check confidence threshold for TRADE signals
        if ($signal.action -eq "TRADE" -and $ExpectedOutcomes.ContainsKey('min_confidence')) {
            if ($signal.confidence -lt $ExpectedOutcomes.min_confidence) {
                $script:allPassed = $false
                $script:failures += "$ScenarioName`: confidence=$($signal.confidence) (expected >= $($ExpectedOutcomes.min_confidence))"
            }
        }
    }
    
    # Verify LIVE safety lock (for LIVE scenarios)
    if ($ScenarioName -like "LIVE*") {
        if ($health -and $health.trades_executed -gt 0) {
            $script:allPassed = $false
            $script:failures += "$ScenarioName`: LIVE safety lock violated - trades_executed=$($health.trades_executed) (expected 0)"
        }
    }
    
    # Check additional artifacts
    $additionalFiles = @('validation_results.json', 'perf_metrics.json', 'exceptions.json', 
                         'run_metadata.json', 'file_hashes.json')
    foreach ($file in $additionalFiles) {
        $filePath = Join-Path $ScenarioDir $file
        if (-not (Test-Path $filePath)) {
            $script:warnings += "$ScenarioName`: Optional file missing: $file"
        }
    }
    
    # Check connectivity probe for LIVE scenarios
    if ($ScenarioName -like "LIVE*") {
        $probePath = Join-Path $ScenarioDir "connectivity_probe.json"
        if (-not (Test-Path $probePath)) {
            $script:warnings += "$ScenarioName`: connectivity_probe.json missing"
        } else {
            $probe = Test-JsonFile -Path $probePath -Scenario $ScenarioName
            if ($probe) {
                Write-Host "[OK] $ScenarioName`: Connectivity probe status: $($probe.status)"
            }
        }
    }
    
    Write-Host "[OK] $ScenarioName`: Basic checks passed"
    Write-Host ""
}

# Verify TREND_UP scenario
$trendUpDir = Join-Path $runFolder "TREND_UP"
Verify-Scenario -ScenarioName "TREND_UP" -ScenarioDir $trendUpDir -ExpectedOutcomes @{
    qc_passed = $true
    qc_status = "PASS"
    action = "TRADE"
    min_confidence = 0.75
    trades_executed = 1  # At least 1
    current_positions = 1  # At least 1
}

# Verify DATA_ERRORS scenario
$dataErrorsDir = Join-Path $runFolder "DATA_ERRORS"
Verify-Scenario -ScenarioName "DATA_ERRORS" -ScenarioDir $dataErrorsDir -ExpectedOutcomes @{
    qc_passed = $false
    qc_status = "FAIL"
    action = "NO_TRADE"
    trades_executed = 0
    current_positions = 0
}

# Verify LIVE_NO_DATA scenario
$liveNoDataDir = Join-Path $runFolder "LIVE_NO_DATA"
Verify-Scenario -ScenarioName "LIVE_NO_DATA" -ScenarioDir $liveNoDataDir -ExpectedOutcomes @{
    qc_status = "NO_DATA"
    action = "NO_TRADE"
    trades_executed = 0
    current_positions = 0
}

# Verify LIVE_CONNECTED_SAFE scenario
$liveSafeDir = Join-Path $runFolder "LIVE_CONNECTED_SAFE"
Verify-Scenario -ScenarioName "LIVE_CONNECTED_SAFE" -ScenarioDir $liveSafeDir -ExpectedOutcomes @{
    action = "NO_TRADE"  # Safety lock enforced
    trades_executed = 0  # Safety lock enforced
    current_positions = 0  # Safety lock enforced
}

# Check forensic audit artifacts
Write-Host "[VERIFY] Checking forensic audit artifacts..."
$auditDir = Join-Path $runFolder "AUDIT"
if (Test-Path $auditDir) {
    $auditFiles = @('env_snapshot.json', 'config_snapshot.json', 'secrets_redaction_report.json')
    foreach ($file in $auditFiles) {
        $filePath = Join-Path $auditDir $file
        if (Test-Path $filePath) {
            $audit = Test-JsonFile -Path $filePath -Scenario "AUDIT"
            if ($audit -and $file -eq "secrets_redaction_report.json") {
                if ($audit.status -ne "PASS") {
                    $script:warnings += "Secrets redaction report status: $($audit.status)"
                }
            }
            Write-Host "[OK] Audit file: $file"
        } else {
            $script:warnings += "Audit file missing: $file"
        }
    }
} else {
    $script:warnings += "AUDIT directory not found"
}
Write-Host ""

# Check file hashes
Write-Host "[VERIFY] Checking file hashes..."
$hashesPath = Join-Path $runFolder "file_hashes.json"
if (Test-Path $hashesPath) {
    $hashes = Test-JsonFile -Path $hashesPath -Scenario "HASHES"
    if ($hashes -and $hashes.files) {
        Write-Host "[OK] File hashes found for $($hashes.files.Count) files"
    }
} else {
    $script:warnings += "file_hashes.json not found"
}
Write-Host ""

# Summary
Write-Host "================================================================================"
if ($warnings.Count -gt 0) {
    Write-Host "[WARNINGS]"
    foreach ($warning in $warnings) {
        Write-Host "  - $warning"
    }
    Write-Host ""
}

if ($allPassed) {
    Write-Host "PROOF_STATUS=PASS"
    Write-Host "================================================================================"
    exit 0
} else {
    Write-Host "PROOF_STATUS=FAIL"
    Write-Host ""
    Write-Host "Failures:"
    foreach ($failure in $failures) {
        Write-Host "  - $failure"
    }
    Write-Host "================================================================================"
    exit 1
}
