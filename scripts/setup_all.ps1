# System3 Ultra - Complete Environment Setup
# Installs all dependencies and validates environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "System3 Ultra - Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Node.js not found!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green

# Install Python dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
Set-Location dashboard\backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python dependencies installed" -ForegroundColor Green
Set-Location ..\..

# Install Node.js dependencies
Write-Host ""
Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
Set-Location dashboard\frontend
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Node.js dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Node.js dependencies installed" -ForegroundColor Green
Set-Location ..\..

# Install Electron dependencies
Write-Host ""
Write-Host "Installing Electron dependencies..." -ForegroundColor Yellow
Set-Location desktop_app
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Electron dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Electron dependencies installed" -ForegroundColor Green
Set-Location ..

# Build frontend
Write-Host ""
Write-Host "Building frontend..." -ForegroundColor Yellow
Set-Location dashboard\frontend
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build frontend" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Frontend built" -ForegroundColor Green
Set-Location ..\..

# Add upgrade agent endpoints
Write-Host ""
Write-Host "Adding upgrade agent endpoints..." -ForegroundColor Yellow
python scripts\add_upgrade_agent_endpoints.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Failed to add upgrade agent endpoints" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Run: npm run build:win (in desktop_app folder)"
Write-Host "  2. Or run: npm start (in desktop_app folder) for development"
Write-Host ""
