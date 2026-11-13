# Dhan duplicate-issuer MRI — operator run

Run from an **Administrator PowerShell** opened in the Genesis System3 repository:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\system3_dhan_issuer_mri_bundle.ps1
```

If the script is located in a clean worktree but the real operator checkout is elsewhere, explicitly point it at the checkout that must be audited:

```powershell
powershell -ExecutionPolicy Bypass -File C:\System3\Genesis_System3\.worktrees\broker-token-permanent\scripts\system3_dhan_issuer_mri_bundle.ps1 -RepoPath C:\System3\Genesis_System3
```

The collector is read-only. It inventories local processes and scheduled tasks, current Git/GitHub workflow activity, GCP Cloud Run jobs/services/schedulers, Secret Manager version metadata and IAM identities, and sanitized production APIs. It never requests or prints a token, PIN, TOTP seed, QR code, account identifier, holdings, funds, positions, or order data.

When it completes, share only the two paths printed as:

```text
MRI_JSON=...\issuer_mri.json
SHARE_SUMMARY=...\SHARE_THIS_SUMMARY.md
```

Do **not** share `.env`, browser screenshots containing credentials, Secret Manager payloads, authenticator QR codes, PINs, TOTP codes, or access tokens.

If `LOCAL_PROCESS_INVENTORY_UNAVAILABLE` or `LOCAL_SCHEDULED_TASK_INVENTORY_UNAVAILABLE` appears, close the current shell, reopen PowerShell with **Run as administrator**, and rerun the same command. A non-zero exit code means anomalies were found and the report was still generated successfully. `-RepoPath` must point to the actual laptop checkout, not merely a clean helper worktree.
