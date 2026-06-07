#!/usr/bin/env python3
"""System3 full repo verification collector.

This script is evidence-only. It does not start live trading, does not place
orders, does not log into broker services, and does not require private runtime
values. It collects backend, frontend, workflow, data/model/backtest/paper,
dashboard, and repo hygiene evidence into reports/latest/full_repo_verification.

It is designed to keep going after failures so the final artifact contains the
complete issue list instead of stopping at the first error.
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "reports" / "latest" / "full_repo_verification"

TEXT_SUFFIXES = {
    ".py", ".yml", ".yaml", ".json", ".md", ".txt", ".toml", ".ini", ".cfg",
    ".ps1", ".bat", ".sh", ".ts", ".tsx", ".js", ".jsx", ".html", ".css",
}

SAFE_ENV = {
    "SYSTEM3_MODE": "analyze",
    "ANALYZE_MODE": "1",
    "LIVE_TRADING_ENABLED": "0",
    "SYSTEM3_LIVE_TRADING_ALLOWED": "0",
    "PYTHONPATH": str(ROOT),
    "PYTHONIOENCODING": "utf-8",
    "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24": "true",
}

CRITICAL_PATHS = [
    "render.yaml",
    "Run-FullQA.ps1",
    "dashboard/backend/app.py",
    "dashboard/backend/Dockerfile",
    "dashboard/backend/requirements.txt",
    "dashboard/frontend/package.json",
    "core/utils/env_loader.py",
    "scripts/system3_master_proof_orchestrator.py",
    ".github/workflows/system3-auto-verifier.yml",
    ".github/workflows/system3-master-proof-control-plane.yml",
    ".github/workflows/repo-cleanliness-gate.yml",
]

PROOF_PATHS = [
    "docs/project_control/SYSTEM3_MASTER_STATUS.md",
    "reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json",
    "reports/latest/repo_cleanliness/05_cleanliness_summary.json",
    "reports/latest/proof_status_matrix/proof_status_matrix.json",
    "reports/latest/system3_master_control_plane/system3_master_control_plane.json",
]

SEARCH_GROUPS = {
    "backend": ["dashboard/backend", "app.py", "Dockerfile", "requirements"],
    "frontend": ["dashboard/frontend", "package.json", "vite", "react", "tsx"],
    "workflows": [".github/workflows", "upload-artifact", "checkout", "git push"],
    "data_history": ["data", "histor", "ohlc", "candle", "option", "chain", "duckdb", "sqlite", "parquet", "csv"],
    "model_training": ["model", "train", "retrain", "predict", "accuracy", "calibrat", "kronos", "wavelet"],
    "backtest": ["backtest", "walk", "strategy", "pnl", "performance", "validation"],
    "paper_analyzer": ["paper", "analyzer", "sandbox", "order", "trade", "position", "lifecycle", "fill"],
    "dashboard": ["dashboard", "chart", "ui", "frontend", "api", "pnl"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_cmd(name: str, cmd: list[str], out_dir: Path, timeout: int = 120, cwd: Path | None = None) -> dict[str, Any]:
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_") or "command"
    env = os.environ.copy()
    env.update(SAFE_ENV)
    started = utc_now()
    result: dict[str, Any] = {
        "name": name,
        "command": cmd,
        "cwd": str(cwd or ROOT),
        "started_utc": started,
        "timeout_seconds": timeout,
        "returncode": None,
        "timed_out": False,
        "ok": False,
        "stdout_file": f"commands/{safe_name}.stdout.txt",
        "stderr_file": f"commands/{safe_name}.stderr.txt",
    }
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd or ROOT),
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        result["returncode"] = proc.returncode
        result["ok"] = proc.returncode == 0
        write_text(out_dir / result["stdout_file"], proc.stdout)
        write_text(out_dir / result["stderr_file"], proc.stderr)
    except subprocess.TimeoutExpired as exc:
        result["timed_out"] = True
        result["returncode"] = 124
        result["ok"] = False
        write_text(out_dir / result["stdout_file"], exc.stdout or "")
        write_text(out_dir / result["stderr_file"], (exc.stderr or "") + "\nTIMEOUT\n")
    except Exception as exc:
        result["returncode"] = 1
        result["ok"] = False
        write_text(out_dir / result["stdout_file"], "")
        write_text(out_dir / result["stderr_file"], repr(exc))
    result["finished_utc"] = utc_now()
    return result


def tracked_files() -> list[str]:
    try:
        out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True, encoding="utf-8", errors="replace")
        return sorted(p for p in out.splitlines() if p.strip())
    except Exception:
        return sorted(rel(p) for p in ROOT.rglob("*") if p.is_file() and ".git/" not in rel(p))


def file_inventory(files: list[str]) -> dict[str, Any]:
    by_top = Counter((p.split("/", 1)[0] if "/" in p else ".") for p in files)
    by_suffix = Counter(Path(p).suffix.lower() or "[no_ext]" for p in files)
    large = []
    for f in files:
        p = ROOT / f
        try:
            size = p.stat().st_size
        except Exception:
            continue
        if size >= 5 * 1024 * 1024:
            large.append({"path": f, "bytes": size})
    duplicates: dict[str, list[str]] = defaultdict(list)
    for f in files:
        name = Path(f).name.lower()
        if name and name not in {"__init__.py", "readme.md"}:
            duplicates[name].append(f)
    duplicate_groups = {k: v for k, v in duplicates.items() if len(v) > 1}
    return {
        "tracked_file_count": len(files),
        "top_level_counts": dict(by_top.most_common(50)),
        "suffix_counts": dict(by_suffix.most_common(80)),
        "large_tracked_files_over_5mb": large[:200],
        "duplicate_basename_group_count": len(duplicate_groups),
        "duplicate_basename_sample": dict(list(sorted(duplicate_groups.items()))[:80]),
    }


def critical_path_status() -> list[dict[str, Any]]:
    rows = []
    for item in CRITICAL_PATHS:
        p = ROOT / item
        rows.append({
            "path": item,
            "exists": p.exists(),
            "bytes": p.stat().st_size if p.exists() and p.is_file() else 0,
        })
    return rows


def proof_status() -> list[dict[str, Any]]:
    rows = []
    for item in PROOF_PATHS:
        p = ROOT / item
        row: dict[str, Any] = {"path": item, "exists": p.exists(), "bytes": p.stat().st_size if p.exists() else 0}
        if p.exists() and p.suffix == ".json":
            try:
                data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
                row["keys"] = sorted(list(data.keys()))[:50]
                row["verdict"] = data.get("verdict")
                row["pass"] = data.get("pass")
                row["trade_ready"] = data.get("trade_ready")
            except Exception as exc:
                row["json_error"] = repr(exc)
        rows.append(row)
    return rows


def search_groups(files: list[str]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    lowered = [(f, f.lower()) for f in files]
    for group, terms in SEARCH_GROUPS.items():
        terms_lower = [t.lower() for t in terms]
        matches = [f for f, low in lowered if any(t in low for t in terms_lower)]
        data[group] = {"count": len(matches), "sample": matches[:200]}
    return data


def static_text_scan(files: list[str], out_dir: Path) -> dict[str, Any]:
    findings: dict[str, list[dict[str, Any]]] = {
        "live_mode_mentions": [],
        "hardcoded_localhost_mentions": [],
        "todo_fixme_mentions": [],
        "workflow_push_without_rebase": [],
    }
    for f in files:
        p = ROOT / f
        if p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if f.startswith(".git/") or f.startswith("node_modules/"):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        low = text.lower()
        if "live_trading_enabled" in low or "system3_live_trading_allowed" in low:
            findings["live_mode_mentions"].append({"path": f})
        if "localhost" in low or "127.0.0.1" in low:
            findings["hardcoded_localhost_mentions"].append({"path": f})
        if "todo" in low or "fixme" in low:
            findings["todo_fixme_mentions"].append({"path": f})
        if f.startswith(".github/workflows/") and "git push" in text and "pull --rebase" not in text and "rebase origin" not in text:
            findings["workflow_push_without_rebase"].append({"path": f})
    for key, rows in findings.items():
        write_json(out_dir / "static_scan" / f"{key}.json", rows[:500])
    return {key: {"count": len(rows), "sample": rows[:50]} for key, rows in findings.items()}


def command_plan(files: list[str]) -> list[tuple[str, list[str], int, Path | None]]:
    commands: list[tuple[str, list[str], int, Path | None]] = [
        ("git_status_short", ["git", "status", "--short"], 60, None),
        ("git_last_commit", ["git", "log", "-1", "--stat"], 60, None),
        ("python_version", [sys.executable, "--version"], 60, None),
        ("python_compile_backend_app", [sys.executable, "-m", "py_compile", "dashboard/backend/app.py"], 120, None),
        ("python_compile_env_loader", [sys.executable, "-m", "py_compile", "core/utils/env_loader.py"], 120, None),
        ("python_compile_master_orchestrator", [sys.executable, "-m", "py_compile", "scripts/system3_master_proof_orchestrator.py"], 120, None),
        ("python_compile_full_repo_verifier", [sys.executable, "-m", "py_compile", "scripts/system3_full_repo_verification.py"], 120, None),
        ("master_orchestrator_dry_run", [sys.executable, "scripts/system3_master_proof_orchestrator.py", "--auto-fix"], 180, None),
    ]
    if shutil.which("node"):
        commands.append(("node_version", ["node", "--version"], 60, None))
    if shutil.which("npm"):
        commands.append(("npm_version", ["npm", "--version"], 60, None))
        frontend_dir = ROOT / "dashboard" / "frontend"
        if (frontend_dir / "package.json").exists():
            commands.append(("frontend_package_scripts", ["npm", "run"], 90, frontend_dir))
            commands.append(("frontend_lint_if_present", ["npm", "run", "lint", "--if-present"], 180, frontend_dir))
            commands.append(("frontend_test_if_present", ["npm", "run", "test", "--if-present", "--", "--watch=false"], 180, frontend_dir))
            commands.append(("frontend_build_if_present", ["npm", "run", "build", "--if-present"], 240, frontend_dir))
    # Compile a representative set of Python files, capped to keep CI safe.
    py_files = [f for f in files if f.endswith(".py") and not f.startswith(("reports/", "audit_artifacts/"))]
    for idx, f in enumerate(py_files[:200], start=1):
        commands.append((f"py_compile_{idx:03d}_{Path(f).stem}", [sys.executable, "-m", "py_compile", f], 60, None))
    return commands


def publish_readme(out_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# System3 Full Repo Verification",
        "",
        f"Generated UTC: {summary['generated_utc']}",
        "",
        f"- Verdict: `{summary['verdict']}`",
        f"- Commands run: `{summary['command_summary']['total']}`",
        f"- Commands passed: `{summary['command_summary']['passed']}`",
        f"- Commands failed: `{summary['command_summary']['failed']}`",
        f"- Commands timed out: `{summary['command_summary']['timed_out']}`",
        f"- Trade ready: `{summary['trade_ready']}`",
        f"- Mode: `{summary['mode']}`",
        "",
        "## Main blockers",
        "",
    ]
    lines.extend([f"- `{b}`" for b in summary["blockers"]] or ["- None"])
    lines.extend(["", "## Important outputs", ""])
    lines.extend([
        "- `summary.json`",
        "- `commands_index.json`",
        "- `commands/*.stdout.txt`",
        "- `commands/*.stderr.txt`",
        "- `file_inventory.json`",
        "- `critical_paths.json`",
        "- `proof_status.json`",
        "- `search_groups.json`",
        "- `static_scan/*.json`",
    ])
    lines.extend(["", "## Safety", "", "Analyzer/Paper only. Live trading disabled. No broker login or order placement is performed by this verifier.", ""])
    write_text(out_dir / "README.md", "\n".join(lines))


def main() -> int:
    out_dir = Path(os.environ.get("SYSTEM3_FULL_VERIFY_OUT", str(DEFAULT_OUT)))
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = tracked_files()
    commands = command_plan(files)
    command_results = []
    for name, cmd, timeout, cwd in commands:
        command_results.append(run_cmd(name, cmd, out_dir, timeout=timeout, cwd=cwd))

    inv = file_inventory(files)
    critical = critical_path_status()
    proofs = proof_status()
    groups = search_groups(files)
    static = static_text_scan(files, out_dir)

    command_summary = {
        "total": len(command_results),
        "passed": sum(1 for r in command_results if r["ok"]),
        "failed": sum(1 for r in command_results if not r["ok"]),
        "timed_out": sum(1 for r in command_results if r["timed_out"]),
    }

    blockers = []
    missing_critical = [r["path"] for r in critical if not r["exists"]]
    if missing_critical:
        blockers.append("missing_critical_paths")
    if command_summary["failed"]:
        blockers.append("one_or_more_verification_commands_failed")
    if static["workflow_push_without_rebase"]["count"]:
        blockers.append("workflow_push_without_rebase_detected")
    if not any(p["path"] == "reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json" and p["exists"] for p in proofs):
        blockers.append("pipeline_readiness_report_missing")

    summary = {
        "generated_utc": utc_now(),
        "runner": {
            "python": sys.version,
            "platform": platform.platform(),
            "cwd": str(ROOT),
        },
        "mode": "Analyzer/Paper only; live trading disabled",
        "trade_ready": False,
        "verdict": "FULL_REPO_VERIFICATION_COMPLETE_WITH_BLOCKERS" if blockers else "FULL_REPO_VERIFICATION_COMPLETE_NO_STATIC_BLOCKERS",
        "blockers": blockers,
        "command_summary": command_summary,
        "critical_missing_count": len(missing_critical),
        "static_scan_counts": {k: v["count"] for k, v in static.items()},
        "tracked_file_count": len(files),
    }

    write_json(out_dir / "commands_index.json", command_results)
    write_json(out_dir / "file_inventory.json", inv)
    write_json(out_dir / "critical_paths.json", critical)
    write_json(out_dir / "proof_status.json", proofs)
    write_json(out_dir / "search_groups.json", groups)
    write_json(out_dir / "summary.json", summary)
    publish_readme(out_dir, summary)

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
