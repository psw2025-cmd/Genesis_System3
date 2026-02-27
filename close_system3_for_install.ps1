# Close System3 Ultra Processes for Installation
# This script closes all System3 Ultra and Electron processes so installation can proceed

Write-Host "=== CLOSING SYSTEM3 ULTRA PROCESSES ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Close System3 Ultra processes
Write-Host "[1/3] Closing System3 Ultra processes..." -ForegroundColor Yellow
$processes = Get-Process | Where-Object { 
    $_.ProcessName -like "*System3*" -or 
    $_.ProcessName -like "*electron*" -or
    $_.MainWindowTitle -like "*System3*"
}

if ($processes) {
    foreach ($proc in $processes) {
        Write-Host "  Closing: $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor Gray
        try {
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            Write-Host "    [OK] Closed" -ForegroundColor Green
        } catch {
            Write-Host "    [WARN] Could not close $($proc.ProcessName)" -ForegroundColor Yellow
        }
    }
    Start-Sleep -Seconds 2
    Write-Host "  [OK] All processes closed" -ForegroundColor Green
} else {
    Write-Host "  [OK] No System3 processes running" -ForegroundColor Green
}

# Step 2: Close Python processes on port 8000 (backend)
Write-Host ""
Write-Host "[2/3] Closing backend processes on port 8000..." -ForegroundColor Yellow
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    $portPid = $port8000.OwningProcess
    Write-Host "  Closing process on port 8000 (PID: $portPid)" -ForegroundColor Gray
    try {
        Stop-Process -Id $portPid -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
        Write-Host "  [OK] Port 8000 cleared" -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] Could not close process on port 8000" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [OK] Port 8000 is free" -ForegroundColor Green
}

# Step 3: Verify all processes are closed
Write-Host ""
Write-Host "[3/3] Verifying all processes are closed..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

$stillRunning = Get-Process | Where-Object { 
    $_.ProcessName -like "*System3*" -or 
    $_.ProcessName -like "*electron*"
}

if ($stillRunning) {
    Write-Host "  [WARN] Some processes may still be running:" -ForegroundColor Yellow
    foreach ($proc in $stillRunning) {
        Write-Host "    - $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "  You may need to manually close these processes" -ForegroundColor Yellow
    Write-Host "  Or run this script again with administrator privileges" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] All processes closed successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== READY FOR INSTALLATION ===" -ForegroundColor Cyan
Write-Host "You can now click 'Retry' in the installer dialog" -ForegroundColor Green
Write-Host ""
