# PowerShell-safe output checker
# Usage: .\tools\check_outputs.ps1

$outputsDir = "outputs"

Write-Host "=== OUTPUTS CHECK ===" -ForegroundColor Cyan
Write-Host ""

if (Test-Path $outputsDir) {
    Write-Host "Outputs directory exists: YES" -ForegroundColor Green
    
    $files = @(
        "health.json",
        "paper_pnl_summary.json",
        "chain_raw_live.csv",
        "perf_metrics.json"
    )
    
    foreach ($file in $files) {
        $path = Join-Path $outputsDir $file
        if (Test-Path $path) {
            $info = Get-Item $path
            Write-Host "  $file : EXISTS (Last modified: $($info.LastWriteTime))" -ForegroundColor Green
        } else {
            Write-Host "  $file : MISSING" -ForegroundColor Red
        }
    }
} else {
    Write-Host "Outputs directory missing!" -ForegroundColor Red
}
