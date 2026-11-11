# System3 Ultra: How to Run Monitoring Script

**Issue**: Windows tries to open `.ps1` files in Notepad instead of running them.

**Solution**: Use one of the methods below.

---

## ✅ Solution 1: Use Batch File (RECOMMENDED)

**Easiest Method**: Double-click `monitor_ultra_system.bat`

Or from command prompt:
```cmd
monitor_ultra_system.bat
```

This batch file will:
- Activate the virtual environment automatically
- Run the PowerShell script with proper execution policy
- Pause at the end so you can see the results

---

## ✅ Solution 2: Run from PowerShell

Open PowerShell and run:
```powershell
powershell -ExecutionPolicy Bypass -File .\monitor_ultra_system.ps1
```

Or if you're already in PowerShell:
```powershell
.\monitor_ultra_system.ps1
```
(May require setting execution policy first)

---

## ✅ Solution 3: Set PowerShell Execution Policy (One-Time)

If you want to run `.ps1` files directly, set execution policy:

**For Current User** (Recommended):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then you can run:
```powershell
.\monitor_ultra_system.ps1
```

**Note**: This is a one-time setup. After this, you can double-click `.ps1` files to run them.

---

## ✅ Solution 4: Run from Command Prompt

From CMD (not PowerShell):
```cmd
powershell -ExecutionPolicy Bypass -File monitor_ultra_system.ps1
```

---

## 🎯 Recommended Approach

**Use the batch file** (`monitor_ultra_system.bat`):
- ✅ Works immediately (no setup needed)
- ✅ Handles virtual environment activation
- ✅ Works from CMD or by double-clicking
- ✅ No execution policy issues

---

## Quick Reference

| Method | Command | When to Use |
|--------|---------|-------------|
| **Batch File** | `monitor_ultra_system.bat` | ✅ **Recommended** - Easiest |
| PowerShell (Bypass) | `powershell -ExecutionPolicy Bypass -File .\monitor_ultra_system.ps1` | When batch file not available |
| PowerShell (Direct) | `.\monitor_ultra_system.ps1` | After setting execution policy |
| CMD | `powershell -ExecutionPolicy Bypass -File monitor_ultra_system.ps1` | From Command Prompt |

---

## Troubleshooting

### "Execution Policy" Error
**Solution**: Use Solution 2 or 3 above

### "Virtual Environment Not Found" Error
**Solution**: Make sure you're in the project directory:
```cmd
cd C:\Genesis_System3
```

### "Python Module Not Found" Error
**Solution**: Activate virtual environment first:
```cmd
venv\Scripts\activate
```

---

## Status

✅ **Batch file created**: `monitor_ultra_system.bat`  
✅ **Ready to use**: Double-click the `.bat` file to run

