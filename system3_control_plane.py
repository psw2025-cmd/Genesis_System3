"""
Genesis System3 Global Control Plane

Safe, read-only-first command wrapper for repo inventory, cleanup classification,
proof checks, and readiness reporting.

This file does not place broker orders, does not enable live trading, does not
load secrets, and does not mutate runtime trading/model/database paths.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "reports" / "ci_truth" / "control_plane"

PROTECTED_PREFIXES = (
    "core/",
    "dashboard/",
    "services/",
    "broker/",
    "brokers/",
    "config/",
    "db/",
    "database/",
    "models/",
    "storage/",
)

GENERATED_PATTERNS = (
    ".pid",
    ".pyc",
    ".pyo",
    ".log",
    ".tmp",
    ".bak",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".duckdb",
)

ARCHIVE_HINTS = (
    "archive/",
    "backup",
    "old",
    "copy",
    "duplicate",
    "tmp_",
)

KEEP_EXACT = {
    ".github/workflows/ci.yml",
    ".github/scripts/root_architecture_gate.py",
    ".gitignore",
    "render.yaml",
    "dashboard/backend/app.py",
    "dashboard/backend/Dockerfile",
    "system3_ultra.py",
    "requirements-ci.txt",
}


@dataclass
class FileClassification:
    path: str
    classification: str
    reason: str
    protected: bool


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_out_dir() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def git_files() -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=120,
            check=False,
        )
        if proc.returncode == 0:
            return [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    except Exception:
        pass
    return sorted(str(p.relative_to(ROOT)).replace(os.sep, "/") for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts)


def is_protected(path: str) -> bool:
    return path.startswith(PROTECTED_PREFIXES)


def classify_path(path: str) -> FileClassification:
    lower = path.lower()
    protected = is_protected(path)

    if path in KEEP_EXACT:
        return FileClassification(path, "KEEP", "authoritative runtime/CI/control file", protected)

    if lower.startswith(".github/workflows/"):
        if lower == ".github/workflows/ci.yml":
            return FileClassification(path, "KEEP", "single active GitHub Actions workflow", protected)
        return FileClassification(path, "DELETE", "extra workflow file; CI policy allows only ci.yml", protected)

    if lower.startswith("state/") and lower.endswith(".pid"):
        return FileClassification(path, "DELETE", "generated runtime PID state", protected)

    if lower.startswith(("reports/", "audit_artifacts/", "logs/", "outputs/")):
        return FileClassification(path, "ARCHIVE", "generated proof/output/log artifact", protected)

    if any(lower.endswith(suffix) for suffix in GENERATED_PATTERNS):
        return FileClassification(path, "REVIEW", "generated-looking suffix; verify not required before deletion", protected)

    if any(hint in lower for hint in ARCHIVE_HINTS):
        return FileClassification(path, "REVIEW", "archive/backup/duplicate naming hint; verify references before deletion", protected)

    if lower.startswith("docs/") and ("final" in lower or "complete" in lower or "success" in lower or "phases_" in lower):
        return FileClassification(path, "ARCHIVE", "historical documentation candidate", protected)

    if lower.startswith("scripts/"):
        return FileClassification(path, "MERGE", "script should be merged behind global control plane if still useful", protected)

    if protected:
        return FileClassification(path, "KEEP", "protected runtime path", protected)

    return FileClassification(path, "REVIEW", "no safe automatic decision", protected)


def build_inventory() -> dict:
    files = git_files()
    classes = [classify_path(path) for path in files]
    summary: dict[str, int] = {}
    for item in classes:
        summary[item.classification] = summary.get(item.classification, 0) + 1
    payload = {
        "generated_utc": utc_now(),
        "repo": "psw2025-cmd/Genesis_System3",
        "mode": "read_only_inventory",
        "file_count": len(files),
        "summary": summary,
        "files": [asdict(item) for item in classes],
    }
    return payload


def write_json(name: str, payload: dict) -> Path:
    ensure_out_dir()
    out = OUT_DIR / name
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return out


def cmd_inventory(args: argparse.Namespace) -> int:
    payload = build_inventory()
    out = write_json("file_inventory_classification.json", payload)
    print(json.dumps({"status": "OK", "output": str(out), "summary": payload["summary"]}, indent=2))
    return 0


def cmd_classify(args: argparse.Namespace) -> int:
    payload = build_inventory()
    filtered = [item for item in payload["files"] if item["classification"] == args.classification]
    result = {
        "generated_utc": utc_now(),
        "classification": args.classification,
        "count": len(filtered),
        "files": filtered,
    }
    out = write_json(f"classification_{args.classification.lower()}.json", result)
    print(json.dumps({"status": "OK", "output": str(out), "count": len(filtered)}, indent=2))
    return 0


def cmd_cleanup(args: argparse.Namespace) -> int:
    payload = build_inventory()
    candidates = [
        item for item in payload["files"]
        if item["classification"] == "DELETE" and not item["protected"]
    ]
    result = {
        "generated_utc": utc_now(),
        "mode": "dry_run" if args.dry_run else "blocked_apply",
        "apply_allowed": False,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "note": "Apply mode is intentionally blocked in this control plane. Delete via reviewed commit only.",
    }
    out = write_json("cleanup_dry_run.json", result)
    print(json.dumps({"status": "OK", "output": str(out), "candidate_count": len(candidates), "apply_allowed": False}, indent=2))
    return 0


def cmd_proofs(args: argparse.Namespace) -> int:
    proof_paths = [
        "reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json",
        "reports/latest/system3_master_control_plane/system3_master_control_plane.json",
        "docs/project_control/REPO_CLEANUP_MANIFEST_20260616.md",
        "docs/project_control/GLOBAL_CONTROL_PLANE_STRUCTURE_20260616.md",
    ]
    result = {
        "generated_utc": utc_now(),
        "proofs": [
            {"path": path, "exists": (ROOT / path).exists()} for path in proof_paths
        ],
        "live_trading_allowed": False,
        "mode": "Analyzer/Paper only",
    }
    out = write_json("proofs_summary.json", result)
    print(json.dumps({"status": "OK", "output": str(out), "proofs": result["proofs"]}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Genesis System3 safe global control plane")
    sub = parser.add_subparsers(dest="command", required=True)

    p_inventory = sub.add_parser("inventory", help="Build file inventory and classification")
    p_inventory.set_defaults(func=cmd_inventory)

    p_classify = sub.add_parser("classify", help="Export files for one classification")
    p_classify.add_argument("classification", choices=["KEEP", "DELETE", "ARCHIVE", "MERGE", "REVIEW"])
    p_classify.set_defaults(func=cmd_classify)

    p_cleanup = sub.add_parser("cleanup", help="Safe cleanup dry-run only")
    p_cleanup.add_argument("--dry-run", action="store_true", default=True)
    p_cleanup.set_defaults(func=cmd_cleanup)

    p_proofs = sub.add_parser("proofs", help="Summarize proof artifacts")
    p_proofs.set_defaults(func=cmd_proofs)

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
