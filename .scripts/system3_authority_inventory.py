#!/usr/bin/env python3
import collections
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
REPORT_DIR = ROOT / "reports" / "authority_inventory"
REPORT_JSON = REPORT_DIR / "root_runtime_authority_inventory.json"
REPORT_MD = REPORT_DIR / "ROOT_RUNTIME_AUTHORITY_INVENTORY.md"

EXCLUDE_SUFFIXES = (".ini", ".pyc", ".pyo", ".log", ".tmp", ".cache")
EXCLUDE_PARTS = (
    "/__pycache__/", "/.pytest_cache/", "/.mypy_cache/",
    "/node_modules/", "/.git/", "/reports/authority_inventory/",
    "/dashboard/frontend/dist/", "/dashboard/backend/logs/",
)

CRITICAL_WORDS = ("angel","binance","broker","order","trade","trader","strategy","live","paper","analyzer","orchestrator","websocket","dashboard","docker","deploy","workflow","secret","credential","token","env")

def git(*args, check=True):
    p = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    if check and p.returncode != 0:
        raise RuntimeError(p.stderr.strip())
    return p.stdout

def sha256_file(p: Path):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def skip(path: str):
    low = "/" + path.lower()
    return path.lower().endswith(EXCLUDE_SUFFIXES) or any(x in low for x in EXCLUDE_PARTS)

def criticality(path: str):
    p = path.lower()
    hits = [w for w in CRITICAL_WORDS if w in p]
    if any(w in p for w in ("angel","binance","broker","order","trade","trader","strategy","live")):
        return "critical_trading", hits
    if any(w in p for w in ("docker","deploy","workflow")):
        return "critical_devops", hits
    if hits:
        return "sensitive", hits
    return "normal", hits

def grep_refs(name: str, self_path: str):
    out = git("grep", "-n", "--no-color", "-F", name, check=False)
    refs = []
    for line in out.splitlines():
        if not line.startswith(self_path + ":"):
            refs.append(line[:220])
    return refs[:20]

tracked = []
for f in git("ls-files").splitlines():
    p = ROOT / f
    if f and p.is_file() and not skip(f):
        tracked.append(f)

hash_map = collections.defaultdict(list)
name_map = collections.defaultdict(list)
meta = {}

for f in tracked:
    p = ROOT / f
    sha = sha256_file(p)
    refs = grep_refs(Path(f).name, f)
    crit, hits = criticality(f)
    meta[f] = {
        "file": f,
        "sha256": sha,
        "size_bytes": p.stat().st_size,
        "criticality": crit,
        "critical_hits": hits,
        "ref_count": len(refs),
        "sample_refs": refs[:5],
        "recommendation": "MANUAL_REVIEW_REQUIRED" if crit != "normal" else ("BATCH1_QUARANTINE_CANDIDATE" if len(refs) == 0 else "KEEP_OR_REVIEW_LATER"),
    }
    hash_map[sha].append(f)
    name_map[p.name].append(f)

dup_content = []
for sha, files in hash_map.items():
    if len(files) > 1:
        ranked = sorted(files, key=lambda x: (meta[x]["criticality"] != "normal", meta[x]["ref_count"], -x.count("/")), reverse=True)
        dup_content.append({"sha256": sha, "keep_candidate": ranked[0], "files": ranked[:30]})

dup_names = []
for name, files in name_map.items():
    if len(files) > 1:
        ranked = sorted(files, key=lambda x: (meta[x]["criticality"] != "normal", meta[x]["ref_count"], -x.count("/")), reverse=True)
        dup_names.append({"basename": name, "keep_candidate": ranked[0], "files": ranked[:30]})

all_dups = sorted(set([f for g in dup_content for f in g["files"]] + [f for g in dup_names for f in g["files"]]))
index = [meta[f] for f in all_dups[:300]]

root_probe = {
    "repo_root": str(ROOT),
    "backend_dir_exists": (ROOT / "backend").is_dir(),
    "backend_dockerfile_exists": (ROOT / "backend" / "Dockerfile").is_file(),
    "dockerignore_exists": (ROOT / ".dockerignore").is_file(),
    "deploy_backend_workflow_exists": (ROOT / ".github" / "workflows" / "deploy-backend.yml").is_file(),
    "dashboard_backend_dir_exists": (ROOT / "dashboard" / "backend").is_dir(),
    "dashboard_backend_dockerfile_exists": (ROOT / "dashboard" / "backend" / "Dockerfile").is_file(),
}

summary = {
    "tracked_files_scanned_after_noise_filter": len(tracked),
    "excluded_noise_rule": "desktop.ini/log/cache/dist/report-authority paths excluded",
    "duplicate_content_groups": len(dup_content),
    "duplicate_name_groups": len(dup_names),
    "unique_duplicate_files_limited_index": len(index),
    "batch1_candidates": sum(1 for x in index if x["recommendation"] == "BATCH1_QUARANTINE_CANDIDATE"),
    "manual_review_required": sum(1 for x in index if x["recommendation"] == "MANUAL_REVIEW_REQUIRED"),
}

report = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "REPORT_ONLY_NO_DELETE_NO_MOVE",
    "root_probe": root_probe,
    "summary": summary,
    "duplicate_content_groups": dup_content[:50],
    "duplicate_name_groups": dup_names[:50],
    "duplicate_file_index_limited": index,
}

REPORT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

md = [
"# Root Runtime Authority Inventory — Compact Report Only",
"",
f"Generated: `{report['generated_at']}`",
"",
"## Safety",
"- No files deleted.",
"- No files moved.",
"- No quarantine performed.",
"- Noise excluded: `desktop.ini`, logs, cache, dist, previous authority reports.",
"",
"## Root / Docker / Backend Probe",
"| Probe | Result |",
"|---|---|",
]
for k,v in root_probe.items():
    md.append(f"| `{k}` | `{v}` |")
md += ["", "## Summary", "| Metric | Count |", "|---|---:|"]
for k,v in summary.items():
    md.append(f"| `{k}` | `{v}` |")
md += ["", "## Top duplicate content groups"]
for i,g in enumerate(dup_content[:20],1):
    md.append(f"### Group {i}")
    md.append(f"- Keep candidate: `{g['keep_candidate']}`")
    for f in g["files"][:10]:
        md.append(f"  - `{f}` — refs={meta[f]['ref_count']}, criticality={meta[f]['criticality']}, recommendation={meta[f]['recommendation']}")
md += ["", "## Top duplicate filename groups"]
for i,g in enumerate(dup_names[:20],1):
    md.append(f"### `{g['basename']}`")
    md.append(f"- Keep candidate: `{g['keep_candidate']}`")
    for f in g["files"][:10]:
        md.append(f"  - `{f}` — refs={meta[f]['ref_count']}, criticality={meta[f]['criticality']}, recommendation={meta[f]['recommendation']}")
REPORT_MD.write_text("\n".join(md), encoding="utf-8")

print("=== ROOT PROBE ===")
print(json.dumps(root_probe, indent=2))
print("=== SUMMARY ===")
print(json.dumps(summary, indent=2))
