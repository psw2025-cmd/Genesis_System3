@echo off
REM System3 Ultra - Complete Environment Setup
echo ========================================
echo System3 Ultra - Environment Setup
echo ========================================
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
python --version
echo.

REM Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    pause
    exit /b 1
)
node --version
echo.

REM Install Python dependencies
echo Installing Python dependencies...
cd dashboard\backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
cd ..\..
echo.

REM Install Node.js dependencies
echo Installing Node.js dependencies...
cd dashboard\frontend
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install Node.js dependencies
    pause
    exit /b 1
)
cd ..\..
echo.

REM Install Electron dependencies
echo Installing Electron dependencies...
cd desktop_app
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install Electron dependencies
    pause
    exit /b 1
)
cd ..
echo.

REM Build frontend
echo Building frontend...
cd dashboard\frontend
call npm run build
if errorlevel 1 (
    echo ERROR: Failed to build frontend
    pause
    exit /b 1
)
cd ..\..
echo.

REM Add upgrade agent endpoints
echo Adding upgrade agent endpoints...
python scripts\add_upgrade_agent_endpoints.py
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Run: cd desktop_app ^&^& npm run build:win
echo   2. Or run: cd desktop_app ^&^& npm start
echo.
pause
