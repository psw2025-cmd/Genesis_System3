@echo off
echo ============================================
echo FIXING AND TESTING SYSTEM3 ULTRA APP
echo ============================================
echo.

echo [1/5] Closing any running instances...
taskkill /F /IM "System3 Ultra.exe" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [2/5] Rebuilding installer with fixes...
cd desktop_app
call npm run build:win
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
cd ..

echo.
echo [3/5] Running QC audit...
python comprehensive_qc_audit.py
if errorlevel 1 (
    echo WARNING: QC audit found issues
) else (
    echo QC audit passed
)

echo.
echo [4/5] Installer ready: desktop_app\dist\System3 Ultra Setup 1.0.0.exe
echo.
echo Next steps:
echo 1. Uninstall old version (if installed)
echo 2. Run the new installer
echo 3. Launch the app
echo 4. Check DevTools (Ctrl+Shift+I) for backend logs
echo 5. Verify backend starts: http://localhost:8000/api/health
echo 6. Run validation: python production_grade_validation.py
echo.
pause
