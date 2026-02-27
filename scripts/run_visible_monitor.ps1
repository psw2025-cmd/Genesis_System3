# Run Visible Monitor in Current Terminal
# Shows continuous activity and progress

Write-Host "========================================" -ForegroundColor Green
Write-Host "  VISIBLE AUTO MONITOR" -ForegroundColor Green
Write-Host "  Goal: Maximum Profit" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Starting visible monitor..." -ForegroundColor Cyan
Write-Host "You will see continuous updates every 10 seconds!" -ForegroundColor Yellow
Write-Host ""

$rootDir = $PSScriptRoot | Split-Path -Parent

if (Test-Path "$rootDir\venv\Scripts\python.exe") {
    $python = "$rootDir\venv\Scripts\python.exe"
} else {
    $python = "python"
}

& $python "$rootDir\scripts\visible_auto_monitor.py"
