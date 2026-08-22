# Cursor → ChatGPT path index

Status: ACTIVE GitHub authority on `main` after PR #319. Gmail is transport/mirror only.
Updated: 2026-08-22T10:34:40Z
Cursor lane: `cursor/ruhi-b002-serving-recapture-2b45`
Docs-only main at index write: `f9a0fe6ce4e66ca2012c08a645a6bad0887a60cb` (PR #319 merge)
Serving / runtime-affecting SHA: `3661b61b4543a6f45b0ecf48a56cd0f765716881` (PR #318; recaptured 2026-08-22T10:33:52Z)
Access: any agent with repo read can open these paths on GitHub. Updates go through PR → main.

Lines 20–22 are working on `main`: ledger, this-batch B002 status, and Issue #188. Do not recreate them.

Read these files in this order before accepting or contradicting Cursor work.

## Authority (always)

| Path | Why |
|---|---|
| `AGENTS.md` | Universal agent contract |
| `docs/RUHI_RULE_V2.md` | Cloud-only multi-agent execution contract |
| `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md` | `latest` is not `live` |
| `docs/authority/AUTONOMOUS_OPERATIONS_POLICY.md` | GCP/Dhan/IAM safety |
| `docs/project_control/SYSTEM3_MASTER_GOAL_LOCK.md` | Master objective + LIVE locks |
| `docs/project_control/CATALYST_EARLY_WARNING_INTELLIGENCE_PLAN.md` | Catalyst/news source, provider-failover, prediction, option, multibagger, UI and proof authority; read before any catalyst implementation |
| `docs/handoffs/MULTI_AI_COORDINATION_LIVE.md` | Live multi-agent handoff snapshot |
| `reports/coordination/ruhi_task_ledger.csv` | Rolling task IDs / ownership / proof |
| `docs/handoffs/RUHI_B002_CURSOR_STATUS.md` | This batch's RUHI status block |
| GitHub Issue #188 | Append-only runtime/progress bus |
| `reports/coordination/chatgpt_backlog/` | Shared ChatGPT analysis CSVs any agent can update |

## Catalyst Early Warning directive

- Do **not** interrupt or widen Cursor RUHI-022 / PR #321.
- Do **not** implement a giant news feature directly.
- After the current owned P0 lane is clear, the first Catalyst task is **read-only Phase 0 source inventory** from `docs/project_control/CATALYST_EARLY_WARNING_INTELLIGENCE_PLAN.md`.
- First required artifact: `reports/coordination/catalyst_source_capability_matrix.csv`.
- The free official baseline must keep working without premium subscriptions; paid providers are optional adapters/enrichment and may never become a single point of failure.
- The target is not a news widget: it is `source -> catalyst -> historical analogue -> current market/option confirmation -> early-move state -> Top-10 PAPER prediction -> immutable outcome -> calibration`.
- Index options, equity options and multibagger research remain separate model horizons/surfaces.
- No catalyst/news implementation may claim DONE without exact source timestamps/provenance, point-in-time anti-lookahead proof, model/outcome artifacts and exact-serving API->store->UI semantic evidence.

## ChatGPT backlog CSVs (any agent may update)

| Path | Contents |
|---|---|
| `reports/coordination/chatgpt_backlog/README.md` | How to use/update these files |
| `reports/coordination/chatgpt_backlog/system3_proof_requirements.csv` | P01–P15 proof requirements |
| `reports/coordination/chatgpt_backlog/system3_micro_execution_plan.csv` | Phase 0–5 execution plan |
| `reports/coordination/chatgpt_backlog/system3_micro_issue_master.csv` | M001+ micro issues |
| `reports/coordination/chatgpt_backlog/system3_micro_proof_matrix.csv` | Micro proof matrix |
| `reports/coordination/chatgpt_backlog/system3_screenshot_evidence_register.csv` | Screenshot evidence register |
| `reports/coordination/chatgpt_backlog/system3_world_class_recommendations.csv` | World-class recommendations |

## This batch implementation

| Path | Why |
|---|---|
| `scripts/scheduler_health_gate.py` | Named scheduler-health gate (transport vs predicates) |
| `tests/test_scheduler_health_gate.py` | Adversarial predicate/transport/sanitizer tests |
| `tests/evals/test_eval_scheduler_health_gate.py` | Workflow wiring eval |
| `.github/workflows/cloud-run-auto-deploy.yml` | Canary/verify now call the gate; always-upload report |

## ChatGPT decision still required

| Path | Contradiction |
|---|---|
| `dashboard/backend/scheduler_contract.py` | Code SSOT expects rotate-daily `30 * * * *` Asia/Kolkata |
| Live Cloud Scheduler `genesis-system3-dhan-token-rotate-daily` | Observed `*/5 * * * *` Asia/Kolkata again at 2026-08-22T10:33:29Z |
| Named deploy artifact | https://github.com/psw2025-cmd/Genesis_System3/actions/runs/32567500703/artifacts/9474562356 |
| Persisted recapture | `reports/coordination/ruhi_b002_recapture_20260822T103352Z.json` |

Do not silently pick one. That mismatch is why `/api/scheduler/health` is `healthy=false` / `alert_severity=critical`.

## Open docs PRs Cursor did not overwrite

| PR | Path / surface |
|---|---|
| #315 | `docs/project_control/AGENT_COORDINATION_CENTER.md`, `docs/project_control/AGENT_TASK_LEDGER.md` |
| #317 | `.cursor/rules/governance-watchdog.mdc` coordination contract |
| #304 | `docs/handoffs/CODEX_CLI_RUHI_EXECUTION.md` |
| #286 | stale scheduler-health engine; **do not merge**; superseded by merged #318 |

## Production URLs

- UI: `https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/`
- Deploy info: `https://genesis-system3-web-doq2wplepa-el.a.run.app/api/deploy/info`
- Broker status: `https://genesis-system3-web-doq2wplepa-el.a.run.app/api/broker/status`
- Scheduler health: `https://genesis-system3-web-doq2wplepa-el.a.run.app/api/scheduler/health?refresh=true`

## Mail rule

Gmail is fallback/mirror. Any material decision from mail must be written back to Issue #188 and one of the files above before merge/deploy.
