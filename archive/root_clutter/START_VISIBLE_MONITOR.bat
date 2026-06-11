@echo off
title VISIBLE AUTO MONITOR - Maximum Profit
color 0A
echo ========================================
echo   VISIBLE AUTO MONITOR
echo   Goal: Maximum Profit
echo ========================================
echo.
echo Starting visible monitor...
echo You will see continuous updates every 10 seconds!
echo.
cd /d %~dp0
if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe scripts\visible_auto_monitor.py
) else (
    python scripts\visible_auto_monitor.py
)
pause
