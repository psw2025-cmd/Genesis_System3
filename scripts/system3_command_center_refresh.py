#!/usr/bin/env python3
"""System3 Command Center — ONE overwrite source for agents.

Replaces repeating manual probes. Always overwrites:
  reports/coordination/COMMAND_CENTER.md
  reports/coordination/ISSUES_ONLY.md
  reports/coordination/ISSUES_MERMAID.md
  reports/coordination/TRACKING_CHECKLIST.* (via tracker)
  reports/coordination/AGENT_OPERATING_OPTIONS.xlsx (via builder)

Usage (after any edit OR on schedule):
  python scripts/system3_command_center_refresh.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "coordination"
PY = sys.executable
POLICY = OUT / "ACCESS_POLICY.yaml"
SMOKE = OUT / "SMOKE_TEST_LAST.json"
AUDIT = OUT / "AUDIT_LOG.jsonl"


def run(script: str) -> None:
    subprocess.check_call([PY, str(ROOT / "scripts" / script)], cwd=str(ROOT))


def load_track() -> dict:
    p = OUT / "TRACKING_CHECKLIST.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def load_policy_meta() -> dict:
    if not POLICY.exists():
        return {}
    text = POLICY.read_text(encoding="utf-8")
    meta = {}
    for key in ("policy_id", "signature_status", "signed_by", "approver_email", "notify_channel", "version"):
        for line in text.splitlines():
            if line.strip().startswith(f"{key}:"):
                meta[key] = line.split(":", 1)[1].strip().strip('"')
                break
    return meta


def load_smoke() -> dict:
    if not SMOKE.exists():
        return {}
    try:
        return json.loads(SMOKE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def last_audit_id() -> str:
    if not AUDIT.exists():
        return ""
    lines = [ln for ln in AUDIT.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        return ""
    try:
        return json.loads(lines[-1]).get("entry_id", "")
    except json.JSONDecodeError:
        return ""


def issues_only_md(data: dict) -> str:
    live = data.get("live") or {}
    now = datetime.now(timezone.utc).isoformat()
    run_id = os.environ.get("CC_RUN_ID") or os.environ.get("GITHUB_RUN_ID") or f"local-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    rows = [r for r in (data.get("rows") or []) if r.get("status") in {"OPEN", "IN_PROGRESS", "WATCH"}]
    rows.sort(key=lambda r: (0 if r.get("pri") == "P0" else 1 if r.get("pri") == "P1" else 2, r.get("id") or ""))
    lines = [
        "# ISSUES ONLY (overwrite)",
        "",
        f"**UTC:** `{live.get('captured_utc') or now}`  ",
        f"**Serving:** `{live.get('serving_sha')}`  ",
        f"**Gates:** {live.get('gates_passing')}/{live.get('gates_total')}  ",
        f"**Broker:** {live.get('broker_auth')} v{live.get('broker_secret_version')}  ",
        f"**Scheduler healthy:** {live.get('scheduler_healthy')}  ",
        f"**last_run_id:** `{run_id}`  ",
        "",
        "## Access requests (credentials / human approval)",
        "",
        "| resource | reason | ttl_requested | approver | owner | ticket | ack_utc |",
        "|---|---|---|---|---|---|---|",
        f"| vault:SYSTEM3_CC_SIGNER_KEY + SYSTEM3_CC_SMOKE_TOKEN | signature_status UNSIGNED_PENDING_VAULT — mint denied | 1h | warghade2012@gmail.com | cursor-composer | issue:#188 | {now} |",
        "",
        "## Acknowledged P0 board (agent-owned; ack refreshed each command_center run)",
        "",
        "| ID | Pri | Status | Title | Live proof | Next | owner | ack_utc |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        ack = now if r.get("pri") == "P0" else ""
        owner = "cursor-composer" if r.get("pri") == "P0" else "shared"
        lines.append(
            f"| {r.get('id')} | {r.get('pri')} | {r.get('status')} | {r.get('title')} | {(r.get('live_proof') or '')[:90]} | {r.get('rec')} | {owner} | {ack} |"
        )
    lines.append("")
    lines.append("Full options Excel: `reports/coordination/AGENT_OPERATING_OPTIONS.xlsx`")
    lines.append("Open sheet `2_Options_Priority` — prefer rank 1 OPT-A1.")
    lines.append("")
    lines.append(
        'If vault mint is required, PR comment exactly: '
        '"Requesting approval: resource=vault:SYSTEM3_CC_SIGNER_KEY, reason=verify ACCESS_POLICY signature for ephemeral CC smoke token, ttl=1h, approver=warghade2012@gmail.com"'
    )
    return "\n".join(lines) + "\n"


def mermaid_md(data: dict) -> str:
    live = data.get("live") or {}
    open_ids = [r["id"] for r in (data.get("rows") or []) if r.get("status") in {"OPEN", "IN_PROGRESS"} and r.get("pri") == "P0"][:12]
    nodes = "\n".join([f'    {i.replace("-", "_")}["{i}"]' for i in open_ids]) or '    NONE["No P0"]'
    links = []
    # micro network: deploy -> ui -> paper -> ml
    mapping = {
        "PEND_001": ["PEND_004", "PEND_011"],
        "PEND_002": ["PEND_014", "PEND_017", "PEND_019"],
        "PEND_004": ["PEND_029"],
        "PEND_014": ["PEND_017", "PEND_018"],
        "PEND_021": ["PEND_014", "PEND_018"],
        "PEND_019": ["PEND_028"],
        "PEND_018": ["PEND_028"],
        "PEND_023": ["PEND_004", "PEND_028"],
    }
    present = {i.replace("-", "_") for i in open_ids}
    for src, dsts in mapping.items():
        if src not in present:
            continue
        for d in dsts:
            if d in present:
                links.append(f"    {src} --> {d}")
    link_txt = "\n".join(links) if links else "    NONE --> NONE"

    return f"""# ISSUES MERMAID (overwrite)

