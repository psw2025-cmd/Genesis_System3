Set-Location 'C:\Users\ADMIN\Genesis_System3\Genesis_System3'
while ($true) {
  try { & 'C:\Python310\python.exe' 'C:\Users\ADMIN\Genesis_System3\Genesis_System3\scripts\system3_mri_gmail_scheduler_watch.py' } catch {  | Out-File 'C:\Users\ADMIN\Genesis_System3\Genesis_System3\reports\latest\mri_watch\_loop_err.txt' -Append }
  Start-Sleep -Seconds 300
}
