# =============================================================================
# Agent Finish Setup - Complete what's left after agent_autonomous_setup.ps1
# Run this to commit setup changes and show exactly what YOU must do manually.
# =============================================================================

$ErrorActionPreference = "Continue"
$ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "`n=== Agent Finish Setup ===" -ForegroundColor Cyan
Write-Host "Project: $ProjectRoot`n" -ForegroundColor Gray

# -----------------------------------------------------------------------------
# 1. Commit setup changes (agent setup files + untrack logs/outputs)
# -----------------------------------------------------------------------------
$hasChanges = git status --porcelain 2>$null
if ($hasChanges) {
    git add .
    git commit -m "Agent autonomous setup: ignore logs/outputs, add setup scripts" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Committed setup changes" -ForegroundColor Green
    } else {
        Write-Host "[~] Commit skipped (maybe nothing to commit)" -ForegroundColor Yellow
    }
} else {
    Write-Host "[OK] No uncommitted changes" -ForegroundColor Green
}

# -----------------------------------------------------------------------------
# 2. Show what YOU must do (cannot be automated)
# -----------------------------------------------------------------------------
Write-Host "`n" + ("="*60) -ForegroundColor Magenta
Write-Host "  WHAT YOU MUST DO (2 steps, one-time)" -ForegroundColor Magenta
Write-Host ("="*60) -ForegroundColor Magenta

Write-Host "`n  STEP 1 - GitHub email (prevents GH007):" -ForegroundColor White
Write-Host "    1. Open: https://github.com/settings/emails" -ForegroundColor Gray
Write-Host "    2. Find: 'Block command line pushes that expose my email'" -ForegroundColor Gray
Write-Host "    3. Turn it OFF (uncheck)" -ForegroundColor Gray

Write-Host "`n  STEP 2 - First push (stores credentials):" -ForegroundColor White
Write-Host "    Run this in your terminal:" -ForegroundColor Gray
Write-Host "      git push" -ForegroundColor Cyan
Write-Host "    Sign in when prompted (browser or dialog)" -ForegroundColor Gray
Write-Host "    After this, agent can push without you" -ForegroundColor Gray

Write-Host "`n" + ("="*60) -ForegroundColor Magenta
Write-Host "  After both steps: Agent can work fully autonomously." -ForegroundColor Green
Write-Host ("="*60) + "`n" -ForegroundColor Magenta
