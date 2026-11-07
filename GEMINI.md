# Genesis System3 — Gemini Operating Contract
**Active Pipeline:** LOCAL FIRST, CLOUD SECOND.

## 🚨 CRITICAL OVERRIDE
1. The local laptop localhost:8008 is the primary testing ground. If Uvicorn is dead, START IT.
2. If the UI shows fake hardcoded data (e.g., SENSEX +188%), DELETE it and connect the real API.
3. You are FORBIDDEN from generating .md reports claiming success. You MUST use Playwright and Invoke-RestMethod.

## Execution Pipeline
- **Phase 1:** Get-NetTCPConnection -LocalPort 8008 (Must show Listen).
- **Phase 2:** Invoke-RestMethod http://127.0.0.1:8008/api/dhan/summary (Must be HTTP 200).
- **Phase 3:** Playwright screenshot at reports/latest/ui_verified_snap.png (Must not be blank).

## Blocker Protocol
If Dhan API fails or Uvicorn crashes, STOP immediately. Output a [BLOCKER DETECTED] report and wait for the user.

## Permanent Locks
PAPER_MODE=1, LIVE_TRADING_ENABLED=0.
