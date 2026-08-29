# Register Windows Task — System3 MRI 5-min watch

**Do not** add GitHub Actions `schedule:` (policy ban).  
Use local Task Scheduler or `python scripts/system3_mri_gmail_scheduler_watch.py --loop`.

## One-shot register (Admin PowerShell optional)

```powershell
cd C:\Users\ADMIN\Genesis_System3\Genesis_System3
$py = "C:\Python310\python.exe"
if (-not (Test-Path $py)) { $py = (Get-Command python).Source }
$tr = "`"$py`" `"$PWD\scripts\system3_mri_gmail_scheduler_watch.py`""
schtasks /Create /TN "System3_MRI_Gmail_Scheduler_Watch" /SC MINUTE /MO 5 /TR $tr /F
schtasks /Query /TN "System3_MRI_Gmail_Scheduler_Watch"
```

## Foreground loop (session-bound)

```powershell
cd C:\Users\ADMIN\Genesis_System3\Genesis_System3
python scripts\system3_mri_gmail_scheduler_watch.py --loop --interval-sec 300
```

## Outputs

- `reports/latest/mri_watch/LATEST.json`
- `reports/latest/mri_watch/TICK_LOG.jsonl`
- `reports/latest/mri_watch/CHECKLIST.md`

## GCP alternative

Cloud Scheduler → GitHub `workflow_dispatch` on an existing workflow — never `on.schedule` in Actions YAML.
