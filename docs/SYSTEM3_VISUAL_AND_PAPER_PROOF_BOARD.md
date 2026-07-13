# System3 Visual + Paper Proof Board

This board is the only accepted proof method for claiming System3 progress.

## Absolute rule

Do **not** claim full system working, production-ready, money-ready, or world-best until proof files and dashboard visual proof show PASS after the latest relevant commit.

## Required proof layers

| Layer | Required proof | Status rule |
|---|---|---|
| GitHub workflows | `reports/latest/windows_self_hosted_workflows/summary.json` | All workflows migrated or manual-review listed |
| Render/backend health | `reports/latest/github_render_failure_tracker/summary.json` | PASS only |
| Dashboard visual | `reports/latest/dashboard_visible_issue_tracker/summary.json` | PASS only |
| Autopilot board | `reports/latest/system3_autopilot_proof_board/summary.json` | PASS only |
| Safe repair runner | `reports/latest/safe_repair_runner/summary.json` | PASS only |
| Market-session proof | `reports/latest/market_session_proof_runner/summary.json` | PASS only during/after market proof |
| Broker Dhan proof | Broker/Dhan status endpoints and reports | No 401/auth error |
| Option-chain proof | Option-chain report | No empty chain caused by auth |
| Paper lifecycle | Paper lifecycle report | Full paper order lifecycle proven |
| ML/profit gates | Gate evaluator report | No ML/profit blocker |

## Visual proof requirement

A screenshot or UI proof must visibly show:

- Owner: Pritam S. Warghade
- Live trading: OFF
- Broker: Dhan connected / token valid
- Option chain: rows visible and not auth-blocked
- Paper trades: source/provenance visible
- Gate matrix: all required gates green/PASS
- No red, PEND, BLOCKED, FAIL, stale, or contradiction text

## Paper proof requirement

Paper proof must include:

- Time
- Symbol
- Underlying equity/index
- F&O eligibility result
- Expiry
- Strike
- CE/PE
- Entry price
- LTP
- Quantity
- SL/TP/trailing rule if applicable
- Reason for trade
- Block reason if no option chain
- Broker/source provenance
- Cumulative P&L

## Current truth rule

If any proof file is missing, stale, blocked, red, or contradictory, status remains:

```text
PENDING / BLOCKED — NOT FULLY WORKING YET
```

## Safety rule

Live trading remains OFF:

```text
LIVE_TRADING_ENABLED=0
SYSTEM3_LIVE_TRADING_ALLOWED=0
ANALYZE_MODE=1
```

No proof workflow may place, modify, cancel, or route a live order.
