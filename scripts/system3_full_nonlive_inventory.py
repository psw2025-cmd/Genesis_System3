#!/usr/bin/env python3
"""Generate exact recursive repository inventory and dependency-oriented counts.

Read-only. Uses git ls-files so ignored caches, virtual environments, market data,
and generated node_modules are excluded from repository evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

TEXT_EXTENSIONS = {
    ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".json", ".yml", ".yaml",
    ".toml", ".ini", ".cfg", ".conf", ".md", ".txt", ".csv", ".html", ".css",
    ".scss", ".sql", ".ps1", ".sh", ".bat", ".dockerfile", ".xml",
}
CATEGORY_RULES = {
    "python": lambda p: p.suffix.lower() == ".py",
    "javascript_typescript": lambda p: p.suffix.lower() in {".js", ".jsx", ".ts", ".tsx"},
    "tests": lambda p: "test" in p.name.lower() or "tests" in p.parts,
    "workflows": lambda p: p.parts[:2] == (".github", "workflows"),
    "dashboard": lambda p: p.parts and p.parts[0] == "dashboard",
    "frontend": lambda p: "frontend" in p.parts,
    "backend": lambda p: "backend" in p.parts,
    "api_route": lambda p: "router" in p.name.lower() or "routers" in p.parts or "api" in p.name.lower(),
    "broker": lambda p: "broker" in p.as_posix().lower() or "dhan" in p.as_posix().lower(),
    "order": lambda p: "order" in p.as_posix().lower(),
    "risk": lambda p: "risk" in p.as_posix().lower() or "kill_switch" in p.as_posix().lower(),
    "model_ml": lambda p: any(token in p.as_posix().lower() for token in ("model", "predict", "training", "ml_")),
    "backtest": lambda p: any(token in p.as_posix().lower() for token in ("backtest", "walkforward", "walk_forward")),
    "scheduler": lambda p: any(token in p.as_posix().lower() for token in ("scheduler", "schedule", "cron")),
    "config": lambda p: p.suffix.lower() in {".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".conf", ".env"},
    "database": lambda p: p.suffix.lower() in {".db", ".sqlite", ".sqlite3", ".sql"},
    "reports": lambda p: p.parts and p.parts[0] in {"reports", "runtime_reports"},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_output(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True, encoding="utf-8").strip()


def line_count(path: Path) -> int | None:
    suffix = path.suffix.lower()
    if suffix not in TEXT_EXTENSIONS and path.name.lower() not in {"dockerfile", "makefile"}:
        return None
    try:
        with path.open("rb") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    tracked = [Path(value) for value in git_output(root, "ls-files", "-z").split("\0") if value]
    tracked = sorted(tracked, key=lambda p: p.as_posix().lower())
    rows: list[dict[str, object]] = []
    extension_counts: Counter[str] = Counter()
    top_level_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    category_lines: Counter[str] = Counter()
    basenames: dict[str, list[str]] = defaultdict(list)
    existing_files = missing_files = total_bytes = total_lines = text_files = 0

    for relative in tracked:
        path = root / relative
        exists = path.is_file()
        size = path.stat().st_size if exists else 0
        lines = line_count(path) if exists else None
        extension = relative.suffix.lower() or "<none>"
        top_level = relative.parts[0] if relative.parts else "<root>"
        categories = [name for name, rule in CATEGORY_RULES.items() if rule(relative)]
        extension_counts[extension] += 1
        top_level_counts[top_level] += 1
        basenames[relative.name.lower()].append(relative.as_posix())
        for category in categories:
            category_counts[category] += 1
            if lines is not None:
                category_lines[category] += lines
        if exists:
            existing_files += 1
            total_bytes += size
        else:
            missing_files += 1
        if lines is not None:
            text_files += 1
            total_lines += lines
        rows.append({
            "path": relative.as_posix(),
            "exists": exists,
            "bytes": size,
            "lines": lines,
            "extension": extension,
            "top_level": top_level,
            "categories": ",".join(categories),
        })

    duplicate_groups = {name: paths for name, paths in basenames.items() if len(paths) > 1}
    duplicate_files = sum(len(paths) for paths in duplicate_groups.values())
    directories = {str(Path(row["path"]).parent.as_posix()) for row in rows}
    directories.discard(".")

    manifest_csv = output / "tracked_file_manifest.csv"
    with manifest_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["path"])
        writer.writeheader()
        writer.writerows(rows)

    duplicate_json = output / "duplicate_basenames.json"
    duplicate_json.write_text(json.dumps(duplicate_groups, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "repository": "psw2025-cmd/Genesis_System3",
        "commit_sha": git_output(root, "rev-parse", "HEAD"),
        "branch_or_ref": os.getenv("GITHUB_REF", "local"),
        "tracked_files": len(tracked),
        "existing_tracked_files": existing_files,
        "missing_tracked_files": missing_files,
        "tracked_directories": len(directories),
        "tracked_bytes": total_bytes,
        "text_files_counted": text_files,
        "text_lines_counted": total_lines,
        "extension_counts": dict(extension_counts.most_common()),
        "top_level_counts": dict(top_level_counts.most_common()),
        "category_file_counts": dict(sorted(category_counts.items())),
        "category_line_counts": dict(sorted(category_lines.items())),
        "duplicate_basename_groups": len(duplicate_groups),
        "files_in_duplicate_basename_groups": duplicate_files,
        "manifest_file": str(manifest_csv),
        "manifest_bytes": manifest_csv.stat().st_size,
        "manifest_sha256": sha256(manifest_csv),
        "duplicate_report_file": str(duplicate_json),
        "duplicate_report_sha256": sha256(duplicate_json),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
    summary_path = output / "inventory_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if missing_files == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
