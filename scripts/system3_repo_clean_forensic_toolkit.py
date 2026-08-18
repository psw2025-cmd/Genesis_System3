#!/usr/bin/env python3
"""Genesis System3 full-repo cleanup forensic toolkit.

REPORT ONLY. Scans every current tracked file, duplicate/reference/import evidence,
Git storage, GitHub repository metadata, Actions artifacts/caches, and local
ignored/untracked disk. It never deletes/moves files, rewrites history, reads
broker secrets, changes IAM, or touches trading/order paths.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import heapq
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "SYSTEM3_REPO_CLEAN_FORENSIC_V1_1"
TEXT_SUFFIXES = {
    ".py", ".pyi", ".yml", ".yaml", ".json", ".md", ".txt", ".toml", ".ini",
    ".cfg", ".ps1", ".bat", ".cmd", ".sh", ".ts", ".tsx", ".js", ".jsx",
    ".mjs", ".cjs", ".html", ".css", ".scss", ".sql", ".xml", ".csv",
}
SOURCE_SUFFIXES = {".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".sh", ".ps1"}
PROTECTED_PREFIXES = (
    ".github/", ".cursor/", "dashboard/backend/", "dashboard/frontend/src/",
    "core/", "config/", "scripts/", "tests/", "docs/authority/",
)
PROTECTED_BASENAMES = {
    "AGENTS.md", "agent_policy.yaml", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "pyproject.toml", "requirements.txt", "package.json", "package-lock.json", "pnpm-lock.yaml",
    "yarn.lock", ".gitignore", ".dockerignore", ".gitattributes",
}
GENERATED_BASENAMES = {"desktop.ini", ".DS_Store"}
GENERATED_SUFFIXES = {".pyc", ".pyo"}
GENERATED_PARTS = {
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".coverage_cache",
    "node_modules", "dist", "build", ".next", ".vite", ".turbo",
}
SUSPICIOUS_PARTS = {
    "archive", "archived", "backup", "backups", "copy", "copies", "old", "obsolete",
    "deprecated", "quarantine", "tmp", "temp", "scratch", "legacy",
}
RUNTIME_WORDS = {
    "broker", "dhan", "order", "trade", "trading", "live", "paper", "risk", "strategy",
    "scanner", "signal", "position", "portfolio", "websocket", "scheduler", "deploy", "cloud",
    "secret", "token", "auth", "dashboard", "api", "worker", "forecast", "rank", "model",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def human_bytes(value: int) -> str:
    n = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if n < 1024 or unit == "TiB":
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{value} B"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(cmd: list[str], root: Path, timeout: int = 180) -> tuple[int, str, str]:
    env = dict(os.environ)
    env.update({
        "SYSTEM3_MODE": "analyze", "ANALYZE_MODE": "1", "LIVE_TRADING_ENABLED": "0",
        "SYSTEM3_LIVE_TRADING_ALLOWED": "0", "AUTO_EXECUTE_TRADES": "0",
    })
    try:
        p = subprocess.run(
            cmd, cwd=root, env=env, text=True, encoding="utf-8", errors="replace",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
        )
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", (exc.stderr or "") + "\nTIMEOUT"


def git(root: Path, *args: str, timeout: int = 180) -> tuple[int, str, str]:
    return run(["git", *args], root, timeout)


def repo_root(start: Path) -> Path:
    rc, out, err = run(["git", "rev-parse", "--show-toplevel"], start, 30)
    if rc:
        raise RuntimeError(err.strip() or "not a git repository")
    return Path(out.strip()).resolve()


def git_file_list(root: Path, ignored: bool | None = None) -> list[str]:
    if ignored is None:
        args = ["ls-files", "-z"]
    elif ignored:
        args = ["ls-files", "--others", "--ignored", "--exclude-standard", "-z"]
    else:
        args = ["ls-files", "--others", "--exclude-standard", "-z"]
    rc, out, _ = git(root, *args)
    return sorted(x for x in out.split("\0") if x) if rc == 0 else []


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_text_path(path: str) -> bool:
    p = Path(path)
    return p.name in {"Dockerfile", "Makefile", "Procfile", ".gitignore", ".dockerignore", ".gitattributes"} or p.suffix.lower() in TEXT_SUFFIXES


def is_source_like(path: str) -> bool:
    return Path(path).suffix.lower() in SOURCE_SUFFIXES


def is_generated_noise(path: str) -> tuple[bool, str | None]:
    p = Path(path)
    if p.name in GENERATED_BASENAMES:
        return True, "generated_os_noise"
    if p.suffix.lower() in GENERATED_SUFFIXES:
        return True, "generated_python_bytecode"
    if set(p.parts).intersection(GENERATED_PARTS):
        return True, "generated_build_or_cache"
    return False, None


def is_protected(path: str) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    p = Path(path)
    if p.name in PROTECTED_BASENAMES:
        reasons.append("protected_basename")
    if any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES):
        reasons.append("protected_runtime_or_governance_prefix")
    if any(word in path.lower() for word in RUNTIME_WORDS):
        reasons.append("runtime_sensitive_name")
    return bool(reasons), reasons


def suspicious_path(path: str) -> list[str]:
    hits = set(part.lower() for part in Path(path).parts).intersection(SUSPICIOUS_PARTS)
    if re.search(r"(?:^|[._-])(old|bak|backup|copy|tmp|temp|legacy|deprecated)(?:[._-]|$)", Path(path).name.lower()):
        hits.add("suspicious_filename")
    return sorted(hits)


@lru_cache(maxsize=None)
def read_text(path: Path, limit: int = 3 * 1024 * 1024) -> str | None:
    try:
        if path.stat().st_size > limit or path.is_symlink():
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def module_name(path: str) -> str | None:
    if not path.endswith(".py"):
        return None
    p = Path(path)
    parts = list(p.parent.parts) if p.name == "__init__.py" else list(p.with_suffix("").parts)
    if not parts or any(not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", x) for x in parts):
        return None
    return ".".join(parts)


def python_reverse_imports(root: Path, files: list[str]) -> dict[str, list[str]]:
    module_to_file = {m: f for f in files if (m := module_name(f))}
    reverse: dict[str, set[str]] = defaultdict(set)
    for importer in (f for f in files if f.endswith(".py")):
        text = read_text(root / importer)
        if text is None:
            continue
        try:
            tree = ast.parse(text, filename=importer)
        except SyntaxError:
            continue
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
                imports.update(f"{node.module}.{a.name}" for a in node.names if a.name != "*")
        for name in imports:
            probe = name
            while probe:
                target = module_to_file.get(probe)
                if target and target != importer:
                    reverse[target].add(importer)
                    break
                probe = probe.rsplit(".", 1)[0] if "." in probe else ""
    return {k: sorted(v) for k, v in reverse.items()}


def literal_refs(root: Path, candidate: str, text_files: list[str], family: set[str]) -> dict[str, Any]:
    path_token = candidate.replace("\\", "/")
    basename = Path(candidate).name
    stem = Path(candidate).stem
    refs = []
    for source in text_files:
        if source == candidate or source in family:
            continue
        text = read_text(root / source)
        if text is None:
            continue
        norm = text.replace("\\", "/")
        kind = None
        if path_token in norm:
            kind = "exact_path_literal"
        elif basename and basename in text:
            kind = "basename_literal"
        elif len(stem) >= 8 and re.search(rf"(?<![A-Za-z0-9_]){re.escape(stem)}(?![A-Za-z0-9_])", text):
            kind = "stem_literal"
        if kind:
            refs.append({"source": source, "kind": kind})
            if len(refs) >= 100:
                break
    critical = [
        r for r in refs
        if r["source"].startswith(".github/workflows/")
        or Path(r["source"]).name in {"Dockerfile", "package.json", "pyproject.toml", "requirements.txt", ".gitattributes"}
    ]
    return {"count": len(refs), "critical_count": len(critical), "refs": refs[:40], "critical_refs": critical[:40]}


def last_change(root: Path, path: str) -> dict[str, Any]:
    rc, out, _ = git(root, "log", "-1", "--format=%H|%ct|%an|%s", "--", path, timeout=60)
    if rc or not out.strip():
        return {"commit": None, "epoch": None, "author": None, "subject": None}
    parts = out.strip().split("|", 3)
    return {
        "commit": parts[0], "epoch": int(parts[1]) if parts[1].isdigit() else None,
        "author": parts[2] if len(parts) > 2 else None,
        "subject": parts[3] if len(parts) > 3 else None,
    }


def authority_score(path: str, meta: dict[str, Any]) -> tuple[int, str]:
    protected, _ = is_protected(path)
    score = (100 if protected else 0) + min(meta.get("ref_count", 0), 25) * 4 + min(meta.get("python_importers", 0), 25) * 5
    if path.startswith(("dashboard/", "core/", "scripts/")):
        score += 20
    if suspicious_path(path):
        score -= 20
    return score - min(path.count("/"), 8), path


def disk_inventory(root: Path, paths: list[str]) -> dict[str, Any]:
    rows, total = [], 0
    by_top: dict[str, int] = defaultdict(int)
    for rel in paths:
        try:
            size = (root / rel).stat().st_size
        except OSError:
            continue
        total += size
        by_top[rel.split("/", 1)[0]] += size
        rows.append({"path": rel, "bytes": size, "human": human_bytes(size)})
    return {
        "count": len(rows), "bytes": total, "human": human_bytes(total),
        "top_files": sorted(rows, key=lambda x: x["bytes"], reverse=True)[:500],
        "top_level_bytes": [
            {"path": k, "bytes": v, "human": human_bytes(v)}
            for k, v in sorted(by_top.items(), key=lambda x: x[1], reverse=True)
        ],
    }


def git_storage(root: Path, topn: int = 100) -> dict[str, Any]:
    shallow_rc, shallow_out, _ = git(root, "rev-parse", "--is-shallow-repository", timeout=30)
    history_complete = not (shallow_rc == 0 and shallow_out.strip().lower() == "true")
    rc, out, _ = git(root, "count-objects", "-vH", timeout=60)
    counts = {}
    if rc == 0:
        for line in out.splitlines():
            if ": " in line:
                k, v = line.split(": ", 1)
                counts[k] = v
    largest: list[tuple[int, str, str]] = []
    rev = subprocess.Popen(
        ["git", "rev-list", "--objects", "--all"], cwd=root,
        stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
    )
    cat = subprocess.Popen(
        ["git", "cat-file", "--batch-check=%(objecttype) %(objectname) %(objectsize) %(rest)"],
        cwd=root, stdin=rev.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace",
    )
    if rev.stdout:
        rev.stdout.close()
    assert cat.stdout is not None
    for line in cat.stdout:
        parts = line.rstrip().split(" ", 3)
        if len(parts) < 3 or parts[0] != "blob":
            continue
        try:
            size = int(parts[2])
        except ValueError:
            continue
        item = (size, parts[1], parts[3] if len(parts) > 3 else "")
        if len(largest) < topn:
            heapq.heappush(largest, item)
        elif size > largest[0][0]:
            heapq.heapreplace(largest, item)
    cat.wait(timeout=180)
    if cat.stderr:
        cat.stderr.read(); cat.stderr.close()
    if cat.stdout:
        cat.stdout.close()
    rev.wait(timeout=180)
    return {
        "history_complete": history_complete,
        "history_scope": "FULL" if history_complete else "SHALLOW_CURRENT_CHECKOUT",
        "count_objects": counts,
        "largest_history_blobs": [
            {"bytes": s, "human": human_bytes(s), "object": h, "path": p}
            for s, h, p in sorted(largest, reverse=True)
        ],
    }


def _github_get(url: str, token: str) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def github_storage_inventory(max_pages: int = 100) -> dict[str, Any]:
    token, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        return {"available": False, "reason": "GITHUB_TOKEN/GITHUB_REPOSITORY unavailable"}

    result: dict[str, Any] = {"available": True, "repository": repo}
    try:
        repo_meta = _github_get(f"https://api.github.com/repos/{repo}", token)
        size_kb = int(repo_meta.get("size") or 0)
        result["repository_size_kb"] = size_kb
        result["repository_size_bytes_approx"] = size_kb * 1024
        result["repository_size_human_approx"] = human_bytes(size_kb * 1024)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
        result["repository_metadata_error"] = type(exc).__name__

    artifacts: list[dict[str, Any]] = []
    artifact_total_count: int | None = None
    artifact_pages = 0
    try:
        for page in range(1, max_pages + 1):
            payload = _github_get(f"https://api.github.com/repos/{repo}/actions/artifacts?per_page=100&page={page}", token)
            artifact_pages = page
            if artifact_total_count is None:
                artifact_total_count = int(payload.get("total_count") or 0)
            batch = payload.get("artifacts") or []
            for a in batch:
                artifacts.append({
                    "id": a.get("id"), "name": a.get("name"),
                    "size_in_bytes": int(a.get("size_in_bytes") or 0),
                    "expired": bool(a.get("expired")), "created_at": a.get("created_at"),
                    "expires_at": a.get("expires_at"),
                    "workflow_run_id": (a.get("workflow_run") or {}).get("id"),
                })
            if not batch or len(artifacts) >= artifact_total_count or len(batch) < 100:
                break
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
        result["artifact_inventory_error"] = type(exc).__name__

    artifact_bytes = sum(x["size_in_bytes"] for x in artifacts)
    artifact_groups: dict[str, dict[str, int]] = defaultdict(lambda: {"count": 0, "bytes": 0})
    for a in artifacts:
        g = artifact_groups[str(a.get("name") or "[unnamed]")]
        g["count"] += 1
        g["bytes"] += a["size_in_bytes"]
    result["actions_artifacts"] = {
        "api_total_count": artifact_total_count,
        "inventory_count": len(artifacts),
        "pages_scanned": artifact_pages,
        "inventory_complete": artifact_total_count is not None and len(artifacts) >= artifact_total_count,
        "inventory_truncated": artifact_total_count is not None and len(artifacts) < artifact_total_count,
        "total_bytes": artifact_bytes,
        "total_human": human_bytes(artifact_bytes),
        "expired_count": sum(1 for x in artifacts if x["expired"]),
        "expired_bytes": sum(x["size_in_bytes"] for x in artifacts if x["expired"]),
        "oldest_created_at": min((x["created_at"] for x in artifacts if x.get("created_at")), default=None),
        "newest_created_at": max((x["created_at"] for x in artifacts if x.get("created_at")), default=None),
        "top_artifacts": sorted(artifacts, key=lambda x: x["size_in_bytes"], reverse=True)[:100],
        "top_name_groups": [
            {"name": name, "count": data["count"], "bytes": data["bytes"], "human": human_bytes(data["bytes"])}
            for name, data in sorted(artifact_groups.items(), key=lambda kv: kv[1]["bytes"], reverse=True)[:100]
        ],
        "artifacts": artifacts,
    }

    caches: list[dict[str, Any]] = []
    cache_total_count: int | None = None
    cache_pages = 0
    try:
        for page in range(1, max_pages + 1):
            payload = _github_get(f"https://api.github.com/repos/{repo}/actions/caches?per_page=100&page={page}", token)
            cache_pages = page
            if cache_total_count is None:
                cache_total_count = int(payload.get("total_count") or 0)
            batch = payload.get("actions_caches") or []
            for a in batch:
                caches.append({
                    "id": a.get("id"), "key": a.get("key"), "ref": a.get("ref"),
                    "size_in_bytes": int(a.get("size_in_bytes") or 0),
                    "created_at": a.get("created_at"), "last_accessed_at": a.get("last_accessed_at"),
                })
            if not batch or len(caches) >= cache_total_count or len(batch) < 100:
                break
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
        result["cache_inventory_error"] = type(exc).__name__

    cache_bytes = sum(x["size_in_bytes"] for x in caches)
    result["actions_caches"] = {
        "api_total_count": cache_total_count,
        "inventory_count": len(caches),
        "pages_scanned": cache_pages,
        "inventory_complete": cache_total_count is not None and len(caches) >= cache_total_count,
        "inventory_truncated": cache_total_count is not None and len(caches) < cache_total_count,
        "total_bytes": cache_bytes,
        "total_human": human_bytes(cache_bytes),
        "top_caches": sorted(caches, key=lambda x: x["size_in_bytes"], reverse=True)[:100],
        "caches": caches,
    }
    result["actions_known_storage_bytes"] = artifact_bytes + cache_bytes
    result["actions_known_storage_human"] = human_bytes(artifact_bytes + cache_bytes)
    return result


def build_report(root: Path, out_dir: Path, include_actions: bool) -> dict[str, Any]:
    files = git_file_list(root)
    text_files = [f for f in files if is_text_path(f)]
    reverse = python_reverse_imports(root, files)
    hash_map: dict[str, list[str]] = defaultdict(list)
    name_map: dict[str, list[str]] = defaultdict(list)
    inventory, total_bytes = [], 0

    for path in files:
        full = root / path
        symlink = full.is_symlink()
        try:
            if symlink:
                size = len(os.readlink(full).encode("utf-8", errors="replace"))
                digest = "SYMLINK:" + hashlib.sha256(os.readlink(full).encode()).hexdigest()
            else:
                size, digest = full.stat().st_size, sha256_file(full)
        except OSError:
            size, digest = 0, ""
        total_bytes += size
        if digest and not symlink:
            hash_map[digest].append(path)
        name_map[Path(path).name.lower()].append(path)
        protected, protected_reasons = is_protected(path)
        if symlink:
            protected, protected_reasons = True, protected_reasons + ["tracked_symlink"]
        generated, generated_reason = is_generated_noise(path)
        inventory.append({
            "path": path, "bytes": size, "human": human_bytes(size), "sha256": digest,
            "suffix": Path(path).suffix.lower(), "text": is_text_path(path), "source_like": is_source_like(path),
            "symlink": symlink, "protected": protected, "protected_reasons": protected_reasons,
            "generated_noise": generated, "generated_reason": generated_reason,
            "suspicious_parts": suspicious_path(path), "python_importers": len(reverse.get(path, [])),
            "python_importer_sample": reverse.get(path, [])[:20],
        })

    duplicate_groups, duplicate_paths = [], set()
    for digest, group in hash_map.items():
        if digest and len(group) > 1:
            bytes_each = (root / group[0]).stat().st_size
            duplicate_paths.update(group)
            duplicate_groups.append({"sha256": digest, "files": sorted(group), "bytes_each": bytes_each})
    duplicate_groups.sort(key=lambda g: g["bytes_each"] * (len(g["files"]) - 1), reverse=True)
    duplicate_names = [
        {"basename": n, "files": sorted(g)}
        for n, g in name_map.items() if n and len(g) > 1 and n not in {"__init__.py", "readme.md"}
    ]
    duplicate_names.sort(key=lambda x: (-len(x["files"]), x["basename"]))

    for row in inventory:
        if row["protected"]:
            row["initial_disposition"] = "KEEP_REQUIRED_PROTECTED"
        elif row["generated_noise"]:
            row["initial_disposition"] = "DELETE_CANDIDATE_GENERATED"
        elif row["path"] in duplicate_paths:
            row["initial_disposition"] = "REVIEW_EXACT_DUPLICATE"
        elif row["suspicious_parts"]:
            row["initial_disposition"] = "REVIEW_SUSPICIOUS_PATH"
        elif row["bytes"] >= 1024 * 1024:
            row["initial_disposition"] = "REVIEW_LARGE_FILE"
        else:
            row["initial_disposition"] = "KEEP_BASELINE_NOT_A_CLEANUP_CANDIDATE"

    meta = {r["path"]: r for r in inventory}
    family_by_path: dict[str, set[str]] = {}
    for g in duplicate_groups:
        family = set(g["files"])
        for p in family:
            family_by_path[p] = family
    candidates = sorted({
        r["path"] for r in inventory
        if r["generated_noise"] or r["path"] in duplicate_paths or r["suspicious_parts"] or r["bytes"] >= 1024 * 1024
    })
    for path in candidates:
        refs = literal_refs(root, path, text_files, family_by_path.get(path, {path}))
        meta[path].update({
            "ref_count": refs["count"], "critical_ref_count": refs["critical_count"],
            "reference_sample": refs["refs"], "critical_reference_sample": refs["critical_refs"],
            "last_change": last_change(root, path),
        })

    keep_by_hash: dict[str, str] = {}
    for g in duplicate_groups:
        keep = sorted(g["files"], key=lambda p: authority_score(p, meta[p]), reverse=True)[0]
        keep_by_hash[g["sha256"]] = keep
        g["keep_candidate"] = keep
        g["reclaimable_duplicate_bytes"] = g["bytes_each"] * (len(g["files"]) - 1)

    decisions = []
    for path in candidates:
        m = meta[path]
        protected, protected_reasons = is_protected(path)
        generated, generated_reason = is_generated_noise(path)
        refs = int(m.get("ref_count", 0))
        critical_refs = int(m.get("critical_ref_count", 0))
        importers = int(m.get("python_importers", 0))
        family = family_by_path.get(path, {path})
        replacement = keep_by_hash.get(m["sha256"]) if len(family) > 1 else None
        if replacement == path:
            replacement = None
        reasons, blockers = [], []
        if generated and generated_reason:
            reasons.append(generated_reason)
        if path in duplicate_paths:
            reasons.append("duplicate_content")
        if suspicious_path(path):
            reasons.append("suspicious_archive_backup_path")
        if refs:
            blockers.append(f"literal_refs={refs}")
        if critical_refs:
            blockers.append(f"critical_refs={critical_refs}")
        if importers:
            blockers.append(f"python_importers={importers}")
        blockers.extend(protected_reasons)
        decision, confidence = "KEEP_REQUIRED", 100 if protected else 60

        if generated and not protected and refs == 0 and importers == 0:
            decision, confidence = "DELETE_PROVEN_100", 100
        elif m["bytes"] == 0 and path in duplicate_paths:
            decision, confidence = "REVIEW_ZERO_BYTE_MARKER", 20
            blockers.append("zero_byte_files_can_be_semantic_markers")
            replacement = None
        elif replacement and not protected and refs == 0 and importers == 0:
            if is_source_like(path):
                decision, confidence = "QUARANTINE_FIRST_SOURCE_DUPLICATE", 95
                blockers.append("source_like_requires_cleanup_PR_CI_before_delete")
            elif (
                suspicious_path(path)
                and not suspicious_path(replacement)
                and Path(path).name == Path(replacement).name
                and m["bytes"] > 0
            ):
                decision, confidence = "DELETE_PROVEN_100", 100
            else:
                decision, confidence = "QUARANTINE_FIRST_EXACT_DUPLICATE", 90
                blockers.append("exact_duplicate_but_authority_path_not_strong_enough_for_direct_delete")
        elif suspicious_path(path) and not protected and refs == 0 and importers == 0:
            decision, confidence = "QUARANTINE_FIRST_UNREFERENCED", 85
            blockers.append("no_byte_identical_authoritative_replacement")
        elif m["bytes"] >= 1024 * 1024 and not protected:
            decision, confidence = "REVIEW_LARGE_FILE", 50
            blockers.append("large_file_requires_authority_review")

        decisions.append({
            "path": path, "decision": decision, "confidence": confidence,
            "bytes": m["bytes"], "human": m["human"], "reasons": reasons,
            "replacement": replacement, "sha256": m["sha256"], "ref_count": refs,
            "critical_ref_count": critical_refs, "python_importers": importers,
            "blockers": sorted(set(blockers)), "last_change": m.get("last_change"),
            "reference_sample": m.get("reference_sample", []),
            "python_importer_sample": m.get("python_importer_sample", []),
        })

    proven = [x for x in decisions if x["decision"] == "DELETE_PROVEN_100"]
    quarantine = [x for x in decisions if x["decision"].startswith("QUARANTINE_FIRST")]
    large = sorted(inventory, key=lambda x: x["bytes"], reverse=True)[:200]
    untracked = disk_inventory(root, git_file_list(root, ignored=False))
    ignored = disk_inventory(root, git_file_list(root, ignored=True))
    storage = git_storage(root)
    github_storage = github_storage_inventory() if include_actions else {"available": False, "reason": "not requested"}
    _, head, _ = git(root, "rev-parse", "HEAD")
    _, branch, _ = git(root, "branch", "--show-current")
    _, dirty, _ = git(root, "status", "--porcelain")

    summary = {
        "schema": SCHEMA_VERSION, "generated_at_utc": utc_now(), "repo_root": str(root),
        "head_sha": head.strip(), "branch": branch.strip(),
        "working_tree_dirty_entries": len(dirty.splitlines()),
        "tracked_file_count": len(files), "tracked_bytes": total_bytes, "tracked_human": human_bytes(total_bytes),
        "untracked_file_count": untracked["count"], "untracked_bytes": untracked["bytes"], "untracked_human": untracked["human"],
        "ignored_file_count": ignored["count"], "ignored_bytes": ignored["bytes"], "ignored_human": ignored["human"],
        "text_file_count": len(text_files), "python_import_graph_target_count": len(reverse),
        "duplicate_content_group_count": len(duplicate_groups),
        "duplicate_content_reclaimable_bytes": sum(g["reclaimable_duplicate_bytes"] for g in duplicate_groups),
        "decision_counts": dict(Counter(x["decision"] for x in decisions)),
        "delete_proven_count": len(proven), "delete_proven_bytes": sum(x["bytes"] for x in proven),
        "delete_proven_human": human_bytes(sum(x["bytes"] for x in proven)),
        "quarantine_first_count": len(quarantine), "quarantine_first_bytes": sum(x["bytes"] for x in quarantine),
        "quarantine_first_human": human_bytes(sum(x["bytes"] for x in quarantine)),
        "git_history_complete": storage["history_complete"], "git_history_scope": storage["history_scope"],
        "github_storage_inventory_available": bool(github_storage.get("available")),
        "no_files_deleted": True,
        "confidence_contract": {
            "DELETE_PROVEN_100": "Known generated noise with zero refs/importers/protected signals, or a non-empty byte-identical non-source duplicate in a stale/archive path with same basename, zero refs/importers, and a non-stale authoritative replacement.",
            "QUARANTINE_FIRST_SOURCE_DUPLICATE": "Byte-identical source duplicate with zero detected refs/importers; still requires cleanup PR + normal CI.",
            "QUARANTINE_FIRST_EXACT_DUPLICATE": "Byte-identical non-source duplicate, but authority/path proof is not strong enough for direct deletion.",
            "QUARANTINE_FIRST_UNREFERENCED": "Looks stale/unreferenced but lacks an identical authoritative replacement.",
            "REVIEW_ZERO_BYTE_MARKER": "Zero-byte files are never delete-proven by duplicate hash because empty marker files can be semantically meaningful.",
            "KEEP_REQUIRED": "Protected/runtime-sensitive or referenced.",
        },
    }

    outputs = {
        "01_summary.json": summary, "02_file_inventory.json": inventory,
        "03_delete_proven_100.json": sorted(proven, key=lambda x: x["bytes"], reverse=True),
        "04_quarantine_first.json": sorted(quarantine, key=lambda x: x["bytes"], reverse=True),
        "05_all_candidate_decisions.json": sorted(decisions, key=lambda x: (-x["bytes"], x["path"])),
        "06_duplicate_content_groups.json": duplicate_groups,
        "06b_duplicate_basename_groups_review_only.json": duplicate_names,
        "07_large_current_files.json": large, "08_python_reverse_import_graph.json": reverse,
        "09_git_storage_and_largest_history_blobs.json": storage,
        "10_github_storage_actions_artifacts_caches.json": github_storage,
        "11_local_untracked_disk_inventory.json": untracked,
        "12_local_ignored_disk_inventory.json": ignored,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in outputs.items():
        write_json(out_dir / name, payload)
    write_text(
        out_dir / "DELETE_PROVEN_100_COMMANDS.txt",
        "\n".join(f"git rm -- {json.dumps(x['path'])}" for x in proven) + ("\n" if proven else ""),
    )
    write_text(
        out_dir / "KEEP_REQUIRED_PATHS.txt",
        "\n".join(sorted(x["path"] for x in decisions if x["decision"] == "KEEP_REQUIRED")) + "\n",
    )

    artifacts = github_storage.get("actions_artifacts", {}) if github_storage.get("available") else {}
    caches = github_storage.get("actions_caches", {}) if github_storage.get("available") else {}
    md = [
        "# Genesis System3 Repo Clean Forensic — Executive Delete Decision", "",
        f"- Schema: `{SCHEMA_VERSION}`", f"- Generated UTC: `{summary['generated_at_utc']}`",
        f"- HEAD: `{summary['head_sha']}`", f"- Tracked files scanned: **{len(files)}**",
        f"- Current tracked size: **{human_bytes(total_bytes)}**",
        f"- `DELETE_PROVEN_100`: **{len(proven)} files / {summary['delete_proven_human']}**",
        f"- Quarantine-first: **{len(quarantine)} files / {summary['quarantine_first_human']}**",
        f"- Exact duplicate groups: **{len(duplicate_groups)}**; theoretical duplicate bytes: **{human_bytes(summary['duplicate_content_reclaimable_bytes'])}**",
        f"- Git-history evidence: **{storage['history_scope']}**",
        "- Files deleted by toolkit: **0**", "", "## Immediate deletion contract", "",
        "`DELETE_PROVEN_100` is intentionally narrow. Empty-file hash matches never qualify. Source/runtime deletion still goes through a cleanup PR and normal CI.",
        "", "## DELETE_PROVEN_100", "", "| Path | Size | Reason | Identical replacement |", "|---|---:|---|---|",
    ]
    for x in sorted(proven, key=lambda r: r["bytes"], reverse=True)[:30]:
        md.append(f"| `{x['path']}` | {x['human']} | {', '.join(x['reasons']) or 'policy proof'} | `{x['replacement'] or ''}` |")
    if not proven:
        md.append("| _None_ | 0 B | No file met every deletion gate | |")
    md += ["", "## Quarantine-first — do not delete yet", "", "| Path | Size | Confidence | Blocker |", "|---|---:|---:|---|"]
    for x in sorted(quarantine, key=lambda r: r["bytes"], reverse=True)[:30]:
        md.append(f"| `{x['path']}` | {x['human']} | {x['confidence']} | {', '.join(x['blockers'])} |")
    if not quarantine:
        md.append("| _None_ | 0 B | - | - |")
    md += [
        "", "## Storage layers", "",
        f"- Current tracked worktree: **{human_bytes(total_bytes)}**",
        f"- Local untracked: **{untracked['count']} files / {untracked['human']}**",
        f"- Local ignored/generated: **{ignored['count']} files / {ignored['human']}**",
    ]
    counts = storage.get("count_objects", {})
    if counts:
        md += [f"- Git object database size-pack: **{counts.get('size-pack', 'unknown')}**", f"- Git loose object size: **{counts.get('size', 'unknown')}**"]
    if github_storage.get("available"):
        md += [
            f"- GitHub repository reported size: **{github_storage.get('repository_size_human_approx', 'unknown')}**",
            f"- Actions artifacts: **{artifacts.get('inventory_count', 0)} inventoried / API total {artifacts.get('api_total_count')} / {artifacts.get('total_human', '0 B')}**",
            f"- Actions artifact inventory complete: **{artifacts.get('inventory_complete')}**",
            f"- Actions caches: **{caches.get('inventory_count', 0)} inventoried / API total {caches.get('api_total_count')} / {caches.get('total_human', '0 B')}**",
            f"- Known Actions artifact+cache storage: **{github_storage.get('actions_known_storage_human', '0 B')}**",
        ]
    else:
        md.append(f"- GitHub storage inventory: `{github_storage.get('reason', 'unavailable')}`")
    md += [
        "", "## Evidence rules", "",
        "- Every current tracked file is size/hash/disposition inventoried.",
        "- Exact duplicates use SHA-256; basename similarity never proves deletion.",
        "- Zero-byte duplicates never become delete-proven solely because all empty files hash the same.",
        "- Python reverse imports and literal path/basename references are checked.",
        "- Workflow/Docker/package references, symlinks, and runtime/governance paths fail closed.",
        "- Current files, Git history, Actions artifacts/caches, and local ignored/untracked disk are separate storage layers.",
        "- PR runs scan all current tracked files; full Git-history conclusions require a non-shallow main/manual run.",
        "- No broker call, secret read, LIVE/order action, IAM change, file deletion, artifact deletion, or history rewrite occurs.",
        "", "## Next action", "",
        "Only fresh `03_delete_proven_100.json` rows may seed a cleanup PR. Never directly delete quarantine/review rows.",
    ]
    write_text(out_dir / "00_EXECUTIVE_DELETE_DECISION.md", "\n".join(md) + "\n")
    return summary


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", default=".")
    p.add_argument("--out", default="reports/local/repo_clean_forensic")
    p.add_argument("--github-artifacts", action="store_true")
    args = p.parse_args(argv or sys.argv[1:])
    root = repo_root(Path(args.repo).resolve())
    out = Path(args.out)
    out = out if out.is_absolute() else root / out
    summary = build_report(root, out, args.github_artifacts)
    print(json.dumps({
        "schema": summary["schema"], "head_sha": summary["head_sha"],
        "tracked_file_count": summary["tracked_file_count"], "tracked_human": summary["tracked_human"],
        "delete_proven_count": summary["delete_proven_count"], "delete_proven_human": summary["delete_proven_human"],
        "quarantine_first_count": summary["quarantine_first_count"],
        "git_history_scope": summary["git_history_scope"],
        "report": str(out / "00_EXECUTIVE_DELETE_DECISION.md"), "files_deleted": 0,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
