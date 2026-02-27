Write-Host "=== Environment Clean Check ===" -ForegroundColor Cyan

# 1. Delete venv if exists
if (Test-Path .\.venv) {
    Remove-Item -Recurse -Force .\.venv
    Write-Host "Deleted old venv" -ForegroundColor Yellow
} else {
    Write-Host "No venv found" -ForegroundColor Green
}

# 2. Remove residual artifacts
Get-ChildItem -Recurse -Include "__pycache__","*.pyc","*.pyo","*.log","*.tmp" | 
    Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "Cleaned residual artifacts" -ForegroundColor Yellow

# 3. Confirm requirements files exist
$reqFiles = Get-ChildItem . -Recurse -Include "requirements*.txt"
if ($reqFiles) {
    Write-Host "Requirements files present:" -ForegroundColor Green
    $reqFiles | ForEach-Object { Write-Host $_.FullName -ForegroundColor Green }
} else {
    Write-Host "FAIL - No requirements files found" -ForegroundColor Red
    exit 1
}

Write-Host "=== Environment Clean ===" -ForegroundColor Cyan
