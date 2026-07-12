#!/usr/bin/env python3
"""
System3 Experimental Solution Planner

Reads all latest proof reports and produces grouped fix lanes.
Goal: stop random patching and choose the fastest root-cause path.
No secrets. No live orders.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "experimental_solution_planner"
DOC = ROOT / "docs" / "SYSTEM3_EXPERIMENTAL_SOLUTION_PLAN.md"

REPORTS = [
    "reports/latest/render_100_agent_swarm/summary.json",
    "reports/latest/autopilot_proof_board/summary.json",
    "reports/latest/dashboard_visible_issue_tracker/summary.json",
    "reports/latest/secure_install_credential_audit/summary.json",
    "reports/latest/parallel_root_cause_audit/summary.json",
    "reports/latest/workflow_failure_tracker/summary.json",
    "reports/latest/todo_status_update/summary.json",
    "reports/latest/system3_public_truth/index.json",
]

LANE_RULES = [
    ("RENDER_DEPLOY", ["render", "deploy", "stale", "frontend bundle", "public truth"]),
    ("UI_RED_VISUAL", ["visible", "ui", "red", "blocked", "pending", "screenshot"]),
    ("BROKER_DHAN", ["broker", "dhan", "token", "auth", "fund", "holding", "client"]),
    ("OPTION_CHAIN", ["option", "chain", "strike", "expiry", "0/4"]),
    ("SCANNER_SIGNAL", ["scanner", "signal", "ce/pe", "candidate", "no trade"]),
    ("PAPER_LIFECYCLE", ["paper", "lifecycle", "entry", "exit", "pnl", "provenance"]),
    ("ML_TRAINING", ["ml", "model", "training", "accuracy", "auc", "spearman", "expectancy"]),
    ("WORKFLOW_CI", ["workflow", "github", "ci", "action", "failed", "timed_out", "cancelled"]),
    ("INSTALL_CREDENTIAL", ["install", "dependency", "credential", "secret", "env"]),
    ("ROUTE_CODE", ["route", "router", "app.py", "duplicate", "inactive"]),
    ("FAKE_STALE_DATA", ["fake", "mock", "fixture", "synthetic", "yahoo", "bhavcopy"]),
]

LANE_FIXES = {
    "RENDER_DEPLOY": [
        "Verify /api/deploy/info exposes latest commit.",
        "Force Render redeploy if commit mismatch or missing.",
        "Run live dashboard screenshot proof after deploy.",
    ],
    "UI_RED_VISUAL": [
        "Use dashboard_visible_issue_tracker output as source of truth.",
        "Fix root cause for each visible red/blocked/pending line; do not hide text.",
        "Re-run tracker until visible_issue_count=0.",
    ],
    "BROKER_DHAN": [
        "Check broker diagnose/funds/holdings/positions read-only endpoints.",
        "Treat token/auth/funds failure as connected=false.",
        "Do not enable live orders.",
    ],
    "OPTION_CHAIN": [
        "Prove Dhan chain rows for enabled universe.",
        "Show strike/expiry/CE/PE visibility in dashboard.",
        "Block scanner until chain rows are real.",
    ],
    "SCANNER_SIGNAL": [
        "Verify top_contract_gainers returns real rows.",
        "Require CE/PE side, strike, expiry, score, reason.",
        "If market closed, report exact blocked reason, not fake signal.",
    ],
    "PAPER_LIFECYCLE": [
        "Require paper entry, exit, PnL, source/provenance.",
        "Reject fake/fixture/mock rows.",
        "Show order endpoints not called.",
    ],
    "ML_TRAINING": [
        "Build real CE/PE dataset proof.",
        "Train/test split and accuracy/AUC/Spearman proof.",
        "Dashboard must show score and blocked reason if unavailable.",
    ],
    "WORKFLOW_CI": [
        "Read workflow_failure_tracker TODO.",
        "Fix failing workflow logs one by one.",
        "Keep failed workflows in TODO until later successful run proves fixed.",
    ],
    "INSTALL_CREDENTIAL": [
        "Fix dependency/import/compile errors from secure audit.",
        "Verify credentials via redacted secure env checks only.",
        "Never print or commit credential values.",
    ],
    "ROUTE_CODE": [
        "Patch active dashboard/backend/app.py route if routers are disabled.",
        "Remove duplicate route ambiguity or prove active endpoint response.",
        "Add tests/proofs for active route behavior.",
    ],
    "FAKE_STALE_DATA": [
        "Remove fake/mock/synthetic/Yahoo/bhavcopy from displayed live truth path.",
        "Allow only explicit blocked status when real data missing.",
        "Add proof that no fake rows are used in paper/signals/ML dashboard.",
    ],
}


def load_json(path: str) -> Dict[str, Any]:
    p = ROOT / path
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return {"_error": str(exc)}


def extract_issues(data: Any) -> List[str]:
    out: List[str] = []
    if isinstance(data, dict):
        for key in ["blockers", "todo", "issues", "visible_issues", "failed_runs"]:
            val = data.get(key)
            if isinstance(val, list):
                for x in val[:500]:
                    out.append(json.dumps(x, ensure_ascii=False)[:500] if isinstance(x, dict) else str(x)[:500])
        for k, v in data.items():
            if k.endswith("count") and isinstance(v, int) and v > 0:
                out.append(f"{k}={v}")
            if k == "status" and str(v).upper() not in {"PASS", "OK", "DONE"}:
                out.append(f"status={v}")
    return out


def choose_lane(issue: str) -> str:
    low = issue.lower()
    scores = Counter()
    for lane, keys in LANE_RULES:
        for key in keys:
            if key in low:
                scores[lane] += 1
    return scores.most_common(1)[0][0] if scores else "UNKNOWN"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    all_issues: List[Dict[str, str]] = []
    report_status = {}
    for rel in REPORTS:
        data = load_json(rel)
        status = data.get("status") or data.get("final_verdict") or ("MISSING" if not data else "UNKNOWN")
        report_status[rel] = status
        for issue in extract_issues(data):
            all_issues.append({"report": rel, "issue": issue, "lane": choose_lane(issue)})
        if not data:
            all_issues.append({"report": rel, "issue": f"missing_report:{rel}", "lane": "WORKFLOW_CI"})

    lanes = defaultdict(list)
    for item in all_issues:
        lanes[item["lane"]].append(item)

    lane_order = sorted(lanes, key=lambda k: len(lanes[k]), reverse=True)
    plan = []
    for lane in lane_order:
        plan.append({
            "lane": lane,
            "issue_count": len(lanes[lane]),
            "top_issues": lanes[lane][:25],
            "recommended_fixes": LANE_FIXES.get(lane, ["Inspect source report, classify manually, add rule to planner."]),
        })

    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not all_issues else "BLOCKED",
        "issue_count": len(all_issues),
        "lane_count": len(plan),
        "report_status": report_status,
        "lanes": plan,
        "live_trading_enabled": False,
        "order_routes_called": False,
        "secrets_printed": False,
        "production_grade_claim_allowed": not all_issues,
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# System3 Experimental Solution Plan",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Status: **{payload['status']}**",
        f"Issues: `{payload['issue_count']}`",
        f"Fix lanes: `{payload['lane_count']}`",
        "",
        "## Rule",
        "",
        "Use this plan to fix root causes by lane. Do not claim resolved until proof reports are PASS and live dashboard visual issues are zero.",
        "",
        "## Report status",
        "",
        "| Report | Status |",
        "|---|---|",
    ]
    for rel, status in report_status.items():
        lines.append(f"| `{rel}` | `{status}` |")
    lines += ["", "## Fix lanes", ""]
    for lane in plan:
        lines.append(f"### {lane['lane']} — {lane['issue_count']} issues")
        lines.append("")
        lines.append("Recommended fixes:")
        for fix in lane["recommended_fixes"]:
            lines.append(f"- {fix}")
        lines.append("")
        lines.append("Top issues:")
        for issue in lane["top_issues"][:15]:
            lines.append(f"- `{issue['report']}`: {issue['issue']}")
        lines.append("")
    md = "\n".join(lines) + "\n"
    (OUT / "summary.md").write_text(md, encoding="utf-8")
    DOC.write_text(md, encoding="utf-8")
    print(json.dumps(payload, indent=2)[:12000])
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