Serving `{live.get('serving_sha')}` · gates {live.get('gates_passing')}/{live.get('gates_total')}

## P0 dependency micro-network

```mermaid
flowchart LR
{nodes}
{link_txt}
```

## Full control loop

```mermaid
flowchart TD
  CC[command_center_refresh] --> T[TRACKING_CHECKLIST overwrite]
  CC --> X[AGENT_OPERATING_OPTIONS.xlsx]
  CC --> I[ISSUES_ONLY.md]
  CC --> M[ISSUES_MERMAID.md]
  T --> A[Agent picks highest P0]
  A --> E[Edit primary clone]
  E --> CC2[AUTO trigger command_center again]
  CC2 --> P[PR merge deploy]
  P --> S[Serving SHA proof]
  S --> B[Browser re-snap]
  B --> D{{Match?}}
  D -->|No| A
  D -->|Yes| DONE[Mark DONE on checklist]
```

## Advanced solution order (agent-first)

1. OPT-A1 deploy chain+API aliases  
2. OPT-A10 keep command_center as only probe source  
3. OPT-A3 deploy lag  
4. OPT-A4 scheduler  
5. OPT-A5 paper persistence  
6. OPT-A6 signals  
7. OPT-A7 ML gates (long)
"""


def command_center_md(data: dict) -> str:
    live = data.get("live") or {}
    counts = data.get("counts") or {}
    policy = load_policy_meta()
    smoke = load_smoke()
    run_id = os.environ.get("CC_RUN_ID") or os.environ.get("GITHUB_RUN_ID") or smoke.get("run_id") or "local-unknown"
    token_id = os.environ.get("CC_TOKEN_ID") or f"dryrun-{run_id}"
    ttl = os.environ.get("CC_TOKEN_TTL") or "0s-mint-denied"
    audit_id = last_audit_id()
    return f"""# COMMAND CENTER (overwrite — single source)

**Do not re-run ad-hoc curl/probe spam.** Refresh this file instead.

```powershell
# After ANY edit OR anytime (idempotent):
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_command_center_refresh.ps1
```

## Access / token metadata

