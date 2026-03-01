# P2.4: Log rotation for logs/ directory
# Run daily via Task Scheduler: schtasks /create /tn "System3LogRotation" /tr "powershell -File ...\log_rotation.ps1" /sc daily
# Keeps last 7 days, removes older log files

param(
    [string]$LogsDir = (Join-Path (Split-Path -Parent $PSScriptRoot) "logs"),
    [int]$RetainDays = 7
)

$ErrorActionPreference = "Continue"
if (!(Test-Path $LogsDir)) { exit 0 }
$cutoff = (Get-Date).AddDays(-$RetainDays)
$count = 0
Get-ChildItem -Path $LogsDir -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
    $_.LastWriteTime -lt $cutoff -and $_.Extension -match '\.(log|jsonl|txt)$'
} | ForEach-Object {
    Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
    $count++
}
if ($count -gt 0) { Write-Host "Rotated (removed) $count log files older than $RetainDays days" }
