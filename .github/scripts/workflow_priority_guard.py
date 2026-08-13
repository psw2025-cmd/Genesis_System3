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
    "frontend-runtime-smoke.yml",
}
MANUAL_ONLY = {"gcp-dhan-token-rotation.yml"}
ALLOWED = AUTOMATIC | MANUAL_ONLY


def _top_level_on_block(text: str) -> str:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if re.match(r"^on\s*:\s*$", line):
            start = index + 1
            continue
        if start is not None and line.strip() and not line.lstrip().startswith("#"):
            current_indent = len(line) - len(line.lstrip())
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

    forbidden_trigger = re.compile(
        r"^\s*(schedule|workflow_run|repository_dispatch|issue_comment|issues)\s*:",
        re.IGNORECASE | re.MULTILINE,
    )
    self_hosted = re.compile(
        r"runs-on:\s*(?:\[[^\]]*)?self-hosted",
        re.IGNORECASE,
    )
    retired_runtime = re.compile(r"render\.com|api\.render\.com", re.IGNORECASE)
    live_enable = re.compile(
        r"LIVE_TRADING_ENABLED\s*[:=]\s*[\"']?(?:1|true|yes)|"
        r"SYSTEM3_LIVE_TRADING_ALLOWED\s*[:=]\s*[\"']?(?:1|true|yes)|"
        r"AUTO_EXECUTE_TRADES\s*[:=]\s*[\"']?(?:1|true|yes)",
        re.IGNORECASE,
    )

    trigger_blocks: dict[str, str] = {}
    for name in files:
        text = (WORKFLOW_DIR / name).read_text(encoding="utf-8")
        on_block = _top_level_on_block(text)
        trigger_blocks[name] = on_block
        if not on_block:
            raise SystemExit(f"WORKFLOW_TRIGGER_BLOCK_MISSING file={name}")
        match = forbidden_trigger.search(on_block)
        if match:
            raise SystemExit(f"WORKFLOW_FORBIDDEN_TRIGGER file={name} match={match.group(1)!r}")
        if self_hosted.search(text):
            raise SystemExit(f"WORKFLOW_SELF_HOSTED_FORBIDDEN file={name}")
        if retired_runtime.search(text):
            raise SystemExit(f"WORKFLOW_RETIRED_RUNTIME_REFERENCE file={name}")
        if live_enable.search(text):
            raise SystemExit(f"WORKFLOW_LIVE_TRADING_FORBIDDEN file={name}")

    manual_on = trigger_blocks["gcp-dhan-token-rotation.yml"]
    if "workflow_dispatch:" not in manual_on:
        raise SystemExit("MANUAL_ROTATION_WORKFLOW_DISPATCH_MISSING")
    if re.search(r"^\s*(push|pull_request)\s*:", manual_on, re.MULTILINE):
        raise SystemExit(f"MANUAL_ROTATION_HAS_AUTOMATIC_TRIGGER block={manual_on!r}")

    ci_on = trigger_blocks["ci.yml"]
    if "pull_request:" not in ci_on or "push:" not in ci_on:
        raise SystemExit("GLOBAL_SAFETY_PRIORITY_TRIGGERS_MISSING")

    guard_on = trigger_blocks["workflow-priority-guard.yml"]
    if "pull_request:" not in guard_on or "push:" not in guard_on:
        raise SystemExit("WORKFLOW_PRIORITY_GUARD_TRIGGERS_MISSING")

    deploy_on = trigger_blocks["cloud-run-auto-deploy.yml"]
    if "push:" not in deploy_on or not re.search(r"branches:\s*\[\s*main\s*\]", deploy_on):
        raise SystemExit("CLOUD_RUN_MAIN_TRIGGER_MISSING")

    for name in ("gcp-stage2-ci.yml", "gcp-dhan-token-fix-ci.yml", "frontend-runtime-smoke.yml"):
        if "pull_request:" not in trigger_blocks[name]:
            raise SystemExit(f"FOCUSED_PRIORITY_PR_TRIGGER_MISSING file={name}")

    print(
        "WORKFLOW_PRIORITY_POLICY=PASS",
        {
            "active_workflow_count": len(files),
            "automatic": sorted(AUTOMATIC),
            "manual_only": sorted(MANUAL_ONLY),
            "unexpected": [],
            "self_hosted": False,
            "retired_runtime_workflows": False,
            "scheduled_github_workflows": False,
            "live_trading": False,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
