# Autonomous backlog — GEMINI loop (self-discovered, 2026-08-16)

Target: https://genesis-system3-web-doq2wplepa-el.a.run.app/ui
Policy: agent_policy.yaml (no synthetic inventions; no gate weakening; test-first)

| ID | Severity | Defect | Evidence | Status |
|----|----------|--------|----------|--------|
| A1 | P0 | gain_rank live rows omit spot_price → Overview `--` | Live SHA `3f734397…`: 25/25 spots + banner present | VERIFIED LIVE |
| A2a | P0 | `/api/accuracy_trend` days≠`/api/auto_gates` Spearman series (1 vs 6) | trend local-only; gates use Firestore `load_spearman_days` | IN_PROGRESS (align contracts; gate still honest FAIL) |
| A2 | P0 | Proof gate 6/7 trip ML_SPEARMAN (need ≥0.70 on 5 days) | note `6/5 days · ρ=0.55 · need ≥0.7`; days_passing=1 | OPEN — do not force PASS |
| A3 | P1 | Model pipeline NO_TRADE / confidence 0 / no directional bias | `/api/state` signals | OPEN — honesty UX; real signals NOT_PROVEN |
| A4 | P1 | connected≠market-data reliability | prior URL proof 429/cache | OPEN — UI lane split already on main |
| A5 | P2 | Auton telemetrics banner while loop active | live bundle contains `[AUTONOMOUS LOOP]` | VERIFIED LIVE |

Resolved count updates only after live SHA verifies the fix.
Never remove banner until all proof gates genuinely READY.
