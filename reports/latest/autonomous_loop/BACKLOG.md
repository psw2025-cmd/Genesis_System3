# Autonomous backlog — GEMINI loop (self-discovered, 2026-08-16)

Target: https://genesis-system3-web-doq2wplepa-el.a.run.app/ui
Policy: agent_policy.yaml (no synthetic inventions; no gate weakening; test-first)
Closure: `python scripts/system3_continuous_closure_orchestrator.py` → `reports/latest/continuous_closure/resume_state.json`

| ID | Severity | Defect | Evidence | Status |
|----|----------|--------|----------|--------|
| A1 | P0 | gain_rank live rows omit spot_price → Overview `--` | Live: 25/25 spots + banner | VERIFIED LIVE |
| A2a | P0 | `/api/accuracy_trend` days≠`/api/auto_gates` Spearman series | Live ALIGN days=6 `source=load_spearman_days` | VERIFIED LIVE |
| A2 | P0 | Proof gate 6/7 trip ML_SPEARMAN (need ≥0.70 on 5 days) | note `6/5 days · ρ=0.55 · need ≥0.7` | OPEN — do not force PASS |
| A3 | P1 | Model pipeline NO_TRADE / confidence 0 / no directional bias | `/api/signal/top` MARKET_CLOSED | OPEN — honesty UX; real signals NOT_PROVEN |
| A4 | P1 | connected≠market-data reliability | prior URL proof 429/cache | OPEN — UI lane split already on main |
| A5 | P2 | Auton telemetrics banner while loop active | live bundle contains `[AUTONOMOUS LOOP]` | VERIFIED LIVE |
| C1 | P0 | Continuous closure system (scan/verify/watchdog/cards/resume) | `/api/continuous_closure` + Overview board | IN_PROGRESS |

Resolved count updates only after live SHA verifies the fix.
Never remove banner until all proof gates genuinely READY.
Next session: read `reports/latest/continuous_closure/resume_state.json` and execute `next_id`.
