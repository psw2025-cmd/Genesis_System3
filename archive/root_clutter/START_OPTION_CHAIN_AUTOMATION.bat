@echo off
REM ===================================================================
REM Option Chain Automation System - Quick Start Batch File
REM ===================================================================
REM This batch file starts the option chain automation system
REM with proper environment setup and error handling
REM ===================================================================

setlocal enabledelayedexpansion

REM Set project root
set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please create venv first: python -m venv venv
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in venv!
    pause
    exit /b 1
)

echo ===================================================================
echo OPTION CHAIN AUTOMATION SYSTEM - STARTING
echo ===================================================================
echo.
echo Project Root: %ROOT_DIR%
echo Python: 
python --version
echo.
echo ===================================================================
echo.

REM Check if config file exists
if exist "config\option_chain_config.json" (
    echo [INFO] Using custom config: config\option_chain_config.json
    python option_chain_automation_master.py --config config\option_chain_config.json
) else (
    echo [INFO] Using default configuration
    python option_chain_automation_master.py
)

REM Check exit code
if errorlevel 1 (
    echo.
    echo [ERROR] System exited with error!
    pause
    exit /b 1
)

echo.
echo ===================================================================
echo SYSTEM STOPPED
echo ===================================================================
pause
