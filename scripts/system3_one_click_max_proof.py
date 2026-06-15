#!/usr/bin/env python3
"""
System3 One-Click Max Proof Runner.

Goal: do the maximum safe proof collection from one command.

It tries multiple modes:
1. local-only reports
2. SYSTEM3_API_BASE if set
3. user-supplied --api-base values
4. known/default Render URL unless --skip-default-api is used
5. localhost candidates unless --skip-localhost is used

It runs the global control-plane runner for each reachable/allowed mode,
preserves every scenario output, compares results, and creates a zip bundle.

Safety:
- does not enable live trading
- does not place/modify/cancel orders
- does not edit runtime logic
- does not edit .env/secrets/credentials/token files
- writes only under reports/latest and reports/max_proof
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_RENDER_API = "https://genesis-system3-backend.onrender.com"
LOCALHOST_APIS = ["http://127.0.0.1:8000", "http://127.0.0.1:5000", "http://localhost:8000", "http://localhost:5000"]

REPORTS_TO_PRESERVE = [
    "system3_control_plane_status.json",
    "system3_control_plane_status.md",
    "system3_blocker_report.json",
    "system3_blocker_report.md",
    "option_strike_visibility.json",
    "option_strike_visibility.md",
    "model_accuracy_report.json",
    "model_accuracy_report.md",
    "markdown_inventory.json",
    "markdown_inventory.md",
    "documentation_contradictions.md",
]

COMPILE_CHECK_SCRIPTS = [
    "scripts/system3_markdown_inventory.py",
    "scripts/system3_option_visibility_audit.py",
    "scripts/system3_model_accuracy_tracker.py",
    "scripts/system3_blocker_finder.py",
    "scripts/system3_control_plane_runner.py",
    "scripts/system3_one_click_max_proof.py",
]


@dataclass
class ScenarioResult:
    name: str
    api_base: Optional[str]
    returncode: int
    status: str
    output_dir: str
    stdout_tail: str
    stderr_tail: str
    summary: Dict[str, Any]


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def tail(text: str, limit: int = 5000) -> str:
    return text[-limit:] if text else ""


def safe_json(path: Path) -> Optional[Any]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def fetch_endpoint(api_base: str, endpoint: str, timeout: int = 8) -> Dict[str, Any]:
    url = api_base.rstrip("/") + endpoint
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        return {"ok": True, "url": url, "data": data, "error": None}
    except Exception as exc:
        return {"ok": False, "url": url, "data": None, "error": f"{type(exc).__name__}: {exc}"}


def compile_check(root: Path) -> Dict[str, Any]:
    results = []
    all_pass = True
    for rel in COMPILE_CHECK_SCRIPTS:
        p = root / rel
        if not p.exists():
            results.append({"path": rel, "status": "MISSING", "returncode": 127, "stderr": "missing"})
            all_pass = False
            continue
        proc = subprocess.run([sys.executable, "-m", "py_compile", str(p)], cwd=str(root), text=True, capture_output=True)
        status = "PASS" if proc.returncode == 0 else "FAIL"
        if proc.returncode != 0:
            all_pass = False
        results.append({"path": rel, "status": status, "returncode": proc.returncode, "stderr": tail(proc.stderr)})
    return {"all_pass": all_pass, "results": results}


def unique_scenarios(args: argparse.Namespace) -> List[tuple[str, Optional[str]]]:
    scenarios: List[tuple[str, Optional[str]]] = [("local_only", None)]
    seen = {None}
    candidates: List[str] = []
    if os.environ.get("SYSTEM3_API_BASE"):
        candidates.append(os.environ["SYSTEM3_API_BASE"])
    for item in args.api_base or []:
        candidates.append(item)
    if not args.skip_default_api:
        candidates.append(DEFAULT_RENDER_API)
    if not args.skip_localhost:
        candidates.extend(LOCALHOST_APIS)
    for api in candidates:
        clean = api.rstrip("/")
        if clean not in seen:
            seen.add(clean)
            safe_name = clean.replace("https://", "").replace("http://", "").replace("/", "_").replace(":", "_")
            scenarios.append((safe_name, clean))
    return scenarios


def preserve_latest_reports(root: Path, dest: Path) -> None:
    latest = root / "reports" / "latest"
    dest.mkdir(parents=True, exist_ok=True)
    for name in REPORTS_TO_PRESERVE:
        src = latest / name
        if src.exists():
            shutil.copy2(src, dest / name)


def run_control_plane(root: Path, name: str, api_base: Optional[str], base_out: Path, timeout: int) -> ScenarioResult:
    runner = root / "scripts" / "system3_control_plane_runner.py"
    out_dir = base_out / name
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(runner), "--timeout", str(timeout)]
    if api_base:
        cmd.extend(["--api-base", api_base])
    env = os.environ.copy()
    if api_base:
        env["SYSTEM3_API_BASE"] = api_base
    proc = subprocess.run(cmd, cwd=str(root), text=True, capture_output=True, env=env, timeout=max(timeout * 5, 120))
    preserve_latest_reports(root, out_dir)
    status_json = safe_json(out_dir / "system3_control_plane_status.json") or {}
    summary = {
        "runner_summary": status_json.get("overall_verdict"),
        "blocker_summary": (status_json.get("report_status") or {}).get("blocker_summary"),
        "option_summary": (status_json.get("report_status") or {}).get("option_summary"),
        "model_summary": (status_json.get("report_status") or {}).get("model_summary"),
        "markdown_summary": (status_json.get("report_status") or {}).get("markdown_summary"),
    }
    return ScenarioResult(
        name=name,
        api_base=api_base,
        returncode=proc.returncode,
        status="PASS" if proc.returncode == 0 else "FAIL",
        output_dir=str(out_dir.relative_to(root)),
        stdout_tail=tail(proc.stdout),
        stderr_tail=tail(proc.stderr),
        summary=summary,
    )


def endpoint_probe(api_base: str) -> Dict[str, Any]:
    probes = {}
    for endpoint in ["/api/state", "/api/broker/status", "/api/system_health", "/api/gain_rank", "/api/accuracy_trend"]:
        probes[endpoint] = fetch_endpoint(api_base, endpoint)
    return probes


def write_master_reports(root: Path, base_out: Path, compile_result: Dict[str, Any], scenarios: List[ScenarioResult], probes: Dict[str, Any]) -> Path:
    latest = root / "reports" / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    total_pass = sum(1 for s in scenarios if s.status == "PASS")
    data = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": "PASS_SCRIPTS_AND_SCENARIOS_REVIEW_REQUIRED" if compile_result["all_pass"] and total_pass >= 1 else "FAIL_REVIEW_REQUIRED",
        "compile_check": compile_result,
        "scenarios": [asdict(s) for s in scenarios],
        "endpoint_probes": probes,
        "proof_folder": str(base_out.relative_to(root)),
    }
    (latest / "system3_one_click_max_proof.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# System3 One-Click Max Proof Report",
        "",
        f"Generated UTC: `{data['generated_at_utc']}`",
        "",
        "## Verdict",
        "",
        f"`{data['verdict']}`",
        "",
        "## Compile Check",
        "",
        f"- **All pass**: `{compile_result['all_pass']}`",
        "",
        "| Script | Status | Return Code |",
        "|---|---:|---:|",
    ]
    for r in compile_result["results"]:
        lines.append(f"| `{r['path']}` | `{r['status']}` | `{r['returncode']}` |")
    lines.extend(["", "## Scenario Runs", "", "| Scenario | API Base | Status | Return Code | Output Folder |", "|---|---|---:|---:|---|"])
    for s in scenarios:
        lines.append(f"| `{s.name}` | `{s.api_base}` | `{s.status}` | `{s.returncode}` | `{s.output_dir}` |")
    lines.extend(["", "## Endpoint Probe Summary", "", "| API Base | Endpoint | OK | Error |", "|---|---|---:|---|"])
    for api, probe_set in probes.items():
        for endpoint, result in probe_set.items():
            lines.append(f"| `{api}` | `{endpoint}` | `{result.get('ok')}` | `{result.get('error')}` |")
    lines.extend([
        "",
        "## What This Proves",
        "",
        "- Verification scripts compile and run where possible.",
        "- Local-only and API-backed scenarios are preserved separately.",
        "- Markdown, option visibility, model accuracy, blocker, and control-plane reports are bundled for review.",
        "",
        "## What This Does Not Prove",
        "",
        "- It does not prove live trading readiness.",
        "- It does not fix runtime bugs by itself.",
        "- It does not guarantee model profitability.",
        "- It does not touch credentials or enable orders.",
        "",
        "## Next Rule",
        "",
        "Review this report and the preserved scenario folders before patching runtime code.",
    ])
    (latest / "system3_one_click_max_proof.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    shutil.copy2(latest / "system3_one_click_max_proof.json", base_out / "system3_one_click_max_proof.json")
    shutil.copy2(latest / "system3_one_click_max_proof.md", base_out / "system3_one_click_max_proof.md")
    return latest / "system3_one_click_max_proof.md"


def zip_proof(root: Path, base_out: Path) -> Path:
    zip_path = root / "reports" / "latest" / f"system3_max_proof_{base_out.name}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in base_out.rglob("*"):
            if p.is_file():
                zf.write(p, p.relative_to(root).as_posix())
        for name in ["system3_one_click_max_proof.md", "system3_one_click_max_proof.json"]:
            p = root / "reports" / "latest" / name
            if p.exists():
                zf.write(p, p.relative_to(root).as_posix())
    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser(description="System3 one-click maximum safe proof runner")
    parser.add_argument("--root", default=None)
    parser.add_argument("--api-base", action="append", help="Optional API base. Can be used multiple times.")
    parser.add_argument("--skip-default-api", action="store_true")
    parser.add_argument("--skip-localhost", action="store_true")
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else repo_root_from_script()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    base_out = root / "reports" / "max_proof" / stamp
    base_out.mkdir(parents=True, exist_ok=True)

    compile_result = compile_check(root)
    probes: Dict[str, Any] = {}
    scenario_results: List[ScenarioResult] = []

    for name, api_base in unique_scenarios(args):
        if api_base:
            probes[api_base] = endpoint_probe(api_base)
        try:
            scenario_results.append(run_control_plane(root, name, api_base, base_out, args.timeout))
        except subprocess.TimeoutExpired as exc:
            out_dir = base_out / name
            out_dir.mkdir(parents=True, exist_ok=True)
            scenario_results.append(ScenarioResult(name, api_base, 124, "TIMEOUT", str(out_dir.relative_to(root)), tail(exc.stdout or ""), tail(exc.stderr or ""), {}))
        except Exception as exc:
            out_dir = base_out / name
            out_dir.mkdir(parents=True, exist_ok=True)
            scenario_results.append(ScenarioResult(name, api_base, 126, "ERROR", str(out_dir.relative_to(root)), "", f"{type(exc).__name__}: {exc}", {}))

    report_path = write_master_reports(root, base_out, compile_result, scenario_results, probes)
    zip_path = zip_proof(root, base_out)

    print("SYSTEM3_ONE_CLICK_MAX_PROOF_COMPLETE")
    print(json.dumps({
        "report": str(report_path.relative_to(root)),
        "zip": str(zip_path.relative_to(root)),
        "proof_folder": str(base_out.relative_to(root)),
    }, indent=2))
    return 0 if compile_result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
