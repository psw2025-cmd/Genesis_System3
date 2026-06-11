# SYSTEM3 ENVIRONMENT AUTO-SETUP SCRIPT
# Usage: .\start_system3_env.ps1

# Activate Python venv
.\venv\Scripts\Activate.ps1

# Show Python version and executable path
python --version
Write-Host "Python executable:" (Get-Command python).Source

# Run environment snapshot if available
if (Test-Path ".\system3_env_snapshot.ps1") {
    .\system3_env_snapshot.ps1
}

# (Optional) Run any startup batch or validation script
# Uncomment below to run autorun or validation
# .\run_full_verification_with_env.bat
# .\START_AUTORUN_AND_WATCHDOG.bat

Write-Host "SYSTEM3 environment setup complete."
