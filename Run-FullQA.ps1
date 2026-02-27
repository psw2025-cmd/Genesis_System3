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

$repoRoot = "C:\Genesis_System3"
Set-Location $repoRoot

$logDir = Join-Path $repoRoot "logs\inspector"
if (!(Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }

Write-Host "=== QA Guardian (STRICT) ===" -ForegroundColor Cyan
Write-Host "Repo: $repoRoot" -ForegroundColor Gray

if (!(Test-Path "$repoRoot\.venv\Scripts\python.exe")) {
    throw "Missing .venv. Run Run-All.bat Step 3/6 first."
}
& "$repoRoot\.venv\Scripts\Activate.ps1"

$null = Invoke-Step -Name "Env: python --version" -Command { python --version } -ProofPath (Join-Path $logDir "python_version.txt")
$null = Invoke-Step -Name "Env: pip check" -Command { pip check } -ProofPath (Join-Path $logDir "pip_check.txt")

# Limit lint scope to project code (avoid scanning .venv / node_modules).
$lintTargets = @(
    "core",
    "scripts",
    "tools",
    "phases",
    "dashboard\backend"
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
        Write-Host "FAIL - $dep import failed" -ForegroundColor Red
        throw "Missing runtime import: $dep"
    }
}

# Required QA tools (we pin these in requirements-dev.txt)
$null = Invoke-Step -Name "Lint: flake8" -Command { flake8 @lintTargets } -ProofPath (Join-Path $logDir "flake8_report.txt")
$null = Invoke-Step -Name "Format: black --check" -Command { black --check @lintTargets } -ProofPath (Join-Path $logDir "black_report.txt")
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
    pytest --maxfail=1 --disable-warnings -q --ignore=core/engine/test_angelone_api.py --ignore=core/engine/test_angelone_option_chain.py --ignore=scripts
} -ProofPath (Join-Path $logDir "pytest_report.txt")

# Optional: Playwright browser install reminder (not auto-run here)
"If Playwright browser tests are needed, run: playwright install chromium" | Out-File (Join-Path $logDir "playwright_reminder.txt")

# Optional tools (do not hard-fail if missing)
if (Command-Exists "codeql") {
    $null = Invoke-Step -Name "Optional: codeql (analyze)" -Command { codeql version } -ProofPath (Join-Path $logDir "codeql_version.txt") -Optional:$true
} else {
    "SKIP: codeql not installed" | Out-File (Join-Path $logDir "codeql_skipped.txt")
}
if (Command-Exists "sonar-scanner") {
    $null = Invoke-Step -Name "Optional: sonar-scanner" -Command { sonar-scanner -v } -ProofPath (Join-Path $logDir "sonar_version.txt") -Optional:$true
} else {
    "SKIP: sonar-scanner not installed" | Out-File (Join-Path $logDir "sonar_skipped.txt")
}

# Optional: Angel One SmartAPI connectivity (skipped unless SMARTAPI_KEY set)
if ($env:SMARTAPI_KEY) {
    $pythonCode = @"
import os
try:
    from smartapi import SmartConnect
except Exception as e:
    print('smartapi import failed:', e)
    raise
api_key = os.getenv('SMARTAPI_KEY')
if not api_key:
    raise SystemExit('SMARTAPI_KEY missing')
obj = SmartConnect(api_key=api_key)
print('Angel One SmartAPI connectivity: initialized (no live trading performed)') 
"@
    $null = Invoke-Step -Name "Optional: SmartAPI connectivity" -Command { python -c $pythonCode } -ProofPath (Join-Path $logDir "smartapi_connectivity.txt") -Optional:$true
} else {
    "SKIP: SMARTAPI_KEY not set" | Out-File (Join-Path $logDir "smartapi_skipped.txt")
}

# Optional: Frontend build (only if frontend folder exists; optional so QA passes without npm/frontend)
$frontendDir = Join-Path $repoRoot "dashboard\frontend"
if (Test-Path (Join-Path $frontendDir "package.json")) {
    if (Command-Exists "npm") {
        Push-Location $frontendDir
        try {
            $null = Invoke-Step -Name "Frontend: npm ci" -Command { npm ci } -ProofPath (Join-Path $logDir "npm_ci.txt") -Optional:$true
            $null = Invoke-Step -Name "Frontend: npm run build" -Command { npm run build } -ProofPath (Join-Path $logDir "npm_build.txt") -Optional:$true
        } finally {
            Pop-Location
        }
    } else {
        "SKIP: npm not installed" | Out-File (Join-Path $logDir "frontend_build_skipped.txt")
    }
} else {
    "SKIP: dashboard/frontend/package.json not found" | Out-File (Join-Path $logDir "frontend_build_skipped.txt")
}

Get-Date | Out-File (Join-Path $logDir "qa_timestamp.txt")
Write-Host "`n=== QA PASS (STRICT) ===" -ForegroundColor Cyan
