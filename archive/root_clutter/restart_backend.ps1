# System3 Backend Restart Script
# Cleanly kills all Python processes on port 8000 and restarts backend

Write-Host "=" * 70
Write-Host "SYSTEM3 BACKEND RESTART"
Write-Host "=" * 70

# Kill ALL Python processes (hard reset) to stop multiple backends / SmartAPI sessions
Write-Host "`n[1/3] Stopping ALL python processes (full reset)..."
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Aggressively kill anything listening on port 8000
Write-Host "   Checking for processes on port 8000..."
$maxAttempts = 5
$attempt = 0
do {
    $attempt++
    $port8000Pids = @()
    $netstatOutput = netstat -ano | findstr ":8000.*LISTENING"
    if ($netstatOutput) {
        $port8000Pids = $netstatOutput | ForEach-Object {
            $parts = $_.Split() | Where-Object { $_ -ne "" }
            if ($parts.Count -gt 0) {
                $pid = $parts[-1]
                if ($pid -match '^\d+$') {
                    $pid
                }
            }
        }
    }
    
    if ($port8000Pids.Count -gt 0) {
        Write-Host "   Attempt $attempt - Found processes on port 8000: $($port8000Pids -join ', ')"
        foreach ($procId in $port8000Pids) {
            Write-Host "   Killing process $procId..."
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 3
    } else {
        Write-Host "   ✅ Port 8000 is free"
        break
    }
} while ($attempt -lt $maxAttempts)

# Final verification
$stillListening = netstat -ano | findstr ":8000.*LISTENING"
if ($stillListening) {
    Write-Host "   ⚠️  WARNING: Port 8000 still in use after $maxAttempts attempts!"
    Write-Host "   Trying one more aggressive cleanup..."
    # Try killing by port using netstat
    $finalPids = netstat -ano | findstr ":8000" | ForEach-Object {
        $parts = $_.Split() | Where-Object { $_ -ne "" }
        if ($parts.Count -gt 0) {
            $pid = $parts[-1]
            if ($pid -match '^\d+$') {
                $pid
            }
        }
    } | Sort-Object -Unique
    foreach ($pid in $finalPids) {
        Write-Host "   Force killing PID $pid..."
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 5
}

Write-Host "✅ Port cleanup complete"

# Verify port is free
Write-Host "`n[2/3] Verifying port 8000 is free..."
$stillListening = netstat -ano | findstr ":8000.*LISTENING"
if ($stillListening) {
    Write-Host "⚠️  Warning: Port 8000 still in use. Waiting 3s..."
    Start-Sleep -Seconds 3
} else {
    Write-Host "✅ Port 8000 is free"
}

# Start backend (PRODUCTION MODE - no reload to avoid Angel One reconnects)
Write-Host "`n[3/3] Starting backend (PRODUCTION MODE - no auto-reload)..."
cd C:\Genesis_System3\dashboard\backend

# CRITICAL: Enforce REAL_ONLY mode
$env:SYSTEM3_REAL_ONLY = "1"
Write-Host "✅ REAL_ONLY mode: ENABLED (SYSTEM3_REAL_ONLY=1)" -ForegroundColor Green
Write-Host "   Synthetic data generation: DISABLED" -ForegroundColor Green

# Create log file for backend output
$logFile = "C:\Genesis_System3\outputs\backend.log"
$logDir = Split-Path $logFile -Parent
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Use the dedicated batch file that keeps window open
$batchFile = "C:\Genesis_System3\start_backend.bat"
if (-not (Test-Path $batchFile)) {
    Write-Host "⚠️  Warning: start_backend.bat not found, creating it..."
    # Create it if missing
    $backendScript = @"
@echo off
title System3 Backend - Port 8000
cd /d C:\Genesis_System3\dashboard\backend
echo ========================================
echo System3 Backend Starting...
echo ========================================
echo Directory: %CD%
echo Log file: C:\Genesis_System3\outputs\backend.log
echo ========================================
echo.
if not exist "C:\Genesis_System3\outputs" mkdir "C:\Genesis_System3\outputs"
python -m uvicorn app:app --host 127.0.0.1 --port 8000 > C:\Genesis_System3\outputs\backend.log 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Backend crashed!
    echo ========================================
    echo Check the log file: C:\Genesis_System3\outputs\backend.log
    echo ========================================
    echo.
    echo Last 20 lines of log:
    echo ========================================
    powershell -Command "Get-Content 'C:\Genesis_System3\outputs\backend.log' -Tail 20"
    echo ========================================
    echo.
    echo Press any key to close this window...
    pause >nul
)
"@
    $backendScript | Out-File -FilePath $batchFile -Encoding ASCII
}

# Start backend using batch file (window stays open on error)
$backendProc = Start-Process cmd.exe -ArgumentList "/k", "`"$batchFile`"" -PassThru -WindowStyle Normal

Write-Host "✅ Backend started (PID: $($backendProc.Id))"
Write-Host "   Log file: $logFile"
Write-Host "   Window will stay open if backend crashes"
Write-Host "`nWaiting 8 seconds for initialization..."
Start-Sleep -Seconds 8

# Verify backend is responding
Write-Host "`n[VERIFY] Checking backend health..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 5
    Write-Host "✅ Backend is responding!"
    Write-Host "   Status: $($response.status)"
    Write-Host "   Mode: $($response.mode)"
    Write-Host "   Broker: $($response.broker_status)"
    Write-Host "   QC: $($response.qc_status)"
} catch {
    Write-Host "⚠️  Backend not responding yet. Check the backend window for errors."
}

Write-Host "`n" + "=" * 70
Write-Host "Backend restart complete!"
Write-Host "Dashboard: http://localhost:3000 (or Electron app)"
Write-Host "API Docs: http://localhost:8000/docs"
Write-Host "=" * 70
