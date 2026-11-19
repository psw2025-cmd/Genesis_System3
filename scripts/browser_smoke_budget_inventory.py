#!/usr/bin/env python3
"""Read-only browser smoke timeout-budget inventory; NOT a browser acceptance test."""
from __future__ import annotations
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "frontend_local_runtime_smoke.py"
OUTER_ATTEMPT_SECONDS = 180  # Workflow wrapper; recheck workflow when changing.
PER_TAB_MAX_SECONDS = 10  # Diagnostic upper bound, not an observed runtime.


def analyze(source: str) -> dict:
    tree = ast.parse(source)
    tabs = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "TABS":
                    tabs = ast.literal_eval(node.value)
    if not isinstance(tabs, list) or not all(isinstance(t, str) for t in tabs):
        raise ValueError("canonical TABS contract missing")
    if len(tabs) != len(set(tabs)):
        raise ValueError("duplicate tab identifiers")
    if len(tabs) != 23:
        raise ValueError(f"expected 23 tabs, got {len(tabs)}")
    return {
        "status": "DIAGNOSTIC_ONLY",
        "tabs_per_viewport": len(tabs),
        "viewports": 2,
        "max_sequential_tab_wait_seconds": len(tabs) * 2 * PER_TAB_MAX_SECONDS,
        "outer_attempt_seconds": OUTER_ATTEMPT_SECONDS,
        "max_wait_exceeds_outer_attempt": len(tabs) * 2 * PER_TAB_MAX_SECONDS > OUTER_ATTEMPT_SECONDS,
        "note": "Upper bound excludes browser startup and other waits; does not prove React root cause or browser PASS.",
    }


def main() -> int:
    print(json.dumps(analyze(SOURCE.read_text(encoding="utf-8")), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
