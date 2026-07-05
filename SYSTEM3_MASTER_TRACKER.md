# System3 Master Tracker

## Purpose

This is the single live control-plane document for System3. If any other report says `FINAL`, `COMPLETE`, `PASS`, or `READY`, this file still decides the current truth.

System3's locked goal is to identify valid option-tradable Indian market opportunities before the move, map them to real PE/CE contracts with expiry/strike/token evidence, paper-trade safely, and prove prediction accuracy and paper profitability every trading day.

## Current Operating Mode

| Area | Current truth | Status |
|---|---|---|
| Trading mode | PAPER / ANALYZER only | SAFE |
| Live trading | Disabled | SAFE |
| Order placement | Blocked | SAFE |
| Broker | Dhan read-only/analyzer status currently connected in latest user runtime proof | WATCH |
| Runtime issue | Fresh false `BROKER_DISCONNECTED` alert loop while broker is connected | OPEN |
| Options scope | Index and equity options must pass tradability before any paper trade | OPEN |
| Model proof | Needs multi-day prediction-vs-actual validation | OPEN |
| Dashboard proof | Must become runtime-driven, not hard-coded pass badges | OPEN |

## Active Control Documents

| Document | Role | Status |
|---|---|---|
| `SYSTEM3_MASTER_TRACKER.md` | Current system truth and next actions | ACTIVE |
| `SYSTEM3_BLOCKER_REGISTER.md` | Severity-ranked blockers | ACTIVE |
| `docs/control_plane/SYSTEM3_CURRENT_RUNTIME_TRUTH.md` | Runtime state, API truth, alert contradictions | ACTIVE |
| `docs/control_plane/SYSTEM3_SIGNAL_TO_TRADE_CONTROL.md` | Signal to PE/CE expiry/strike/token/paper trade chain | ACTIVE |
| `docs/control_plane/SYSTEM3_MODEL_ACCURACY_REGISTER.md` | Prediction accuracy and daily outcome tracking | ACTIVE |
| `docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md` | Agent workflow and proof rules | ACTIVE |
| `docs/control_plane/SYSTEM3_DOCUMENTATION_CONTROL_PLANE.md` | Markdown inventory, archive policy, contradiction rules | ACTIVE |

## Current Open Blockers

| ID | Severity | Blocker | Current proof | Required fix/proof |
|---|---:|---|---|---|
| SYS3-BLK-001 | HIGH | False `BROKER_DISCONNECTED` alert loop | `/api/state` shows broker connected and fresh disconnect alert at same timestamp | Canonical broker status, 3-failure threshold, alert dedupe, recovery clear |
| SYS3-BLK-002 | HIGH | Dashboard proof gates partly hard-coded / contradictory | UI can show pass while lifecycle/validation/human approval remain pending | Runtime-backed proof gates |
| SYS3-BLK-003 | CRITICAL | PE/CE strike/token visibility not proven for each signal | User observed only index display and missing equity option strike clarity | Option visibility audit per signal |
| SYS3-BLK-004 | CRITICAL | Equity F&O eligibility not proven before trade readiness | Prior signals included equities where option eligibility was uncertain | NSE/Dhan option universe filter before trade candidate |
| SYS3-BLK-005 | HIGH | Model accuracy not proven over enough market days | Accuracy screen/report shows limited validation | Daily prediction-vs-actual register |
| SYS3-BLK-006 | MEDIUM | Documentation sprawl and old final reports | Many historic `FINAL/COMPLETE/VALIDATION` docs exist | Classify docs; active truth only from control-plane docs |
| SYS3-BLK-007 | HIGH | No automated blocker report currently enforced | Repetitive issues reappear | `scripts/system3_blocker_finder.py` and report outputs |

## Done

| Date | Done item | Proof |
|---|---|---|
| 2026-06-15 | Confirmed current runtime safety from user `/api/state`: PAPER, Dhan ANALYZER, live false, order false, positions empty, PnL zero | User-provided `/api/state` JSON |
| 2026-06-15 | Identified false broker alert loop as current critical workflow contradiction | User `/api/state` plus code inspection |
| 2026-06-15 | Created active documentation control plane files | This commit |

## Next Safe Actions

1. Generate complete markdown inventory and classify every `.md` file.
2. Fix false `BROKER_DISCONNECTED` alert loop.
3. Add PE/CE option visibility audit.
4. Add F&O eligibility filter proof.
5. Add model accuracy daily register output.
6. Replace hard-coded dashboard proof gates with backend proof.
7. Run full-session PAPER proof before any live-readiness claim.

## Non-Negotiable Rules

- Do not enable live trading.
- Do not touch `.env`, secrets, Dhan credentials, or token files.
- Do not treat dashboard pass badges as truth unless backed by runtime proof.
- Do not count a signal as trade-ready until option eligibility, expiry, strike, token, quote, and liquidity/spread are proven.
- Do not call a model accurate until prediction-before-move proof and actual result comparison exist.
- Do not delete old markdown docs until inventory and archive classification are complete.
