# Current-remote-main revalidation addendum — 2026-08-16

This addendum preserves the original PR #249 extracts as historical evidence and
corrects claims that were produced from a stale/local checkout. It does not rewrite
the original audit.

## Authorities

- Repository truth: `psw2025-cmd/Genesis_System3` `origin/main`
- Revalidated main SHA: `ebd77a0efe545bedaab9fcc1de3a1a180466c263`
- User-facing truth: `https://genesis-system3-web-doq2wplepa-el.a.run.app/ui`
- Request-scoped production serving SHA at baseline:
  `997daef4cfb3322e317da69b5cbb5b69950dab26`
- Coordination authority: GitHub Issue #188
- Safety: PAPER/ANALYZER; LIVE and order authority remain off

## Mandatory evidence classification

Every prior finding must be classified as one of:

- `REVALIDATED_CURRENT_REMOTE_MAIN`
- `HISTORICAL_OR_LOCAL_ONLY`
- `STALE_SOURCE_REVALIDATION_REQUIRED`
- `DISPROVEN_BY_CURRENT_MAIN`

No local checkout observation is current production truth.

## Corrections and current evidence

| Area | Prior extract claim | Remote-main evidence | Current verdict |
|---|---|---|---|
| Q21 canonical navigation | Only about 16 tabs wired; Decision Intel, Prediction Audit and Data Integrity absent/orphaned | `dashboard/frontend/src/components/Sidebar.tsx` defines 22 canonical tabs; `dashboard/frontend/src/App.tsx` imports and renders all 22 | `DISPROVEN_BY_CURRENT_MAIN` |
| Q21 production rendering | Several named workspaces not reachable | Fresh production browser baseline showed all 22 navigation entries and direct `?tab=` routing | `REVALIDATED_CURRENT_REMOTE_MAIN` |
| Serving identity | UI deployment identity not visible | Data Integrity and proof diagnostics show short SHA; `/api/deploy/info` exposes exact SHA/service/region with LIVE false | `REVALIDATED_CURRENT_REMOTE_MAIN` |
| Broker safety truth | Token generation / safety not URL-visible | Data Integrity, System and Broker render safe Secret Manager version identifier, broker state, PAPER/ANALYZER and LIVE/order locks; no token value | `REVALIDATED_CURRENT_REMOTE_MAIN` |
| Instrument master | Local master reported stale | Request-scoped production `/api/instruments/health` reported 119,552 runtime rows, `stale=false`, Dhan source and current sync timestamp | `HISTORICAL_OR_LOCAL_ONLY` for the old local-stale claim; cloud master `REVALIDATED_CURRENT_REMOTE_MAIN` |
| Prediction validation history | One-day ρ=0.20 was treated as the only validation truth | `/api/accuracy_trend` still reports one day and avg ρ=0.20, while canonical `/api/auto_gates` reports six days and latest ρ=0.55 | `REVALIDATED_CURRENT_REMOTE_MAIN` contract conflict; promotion remains blocked |
| Gate ledger | Summary proof rows can be consumed as gate truth | `/api/auto_gates.proof_gates` says PASS for expectancy, paper lifecycle, tick health and option visibility while `/api/auto_gates.gates` marks those same gate IDs `pass=false` | `REVALIDATED_CURRENT_REMOTE_MAIN` data-contract defect; canonical gate map must win and conflicts must be visible |
| Costed walk-forward | PASS might be read as strategy performance | `/api/backtest/results` has 8 trades / 5 days, costs and slippage included, but net P&L is -₹102,636.35 and the artifact says it is pipeline proof only | `REVALIDATED_CURRENT_REMOTE_MAIN`: pipeline `PARTIAL`; strategy performance `NOT_PROVEN` |
| Paper outcome | Paper lifecycle implied successful | Current `/api/auto_gates` reports 9 trades, win rate 0.3333, net expectancy -196.14 and canonical lifecycle `pass=false` | `REVALIDATED_CURRENT_REMOTE_MAIN`: promotion `BLOCKED` |
| ML proof | Model families/artifacts implied active intelligence | Current `/api/ml/performance` does not establish a proof-ready champion; heuristics remain non-ML | `REVALIDATED_CURRENT_REMOTE_MAIN`: `NOT_PROVEN` |
| Engineering wave visibility | GitHub coordination can substitute for URL truth | `/api/agent/status` responds but does not expose current wave, owner or next dependency | `UI_OBSERVABILITY_GAP`: `BACKEND_PROGRESS_CONTRACT_REQUIRED` |

## UI-OBS-1 bounded remediation

Cursor's current non-overlapping frontend wave:

1. preserves all 22 tabs;
2. adds a runtime-derived implementation progress panel to Data Integrity;
3. shows source and verification time for every progress lane;
4. renders unsupported fields as `NOT_PROVEN`/`BACKEND_PROGRESS_CONTRACT_REQUIRED`;
5. reconciles Prediction Audit against canonical `/api/auto_gates.gates` and visibly
   fails closed when summary rows disagree;
6. shows validation sample size and the `/api/accuracy_trend` versus
   `/api/auto_gates` history conflict;
7. replaces raw backtest JSON with costed sample/P&L semantics and
   `PIPELINE_PROOF_ONLY`;
8. fixes 0–1 paper win-rate values so `0.3333` renders as `33.3%`, not `0.3%`.

This wave does not modify broker backend, token rotation, Secret Manager, IAM, GCP
configuration, schedulers, LIVE/order logic, or production secrets.

## Remaining fail-closed dependencies

- Current wave/owner/next dependency need a safe backend progress contract.
- Accuracy-history writers/contracts must reconcile one day versus six days.
- `/api/auto_gates` must stop publishing contradictory canonical and summary verdicts.
- Durable broad-market history, fair champion/challenger tournament and positive
  costed OOS performance remain unproven.
- Final PASS requires merge/deploy and a new exact-serving-SHA production-browser
  proof; local screenshots and CI do not satisfy URL acceptance.
