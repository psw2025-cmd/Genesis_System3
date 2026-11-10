# Live Dhan vs System3 parity — unresolved issues

**Captured:** 2026-08-25 ~14:40 IST  
**Serving SHA:** `719566d23fd9aeb783a72fcec9493557f783781f`  
**GitHub main (ahead):** `2c0b44a…`  
**Broker:** connected / Session OK · PAPER · LIVE OFF  
**Evidence:** `reports/latest/dhan_parity/DHAN_PARITY_LIVE_COMPARE.json` + live browser `/?tab=chain`  
**Dhan reference:** `https://web.dhan.co/advancedoptionchain` (+ home/positions/portfolio)

## Priority rule

System3 must **full-match real-time Dhan market surfaces** for index + equity options (columns, freshness, ATM focus, charts). Until then: **NOT DONE** / no false-green.

---

## P0 — still open

| ID | Issue | Live proof | Dhan truth |
|---|---|---|---|
| P0-CHAIN-STALE | Chain tab shows **DHAN EXPIRY SNAPSHOT** while market open, `fetched=07:49:32Z` while UI clock ~09:09Z (~80+ min stale) yet `status=OK` | Screenshot `/?tab=chain` 2026-08-25 | Dhan advanced chain updates continuously |
| P0-ATM-VIEW | Default visible rows deep OTM (**27050–27150**) while spot **~24130** — looks like wrong chain; ATM not centered | Same screenshot | Dhan centers near ATM |
| P0-LTP-CHG | API has `change`/`change_percent`; **UI table has no LTP Chg (%)** | `OptionChain.tsx` headers: OI,ChgOI,Vol,IV,LTP,Bid… | Dhan column **LTP Chg (%)** |
| P0-BUILDUP | No **Buildup** (Long/Short/Short Covering/…) in chain UI | UI headers | Dhan **Buildup** |
| P0-OI-VOL-PCT | UI shows absolute ChgOI/Vol only — missing **OI chg (%)** and **Vol chg (%)** | UI vs API `oi_change` absolute | Dhan % change columns |
| P0-GREEKS-TABLE | API returns delta/gamma/theta/vega; **not shown in chain table** | API ATM sample has delta; UI no Greek cols | Dhan shows Delta/Gamma/Theta/Vega |
| P0-DEPLOY-LAG | Serving behind `main` | deploy_info `719566d` vs main `2c0b44a` | N/A — GitOps |

## P1 — equity options / tabs / charts

| ID | Issue | Proof |
|---|---|---|
| P1-EQ-SECURITY-ID | Equity option chains need Dhan **security_id** / scrip master map (ANGEL ONE etc.); index-only acceptance is insufficient | Dhan equity chain + Gemini note on `security_id_list` |
| P1-EQ-TOP-CE | Top CE / equity option scanner must be live-verified vs Dhan watchlist & chain | `/api/scanner/equity_options` = 200; product UI parity TBD |
| P1-HOLDINGS-FUNDS | `/api/holdings` **404**, `/api/funds` **404** while Dhan Portfolio/Positions show funds & holdings | curl probe 2026-08-25 |
| P1-CHARTS | `/api/charts/NIFTY` **404** — no live chart/graph parity with Dhan | curl probe |
| P1-MULTIBAGGER-ROUTE | `/api/multibagger` **404** | curl probe |
| P1-SENSEX-PCR | SENSEX/NIFTY PCR/spot must be cross-checked same session vs Dhan header (ATM IV, PCR, lot, DTE) | Dhan SENSEX header vs System3 chain meta |

## P2 — quality / false-green

| ID | Issue |
|---|---|
| P2-ZERO-ROWS | Far OTM rows LTP/IV often 0 — must not look like “full live chain ready” without ATM filter |
| P2-SNAPSHOT-LABEL | Label **DHAN EXPIRY SNAPSHOT** during market hours is DEGRADED; must not classify as LIVE match |
| P2-IV-SCALE | Confirm IV display scale (0.15 vs 15%) matches Dhan ATM IV presentation |

## API field coverage (backend OK, UI incomplete)

NIFTY ATM sample (API live compare): spot~24209, CE 24200 LTP 44.9, change_percent≈-27%, oi_change present, greeks present.

**Missing in UI vs Dhan:** buildup, vol_chg_pct, oi_chg_pct, ltp_chg display, greeks columns.

## Endpoint probe (serving)

| Path | HTTP |
|---|---|
| `/api/positions` | 200 |
| `/api/signals` | 200 |
| `/api/scanner/equity_options` | 200 |
| `/api/holdings` | 404 |
| `/api/funds` | 404 |
| `/api/charts/NIFTY` | 404 |
| `/api/equity/options` | 404 |
| `/api/multibagger` | 404 |

## Acceptance (Dhan full match) — FAIL until

1. Market-open chain badge = **LIVE DHAN** with age < 60s (or explicit STALE)  
2. Default view = ATM ±N (not deep OTM)  
3. Columns: LTP, **LTP Chg %**, OI, **OI chg %**, Vol, **Vol chg %**, **Buildup**, IV, Bid/Ask, **Greeks**  
4. Equity underlying load via security_id works and matches Dhan chain  
5. Charts/graphs live route exists OR tab marked MISSING (not false-green)  
6. Holdings/funds surfaces match Dhan Portfolio/Positions (read-only)  
7. Browser proof on exact serving SHA same session as Dhan screenshot

## Keep open while tracking

- System3: https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=chain  
- System3 broker: https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=broker  
- Dhan chain: https://web.dhan.co/advancedoptionchain  
- Dhan positions: https://web.dhan.co/index/positions  
- Dhan portfolio: https://web.dhan.co/index/portfolio  
