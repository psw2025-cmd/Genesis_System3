$ErrorActionPreference = "Stop"

function Command-Exists {
    param([Parameter(Mandatory=$true)][string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-Step {
    param(
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$true)][scriptblock]$Command,
        [Parameter(Mandatory=$true)][string]$ProofPath,
        [bool]$Optional = $false
    )
    Write-Host "`n[$Name]" -ForegroundColor Yellow
    $started = Get-Date
    try {
        # Always restore ErrorActionPreference, even on failure or exceptions.
        $oldEap = $ErrorActionPreference
        try {
            # Avoid treating native stderr output as a terminating PowerShell error.
            $ErrorActionPreference = "Continue"
            & $Command 2>&1 | Tee-Object -FilePath $ProofPath
            $exit = $LASTEXITCODE
        } finally {
            $ErrorActionPreference = $oldEap
        }

        if ($exit -ne 0) { throw "ExitCode=$exit" }
        $elapsed = (Get-Date) - $started
        Write-Host "OK ($($elapsed.TotalSeconds)s) -> $ProofPath" -ForegroundColor Green
        return $true
    } catch {
        $elapsed = (Get-Date) - $started
        if ($Optional) {
            Write-Host "SKIP/FAIL-OPTIONAL ($($elapsed.TotalSeconds)s) -> $ProofPath" -ForegroundColor DarkYellow
            return $false
        }
        Write-Host "FAIL ($($elapsed.TotalSeconds)s) -> $ProofPath" -ForegroundColor Red
        throw
    }
}

function Get-RepoRoot {
    if ($env:GITHUB_WORKSPACE -and (Test-Path $env:GITHUB_WORKSPACE)) {
        return (Resolve-Path $env:GITHUB_WORKSPACE).Path
    }
    if ($PSScriptRoot -and (Test-Path $PSScriptRoot)) {
        return (Resolve-Path $PSScriptRoot).Path
    }
    return (Get-Location).Path
}

$repoRoot = Get-RepoRoot
Set-Location $repoRoot

$logDir = Join-Path $repoRoot "logs\inspector"
if (!(Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

Write-Host "=== QA Guardian (STRICT) ===" -ForegroundColor Cyan
Write-Host "Repo: $repoRoot" -ForegroundColor Gray

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$venvActivate = Join-Path $repoRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $venvPython) {
    if (Test-Path $venvActivate) { & $venvActivate }
} else {
    Write-Host "REPORT-ONLY: .venv not found. Using current GitHub Actions Python/runtime." -ForegroundColor DarkYellow
}

$null = Invoke-Step -Name "Env: python --version" -Command { python --version } -ProofPath (Join-Path $logDir "python_version.txt")
$null = Invoke-Step -Name "Env: pip check" -Command { pip check } -ProofPath (Join-Path $logDir "pip_check.txt") -Optional $true

# Limit lint scope to project code (avoid scanning .venv / node_modules).
$lintTargets = @(
    "core",
    "scripts",
    "tools",
    "phases",
    "dashboard"
) | Where-Object { Test-Path (Join-Path $repoRoot $_) }

# Runtime import sanity (only what we actually require)
$runtimeImports = @("lightgbm","xgboost","tensorflow","torch","sklearn","plotly","altair","dash","streamlit")
$importProof = Join-Path $logDir "runtime_imports.txt"
Write-Host "`n[Runtime: imports]" -ForegroundColor Yellow
"" | Out-File $importProof
foreach ($dep in $runtimeImports) {
    $oldEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    python -c "import $dep" 2>$null
    $exit = $LASTEXITCODE
    $ErrorActionPreference = $oldEap
    if ($exit -eq 0) {
        "OK - $dep" | Add-Content $importProof
        Write-Host "OK - $dep" -ForegroundColor Green
    } else {
        $oldEap2 = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        $err = (python -c "import importlib,sys; importlib.import_module(sys.argv[1])" $dep 2>&1 | Out-String).Trim()
        $ErrorActionPreference = $oldEap2
        "FAIL - $dep :: $err" | Add-Content $importProof
        Write-Host "REPORT-ONLY: $dep import failed" -ForegroundColor DarkYellow
    }
}

# Required QA tools. Keep legacy QA report-only while architecture/trading safety gate remains blocking.
$null = Invoke-Step -Name "Lint: flake8" -Command { flake8 @lintTargets } -ProofPath (Join-Path $logDir "flake8_report.txt") -Optional $true
$null = Invoke-Step -Name "Format: black --check" -Command { black --check @lintTargets } -ProofPath (Join-Path $logDir "black_report.txt") -Optional $true
# Bandit: report-only (findings in bandit_report.json).
$banditJson = Join-Path $logDir "bandit_report.json"
Write-Host "`n[Security: bandit -r core (report-only)]" -ForegroundColor Yellow
$oldEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
bandit -r core -f json -o $banditJson 2>&1
$ErrorActionPreference = $oldEap
"bandit (report-only). ExitCode=$LASTEXITCODE. See bandit_report.json." | Out-File (Join-Path $logDir "bandit_report.txt")
if ($LASTEXITCODE -ne 0) { Write-Host "REPORT-ONLY: findings in bandit_report.json" -ForegroundColor DarkYellow } else { Write-Host "OK -> $banditJson" -ForegroundColor Green }
# Safety: report-only (vulns logged to safety_report.txt).
Write-Host "`n[Security: safety (report-only)]" -ForegroundColor Yellow
$safetyProof = Join-Path $logDir "safety_report.txt"
$oldEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
safety check --full-report 2>&1 | Tee-Object -FilePath $safetyProof
$ErrorActionPreference = $oldEap
if ($LASTEXITCODE -ne 0) {
    "Safety reported vulnerabilities (report-only). ExitCode=$LASTEXITCODE" | Add-Content $safetyProof
    Write-Host "REPORT-ONLY: vulnerabilities logged to safety_report.txt" -ForegroundColor DarkYellow
} else {
    Write-Host "OK -> $safetyProof" -ForegroundColor Green
}
# pip-audit: report-only (vulns logged to pip_audit.json; see docs/FULL_ACTION_PLAN_AND_CHECKLIST.md)
Write-Host "`n[Security: pip-audit (report-only)]" -ForegroundColor Yellow
$pipAuditOut = Join-Path $logDir "pip_audit_stdout.txt"
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
$null = Invoke-Step -Name "Tests: pytest" -Command {
    pytest --maxfail=1 --disable-warnings -q --ignore=core/engine/test_angelone_api.py --ignore=core/engine/test_angelone_option_chain.py --ignore=scripts --ignore=tests/auto/system3_generated_tests
} -ProofPath (Join-Path $logDir "pytest_report.txt") -Optional $true

# Optional: Playwright browser install reminder (not auto-run here)
"If Playwright browser tests are needed, run: playwright install chromium" | Out-File (Join-Path $logDir "playwright_reminder.txt")
Write-Host "`nREPORT-ONLY FullQA completed. Blocking gate remains architecture/trading safety." -ForegroundColor Cyan
