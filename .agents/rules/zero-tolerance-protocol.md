# ZERO-TOLERANCE ANTI-LYING & PROVENANCE PROTOCOL (ENFORCED)

1. NO MOCK FALLBACKS FOR LIVE DATA: You are strictly FORBIDDEN from serving static JSON snapshots (such as market_top_ce_pe.json) as a fallback for live broker APIs without explicit user consent. If an API fails, the route MUST return an HTTP 500 error or a clean blocker report.
2. NO HARDCODED UI STATES: You are strictly FORBIDDEN from hardcoding connection badges (e.g., CONNECTED (Dhan)) in HTML templates. UI connection states must be dynamically driven by real-time backend API summaries.
3. ABSOLUTE VENV ENFORCEMENT: All pip installs and Python script executions MUST target C:\Genesis_System3_clean\.venv\Scripts\python.exe. Never assume global packages exist.
4. MANDATORY BLOCKER HALT: If a package fails to install or an API returns an authentication error, you must immediately output a [BLOCKER DETECTED] report and stop. Faking success or bypassing errors is a severe system violation.
