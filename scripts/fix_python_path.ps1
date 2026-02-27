# Fix Python PATH Issues
# Ensures Python and pip are accessible from PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fixing Python PATH Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find Python installation
$pythonPath = $null
$pythonExe = Get-Command python -ErrorAction SilentlyContinue
if ($pythonExe) {
    $pythonPath = Split-Path $pythonExe.Source -Parent
    Write-Host "[OK] Found Python at: $pythonPath" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Python not found in PATH" -ForegroundColor Red
    exit 1
}

# Find pip
$pipPath = Join-Path $pythonPath "Scripts\pip.exe"
if (Test-Path $pipPath) {
    Write-Host "[OK] Found pip at: $pipPath" -ForegroundColor Green
} else {
    Write-Host "[WARNING] pip.exe not found at expected location" -ForegroundColor Yellow
}

# Check if Scripts is in PATH
$scriptsPath = Join-Path $pythonPath "Scripts"
$currentPath = $env:PATH -split ';'
$scriptsInPath = $currentPath | Where-Object { $_ -eq $scriptsPath }

if (-not $scriptsInPath) {
    Write-Host "[INFO] Adding Python Scripts to PATH for this session..." -ForegroundColor Yellow
    $env:PATH = "$scriptsPath;$env:PATH"
    Write-Host "[OK] PATH updated (session only)" -ForegroundColor Green
} else {
    Write-Host "[OK] Python Scripts already in PATH" -ForegroundColor Green
}

# Verify pip works
Write-Host ""
Write-Host "Verifying pip..." -ForegroundColor Yellow
$pipVersion = python -m pip --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] pip is accessible: $pipVersion" -ForegroundColor Green
} else {
    Write-Host "[ERROR] pip not accessible" -ForegroundColor Red
    exit 1
}

# Verify Python works
Write-Host ""
Write-Host "Verifying Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Python is accessible: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Python not accessible" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] Python PATH is configured correctly" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: This fix is for the current PowerShell session only."
Write-Host "For permanent fix, add to System Environment Variables:"
Write-Host "  $scriptsPath"
Write-Host ""
