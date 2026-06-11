# Run System3 autorun master with venv enforced
# Usage: powershell -ExecutionPolicy Bypass -File .\run_autorun_master.ps1

$venv = "C:\\Genesis_System3\\venv\\Scripts\\Activate.ps1"
if (-not (Test-Path $venv)) {
    Write-Host "[ERROR] venv not found at $venv" -ForegroundColor Red
    exit 1
}

& $venv
if (-not $env:VIRTUAL_ENV) {
    Write-Host "[ERROR] Failed to activate venv" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] venv activated: $env:VIRTUAL_ENV" -ForegroundColor Green
python system3_autorun_master.py
