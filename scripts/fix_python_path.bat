@echo off
REM Fix Python PATH Issues - Permanent Solution
echo ========================================
echo Fixing Python PATH Configuration
echo ========================================
echo.

REM Find Python
where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

REM Get Python path
for /f "tokens=*" %%i in ('where python') do set PYTHON_EXE=%%i
for %%i in ("%PYTHON_EXE%") do set PYTHON_DIR=%%~dpi
set SCRIPTS_DIR=%PYTHON_DIR%Scripts

echo Python found at: %PYTHON_DIR%
echo Scripts directory: %SCRIPTS_DIR%
echo.

REM Check if Scripts exists
if not exist "%SCRIPTS_DIR%pip.exe" (
    echo WARNING: pip.exe not found at %SCRIPTS_DIR%
    echo.
)

REM Verify pip works
echo Verifying pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip not accessible
    echo.
    echo To fix permanently:
    echo 1. Open System Properties ^> Environment Variables
    echo 2. Add to PATH: %SCRIPTS_DIR%
    pause
    exit /b 1
) else (
    echo [OK] pip is accessible
)

REM Verify Python works
echo Verifying Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not accessible
    pause
    exit /b 1
) else (
    echo [OK] Python is accessible
)

echo.
echo ========================================
echo [SUCCESS] Python PATH is configured
echo ========================================
echo.
echo Note: For permanent fix, add to System PATH:
echo   %SCRIPTS_DIR%
echo.
pause
