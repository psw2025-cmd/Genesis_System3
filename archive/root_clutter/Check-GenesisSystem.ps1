Write-Host "=== Genesis_System3 Diagnostic Script ===" -ForegroundColor Cyan

# 1. Check folder attributes
Write-Host "`n[1] Folder Attributes:" -ForegroundColor Yellow
attrib C:\Genesis_System3

# 2. Check if venv exists
Write-Host "`n[2] venv Folder Exists:" -ForegroundColor Yellow
Test-Path C:\Genesis_System3\venv

# 3. Check permissions
Write-Host "`n[3] Folder Permissions:" -ForegroundColor Yellow
icacls C:\Genesis_System3

# 4. Check if folder is inside Google Drive or OneDrive
Write-Host "`n[4] Cloud Sync Check:" -ForegroundColor Yellow
Get-ChildItem "C:\" | Where-Object { $_.Name -match "Google Drive|OneDrive" }

# 5. Check running sync processes
Write-Host "`n[5] Sync Processes:" -ForegroundColor Yellow
Get-Process | Where-Object { $_.ProcessName -match "GoogleDrive|OneDrive" }

Write-Host "`n=== End of Diagnostics ===" -ForegroundColor Cyan
