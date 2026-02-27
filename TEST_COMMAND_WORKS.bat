@echo off
REM ====================================================================
REM TEST COMMAND WORKS - Verify the command executes
REM ====================================================================

title Test Command Works

cd /d "%~dp0"

echo.
echo Testing if command will execute in new window...
echo.

REM Test with a simple command first
start "Test Window" cmd /k "cd /d %~dp0 && echo TEST OUTPUT - If you see this, command works! && echo. && echo Testing Python... && python --version && echo. && echo Command test complete && pause"

echo.
echo Test window opened. Check if you see output.
echo.
pause
