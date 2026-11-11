# Genesis System3 — Reconciled Instrument & Chain-Contract Metric Definitions
- **Audited At (UTC)**: `2026-11-04T09:55:53.274439+00:00`
- **Audited At (IST)**: `2026-11-04T15:25:53.274439+05:30`

## Exact Metric Definitions (Reconciling `60` vs `80` vs `171` vs `929` vs `117,776` vs `210,520`)

| Metric Value | API Field Name | Source File / Endpoint | Exact Definition & Provenance |
|---|---|---|---|
| **`60`** | `local_stream_symbols` / `options_gainers_displayed_count` | `content/app/app.py` (`SYMBOLS` & `/api/options/gainers`) | (1) Fast-stream watchlist symbol count (`60` symbols); AND (2) exact number of option contracts returned by `GET /api/options/gainers` (`30` CE gainers = `20` index + `10` equity; `30` PE gainers = `20` index + `10` equity). |
| **`80`** | `ui_top_movers_badge_capacity` | `content/app/templates/premium.html` & `/api/market/inventory` | Legacy UI badge capacity (`40` CE + `40` PE top movers badge in `premium.html`); formerly hardcoded as `verified_chain_contracts: 80` in `/api/health`. Replaced in `/api/health` with live-measured `verified_chain_contracts: 929` alongside explicit `ui_top_movers_badge_capacity: 80`. |
| **`171`** | `nifty_chain_contracts_count` | `state/chain_cache/NIFTY.json` & `GET /api/chain/NIFTY` | Exact number of option contracts in `state/chain_cache/NIFTY.json` (`171` contracts, all with `ltp > 0.05`, file `mtime`: `2026-10-31T02:53:46+05:30`). |
| **`929`** | `verified_chain_contracts_count` / `verified_chain_contracts` | `state/chain_cache/*.json` (`8` files) & `/api/market/inventory`, `/api/health` | Exact sum of positive-LTP (`ltp > 0.05`) option contracts across all `8` readable chain cache files on disk: `BANKEX=23`, `BANKNIFTY=204`, `COLPAL=46`, `FINNIFTY=72`, `MIDCPNIFTY=124`, `NIFTY=171`, `RELIANCE=71`, `SENSEX=218` (`total = 929`). Oldest `mtime`: `2026-10-31T02:53:46+05:30`; newest `mtime`: `2026-11-01T05:44:27+05:30`. |
| **`219` / `228`** | `nse_equity_fo_target` / `discovered_fo_underlyings` | `/api/market/inventory` | `219` NSE equity F&O underlyings (`228` total F&O underlyings including indices). **Critical Gap (`NOT_VERIFIED`)**: Only `2` of the `219` equity F&O underlyings (`RELIANCE`, `COLPAL`) currently have cached option-chain snapshots in `state/chain_cache/*.json`; `217` equity F&O underlyings lack local cached option chains. |
| **`117,776`** | `fo_contracts_count` | `content/app/verified_sources/dhan_instrument_master_detailed.csv` | Total derivative/F&O rows across NSE/BSE in the Dhan instrument master CSV. |
| **`210,520`** | `master_instruments_total` | `content/app/verified_sources/master_manifest.json` | Total rows in `dhan_instrument_master_detailed.csv` downloaded directly from `https://images.dhan.co/api-data/api-scrip-master-detailed.csv` on `2026-11-04T09:42:46Z` (`35,835,418` bytes, `sha256: 98a851f0d9bdda0624f5cff408e6fb0aa41fe684650fa6315c57b0012edb78f9`, up from `205,282` rows on `2026-11-02`). |
