@echo off
setlocal
cd /d "%~dp0.."
echo [INFO] Dashboard browser proof - Playwright
if not exist "tools\playwright-setup\node_modules\@playwright\test" (
  echo [INFO] Installing Playwright test runner...
  pushd tools\playwright-setup
  call npm install
  popd
)
echo [INFO] Installing Chromium...
set NODE_PATH=%CD%\tools\playwright-setup\node_modules
call npx --prefix tools\playwright-setup playwright install chromium
echo [INFO] Running dashboard proof tests...
set DASHBOARD_URL=https://genesis-system3-backend.onrender.com/ui
call npx --prefix tools\playwright-setup playwright test
echo [DONE] Reports:
echo   reports\latest\dashboard_browser_proof\summary.md
echo   reports\latest\dashboard_browser_proof\summary.json
endlocal
