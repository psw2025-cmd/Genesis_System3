# Genesis System3 — Paper Trade Lifecycle & Safety Gate Audit (`OBS-017`, `PEND-022..027`, `G13..G16`)
- **Observed UTC**: `2026-11-04T09:26:15.528711+00:00`
- **Authoritative Proof File**: `reports/latest/analyzer_paper_lifecycle_proof/summary.json`
- **Live Endpoints**: `GET /api/paper/ledger`, `GET /api/paper/lifecycle`, `GET /api/v1/placeorder`, `POST /api/v1/placeorder`

## 1. Reconciled Paper Trade Lifecycle (`LIFECYCLE_20261030_152644`)
| Field | Observed Value | Verification |
|---|---|---|
| `proof_id` | `LIFECYCLE_20261030_152644` | `PASS` |
| `idempotency_key` | `IDEMP_LIFECYCLE_20261030_152644` | `PASS` |
| `signal_generated` -> `entry_order_placed` -> `exit_completed` | `true` -> `true` -> `true` | `PASS` |
| `gross_pnl_inr` | `+₹5.00` | `PASS` |
| `charges_inr` (Statutory + Brokerage Friction) | `-₹20.00` | `PASS` |
| `net_pnl_inr` | `-₹15.00` | `PASS` |
| `real_broker_orders_sent` | `0` | `PASS` (`tests/test_order_zero_calls.py`) |

## 2. Negative Safety Gate Verification (`G16` / `PEND-027` / `PEND-059` / `PEND-067`)
- `POST http://127.0.0.1:8008/api/v1/placeorder` -> **HTTP 403 Forbidden** (`Order Blocked by Backend Safety Gate: Live trading is locked (LIVE_TRADING_ENABLED=0)`).
- `pytest tests/test_order_zero_calls.py` -> **PASS** (`0` real broker order mutations across all code paths).
