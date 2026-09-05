# Genesis System3 — GCP → Local Laptop Eradication Tracker

Authority: `docs/RUHI_RULE_V2.md` RHUI_RULE_V2.3

Goal: continuously discover, replace, remove and verify every Genesis System3 GCP dependency without breaking required PAPER/analyzer capability.

| Item | Location | Old GCP role | Required capability | Local replacement | State | Proof | Owner/blocker |
|---|---|---|---|---|---|---|---|
| Cloud Run runtime/service references | repo/workflows/docs/runtime metadata | web runtime | dashboard/API process | Windows local service/process supervisor | DISCOVERED | historical GCP references exist | controller/local agent |
| Cloud Run jobs | workflows/scripts/docs | scheduled/background jobs | background execution | Windows Task Scheduler/local supervisor | DISCOVERED | migration verification required | local agent |
| Cloud Scheduler | workflows/docs/config | timed triggers | scheduled automation | Windows Task Scheduler | DISCOVERED | migration verification required | local agent |
| Secret Manager | broker/config/docs | broker/runtime secrets | secure credentials/token lifecycle | secure local secret store/env mapping | DISCOVERED | migration verification required | local agent; never expose values |
| Cloud databases/storage | source/config/docs | state/history/artifacts | durable state + backups | local DB/files + Drive backup evidence | DISCOVERED | dependency inventory required | controller/local agent |
| GCP logging/monitoring | workflows/docs/source | logs/health/alerts | diagnostics/watchdog | local logs/watchdog + Drive evidence | DISCOVERED | recent Drive logs exist | local agent |
| GCP deploy/WIF workflows | `.github/workflows/**` | deployment | CI validation only | GitHub CI without GCP deploy | DISCOVERED | PR #446 removed known triggers; full search still required | controller |
| Cloud Run URLs/deploy metadata | UI/API/docs/tests | production identity/proof | local runtime identity | localhost/LAN runtime identity + main SHA | DISCOVERED | replacement audit required | controller/local agent |
| Residual GCP billing/resources | external GCP account | cost/resources | none after migration | delete/disable externally | EXTERNAL_CLEANUP_REQUIRED | Gmail budget/decommission alerts show teardown not yet independently proven | owner-only external teardown if tools unavailable |

## Mandatory recurring check

Every material controller cycle must update this tracker when a new GCP dependency/reference is found, when a local replacement is proven, or when a residual item is removed. `GCP_EXIT_COMPLETE` is forbidden until RHUI_RULE_V2.3 section 13 is fully proven.
