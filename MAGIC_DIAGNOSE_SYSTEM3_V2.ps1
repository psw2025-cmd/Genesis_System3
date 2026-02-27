$ErrorActionPreference = "SilentlyContinue"

$ROOT = "C:\Genesis_System3"
$OUT  = Join-Path $ROOT "MAGIC_OUTPUT_V2"
$ZIP  = Join-Path $ROOT "MAGIC_OUTPUT_V2.zip"
$APP  = Join-Path $env:LOCALAPPDATA "Programs\System3 Ultra"
$RES  = Join-Path $APP "resources"
$ASAR = Join-Path $RES "app.asar"

Remove-Item $OUT -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item $ZIP -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $OUT | Out-Null

"=== SYSTEM3 MAGIC DIAGNOSE V2 ===" | Out-File (Join-Path $OUT "status.txt") -Encoding utf8
("Time: " + (Get-Date)) | Out-File (Join-Path $OUT "status.txt") -Append

# 1) Capture any running processes (should be none after you stopped)
"--- PROCESSES (before) ---" | Out-File (Join-Path $OUT "status.txt") -Append
Get-Process "System3 Ultra" -ErrorAction SilentlyContinue |
  Select Id,StartTime,Path | Format-Table -AutoSize |
  Out-File (Join-Path $OUT "processes_before.txt")

# 2) Visible windows listing (non-generic delegate)
Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;

public static class WinEnum {
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

  [DllImport("user32.dll")]
  public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

  [DllImport("user32.dll", CharSet=CharSet.Unicode)]
  public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

  [DllImport("user32.dll")]
  public static extern bool IsWindowVisible(IntPtr hWnd);
}
"@

$winOut = New-Object System.Collections.Generic.List[string]
[WinEnum]::EnumWindows({ param($h,$l)
  if ([WinEnum]::IsWindowVisible($h)) {
    $sb = New-Object System.Text.StringBuilder 512
    [void][WinEnum]::GetWindowText($h,$sb,$sb.Capacity)
    $t = $sb.ToString()
    if ($t.Trim().Length -gt 0) { $winOut.Add($t) }
  }
  return $true
}, [IntPtr]::Zero) | Out-Null

$winOut | Sort-Object | Out-File (Join-Path $OUT "visible_windows.txt") -Encoding utf8

# 3) Installed app tree (top-level + resources)
if (Test-Path $APP) {
  Get-ChildItem $APP | Select Name,Length,LastWriteTime | Format-Table -AutoSize |
    Out-File (Join-Path $OUT "installed_app_listing.txt")
}
if (Test-Path $RES) {
  Get-ChildItem $RES | Select Name,Length,LastWriteTime | Format-Table -AutoSize |
    Out-File (Join-Path $OUT "installed_resources_listing.txt")

  Get-ChildItem $RES -Recurse -ErrorAction SilentlyContinue |
    Select FullName,Length | Out-File (Join-Path $OUT "resources_tree.txt") -Encoding utf8
}

# 4) Extract app.asar (if possible)
if (Test-Path $ASAR) {
  "Extracting app.asar ..." | Out-File (Join-Path $OUT "status.txt") -Append
  $asarOut = Join-Path $OUT "app_asar_extracted"
  New-Item -ItemType Directory -Force -Path $asarOut | Out-Null
  cmd /c "cd /d `"$OUT`" && npx asar extract `"$ASAR`" `"$asarOut`"" 1> (Join-Path $OUT "asar_extract_stdout.txt") 2> (Join-Path $OUT "asar_extract_stderr.txt")
  Get-ChildItem $asarOut -Recurse -Filter "main.js" -ErrorAction SilentlyContinue |
    Copy-Item -Destination (Join-Path $OUT "main.js.from_asar") -Force -ErrorAction SilentlyContinue
}

# 5) Copy project configs if exist
$cfgDir = Join-Path $OUT "project_configs"
New-Item -ItemType Directory -Force -Path $cfgDir | Out-Null
$maybe = @(
  "$ROOT\desktop_app\main.js",
  "$ROOT\desktop_app\package.json",
  "$ROOT\dashboard\frontend\package.json",
  "$ROOT\dashboard\backend\requirements.txt"
)
foreach ($f in $maybe) { if (Test-Path $f) { Copy-Item $f $cfgDir -Force | Out-Null } }

# 6) Copy logs safely (skip locked files)
$logsSrc = Join-Path $ROOT "logs"
$logsDst = Join-Path $OUT "logs"
if (Test-Path $logsSrc) {
  New-Item -ItemType Directory -Force -Path $logsDst | Out-Null
  # Robocopy skips locked files automatically; /ZB uses backup mode if possible
  cmd /c "robocopy `"$logsSrc`" `"$logsDst`" /E /R:1 /W:1 /ZB /NFL /NDL /NP /NJH /NJS /XF *.lock" 1> (Join-Path $OUT "robocopy_logs.txt") 2>&1
}

# 7) ZIP safely (prefer 7z if available)
$sevenZip = @(
  "C:\Program Files\7-Zip\7z.exe",
  "C:\Program Files (x86)\7-Zip\7z.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($sevenZip) {
  cmd /c "`"$sevenZip`" a -tzip `"$ZIP`" `"$OUT\*`"" 1> (Join-Path $OUT "zip_stdout.txt") 2> (Join-Path $OUT "zip_stderr.txt")
} else {
  # Fallback: zip without failing on locked reads (best-effort)
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  try {
    [System.IO.Compression.ZipFile]::CreateFromDirectory($OUT, $ZIP)
  } catch {
    $_ | Out-File (Join-Path $OUT "zip_error.txt") -Encoding utf8
  }
}

"ZIP_PATH=$ZIP" | Out-File (Join-Path $OUT "status.txt") -Append
Write-Host "DONE -> $ZIP"
