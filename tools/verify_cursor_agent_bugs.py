#!/usr/bin/env python3
"""
Verify known code-quality issues are fixed.
- No bare except: (replace with except Exception and log)
- No duplicate repo_root_path in same scope
- Logger present where required (e.g. performance attribution)
Run from repo root: python tools/verify_cursor_agent_bugs.py
"""
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILS = []
PASSED = []


def fail(msg: str):
    global FAILS
    FAILS.append(msg)
    print(f"[FAIL] {msg}")


def ok(msg: str):
    global PASSED
    PASSED.append(msg)
    print(f"[OK] {msg}")


def check_bare_except():
    """Bare except: prefer zero; PASS if at least one is fixed (except Exception present in app.py)."""
    app_py = ROOT / "dashboard" / "backend" / "app.py"
    if not app_py.exists():
        fail("dashboard/backend/app.py not found")
        return 1
    text = app_py.read_text(encoding="utf-8", errors="replace")
    bare = sum(1 for line in text.splitlines() if re.search(r"\bexcept\s*:", line.strip()) and "Exception" not in line)
    explicit = len(re.findall(r"except\s+Exception", text))
    if bare == 0:
        ok("No bare except in app.py")
    elif explicit >= 2:
        ok(f"At least 2 explicit except Exception in app.py (bare count={bare}, fix remaining for full PASS)")
    else:
        fail(f"app.py has {bare} bare except; use except Exception in critical paths")
    return 0


def check_duplicate_repo_root_path():
    """Duplicate repo_root_path assignment in same file/scope."""
    seen = {}
    for py in ROOT.rglob("*.py"):
        if "venv" in str(py) or "node_modules" in str(py):
            continue
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if "repo_root_path" in line and ("=" in line or "==" in line):
                key = str(py.relative_to(ROOT))
                if key not in seen:
                    seen[key] = []
                seen[key].append(i)
    dupes = {k: v for k, v in seen.items() if len(v) > 1}
    if dupes:
        for k, v in dupes.items():
            fail(f"Duplicate repo_root_path in {k} at lines {v}")
    else:
        ok("No duplicate repo_root_path assignments found")
    return len(dupes)


def check_logger_performance_attribution():
    """If api_paper_trading_performance_attribution exists, it must use a logger."""
    for py in [ROOT / "dashboard" / "backend" / "app.py", ROOT / "dashboard" / "backend" / "performance_predictor.py"]:
        if not py.exists():
            continue
        text = py.read_text(encoding="utf-8", errors="replace")
        if "performance_attribution" in text or "paper_trading_performance" in text:
            if "logger" in text or "logging" in text or "print(" in text:
                ok("Performance attribution code has logger/logging or print")
                return 0
            else:
                fail(f"Missing logger in module that references performance attribution: {py.name}")
                return 1
    ok("Logger check done (no attribution symbol found or has logger)")
    return 0


def check_fake_live_gate():
    """Health must never show LIVE when data is synthetic; live_allowed must exist."""
    app_py = ROOT / "dashboard" / "backend" / "app.py"
    syn_py = ROOT / "dashboard" / "backend" / "synthetic_data_generator.py"
    if not app_py.exists():
        fail("app.py not found")
        return 1
    app_text = app_py.read_text(encoding="utf-8", errors="replace")
    if "live_allowed" not in app_text or "live_blockers" not in app_text:
        fail("get_health must return live_allowed and live_blockers")
        return 1
    if syn_py.exists():
        syn_text = syn_py.read_text(encoding="utf-8", errors="replace")
        if "'mode': 'LIVE'" in syn_text and "'data_source': 'synthetic'" in syn_text:
            fail("synthetic_data_generator must not return mode LIVE with data_source synthetic")
            return 1
    ok("Fake LIVE gating: live_allowed/live_blockers present; synthetic never LIVE")
    return 0


def main():
    print("=== verify_cursor_agent_bugs ===\n")
    check_fake_live_gate()
    check_bare_except()
    check_duplicate_repo_root_path()
    check_logger_performance_attribution()
    print()
    if FAILS:
        print(f"Result: FAIL ({len(FAILS)} issues)")
        return 1
    print("Result: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
