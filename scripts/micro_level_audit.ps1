# Micro-Level Dashboard System Audit
# Comprehensive audit of all components at micro level

$ErrorActionPreference = "Continue"
$ROOT_DIR = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$VENV_DIR = Join-Path $ROOT_DIR "venv"
$BACKEND_DIR = Join-Path $ROOT_DIR "dashboard\backend"
$FRONTEND_DIR = Join-Path $ROOT_DIR "dashboard\frontend"
$OUTPUTS_DIR = Join-Path $ROOT_DIR "outputs"
$LOGS_DIR = Join-Path $ROOT_DIR "logs"

$auditResults = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    checks = @()
    summary = @{
        total_checks = 0
        passed = 0
        failed = 0
        warnings = 0
    }
}

function Add-Check {
    param($name, $status, $details, $severity = "INFO")
    $auditResults.checks += @{
        name = $name
        status = $status
        details = $details
        severity = $severity
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    $auditResults.summary.total_checks++
    if ($status -eq "PASS") { $auditResults.summary.passed++ }
    elseif ($status -eq "FAIL") { $auditResults.summary.failed++ }
    elseif ($status -eq "WARN") { $auditResults.summary.warnings++ }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MICRO-LEVEL DASHBOARD SYSTEM AUDIT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# AUDIT 1: Prerequisites
Write-Host "[AUDIT 1/15] Prerequisites" -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    $pyVersion = python --version 2>&1
    Write-Host "  ✅ Python: $pyVersion" -ForegroundColor Green
    Add-Check "Python Installation" "PASS" $pyVersion
} else {
    Write-Host "  ❌ Python: NOT FOUND" -ForegroundColor Red
    Add-Check "Python Installation" "FAIL" "Python not found in PATH" "CRITICAL"
}

$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✅ Node.js: $nodeVersion" -ForegroundColor Green
    Add-Check "Node.js Installation" "PASS" $nodeVersion
} else {
    Write-Host "  ❌ Node.js: NOT FOUND" -ForegroundColor Red
    Add-Check "Node.js Installation" "FAIL" "Node.js not found in PATH" "CRITICAL"
}

$npm = Get-Command npm -ErrorAction SilentlyContinue
if ($npm) {
    $npmVersion = npm --version 2>&1
    Write-Host "  ✅ npm: $npmVersion" -ForegroundColor Green
    Add-Check "npm Installation" "PASS" $npmVersion
} else {
    Write-Host "  ❌ npm: NOT FOUND" -ForegroundColor Red
    Add-Check "npm Installation" "FAIL" "npm not found in PATH" "CRITICAL"
}

# AUDIT 2: Virtual Environment
Write-Host "`n[AUDIT 2/15] Virtual Environment" -ForegroundColor Yellow
if (Test-Path "$VENV_DIR\Scripts\python.exe") {
    $venvVersion = & "$VENV_DIR\Scripts\python.exe" --version 2>&1
    Write-Host "  ✅ Venv exists: $venvVersion" -ForegroundColor Green
    Add-Check "Virtual Environment" "PASS" $venvVersion
} else {
    Write-Host "  ❌ Venv missing" -ForegroundColor Red
    Add-Check "Virtual Environment" "FAIL" "venv\Scripts\python.exe not found" "CRITICAL"
}

# AUDIT 3: Critical Python Packages
Write-Host "`n[AUDIT 3/15] Critical Python Packages" -ForegroundColor Yellow
$criticalPackages = @("pandas", "numpy", "uvicorn", "fastapi", "requests", "aiohttp")
$installedPackages = 0
foreach ($pkg in $criticalPackages) {
    $check = & "$VENV_DIR\Scripts\python.exe" -m pip show $pkg 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $version = & "$VENV_DIR\Scripts\python.exe" -m pip show $pkg 2>&1 | Select-String "Version:" | ForEach-Object { $_.ToString().Split(":")[1].Trim() }
        Write-Host "  ✅ $pkg : $version" -ForegroundColor Green
        $installedPackages++
    } else {
        Write-Host "  ❌ $pkg : NOT INSTALLED" -ForegroundColor Red
    }
}
if ($installedPackages -eq $criticalPackages.Count) {
    Add-Check "Critical Python Packages" "PASS" "All $($criticalPackages.Count) packages installed"
} else {
    Add-Check "Critical Python Packages" "FAIL" "$installedPackages/$($criticalPackages.Count) packages installed" "HIGH"
}

