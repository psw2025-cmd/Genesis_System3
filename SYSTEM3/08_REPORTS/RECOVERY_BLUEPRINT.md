# Phase 0.5 recovery blueprint
| Blocker | Root cause | Fix | Verification | Expected result |
|---|---|---|---|---|
| B-001 | Deleted verifier/dangling workflow | Restore+modernize script, gate and tests | Exact-head CI + negative test | Code proof PASS, live proof BLOCKED pending deploy |
| B-002 | Removed auto-deploy path | Implement manual-only candidate with immutable digest + rollback | Static CI cannot execute without approval | Candidate reviewed |
| B-003 | Owner consent absent | Separate scoped approval after candidate PASS | Explicit receipt | Authorized bounded change only |
| B-004 | No serving service | Future approved candidate | Serving SHA/digest/revision | Real runtime proof |
| B-005 | No broker/worker proof | Read-only market-session verifier, lease, heartbeat, ledger | Independent UTC reconciliation | PAPER runtime proof |
| B-006 | No independent broker history | Authorized read-only order-history inspection | Broker-side reconciliation | Actual-order verdict |
| B-007 | Insufficient reliability/analytics | OTel/SLO/FinOps/walk-forward/failure injection | Measured source-backed receipts | Reliable phase gates |
