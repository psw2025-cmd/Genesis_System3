# Autonomous backlog — GEMINI loop (self-discovered, 2026-08-16)

Target: https://genesis-system3-web-doq2wplepa-el.a.run.app/ui
Policy: agent_policy.yaml (no synthetic inventions; no gate weakening; test-first)

| ID | Severity | Defect | Evidence | Status |
|----|----------|--------|----------|--------|
| A1 | P0 | gain_rank live rows omit spot_price → Overview `--` | `/api/gain_rank` FINNIFTY/MIDCPNIFTY spot empty; `/api/chain/NIFTY` spot=24366 MARKET_CLOSED_DHAN_SNAPSHOT | IN_PROGRESS (eval+enrich) |
| A2 | P0 | Proof gate 6/7 trip ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS | `/api/auto_gates`; accuracy_trend days=1 ρ=0.20 | OPEN — do not force PASS |
| A3 | P1 | Model pipeline NO_TRADE / confidence 0 / no directional bias | `/api/state` signals | OPEN — honesty UX present; real signals still NOT_PROVEN |
| A4 | P1 | connected≠market-data reliability | prior URL proof 429/cache | OPEN — UI lane split already on main |
| A5 | P2 | Auton telemetrics banner required while loop active | gemini Step 2 | IN_PROGRESS |

Resolved count updates only after live SHA verifies the fix.
