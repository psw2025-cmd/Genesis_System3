#!/usr/bin/env python3
"""System3 Windows self-hosted workflow migrator and proof report.

Purpose:
- scan every .github/workflows/*.yml and *.yaml
- convert safe `runs-on:` values to `[self-hosted, Windows]`
- keep Linux/container-specific workflows in manual review
- write JSON/Markdown proof reports

Safety:
- no live trading enablement
- no broker order routes
- no secrets printed
- no fake PASS
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
WF_DIR = ROOT / ".github" / "workflows"
OUT_DIR = ROOT / "reports" / "latest" / "windows_self_hosted_workflows"
TODO_MD = ROOT / "docs" / "SYSTEM3_WINDOWS_SELF_HOSTED_WORKFLOW_TODO.md"
RUNNER_EXPR = "[self-hosted, Windows]"

MANUAL_REVIEW_PATTERNS = [
    r"runs-on:\s*\$\{\{",
    r"container:",
    r"services:",
    r"sudo\s+",
    r"apt-get\s+",
    r"/bin/bash",
    r"bash\s+<<",
    r"docker\s+",
    r"ubuntu-latest.*#\s*linux-required",
]

SKIP_FILES = {
    "system3-windows-self-hosted-workflow-migration.yml",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def workflow_files() -> List[Path]:
    if not WF_DIR.exists():
        return []
    return sorted([p for p in WF_DIR.glob("*.yml")] + [p for p in WF_DIR.glob("*.yaml")])


def classify(text: str, path: Path) -> Tuple[str, List[str]]:
    reasons: List[str] = []
    if path.name in SKIP_FILES:
        return "self_hosted_control", ["control workflow already self-hosted"]
    for pat in MANUAL_REVIEW_PATTERNS:
        if re.search(pat, text, flags=re.I):
            reasons.append(f"manual_review_pattern:{pat}")
    if "runs-on:" not in text:
        reasons.append("no_runs_on_found")
    if "ubuntu-latest" in text or "windows-latest" in text or "macos-latest" in text:
        if reasons:
            return "manual_review", reasons
        return "migratable", ["hosted_runner_literal_found"]
    if RUNNER_EXPR in text:
        return "already_self_hosted", ["already uses self-hosted Windows runner"]
    return "manual_review", reasons or ["unknown runner expression"]


def migrate_text(text: str) -> str:
    # Replace only simple literal hosted runners. Complex expressions are manual-review only.
    text = re.sub(r"runs-on:\s*ubuntu-latest", f"runs-on: {RUNNER_EXPR}", text)
    text = re.sub(r"runs-on:\s*windows-latest", f"runs-on: {RUNNER_EXPR}", text)
    text = re.sub(r"runs-on:\s*macos-latest", f"runs-on: {RUNNER_EXPR}", text)
    return text


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TODO_MD.parent.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []
    changed: List[str] = []

    for path in workflow_files():
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        text = path.read_text(encoding="utf-8")
        status, reasons = classify(text, path)
        new_text = text
        if status == "migratable" and os.environ.get("SYSTEM3_APPLY_WORKFLOW_MIGRATION", "1") not in ("0", "false", "False"):
            new_text = migrate_text(text)
            if new_text != text:
                path.write_text(new_text, encoding="utf-8")
                changed.append(rel)
                status = "migrated"
            else:
                status = "unchanged"
        rows.append({
            "workflow": rel,
            "status": status,
            "reasons": reasons,
            "changed": rel in changed,
            "uses_self_hosted_windows_after": RUNNER_EXPR in new_text,
        })

    counts: Dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    blocker_count = sum(1 for row in rows if row["status"] == "manual_review")
    payload = {
        "generated_utc": now(),
        "status": "PASS" if blocker_count == 0 else "PARTIAL",
        "runner_target": RUNNER_EXPR,
        "workflow_count": len(rows),
        "changed_count": len(changed),
        "manual_review_count": blocker_count,
        "counts": counts,
        "changed_workflows": changed,
        "rows": rows,
        "safety": {
            "live_trading_enabled": False,
            "system3_live_trading_allowed": False,
            "broker_order_routes_touched": False,
            "secrets_printed": False,
        },
    }

    (OUT_DIR / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# System3 Windows Self-Hosted Workflow Migration Proof",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Status: **{payload['status']}**",
        f"Target runner: `{RUNNER_EXPR}`",
        "",
        "## Summary",
        "",
        f"- Workflows scanned: **{payload['workflow_count']}**",
        f"- Workflows changed: **{payload['changed_count']}**",
        f"- Manual review blockers: **{payload['manual_review_count']}**",
        "- Live trading enabled: **false**",
        "- Broker order routes touched: **false**",
        "- Secrets printed: **false**",
        "",
        "## Workflow table",
        "",
        "| Workflow | Status | Changed | Reasons |",
        "|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['workflow']}` | {row['status']} | {str(row['changed']).lower()} | {'; '.join(row['reasons'])} |"
        )
    lines += [
        "",
        "## Rule",
        "",
        "A workflow is not counted as transferred until its file contains `runs-on: [self-hosted, Windows]` or has a documented manual-review reason.",
        "",
        "This proof does not claim System3 trading readiness. It proves only workflow runner migration status.",
    ]
    (OUT_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    todo = [
        "# System3 Windows Self-Hosted Workflow TODO",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        "",
        "## Manual review workflows",
        "",
    ]
    manual = [r for r in rows if r["status"] == "manual_review"]
    if not manual:
        todo.append("No manual-review workflow blockers found.")
    else:
        for row in manual:
            todo.append(f"- [ ] `{row['workflow']}` — {'; '.join(row['reasons'])}")
    todo += [
        "",
        "## Safety rules",
        "",
        "- [ ] Keep `LIVE_TRADING_ENABLED=0`.",
        "- [ ] Keep `SYSTEM3_LIVE_TRADING_ALLOWED=0`.",
        "- [ ] Do not print secrets in runner logs.",
        "- [ ] Do not call broker order routes from proof workflows.",
    ]
    TODO_MD.write_text("\n".join(todo) + "\n", encoding="utf-8")

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
