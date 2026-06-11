# System3 Ultra: Daily All-In-One Health & Backup Script
# Runs core health checks, Ultra checks, and snapshot creation in sequence

param(
    [switch]$RunCampaign = $false  # Set to $true to also run Phase 39 campaign
)

# Colors for output
function Write-Header {
    param([string]$Text)
    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host $Text -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Text)
    Write-Host "[OK] $Text" -ForegroundColor Green
}

function Write-Info {
    param([string]$Text)
    Write-Host "[INFO] $Text" -ForegroundColor White
}

function Write-Warn {
    param([string]$Text)
    Write-Host "[WARN] $Text" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Text)
    Write-Host "[ERROR] $Text" -ForegroundColor Red
}

# Check and activate virtual environment
function Ensure-Venv {
    if (-not $env:VIRTUAL_ENV) {
        Write-Warn "Virtual environment not activated. Activating..."
        $scriptDir = Split-Path -Parent $MyInvocation.PSCommandPath
        $venvPath = Join-Path $scriptDir "venv\Scripts\Activate.ps1"
        if (Test-Path $venvPath) {
            & $venvPath
            Write-Success "Virtual environment activated"
        } else {
            Write-Error "Virtual environment not found at $venvPath"
            return $false
        }
    }
    return $true
}

Write-Header "SYSTEM3 ULTRA: DAILY ALL-IN-ONE HEALTH & BACKUP"

if (-not (Ensure-Venv)) {
    Write-Error "Cannot proceed without virtual environment"
    exit 1
}

$results = @{
    "Phase 43 (Env Guard)" = $false
    "Phase 37 (Policy Monitor)" = $false
    "Phase 38 (Governance Summary)" = $false
    "Phase 42 (Snapshot)" = $false
    "Phase 39 (Campaign)" = $false
}

# Step 1: Environment Guard
Write-Host "`n[1/4] Running Phase 43: Environment & Broker Guard..." -ForegroundColor Green
try {
    python -m core.engine.system3_phase43_env_guard
    $results["Phase 43 (Env Guard)"] = $true
    Write-Success "Phase 43 completed"
} catch {
    Write-Error "Phase 43 failed: $_"
}
Write-Host ""

# Step 2: Policy Monitor
Write-Host "[2/4] Running Phase 37: Policy & Risk Monitor..." -ForegroundColor Green
try {
    python -m core.engine.system3_phase37_policy_risk_monitor
    $results["Phase 37 (Policy Monitor)"] = $true
    Write-Success "Phase 37 completed"
} catch {
    Write-Error "Phase 37 failed: $_"
}
Write-Host ""

# Step 3: Governance Summary
Write-Host "[3/4] Running Phase 38: Governance Summary..." -ForegroundColor Green
try {
    python -m core.engine.system3_phase38_governance_summary
    $results["Phase 38 (Governance Summary)"] = $true
    Write-Success "Phase 38 completed"
} catch {
    Write-Error "Phase 38 failed: $_"
}
Write-Host ""

# Step 4: Snapshot
Write-Host "[4/4] Running Phase 42: Create Snapshot..." -ForegroundColor Green
try {
    python -m core.engine.system3_phase42_snapshot_manager create
    $results["Phase 42 (Snapshot)"] = $true
    Write-Success "Phase 42 completed"
} catch {
    Write-Error "Phase 42 failed: $_"
}
Write-Host ""

# Optional: Phase 39 Campaign
if ($RunCampaign) {
    Write-Host "[OPTIONAL] Running Phase 39: Shadow Campaign..." -ForegroundColor Yellow
    try {
        python -m core.engine.system3_phase39_shadow_campaign
        $results["Phase 39 (Campaign)"] = $true
        Write-Success "Phase 39 completed"
    } catch {
        Write-Error "Phase 39 failed: $_"
    }
    Write-Host ""
}

# Summary
Write-Header "EXECUTION SUMMARY"

$passed = ($results.Values | Where-Object { $_ -eq $true }).Count
$total = $results.Count

foreach ($key in $results.Keys) {
    if ($results[$key]) {
        Write-Success "$key: PASS"
    } else {
        Write-Error "$key: FAIL"
    }
}

Write-Host ""
if ($passed -eq $total) {
    Write-Success "All steps completed successfully ($passed/$total)"
} else {
    Write-Warn "Some steps failed ($passed/$total passed)"
}

Write-Host ""
Write-Info "Review outputs in storage\ultra\"

