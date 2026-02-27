# Start Autonomous Trading System
# Runs everything automatically and monitors continuously

Write-Host "========================================" -ForegroundColor Green
Write-Host "  AUTONOMOUS TRADING SYSTEM" -ForegroundColor Green
Write-Host "  Goal: Maximum Profit" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$rootDir = $PSScriptRoot | Split-Path -Parent

# Start Main Trading System
Write-Host "[1/4] Starting Main Trading System..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir'; Write-Host 'MAIN TRADING SYSTEM' -ForegroundColor Green; .\RUN_FULL_SYSTEM_PRODUCTION.bat" -WindowStyle Normal
Start-Sleep -Seconds 5

# Start Backend API
Write-Host "[2/4] Starting Backend API..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir\dashboard\backend'; Write-Host 'BACKEND API SERVER' -ForegroundColor Green; python app.py" -WindowStyle Normal
Start-Sleep -Seconds 3

# Start Dashboard
Write-Host "[3/4] Starting Dashboard..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir\dashboard'; Write-Host 'DASHBOARD SERVER' -ForegroundColor Green; python -m http.server 8080" -WindowStyle Normal
Start-Sleep -Seconds 2

# Start Auto Monitor
Write-Host "[4/4] Starting Auto Monitor..." -ForegroundColor Cyan
if (Test-Path "$rootDir\venv\Scripts\python.exe") {
    $python = "$rootDir\venv\Scripts\python.exe"
} else {
    $python = "python"
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir'; Write-Host 'AUTO MONITOR AND IMPROVE SYSTEM' -ForegroundColor Green; Write-Host 'Monitoring all systems, fixing issues, optimizing for profit...' -ForegroundColor Cyan; Write-Host ''; & '$python' scripts\auto_monitor_and_improve.py" -WindowStyle Normal

Write-Host ""
Write-Host "✅ All systems started!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Dashboard: http://localhost:8080" -ForegroundColor Cyan
Write-Host "🔧 Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 System will run autonomously and optimize for profit!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit (systems will continue running)..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
