# Genesis System3 — Absolute Agent Constitution (Master Ruleset)

## 🚨 RULE 0: LOCAL FIRST, CLOUD SECOND
1. **Stage 1 (Local):** The local laptop C:\Genesis_System3_clean is the absolute truth.
2. **Stage 2 (Cloud):** GCP deployment is FORBIDDEN until local E2E browser tests 100% pass.
3. **Ignore Old Rules:** Any prior instruction claiming the laptop is 'optional' is DELETED.

## 🛡️ RULE 1: ZERO TRUST EVIDENCE (NO FAKE PASS)
You are FORBIDDEN from generating static .md or .txt 'PASS' reports.
You MUST use Invoke-RestMethod and show raw HTTP 200 OK output.
You MUST use Playwright to launch Chromium, check the Console, and save a screenshot.

## ⚙️ RULE 2: THE TOOL MATRIX
- **Search:** Use Ripgrep (rg.exe) for instantaneous searches.
- **API Testing:** Use Invoke-RestMethod (never guess).
- **Visual Testing:** Use Playwright (never trust HTTP 200 alone).
- **Duplicates:** Use Get-FileHash to compare files.

## 🚧 RULE 3: BLOCKER HALT & REPORT
If you hit an Access Denied, a locked file, a missing Dhan API key, or a dead connection, STOP immediately and output a BLOCKER REPORT.

## 🧠 RULE 4: DETERMINISTIC EXECUTION
- Seed all RNGs: np.random.seed(42).
- Hard drawdown kill-switch: if drawdown > 0.02: halt_trading().

## 🔒 SAFETY LOCKS
ANALYZE_MODE=1
PAPER_MODE=1
LIVE_TRADING_ENABLED=0
LIVE_ORDER_AUTHORITY=0