# AUDIT 4: Backend Dependencies
Write-Host "`n[AUDIT 4/15] Backend Dependencies" -ForegroundColor Yellow
$backendReq = Join-Path $BACKEND_DIR "requirements.txt"
if (Test-Path $backendReq) {
    $reqContent = Get-Content $backendReq | Where-Object { $_ -and -not $_.StartsWith("#") -and $_.Trim() -ne "" }
    Write-Host "  ✅ requirements.txt: $($reqContent.Count) packages" -ForegroundColor Green
    
    $installed = 0
    foreach ($pkg in $reqContent) {
        $pkgName = ($pkg -split "==")[0].Trim()
        $pkgName = ($pkgName -split ">=")[0].Trim()
        $pkgName = ($pkgName -split "<=")[0].Trim()
        $check = & "$VENV_DIR\Scripts\python.exe" -m pip show $pkgName 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $installed++ }
    }
    Write-Host "  ✅ Installed: $installed/$($reqContent.Count)" -ForegroundColor $(if ($installed -eq $reqContent.Count) { 'Green' } else { 'Yellow' })
    Add-Check "Backend Dependencies" $(if ($installed -eq $reqContent.Count) { "PASS" } else { "WARN" }) "$installed/$($reqContent.Count) installed"
} else {
    Write-Host "  ❌ requirements.txt missing" -ForegroundColor Red
    Add-Check "Backend Dependencies" "FAIL" "requirements.txt not found" "HIGH"
}

# AUDIT 5: Frontend Dependencies
Write-Host "`n[AUDIT 5/15] Frontend Dependencies" -ForegroundColor Yellow
if (Test-Path "$FRONTEND_DIR\node_modules") {
    $nodeModules = (Get-ChildItem "$FRONTEND_DIR\node_modules" -Directory -ErrorAction SilentlyContinue).Count
    Write-Host "  ✅ node_modules: $nodeModules packages" -ForegroundColor Green
    Add-Check "Frontend node_modules" "PASS" "$nodeModules packages"
} else {
    Write-Host "  ❌ node_modules missing" -ForegroundColor Red
    Add-Check "Frontend node_modules" "FAIL" "node_modules directory not found" "HIGH"
}

if (Test-Path "$FRONTEND_DIR\package.json") {
    Write-Host "  ✅ package.json exists" -ForegroundColor Green
    Add-Check "Frontend package.json" "PASS" "File exists"
} else {
    Write-Host "  ❌ package.json missing" -ForegroundColor Red
    Add-Check "Frontend package.json" "FAIL" "File not found" "CRITICAL"
}

# AUDIT 6: Backend Code Files
Write-Host "`n[AUDIT 6/15] Backend Code Files" -ForegroundColor Yellow
$backendFiles = @(
    @{Path="app.py"; Critical=$true},
    @{Path="requirements.txt"; Critical=$true}
)
foreach ($file in $backendFiles) {
    $fullPath = Join-Path $BACKEND_DIR $file.Path
    if (Test-Path $fullPath) {
        $size = (Get-Item $fullPath).Length
        Write-Host "  ✅ $($file.Path) ($size bytes)" -ForegroundColor Green
        Add-Check "Backend: $($file.Path)" "PASS" "$size bytes"
    } else {
        Write-Host "  ❌ $($file.Path) - MISSING" -ForegroundColor Red
        Add-Check "Backend: $($file.Path)" "FAIL" "File not found" $(if ($file.Critical) { "CRITICAL" } else { "HIGH" })
    }
}

