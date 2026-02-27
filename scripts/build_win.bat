@echo off
REM Build System3 Ultra Desktop App for Windows
echo ========================================
echo Building System3 Ultra Desktop App
echo ========================================
echo.

REM Build frontend
echo Building frontend...
cd dashboard\frontend
call npm run build
if errorlevel 1 (
    echo ERROR: Frontend build failed
    pause
    exit /b 1
)
cd ..\..

REM Build Electron app
echo.
echo Building Electron app...
cd desktop_app
call npm run build:win
if errorlevel 1 (
    echo ERROR: Electron build failed
    pause
    exit /b 1
)
cd ..

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo EXE file location: desktop_app\dist\
echo.
pause
