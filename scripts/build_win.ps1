# Build System3 Ultra Desktop App for Windows
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building System3 Ultra Desktop App" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ensure frontend is built
Write-Host "Building frontend..." -ForegroundColor Yellow
Set-Location dashboard\frontend
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Frontend build failed" -ForegroundColor Red
    exit 1
}
Set-Location ..\..

# Build Electron app
Write-Host ""
Write-Host "Building Electron app..." -ForegroundColor Yellow
Set-Location desktop_app
npm run build:win
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Electron build failed" -ForegroundColor Red
    exit 1
}
Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "EXE file location: desktop_app\dist\"
Write-Host ""
