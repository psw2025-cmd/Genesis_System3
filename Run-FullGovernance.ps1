$ErrorActionPreference = "Stop"

function Invoke-Step {
    param(
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$true)][scriptblock]$Command,
        [Parameter(Mandatory=$true)][string]$ProofPath
    )
    Write-Host "`n[$Name]" -ForegroundColor Yellow
    $started = Get-Date
    # Always restore ErrorActionPreference, even on failure or exceptions.
    $oldEap = $ErrorActionPreference
    try {
        try {
            # Avoid treating native stderr output as a terminating PowerShell error.
            $ErrorActionPreference = "Continue"
            & $Command 2>&1 | Tee-Object -FilePath $ProofPath
            $exit = $LASTEXITCODE
        } finally {
            $ErrorActionPreference = $oldEap
        }

        if ($exit -ne 0) {
            throw "ExitCode=$exit"
        }
        $elapsed = (Get-Date) - $started
        Write-Host "OK ($($elapsed.TotalSeconds)s) -> $ProofPath" -ForegroundColor Green
    } catch {
        $elapsed = (Get-Date) - $started
        Write-Host "FAIL ($($elapsed.TotalSeconds)s) -> $ProofPath" -ForegroundColor Red
        throw
    }
}

Write-Host "=== Full Governance Script Start (STRICT) ===" -ForegroundColor Cyan

$repoRoot = "C:\Genesis_System3"
Set-Location $repoRoot

