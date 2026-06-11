# ===========================
# MAGIC_PRECHECK_SYSTEM3.ps1
# ===========================
# PURPOSE:
# 1) Pre-check everything needed to understand current SYSTEM3 status (Windows + Cursor + Python + .venv + deps + ports + git + Node).
# 2) Produces a single Proof Bundle folder with logs + JSON summary.
#
# HOW TO RUN (PowerShell, no admin needed):
#   cd C:\Genesis_System3
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\MAGIC_PRECHECK_SYSTEM3.ps1
#
# OUTPUT:
#   C:\Genesis_System3\outputs\proof_bundle\precheck_<timestamp>\

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

function Write-Section($t) {
  Write-Host ""
  Write-Host "============================================================"
  Write-Host $t
  Write-Host "============================================================"
}

function Safe-Exec($cmd, $outFile) {
  try {
    cmd /c $cmd *> $outFile
    return $true
  } catch {
    $_ | Out-File -FilePath $outFile -Append
    return $false
  }
}

$root = (Get-Location).Path
$ts = (Get-Date).ToString("yyyyMMdd_HHmmss")
$outRoot = Join-Path $root "outputs\proof_bundle\precheck_$ts"
New-Item -ItemType Directory -Force -Path $outRoot | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $outRoot "logs") | Out-Null

$summary = [ordered]@{
  root = $root
  timestamp = (Get-Date).ToString("o")
  windows = [ordered]@{}
  cursor = [ordered]@{}
  python = [ordered]@{}
  venv = [ordered]@{}
  pip = [ordered]@{}
  node = [ordered]@{}
  git = [ordered]@{}
  ports = [ordered]@{}
  project = [ordered]@{}
  findings = @()
  recommended_actions = @()
}

Write-Section "SYSTEM3 MAGIC PRECHECK START"

# --- Windows basics ---
Write-Section "Windows / PowerShell"
$winFile = Join-Path $outRoot "logs\windows.txt"
Safe-Exec 'ver' $winFile | Out-Null
Safe-Exec 'whoami' (Join-Path $outRoot "logs\whoami.txt") | Out-Null
Safe-Exec 'powershell -NoProfile -Command "$PSVersionTable | Format-List *"' (Join-Path $outRoot "logs\ps_version.txt") | Out-Null
$summary.windows.username = (whoami)
$summary.windows.ps_version = $PSVersionTable.PSVersion.ToString()

# --- Execution Policy ---
Write-Section "ExecutionPolicy"
$pol = Get-ExecutionPolicy -List | Out-String
$pol | Out-File (Join-Path $outRoot "logs\execution_policy.txt")
$summary.windows.execution_policy = $pol

# --- Cursor / .cursor extension evidence (best-effort) ---
Write-Section "Cursor (best-effort file existence)"
$cursorExtPath = Join-Path $env:USERPROFILE ".cursor\extensions"
$summary.cursor.extensions_path = $cursorExtPath
if (Test-Path $cursorExtPath) {
  Get-ChildItem $cursorExtPath -ErrorAction SilentlyContinue |
    Select-Object Name, LastWriteTime |
    Sort-Object LastWriteTime -Descending |
    Format-Table -AutoSize | Out-String | Out-File (Join-Path $outRoot "logs\cursor_extensions.txt")
  $summary.cursor.extensions_found = $true
} else {
  "Cursor extensions folder not found: $cursorExtPath" | Out-File (Join-Path $outRoot "logs\cursor_extensions.txt")
  $summary.cursor.extensions_found = $false
  $summary.findings += "Cursor extensions folder not found. (This is not always a problem.)"
}

# --- Repo / key files presence ---
Write-Section "Project file presence"
$presence = [ordered]@{
  ".cursorrules" = (Test-Path (Join-Path $root ".cursorrules"))
  "AGENT.md" = (Test-Path (Join-Path $root "AGENT.md"))
  "docs\CURSOR_SETUP.md" = (Test-Path (Join-Path $root "docs\CURSOR_SETUP.md"))
  "requirements_runtime.txt" = (Test-Path (Join-Path $root "requirements_runtime.txt"))
  "pyproject.toml" = (Test-Path (Join-Path $root "pyproject.toml"))
  "package.json" = (Test-Path (Join-Path $root "package.json"))
  "src" = (Test-Path (Join-Path $root "src"))
  ".env" = (Test-Path (Join-Path $root ".env"))
  "config\secrets.env" = (Test-Path (Join-Path $root "config\secrets.env"))
}
$presence | ConvertTo-Json -Depth 5 | Out-File (Join-Path $outRoot "logs\project_presence.json")
$summary.project.presence = $presence

# --- Python discovery ---
Write-Section "Python discovery"
$pyInfoFile = Join-Path $outRoot "logs\python_discovery.txt"
Safe-Exec 'where python' (Join-Path $outRoot "logs\where_python.txt") | Out-Null
Safe-Exec 'where py' (Join-Path $outRoot "logs\where_py.txt") | Out-Null
Safe-Exec 'python --version' (Join-Path $outRoot "logs\python_version_global.txt") | Out-Null
Safe-Exec 'py -0p' (Join-Path $outRoot "logs\py_list.txt") | Out-Null

# --- .venv checks ---
Write-Section ".venv checks"
$venvPy = Join-Path $root ".venv\Scripts\python.exe"
$venvExists = Test-Path $venvPy
$summary.venv.venv_python_path = $venvPy
$summary.venv.exists = $venvExists

