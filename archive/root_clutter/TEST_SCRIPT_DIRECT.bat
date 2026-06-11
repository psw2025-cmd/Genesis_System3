@echo off
cd /d C:\Genesis_System3
call venv\Scripts\activate.bat
echo Testing script execution...
echo.
python -u scripts\smart_live_chain_runner.py --refresh 5 --market-check 30 --no-websocket
echo.
echo Script finished with exit code: %ERRORLEVEL%
pause
