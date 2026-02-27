@echo off
echo ============================================
echo STARTING BACKEND FOR TESTING
echo ============================================
echo.

echo Starting backend from development directory...
echo This will allow the dashboard to work while testing
echo.

cd /d C:\Genesis_System3

echo Starting uvicorn...
start "System3 Ultra Backend" cmd /k "python -m uvicorn dashboard.backend.app:app --host 127.0.0.1 --port 8000"

echo.
echo Backend starting in new window...
echo Waiting 5 seconds for startup...
timeout /t 5 /nobreak >nul

echo.
echo Checking if backend is running...
python -c "import requests; r = requests.get('http://localhost:8000/api/health', timeout=3); print('Backend status:', r.status_code); print('Response:', r.json() if r.status_code == 200 else 'Not responding')" 2>nul

if errorlevel 1 (
    echo Backend may still be starting...
    echo Check the backend window for errors
) else (
    echo.
    echo [OK] Backend should be running now!
    echo.
    echo Next steps:
    echo 1. Refresh the dashboard in the app
    echo 2. Or open: http://localhost:8000/api/health in browser
    echo 3. Dashboard should now show data
)

echo.
pause