if ($venvExists) {
  Safe-Exec "`"$venvPy`" -c `"import sys; print(sys.executable); print(sys.version)`"" (Join-Path $outRoot "logs\venv_python_ok.txt") | Out-Null
  Safe-Exec "`"$venvPy`" -m pip --version" (Join-Path $outRoot "logs\venv_pip_version.txt") | Out-Null
  Safe-Exec "`"$venvPy`" -m pip check" (Join-Path $outRoot "logs\venv_pip_check.txt") | Out-Null
  Safe-Exec "`"$venvPy`" -m pip freeze" (Join-Path $outRoot "logs\venv_pip_freeze.txt") | Out-Null
  $summary.venv.python_ok = $true
} else {
  "Missing .venv interpreter: $venvPy" | Out-File (Join-Path $outRoot "logs\venv_missing.txt")
  $summary.venv.python_ok = $false
  $summary.findings += "Missing .venv. Agent autonomy will be unstable until .venv exists."
  $summary.recommended_actions += "Create venv: py -3.11 -m venv .venv; then upgrade pip."
}

# --- Detect legacy venv references in repo ---
Write-Section "Legacy 'venv\' references scan"
$scanFile = Join-Path $outRoot "logs\scan_venv_refs.txt"
Get-ChildItem $root -Recurse -File -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch "\\.venv\\" -and $_.FullName -notmatch "\\node_modules\\" -and $_.FullName -notmatch "\\outputs\\" } |
  Select-String -Pattern "venv\\Scripts\\python\.exe|\\venv\\|^\s*venv\b" -SimpleMatch -ErrorAction SilentlyContinue |
  Select-Object Path, LineNumber, Line |
  Sort-Object Path, LineNumber |
  Format-Table -AutoSize | Out-String | Out-File $scanFile

$venvRefCount = (Get-Content $scanFile | Measure-Object -Line).Lines
$summary.project.legacy_venv_ref_log = "logs\scan_venv_refs.txt"

# --- Node / npm (best effort) ---
Write-Section "Node / npm"
Safe-Exec 'where node' (Join-Path $outRoot "logs\where_node.txt") | Out-Null
Safe-Exec 'node --version' (Join-Path $outRoot "logs\node_version.txt") | Out-Null
Safe-Exec 'where npm' (Join-Path $outRoot "logs\where_npm.txt") | Out-Null
Safe-Exec 'npm --version' (Join-Path $outRoot "logs\npm_version.txt") | Out-Null

# --- Git ---
Write-Section "Git"
Safe-Exec 'where git' (Join-Path $outRoot "logs\where_git.txt") | Out-Null
Safe-Exec 'git --version' (Join-Path $outRoot "logs\git_version.txt") | Out-Null
Safe-Exec 'git status -sb' (Join-Path $outRoot "logs\git_status.txt") | Out-Null
Safe-Exec 'git config --list' (Join-Path $outRoot "logs\git_config_list.txt") | Out-Null

# --- Ports ---
Write-Section "Ports check (8501, 8080, 8000, 5000)"
$portsToCheck = @(8501,8080,8000,5000)
$portLog = Join-Path $outRoot "logs\ports.txt"
foreach ($p in $portsToCheck) {
  "----- PORT $p -----" | Out-File $portLog -Append
  cmd /c "netstat -ano | findstr :$p" | Out-File $portLog -Append
}
$summary.ports.checked = $portsToCheck

# --- Optional: run repo-specific verify script if present ---
Write-Section "Repo verify script (if present)"
$verifyPy = Join-Path $root "tools\verify_cursor_agent_bugs.py"
if ($venvExists -and (Test-Path $verifyPy)) {
  Safe-Exec "`"$venvPy`" `"$verifyPy`"" (Join-Path $outRoot "logs\verify_cursor_agent_bugs.txt") | Out-Null
  $summary.project.verify_script_ran = $true
} else {
  "Skipped: missing .venv or tools\verify_cursor_agent_bugs.py" | Out-File (Join-Path $outRoot "logs\verify_cursor_agent_bugs.txt")
  $summary.project.verify_script_ran = $false
}

# --- Basic env file detection summary ---
Write-Section "Secrets (.env / config\secrets.env) presence"
$summary.project.secrets_present = ($presence[".env"] -or $presence["config\secrets.env"])
if (-not $summary.project.secrets_present) {
  $summary.findings += "No .env / config\secrets.env found. Broker login autonomy will not work until you create one."
  $summary.recommended_actions += "Create .env with ANGEL_CLIENT_CODE, ANGEL_PASSWORD, ANGEL_API_KEY, ANGEL_TOTP_SEED."
}

# --- Build final summary + "PASS/WARN/FAIL" ---
Write-Section "Final verdict"
$verdict = "PASS"
if (-not $venvExists) { $verdict = "FAIL" }
elseif (-not $summary.project.secrets_present) { $verdict = "WARN" }

$summary.verdict = $verdict

# Add venv ref warning if scan contains matches (best-effort heuristic)
if ((Get-Item $scanFile).Length -gt 40) {
  $summary.findings += "Legacy venv references likely exist (see logs\scan_venv_refs.txt)."
  $summary.recommended_actions += "Standardize all scripts to .venv paths (replace venv\ with .venv\)."
  if ($verdict -eq "PASS") { $verdict = "WARN"; $summary.verdict = $verdict }
}

$summary | ConvertTo-Json -Depth 8 | Out-File (Join-Path $outRoot "SUMMARY.json")

Write-Host "VERDICT: $verdict"
Write-Host "Proof bundle created at:"
Write-Host "  $outRoot"
Write-Host "Key outputs:"
Write-Host "  $outRoot\SUMMARY.json"
Write-Host "  $outRoot\logs\venv_pip_check.txt"
Write-Host "  $outRoot\logs\scan_venv_refs.txt"
Write-Host "  $outRoot\logs\ports.txt"

Write-Section "SYSTEM3 MAGIC PRECHECK END"