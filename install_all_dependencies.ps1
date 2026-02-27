# System3 Ultra - Complete Dependency Installation Script
# Installs all Python and Node.js dependencies for the entire project

Write-Host "=" * 80
Write-Host "SYSTEM3 ULTRA - COMPLETE DEPENDENCY INSTALLATION"
Write-Host "=" * 80

# Check Python version
Write-Host "`n[1/5] Checking Python installation..."
$pythonVersion = python --version 2>&1
Write-Host "Python: $pythonVersion"

# Upgrade pip, setuptools, wheel
Write-Host "`n[2/5] Upgrading pip, setuptools, wheel..."
python -m pip install --upgrade pip setuptools wheel --quiet

# Install root requirements.txt
Write-Host "`n[3/5] Installing root requirements.txt..."
if (Test-Path "requirements.txt") {
    python -m pip install -r requirements.txt --quiet
    Write-Host "✓ Root requirements installed"
} else {
    Write-Host "⚠ requirements.txt not found"
}

# Install dashboard backend requirements
Write-Host "`n[4/5] Installing dashboard backend requirements..."
if (Test-Path "dashboard\backend\requirements.txt") {
    python -m pip install -r dashboard\backend\requirements.txt --quiet
    Write-Host "✓ Dashboard backend requirements installed"
} else {
    Write-Host "⚠ dashboard\backend\requirements.txt not found"
}

# Install Angel One specific packages (if not already installed)
Write-Host "`n[5/5] Installing Angel One and related packages..."
$angelPackages = @(
    "smartapi-python>=1.5.0",
    "pyotp>=2.9.0",
    "websocket-client>=1.9.0"
)

foreach ($pkg in $angelPackages) {
    Write-Host "  Installing $pkg..."
    python -m pip install $pkg --quiet --upgrade
}

# Install additional commonly needed packages
Write-Host "`nInstalling additional packages..."
$additionalPackages = @(
    "python-multipart>=0.0.6",
    "aiofiles>=23.0.0",
    "httpx>=0.25.0"
)

foreach ($pkg in $additionalPackages) {
    python -m pip install $pkg --quiet --upgrade
}

# Verify critical packages
Write-Host "`n[VERIFY] Verifying critical packages..."
$criticalPackages = @(
    "smartapi-python",
    "pyotp",
    "fastapi",
    "uvicorn",
    "pandas",
    "numpy",
    "pytz",
    "scipy",
    "scikit-learn",
    "torch",
    "tensorboard",
    "requests",
    "python-dotenv",
    "psutil",
    "logzero",
    "websocket-client",
    "joblib",
    "pyarrow",
    "watchdog",
    "pydantic"
)

$missing = @()
foreach ($pkg in $criticalPackages) {
    $result = python -c "import $($pkg.Replace('-', '_')); print('OK')" 2>&1
    if ($result -match "OK") {
        Write-Host "  ✓ $pkg"
    } else {
        Write-Host "  ✗ $pkg (MISSING)"
        $missing += $pkg
    }
}

if ($missing.Count -gt 0) {
    Write-Host "`n⚠ Missing packages detected. Installing..."
    foreach ($pkg in $missing) {
        python -m pip install $pkg --quiet
    }
}

# Frontend dependencies
Write-Host "`n[FRONTEND] Installing frontend dependencies..."
if (Test-Path "dashboard\frontend\package.json") {
    Set-Location dashboard\frontend
    if (Test-Path "node_modules") {
        Write-Host "  node_modules exists, running npm install..."
    } else {
        Write-Host "  Installing npm packages..."
    }
    npm install --silent
    Set-Location ..\..
    Write-Host "✓ Frontend dependencies installed"
} else {
    Write-Host "⚠ dashboard\frontend\package.json not found"
}

# Desktop app dependencies
Write-Host "`n[DESKTOP APP] Installing desktop app dependencies..."
if (Test-Path "desktop_app\package.json") {
    Set-Location desktop_app
    if (Test-Path "node_modules") {
        Write-Host "  node_modules exists, running npm install..."
    } else {
        Write-Host "  Installing npm packages..."
    }
    npm install --silent
    Set-Location ..
    Write-Host "✓ Desktop app dependencies installed"
} else {
    Write-Host "⚠ desktop_app\package.json not found"
}

Write-Host "`n" + "=" * 80
Write-Host "DEPENDENCY INSTALLATION COMPLETE!"
Write-Host "=" * 80
Write-Host "`nNext steps:"
Write-Host "1. Verify backend: python -m pip list | Select-String 'smartapi|fastapi'"
Write-Host "2. Start backend: .\restart_backend.ps1"
Write-Host "3. Build frontend: cd dashboard\frontend; npm run build"
Write-Host "=" * 80
