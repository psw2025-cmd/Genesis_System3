@echo off
REM P2.4: Log rotation - run daily
powershell -ExecutionPolicy Bypass -File "%~dp0log_rotation.ps1" %*
