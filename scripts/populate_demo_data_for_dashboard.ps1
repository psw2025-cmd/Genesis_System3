# Populate Demo Data for Dashboard Testing (Outside Market Hours)
# Simulates how the dashboard will look during market hours
# Run from repo root: powershell -File scripts\populate_demo_data_for_dashboard.ps1
#
# After running:
#   1. Restart the backend (or it will pick up new files on next request)
#   2. Open http://localhost:3000 and check Chain, Charts, Signals, ML, Model tabs

$ErrorActionPreference = "Stop"
$root = if ($PSScriptRoot) { (Get-Item $PSScriptRoot).Parent.FullName } else { (Get-Location).Path }
Set-Location $root

Write-Host "`n=== Populating Demo Data for Dashboard ===" -ForegroundColor Cyan
Write-Host "This simulates market-hours data so you can test all tabs.`n" -ForegroundColor Gray

# Prefer venv Python if available
$python = "python"
if (Test-Path (Join-Path $root ".venv\Scripts\python.exe")) {
    $python = Join-Path $root ".venv\Scripts\python.exe"
} elseif (Test-Path (Join-Path $root "venv\Scripts\python.exe")) {
    $python = Join-Path $root "venv\Scripts\python.exe"
}

# 1. Chain + Charts + Signals + QC - use existing Python script
Write-Host "[1/4] Generating synthetic chain, signal, QC data..." -ForegroundColor Yellow
& $python scripts\generate_synthetic_live_data.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [WARN] generate_synthetic_live_data.py failed - Chain/Charts may be empty" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] chain_raw_live.csv, top_trade_signal.json, qc_report_live.json created" -ForegroundColor Green
}

# 2. ML tab - create sample ml_performance.json
Write-Host "`n[2/4] Creating sample ML performance data..." -ForegroundColor Yellow
$mlPath = Join-Path $root "outputs\ml_performance.json"
$mlData = @{
    models = @{
        Ensemble = @{
            total_predictions = 150
            total_accuracy = 112.5
            avg_confidence = 0.72
            underlyings = @("NIFTY", "BANKNIFTY", "FINNIFTY")
        }
        XGBoost = @{
            total_predictions = 80
            total_accuracy = 58.4
            avg_confidence = 0.68
            underlyings = @("NIFTY", "BANKNIFTY")
        }
        LightGBM = @{
            total_predictions = 70
            total_accuracy = 52.5
            avg_confidence = 0.65
            underlyings = @("NIFTY", "FINNIFTY")
        }
    }
    predictions = @()
} | ConvertTo-Json -Depth 5
# Fix JSON - PowerShell ConvertTo-Json uses @() for arrays, need proper format
$mlJson = @'
{
  "models": {
    "Ensemble": {
      "total_predictions": 150,
      "total_accuracy": 112.5,
      "avg_confidence": 0.72,
      "underlyings": ["NIFTY", "BANKNIFTY", "FINNIFTY"]
    },
    "XGBoost": {
      "total_predictions": 80,
      "total_accuracy": 58.4,
      "avg_confidence": 0.68,
      "underlyings": ["NIFTY", "BANKNIFTY"]
    },
    "LightGBM": {
      "total_predictions": 70,
      "total_accuracy": 52.5,
      "avg_confidence": 0.65,
      "underlyings": ["NIFTY", "FINNIFTY"]
    }
  },
  "predictions": []
}
'@
[System.IO.File]::WriteAllText($mlPath, $mlJson, [System.Text.UTF8Encoding]::new($false))
Write-Host "  [OK] outputs/ml_performance.json created" -ForegroundColor Green

# 3. Model/Logs tab - create sample log file
Write-Host "`n[3/4] Creating sample log file..." -ForegroundColor Yellow
$logsDir = Join-Path $root "logs"
if (!(Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir -Force | Out-Null }
$logFile = Join-Path $logsDir "dashboard_demo_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$logContent = @"
[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] INFO - Dashboard demo mode started
[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] INFO - Synthetic chain data loaded: 200 contracts
[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] INFO - QC status: PASS
[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] INFO - Signal: NO_TRADE (market closed - demo data)
[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] INFO - ML models: Ensemble, XGBoost, LightGBM
[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] INFO - Backend API ready on port 8000
"@
[System.IO.File]::WriteAllText($logFile, $logContent, [System.Text.UTF8Encoding]::new($false))
Write-Host "  [OK] $logFile created" -ForegroundColor Green

# 4. Ensure chain CSV has correct columns for charts (spot_price, underlying)
Write-Host "`n[4/4] Verifying data files..." -ForegroundColor Yellow
$chainFile = Join-Path $root "outputs\chain_raw_live.csv"
if (Test-Path $chainFile) {
    $lineCount = (Get-Content $chainFile | Measure-Object -Line).Lines
    Write-Host "  [OK] chain_raw_live.csv has $lineCount lines" -ForegroundColor Green
} else {
    Write-Host "  [WARN] chain_raw_live.csv not found" -ForegroundColor Yellow
}

Write-Host "`n=== Demo Data Ready ===" -ForegroundColor Cyan
Write-Host @"

Next steps:
  1. If backend is running, refresh the dashboard (http://localhost:3000)
  2. If not, run: START_FULL_DASHBOARD_SYSTEM.bat
  3. Check these tabs:
     - Chain: Should show option chain with contracts
     - Charts: Should show heatmap, IV surface, Greeks, PCR
     - Signals: Should show signal (TRADE or NO_TRADE)
     - ML: Should show model comparison (Ensemble, XGBoost, LightGBM)
     - Model: Should show log lines in Runtime Logs

Alternative (API-level synthetic, no files):
  Set env: SYSTEM3_REAL_ONLY=0
  Restart backend - Chain/Signals/QC will return synthetic data when market closed.
  (Charts use chain data; ML/Logs still need files above.)

"@ -ForegroundColor Gray
