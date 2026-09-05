# RHUI V2.3 GCP Eradication Acceptance

Fail closed: `GCP_EXIT_INCOMPLETE` until every item is proven.

- [ ] No active GCP runtime/deploy/scheduler/token/state dependency in current main.
- [ ] No GitHub workflow can recreate/deploy Genesis System3 to GCP.
- [ ] Broker secrets/token lifecycle works securely on authorized laptop.
- [ ] Local scheduler/background workers survive reboot/restart and are observable.
- [ ] Local DB/state/history persistence and backup/restore proven.
- [ ] Local logging/watchdog/alerts proven and recent evidence reaches Drive.
- [ ] All 22 tabs semantically proven from current-main local runtime.
- [ ] Broker/API + four required option chains proven same-session when applicable.
- [ ] Signal -> PAPER -> persistence -> UI -> P&L/reconciliation lifecycle proven.
- [ ] ML/risk/system gates are truthful; no placeholder/false-green acceptance.
- [ ] Cloud URLs/revision/secret metadata removed from current acceptance logic.
- [ ] Historical GCP docs/artifacts clearly marked historical or retired.
- [ ] Residual GCP account resources/billing independently proven removed or tracked as owner-only external cleanup.
- [ ] Issue #188 and active PRs contain no operative contradictory cloud-authority instruction.

Safety invariant: LIVE=false; orders=false.
