@echo off
REM ============================================================
REM  Build Fresh System3 Ultra Installer
REM  Run this when you made many source changes - it rebuilds
REM  frontend, removes old installer, and creates a new exe.
REM  Pre-requisites: run check_build_requirements.py first (this
REM  script will run it for you and stop if anything is missing).
REM ============================================================
setlocal
cd /d "%~dp0"

echo.
echo [0/5] Checking requirements (Python, venv, Node, npm, deps)...
python check_build_requirements.py
if errorlevel 1 (
    echo.
    echo Fix the [FAIL] items above, then run this script again.
    echo See PRE_BUILD_REQUIREMENTS.md for step-by-step help.
    pause
    exit /b 1
)
echo.

echo [1/5] Cleaning old installer and Electron dist...
if exist "desktop_app\dist" (
    rmdir /s /q "desktop_app\dist"
    echo   Old desktop_app\dist removed.
) else (
    echo   No old dist folder - skip.
)

echo.
echo [2/5] Building frontend (dashboard) - so installer has latest UI...
cd dashboard\frontend
call npm run build
if errorlevel 1 (
    echo ERROR: Frontend build failed.
    cd /d "%~dp0"
    exit /b 1
)
cd /d "%~dp0"
echo   Frontend build done.

echo.
echo [3/5] Building Electron app (creates new installer)...
cd desktop_app
call npm run build
if errorlevel 1 (
    echo ERROR: Electron build failed.
    cd /d "%~dp0"
    exit /b 1
)
cd /d "%~dp0"
echo   Electron build done.

echo.
echo [4/5] Done. New installer location:
echo   %~dp0desktop_app\dist\System3 Ultra Setup 1.0.0.exe
echo.
echo You can now run that exe to install and test.
pause
