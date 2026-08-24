#!/usr/bin/env python3
"""Read-only mounted-drive inventory against the canonical Git cloud checkout.

The scanner never reads secret-like files, emits secret values, follows links,
or mutates source data.  Its only output is one RFC 4180 CSV.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


COLUMNS = [
    "File Name", "Path", "Drive", "Repo (Laptop/Cloud)", "Status (Missing in Cloud / Duplicate / Outdated / Already Synced)",
    "Reason (Why missing or outdated)", "Improvement Potential (Prediction accuracy, dashboard, orchestration)",
    "Global Best Practice Comparison", "Better Solution Reference (tools, workflows, datasets)",
]

SKIP_DIRS = {
    "$recycle.bin", "system volume information", "windows", "program files", "program files (x86)",
    "programdata", "appdata", ".git", ".svn", ".hg", "node_modules", ".venv", "venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", "dist", "build", "target",
    "packages", "cache", "caches", "temp", "tmp",
}
SECRET_RE = re.compile(r"(^|[._-])(secret|credential|token|apikey|api_key|private[_-]?key|password|passwd)([._-]|$)", re.I)
RELEVANT_RE = re.compile(
    r"genesis|system3|trading|market|dhan|option|equity|model|predict|feature|backtest|dashboard|broker|portfolio|catalyst|audit",
    re.I,
)
EXTENSIONS = {
    ".py", ".md", ".yaml", ".yml", ".json", ".csv", ".parquet", ".feather", ".arrow", ".ipynb",
    ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".sql", ".toml", ".ini", ".cfg", ".txt",
    ".ps1", ".bat", ".sh", ".png", ".jpg", ".jpeg", ".svg", ".webp", ".pkl", ".joblib",
}
MAX_HASH_BYTES = 512 * 1024 * 1024


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-c", f"safe.directory={repo.as_posix()}", "-C", str(repo), *args], text=True).strip()


def mounted_roots() -> list[Path]:
    if os.name != "nt":
        return [Path("/")]
    import ctypes
    mask = ctypes.windll.kernel32.GetLogicalDrives()
    return [Path(f"{chr(65 + i)}:\\") for i in range(26) if mask & (1 << i) and Path(f"{chr(65 + i)}:\\").exists()]


def sha256(path: Path, size: int) -> str | None:
    if size > MAX_HASH_BYTES:
        return None
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()
    except (OSError, PermissionError):
        return None


def useful_fields(path: Path) -> tuple[str, str, str]:
    ext = path.suffix.lower()
    if ext in {".csv", ".parquet", ".feather", ".arrow"}:
        return (
            "Prediction: candidate data/lineage; require OOS proof.",
            "Immutable raw+manifest+availability time+leakage-safe OOS.",
            "DVC; GCS versioning/retention; System3 benchmark policy.",
        )
    if ext in {".pkl", ".joblib"} or re.search(r"model|predict|feature|backtest", path.name, re.I):
        return (
            "Prediction: challenger asset; require lineage/cost/drift proof.",
            "Immutable registry; same-window baseline/champion walk-forward.",
            "MLflow; DVC; PREDICTION_WORLD_CLASS_BENCHMARK_POLICY.md.",
        )
    if ext in {".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".png", ".jpg", ".jpeg", ".svg", ".webp"}:
        return (
            "Dashboard: candidate UI/chart asset; mock data is not truth.",
            "API/UI parity+accessibility+fresh browser/network proof.",
            "Playwright traces; WCAG; System3 22-tab contract.",
        )
    return (
        "Orchestration: inspect/test on isolated branch before adoption.",
        "One authority+least privilege+provenance+idempotent rollback.",
        "GitHub OIDC; SLSA; System3 preflight/closure policies.",
    )


def cloud_inventory(repo: Path):
    tracked = git(repo, "ls-files", "-z").split("\0")
    records, by_hash, by_name = [], defaultdict(list), defaultdict(list)
    for rel in filter(None, tracked):
        path = repo / rel
        try:
            stat = path.stat()
        except OSError:
            continue
        digest = sha256(path, stat.st_size)
        item = {"path": path, "rel": rel.replace("\\", "/"), "name": path.name, "size": stat.st_size, "mtime": stat.st_mtime, "hash": digest}
        records.append(item)
        if digest:
            by_hash[digest].append(item)
        by_name[path.name.lower()].append(item)
    return records, by_hash, by_name


def local_candidates(roots: list[Path], canonical_repo: Path):
    canonical = str(canonical_repo.resolve()).lower()
    for root in roots:
        for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
            current_lower = current.lower()
            if current_lower.startswith(canonical):
                dirs[:] = []
                continue
            dirs[:] = [d for d in dirs if d.lower() not in SKIP_DIRS and not SECRET_RE.search(d)]
            relevant_dir = bool(RELEVANT_RE.search(current))
            for name in files:
                path = Path(current) / name
                if SECRET_RE.search(name) or path.suffix.lower() not in EXTENSIONS:
                    continue
                if not relevant_dir and not RELEVANT_RE.search(name):
                    continue
                try:
                    stat = path.stat()
                except (OSError, PermissionError):
                    continue
                yield {"path": path, "name": name, "size": stat.st_size, "mtime": stat.st_mtime, "hash": None}


def listed_candidates(lists: list[Path], canonical_repo: Path):
    canonical = str(canonical_repo.resolve()).lower()
    seen: set[str] = set()
    for listing in lists:
        with listing.open("r", encoding="utf-8-sig", errors="replace") as handle:
            for raw in handle:
                value = raw.rstrip("\r\n")
                if not value or value.lower().startswith(canonical) or value.lower() in seen:
                    continue
                seen.add(value.lower())
                path = Path(value)
                if SECRET_RE.search(path.name):
                    continue
                try:
                    stat = path.stat()
                except (OSError, PermissionError):
                    continue
                yield {"path": path, "name": path.name, "size": stat.st_size, "mtime": stat.st_mtime, "hash": None}


def row(item, repo_kind: str, status: str, reason: str):
    potential, practice, reference = useful_fields(item["path"])
    modified = datetime.fromtimestamp(item["mtime"], timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    digest_note = f"h={item['hash']}" if item["hash"] else "h=NOT_COMPUTED"
    return {
        COLUMNS[0]: item["name"], COLUMNS[1]: str(item["path"]), COLUMNS[2]: item["path"].drive or "/",
        COLUMNS[3]: repo_kind, COLUMNS[4]: status,
        COLUMNS[5]: f"{reason};s={item['size']};m={modified};{digest_note}",
        COLUMNS[6]: potential, COLUMNS[7]: practice, COLUMNS[8]: reference,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--candidate-list", type=Path, action="append", default=[])
    args = parser.parse_args()
    repo = args.repo.resolve()
    cloud, cloud_hashes, cloud_names = cloud_inventory(repo)
    output = args.output.resolve()
    roots = mounted_roots()
    local = list(listed_candidates(args.candidate_list, repo)) if args.candidate_list else list(local_candidates(roots, repo))
    cloud_size_count = defaultdict(int)
    for item in cloud:
        if item["hash"]:
            cloud_size_count[item["size"]] += 1
    local_size_count = defaultdict(int)
    local_name_size_count = defaultdict(int)
    for item in local:
        local_size_count[item["size"]] += 1
        local_name_size_count[(item["name"].lower(), item["size"])] += 1
    # Stage hashing: digest only files that can possibly match by byte length,
    # plus same-name candidates needed for an exact synced/outdated decision.
    for item in local:
        if cloud_size_count[item["size"]] <= 3 and cloud_size_count[item["size"]] > 0 or local_name_size_count[(item["name"].lower(), item["size"])] > 1 or item["name"].lower() in cloud_names:
            item["hash"] = sha256(item["path"], item["size"])
    local_hash_count = defaultdict(int)
    classified = []
    for item in local:
        if item["hash"]:
            local_hash_count[item["hash"]] += 1

    rows = [row(item, "Cloud", "Already Synced", f"Tracked by canonical cloud main {git(repo, 'rev-parse', 'HEAD')}; rel={item['rel']}") for item in cloud]
    for item in local:
        digest = item["hash"]
        same_name = cloud_names.get(item["name"].lower(), [])
        if digest and digest in cloud_hashes:
            status = "Already Synced"
            reason = "Byte-identical SHA-256 exists in canonical cloud main at " + "|".join(x["rel"] for x in cloud_hashes[digest][:5])
        elif digest and local_hash_count[digest] > 1:
            status = "Duplicate"
            reason = "Byte-identical duplicate exists on laptop but no identical cloud-main object was found"
        elif same_name:
            status = "Outdated"
            reason = "Same filename exists in cloud main with different content; semantic/version review required at " + "|".join(x["rel"] for x in same_name[:5])
        else:
            status = "Missing in Cloud"
            reason = "Relevant candidate has no same-name or byte-identical object in canonical cloud main; usefulness remains unproven"
        classified.append((item, status, reason))

    # Collapse byte-identical clone/report occurrences while preserving counts
    # and representative paths in the single CSV. Different hashes never merge.
    groups = defaultdict(list)
    for item, status, reason in classified:
        identity = item["hash"] or f"UNHASHED:{item['name'].lower()}:{item['size']}"
        groups[(status, identity, item["name"].lower())].append((item, reason))
    for (_status, _identity, _name), occurrences in groups.items():
        item, reason = occurrences[0]
        item = dict(item)
        item["path"] = occurrences[0][0]["path"]
        rows.append(row(item, "Laptop", _status, f"{reason}; occurrences={len(occurrences)}"))

    rows.sort(key=lambda r: (r[COLUMNS[3]], r[COLUMNS[4]], r[COLUMNS[2]], r[COLUMNS[1]].lower()))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)
    print(f"OUTPUT={output}")
    print(f"DRIVES={','.join(str(x) for x in roots)} CLOUD={len(cloud)} LAPTOP={len(local)} ROWS={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
