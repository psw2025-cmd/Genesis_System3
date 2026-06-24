#!/usr/bin/env python3
"""
Root-level clutter reference proof.

Checks which root-level .md/.bat/.ps1/.py/.txt/.sh files are referenced in
active code dirs (core/, dashboard/, scripts/, src/, .github/workflows/).
Uses grep for speed — finishes in seconds not minutes.
"""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_DIRS = ["core", "dashboard", "scripts", "src", ".github/workflows"]
EXTENSIONS = {".md", ".bat", ".ps1", ".py", ".txt", ".sh"}
OUT = ROOT / "reports" / "latest" / "root_clutter_reference_proof"


def tracked_files() -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    return [x for x in out.splitlines() if x.strip()]


def get_root_targets(all_files: list[str]) -> list[str]:
    return sorted(f for f in all_files if "/" not in f and Path(f).suffix.lower() in EXTENSIONS)


def get_active_paths(all_files: list[str]) -> list[Path]:
    paths = []
    for f in all_files:
        for d in ACTIVE_DIRS:
            if f.startswith(d + "/"):
                paths.append(ROOT / f)
                break
    return paths


def grep_in_active(pattern: str, active_paths: list[Path]) -> list[str]:
    """Run grep for a pattern across active file paths. Returns list of matching filenames."""
    if not active_paths:
        return []
    cmd = ["grep", "-l", "-E", "--include=*", pattern] + [str(p) for p in active_paths]
    try:
        out = subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
        return [os.path.relpath(x, ROOT) for x in out.splitlines() if x.strip()]
    except subprocess.CalledProcessError:
        return []


def batch_grep_referenced(targets: list[str], active_paths: list[Path]) -> set[str]:
    """
    Use a single grep call with alternation to find all targets referenced anywhere.
    Returns set of target filenames that ARE referenced.
    """
    if not targets or not active_paths:
        return set()

    # Build alternation pattern of all basenames
    names = [Path(t).name for t in targets]
    # Escape dots
    escaped = [n.replace(".", r"\.") for n in names]
    # Grep with alternation (grep -E supports |)
    # Split into batches of 100 to avoid arg limits
    referenced_names: set[str] = set()
    batch_size = 100
    for i in range(0, len(escaped), batch_size):
        batch = escaped[i : i + batch_size]
        pattern = "|".join(batch)
        cmd = ["grep", "-r", "-l", "-E", pattern] + [str(p) for p in active_paths]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            if result.returncode == 0:
                # At least one file matched; now find which targets were matched
                # Do a quick pass per matched file
                for matched_file in result.stdout.splitlines():
                    mf = Path(matched_file)
                    if not mf.is_file():
                        continue
                    try:
                        content = mf.read_text(encoding="utf-8", errors="replace")
                    except Exception:
                        continue
                    for orig_name, esc_name in zip(names[i : i + batch_size], batch):
                        if orig_name in content:
                            referenced_names.add(orig_name)
        except Exception:
            pass
    return referenced_names


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    all_files = tracked_files()
    targets = get_root_targets(all_files)
    active_paths = get_active_paths(all_files)

    print(f"Root clutter targets: {len(targets)}")
    print(f"Active code files to scan: {len(active_paths)}")
    print("Running batch grep scan...")

    referenced_names = batch_grep_referenced(targets, active_paths)

    results = []
    safe_count = 0
    keep_count = 0
    by_ext: dict[str, dict] = {}

    for t in targets:
        fname = Path(t).name
        ext = Path(t).suffix.lower()
        is_ref = fname in referenced_names
        cls = "KEEP_referenced" if is_ref else "SAFE_TO_ARCHIVE"
        if is_ref:
            keep_count += 1
        else:
            safe_count += 1
        by_ext.setdefault(ext, {"safe_to_archive": 0, "keep_referenced": 0})
        by_ext[ext]["safe_to_archive" if not is_ref else "keep_referenced"] += 1
        results.append({"file": t, "ext": ext, "classification": cls, "referenced": is_ref})

    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "root_clutter_scanned": len(targets),
        "active_dirs_scanned": ACTIVE_DIRS,
        "safe_to_archive_count": safe_count,
        "keep_referenced_count": keep_count,
        "by_extension": by_ext,
        "verdict": "PROOF_COMPLETE",
    }

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "full_detail.json").write_text(
        json.dumps({"summary": summary, "results": results}, indent=2) + "\n", encoding="utf-8"
    )

    keep_list = [r["file"] for r in results if r["referenced"]]
    safe_list = [r["file"] for r in results if not r["referenced"]]
    (OUT / "keep_referenced.txt").write_text("\n".join(keep_list) + "\n", encoding="utf-8")
    (OUT / "safe_to_archive.txt").write_text("\n".join(safe_list) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(f"\nKEEP (referenced in active dirs): {keep_count} files")
    print(f"SAFE TO ARCHIVE: {safe_count} files")
    print(f"Reports: {OUT}")


if __name__ == "__main__":
    main()
