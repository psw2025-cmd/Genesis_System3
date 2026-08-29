## RUHI STATUS — Cursor — Dhan live parity P0 board (2026-08-25)

**Claim:** live tracking Dhan↔System3 market match (chain/equity/charts) — docs + issue ledger updated; implementation not claimed DONE.

### Live (serving `719566d`, broker Session OK, PAPER/LIVE OFF)
- UI `/?tab=chain`: **DHAN EXPIRY SNAPSHOT** with `fetched=07:49Z` while session clock ~09:09Z → stale/false-green risk
- Visible strikes **27050+** vs spot **~24130** → ATM not centered
- Missing vs Dhan advanced chain: **LTP Chg %**, **Buildup**, **OI/Vol chg %**, **Greeks** in table (API has change_percent + greeks)
- `/api/holdings` `/api/funds` `/api/charts/NIFTY` → **404**
- Serving behind GitHub main `2c0b44a`

### Docs
- `docs/RUHI_RULE_V2.md` §16 Dhan live market parity (HIGH PRIORITY)
- `docs/handoffs/SYSTEM3_MASTER_AUTOMATION_RUNBOOK.md` §3 parity board
- `reports/latest/dhan_parity/DHAN_LIVE_PARITY_ISSUES.md`

USER_ACTION_REQUIRED: NONE (keep Dhan + System3 chain tabs open for continuous compare)
