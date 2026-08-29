# Claude CLI — max access bootstrap (revised after probe)

Probe result: Claude CLI is **already on PATH**. Only shared gap with Cursor is **GCP ADC / Cloud Run describe**.

## Always start here

```powershell
cd C:\Users\ADMIN\Genesis_System3\Genesis_System3
```

## Grant the one missing piece (same as Cursor)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\reports\latest\access_capability\ACCESS_GRANT_REVISE.ps1
```

## Then start Claude with full tool surface

```powershell
cd C:\Users\ADMIN\Genesis_System3\Genesis_System3
git fetch origin
claude
```

Tell Claude on first message:

> Use primary clone only. Cloud+GitHub are truth. Run `py -3 scripts/system3_access_capability_probe.py` if unsure about access. Never use C:\System3\Genesis_System3.

## Already available (do not reinstall)

- git, gh (logged in as psw2025-cmd), gcloud CLI, Gmail API files+venv, live Cloud Run HTTP, Claude CLI