| Field | Value |
|---|---|
| policy_id | `{policy.get('policy_id')}` |
| policy_version | `{policy.get('version')}` |
| signature_status | `{policy.get('signature_status')}` |
| signed_by | `{policy.get('signed_by')}` |
| last_run_id | `{run_id}` |
| token_id | `{token_id}` |
| token_ttl | `{ttl}` |
| mint_status | `DENIED until signature_status=VERIFIED` |
| smoke_passed | `{smoke.get('passed')}` |
| last_audit_entry_id | `{audit_id}` |
| notify_channel | `{policy.get('notify_channel')}` |
| approver_email | `{policy.get('approver_email')}` |

## Live snapshot

| Field | Value |
|---|---|
| UTC | {live.get('captured_utc')} |
| Serving | `{live.get('serving_sha')}` |
| Gates | {live.get('gates_passing')}/{live.get('gates_total')} trade_ready={live.get('trade_ready')} |
| Broker | {live.get('broker_auth')} v{live.get('broker_secret_version')} |
| Scheduler healthy | {live.get('scheduler_healthy')} |
| LIVE | {live.get('live_trading_enabled')} |
| OPEN / IN_PROGRESS / DONE | {counts.get('open')} / {counts.get('in_progress')} / {counts.get('done')} |
| P0 active | {counts.get('p0_active')} |

## Open these artifacts (always same paths)

| Artifact | Path |
|---|---|
| Issues only | `reports/coordination/ISSUES_ONLY.md` |
| Mermaid network | `reports/coordination/ISSUES_MERMAID.md` |
| Full checklist | `reports/coordination/TRACKING_CHECKLIST.md` |
| Options Excel | `reports/coordination/AGENT_OPERATING_OPTIONS.xlsx` |
| Access policy | `reports/coordination/ACCESS_POLICY.yaml` |
| Audit log | `reports/coordination/AUDIT_LOG.jsonl` |
| Smoke last | `reports/coordination/SMOKE_TEST_LAST.json` |
| Catalog | `docs/handoffs/SESSION_ISSUES_MASTER.md` |
| Runbook | `docs/handoffs/SYSTEM3_MASTER_AUTOMATION_RUNBOOK.md` |

## First priority for any agent

1. Read `ISSUES_ONLY.md`  
2. Open Excel sheet `2_Options_Priority` → **OPT-A1**  
3. If local fixes pending → get user **commit+PR** then deploy proof  
4. After edit finish → **run this command_center immediately** (do not wait for hourly schedule)  
5. Re-snap UI; flip DONE only on serving SHA  

## User minimal involvement

Primary path + approve PR + LIVE OFF + optional Dhan confirm. Everything else agent-automated.
"""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    if not os.environ.get("CC_RUN_ID") and not os.environ.get("GITHUB_RUN_ID"):
        os.environ["CC_RUN_ID"] = f"local-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    if not os.environ.get("CC_TOKEN_ID"):
        os.environ["CC_TOKEN_ID"] = f"dryrun-{os.environ['CC_RUN_ID']}"
    if not os.environ.get("CC_TOKEN_TTL"):
        os.environ["CC_TOKEN_TTL"] = "0s-mint-denied"

    run("system3_pending_tracker_refresh.py")
    run("system3_build_operating_options_xlsx.py")
    data = load_track()
    (OUT / "ISSUES_ONLY.md").write_text(issues_only_md(data), encoding="utf-8")
    (OUT / "ISSUES_MERMAID.md").write_text(mermaid_md(data), encoding="utf-8")
    (OUT / "COMMAND_CENTER.md").write_text(command_center_md(data), encoding="utf-8")
    # mirror
    mirror = ROOT / "reports" / "latest" / "tracking"
    mirror.mkdir(parents=True, exist_ok=True)
    for name in ("COMMAND_CENTER.md", "ISSUES_ONLY.md", "ISSUES_MERMAID.md"):
        (mirror / name).write_text((OUT / name).read_text(encoding="utf-8"), encoding="utf-8")
    print("COMMAND_CENTER refresh complete (overwrite-only).")
    print(f"Open {OUT / 'COMMAND_CENTER.md'}")
    print(f"Excel {OUT / 'AGENT_OPERATING_OPTIONS.xlsx'}")
    print(f"last_run_id={os.environ.get('CC_RUN_ID')} token_id={os.environ.get('CC_TOKEN_ID')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
