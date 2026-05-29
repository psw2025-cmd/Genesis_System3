#!/usr/bin/env python3
import ast
import collections
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
REPORT_DIR = ROOT / "reports" / "authority_inventory"
REPORT_JSON = REPORT_DIR / "root_runtime_authority_inventory.json"
REPORT_MD = REPORT_DIR / "ROOT_RUNTIME_AUTHORITY_INVENTORY.md"

EXCLUDE_PREFIXES = (
    ".git/",
    ".venv/",
    "venv/",
    "node_modules/",
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
    "reports/authority_inventory/",
)

CRITICAL_WORDS = (
    "angel", "binance", "broker", "order", "trade", "trader", "strategy",
    "live", "paper", "analyzer", "orchestrator", "websocket", "dashboard",
    "docker", "deploy", "workflow", "secret", "credential", "token", "env",
)

def git(*args, check=True):
    p = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    if check and p.returncode != 0:
        raise RuntimeError(p.stderr.strip())
    return p.stdout

def sha256_file(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def classify(path: str):
    p = path.lower()
    if p.startswith(".github/workflows/") or p.endswith((".yml", ".yaml")) and "workflow" in p:
        return "ci"
    if "/test" in p or p.startswith("test") or "/tests/" in p or p.endswith("_test.py") or p.endswith(".spec.js"):
        return "test"
    if p.endswith((".md", ".rst", ".txt", ".adoc")) or p.startswith("docs/"):
        return "doc"
    if p.endswith((".json", ".toml", ".ini", ".cfg", ".yml", ".yaml")) or "dockerfile" in p or "compose" in p:
        return "config"
    return "production"

def criticality(path: str):
    p = path.lower()
    hits = [w for w in CRITICAL_WORDS if w in p]
    if any(w in p for w in ("angel", "binance", "broker", "order", "trade", "trader", "strategy", "live")):
        return "critical_trading", hits
    if any(w in p for w in ("docker", "deploy", "workflow")):
        return "critical_devops", hits
    if hits:
        return "sensitive", hits
    return "normal", hits

def git_grep(pattern: str, fixed=True):
    cmd = ["grep", "-n", "--no-color"]
    if fixed:
        cmd.append("-F")
    else:
        cmd.append("-E")
    cmd.append(pattern)
    out = git(*cmd, check=False)
    return [x for x in out.splitlines() if x.strip()]

def python_import_names(path: str):
    f = ROOT / path
    if not f.exists() or f.suffix != ".py":
        return []
    try:
        tree = ast.parse(f.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return []
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                names.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "import_module":
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    names.add(node.args[0].value.split(".")[0])
            if isinstance(node.func, ast.Name) and node.func.id == "__import__":
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    names.add(node.args[0].value.split(".")[0])
    return sorted(names)

def ref_bucket(ref_line: str):
    file_part = ref_line.split(":", 1)[0]
    c = classify(file_part)
    if c == "ci":
        return "ci_refs"
    if c == "test":
        return "test_refs"
    if c == "doc":
        return "doc_refs"
    if c == "config":
        return "config_refs"
    return "code_refs"

def collect_refs(path: str):
    base = Path(path).name
    stem = Path(path).stem
    refs = {
        "code_refs": [],
        "test_refs": [],
        "doc_refs": [],
        "config_refs": [],
        "ci_refs": [],
        "docker_refs": [],
        "import_refs": [],
        "dynamic_import_refs": [],
    }

    candidates = set()
    for pattern, fixed in [(base, True), (stem, True)]:
        for line in git_grep(pattern, fixed=fixed):
            if not line.startswith(path + ":"):
                candidates.add(line)

    if path.endswith(".py"):
        mod = stem.replace("-", "_")
        for pattern in [f"import {mod}", f"from {mod}", f'importlib.import_module("{mod}', f"__import__('{mod}"]:
            for line in git_grep(pattern, fixed=True):
                if not line.startswith(path + ":"):
                    candidates.add(line)

    for line in sorted(candidates):
        upper = line.upper()
        if "COPY " in upper or "ADD " in upper:
            refs["docker_refs"].append(line)
        elif "IMPORT" in upper or "FROM " in upper:
            refs["import_refs"].append(line)
        elif "IMPORT_MODULE" in upper or "__IMPORT__" in upper:
            refs["dynamic_import_refs"].append(line)
        else:
            refs[ref_bucket(line)].append(line)

    for k in refs:
        refs[k] = refs[k][:25]
    return refs

def git_history(path: str):
    out = git("log", "--format=%H|%aI|%an", "--", path, check=False).splitlines()
    if not out:
        return {"commits": 0, "last_commit": None, "last_author": None}
    head = out[0].split("|", 2)
    return {"commits": len(out), "last_commit": head[1] if len(head) > 1 else None, "last_author": head[2] if len(head) > 2 else None}

def authority_score(path: str, refs: dict, hist: dict):
    cls = classify(path)
    score = 0
    if cls == "production": score += 120
    if cls == "config": score += 70
    if cls == "ci": score += 50
    if cls == "test": score += 20
    if cls == "doc": score += 5

    crit, _ = criticality(path)
    if crit == "critical_trading": score += 100
    elif crit == "critical_devops": score += 60
    elif crit == "sensitive": score += 25

    score += len(refs.get("code_refs", [])) * 8
    score += len(refs.get("import_refs", [])) * 10
    score += len(refs.get("dynamic_import_refs", [])) * 15
    score += len(refs.get("docker_refs", [])) * 12
    score += len(refs.get("ci_refs", [])) * 8
    score += min(hist.get("commits", 0), 30)
    score += max(0, 20 - path.count("/") * 2)
    return score

def quarantine_recommendation(path: str, refs: dict):
    crit, hits = criticality(path)
    ref_count = sum(len(v) for v in refs.values())
    if crit in ("critical_trading", "critical_devops"):
        return "DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW", ref_count, hits
    if ref_count == 0:
        return "QUARANTINE_CANDIDATE_BATCH_1", ref_count, hits
    if ref_count <= 2:
        return "REVIEW_BEFORE_QUARANTINE", ref_count, hits
    return "KEEP_OR_REVIEW_LATER", ref_count, hits

tracked = []
for f in git("ls-files").splitlines():
    if not f or f.startswith(EXCLUDE_PREFIXES):
        continue
    p = ROOT / f
    if p.is_file():
        tracked.append(f)

hash_map = collections.defaultdict(list)
name_map = collections.defaultdict(list)
meta = {}

for f in tracked:
    p = ROOT / f
    sha = sha256_file(p)
    hist = git_history(f)
    refs = collect_refs(f)
    qrec, ref_count, crit_hits = quarantine_recommendation(f, refs)
    meta[f] = {
        "file": f,
        "sha256": sha,
        "size_bytes": p.stat().st_size,
        "class": classify(f),
        "criticality": criticality(f)[0],
        "critical_hits": crit_hits,
        "history": hist,
        "refs": refs,
        "ref_count": ref_count,
        "authority_score": authority_score(f, refs, hist),
        "quarantine_recommendation": qrec,
    }
    hash_map[sha].append(f)
    name_map[p.name].append(f)

duplicate_hash_groups = []
for sha, files in hash_map.items():
    if len(files) > 1:
        ranked = sorted(files, key=lambda x: meta[x]["authority_score"], reverse=True)
        duplicate_hash_groups.append({
            "sha256": sha,
            "authoritative_keep_candidate": ranked[0],
            "files": ranked,
            "members": [meta[x] for x in ranked],
        })

duplicate_name_groups = []
for name, files in name_map.items():
    if len(files) > 1:
        ranked = sorted(files, key=lambda x: meta[x]["authority_score"], reverse=True)
        duplicate_name_groups.append({
            "basename": name,
            "authoritative_keep_candidate": ranked[0],
            "files": ranked,
            "members": [meta[x] for x in ranked],
        })

backend_exists = (ROOT / "backend").is_dir()
backend_dockerfile_exists = (ROOT / "backend" / "Dockerfile").is_file()
dockerignore_exists = (ROOT / ".dockerignore").is_file()
deploy_backend_exists = (ROOT / ".github" / "workflows" / "deploy-backend.yml").is_file()

all_duplicate_files = sorted(set(
    [f for g in duplicate_hash_groups for f in g["files"]] +
    [f for g in duplicate_name_groups for f in g["files"]]
))

report = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "repo": ROOT.name,
    "policy": {
        "mode": "REPORT_ONLY",
        "deleted_files": 0,
        "moved_files": 0,
        "quarantine_performed": False,
        "safe_next_step": "Review this PR, then create a separate quarantine PR only for approved batch-1 candidates.",
    },
    "root_probe": {
        "repo_root": str(ROOT),
        "backend_dir_exists": backend_exists,
        "backend_dockerfile_exists": backend_dockerfile_exists,
        "dockerignore_exists": dockerignore_exists,
        "deploy_backend_workflow_exists": deploy_backend_exists,
    },
    "summary": {
        "tracked_files_scanned": len(tracked),
        "duplicate_content_groups": len(duplicate_hash_groups),
        "duplicate_name_groups": len(duplicate_name_groups),
        "unique_duplicate_files": len(all_duplicate_files),
        "batch1_quarantine_candidates": sum(1 for f in all_duplicate_files if meta[f]["quarantine_recommendation"] == "QUARANTINE_CANDIDATE_BATCH_1"),
        "manual_review_required": sum(1 for f in all_duplicate_files if meta[f]["quarantine_recommendation"] == "DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW"),
    },
    "duplicate_content_groups": duplicate_hash_groups,
    "duplicate_name_groups": duplicate_name_groups,
    "duplicate_file_index": [meta[f] for f in all_duplicate_files],
}

REPORT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

md = []
s = report["summary"]
rp = report["root_probe"]
md.append("# Root Runtime Authority Inventory — Report Only")
md.append("")
md.append(f"Generated: `{report['generated_at']}`")
md.append("")
md.append("## Safety policy")
md.append("- No files deleted.")
md.append("- No files moved.")
md.append("- No quarantine performed.")
md.append("- This PR is discovery/report only.")
md.append("")
md.append("## Root / Docker / Backend probe")
md.append("| Probe | Result |")
md.append("|---|---|")
for k, v in rp.items():
    md.append(f"| `{k}` | `{v}` |")
md.append("")
md.append("## Summary")
md.append("| Metric | Count |")
md.append("|---|---:|")
for k, v in s.items():
    md.append(f"| `{k}` | {v} |")
md.append("")
md.append("## Duplicate content groups")
if not duplicate_hash_groups:
    md.append("No identical-content duplicate groups found.")
else:
    for i, g in enumerate(duplicate_hash_groups[:50], 1):
        md.append(f"### Group {i}: `{g['sha256'][:16]}...`")
        md.append(f"- Keep candidate: `{g['authoritative_keep_candidate']}`")
        for f in g["files"]:
            m = meta[f]
            md.append(f"  - `{f}` — class=`{m['class']}`, criticality=`{m['criticality']}`, refs={m['ref_count']}, action=`{m['quarantine_recommendation']}`")
        md.append("")
md.append("## Duplicate filename groups")
if not duplicate_name_groups:
    md.append("No same-basename duplicate groups found.")
else:
    for i, g in enumerate(duplicate_name_groups[:50], 1):
        md.append(f"### `{g['basename']}`")
        md.append(f"- Keep candidate: `{g['authoritative_keep_candidate']}`")
        for f in g["files"]:
            m = meta[f]
            md.append(f"  - `{f}` — class=`{m['class']}`, criticality=`{m['criticality']}`, refs={m['ref_count']}, action=`{m['quarantine_recommendation']}`")
        md.append("")
md.append("## Next safe action after this PR")
md.append("Create a separate quarantine PR only for `QUARANTINE_CANDIDATE_BATCH_1` files after human review.")
md.append("")
REPORT_MD.write_text("\n".join(md), encoding="utf-8")

print("=== ROOT PROBE ===")
print(json.dumps(report["root_probe"], indent=2))
print("=== SUMMARY ===")
print(json.dumps(report["summary"], indent=2))
print(f"JSON: {REPORT_JSON}")
print(f"MD:   {REPORT_MD}")
