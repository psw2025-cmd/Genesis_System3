# Genesis System3 — Reconciled File & Forensic Inventory
- **Observed UTC**: `2026-11-04T09:26:15.528711+00:00`
- **Observed IST**: `2026-11-04T14:56:15.528711+05:30`
- **Authoritative Repo**: `C:\Genesis_System3_clean`
- **Git Branch / HEAD**: `fix/scanner-219-equity-rotate` / `d5ad4d0c7a9dc3c26ad13666fb791bb9e2a13a82`

## Summary Counts (Independently Reproduced)
- **Tracked Git Paths (`git ls-files`)**: `3,197`
- **Scanned On-Disk Eligible Files (`GENESIS_DEEP_FORENSIC_AST_HASH.json`)**: `2,150`
- **Python Files Parsed via AST (`ast.parse`)**: `953` (`0` syntax errors)
- **Worktree Dirty Entries (`git status --porcelain`)**: `1,140` (preserved; 0 destructive git operations executed)
- **Dhan 100-Check Forensic Batch (`DHAN_FORENSIC_100_RESULTS.json`)**: `90 PRESENT`, `8 TRACKED_MISSING` (`reports/latest/dhan_parity/*`, `dhan_token_issuer_forensics/summary.json`, `dhan_option_chain_schema_audit/summary.md`, `dhan_advance_platform_verification/summary.md`), `2 NOT_FOUND` (`src/dhan/missing.py` negative control + `reports/latest/dhan_parity` directory).

## Key Modified Runtime & Remediation Files (SHA-256 Verified)
| Relative Path | Role | SHA-256 | Status |
|---|---|---|---|
| `content/app/app.py` | Active Port 8008 Institutional Command Center & 653-Route FastAPI Server | `ce8adaf14d0fff5129a4238c21501eb188d51d3415f2c04a9f351086b93fb021` | `PASS (MODIFIED & VERIFIED)` |
| `content/app/dhan_account_router.py` | Live Dhan Demat Holdings (11 Stocks), Funds & Profile Router | `9101a6c4ecb7c480784f348a4f7b2e40c4d9b4edca40412647f28d30f004b6f9` | `PASS (MODIFIED & VERIFIED)` |
| `content/app/verified_market.py` | Verified Dhan Market Quotes (`NIFTY`, `BANKNIFTY`, `SENSEX`) | `2211097daa66525ef14d922c5c9bddc94ef7022d3dee2e13a751f52ab3fca8d8` | `PASS (VERIFIED)` |
| `content/app/templates/premium.html` | Institutional Command Center UI Template (Port 8008 `/ui`) | `f10323df0ecf5dc2583aede314e597419b7566c9025317aa865679d9105291cd` | `PASS (MODIFIED & VERIFIED)` |
| `dashboard/backend/app.py` | Dashboard Backend (`REP-002` bare-except zero-masking remediated) | `c7c5e0b342ec3318679cfeb4453f9d041c62431a4445469f5b69aada2aa7aa48` | `PASS (MODIFIED & VERIFIED)` |
| `dashboard/backend/greeks_calculator.py` | Option Greeks Calculator (`REP-015` IST expiry arithmetic fixed) | `dd0af2bf194c4cc902e2e5333ed11efce8a794c9ede681d019f83058ee5d0ac9` | `PASS (MODIFIED & VERIFIED)` |
| `dashboard/backend/paper_pipeline_v8.py` | Paper Pipeline (`REP-016` IST fallback timezone fixed) | `8e3cf816ef49f0dde89b206f340cfeeb80abe3cab0c0b2e51ff8be3f6d26c1c0` | `PASS (MODIFIED & VERIFIED)` |
| `dashboard/backend/runtime_state_store.py` | Runtime State Store (`REP-018` UTC timezone-aware timestamps fixed) | `172bfb4b377f674a26380ac1533796598d9bb68d4032fb156aeb61fc7d895d95` | `PASS (MODIFIED & VERIFIED)` |
| `dashboard/backend/services/moneycontrol_live.py` | Moneycontrol Benchmark Scraper (`OBS-009` / `REP-019` fixed) | `bd2ea32e3b1275d30dd89b76e4a15a931f963722718a97e56754b27827a6c88f` | `PASS (MODIFIED & VERIFIED)` |
| `docs/DHAN_BROKER_API_ANALYSIS.md` | Dhan Broker Docs (`DH-012`/`DH-013` AngelOne URL mix-up reconciled) | `039bdfb022459303b969984548e983c4a2d7235000802ea1ef81c67fd081c587` | `PASS (MODIFIED & VERIFIED)` |
