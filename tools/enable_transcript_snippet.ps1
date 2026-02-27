<#
  Interactive script which appends a safe PowerShell transcript snippet to your $PROFILE.
  Prompts before making any change and writes a backup of your profile first.
#>
Set-StrictMode -Version Latest

Write-Host "This will add an auto-transcript snippet to your PowerShell profile (local only)."
Write-Host "Transcripts capture everything typed and printed in the shell session. Do NOT enable if you'll enter secrets."

$confirm = Read-Host "Append transcript start to your PowerShell profile? (Y/N)"
if ($confirm -notin @('Y','y')) { Write-Host "Aborted by user."; exit 0 }

if (!(Test-Path -Path $PROFILE)) { New-Item -Path $PROFILE -ItemType File -Force | Out-Null }

$profileText = Get-Content -Path $PROFILE -Raw -ErrorAction SilentlyContinue
$backup = "$PROFILE.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item -Path $PROFILE -Destination $backup -Force
Write-Host "Profile backed up to: $backup"

$snippet = @'
# Start a per-session transcript for System3 (local only)
try {
  $root = "C:\Genesis_System3"
  $logdir = Join-Path $root "logs\inspector"
  if (!(Test-Path $logdir)) { New-Item -ItemType Directory -Path $logdir -Force | Out-Null }
  $ts = (Get-Date).ToString('yyyyMMdd_HHmmss')
  $transcriptFile = Join-Path $logdir "transcript_$ts.txt"
  Start-Transcript -Path $transcriptFile -ErrorAction SilentlyContinue
} catch {
  Write-Verbose "Transcript start failed: $_"
}
'@

Add-Content -Path $PROFILE -Value "`n$snippet`n"
Write-Host "Snippet appended to $PROFILE"
Write-Host "You must restart PowerShell to begin auto-transcripts. Use Stop-Transcript to stop a running one."
