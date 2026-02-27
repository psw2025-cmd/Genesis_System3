@echo off
echo ============================================
echo CLOSING SYSTEM3 ULTRA AND PREPARING INSTALL
echo ============================================
echo.

echo [1/4] Closing System3 Ultra processes...
taskkill /F /IM "System3 Ultra.exe" 2>nul
if errorlevel 1 (
    echo   No System3 Ultra.exe process found
) else (
    echo   System3 Ultra.exe closed
)

echo.
echo [2/4] Closing Electron processes...
taskkill /F /IM electron.exe 2>nul
if errorlevel 1 (
    echo   No electron.exe process found
) else (
    echo   electron.exe closed
)

echo.
echo [3/4] Closing Python backend processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
    taskkill /F /PID %%a 2>nul
    if not errorlevel 1 (
        echo   Closed process on port 8000 (PID: %%a)
    )
)

echo.
echo [4/4] Waiting 3 seconds for processes to fully close...
timeout /t 3 /nobreak >nul

echo.
echo ============================================
echo READY FOR INSTALLATION
echo ============================================
echo.
echo You can now:
echo 1. Click Retry in the installer window
echo 2. Or run the installer again: desktop_app\dist\System3 Ultra Setup 1.0.0.exe
echo.
pause
