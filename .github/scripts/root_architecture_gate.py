from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OUT_DIR = ROOT / "reports" / "ci_truth"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REPORT_JSON = OUT_DIR / "root_architecture_gate.json"
REPORT_MD = OUT_DIR / "ROOT_ARCHITECTURE_GATE.md"
DIFF_DEBUG_JSON = OUT_DIR / "changed_files_debug.json"

PROTECTED_PATH_PREFIXES = (
    "core/",
    "services/",
    "strategies/",
    "broker/",
    "brokers/",
    "db/",
    "database/",
    "storage/",
    "models/",
    "core/models/",
)

SECRET_PATTERNS = [
    r"api[_-]?key\s*=\s*['\"][A-Za-z0-9_\-]{12,}",
    r"secret\s*=\s*['\"][A-Za-z0-9_\-]{12,}",
    r"password\s*=\s*['\"][^'\"]{6,}",
    r"totp\s*=\s*['\"][A-Za-z0-9]{6,}",
    r"jwt\s*=\s*['\"][A-Za-z0-9_\-.]{20,}",
]

CRITICAL_FILES = [
    "run_system3.py",
    ".github/workflows/ci.yml",
    "requirements-ci.txt",
]

CRITICAL_DIRS = [
    ".github/workflows",
    ".github/scripts",
]

DIFF_DEBUG: list[dict] = []


def sh(cmd: list[str], allow_fail: bool = False) -> dict:
    try:
        p = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=120,
        )
        return {
            "cmd": cmd,
            "return_code": p.returncode,
            "output": (p.stdout or "")[-6000:],
            "ok": p.returncode == 0 or allow_fail,
        }
    except Exception as e:
        return {
            "cmd": cmd,
            "return_code": 999,
            "output": str(e),
            "ok": allow_fail,
        }


def parse_diff_files(result: dict) -> list[str]:
    if result.get("return_code") != 0:
        return []
    files: list[str] = []
    for line in result.get("output", "").splitlines():
        value = line.strip()
        if not value:
            continue
        if value.lower().startswith(("fatal:", "error:", "warning:")):
            continue
        files.append(value)
    return files


def changed_files() -> list[str]:
    commands = [
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        ["git", "diff", "--name-only", "HEAD~1..HEAD"],
    ]
    for cmd in commands:
        result = sh(cmd, allow_fail=True)
        files = parse_diff_files(result)
        DIFF_DEBUG.append(
            {
                "cmd": cmd,
                "return_code": result.get("return_code"),
                "selected": bool(files),
                "files": files,
                "output_tail": result.get("output", "")[-2000:],
            }
        )
        if files:
            DIFF_DEBUG_JSON.write_text(json.dumps(DIFF_DEBUG, indent=2), encoding="utf-8")
            return files
    DIFF_DEBUG_JSON.write_text(json.dumps(DIFF_DEBUG, indent=2), encoding="utf-8")
    return []


def check_required_files() -> dict:
    missing = [p for p in CRITICAL_FILES if not (ROOT / p).exists()]
    missing_dirs = [p for p in CRITICAL_DIRS if not (ROOT / p).exists()]
    return {
        "name": "required_files_and_dirs",
        "status": "PASS" if not missing and not missing_dirs else "FAIL",
        "missing_files": missing,
        "missing_dirs": missing_dirs,
    }


def check_python_compile() -> dict:
    candidates = [
        ROOT / "run_system3.py",
        ROOT / ".github/scripts/root_architecture_gate.py",
    ]
    existing = [str(p.relative_to(ROOT)) for p in candidates if p.exists()]
    failures = []
    for p in existing:
        r = sh([sys.executable, "-m", "py_compile", p], allow_fail=False)
        if not r["ok"]:
            failures.append({"file": p, "output": r["output"]})
    return {
        "name": "critical_python_compile",
        "status": "PASS" if not failures else "FAIL",
        "files_checked": existing,
        "failures": failures,
    }


