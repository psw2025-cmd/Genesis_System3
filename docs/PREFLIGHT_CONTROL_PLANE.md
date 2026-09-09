# System3 Local Preflight Control Plane

Before substantive work:

1. Fetch remote `main` and record its full SHA.
2. Read Issue #188 and active PR ownership.
3. Record local `HEAD`, `origin/main`, ahead/behind state and working-tree provenance.
4. Identify the process/PID/command line owning the current-main localhost port.
5. Verify backend and `/ui` reachability from the same laptop session.
6. Record broker status/expiry/source metadata without values.
7. Verify NIFTY, BANKNIFTY, FINNIFTY and MIDCPNIFTY source/freshness/contracts.
8. Verify schedulers/background workers, local DB/state and logs/alerts.
9. Verify all 22 canonical tabs semantically and reconcile them with their APIs.
10. Fail closed on missing, stale, contradictory, or unavailable evidence.

Safety invariants: analyze/PAPER only, LIVE disabled, automatic real orders disabled, real broker order count zero.
