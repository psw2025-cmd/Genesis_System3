#!/usr/bin/env python3
"""
System3 Autopilot Proof Board

Aggregates backend, frontend, visual UI, GitHub/Render failure tracking, workflow, TODO, Render/public-truth, broker/chain/paper/ML proof into one board.
No chat screenshot dependency. No secret printing. No live orders.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "autopilot_proof_board"
DOC = ROOT / "docs" / "SYSTEM3_AUTOPILOT_LATEST_STATUS.md"


def read_json(rel: str) -> Dict[str, Any]:
    p = ROOT / rel
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return {"_error": str(exc)}


def read_text(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")


def report_status(name: str, data: Dict[str, Any], missing_blocker: str) -> Dict[str, Any]:
    if not data:
        return {"name": name, "status": "MISSING", "blockers": [missing_blocker]}
    status = str(data.get("status") or data.get("final_verdict") or data.get("verdict") or "UNKNOWN")
    blockers: List[str] = []
    for key in ("blockers", "todo", "visible_issues", "render_failures", "failed_workflows"):
        val = data.get(key)
        if isinstance(val, list):
            for x in val[:200]:
                if isinstance(x, dict):
                    blockers.append(json.dumps(x, ensure_ascii=False)[:300])
                else:
                    blockers.append(str(x)[:300])
    for count_key in ("failed_count", "visible_issue_count", "screenshot_missing_count", "ui_exception_count", "github_failed_count", "render_failed_count", "todo_count"):
        if data.get(count_key):
            blockers.append(f"{count_key}={data.get(count_key)}")
    return {"name": name, "status": status, "blockers": blockers}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    public_truth_md = read_text("reports/latest/system3_public_truth/index.md")
    public_truth = read_json("reports/latest/system3_public_truth/index.json")
    if public_truth_md and not public_truth:
        public_truth = {
            "status": "PASS" if "Final verdict: **PASS**" in public_truth_md else "FAIL" if "Final verdict: **FAIL**" in public_truth_md else "UNKNOWN",
            "markdown_present": True,
        }

    sources = [
        report_status("secure_install_credential_audit", read_json("reports/latest/secure_install_credential_audit/summary.json"), "Install/credential audit has not run."),
        report_status("dashboard_visible_issue_tracker", read_json("reports/latest/dashboard_visible_issue_tracker/summary.json"), "Visible UI issue tracker has not run."),
        report_status("github_render_failure_tracker", read_json("reports/latest/github_render_failure_tracker/summary.json"), "GitHub + Render failure tracker has not run."),
        report_status("parallel_root_cause_audit", read_json("reports/latest/parallel_root_cause_audit/summary.json"), "Parallel root-cause audit has not run."),
        report_status("workflow_failure_tracker", read_json("reports/latest/workflow_failure_tracker/summary.json"), "Workflow failure tracker has not run."),
        report_status("todo_status_update", read_json("reports/latest/todo_status_update/summary.json"), "1000+ TODO status updater has not run."),
        report_status("dashboard_visual_production_proof", read_json("reports/latest/dashboard_visual_production_proof/summary.json"), "Dashboard visual production proof has not run."),
        report_status("system3_public_truth", public_truth, "Final public truth has not run."),
    ]

    blockers: List[str] = []
    gate_rows = []
    pass_statuses = {"PASS", "DONE", "OK"}
    soft_statuses = {"PARTIAL", "WARN"}
    for s in sources:
        raw = str(s["status"]).upper()
        gate_status = "PASS" if raw in pass_statuses else "PARTIAL" if raw in soft_statuses else "BLOCKED"
        if gate_status != "PASS":
            blockers.extend([f"{s['name']}: {b}" for b in (s.get("blockers") or [f"status={s['status']}"])])
        gate_rows.append({"gate": s["name"], "raw_status": s["status"], "gate_status": gate_status, "blocker_count": len(s.get("blockers") or [])})

    core_gates = {
        "render_visual": any(x["gate"] == "dashboard_visible_issue_tracker" and x["gate_status"] == "PASS" for x in gate_rows),
        "github_render_health": any(x["gate"] == "github_render_failure_tracker" and x["gate_status"] == "PASS" for x in gate_rows),
        "backend_frontend_install": any(x["gate"] == "secure_install_credential_audit" and x["gate_status"] == "PASS" for x in gate_rows),
        "workflow_health": any(x["gate"] == "workflow_failure_tracker" and x["gate_status"] == "PASS" for x in gate_rows),
        "root_cause_zero": any(x["gate"] == "parallel_root_cause_audit" and x["gate_status"] == "PASS" for x in gate_rows),
        "todo_zero": any(x["gate"] == "todo_status_update" and x["gate_status"] == "PASS" for x in gate_rows),
        "public_truth_pass": any(x["gate"] == "system3_public_truth" and x["gate_status"] == "PASS" for x in gate_rows),
    }
    for k, v in core_gates.items():
        if not v:
            blockers.append(f"core_gate_blocked:{k}")

    final_status = "PASS" if not blockers and all(core_gates.values()) else "BLOCKED"
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": final_status,
        "owner": "PRITAM S. WARGHADE",
        "live_trading_enabled": False,
        "order_routes_called": False,
        "secrets_printed": False,
        "manual_screenshot_required": False,
        "production_grade_claim_allowed": final_status == "PASS",
        "core_gates": core_gates,
        "gate_rows": gate_rows,
        "blocker_count": len(blockers),
        "blockers": blockers[:500],
        "proof_files": {
            "this_summary": "reports/latest/autopilot_proof_board/summary.json",
            "this_markdown": "reports/latest/autopilot_proof_board/summary.md",
            "visible_ui_issues": "reports/latest/dashboard_visible_issue_tracker/summary.md",
            "github_render_failures": "docs/SYSTEM3_GITHUB_RENDER_FAILURE_TODO.md",
            "workflow_failures": "docs/SYSTEM3_WORKFLOW_FAILURE_TODO.md",
            "todo_status": "reports/latest/todo_status_update/summary.md",
            "public_truth": "reports/latest/system3_public_truth/index.md",
        },
    }

    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# System3 Autopilot Latest Status",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Owner/operator: **{payload['owner']}**",
        f"Status: **{payload['status']}**",
        f"Blockers: `{payload['blocker_count']}`",
        "",
        "## Non-negotiable rules",
        "",
        "- Manual screenshots from user are not required for proof.",
        "- Backend, frontend, live dashboard UI, GitHub/Render health, workflow health, TODO status, and final truth must be proven by automation.",
        "- Secrets are never printed or committed.",
        "- Live trading remains OFF; no live order routes are called.",
        "- Production-grade claim is allowed only when this board is PASS.",
        "",
        "## Core gates",
        "",
        "| Gate | Status |",
        "|---|---:|",
    ]
    for k, v in core_gates.items():
        lines.append(f"| {k} | {'PASS' if v else 'BLOCKED'} |")
    lines += ["", "## Source reports", "", "| Report | Raw status | Gate status | Blockers |", "|---|---|---|---:|"]
    for r in gate_rows:
        lines.append(f"| {r['gate']} | {r['raw_status']} | {r['gate_status']} | {r['blocker_count']} |")
    lines += ["", "## Blockers", ""]
    lines += [f"- [ ] {b}" for b in payload["blockers"]] or ["- [x] None"]

    md = "\n".join(lines) + "\n"
    (OUT / "summary.md").write_text(md, encoding="utf-8")
    DOC.write_text(md, encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if final_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
