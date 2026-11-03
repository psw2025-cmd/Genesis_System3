# Genesis System3 — Gemini Operating Contract (LOCAL FIRST, CLOUD SECOND)

**Active owner directive:** Test and repair the local workstation at `C:\Genesis_System3_clean` FIRST. The "cloud-only" directive is SUSPENDED until local verification is complete.

## Core Rules
1. **Localhost is Stage 1:** The UI at `http://127.0.0.1:8008/ui` must be fully functional. 
2. **Dhan Broker:** Ensure the Dhan API routes (`/api/dhan/summary`, `/api/depth`) return HTTP 200 OK locally.
3. **No Fake PASS:** You MUST execute `Invoke-RestMethod` and use Playwright to prove the UI works.
4. **PAPER_MODE:** `PAPER_MODE=1`, `LIVE_TRADING_ENABLED=0`. No live orders, but paper trading MUST function and write to the database.
5. **Cloud Gate:** Only after local E2E tests pass, you may prepare the GitHub commit and GCP deployment scripts.
