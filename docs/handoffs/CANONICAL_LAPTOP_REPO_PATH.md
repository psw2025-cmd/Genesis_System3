# Cloud + GitHub temporal truth

**Updated:** 2026-08-25 (re-verify)

## Authority order

1. GitHub `main` — code truth  
2. Live Cloud Run `/api/deploy_info` — serving truth  
3. Laptop — working copy only (never final truth)

## Mandatory before local work

1. `git fetch origin` in primary clone  
2. Compare GitHub/`origin/main` vs laptop HEAD vs live serving SHA  
3. Never edit `C:\System3\Genesis_System3` or other banned paths  

Primary clone only: `C:\Users\ADMIN\Genesis_System3\Genesis_System3`

## Latest re-verify snapshot

See `reports/latest/repo_path_audit/cloud_github_vs_laptop.json`.

Rule: `.cursor/rules/canonical-laptop-repo-path.mdc` (alwaysApply)
