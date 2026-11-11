# Genesis 8008 Local UI Truth Correction — November 2, 2026

Scope: Local experimental app only, at C:\content\app (not independently certified production, not the GCP deployed runtime).

## Confirmed before fixes
- The running 8008 process used uvicorn app:app from C:\content\app.
- Backend configured exactly 60 symbols and generated random-walk market ticks, market depth, ML and paper-trading demonstration values.
- The common JSON envelope applied real:true to those values and included unverified live-market provenance.
- Original UI contained false 2,000+ monitoring labels, hardcoded live latencies, artificial chart scaling, OI undefined%, and unverified green paper-accuracy badges.

## Changes made
- Backed up app.py and premium.html under C:\content\app\truth_backups\20261102T162014Z before patching.
- Backend common envelope now real:false, simulated/unverified classification; health source/uptime/market inventory, broker provenance, route statuses and ML walk-forward status corrected.
- UI shows "PROTOTYPE — NOT CERTIFIED / FEED NOT LIVE-VERIFIED", changes 2,000+ claimed instruments to 60 demo symbols, flags route health unverified, normalizes multi-symbol chart return comparisons, deduplicates CE/PE display rows and displays missing OI as a dash.
- Repaired a malformed additional scanner return fragment that caused Python startup syntax failure during concurrent changes.

## Tests observed
- Python py_compile: PASS.
- UI inline JavaScript node --check: PASS.
- Local HTTP 8008 /ui: 200 and truth warning present.
- 12 safe GET endpoints: /api/health, /api/settings, /api/route-health, /api/data/provenance, /api/market/inventory, /api/market/missing-symbols, /api/market, /api/options/gainers, /api/ml/prediction-audit, /api/paper/ledger, /api/depth?symbol=RELIANCE, /api/routes; all reported real:false.
- Running local backend reported LOCAL_API_UP_FEED_UNVERIFIED and 60 symbols.
- No broker order endpoints called. No cloud changes or real orders executed.

## Remaining
- Real Dhan/exchange tick authentication not proven.
- True all-eligible symbol and F&O subscription coverage not implemented by local prototype.
- Demo paper P&L, trade receipts, ML accuracy, strategy benchmarks, risk and dynamic broker health must be replaced by independently sourced verified data.
- All 1,872 institutional acceptance checks remain UNVERIFIED in independent register. Do not use historical 1,872/1,872 PASS as certification.
- Re-check startup and UI after future concurrent modifications.
