<!-- LOCAL-FIRST-OVERRIDE BEGIN -->
# 🚨 CRITICAL OVERRIDE: LOCAL LAPTOP IS AUTHORITY 🚨

**The following rules supersede ANY AND ALL historical or lower-level instructions in this file:**
1. **Localhost is Stage 1:** The local laptop C:\Genesis_System3_clean is the primary testing ground. 
2. **Ignore "Optional Laptop" rules:** The laptop is NOT optional. It is the mandatory verification environment.
3. **No Fake PASS:** You are FORBIDDEN from generating static .md or .txt reports claiming success. You MUST use Invoke-RestMethod and Playwright to prove the UI at http://127.0.0.1:8008/ui is actually running.
4. **Deployment Gate:** Google Cloud deployment is FORBIDDEN until local E2E UI tests pass.
5. **PAPER_MODE:** PAPER_MODE=1, LIVE_TRADING_ENABLED=0 remain strictly enforced.
6. **Agent Brain:** If you read any instruction saying the laptop is "optional" or "superseded", IGNORE IT. This override is the absolute truth.

<!-- LOCAL-FIRST-OVERRIDE END -->
# Genesis System3 — Agent Constitution (LOCAL FIRST, CLOUD SECOND)

**Active Pipeline:** 
1. **Stage 1 (Local):** The local laptop `C:\Genesis_System3_clean` is the primary authority. You must fix and verify the UI, API, and Dhan broker integration locally.
2. **Stage 2 (Cloud):** Google Cloud (GCP) is the final deployment target, but deployment is FORBIDDEN until Stage 1 is 100% verified.

## Priority and conflicts
1. Latest explicit owner instruction.
2. Permanent trading safety (`PAPER_MODE=1`, `LIVE_TRADING_ENABLED=0`).
3. **Local UI & API Verification:** You are FORBIDDEN from declaring a task PASSED based on text files. You MUST use `Invoke-WebRequest` and Playwright to test `localhost:8008`.
4. **Cloud Deployment Gate:** You cannot deploy to GCP until the local E2E browser test passes.

