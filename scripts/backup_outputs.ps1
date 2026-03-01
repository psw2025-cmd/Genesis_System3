# Backup outputs/ and config/ for Genesis System3
# Usage: powershell -File scripts\backup_outputs.ps1
# Run from repo root: cd C:\Genesis_System3; .\scripts\backup_outputs.ps1
$root = if ($PSScriptRoot) { (Get-Item $PSScriptRoot).Parent.FullName } else { (Get-Location).Path }
$date = Get-Date -Format "yyyyMMdd"
$dest = Join-Path $root "outputs_backup\$date"
New-Item -ItemType Directory -Path $dest -Force | Out-Null
Copy-Item -Path (Join-Path $root "outputs\*") -Destination $dest -Recurse -Force -ErrorAction SilentlyContinue
$configDest = Join-Path $dest "config"
New-Item -ItemType Directory -Path $configDest -Force | Out-Null
Copy-Item -Path (Join-Path $root "config\*") -Destination $configDest -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Backup complete: $dest"
