@echo off
REM One-shot: start local stack + run local CI (full laptop workflow)
cd /d "%~dp0.."
echo === Step 1: Start local stack ===
call tools\run_local_stack.bat --no-open --no-pause
echo.
echo === Step 2: Run local CI (GitHub Actions replacement) ===
timeout /t 5 /nobreak >nul
call tools\run_local_ci.bat --fast
set RC=%ERRORLEVEL%
echo.
echo === Done ===
echo   Dashboard: http://127.0.0.1:8000/ui
echo   CI report: reports\latest\local_ci\summary.md
exit /b %RC%
