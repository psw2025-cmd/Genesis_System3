@echo off
setlocal
cd /d "%~dp0\.."
if not exist "venv\Scripts\python.exe" (
  echo ERROR: venv not found. Run from Genesis_System3 with venv installed.
  exit /b 1
)
venv\Scripts\python.exe tools\fetch_nse_option_chain.py %*
