@echo off
setlocal enabledelayedexpansion
title Safe C: Drive Cleanup - Temp and cache only

REM ============================================================
REM SAFE C: CLEANUP - Removes only temporary and cache files
REM that are safe to delete. Does NOT touch Windows system files,
REM Program Files, or any critical data.
REM ============================================================

echo.
echo ============================================================
echo   Safe C: Drive Cleanup (temp, caches, Python/npm junk)
echo ============================================================
echo.
echo This will remove ONLY:
echo   - Your user TEMP folders
echo   - Pip cache (downloaded package cache)
echo   - NPM cache
echo   - Python __pycache__, .pyc, .pyo in this project
echo   - Pytest/mypy cache in this project
echo   - Windows Temp folder (if run as Administrator)
echo   - Recycle Bin (optional)
echo.
echo It will NOT touch: Windows, Program Files, your documents,
echo   or any application data outside temp/cache.
echo.
set /p confirm="Proceed? (Y/N): "
if /i not "%confirm%"=="Y" (
  echo Cancelled.
  exit /b 0
)

set "freed=0"

REM --- 1. User TEMP and TMP
echo.
echo [1/7] Cleaning user TEMP folders...
if exist "%TEMP%" (
  for /f "tokens=3" %%a in ('dir "%TEMP%" /a /-c 2^>nul ^| find "File(s)"') do set "freed=%%a"
  rd /s /q "%TEMP%" 2>nul
  mkdir "%TEMP%" 2>nul
  echo   Done: %TEMP%
)
if exist "%TMP%" if not "%TMP%"=="%TEMP%" (
  rd /s /q "%TMP%" 2>nul
  mkdir "%TMP%" 2>nul
  echo   Done: %TMP%
)

REM --- 2. Pip cache
echo.
echo [2/7] Cleaning pip cache...
pip cache purge 2>nul
if errorlevel 1 (
  if exist "%LOCALAPPDATA%\pip\cache" (
    rd /s /q "%LOCALAPPDATA%\pip\cache" 2>nul
    echo   Done: pip cache folder removed
  ) else echo   Skipped: pip not in PATH or no cache
) else echo   Done: pip cache purged

REM --- 3. NPM cache
echo.
echo [3/7] Cleaning npm cache...
npm cache clean --force 2>nul
if errorlevel 1 (echo   Skipped: npm not in PATH) else echo   Done: npm cache cleaned

REM --- 4. Python bytecode in THIS project only
echo.
echo [4/7] Cleaning Python cache in this project...
cd /d "%~dp0"
for /d /r %%d in (__pycache__) do (
  if exist "%%d" rd /s /q "%%d" 2>nul
)
del /s /q "*.pyc" "*.pyo" 2>nul
for /d /r %%d in (.pytest_cache .mypy_cache) do (
  if exist "%%d" rd /s /q "%%d" 2>nul
)
echo   Done: __pycache__, .pyc, .pyo, .pytest_cache, .mypy_cache

REM --- 5. Optional: Python cache in user folder (common dev locations)
echo.
echo [5/7] Cleaning Python cache in user AppData...
if exist "%USERPROFILE%\.cache\pip" rd /s /q "%USERPROFILE%\.cache\pip" 2>nul
if exist "%LOCALAPPDATA%\pytest-cache" rd /s /q "%LOCALAPPDATA%\pytest-cache" 2>nul
echo   Done

REM --- 6. Windows Temp (only if we have admin rights)
echo.
echo [6/7] Cleaning Windows Temp folder...
if exist "C:\Windows\Temp" (
  net session >nul 2>&1
  if errorlevel 1 (
    echo   Skipped: Run as Administrator to clean C:\Windows\Temp
  ) else (
    del /f /s /q "C:\Windows\Temp\*.*" 2>nul
    for /d %%d in ("C:\Windows\Temp\*") do rd /s /q "%%d" 2>nul
    echo   Done: C:\Windows\Temp
  )
) else echo   Skipped: C:\Windows\Temp not found

REM --- 7. Recycle Bin (optional)
echo.
set /p bin="Empty Recycle Bin? (Y/N): "
if /i "!bin!"=="Y" (
  echo [7/7] Emptying Recycle Bin...
  rd /s /q "%SystemDrive%\$Recycle.bin" 2>nul
  echo   Done (may need admin for full clean)
) else (
  echo [7/7] Recycle Bin: skipped
)

echo.
echo ============================================================
echo   Safe cleanup finished.
echo   To free more space: run as Administrator and use
echo   Windows Disk Cleanup (cleanmgr) or uninstall unused apps.
echo ============================================================
endlocal
exit /b 0
