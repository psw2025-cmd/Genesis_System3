@echo off
echo ============================================
echo CLOSING SYSTEM3 ULTRA FOR INSTALLATION
echo ============================================
echo.

echo Closing all System3 Ultra processes...
taskkill /F /IM "System3 Ultra.exe" >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] System3 Ultra.exe closed
) else (
    echo [INFO] No System3 Ultra.exe process found
)

echo.
echo Closing Python backend processes on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process %%a...
    taskkill /F /PID %%a >nul 2>&1
    if %errorlevel% == 0 (
        echo [OK] Process %%a closed
    )
)

echo.
echo Closing any remaining Python processes with uvicorn...
taskkill /F /FI "WINDOWTITLE eq *uvicorn*" >nul 2>&1
wmic process where "commandline like '%%uvicorn%%'" delete >nul 2>&1

echo.
echo Waiting 2 seconds for processes to fully close...
timeout /t 2 /nobreak >nul

echo.
echo ============================================
echo VERIFICATION
echo ============================================
echo.

tasklist | findstr /i "System3 Ultra.exe" >nul
if %errorlevel% == 0 (
    echo [WARNING] System3 Ultra.exe is still running!
    echo Please close it manually from Task Manager
) else (
    echo [OK] System3 Ultra.exe is not running
)

netstat -aon | findstr :8000 | findstr LISTENING >nul
if %errorlevel% == 0 (
    echo [WARNING] Port 8000 is still in use!
    echo Check Task Manager for Python processes
) else (
    echo [OK] Port 8000 is free
)

echo.
echo ============================================
echo READY FOR INSTALLATION
echo ============================================
echo.
echo You can now run the installer:
echo desktop_app\dist\System3 Ultra Setup 1.0.0.exe
echo.
pause
