@echo off
title COMBINED AUTO SYSTEM - Check, Fix, Verify Online
color 0A
echo ========================================
echo   COMBINED AUTO SYSTEM
echo   Check, Fix, Verify Online Every 2 Min
echo   Goal: Maximum Profit
echo ========================================
echo.
echo Starting combined auto system...
echo Will check, fix, and verify against internet every 2 minutes!
echo.
cd /d %~dp0
if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe scripts\combined_auto_system.py
) else (
    python scripts\combined_auto_system.py
)
pause
