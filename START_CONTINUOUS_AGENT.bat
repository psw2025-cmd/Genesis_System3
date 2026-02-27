@echo off
title CONTINUOUS AUTO AGENT - Every 2 Minutes
color 0A
echo ========================================
echo   CONTINUOUS AUTO AGENT
echo   Self-Triggering Every 2 Minutes
echo   Goal: Maximum Profit
echo ========================================
echo.
echo Starting continuous agent...
echo Will check and fix everything every 2 minutes!
echo.
cd /d %~dp0
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe scripts\continuous_auto_agent.py
) else if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe scripts\continuous_auto_agent.py
) else (
    python scripts\continuous_auto_agent.py
)
pause
