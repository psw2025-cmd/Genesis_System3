# Dashboard Implementation Checklist — TradingView/Binance Quality & Full Working Capability

**Goal:** Implement everything needed so our dashboard matches the **quality and full working capability** of TradingView / exchange-style (e.g. Binance) dashboards, using **Angel One only** (no Binance).

---

## 1. What TradingView/Exchange Dashboards Have (The Bar)

| Capability | TradingView / Binance-style | Our target |
|------------|-----------------------------|------------|
| **Candlestick / K-line chart** | Full OHLCV chart, multiple timeframes, zoom, crosshair | Same: professional price chart |
| **Real-time ticker** | Last price, 24h change %, volume, sparkline | Same for underlyings (NIFTY, BANKNIFTY, etc.) |
| **Order book** | Bids/asks ladder, depth, spread | Same for F&O (option chain as order-book style or L2 if available) |
| **Recent trades** | Live list: price, size, time, side | Same: last N trades per symbol/session |
| **Order form** | Limit/market, buy/sell, quantity, place/cancel | Same: paper or live (Angel) with clear mode |
| **Positions & orders** | Open positions, open orders, PnL, cancel | Same, wired to real data |
| **Symbol/watchlist** | Switch symbol, multi-symbol view | Same: underlyings + optional watchlist |
| **Studies / indicators** | Volume, MA, RSI, etc. on chart | Optional: volume, simple indicators |
| **Layout & UX** | Resizable panels, dark/light, keyboard | Same: responsive, theme, accessibility |
| **Data freshness** | WebSocket + REST, “last update” labels | Same: WS + polling, visible timestamps |
| **Export / proof** | Screenshot, export report, audit trail | Same: proof pack, export PnL/positions |

---

## 2. Current State vs Gaps

### 2.1 What We Already Have (Working)

| Area | What exists | Notes |
|------|-------------|--------|
| **Overview** | Health, broker status, market status, cycle count, PnL summary, SLA | Uses `/api/state`, `/api/perf`; WebSocket for live updates |
| **Option chain** | Full chain table, filters (ATM, strike range, liquidity), spot, PCR | `/api/chain/{underlying}`; real or synthetic by config |
| **Signals** | Top signal, QC status, direction, confidence | `/api/state`, `/api/signal/top`, `/api/qc` |
| **Paper trading** | Positions, PnL history, close position, line/pie charts | `/api/state`, `/api/pnl`, `/api/positions`, close endpoint |
| **Advanced charts** | Heatmap (OI/vol/IV/LTP), IV surface, Greeks, PCR | `/api/charting/*`; Recharts (BarChart), no candlesticks yet |
| **Risk** | Portfolio risk, limits check | `/api/risk`, `/api/risk/portfolio`, `/api/risk/check-limits` |
| **Alerts** | List, read/unread, recent | `/api/alerts`, `/api/alerts/recent`, `/api/alerts/unread` |
| **ML / Model** | Performance, compare, behavior | `/api/ml/*`, `/api/model/behavior` |
| **Control plane** | Runner status, learning, forensic, validation | APIs exist; some UI actions call backend |
| **Agent** | Status, memory, issues, upgrade plan, test results | `/api/agent/*` |
| **Real-time** | WebSocket `/ws/stream` + polling fallback | Used in Overview |
| **Backend** | Many REST APIs + WebSocket; state SSOT | Single source of truth for dashboard |

### 2.2 Gaps (What We Need to Implement)

| # | Gap | Priority | Backend | Frontend | Notes |
|---|-----|----------|---------|----------|--------|
| **G1** | **Candlestick / K-line chart** | High | OHLCV API (Angel historical + live); optional datafeed for TV | Add TradingView Lightweight Charts or Charting Library; symbol + interval selector | Need OHLC bars (1m/5m/15m/1h/1D) from Angel or stored series |
| **G2** | **OHLCV / bars API** | High | `GET /api/chart/ohlc/{underlying}?interval=5m&from=&to=` (and/or datafeed for TV) | Consumed by chart component | Backend must fetch from Angel or from stored candle data |
| **G3** | **Ticker strip** | Medium | `GET /api/ticker` or reuse chain/spot per underlying | Ticker bar: last, change %, volume, optional sparkline | Can derive from existing chain/spot + history |
| **G4** | **Order book–style view** | Medium | Option chain already has LTP/bid/ask; optional L2 endpoint if Angel provides | Order book ladder UI (bids left, asks right, spread) | Can build from current chain data (CE/PE by strike) |
| **G5** | **Recent trades list** | Medium | `/api/trades/today`, `/api/trades/history` exist | Dedicated “Recent trades” panel: table, live update (poll/WS) | Wire existing APIs to a visible component |
| **G6** | **Proof pack from UI** | Medium | `/api/proof-pack` or script | “Download Proof Pack” calls API or triggers script; no “not implemented” alert | Replace ControlPlane alert with real action |
| **G7** | **Order form (place/cancel)** | High (for full trading UX) | `/api/orders/create`, `/api/orders/{id}/cancel` exist | Order form: symbol, side, type, qty, price; confirm; show result | Ensure backend is wired to Angel paper/live; form in Paper Trading or dedicated page |
| **G8** | **Open orders table** | High | `/api/orders`, `/api/orders/history` | Table: order id, symbol, side, qty, status, cancel button | Wire to existing endpoints |
| **G9** | **Data freshness labels** | Low | Timestamps in responses (e.g. `last_updated`) | Show “Updated 2s ago” on each panel | Backend already has timestamps; frontend to display |
| **G10** | **Resizable layout** | Low | — | Resizable panels (e.g. react-resizable or grid) | UX polish |
| **G11** | **Export report / CSV** | Medium | `/api/export/positions`, `/api/export/pnl`, `/api/export/report` | Buttons that download; no stubs | Verify endpoints return correct files; wire buttons |
| **G12** | **Symbol switcher everywhere** | Low | Underlyings from `/api/underlyings` | Global or per-page underlying selector | Some pages have it; make consistent |
| **G13** | **Chart studies (e.g. volume)** | Low | Volume in OHLCV response | Add volume bars under candlestick chart | After G1/G2 |

