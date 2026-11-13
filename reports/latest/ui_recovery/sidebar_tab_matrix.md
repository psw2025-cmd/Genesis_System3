# Genesis System3 — UI Tab & Component Matrix (`PEND-003`, `PEND-004`, `PEND-061`, `REP-010`)
- **Observed UTC**: `2026-11-04T09:26:15.528711+00:00`

## 1. Port 8008 Institutional Command Center (`/ui` in `content/app/templates/premium.html`)
| Tab / Section ID | DOM Selector | Bound Backend APIs | Browser E2E Screenshot | Status |
|---|---|---|---|---|
| Top Command Header & Ticker Strip | `.ticker-overview-bar`, `#clock-utc` | `/api/verified-market`, `/api/market`, `/ws/stream` | `screenshots/proof_2_ui_overview_and_tickers.png` | `PASS` |
| `[TAB 1]` Multi-Timeframe WebGL/SVG Chart | `#inst-tab-btn-1`, `#inst-tab-content-1`, `#mainChart` | `/api/history?symbol=NIFTY`, `/api/history?symbol=RELIANCE` | `screenshots/proof_4_ui_3col_chart_and_routes.png` | `PASS` |
| `[TAB 2]` Live Broker Account & Demat Holdings | `#inst-tab-btn-2`, `#inst-tab-content-2` | `/api/dhan/summary`, `/api/dhan/holdings` (11 stocks = ₹3,49,655.36) | `screenshots/proof_3_ui_tab2_dhan_11_holdings.png` | `PASS` |
| `[TAB 3]` Quantitative Prediction & Micro-Reasoning | `#inst-tab-btn-3`, `#inst-tab-content-3` | `/api/ml/prediction-audit`, `/api/ml/forecast-vs-actual` | `screenshots/ui_verified_snap.png` | `PASS` |
| `[TAB 4]` Autonomous Agent Sandbox Logs | `#inst-tab-btn-4`, `#inst-tab-content-4` | `/api/routes`, `/api/dhan/discovery/chain-subscriptions` | `screenshots/ui_verified_snap.png` | `PASS` |
| 3-Column Command Grid (`.command-grid`) | Left Watchlist/653 Routes, Center Chart/CE-PE Movers, Right Order/Risk | `/api/options/gainers`, `/api/depth`, `/api/risk`, `/api/routes` | `screenshots/proof_4_ui_3col_chart_and_routes.png` | `PASS` |
| Live Order Modal & Safety Gate | `#btn-open-live-order`, `#live-order-modal`, `#order-toast` | `POST /api/v1/placeorder` (HTTP 403 Safety Gate Block) | `screenshots/ui_e2e_verified.png` | `PASS` |

## 2. React SPA Workspace (`dashboard/frontend/src/App.tsx` — 22+ Tab Switch Inventory)
Tracked React component files in `dashboard/frontend/src/components`: `64` files (`54` direct + `10` workspace components).
- Mapped `App.tsx` switch cases: `overview`, `command-center`, `market-top-ce-pe`, `options-intel`, `option-chain`, `equity-options`, `multibagger`, `gap-up`, `prediction-audit`, `ml-performance`, `paper`, `trade-history`, `positions`, `strategy-lab`, `genesis-brain`, `orchestrator`, `truth`, `e2e-proof`, `recovery`, `health`, `trading-control`, `sim-live`, `alerts`.
- **Note on `REP-006` / `PEND-057`**: `dashboard/frontend/src/config.ts` defaults to `localhost:8000` when running the standalone Vite React dev server (`port 3000`), whereas the authoritative local SSR/SPA production command center runs on `http://127.0.0.1:8008/ui`.
