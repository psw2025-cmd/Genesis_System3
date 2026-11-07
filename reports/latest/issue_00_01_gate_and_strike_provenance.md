# Genesis System3 — gate and strike provenance audit (30 October 2026)

## Verified execution
- Repository: C:\\Genesis_System3_clean; starting HEAD: 7fdd44fae.
- Existing tests: tests/test_system3_auto_gates.py and tests/test_firestore_state_backend.py PASS (16 tests).
- Added tests/test_stale_tick_gate_fail_closed.py: 2 additional tests PASS; combined 18 PASS.
- Backend module imported successfully (APP_IMPORT_PASS); this is not proof of working HTTP service.
- Direct cloud revision: genesis-system3-web-00053-cbv, 100% production traffic.
- Local evaluator after rejecting old tick certificate: 3/7, trade_ready=false; blockers PROFIT_BLOCKER, SYS3-BLK-005, SYS3-BLK-008, TICK_HEALTH_BLOCKER.
- Earlier local evaluator before fix: 4/7, demonstrating a stale PASS flag bypass.

## Evidence mismatch
- Correct expectancy report: reports/latest/friction_expectancy/summary.json — pass=false, source=none, trade_count=0.
- Correct lifecycle report: reports/latest/analyzer_paper_lifecycle_proof/summary.json — pass=false, full_lifecycle_proven=false.
- Correct tick report: reports/latest/websocket_tick_health/summary.json — previously pass=true with 5-second claimed age yet generated 2026-08-29. Historical claim is not a current tick.
- Canonical trade ledgers storage/live/paper_trades.json and outputs/paper_closed_trades.json are absent.
- The six supplied PAPER trades and 450.41 expectancy have no corresponding independent raw ledger in the checked paths; cannot verify strikes, entry/exit, cost, expiry, or execution_id. No synthetic trade values were published.

## Code paths and limitations
- scripts/system3_friction_expectancy_proof.py loads trades from storage/live/paper_closed_trades.json, outputs/paper_closed_trades.json, or /api/paper; its source provenance is not automatically verified.
- scripts/system3_gate_evaluator.py reads reports/latest/friction_expectancy/summary.json, analyzer_paper_lifecycle_proof/summary.json, websocket_tick_health/summary.json.
- dashboard/backend/auto_gates_service.py enables cloud_mode based on Firestore env and uses skip_proofs=True; cloud evaluator still reads local packaged reports for three gates, while Spearman days can read Firestore.
- dashboard/backend/firestore_state_backend.py has document APIs for scheduler evidence and validation days, not automatic publication of these three evidence JSON files.
- /api/recovery/progress is deployed but local main in this clean checkout lacks the RecoveryProgressTab implementation; 113/113 is not supported.

## Repair made
- scripts/system3_gate_evaluator.py: disallow a stale PASS bit from clearing tick-health. Require fresh source timestamp, <=15s tick, <=10s refresh and broker_connected.
- tests/test_stale_tick_gate_fail_closed.py added to reject outdated and missing timestamps.
- Not merged, not deployed, no Firestore writes, and no real broker orders.

## Next evidence required
1. Obtain real append-only PAPER execution ledger with unique IDs and matching broker market quotes at stated timestamps; prove expiry/strike contracts were eligible and order was simulated.
2. Recompute friction from genuine ledger, hash every source, verify cost and duplicates; reject self-authored summary-only records.
3. Prove lifecycle using entry/fill/exit records and live timestamps; prove tick freshness with authenticated broker marketfeed.
4. Introduce isolated evidence publisher with a schema, hashes, run identity, and transaction readback; update CLOUD evaluator to read and revalidate this durable evidence. Simply uploading summary JSON cannot make cloud 7/7.
5. Resolve broker error 906 and Dhan option-chain empty data, then validate all UI/Excel entries; do not turn 113 checks PASS based on template presence.
