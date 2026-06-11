# Fix Pandas Installation - Use Pre-built Wheels
# This script fixes the pandas compilation error by using pre-built wheels

Write-Host "=== FIXING PANDAS INSTALLATION ===" -ForegroundColor Yellow
Write-Host ""

# Step 1: Upgrade pip, setuptools, and wheel to ensure we can use wheels
Write-Host "Step 1: Upgrading pip, setuptools, and wheel..." -ForegroundColor Cyan
& ".\venv\Scripts\pip.exe" install --upgrade --no-cache-dir pip setuptools wheel
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Warning: pip upgrade had issues, continuing..." -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Remove any broken pandas and numpy installations
Write-Host "Step 2: Cleaning up broken pandas and numpy installations..." -ForegroundColor Cyan
Remove-Item -Recurse -Force ".\venv\Lib\site-packages\pandas" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force ".\venv\Lib\site-packages\numpy" -ErrorAction SilentlyContinue
Get-ChildItem ".\venv\Lib\site-packages" -Filter "pandas-*.dist-info" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem ".\venv\Lib\site-packages" -Filter "numpy-*.dist-info" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem ".\venv\Lib\site-packages" -Filter "pandas-*.egg-info" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem ".\venv\Lib\site-packages" -Filter "numpy-*.egg-info" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "  Cleaned up pandas and numpy remnants" -ForegroundColor Green

Write-Host ""

# Step 3: Install numpy first (required dependency)
Write-Host "Step 3a: Installing numpy first..." -ForegroundColor Cyan
& ".\venv\Scripts\pip.exe" install --force-reinstall --no-deps --no-cache-dir numpy 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Warning: numpy installation had issues, continuing..." -ForegroundColor Yellow
}

Write-Host ""

# Step 3b: Install pandas using ONLY pre-built wheels (no compilation)
Write-Host "Step 3b: Installing pandas using pre-built wheels (no compilation)..." -ForegroundColor Cyan
Write-Host "  This may take a few minutes..." -ForegroundColor Gray

# Install pandas with --prefer-binary to use wheels when available
& ".\venv\Scripts\pip.exe" install --prefer-binary --no-cache-dir pandas 2>&1 | Tee-Object -Variable pipOutput

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  Attempt 1 failed, trying with force reinstall..." -ForegroundColor Yellow
    
    # Try with force reinstall
    & ".\venv\Scripts\pip.exe" install --force-reinstall --prefer-binary --no-cache-dir pandas 2>&1 | Tee-Object -Variable pipOutput
}

Write-Host ""

# Step 4: Verify installation
Write-Host "Step 4: Verifying pandas installation..." -ForegroundColor Cyan
$pythonExe = ".\venv\Scripts\python.exe"
$testScript = @"
import sys
try:
    import pandas as pd
    print('SUCCESS: pandas ' + pd.__version__ + ' installed')
    print('pandas.__file__: ' + str(pd.__file__))
    print('Has DataFrame: ' + str(hasattr(pd, 'DataFrame')))
    sys.exit(0)
except Exception as e:
    print('FAILED: ' + str(e))
    sys.exit(1)
"@

$testScript | & $pythonExe
$verifyResult = $LASTEXITCODE

Write-Host ""

if ($verifyResult -eq 0) {
    Write-Host "=== SUCCESS ===" -ForegroundColor Green
    Write-Host "Pandas has been successfully installed using pre-built wheels." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Run your main script again" -ForegroundColor White
    Write-Host "  2. If you still see errors, check that venv is activated" -ForegroundColor White
} else {
    Write-Host "=== FAILED ===" -ForegroundColor Red
    Write-Host "Pandas installation verification failed." -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Ensure you have internet connection" -ForegroundColor White
    Write-Host "  2. Check if antivirus is blocking pip" -ForegroundColor White
    Write-Host "  3. Try running: .\venv\Scripts\pip.exe install --upgrade pip" -ForegroundColor White
    Write-Host "  4. Consider recreating the venv if issues persist" -ForegroundColor White
}

Write-Host ""
