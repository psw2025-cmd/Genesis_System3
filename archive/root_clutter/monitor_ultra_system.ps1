# System3 Ultra: Daily Monitoring Script
# Run this script daily to check system status
# 
# TO RUN THIS SCRIPT:
# Option 1: Double-click monitor_ultra_system.bat (recommended)
# Option 2: powershell -ExecutionPolicy Bypass -File .\monitor_ultra_system.ps1
# Option 3: In PowerShell: .\monitor_ultra_system.ps1 (if execution policy allows)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SYSTEM3 ULTRA: DAILY MONITORING CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "[WARN] Virtual environment not activated. Activating..." -ForegroundColor Yellow
    if (Test-Path "C:\Genesis_System3\venv\Scripts\Activate.ps1") {
        & "C:\Genesis_System3\venv\Scripts\Activate.ps1"
    } else {
        Write-Host "[ERROR] Virtual environment not found at C:\Genesis_System3\venv" -ForegroundColor Red
        Write-Host "[INFO] Please activate venv manually: venv\Scripts\activate" -ForegroundColor Yellow
    }
}

# 1. Policy & Risk Monitor
Write-Host "[1/4] Running Policy & Risk Monitor..." -ForegroundColor Green
python -m core.engine.system3_phase37_policy_risk_monitor
Write-Host ""

# 2. Decision Auditor
Write-Host "[2/4] Running Decision Auditor..." -ForegroundColor Green
python -m core.engine.system3_phase35_ultra_auditor
Write-Host ""

# 3. Governance Summary
Write-Host "[3/4] Running Governance Summary..." -ForegroundColor Green
python -m core.engine.system3_phase38_governance_summary
Write-Host ""

# 4. Check Shadow Trades
Write-Host "[4/4] Checking Shadow Trades..." -ForegroundColor Green
$shadowFile = "storage\live\angel_index_ai_ultra_trades_shadow.csv"
if (Test-Path $shadowFile) {
    $shadowCount = (Get-Content $shadowFile | Measure-Object -Line).Lines - 1
    if ($shadowCount -gt 0) {
        Write-Host "[INFO] Shadow trades found: $shadowCount" -ForegroundColor Green
        Write-Host "[INFO] Review: type $shadowFile | Select-Object -First 10" -ForegroundColor Yellow
    } else {
        Write-Host "[INFO] No shadow trades yet (expected with conservative signals)" -ForegroundColor Yellow
    }
} else {
    Write-Host "[INFO] Shadow trades file not created yet" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "MONITORING CHECK COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Review outputs:" -ForegroundColor Yellow
Write-Host "  - Policy Dashboard: storage\ultra\phase37_policy_risk_dashboard.md" -ForegroundColor White
Write-Host "  - Audit Report: storage\ultra\phase35_decision_audit_report.md" -ForegroundColor White
Write-Host "  - Governance Summary: storage\ultra\phase38_governance_summary.md" -ForegroundColor White
Write-Host ""

