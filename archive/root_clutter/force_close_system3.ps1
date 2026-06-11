# Force Close System3 Ultra for Installation
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "FORCE CLOSING SYSTEM3 ULTRA" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Close System3 Ultra.exe
Write-Host "Closing System3 Ultra.exe..." -ForegroundColor Yellow
$processes = Get-Process -Name "System3 Ultra" -ErrorAction SilentlyContinue
if ($processes) {
    $processes | ForEach-Object {
        Write-Host "  Killing process: $($_.Id) - $($_.ProcessName)" -ForegroundColor Yellow
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] System3 Ultra.exe closed" -ForegroundColor Green
} else {
    Write-Host "[INFO] No System3 Ultra.exe process found" -ForegroundColor Gray
}

# Close any Electron processes
Write-Host ""
Write-Host "Closing Electron processes..." -ForegroundColor Yellow
$electron = Get-Process -Name "electron" -ErrorAction SilentlyContinue
if ($electron) {
    $electron | ForEach-Object {
        Write-Host "  Killing Electron process: $($_.Id)" -ForegroundColor Yellow
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] Electron processes closed" -ForegroundColor Green
}

# Close Python processes on port 8000
Write-Host ""
Write-Host "Closing Python backend on port 8000..." -ForegroundColor Yellow
$connections = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($connections) {
    $connections | ForEach-Object {
        $pid = $_.OwningProcess
        Write-Host "  Killing process $pid on port 8000..." -ForegroundColor Yellow
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] Port 8000 processes closed" -ForegroundColor Green
} else {
    Write-Host "[INFO] Port 8000 is free" -ForegroundColor Gray
}

# Close any uvicorn processes
Write-Host ""
Write-Host "Closing uvicorn processes..." -ForegroundColor Yellow
Get-Process python* -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*" -or $_.Path -like "*uvicorn*"
} | ForEach-Object {
    Write-Host "  Killing Python process: $($_.Id)" -ForegroundColor Yellow
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Waiting 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Verification
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "VERIFICATION" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$stillRunning = Get-Process -Name "System3 Ultra" -ErrorAction SilentlyContinue
if ($stillRunning) {
    Write-Host "[WARNING] System3 Ultra.exe is still running!" -ForegroundColor Red
    Write-Host "  Process IDs: $($stillRunning.Id -join ', ')" -ForegroundColor Red
    Write-Host "  Please close manually from Task Manager" -ForegroundColor Yellow
} else {
    Write-Host "[OK] System3 Ultra.exe is not running" -ForegroundColor Green
}

$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    Write-Host "[WARNING] Port 8000 is still in use!" -ForegroundColor Red
    Write-Host "  Process ID: $($port8000.OwningProcess)" -ForegroundColor Red
} else {
    Write-Host "[OK] Port 8000 is free" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "READY FOR INSTALLATION" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now run the installer:" -ForegroundColor Green
Write-Host "  desktop_app\dist\System3 Ultra Setup 1.0.0.exe" -ForegroundColor White
Write-Host ""
