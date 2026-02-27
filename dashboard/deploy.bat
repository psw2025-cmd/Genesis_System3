@echo off
echo ========================================
echo Genesis System3 Dashboard - Deploy
echo ========================================
echo.

cd /d %~dp0\dashboard

echo Starting HTTP server on port 8080...
echo.
echo Dashboard will be available at:
echo   http://localhost:8080
echo.
echo Press Ctrl+C to stop the server
echo.

python -m http.server 8080

pause
