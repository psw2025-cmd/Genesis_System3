# IMPORTANT: Always use venv for Python execution in this workspace

## Quick Activation
```powershell
& C:\Genesis_System3\venv\Scripts\Activate.ps1
```

After activation, your prompt will show:
```
(venv) PS C:\Genesis_System3>
```

## Why This Matters
- All Python packages (requirements) are isolated in this venv
- Ensures reproducible, clean environment
- Avoids conflicts with system Python
- Required for all Python scripts: `python script.py`, `pip install`, etc.

## Deactivate (if needed)
```powershell
deactivate
```

## Check venv status
```powershell
$env:VIRTUAL_ENV
```
If output shows the venv path, you're activated. If empty, you're not in the venv.

## Auto-activation (optional)
Add to your PowerShell profile to auto-activate on startup:
```powershell
& "C:\Genesis_System3\venv\Scripts\Activate.ps1"
```

---
**This venv is mandatory for all Genesis_System3 Python work.**
