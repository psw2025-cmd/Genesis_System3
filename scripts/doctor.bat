@echo off
REM ====================================================================
REM GENESIS SYSTEM3 - DOCTOR SCRIPT (Windows)
REM ====================================================================
REM Environment and dependency validator
REM ====================================================================

cd /d "%~dp0.."
python scripts\doctor.py
pause
