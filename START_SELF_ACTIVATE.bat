@echo off
title SELF-ACTIVATING ANALYSIS & IMPROVEMENT SYSTEM
color 0A
echo ========================================
echo   SELF-ACTIVATING ANALYSIS SYSTEM
echo   Auto-Analyze Every 2 Minutes
echo   Goal: Maximum Profit
echo ========================================
echo.
echo Starting self-activating system...
echo Will analyze and improve every 2 minutes!
echo.
cd /d %~dp0
if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe scripts\self_activate_analyze_improve.py
) else (
    python scripts\self_activate_analyze_improve.py
)
pause