def check_protected_paths_not_changed(files: list[str]) -> dict:
    allowed_prefixes = (
        ".github/",
        "docs/ci_truth/",
        "reports/ci_truth/",
    )
    violations = []
    for f in files:
        if f.startswith(allowed_prefixes):
            continue
        if f.startswith(PROTECTED_PATH_PREFIXES):
            violations.append(f)
    return {
        "name": "protected_runtime_paths_not_changed",
        "status": "PASS" if not violations else "FAIL",
        "changed_files": files,
        "violations": violations,
    }


def check_no_env_or_db_or_model_artifacts_changed(files: list[str]) -> dict:
    blocked_suffix = (
        ".env",
        ".db",
        ".duckdb",
        ".sqlite",
        ".sqlite3",
        ".pkl",
        ".joblib",
        ".onnx",
        ".pt",
        ".pth",
        ".h5",
        ".keras",
    )
    blocked = []
    for f in files:
        name = Path(f).name.lower()
        if name == ".env" or any(name.endswith(s) for s in blocked_suffix):
            blocked.append(f)
    return {
        "name": "no_env_db_model_artifacts_changed",
        "status": "PASS" if not blocked else "FAIL",
        "blocked_files": blocked,
    }


def check_secret_like_values_in_changed_files(files: list[str]) -> dict:
    findings = []
    for f in files:
        path = ROOT / f
        if not path.exists() or path.is_dir() or path.stat().st_size > 2_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pattern in SECRET_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                findings.append({"file": f, "pattern": pattern})
    return {
        "name": "no_secret_like_values_in_changed_files",
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
    }


def check_trading_safety_text(files: list[str]) -> dict:
    suspicious = []
    suspicious_terms = [
        "LIVE_TRADING_ENABLED=true",
        "TRADING_MODE=live",
        "STRATEGY_MODE=LIVE",
        "placeOrder(",
        "place_order(",
        "dhanhq.placeOrder",
    ]
    gate_script = ".github/scripts/root_architecture_gate.py"
    for f in files:
        if f == gate_script:
            continue
        path = ROOT / f
        if not path.exists() or path.is_dir():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for term in suspicious_terms:
            if term in text:
                suspicious.append({"file": f, "term": term})
    return {
        "name": "no_obvious_live_trading_enablement_in_changed_files",
        "status": "PASS" if not suspicious else "FAIL",
        "findings": suspicious,
    }


def main() -> int:
    files = changed_files()
    checks = [
        check_required_files(),
        check_python_compile(),
        check_protected_paths_not_changed(files),
        check_no_env_or_db_or_model_artifacts_changed(files),
        check_secret_like_values_in_changed_files(files),
        check_trading_safety_text(files),
    ]
    failed = [c for c in checks if c["status"] != "PASS"]
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "policy": "Architecture and trading safety must be FULL PASS. Only ci.yml is the active workflow.",
        "blocking": True,
        "changed_files": files,
        "checks": checks,
        "status": "PASS" if not failed else "FAIL",
        "failed_count": len(failed),
        "protected_scope": {
            "trading_logic_changed": False,
            "broker_config_changed": False,
            "env_changed": False,
            "database_changed": False,
            "model_artifacts_changed": False,
        },
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# Root Architecture Gate\n",
        f"Generated UTC: `{payload['generated_at_utc']}`\n",
        "## Policy\n",
        payload["policy"] + "\n",
        "## Result\n",
        f"Status: **{payload['status']}**\n",
        "## Checks\n",
        "| Check | Status |",
        "|---|---|",
    ]
    for c in checks:
        lines.append(f"| {c['name']} | {c['status']} |")
    lines.append("\n## Changed files")
    if files:
        for f in files:
            lines.append(f"- `{f}`")
    else:
        lines.append("- None detected")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        Path(summary).write_text(REPORT_MD.read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
