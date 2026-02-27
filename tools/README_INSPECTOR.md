# System3 Inspector Tools

Files added under `tools/` to help you enable safe local monitoring and periodic inspection of the project.

- `create_inspector_task.ps1` — Interactive helper to register a Windows Scheduled Task that runs the inspector every 15 minutes. Prompts before creating the task. Does not run anything by itself.
- `run_inspector_wrapper.ps1` — Task wrapper that runs `system3_full_inspector.py` and saves stdout/stderr to `logs/inspector/inspector_YYYYMMDD_HHMMSS.log`.
- `enable_transcript_snippet.ps1` — Interactive script that appends a PowerShell profile snippet to automatically start session transcripts to `logs/inspector/`. Prompts and backs up your profile before modifying it.

Security & privacy
- All operations are local and require explicit prompts. Nothing is uploaded automatically.
- Transcripts capture everything typed and printed in PowerShell sessions — do not enable if you will type secrets (passwords, API keys) that you do not want stored.

How to use (recommended flow)
1. Open a PowerShell window as your normal user and inspect the helper scripts (they are prompt-driven):
   ```powershell
   notepad .\tools\create_inspector_task.ps1
   notepad .\tools\run_inspector_wrapper.ps1
   notepad .\tools\enable_transcript_snippet.ps1
   ```
2. (Optional) Enable transcripts by running the snippet script and answering Y when asked:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\enable_transcript_snippet.ps1
   ```
3. Register the scheduled task (prompts will ask for confirmation):
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\create_inspector_task.ps1
   ```
4. You can test a single manual run and capture output to logs:
   ```powershell
   $ts = (Get-Date).ToString('yyyyMMdd_HHmmss')
   python .\system3_full_inspector.py *> .\logs\inspector\inspector_$ts.log
   ```

Managing the scheduled task
- Open Task Scheduler and look for task `System3Inspector` to disable or delete it.

If you'd like, I can also create a small helper that prints the latest logs or upload selected logs for analysis (only with your explicit consent).
