@echo off
setlocal
cd /d "%~dp0\.."
venv\Scripts\python.exe tools\promote_to_cloud.py %*
