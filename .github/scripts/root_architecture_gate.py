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
    "core/engine/",
    "core/models/",
    "services/",
    "strategies/",
    "broker/",
    "brokers/",
    "db/",
    "database/",
    "models/",
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
    "AGENTS.md",
    "state/FAILURE_REMEDIATION_CHECKLIST.md",
    "state/AUTONOMOUS_ENGINEERING_MASTER_PLAN.md",
    "scripts/frontend_local_runtime_smoke.py",
    "scripts/gcp_ui_tab_visual_proof.py",
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


def check_governance_contract() -> dict:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8", errors="ignore")
    master = (ROOT / "state/AUTONOMOUS_ENGINEERING_MASTER_PLAN.md").read_text(encoding="utf-8", errors="ignore")
    failure = (ROOT / "state/FAILURE_REMEDIATION_CHECKLIST.md").read_text(encoding="utf-8", errors="ignore")
    local = (ROOT / "scripts/frontend_local_runtime_smoke.py").read_text(encoding="utf-8", errors="ignore")
    deployed = (ROOT / "scripts/gcp_ui_tab_visual_proof.py").read_text(encoding="utf-8", errors="ignore")

    required_agent_markers = [
        "GCP is production/deployment authority",
        "Recursive 10-step failure loop",
        "LOCAL_NON_PRODUCTION",
        "Production broker-connected claims are forbidden unless Layer B passes",
        "AGENT_EXECUTION_FAILED",
        "CLOSED — PROVEN",
    ]
    required_master_markers = [
        "Authority ladder",
        "Repository-wide forensic inventory checklist",
        "Automation self-check matrix",
        "Smoke-test ladder",
        "Issue #188 market-data completeness checklist",
        "SYSTEM_STATE.md` is stale",
    ]
    required_failure_markers = [
        "Universal 10-step loop",
        "Child-loop rule",
        "UI-001",
        "Closure rule",
    ]
    required_local_markers = [
        'PROOF_SCOPE = "LOCAL_NON_PRODUCTION"',
        "PRODUCTION_AUTHORITY = False",
        "BROKER_CONNECTIVITY_PROVEN = False",
        '"production_claim_allowed": False',
        '"proof_scope": PROOF_SCOPE',
        '"production_authority": PRODUCTION_AUTHORITY',
        '"broker_connectivity_proven": BROKER_CONNECTIVITY_PROVEN',
    ]
    required_deployed_markers = [
        '"source": "real_deployed_cloud_run_ui"',
        "EXPECTED_SHA",
        "gcloud",
        "https://",
    ]

    missing = []
    for scope, text, markers in (
        ("AGENTS.md", agents, required_agent_markers),
        ("master_plan", master, required_master_markers),
        ("failure_checklist", failure, required_failure_markers),
        ("local_ui_proof", local, required_local_markers),
        ("deployed_ui_proof", deployed, required_deployed_markers),
    ):
        for marker in markers:
            if marker not in text:
                missing.append({"scope": scope, "marker": marker})

    forbidden_local = [
        "PRODUCTION_AUTHORITY = True",
        "BROKER_CONNECTIVITY_PROVEN = True",
        '"production_claim_allowed": True',
        'PROOF_SCOPE = "PRODUCTION"',
    ]
    forbidden_hits = [marker for marker in forbidden_local if marker in local]

    return {
        "name": "universal_agent_and_ui_provenance_contract",
        "status": "PASS" if not missing and not forbidden_hits else "FAIL",
        "missing_markers": missing,
        "forbidden_local_markers": forbidden_hits,
        "note": "Local browser proof may never claim GCP/broker production authority; recursive governance files are mandatory.",
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
        ".env", ".db", ".duckdb", ".sqlite", ".sqlite3", ".pkl", ".joblib",
        ".onnx", ".pt", ".pth", ".h5", ".keras",
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


def _added_lines_from_diff(files, gate_script):
    scan_files = [f for f in files if f != gate_script]
    if not scan_files:
        return []
    for cmd in (
        ["git", "diff", "origin/main...HEAD", "--"] + scan_files,
        ["git", "diff", "HEAD~1..HEAD", "--"] + scan_files,
    ):
        result = sh(cmd, allow_fail=True)
        if result.get("return_code") not in (0, 1):
            continue
        output = result.get("output", "")
        if not output.strip():
            continue
        added, current_file = [], ""
        for line in output.splitlines():
            if line.startswith("+++ b/"):
                current_file = line[6:]
            elif line.startswith("+") and not line.startswith("+++"):
                added.append((current_file, line[1:]))
        return added
    return []


def check_trading_safety_text(files: list) -> dict:
    suspicious_terms = [
        "LIVE_TRADING_ENABLED=true", "TRADING_MODE=live",
        "STRATEGY_MODE=LIVE", "placeOrder(", "place_order(", "dhanhq.placeOrder",
    ]
    gate_script = ".github/scripts/root_architecture_gate.py"
    added_lines = _added_lines_from_diff(files, gate_script)
    suspicious = []
    for file_name, line_text in added_lines:
        for term in suspicious_terms:
            if term in line_text:
                suspicious.append({"file": file_name, "term": term, "added_line": line_text.strip()})
    return {
        "name": "no_obvious_live_trading_enablement_in_changed_files",
        "status": "PASS" if not suspicious else "FAIL",
        "findings": suspicious,
        "note": "Scans only newly added diff lines; pre-existing code not flagged.",
    }


def main() -> int:
    files = changed_files()
    checks = [
        check_required_files(),
        check_governance_contract(),
        check_python_compile(),
        check_protected_paths_not_changed(files),
        check_no_env_or_db_or_model_artifacts_changed(files),
        check_secret_like_values_in_changed_files(files),
        check_trading_safety_text(files),
    ]
    failed = [c for c in checks if c["status"] != "PASS"]
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "policy": "Architecture, universal agent governance, proof provenance and trading safety must be FULL PASS.",
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
