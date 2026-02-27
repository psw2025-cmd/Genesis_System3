# Clean and Build Script
# Closes all System3/Electron processes and cleans dist directory before building

Write-Host "=== CLEANING AND PREPARING FOR BUILD ===" -ForegroundColor Cyan

# Step 1: Close all System3 Ultra processes
Write-Host "`n[1/4] Closing all System3 Ultra processes..." -ForegroundColor Yellow
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
        } catch {
            Write-Host "  Warning: Could not close $($proc.ProcessName)" -ForegroundColor Yellow
        }
    }
    Start-Sleep -Seconds 2
    Write-Host "  [OK] Processes closed" -ForegroundColor Green
} else {
    Write-Host "  [OK] No System3 processes running" -ForegroundColor Green
}

# Step 2: Close Python processes on port 8000 (backend)
Write-Host "`n[2/4] Checking for backend processes on port 8000..." -ForegroundColor Yellow
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    $portPid = $port8000.OwningProcess
    Write-Host "  Closing process on port 8000 (PID: $portPid)" -ForegroundColor Gray
    try {
        Stop-Process -Id $portPid -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    } catch {
        Write-Host "  Warning: Could not close process on port 8000" -ForegroundColor Yellow
    }
    Write-Host "  [OK] Port 8000 cleared" -ForegroundColor Green
} else {
    Write-Host "  [OK] Port 8000 is free" -ForegroundColor Green
}

# Step 3: Clean dist directory
Write-Host "`n[3/4] Cleaning dist directory..." -ForegroundColor Yellow
$distDir = "C:\Genesis_System3\desktop_app\dist"
if (Test-Path $distDir) {
    Write-Host "  Removing: $distDir" -ForegroundColor Gray
    try {
        # Try to remove with retries
        $maxRetries = 5
        $retryCount = 0
        $removed = $false
        
        while ($retryCount -lt $maxRetries -and -not $removed) {
            try {
                Remove-Item -Path $distDir -Recurse -Force -ErrorAction Stop
                $removed = $true
                Write-Host "  [OK] Dist directory removed" -ForegroundColor Green
            } catch {
                $retryCount++
                if ($retryCount -lt $maxRetries) {
                    Write-Host "  Retry $retryCount/$maxRetries - waiting 2 seconds..." -ForegroundColor Yellow
                    Start-Sleep -Seconds 2
                    
                    # Try to close any remaining processes
                    Get-Process | Where-Object { $_.Path -like "*dist*" } | Stop-Process -Force -ErrorAction SilentlyContinue
                } else {
                    Write-Host "  [WARN] Could not fully remove dist directory (some files may be locked)" -ForegroundColor Yellow
                    Write-Host "  Attempting to remove individual locked files..." -ForegroundColor Yellow
                    
                    # Try to remove individual files
                    Get-ChildItem -Path $distDir -Recurse -File | ForEach-Object {
                        try {
                            Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
                        } catch {
                            Write-Host "    Could not remove: $($_.Name)" -ForegroundColor Gray
                        }
                    }
                }
            }
        }
    } catch {
        Write-Host "  [ERROR] Failed to remove dist directory: $_" -ForegroundColor Red
        Write-Host "  You may need to manually close all applications and try again" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [OK] Dist directory does not exist (nothing to clean)" -ForegroundColor Green
}

# Step 4: Verify clean state
Write-Host "`n[4/4] Verifying clean state..." -ForegroundColor Yellow
$stillRunning = Get-Process | Where-Object { 
    $_.ProcessName -like "*System3*" -or 
    $_.ProcessName -like "*electron*"
}

if ($stillRunning) {
    Write-Host "  [WARN] Some processes may still be running:" -ForegroundColor Yellow
    foreach ($proc in $stillRunning) {
        Write-Host "    - $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor Gray
    }
    Write-Host "  You may need to manually close these processes" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] All processes closed" -ForegroundColor Green
}

Write-Host "`n=== READY FOR BUILD ===" -ForegroundColor Cyan
Write-Host "You can now run: npm run build" -ForegroundColor Green

