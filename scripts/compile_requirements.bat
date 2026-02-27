@echo off
REM Regenerate requirements_runtime.txt and requirements-dev.txt from .in sources.
REM Run from repo root: scripts\compile_requirements.bat
REM Prefer .venv if present; otherwise uses system pip.

cd /d "%~dp0\.."
if exist .venv\Scripts\python.exe (
  set PY=.venv\Scripts\python.exe
  set PIP=.venv\Scripts\pip.exe
  set PIPCOMPILE=.venv\Scripts\pip-compile.exe
) else (
  set PY=python
  set PIP=pip
  set PIPCOMPILE=pip-compile
)

echo Installing pip-tools...
"%PY%" -m pip install pip-tools -q
if errorlevel 1 (echo ERROR: pip-tools install failed & exit /b 1)

echo Compiling requirements_runtime.in -> requirements_runtime.txt...
"%PIPCOMPILE%" requirements_runtime.in -o requirements_runtime.txt
if errorlevel 1 (echo ERROR: pip-compile runtime failed & exit /b 1)

echo Compiling requirements-dev.in -> requirements-dev.txt...
"%PIPCOMPILE%" requirements-dev.in -o requirements-dev.txt
if errorlevel 1 (echo ERROR: pip-compile dev failed & exit /b 1)

echo Done. Install with: pip install -r requirements_runtime.txt && pip install -r requirements-dev.txt
exit /b 0