# AUDIT 7: Frontend Code Files
Write-Host "`n[AUDIT 7/15] Frontend Code Files" -ForegroundColor Yellow
$frontendFiles = @(
    @{Path="src\App.tsx"; Critical=$true},
    @{Path="src\config.ts"; Critical=$true},
    @{Path="src\components\ChainAnalytics.tsx"; Critical=$true},
    @{Path="src\components\Overview.tsx"; Critical=$true},
    @{Path="src\components\PaperTrading.tsx"; Critical=$false},
    @{Path="src\components\ModelBehavior.tsx"; Critical=$false},
    @{Path="src\components\Signals.tsx"; Critical=$false},
    @{Path="src\components\ControlPlane.tsx"; Critical=$false}
)
foreach ($file in $frontendFiles) {
    $fullPath = Join-Path $FRONTEND_DIR $file.Path
    if (Test-Path $fullPath) {
        Write-Host "  ✅ $($file.Path)" -ForegroundColor Green
        Add-Check "Frontend: $($file.Path)" "PASS" "File exists"
    } else {
        Write-Host "  ❌ $($file.Path) - MISSING" -ForegroundColor Red
        Add-Check "Frontend: $($file.Path)" "FAIL" "File not found" $(if ($file.Critical) { "CRITICAL" } else { "MEDIUM" })
    }
}

# AUDIT 8: Port Status
Write-Host "`n[AUDIT 8/15] Port Status" -ForegroundColor Yellow
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue

if ($port8000) {
    $proc = Get-Process -Id $port8000.OwningProcess -ErrorAction SilentlyContinue
    Write-Host "  ✅ Port 8000: IN USE (PID: $($port8000.OwningProcess), Process: $($proc.ProcessName))" -ForegroundColor Green
    Add-Check "Port 8000" "PASS" "In use by $($proc.ProcessName)"
} else {
    Write-Host "  ✅ Port 8000: FREE" -ForegroundColor Gray
    Add-Check "Port 8000" "PASS" "Port is free"
}

if ($port3000) {
    $proc = Get-Process -Id $port3000.OwningProcess -ErrorAction SilentlyContinue
    Write-Host "  ✅ Port 3000: IN USE (PID: $($port3000.OwningProcess), Process: $($proc.ProcessName))" -ForegroundColor Green
    Add-Check "Port 3000" "PASS" "In use by $($proc.ProcessName)"
} else {
    Write-Host "  ✅ Port 3000: FREE" -ForegroundColor Gray
    Add-Check "Port 3000" "PASS" "Port is free"
}

# AUDIT 9: Service Health
Write-Host "`n[AUDIT 9/15] Service Health" -ForegroundColor Yellow
try {
    $backend = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    $backendData = $backend.Content | ConvertFrom-Json
    Write-Host "  ✅ Backend: RUNNING" -ForegroundColor Green
    Write-Host "    Status: $($backendData.status)" -ForegroundColor Gray
    Write-Host "    Mode: $($backendData.mode)" -ForegroundColor Gray
    Write-Host "    Market: $($backendData.market_status)" -ForegroundColor Gray
    Write-Host "    Broker: $($backendData.broker_status)" -ForegroundColor Gray
    Add-Check "Backend Health" "PASS" "Status: $($backendData.status), Mode: $($backendData.mode)"
} catch {
    Write-Host "  ❌ Backend: NOT RESPONDING" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor Gray
    Add-Check "Backend Health" "FAIL" "Not responding: $_" "CRITICAL"
}

try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host "  ✅ Frontend: RUNNING (Status: $($frontend.StatusCode))" -ForegroundColor Green
    Add-Check "Frontend Health" "PASS" "Status: $($frontend.StatusCode)"
} catch {
    Write-Host "  ❌ Frontend: NOT RESPONDING" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor Gray
    Add-Check "Frontend Health" "FAIL" "Not responding: $_" "CRITICAL"
}

# AUDIT 10: API Endpoints
Write-Host "`n[AUDIT 10/15] API Endpoints" -ForegroundColor Yellow
$endpoints = @(
    @{Path="/api/health"; Name="Health"},
    @{Path="/api/qc"; Name="QC"},
    @{Path="/api/signal/top"; Name="Signal"},
    @{Path="/api/positions"; Name="Positions"},
    @{Path="/api/pnl"; Name="PnL"},
    @{Path="/api/perf"; Name="Performance"},
    @{Path="/api/chain/NIFTY"; Name="Chain NIFTY"}
)
$working = 0
foreach ($ep in $endpoints) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000$($ep.Path)" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        Write-Host "  ✅ $($ep.Name): $($r.StatusCode)" -ForegroundColor Green
        $working++
        Add-Check "API: $($ep.Name)" "PASS" "Status: $($r.StatusCode)"
    } catch {
        Write-Host "  ❌ $($ep.Name): FAILED" -ForegroundColor Red
        Add-Check "API: $($ep.Name)" "FAIL" "Error: $_" "HIGH"
    }
}
Write-Host "  Summary: $working/$($endpoints.Count) endpoints working" -ForegroundColor $(if ($working -eq $endpoints.Count) { 'Green' } else { 'Yellow' })

