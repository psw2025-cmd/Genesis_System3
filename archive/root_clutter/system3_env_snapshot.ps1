# system3_env_snapshot.ps1
# Run from: PS C:\Genesis_System3>

Write-Host "===== SYSTEM3 ENVIRONMENT SNAPSHOT ====="
Write-Host ""

# 1. Basic OS + shell info
Write-Host "=== OS & SHELL ==="
Write-Host ("OS Version        : {0}" -f ([System.Environment]::OSVersion.VersionString))
Write-Host ("PowerShell        : {0}" -f $PSVersionTable.PSVersion)
Write-Host ("Host Process      : {0}" -f $Host.Name)
Write-Host ""

# 2. Virtual environment status
Write-Host "=== PYTHON VENV ==="
Write-Host ("Current Directory : {0}" -f (Get-Location))
Write-Host ("PythonHome        : {0}" -f $env:PYTHONHOME)
Write-Host ("PythonPath        : {0}" -f $env:PATH)
$venvPath = "C:\Genesis_System3\venv\Scripts\python.exe"
if (Test-Path $venvPath) {
    Write-Host ("Venv Python       : {0}" -f $venvPath)
    & $venvPath --version
} else {
    Write-Host "Venv Python       : NOT FOUND at C:\Genesis_System3\venv\Scripts\python.exe"
}
Write-Host ""

# 3. Key Python packages (from venv if possible)
Write-Host "=== PYTHON PACKAGES (SHORT LIST) ==="
if (Test-Path $venvPath) {
    & $venvPath -m pip list --format=columns | Select-Object -First 40
} else {
    Write-Host "Cannot list packages (venv python not found)."
}
Write-Host ""

# 4. Important files & scripts in project root
Write-Host "=== PROJECT ROOT FILES ==="
Get-ChildItem -Path "C:\Genesis_System3" -File |
  Where-Object { $_.Extension -in ".bat",".ps1",".py",".json",".md" } |
  Sort-Object Name |
  Select-Object Name, Extension, LastWriteTime
Write-Host ""

# 5. Live CSV inventory
Write-Host "=== STORAGE/LIVE CSV FILES ==="
$livePath = "C:\Genesis_System3\storage\live"
if (Test-Path $livePath) {
    Get-ChildItem -Path $livePath -Filter "*.csv" |
      Select-Object Name,
                    @{N="Rows";E={(Get-Content $_.FullName | Measure-Object -Line).Lines}},
                    LastWriteTime
} else {
    Write-Host "storage/live directory NOT FOUND"
}
Write-Host ""

# 6. Batch files relevant to autorun
Write-Host "=== BATCH FILES (ROOT) ==="
Get-ChildItem -Path "C:\Genesis_System3" -Filter "*.bat" |
  Select-Object Name, LastWriteTime
Write-Host ""

# 7. Heartbeat & watchdog status
Write-Host "=== HEARTBEAT & WATCHDOG ==="
$hb = "C:\Genesis_System3\system3_daily_heartbeat.json"
if (Test-Path $hb) {
    Write-Host "Heartbeat file FOUND at system3_daily_heartbeat.json"
    Get-Item $hb | Select-Object LastWriteTime, Length
} else {
    Write-Host "Heartbeat file NOT FOUND in project root."
}
$wdLog = Get-ChildItem "C:\Genesis_System3\logs" -Filter "system3_watchdog_*.log" -ErrorAction SilentlyContinue |
           Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($wdLog) {
    Write-Host ("Latest watchdog log: {0}" -f $wdLog.FullName)
    Get-Content $wdLog.FullName -Tail 10
} else {
    Write-Host "No watchdog logs found."
}
Write-Host ""

Write-Host "===== END SYSTEM3 ENVIRONMENT SNAPSHOT ====="
