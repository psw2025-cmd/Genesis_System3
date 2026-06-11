# Build Instructions - Fixed

## Problem
Build fails with: `Access is denied` when trying to remove files from `dist\win-unpacked`

## Solution
The dist directory is locked because:
1. Electron app is still running
2. Backend process has files open
3. Windows file system has files locked

## Steps to Build

### Option 1: Use Clean Script (Recommended)
```powershell
cd C:\Genesis_System3
.\clean_and_build.ps1
cd desktop_app
npm run build
```

### Option 2: Manual Clean
1. **Close all System3 processes:**
   ```powershell
   Get-Process | Where-Object { $_.ProcessName -like "*System3*" -or $_.ProcessName -like "*electron*" } | Stop-Process -Force
   ```

2. **Close backend (if running):**
   ```powershell
   Get-NetTCPConnection -LocalPort 8000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
   ```

3. **Wait 2-3 seconds** for processes to fully close

4. **Remove dist directory:**
   ```powershell
   cd C:\Genesis_System3\desktop_app
   Remove-Item -Path dist -Recurse -Force -ErrorAction SilentlyContinue
   ```

5. **Build:**
   ```powershell
   npm run build
   ```

### Option 3: If Files Still Locked
1. Close ALL applications (VS Code, browsers, etc.)
2. Open Task Manager (Ctrl+Shift+Esc)
3. End any remaining Electron/Node processes
4. Wait 5 seconds
5. Try Option 2 again

## Verification Before Build

Run verification to ensure everything is ready:
```powershell
cd C:\Genesis_System3
python comprehensive_electron_app_verification.py
```

All 6 phases should pass before building.

## After Build

The installer will be at:
- `desktop_app\dist\System3 Ultra Setup 1.0.0.exe`
