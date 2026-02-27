# Dashboard Data Monitor - Runs every 5 minutes
# Validates data quality and fixes issues automatically

$ErrorActionPreference = "Continue"
$ROOT_DIR = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$VENV_DIR = Join-Path $ROOT_DIR "venv"
$OUTPUTS_DIR = Join-Path $ROOT_DIR "outputs"

Write-Host "Dashboard Monitor Started - Checking every 5 minutes" -ForegroundColor Cyan

while ($true) {
    try {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "`n[$timestamp] Running data validation..." -ForegroundColor Yellow
        
        # Run data validation
        $validatorScript = Join-Path $ROOT_DIR "scripts\dashboard_data_validator.py"
        if (Test-Path $validatorScript) {
            $validationOutput = & "$VENV_DIR\Scripts\python.exe" $validatorScript 2>&1
            
            # Check for critical issues
            $validationDir = Join-Path $OUTPUTS_DIR "validation"
            $latestReport = Get-ChildItem $validationDir -Filter "dashboard_validation_*.json" -ErrorAction SilentlyContinue | 
                Sort-Object LastWriteTime -Descending | Select-Object -First 1
            
            if ($latestReport) {
                $report = Get-Content $latestReport.FullName | ConvertFrom-Json
                $criticalIssues = $report.critical_issues
                
                if ($criticalIssues -gt 0) {
                    Write-Host "  [ALERT] $criticalIssues critical issues found!" -ForegroundColor Red
                    Write-Host "  Running auto-fix..." -ForegroundColor Yellow
                    
                    # Run fix script
                    $fixScript = Join-Path $ROOT_DIR "scripts\fix_dashboard_data_issues.py"
                    if (Test-Path $fixScript) {
                        & "$VENV_DIR\Scripts\python.exe" $fixScript 2>&1 | Out-Null
                        Write-Host "  [OK] Auto-fix completed" -ForegroundColor Green
                    }
                } else {
                    Write-Host "  [OK] No critical issues" -ForegroundColor Green
                }
            }
        }
        
        # Check backend health
        try {
            $health = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
            if ($health.StatusCode -eq 200) {
                Write-Host "  [OK] Backend healthy" -ForegroundColor Green
            }
        } catch {
            Write-Host "  [WARN] Backend not responding" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "  [ERROR] Monitor error: $_" -ForegroundColor Red
    }
    
    # Wait 5 minutes
    Start-Sleep -Seconds 300
}
