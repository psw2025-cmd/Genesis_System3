# Genesis System3 — Agent Constitution (LOCAL FIRST, CLOUD SECOND)

**Active Pipeline:** 
1. **Stage 1 (Local):** The local laptop `C:\Genesis_System3_clean` is the primary authority. You must fix and verify the UI, API, and Dhan broker integration locally.
2. **Stage 2 (Cloud):** Google Cloud (GCP) is the final deployment target, but deployment is FORBIDDEN until Stage 1 is 100% verified.

## Priority and conflicts
1. Latest explicit owner instruction.
2. Permanent trading safety (`PAPER_MODE=1`, `LIVE_TRADING_ENABLED=0`).
3. **Local UI & API Verification:** You are FORBIDDEN from declaring a task PASSED based on text files. You MUST use `Invoke-WebRequest` and Playwright to test `localhost:8008`.
4. **Cloud Deployment Gate:** You cannot deploy to GCP until the local E2E browser test passes.
