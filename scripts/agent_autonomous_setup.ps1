# =============================================================================
# Agent Autonomous Setup - Genesis_System3
# Run once to enable AI agent to work fully in venv without manual steps.
# =============================================================================

$ErrorActionPreference = "Continue"
$ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$ProjectRoot = Split-Path -Parent $ScriptDir
if (-not (Test-Path $ProjectRoot)) { $ProjectRoot = (Get-Location).Path }
Set-Location $ProjectRoot

$Report = @{
    Done = @()
    Pending = @()
    Failed = @()
}

Write-Host "`n=== Agent Autonomous Setup ===" -ForegroundColor Cyan
Write-Host "Project: $ProjectRoot`n" -ForegroundColor Gray

# -----------------------------------------------------------------------------
# 1. Git credential helper (enables push without manual password)
# -----------------------------------------------------------------------------
try {
    git config --global credential.helper manager 2>$null
    $Report.Done += "Git credential.helper = manager"
} catch { $Report.Failed += "credential.helper: $_" }

# -----------------------------------------------------------------------------
# 2. Git user identity (noreply avoids GH007)
# -----------------------------------------------------------------------------
try {
    git config --global user.name "psw2025-cmd" 2>$null
    git config --global user.email "176781239+psw2025-cmd@users.noreply.github.com" 2>$null
    $Report.Done += "Git user.name + user.email (noreply)"
} catch { $Report.Failed += "user config: $_" }

# -----------------------------------------------------------------------------
# 3. Ensure outputs/ in .gitignore (runtime_state.json, etc.)
# -----------------------------------------------------------------------------
$gitignorePath = Join-Path $ProjectRoot ".gitignore"
$gitignore = Get-Content $gitignorePath -Raw -ErrorAction SilentlyContinue
if ($gitignore -notmatch "outputs/") {
    Add-Content -Path $gitignorePath -Value "`n# Runtime outputs`noutputs/"
    $Report.Done += "Added outputs/ to .gitignore"
} else {
    $Report.Done += ".gitignore already has outputs/"
}

# -----------------------------------------------------------------------------
# 4. Untrack logs/ and outputs/ (force, so no more noisy diffs)
# -----------------------------------------------------------------------------
try {
    git rm -r --cached logs/ -f 2>$null
    git rm -r --cached outputs/ -f 2>$null
    $Report.Done += "Untracked logs/ and outputs/ from Git"
} catch { $Report.Pending += "Untrack logs/outputs (may need manual: git rm -r --cached logs/ -f; git rm -r --cached outputs/ -f)" }

# -----------------------------------------------------------------------------
# 5. Git prune (clean unreachable objects)
# -----------------------------------------------------------------------------
try {
    git prune 2>$null
    $Report.Done += "Ran git prune"
} catch { $Report.Pending += "Optional: run 'git prune'" }

# -----------------------------------------------------------------------------
# 6. Verify venv exists and Python works
# -----------------------------------------------------------------------------
$venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $pyVer = & $venvPython -c "import sys; print(sys.version.split()[0])" 2>$null
    $Report.Done += "Venv OK (Python $pyVer)"
} else {
    $Report.Failed += "Venv not found at .venv\Scripts\python.exe"
}

# -----------------------------------------------------------------------------
# 7. Verify pip/requirements
# -----------------------------------------------------------------------------
if (Test-Path $venvPython) {
    $pipOk = & $venvPython -m pip --version 2>$null
    if ($LASTEXITCODE -eq 0) { $Report.Done += "pip OK" } else { $Report.Failed += "pip check failed" }
}

# -----------------------------------------------------------------------------
# 8. Stage and show status (do not commit automatically - agent can do that)
# -----------------------------------------------------------------------------
git add . 2>$null
$status = git status -sb 2>$null

# -----------------------------------------------------------------------------
# REPORT
# -----------------------------------------------------------------------------
Write-Host "`n--- DONE (no manual action) ---" -ForegroundColor Green
foreach ($item in $Report.Done) { Write-Host "  [OK] $item" -ForegroundColor Green }

if ($Report.Pending.Count -gt 0) {
    Write-Host "`n--- PENDING (optional or one-time) ---" -ForegroundColor Yellow
    foreach ($item in $Report.Pending) { Write-Host "  [~] $item" -ForegroundColor Yellow }
}

if ($Report.Failed.Count -gt 0) {
    Write-Host "`n--- FAILED ---" -ForegroundColor Red
    foreach ($item in $Report.Failed) { Write-Host "  [X] $item" -ForegroundColor Red }
}

Write-Host "`n--- MANUAL (you must do once) ---" -ForegroundColor Magenta
Write-Host "  1. GitHub: https://github.com/settings/emails" -ForegroundColor Magenta
Write-Host "     -> Turn OFF 'Block command line pushes that expose my email'" -ForegroundColor Magenta
Write-Host "  2. Run 'git push' once and sign in when prompted (Credential Manager stores it)" -ForegroundColor Magenta

Write-Host "`n--- Git status ---" -ForegroundColor Gray
Write-Host $status -ForegroundColor Gray

Write-Host "`n--- Agent commands (use venv) ---" -ForegroundColor Cyan
Write-Host "  .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  .venv\Scripts\python.exe -m pytest ..." -ForegroundColor White
Write-Host "  .venv\Scripts\python.exe -m black --check ." -ForegroundColor White
Write-Host "  git add . ; git commit -m '...' ; git push" -ForegroundColor White
Write-Host ""
