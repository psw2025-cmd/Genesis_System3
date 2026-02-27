<#
.SYNOPSIS
  Interactive helper to register a scheduled task that runs the system inspector.

USAGE
  Run this script from PowerShell to create a scheduled task that will periodically
  run `system3_full_inspector.py` and save logs under `logs\inspector`.

SECURITY
  This script only performs actions after explicit prompts. It does NOT transmit
  any data off your machine. You remain in control.
#>

Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir "..")

Write-Host "Project root: $projectRoot"

# Ensure logs directory exists
$logDir = Join-Path $projectRoot 'logs\inspector'
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    Write-Host "Created log directory: $logDir"
} else {
    Write-Host "Log directory exists: $logDir"
}

# Check for python
$pyCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pyCmd) {
    Write-Warning "Python not found in PATH. The scheduled task will likely fail until Python is accessible."
    Write-Host "You can install Python or add it to PATH. Press Enter to continue anyway or Ctrl+C to abort."
    Read-Host
}

# Ensure wrapper exists
$wrapper = Join-Path $scriptDir 'run_inspector_wrapper.ps1'
if (!(Test-Path $wrapper)) {
    Write-Warning "Wrapper script not found: $wrapper"
    Write-Host "Please ensure `run_inspector_wrapper.ps1` exists in the same folder as this script."
    exit 1
}

# Ask to create scheduled task
$create = Read-Host "Create scheduled task to run inspector every 15 minutes? (Y/N)"
if ($create -notin @('Y','y')) {
    Write-Host "Aborting: no scheduled task created."
    exit 0
}

try {
    $taskName = 'System3Inspector'
    # Action runs PowerShell in no-profile mode to execute the wrapper
    $action = New-ScheduledTaskAction -Execute 'PowerShell.exe' -Argument "-NoProfile -WindowStyle Hidden -File `"$wrapper`""
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Days 365)
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Description 'Run system3_full_inspector periodically and save logs to logs\inspector' -User $env:UserName -RunLevel Limited -ErrorAction Stop
    Write-Host "Scheduled task '$taskName' registered. You can manage it via Task Scheduler."
} catch {
    Write-Error "Failed to register scheduled task: $_"
}

Write-Host "Done. The inspector will run under your user account as scheduled."
