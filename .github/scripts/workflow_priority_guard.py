#!/usr/bin/env python3
"""Fail closed unless only the approved System3 priority workflows are active."""
from __future__ import annotations

import re
from pathlib import Path

WORKFLOW_DIR = Path(".github/workflows")
POLICY_PATH = Path("docs/SYSTEM3_WORKFLOW_PRIORITY_POLICY.md")

AUTOMATIC = {
    "ci.yml",
    "workflow-priority-guard.yml",
    "cloud-run-auto-deploy.yml",
    "gcp-stage2-ci.yml",
    "gcp-dhan-token-fix-ci.yml",
}
MANUAL_ONLY = {"gcp-dhan-token-rotation.yml"}
ALLOWED = AUTOMATIC | MANUAL_ONLY


def _top_level_on_block(text: str) -> str:
    lines = text.splitlines()
    start = None
    indent = None
    for index, line in enumerate(lines):
        if re.match(r"^on\s*:\s*$", line):
            start = index + 1
            continue
        if start is not None:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            current_indent = len(line) - len(line.lstrip())
            if indent is None:
                indent = current_indent
            if current_indent == 0:
                return "\n".join(lines[start:index])
    return "\n".join(lines[start:]) if start is not None else ""


def main() -> int:
    files = sorted(
        p.name
        for pattern in ("*.yml", "*.yaml")
        for p in WORKFLOW_DIR.glob(pattern)
        if p.is_file()
    )
    actual = set(files)
    unexpected = sorted(actual - ALLOWED)
    missing = sorted(ALLOWED - actual)
    if unexpected or missing:
        raise SystemExit(
            f"WORKFLOW_ALLOWLIST_FAIL unexpected={unexpected} missing={missing} actual={files}"
        )

    if not POLICY_PATH.is_file():
        raise SystemExit(f"WORKFLOW_POLICY_MISSING {POLICY_PATH}")

    forbidden_global = re.compile(
        r"runs-on:\s*(?:\[[^\]]*)?self-hosted|\bschedule\s*:|\bworkflow_run\s*:|"
        r"\brepository_dispatch\s*:|\bissue_comment\s*:|\bissues\s*:|render\.com|api\.render\.com",
        re.IGNORECASE,
    )
    for name in files:
        text = (WORKFLOW_DIR / name).read_text(encoding="utf-8")
        match = forbidden_global.search(text)
        if match:
            raise SystemExit(f"WORKFLOW_FORBIDDEN_TRIGGER_OR_RUNTIME file={name} match={match.group(0)!r}")

        if re.search(
            r"LIVE_TRADING_ENABLED\s*[:=]\s*[\"']?(?:1|true|yes)|"
            r"SYSTEM3_LIVE_TRADING_ALLOWED\s*[:=]\s*[\"']?(?:1|true|yes)|"
            r"AUTO_EXECUTE_TRADES\s*[:=]\s*[\"']?(?:1|true|yes)",
            text,
            re.IGNORECASE,
        ):
            raise SystemExit(f"WORKFLOW_LIVE_TRADING_FORBIDDEN file={name}")

    manual_text = (WORKFLOW_DIR / "gcp-dhan-token-rotation.yml").read_text(encoding="utf-8")
    manual_on = _top_level_on_block(manual_text)
    if "workflow_dispatch:" not in manual_on:
        raise SystemExit("MANUAL_ROTATION_WORKFLOW_DISPATCH_MISSING")
    if re.search(r"^\s*(push|pull_request|schedule|workflow_run|repository_dispatch)\s*:", manual_on, re.M):
        raise SystemExit(f"MANUAL_ROTATION_HAS_AUTOMATIC_TRIGGER block={manual_on!r}")

    ci_text = (WORKFLOW_DIR / "ci.yml").read_text(encoding="utf-8")
    if "pull_request:" not in _top_level_on_block(ci_text) or "push:" not in _top_level_on_block(ci_text):
        raise SystemExit("GLOBAL_SAFETY_PRIORITY_TRIGGERS_MISSING")

    deploy_text = (WORKFLOW_DIR / "cloud-run-auto-deploy.yml").read_text(encoding="utf-8")
    deploy_on = _top_level_on_block(deploy_text)
    if "push:" not in deploy_on or "branches: [main]" not in deploy_on:
        raise SystemExit("CLOUD_RUN_MAIN_TRIGGER_MISSING")

    for name in ("gcp-stage2-ci.yml", "gcp-dhan-token-fix-ci.yml"):
        block = _top_level_on_block((WORKFLOW_DIR / name).read_text(encoding="utf-8"))
        if "pull_request:" not in block:
            raise SystemExit(f"FOCUSED_PRIORITY_PR_TRIGGER_MISSING file={name}")

    print(
        "WORKFLOW_PRIORITY_POLICY=PASS",
        {
            "active_workflow_count": len(files),
            "automatic": sorted(AUTOMATIC),
            "manual_only": sorted(MANUAL_ONLY),
            "unexpected": [],
            "self_hosted": False,
            "render_workflows": False,
            "scheduled_github_workflows": False,
            "live_trading": False,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
