# Continuous Closure System — operator map

**Goal:** minimal manual work; continuous issue resolution across sessions.

**Entry points**
- CLI: `python scripts/system3_continuous_closure_orchestrator.py`
- Offline: `python scripts/system3_continuous_closure_orchestrator.py --offline`
- API: `GET /api/continuous_closure`
- UI: Overview → **Continuous Closure · Blocker Cards**
- Resume file: `reports/latest/continuous_closure/resume_state.json`

**Pipeline**

```text
1 REPO-FIRST SCAN     BACKLOG.md + agent_policy
2 MULTI-SOURCE VERIFY repo · reports · live URL APIs
3 WATCHDOG            open vs resolved · banner required?
4 BLOCKER CARDS       merged fail-closed cards
5 AUTO-RESUME         next OPEN/IN_PROGRESS id + instruction
```

**Next session / Automation tick**
1. Read `resume_state.json` + `BACKLOG.md`
2. Execute `next_id` test-first under `tests/evals/`
3. Ship → live SHA verify → update BACKLOG → re-run orchestrator
4. Never invent prices/ρ; never weaken gates; LIVE stays false

**Policy companions:** `agent_policy.yaml`, Gemini loop doc, E2E issues→solutions law.