# AUDIT 11: Data Files
Write-Host "`n[AUDIT 11/15] Data Files" -ForegroundColor Yellow
$dataFiles = @(
    @{Path="health.json"; Critical=$true},
    @{Path="chain_raw_live.csv"; Critical=$true},
    @{Path="qc_report_live.json"; Critical=$false},
    @{Path="perf_metrics.json"; Critical=$false},
    @{Path="top_trade_signal.json"; Critical=$false},
    @{Path="positions_live.json"; Critical=$false}
)
foreach ($file in $dataFiles) {
    $fullPath = Join-Path $OUTPUTS_DIR $file.Path
    if (Test-Path $fullPath) {
        $age = (Get-Date) - (Get-Item $fullPath).LastWriteTime
        $size = (Get-Item $fullPath).Length
        $ageStr = if ($age.TotalMinutes -lt 60) { "$([math]::Round($age.TotalMinutes, 1)) min" } else { "$([math]::Round($age.TotalHours, 1)) hours" }
        Write-Host "  ✅ $($file.Path)" -ForegroundColor Green
        Write-Host "    Size: $size bytes, Age: $ageStr" -ForegroundColor Gray
        Add-Check "Data: $($file.Path)" "PASS" "Size: $size bytes, Age: $ageStr"
    } else {
        Write-Host "  ⚠️ $($file.Path) - MISSING" -ForegroundColor Yellow
        Add-Check "Data: $($file.Path)" $(if ($file.Critical) { "FAIL" } else { "WARN" }) "File not found" $(if ($file.Critical) { "HIGH" } else { "LOW" })
    }
}

# AUDIT 12: CORS Configuration
Write-Host "`n[AUDIT 12/15] CORS Configuration" -ForegroundColor Yellow
$backendApp = Join-Path $BACKEND_DIR "app.py"
if (Test-Path $backendApp) {
    $content = Get-Content $backendApp -Raw
    if ($content -match "allow_origins.*\*") {
        Write-Host "  ✅ CORS: Allows all origins (development mode)" -ForegroundColor Green
        Add-Check "CORS Configuration" "PASS" "Allows all origins"
    } elseif ($content -match "allow_origins.*192\.168") {
        Write-Host "  ✅ CORS: Configured for network IPs" -ForegroundColor Green
        Add-Check "CORS Configuration" "PASS" "Network IPs allowed"
    } else {
        Write-Host "  ⚠️ CORS: May need update for network access" -ForegroundColor Yellow
        Add-Check "CORS Configuration" "WARN" "May not allow network IPs" "MEDIUM"
    }
} else {
    Write-Host "  ❌ Cannot check CORS: app.py not found" -ForegroundColor Red
    Add-Check "CORS Configuration" "FAIL" "Cannot verify" "HIGH"
}

# AUDIT 13: Frontend Config
Write-Host "`n[AUDIT 13/15] Frontend Configuration" -ForegroundColor Yellow
$configFile = Join-Path $FRONTEND_DIR "src\config.ts"
if (Test-Path $configFile) {
    $configContent = Get-Content $configFile -Raw
    if ($configContent -match "getApiBase|API_BASE") {
        Write-Host "  ✅ Frontend config: Dynamic API detection" -ForegroundColor Green
        Add-Check "Frontend Config" "PASS" "Dynamic API base configured"
    } else {
        Write-Host "  ⚠️ Frontend config: May use hardcoded localhost" -ForegroundColor Yellow
        Add-Check "Frontend Config" "WARN" "May not handle network IPs" "MEDIUM"
    }
} else {
    Write-Host "  ❌ Frontend config: Missing" -ForegroundColor Red
    Add-Check "Frontend Config" "FAIL" "config.ts not found" "HIGH"
}