---

## 3. Implementation Order (Recommended)

### Phase A — Charts & data (TradingView-like)

1. **G2** — Add OHLCV/bars API (from Angel or stored data).
2. **G1** — Add candlestick chart (e.g. `lightweight-charts`) and wire to G2; symbol + interval.
3. **G13** (optional) — Add volume to bars and volume series on chart.

### Phase B — Trading UX (exchange-like)

4. **G7** — Order form: place order (paper/live via Angel), show success/error.
5. **G8** — Open orders table with cancel.
6. **G5** — Recent trades panel using `/api/trades/today` and `/api/trades/history`.

### Phase C — Ticker & order book

7. **G3** — Ticker strip (last, change %, volume) for underlyings.
8. **G4** — Order book–style view from option chain (bids/asks by strike).

### Phase D — Polish & proof

9. **G6** — Proof pack: real implementation in Control Plane (API or script trigger).
10. **G11** — Export: wire export endpoints to buttons; verify file download.
11. **G9** — “Last updated” labels on key panels.
12. **G10** — Resizable layout (optional).
13. **G12** — Consistent symbol/watchlist switcher.

---

## 4. Backend Additions (Summary)

| Endpoint / feature | Purpose |
|--------------------|--------|
| `GET /api/chart/ohlc/{underlying}?interval=5m&from=&to=` | OHLCV bars for candlestick chart (Angel or stored). |
| (Optional) Datafeed endpoint for TradingView Charting Library | Same data in TV protocol (e.g. `getBars`, `resolveSymbol`). |
| `GET /api/ticker` or `GET /api/ticker/{underlying}` | Last price, 24h change, volume for ticker strip. |
| Ensure `/api/trades/today` and `/api/trades/history` return correct shape | For recent-trades panel. |
| `GET /api/proof-pack` or documented script | For “Download Proof Pack” in UI. |
| Confirm `/api/orders/create`, `/api/orders`, `/api/orders/{id}/cancel` | Fully wired to Angel (paper/live). |

---

## 5. Frontend Additions (Summary)

| Component / change | Purpose |
|--------------------|--------|
| **Candlestick chart page or section** | TradingView-like price chart (e.g. `lightweight-charts`). |
| **Ticker strip** | Top or sidebar: underlying, last, change %, volume. |
| **Order book panel** | Bids/asks from chain or L2. |
| **Recent trades panel** | Table of recent trades; poll or WebSocket. |
| **Order form** | Place order (and cancel from orders table). |
| **Open orders table** | List + cancel. |
| **Proof pack button** | Calls API or runs script; no “not implemented” alert. |
| **Export buttons** | Positions, PnL, report — trigger download. |
| **“Last updated” labels** | On Overview, Chain, Signals, etc. |
| (Optional) **Resizable layout** | Drag to resize panels. |

---

## 6. Definition of “Full Working Capability”

The dashboard will be at **TradingView/Binance-style quality and full working capability** when:

- [ ] **Charts:** Candlestick (OHLCV) chart with at least one timeframe and real data from Angel.
- [ ] **Ticker:** Visible last price and change (and optionally volume) for selected underlyings.
- [ ] **Order book:** Order book–style view (from chain or L2) with spread.
- [ ] **Trades:** Recent trades list visible and updating.
- [ ] **Orders:** Place order and cancel order from UI; open orders table.
- [ ] **Positions:** Already there; ensure PnL and close work correctly.
- [ ] **Proof & export:** Proof pack and export (positions/PnL/report) work from UI.
- [ ] **Data freshness:** Key panels show last update time.
- [ ] **No stubs:** No “not implemented” alerts for core actions (proof pack, export, order place/cancel).

---

## 7. References

- **TradingView / exchange reference:** `docs/TRADINGVIEW_AND_EXCHANGE_DASHBOARD_REFERENCE.md`
- **Current backend routes:** `dashboard/backend/app.py` (e.g. `/api/chain`, `/api/charting/*`, `/api/orders/*`, `/api/trades/*`, `/api/export/*`, `/api/proof-pack`).
- **Current frontend:** `dashboard/frontend/src/App.tsx` (routes), `dashboard/frontend/src/components/*`.
- **Angel only:** No Binance; all data and orders via Angel One.

Use this checklist to implement the missing pieces so the dashboard matches TradingView/exchange quality and is fully usable end-to-end.
