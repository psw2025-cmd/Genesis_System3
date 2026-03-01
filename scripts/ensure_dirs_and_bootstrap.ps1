# Ensure required directories exist and create bootstrap files for cold start
# Run from repo root: powershell -File scripts\ensure_dirs_and_bootstrap.ps1
$root = if ($PSScriptRoot) { (Get-Item $PSScriptRoot).Parent.FullName } else { (Get-Location).Path }
$dirs = @(
    "outputs",
    "outputs/audit",
    "outputs/db",
    "outputs/state_snapshots",
    "outputs/validation",
    "logs",
    "logs/inspector",
    "config",
    "storage",
    "storage/live",
    "storage/learning",
    "storage/config"
)
foreach ($d in $dirs) {
    $p = Join-Path $root $d
    if (!(Test-Path $p)) {
        New-Item -ItemType Directory -Path $p -Force | Out-Null
        Write-Host "Created: $d"
    }
}
# Bootstrap health.json when missing (allows dashboard to start before trading system)
# Use UTF-8 without BOM so Python json.loads() works (PowerShell Set-Content adds BOM)
$healthPath = Join-Path $root "outputs\health.json"
if (!(Test-Path $healthPath)) {
    $bootstrap = @{
        is_connected = $false
        broker_status = "disconnected"
        data_source = "not_ready"
        mode = "PAPER"
        qc_status = "PASS"
        qc_failures = @()
        timestamp = (Get-Date).ToString("o")
    }
    $json = $bootstrap | ConvertTo-Json
    [System.IO.File]::WriteAllText($healthPath, $json, [System.Text.UTF8Encoding]::new($false))
    Write-Host "Created bootstrap: outputs/health.json"
}
# Bootstrap positions_live.json when missing
$posPath = Join-Path $root "outputs\positions_live.json"
if (!(Test-Path $posPath)) {
    [System.IO.File]::WriteAllText($posPath, '{"positions":[],"timestamp":""}', [System.Text.UTF8Encoding]::new($false))
    Write-Host "Created bootstrap: outputs/positions_live.json"
}
# Bootstrap ml_performance.json when missing (ML tab - seed models for cold start)
$mlPath = Join-Path $root "outputs\ml_performance.json"
if (!(Test-Path $mlPath)) {
    $mlBootstrap = '{"models":{"Ensemble":{"total_predictions":0,"total_accuracy":0.0,"avg_confidence":0.0,"underlyings":[]},"Fallback":{"total_predictions":0,"total_accuracy":0.0,"avg_confidence":0.0,"underlyings":[]}},"predictions":[]}'
    [System.IO.File]::WriteAllText($mlPath, $mlBootstrap, [System.Text.UTF8Encoding]::new($false))
    Write-Host "Created bootstrap: outputs/ml_performance.json"
}
# Bootstrap paper_pnl_summary.json when missing (PnL API primary source)
$pnlPath = Join-Path $root "outputs\paper_pnl_summary.json"
if (!(Test-Path $pnlPath)) {
    $pnlBootstrap = '{"total_pnl":0.0,"total_realized_pnl":0.0,"total_unrealized_pnl":0.0,"open_positions":0,"total_trades":0,"win_rate":0.0,"timestamp_ist":""}'
    [System.IO.File]::WriteAllText($pnlPath, $pnlBootstrap, [System.Text.UTF8Encoding]::new($false))
    Write-Host "Created bootstrap: outputs/paper_pnl_summary.json"
}
Write-Host "Bootstrap complete."
