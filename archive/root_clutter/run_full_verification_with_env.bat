@echo off
rem UTF-8-safe runner for full verification checklist
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
rem ensure repo root is on PYTHONPATH
set PYTHONPATH=%CD%
rem activate venv if present
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)
%~dp0venv\Scripts\python.exe run_full_verification_checklist.py %*
exit /b %ERRORLEVEL%
