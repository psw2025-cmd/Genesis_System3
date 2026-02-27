# Run pre-build check and then build fresh installer.
# Usage: .\run_build.ps1
# Do NOT paste script output into the terminal - run this file.

Set-Location $PSScriptRoot

Write-Host "Step 1: Checking requirements..." -ForegroundColor Cyan
python check_build_requirements.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Fix [FAIL] items above, then run again." -ForegroundColor Red
    exit 1
}

Write-Host "`nStep 2: Running build_fresh_installer.bat..." -ForegroundColor Cyan
cmd /c "build_fresh_installer.bat"
exit $LASTEXITCODE