$logDir = Join-Path $repoRoot "logs\inspector"
if (!(Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }

Write-Host "`n[Environment]" -ForegroundColor Yellow
Write-Host "Repo: $repoRoot" -ForegroundColor Gray

$createdVenv = $false
# Use existing venv created by Run-All. If missing, create it (standalone use).
if (!(Test-Path "$repoRoot\.venv\Scripts\python.exe")) {
    Write-Host "No .venv found; creating new venv (Python 3.10)..." -ForegroundColor Yellow
    py -3.10 -m venv .venv
    $createdVenv = $true
}
& "$repoRoot\.venv\Scripts\Activate.ps1"

Invoke-Step -Name "Pip: upgrade (pip only)" -Command { python -m pip install --upgrade pip } -ProofPath (Join-Path $logDir "governance_pip_upgrade.txt")

# Limit lint scope to project code (avoid scanning .venv / node_modules).
$lintTargets = @(
    "core",
    "scripts",
    "tools",
    "phases",
    "dashboard"
) | Where-Object { Test-Path (Join-Path $repoRoot $_) }

# Dependency install is only required when the venv was created here (or when explicitly requested).
# Run-All already installs deps in Step 6; re-installing can cause noisy resolver messages and churn.
if ($createdVenv -or $env:GOVERNANCE_REINSTALL_DEPS -eq "1") {
    Invoke-Step -Name "Install: runtime requirements" -Command { pip install -r requirements_runtime.txt } -ProofPath (Join-Path $logDir "governance_install_runtime.txt")
    Invoke-Step -Name "Install: dev requirements" -Command { pip install -r requirements-dev.txt } -ProofPath (Join-Path $logDir "governance_install_dev.txt")
} else {
    "SKIP: deps already installed by Run-All Step 6 (set GOVERNANCE_REINSTALL_DEPS=1 to force reinstall)" | Out-File (Join-Path $logDir "governance_install_skipped.txt")
    Write-Host "SKIP: dependency reinstall (already handled by Run-All Step 6)" -ForegroundColor DarkYellow
}

# Basic consistency check
Invoke-Step -Name "Pip: check" -Command { pip check } -ProofPath (Join-Path $logDir "governance_pip_check.txt")

# Proof artifacts (security). pip-audit: report-only (vulns logged to pip_audit.json; see docs/FULL_ACTION_PLAN_AND_CHECKLIST.md).
Write-Host "`n[Security: pip-audit (report-only)]" -ForegroundColor Yellow
$pipAuditOut = Join-Path $logDir "governance_pip_audit_stdout.txt"
$pipAuditJson = Join-Path $logDir "pip_audit.json"
$oldEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
pip-audit -f json -o $pipAuditJson 2>&1 | Tee-Object -FilePath $pipAuditOut
$ErrorActionPreference = $oldEap
if ($LASTEXITCODE -ne 0) {
    "pip-audit reported vulnerabilities (report-only; see pip_audit.json). ExitCode=$LASTEXITCODE" | Add-Content $pipAuditOut
    Write-Host "REPORT-ONLY: vulnerabilities logged to pip_audit.json" -ForegroundColor DarkYellow
} else {
    Write-Host "OK -> $pipAuditOut" -ForegroundColor Green
}
# Safety: report-only. Prefer 'safety scan' (check deprecated Jun 2024). Auto-install if missing.
Write-Host "`n[Security: safety (report-only)]" -ForegroundColor Yellow
$safetyProof = Join-Path $logDir "safety_report.txt"
$oldEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
if (!(Get-Command safety -ErrorAction SilentlyContinue)) { pip install safety -q 2>$null }
if (Get-Command safety -ErrorAction SilentlyContinue) {
    $safetyOut = & safety scan 2>&1; if ($LASTEXITCODE -ne 0) { $safetyOut = & safety check --full-report 2>&1 }
    $safetyOut | Tee-Object -FilePath $safetyProof
} else { "safety not installed" | Out-File $safetyProof }
$ErrorActionPreference = $oldEap
if ($LASTEXITCODE -ne 0) {
    "Safety reported vulnerabilities (report-only; see safety_report.txt). ExitCode=$LASTEXITCODE" | Add-Content $safetyProof
    Write-Host "REPORT-ONLY: vulnerabilities logged to safety_report.txt" -ForegroundColor DarkYellow
} else {
    Write-Host "OK -> $safetyProof" -ForegroundColor Green
}

# black_diff.txt: proof artifact for formatting changes
$blackDiff = Join-Path $logDir "black_diff.txt"
$oldEap = $ErrorActionPreference; $ErrorActionPreference = "Continue"
$diffOut = & black --diff @lintTargets 2>&1; $diffOut | Set-Content -Path $blackDiff
$ErrorActionPreference = $oldEap
# QA required tools (fail-fast on non-zero exit)
Invoke-Step -Name "QA: black --check" -Command { black --check @lintTargets } -ProofPath (Join-Path $logDir "black_report.txt")
Invoke-Step -Name "QA: flake8" -Command { flake8 @lintTargets } -ProofPath (Join-Path $logDir "flake8_report.txt")
# Bandit: report-only (findings in bandit_report.json); -f json -o file avoids Windows UnicodeEncodeError.
$banditJson = Join-Path $logDir "bandit_report.json"
Write-Host "`n[QA: bandit -r core (report-only)]" -ForegroundColor Yellow
$oldEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
bandit -r core -f json -o $banditJson 2>&1
$ErrorActionPreference = $oldEap
"bandit -r core (report-only). ExitCode=$LASTEXITCODE. See bandit_report.json." | Out-File (Join-Path $logDir "bandit_report.txt")
if ($LASTEXITCODE -ne 0) { Write-Host "REPORT-ONLY: findings in bandit_report.json" -ForegroundColor DarkYellow } else { Write-Host "OK -> $banditJson" -ForegroundColor Green }
# Pytest: ignore tests that require optional SmartApi; fail fast on first failure.
Invoke-Step -Name "QA: pytest" -Command {
    pytest --maxfail=1 --disable-warnings -q --ignore=core/engine/test_angelone_api.py --ignore=core/engine/test_angelone_option_chain.py --ignore=scripts --ignore=tests/auto/system3_generated_tests
} -ProofPath (Join-Path $logDir "pytest_report.txt")

Write-Host "`n=== Governance PASS (STRICT) ===" -ForegroundColor Cyan
