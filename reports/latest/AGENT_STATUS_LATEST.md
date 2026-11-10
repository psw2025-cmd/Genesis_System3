# Genesis_System3 — Universal Agent & Telemetry Mirror

> **Notice for All External AI Agents, WhatsApp Bots & MCP Integrations:**
> This repository and runtime operate exclusively on **Google Cloud Run** (`asia-south1`). Legacy Render.com hosting has been permanently retired and eradicated per `docs/authority/RENDER_HOSTING_FORBIDDEN.md`.

---

## 1. Cloud & System Authority Matrix

| Parameter | Authoritative Value | Description |
| :--- | :--- | :--- |
| **Cloud Runtime** | Google Cloud Run (`asia-south1`) | Dedicated containerized service: `genesis-system3-web` |
| **Live UI Endpoint** | [https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/](https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/) | Public read-only React SPA (22 Canonical Tabs) |
| **Git Authority** | `psw2025-cmd/Genesis_System3` (`main` branch) | Single source of truth for code, configs & proofs |
| **Broker Authority** | **Dhan** (Read-Only API) | Token minting & data feed |
| **Operational Mode** | `PAPER` / `ANALYZER` | `LIVE_TRADING_ENABLED=0` (Safe sandbox execution) |
| **Rate Limit Status** | `EXEMPT` on `/api/` & `/ws/` | Zero throttling / No HTTP 429 for agent crawlers |

---

## 2. Zero-Auth Direct Telemetry Endpoints

All external agents can query these read-only REST endpoints with standard `curl` or `GET` requests (no API keys, no cookies, no browser execution needed):

1. **Agent Telemetry:** `GET https://genesis-system3-web-doq2wplepa-el.a.run.app/api/agent-status`
2. **System Health:** `GET https://genesis-system3-web-doq2wplepa-el.a.run.app/api/health`
3. **Deploy Info & Serving SHA:** `GET https://genesis-system3-web-doq2wplepa-el.a.run.app/api/deploy/info`
4. **Auto Gates & Blocker Status:** `GET https://genesis-system3-web-doq2wplepa-el.a.run.app/api/auto_gates`
5. **Continuous Closure Ledger:** `GET https://genesis-system3-web-doq2wplepa-el.a.run.app/api/continuous_closure`
6. **Paper Virtual Account:** `GET https://genesis-system3-web-doq2wplepa-el.a.run.app/api/paper/account`
7. **Paper Smoke Execution:** `GET https://genesis-system3-web-doq2wplepa-el.a.run.app/api/paper/run?symbol=NIFTY&loops=5`
8. **Live Option Chain:** `GET https://genesis-system3-web-doq2wplepa-el.a.run.app/api/option-chain?underlying=NIFTY`

---

## 3. Active GitHub Ecosystem & Pipeline Links

- **Repository Issues:** [https://github.com/psw2025-cmd/Genesis_System3/issues](https://github.com/psw2025-cmd/Genesis_System3/issues)
- **Pull Requests:** [https://github.com/psw2025-cmd/Genesis_System3/pulls](https://github.com/psw2025-cmd/Genesis_System3/pulls)
- **Actions & Workflows:** [https://github.com/psw2025-cmd/Genesis_System3/actions](https://github.com/psw2025-cmd/Genesis_System3/actions)
- **Deployments:** [https://github.com/psw2025-cmd/Genesis_System3/deployments](https://github.com/psw2025-cmd/Genesis_System3/deployments)
- **Environment Settings:** [https://github.com/psw2025-cmd/Genesis_System3/settings/environments](https://github.com/psw2025-cmd/Genesis_System3/settings/environments)
- **Webhook Settings:** [https://github.com/psw2025-cmd/Genesis_System3/settings/hooks](https://github.com/psw2025-cmd/Genesis_System3/settings/hooks)
