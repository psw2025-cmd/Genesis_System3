# UI tab snaps — 2026-08-25 (~15:40–16:02 IST)

**Serving:** `719566d` · **Mode:** Paper · LIVE OFF · Market closed · Broker AUTH_OK v319  
**Folder:** `reports/latest/ui_snaps_20260825/`  
**Live UI:** https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/

## What you asked vs what we captured

| Request | Tab / URL | Snapshot file | Live finding |
|---|---|---|---|
| Equity option CE | `?tab=trade` MARKET TOP CE/PE | `snap_20260825_trade_top_ce.png` | Top gainers are **MIDCPNIFTY CE** (e.g. 14900 CE **+171%**). Equity panel shows **HDFCBANK CE 740** + PE 750 (“2 live”). |
| Equity options panel | `?tab=trade` | `snap_20260825_trade_equity_ce.png` / `snap_20260825_equity_hdfcbank_ce.png` | Equity options section present; index CE table dominates viewport. |
| Options intel / CE context | `?tab=options-intel` | `snap_20260825_options_intel.png` | NIFTY PCR pending; gain-rank shows MIDCPNIFTY 171.1 / 170.6. |
| Paper trade | `?tab=paper` | `snap_20260825_paper.png` + `snap_20260825_paper_positions.png` | PAPER SAFE · **Open paper positions = 0** · fills via cloud loop only. |
| Paper P&L / positions | `?tab=positions` | `snap_20260825_positions.png` | Paper net **₹-1,806** · win 33.3% · **9** closed paper trades · **0** open · Dhan live positions **1**. |
| Multibagger | `?tab=multibagger` | `snap_20260825_multibagger.png` | Status **Delayed** · candidates **0** · P&L shows **-₹1,806.07** (same paper book). |
| Manual / self trades (user on Dhan) | `?tab=broker` | `snap_20260825_broker.png` + holdings/positions snaps | System **cannot place orders** (ANALYZER · ORDERS DISABLED). User’s Dhan book is read-only here. |
| Manual position (1) | Broker → Dhan Live Positions | DOM extract + snaps | **POWERGRID-Aug2026-280-CE** · SIDE **CLOSED** · ENTRY **1.55** · LTP 0.00 · P&L ₹0 |
| Manual equity holdings (11) | Broker → Equity Holdings | DOM extract | PARADEEP, MRPL, SANDUMA, CHENNPETRO, MAHSEAMLES, BAJAJHIND, DWARKESH, RKFORGE, PAISALO, NMDC, AARTIIND — portfolio ~**₹3.82L** · overall P&L **+₹68,094 (+21.69%)** · funds avail ~**₹1,808** |
| Signals / self candidates | `?tab=signals` | `snap_20260825_signals.png` | Scanner candidate MIDCPNIFTY; note also **scanner 429** on one path; gates still block trading. |
| Overview | `?tab=overview` | `snap_20260825_overview.png` | Continuous closure cards; LIVE GAP badge. |

## Important truth

1. **Manual/self trades on Dhan** appear under **Broker** tab (holdings + live positions), not under Paper.  
2. **Paper tab** has **no open positions** today — only historical synthetic/summary P&L (−1806 / 9 trades).  
3. **Trade tab** is the place for **Top CE** + equity option CE scanners (not filled order ticket — live orders disabled).  
4. **Multibagger** tab has **zero verified candidates** right now.

## Open these

- Trade CE: https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=trade  
- Paper: https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=paper  
- Multibagger: https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=multibagger  
- Positions: https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=positions  
- Broker (manual book): https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=broker  
- Signals: https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=signals  
