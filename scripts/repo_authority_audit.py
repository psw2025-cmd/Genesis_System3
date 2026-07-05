"""
Repo Authority & Source-of-Truth Audit — GitHub Issue #28
=============================================================
Scans the repo for likely duplicate/conflicting modules around the same
responsibility (e.g. multiple "orchestrator", "scheduler", "gain_rank"
implementations) so that "which file actually runs" stops being
ambiguous. Outputs a single report — does NOT delete or move anything;
this is a read-only audit, safe to run unattended on a schedule.

Heuristic: groups files by a normalized "topic" extracted from filename
(strip phase/numbered prefixes, common suffixes), flags any topic with
more than one matching file across core/, scripts/, tools/ as a
"possible authority conflict" worth a human decision.

Writes: reports/latest/repo_authority/repo_authority_audit.md

Usage:
    python scripts/repo_authority_audit.py
"""

import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT_DIR / "reports" / "latest" / "repo_authority"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SCAN_DIRS = ["core", "scripts", "tools", "src"]
SKIP_DIR_PARTS = {"node_modules", "__pycache__", ".git", "dist", "build", "venv", ".venv"}

# Known authoritative entrypoints (from CHANGE_LOG / docs / render.yaml /
# job scheduler config). Any file matching a conflict topic that is NOT
# one of these is flagged for review, not auto-deleted.
KNOWN_AUTHORITATIVE = {
    "dashboard/backend/app.py",
    "scripts/cloud_worker.py",
    "core/engine/system3_phase82_job_scheduler.py",
    "scripts/daily_gain_rank_and_validate.py",
    "src/ranking/gain_rank_engine.py",
    "src/validation/market_result_validator.py",
    "core/brokers/dhan/token_manager.py",
    "core/brokers/dhan/token_watchdog.py",
    "scripts/paper_lifecycle_proof.py",
}

# Topics that are expected to have many legitimately-separate files
# (test files, per-phase reports) — exclude from conflict detection.
EXCLUDE_TOPIC_SUBSTR = {"test", "_proposal_", "readme"}


def normalize_topic(filename: str) -> str:
    """
    Strip phaseNN/PHnn/v2/_2/_old/_new/_backup decorations to find the
    underlying "topic" a file is about, so phase82_job_scheduler.py and
    job_scheduler.py group under the same topic for conflict detection.
    """
    name = filename.lower()
    name = re.sub(r"\.py$", "", name)
    name = re.sub(r"\.backup$", "", name)
    name = re.sub(r"(^|_)(ph|phase)\d+(_|$)", "_", name)
    name = re.sub(r"(^|_)v\d+(_|$)", "_", name)
    name = re.sub(r"(_old|_new|_backup|_deprecated|_legacy|_v\d+)$", "", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name


def scan_files() -> dict:
    """Returns {normalized_topic: [relative_paths]}."""
    topics = defaultdict(list)
    for scan_dir in SCAN_DIRS:
        base = ROOT_DIR / scan_dir
        if not base.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_PARTS]
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                if fn.startswith("__"):
                    continue
                rel = str((Path(dirpath) / fn).relative_to(ROOT_DIR)).replace("\\", "/")
                topic = normalize_topic(fn)
                if any(s in topic for s in EXCLUDE_TOPIC_SUBSTR):
                    continue
                topics[topic].append(rel)
    return topics


def find_conflicts(topics: dict) -> list:
    """Topics with 2+ files = possible authority ambiguity."""
    conflicts = []
    for topic, paths in sorted(topics.items()):
        if len(paths) < 2:
            continue
        known = [p for p in paths if p in KNOWN_AUTHORITATIVE]
        unknown = [p for p in paths if p not in KNOWN_AUTHORITATIVE]
        conflicts.append({
            "topic": topic,
            "files": sorted(paths),
            "known_authoritative": known,
            "needs_review": unknown if known else paths,
        })
    return conflicts


def write_report(conflicts: list, total_files: int):
    out_path = OUT_DIR / "repo_authority_audit.md"
    lines = [
        "# Repo Authority & Source-of-Truth Audit — Issue #28",
        f"\n_Generated {datetime.now().isoformat()}_\n",
        f"- Python files scanned (core/, scripts/, tools/, src/): **{total_files}**",
        f"- Topics with possible duplicate/conflicting implementations: **{len(conflicts)}**",
        "\nThis is a **read-only** scan — nothing was moved or deleted. "
        "Each row below is a naming-topic where 2+ files exist; a human "
        "(or a follow-up PR) should confirm which file is authoritative "
        "and either delete, archive, or document the rest.\n",
    ]

    if not conflicts:
        lines.append("\nNo naming conflicts detected.")
    else:
        lines.append("\n## Possible Conflicts\n")
        lines.append("| Topic | Files | Has Known-Authoritative? | Needs Review |")
        lines.append("|-------|-------|---------------------------|--------------|")
        for c in conflicts:
            has_known = "✅ yes" if c["known_authoritative"] else "❌ none declared"
            review = ", ".join(c["needs_review"]) if c["needs_review"] else "—"
            files_str = "<br>".join(c["files"])
            lines.append(f"| `{c['topic']}` | {files_str} | {has_known} | {review} |")

    lines.append(
        "\n## Declared Known-Authoritative Entrypoints\n"
        "(Source: render.yaml, config/system3_job_scheduler.json, CHANGE_LOG.md)\n"
    )
    for f in sorted(KNOWN_AUTHORITATIVE):
        exists = "✅" if (ROOT_DIR / f).exists() else "❌ MISSING"
        lines.append(f"- {exists} `{f}`")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def main():
    print("=" * 70)
    print("REPO AUTHORITY & SOURCE-OF-TRUTH AUDIT — Issue #28")
    print("=" * 70)

    topics = scan_files()
    total_files = sum(len(v) for v in topics.values())
    conflicts = find_conflicts(topics)

    print(f"Scanned {total_files} Python files across {SCAN_DIRS}")
    print(f"Found {len(conflicts)} topics with 2+ files (possible conflicts)")

    out_path = write_report(conflicts, total_files)
    print(f"\nReport written to: {out_path}")

    # Print top conflicts to console for quick visibility in scheduler logs
    if conflicts:
        print("\nTop conflicts (first 10):")
        for c in conflicts[:10]:
            print(f"  {c['topic']}: {len(c['files'])} files — {c['files']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