# AUDIT 14: Log Files
Write-Host "`n[AUDIT 14/15] Log Files" -ForegroundColor Yellow
if (Test-Path $LOGS_DIR) {
    $logFiles = Get-ChildItem $LOGS_DIR -Filter "dashboard_startup_*.log" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 5
    if ($logFiles) {
        Write-Host "  ✅ Log directory exists" -ForegroundColor Green
        Write-Host "  Recent logs:" -ForegroundColor Gray
        foreach ($log in $logFiles) {
            $age = (Get-Date) - $log.LastWriteTime
            $ageStr = if ($age.TotalMinutes -lt 60) { "$([math]::Round($age.TotalMinutes, 1)) min ago" } else { "$([math]::Round($age.TotalHours, 1)) hours ago" }
            Write-Host "    - $($log.Name) ($ageStr)" -ForegroundColor Gray
        }
        Add-Check "Log Files" "PASS" "$($logFiles.Count) recent log files"
    } else {
        Write-Host "  ⚠️ No dashboard startup logs found" -ForegroundColor Yellow
        Add-Check "Log Files" "WARN" "No startup logs" "LOW"
    }
} else {
    Write-Host "  ⚠️ Log directory missing" -ForegroundColor Yellow
    Add-Check "Log Files" "WARN" "Log directory not found" "LOW"
}

# AUDIT 15: Script Files
Write-Host "`n[AUDIT 15/15] Script Files" -ForegroundColor Yellow
$scriptFiles = @(
    @{Path="START_FULL_DASHBOARD_SYSTEM.bat"; Critical=$true},
    @{Path="UPDATE_DASHBOARD_SYSTEM.bat"; Critical=$false},
    @{Path="scripts\auto_fix_and_update_dashboard.ps1"; Critical=$false},
    @{Path="scripts\dashboard_data_validator.py"; Critical=$false},
    @{Path="scripts\multi_user_dashboard_test.py"; Critical=$false}
)
foreach ($file in $scriptFiles) {
    $fullPath = Join-Path $ROOT_DIR $file.Path
    if (Test-Path $fullPath) {
        Write-Host "  ✅ $($file.Path)" -ForegroundColor Green
        Add-Check "Script: $($file.Path)" "PASS" "File exists"
    } else {
        Write-Host "  ⚠️ $($file.Path) - MISSING" -ForegroundColor Yellow
        Add-Check "Script: $($file.Path)" $(if ($file.Critical) { "FAIL" } else { "WARN" }) "File not found" $(if ($file.Critical) { "HIGH" } else { "LOW" })
    }
}

# Save audit results
$auditFile = Join-Path $OUTPUTS_DIR "audit\dashboard_micro_audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$auditFileDir = Split-Path $auditFile
if (-not (Test-Path $auditFileDir)) {
    New-Item -ItemType Directory -Path $auditFileDir -Force | Out-Null
}
$auditResults | ConvertTo-Json -Depth 10 | Out-File -FilePath $auditFile -Encoding UTF8

# Final Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AUDIT SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total Checks: $($auditResults.summary.total_checks)" -ForegroundColor White
Write-Host "Passed: $($auditResults.summary.passed)" -ForegroundColor Green
Write-Host "Failed: $($auditResults.summary.failed)" -ForegroundColor $(if ($auditResults.summary.failed -eq 0) { 'Green' } else { 'Red' })
Write-Host "Warnings: $($auditResults.summary.warnings)" -ForegroundColor $(if ($auditResults.summary.warnings -eq 0) { 'Green' } else { 'Yellow' })
Write-Host ""
Write-Host "Audit Report: $auditFile" -ForegroundColor Cyan
Write-Host ""

# Show critical issues
$criticalIssues = $auditResults.checks | Where-Object { $_.severity -eq "CRITICAL" -and $_.status -eq "FAIL" }
if ($criticalIssues) {
    Write-Host "CRITICAL ISSUES FOUND:" -ForegroundColor Red
    foreach ($issue in $criticalIssues) {
        Write-Host "  ❌ $($issue.name): $($issue.details)" -ForegroundColor Red
    }
    Write-Host ""
}

# Overall status
$overallStatus = if ($auditResults.summary.failed -eq 0) { "PASS" } else { "FAIL" }
Write-Host "Overall Status: $overallStatus" -ForegroundColor $(if ($overallStatus -eq "PASS") { 'Green' } else { 'Red' })
Write-Host ""
