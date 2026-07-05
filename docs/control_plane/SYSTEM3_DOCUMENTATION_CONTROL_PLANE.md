# System3 Documentation Control Plane

## Purpose

System3 has many historical `.md` reports. This file defines how documentation must be controlled so old reports do not override current runtime truth.

The problem is not lack of documentation. The problem is uncontrolled documentation truth.

## Current Finding

Repo inspection shows strong architecture/control documents already exist, including:

- `docs/SYSTEM3_CORE_TRADING_GOAL_AND_ARCHITECTURE.md`
- `docs/SYSTEM3_SINGLE_ASSISTANT_RESPONSIBILITY_RULE.md`
- `docs/runtime/AUTHORITATIVE_RUNTIME_AND_DATA_MAP.md`
- `docs/architecture/MASTER_PR_ROADMAP.md`
- `docs/architecture/SYSTEM3_BRUTAL_GAP_ANALYSIS.md`

But the repo also contains many older docs with names including `FINAL`, `COMPLETE`, `VALIDATION`, `STATUS`, `SUMMARY`, and `REPORT`. Those may be useful evidence, but they must not be treated as current truth unless the master tracker confirms them.

## Documentation Classes

Every `.md` file must be classified into exactly one class:

| Class | Meaning |
|---|---|
| ACTIVE_CONTROL | Current decision/control document |
| REFERENCE | Stable reference or architecture note |
| HISTORICAL_REPORT | Past report, useful evidence, not current truth |
| ARCHIVE_CANDIDATE | Likely old/duplicated doc to move later |
| DUPLICATE_RISK | Similar to another doc and may confuse agents |
| UNKNOWN | Needs manual review |

## Active Control Documents

Only these documents can define current truth:

| File | Class |
|---|---|
| `SYSTEM3_MASTER_TRACKER.md` | ACTIVE_CONTROL |
| `SYSTEM3_BLOCKER_REGISTER.md` | ACTIVE_CONTROL |
| `docs/control_plane/SYSTEM3_CURRENT_RUNTIME_TRUTH.md` | ACTIVE_CONTROL |
| `docs/control_plane/SYSTEM3_SIGNAL_TO_TRADE_CONTROL.md` | ACTIVE_CONTROL |
| `docs/control_plane/SYSTEM3_MODEL_ACCURACY_REGISTER.md` | ACTIVE_CONTROL |
| `docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md` | ACTIVE_CONTROL |
| `docs/control_plane/SYSTEM3_DOCUMENTATION_CONTROL_PLANE.md` | ACTIVE_CONTROL |
| `docs/SYSTEM3_CORE_TRADING_GOAL_AND_ARCHITECTURE.md` | ACTIVE_CONTROL |
| `docs/SYSTEM3_SINGLE_ASSISTANT_RESPONSIBILITY_RULE.md` | ACTIVE_CONTROL |
| `docs/runtime/AUTHORITATIVE_RUNTIME_AND_DATA_MAP.md` | ACTIVE_CONTROL |
| `docs/architecture/MASTER_PR_ROADMAP.md` | REFERENCE |
| `docs/architecture/SYSTEM3_BRUTAL_GAP_ANALYSIS.md` | REFERENCE |

## Contradiction Rules

A documentation contradiction exists when an old document says:

- `FINAL`
- `COMPLETE`
- `PASS`
- `READY`
- `CERTIFIED`
- `8/8`
- `TRADE_READY`
- `LIVE_READY`

but current master tracker or runtime truth says:

- blocker open,
- PAPER only,
- model accuracy insufficient,
- option strike/token not proven,
- paper lifecycle pending,
- false alert loop active,
- dashboard proof gates hard-coded/contradictory.

## Required Inventory Outputs

A future script must generate:

```text
reports/latest/markdown_inventory.md
reports/latest/markdown_inventory.json
reports/latest/documentation_contradictions.md
```

The inventory should include:

| Field | Meaning |
|---|---|
| `path` | Markdown file path |
| `title` | First heading if available |
| `class` | ACTIVE_CONTROL / REFERENCE / HISTORICAL_REPORT / ARCHIVE_CANDIDATE / DUPLICATE_RISK / UNKNOWN |
| `risk_terms` | final/complete/pass/ready/etc. |
| `current_truth_conflict` | true/false |
| `recommended_action` | keep, reference, archive later, review |

## No-Delete Policy

Do not delete old docs immediately.

Safe sequence:

```text
inventory -> classify -> contradiction report -> archive proposal -> user approval -> move/archive later
```

## World-Class Documentation Standard Applied

Professional ML/trading systems require:

- a current truth source,
- data and model documentation,
- model validation records,
- incident/postmortem records,
- runbooks,
- change records,
- blocker registers,
- proof artifacts.

System3 must follow this by making current truth explicit and historical reports subordinate to the active control plane.

## Current Documentation Verdict

| Area | Verdict |
|---|---|
| Architecture docs | Strong but planning-heavy |
| Historical reports | Too many and potentially contradictory |
| Current truth docs | Now created but must be kept updated |
| Markdown inventory | Missing |
| Contradiction report | Missing |
| Archive classification | Missing |

## Next Documentation Action

Create `scripts/system3_markdown_inventory.py` to classify all `.md` files and generate inventory/contradiction reports. Do not delete anything until that report exists.
