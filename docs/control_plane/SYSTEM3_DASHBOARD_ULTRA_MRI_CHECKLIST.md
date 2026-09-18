# Genesis System3 — Dashboard Ultra-MRI Checklist

**Authority marker:** `SYSTEM3_DASHBOARD_ULTRA_MRI_V1`

Use this checklist for every full dashboard review. It applies to all 22 canonical tabs and must be used by implementation and independent-verification agents.

For each tab record:

```text
tab_id
route
rendered
visible_error_or_loading
source_endpoint_or_websocket
http_status
content_type
latency
source/provider
as_of
freshness
row/symbol/contract_count
expected_count_or_reason_not_known
semantic_match_with_api
reload_behavior
reconnect_behavior
console_errors
network_failures
state_root_used
paper_data_visible
live_state_visible_and_false
real_broker_order_count
root_cause_if_failed
implementation_owner
verification_owner
evidence_path
verdict
```

Mandatory cross-tab checks:

1. runtime state is `RUNNING|OFFLINE|RECOVERING|INCOMPLETE_GAP` and truthful;
2. exact Git SHA and generated-at/heartbeat age are visible or available from canonical status endpoint;
3. broker connected/read-only state is consistent across Overview/Broker/Trade/Option Chain and API;
4. market-open/closed truth uses Asia/Kolkata and does not regress during warm-up;
5. source/freshness/provenance are explicit for every market-data surface;
6. NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY required option-chain views are checked separately;
7. NSE/BSE/equity-option supported universe counts are not silently truncated;
8. prediction/forecast pages reject stale source dates and expose provenance;
9. PAPER Trades/Trade/Signals lifecycle joins are consistent with the authoritative local ledger;
10. no synthetic/fixture/sample history is presented as current real PAPER history;
11. charts are populated only from legitimate source data or explicitly show unavailable/gap;
12. reload does not fork local state or lose authoritative ledger continuity;
13. WebSocket disconnect/reconnect surfaces `RECOVERING` rather than stale green status;
14. local runtime normal operation performs no GCP API call;
15. LIVE flags remain false and no place/modify/cancel real-order route is exercised;
16. console/network errors are inspected, not ignored because DOM rendered;
17. one-click launcher startup and clean shutdown/restart are tested;
18. duplicate worker/scheduler protection is verified;
19. laptop-off/missed interval is represented as a real gap unless legitimate backfill proves recovery;
20. all temporary browser profiles/screenshots/transcripts are cleaned or promoted to bounded evidence.

Full review sequence:

```text
PRECHECK CLEANLINESS
-> START CANONICAL LOCAL LAUNCHER
-> VERIFY RUNTIME ROOT + SHA + HEARTBEAT
-> VERIFY BROKER/SESSION READ-ONLY
-> VERIFY API SOURCE/FRESHNESS
-> OPEN FRESH BROWSER
-> REVIEW ALL 22 TABS
-> CAPTURE CONSOLE/NETWORK/WEBSOCKET
-> CORRELATE UI WITH API/DB
-> RELOAD/RECONNECT TEST
-> PROCESS RESTART TEST
-> GAP/RECOVERY TEST WHERE SAFE
-> PAPER SAFETY CHECK
-> CLEAN TEMP OUTPUT
-> INDEPENDENT SECOND REVIEW
-> PUBLISH COMPACT SUMMARY TO ISSUE #188
```

A render-only 22/22 is never semantic PASS.
