#!/usr/bin/env python3
"""
System3 Markdown Inventory and Documentation Contradiction Verifier.

Read-only by design:
- does not modify runtime files
- does not touch .env/secrets/broker credentials
- only writes reports under reports/latest/

Outputs:
- reports/latest/markdown_inventory.json
- reports/latest/markdown_inventory.md
- reports/latest/documentation_contradictions.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

RISK_TERMS = [
    "FINAL",
    "COMPLETE",
    "PASS",
    "READY",
    "CERTIFIED",
    "LIVE_READY",
    "TRADE_READY",
    "8/8",
    "FULLPASS",
    "SUCCESS",
]

STRONG_READY_TERMS = [
    "LIVE_READY",
    "TRADE_READY",
    "CERTIFIED",
    "8/8",
]

REQUIRED_ACTIVE_DOCS = [
    "SYSTEM3_MASTER_TRACKER.md",
    "SYSTEM3_BLOCKER_REGISTER.md",
    "docs/control_plane/SYSTEM3_CURRENT_RUNTIME_TRUTH.md",
    "docs/control_plane/SYSTEM3_SIGNAL_TO_TRADE_CONTROL.md",
    "docs/control_plane/SYSTEM3_MODEL_ACCURACY_REGISTER.md",
    "docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md",
    "docs/control_plane/SYSTEM3_DOCUMENTATION_CONTROL_PLANE.md",
    "docs/SYSTEM3_CORE_TRADING_GOAL_AND_ARCHITECTURE.md",
    "docs/SYSTEM3_SINGLE_ASSISTANT_RESPONSIBILITY_RULE.md",
    "docs/runtime/AUTHORITATIVE_RUNTIME_AND_DATA_MAP.md",
]

REFERENCE_DOCS = {
    "docs/architecture/MASTER_PR_ROADMAP.md",
    "docs/architecture/SYSTEM3_BRUTAL_GAP_ANALYSIS.md",
}

CURRENT_BLOCKER_IDS = [
    "SYS3-BLK-001",
    "SYS3-BLK-002",
    "SYS3-BLK-003",
    "SYS3-BLK-004",
    "SYS3-BLK-005",
    "SYS3-BLK-006",
    "SYS3-BLK-007",
    "SYS3-BLK-008",
    "SYS3-BLK-009",
    "SYS3-BLK-010",
]


@dataclass
class MarkdownEntry:
    path: str
    title: str
    doc_class: str
    size_bytes: int
    sha256: str
    risk_terms: List[str]
    strong_ready_terms: List[str]
    duplicate_key: str
    duplicate_count: int
    duplicate_risk: bool
    current_truth_conflict: bool
    recommended_action: str


def rel_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def iter_markdown_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.md"):
        parts = set(path.relative_to(root).parts)
        if parts & EXCLUDED_DIRS:
            continue
        if path.is_file():
            yield path


def safe_read(path: Path, limit: int = 250_000) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        try:
            data = path.read_text(encoding="latin-1", errors="replace")
        except Exception as exc:
            return f"READ_ERROR: {exc}"
    return data[:limit]


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines()[:80]:
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()[:160] or fallback
    return fallback


def find_terms(text: str, path: str, terms: List[str]) -> List[str]:
    hay = f"{path}\n{text}".upper()
    found = []
    for term in terms:
        if term.upper() in hay:
            found.append(term)
    return found


def normalize_duplicate_key(path: str, title: str) -> str:
    stem = Path(path).stem
    source = title if title and title.lower() not in {"read_error"} else stem
    source = source.lower()
    source = re.sub(r"[^a-z0-9]+", " ", source)
    remove_words = {
        "system3",
        "system",
        "phase",
        "phases",
        "final",
        "complete",
        "completion",
        "summary",
        "report",
        "results",
        "result",
        "status",
        "validation",
        "verified",
        "verification",
        "analysis",
        "audit",
        "copy",
        "part",
        "fullpass",
        "success",
    }
    tokens = [t for t in source.split() if t not in remove_words and not t.isdigit()]
    return " ".join(tokens[:8]) or re.sub(r"[^a-z0-9]+", " ", stem.lower()).strip()


def classify_doc(path: str, title: str, text: str, risk_terms: List[str], duplicate_risk: bool) -> str:
    if path in REQUIRED_ACTIVE_DOCS or path.startswith("docs/control_plane/"):
        return "ACTIVE_CONTROL"
    if path in REFERENCE_DOCS:
        return "REFERENCE"
    lower = path.lower()
    if lower.startswith("reports/") or lower.startswith("runtime_reports/") or lower.startswith("proof/"):
        return "HISTORICAL_REPORT"
    if lower.startswith("state/proposals/"):
        return "HISTORICAL_REPORT"
    if duplicate_risk:
        return "DUPLICATE_RISK"
    if risk_terms:
        return "HISTORICAL_REPORT"
    if lower.startswith("docs/architecture/") or lower.startswith("docs/runtime/"):
        return "REFERENCE"
    if lower.startswith("docs/"):
        return "REFERENCE"
    return "UNKNOWN"


def has_current_open_blockers(root: Path) -> bool:
    blocker_path = root / "SYSTEM3_BLOCKER_REGISTER.md"
    if not blocker_path.exists():
        return True
    text = safe_read(blocker_path).upper()
    return "OPEN" in text and any(b in text for b in CURRENT_BLOCKER_IDS)


def current_truth_conflict(doc_class: str, risk_terms: List[str], strong_terms: List[str], open_blockers: bool) -> bool:
    if doc_class == "ACTIVE_CONTROL":
        return False
    if not open_blockers:
        return False
    if strong_terms:
        return True
    # Treat final/complete/ready/pass docs outside active control as potential contradictions while blockers are open.
    return bool(set(risk_terms) & {"FINAL", "COMPLETE", "PASS", "READY", "FULLPASS", "SUCCESS"})


def recommend_action(doc_class: str, conflict: bool, duplicate_risk: bool) -> str:
    if doc_class == "ACTIVE_CONTROL":
        return "KEEP_ACTIVE_AND_UPDATE_EVERY_RUN"
    if conflict:
        return "REVIEW_AS_CONTRADICTION_DO_NOT_USE_AS_CURRENT_TRUTH"
    if duplicate_risk:
        return "REVIEW_DUPLICATE_ARCHIVE_LATER"
    if doc_class == "HISTORICAL_REPORT":
        return "KEEP_AS_HISTORY_NOT_CURRENT_TRUTH"
    if doc_class == "REFERENCE":
        return "KEEP_AS_REFERENCE"
    return "MANUAL_REVIEW"


def build_inventory(root: Path) -> Tuple[List[MarkdownEntry], Dict[str, object]]:
    raw = []
    for md in sorted(iter_markdown_files(root)):
        path = rel_path(md, root)
        text = safe_read(md)
        title = first_heading(text, Path(path).stem)
        risk_terms = find_terms(text, path, RISK_TERMS)
        strong_terms = find_terms(text, path, STRONG_READY_TERMS)
        dkey = normalize_duplicate_key(path, title)
        raw.append((md, path, text, title, risk_terms, strong_terms, dkey))

    duplicate_counts = Counter(item[-1] for item in raw)
    open_blockers = has_current_open_blockers(root)
    entries: List[MarkdownEntry] = []

    for md, path, text, title, risk_terms, strong_terms, dkey in raw:
        duplicate_count = duplicate_counts[dkey]
        duplicate_risk = duplicate_count > 1 and path not in REQUIRED_ACTIVE_DOCS
        doc_class = classify_doc(path, title, text, risk_terms, duplicate_risk)
        conflict = current_truth_conflict(doc_class, risk_terms, strong_terms, open_blockers)
        entries.append(
            MarkdownEntry(
                path=path,
                title=title,
                doc_class=doc_class,
                size_bytes=md.stat().st_size,
                sha256=file_sha256(md),
                risk_terms=risk_terms,
                strong_ready_terms=strong_terms,
                duplicate_key=dkey,
                duplicate_count=duplicate_count,
                duplicate_risk=duplicate_risk,
                current_truth_conflict=conflict,
                recommended_action=recommend_action(doc_class, conflict, duplicate_risk),
            )
        )

    required_status = {p: (root / p).exists() for p in REQUIRED_ACTIVE_DOCS}
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "total_markdown_files": len(entries),
        "required_active_docs_present": sum(1 for v in required_status.values() if v),
        "required_active_docs_total": len(required_status),
        "missing_required_active_docs": [p for p, exists in required_status.items() if not exists],
        "class_counts": dict(Counter(e.doc_class for e in entries)),
        "risk_term_file_count": sum(1 for e in entries if e.risk_terms),
        "strong_ready_file_count": sum(1 for e in entries if e.strong_ready_terms),
        "duplicate_risk_file_count": sum(1 for e in entries if e.duplicate_risk),
        "contradiction_file_count": sum(1 for e in entries if e.current_truth_conflict),
        "open_blockers_detected": open_blockers,
    }
    return entries, summary


def write_json(path: Path, summary: Dict[str, object], entries: List[MarkdownEntry]) -> None:
    data = {"summary": summary, "entries": [asdict(e) for e in entries]}
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_inventory_md(path: Path, summary: Dict[str, object], entries: List[MarkdownEntry]) -> None:
    lines = []
    lines.append("# System3 Markdown Inventory")
    lines.append("")
    lines.append(f"Generated UTC: `{summary['generated_at_utc']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for key in [
        "total_markdown_files",
        "required_active_docs_present",
        "required_active_docs_total",
        "risk_term_file_count",
        "strong_ready_file_count",
        "duplicate_risk_file_count",
        "contradiction_file_count",
        "open_blockers_detected",
    ]:
        lines.append(f"- **{key}**: `{summary[key]}`")
    lines.append("")
    lines.append("## Class Counts")
    lines.append("")
    for k, v in sorted(summary["class_counts"].items()):
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Missing Required Active Docs")
    lines.append("")
    missing = summary["missing_required_active_docs"]
    if missing:
        for item in missing:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Inventory")
    lines.append("")
    lines.append("| Class | Conflict | Duplicate | Risk Terms | Path | Recommended Action |")
    lines.append("|---|---:|---:|---|---|---|")
    for e in entries:
        terms = ", ".join(e.risk_terms) if e.risk_terms else "-"
        lines.append(
            f"| `{e.doc_class}` | `{e.current_truth_conflict}` | `{e.duplicate_risk}` | `{terms}` | `{e.path}` | `{e.recommended_action}` |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_contradictions_md(path: Path, summary: Dict[str, object], entries: List[MarkdownEntry]) -> None:
    conflicts = [e for e in entries if e.current_truth_conflict]
    strong = [e for e in conflicts if e.strong_ready_terms]
    duplicate = [e for e in entries if e.duplicate_risk]

    lines = []
    lines.append("# System3 Documentation Contradictions")
    lines.append("")
    lines.append(f"Generated UTC: `{summary['generated_at_utc']}`")
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    if conflicts:
        lines.append(
            "FAIL: Some historical/reference markdown files contain final/pass/ready language while current blockers remain open. Do not use those files as current truth."
        )
    else:
        lines.append("PASS: No current markdown contradiction detected by rule scan.")
    lines.append("")
    lines.append("## Current Truth Source")
    lines.append("")
    lines.append("Current truth must come from:")
    lines.append("")
    lines.append("- `SYSTEM3_MASTER_TRACKER.md`")
    lines.append("- `SYSTEM3_BLOCKER_REGISTER.md`")
    lines.append("- `docs/control_plane/SYSTEM3_CURRENT_RUNTIME_TRUTH.md`")
    lines.append("- latest runtime/API proof")
    lines.append("")
    lines.append("## Strong Contradictions")
    lines.append("")
    if strong:
        lines.append("| Strong Terms | Path | Recommended Action |")
        lines.append("|---|---|---|")
        for e in strong:
            lines.append(
                f"| `{', '.join(e.strong_ready_terms)}` | `{e.path}` | `{e.recommended_action}` |"
            )
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## All Contradiction Candidates")
    lines.append("")
    if conflicts:
        lines.append("| Terms | Class | Path | Recommended Action |")
        lines.append("|---|---|---|---|")
        for e in conflicts:
            lines.append(
                f"| `{', '.join(e.risk_terms)}` | `{e.doc_class}` | `{e.path}` | `{e.recommended_action}` |"
            )
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Duplicate Risk Candidates")
    lines.append("")
    if duplicate:
        lines.append("| Duplicate Key | Count | Path |")
        lines.append("|---|---:|---|")
        for e in duplicate:
            lines.append(f"| `{e.duplicate_key}` | `{e.duplicate_count}` | `{e.path}` |")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Required Action")
    lines.append("")
    lines.append("1. Do not delete any markdown file yet.")
    lines.append("2. Treat contradiction candidates as historical evidence only.")
    lines.append("3. Keep active control docs updated after every agent run.")
    lines.append("4. Archive/move old docs only after explicit user approval.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="System3 markdown inventory and contradiction verifier")
    parser.add_argument("--root", default=None, help="Repository root. Defaults to parent of this script directory.")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    root = Path(args.root).resolve() if args.root else script_path.parents[1]
    reports_dir = root / "reports" / "latest"
    reports_dir.mkdir(parents=True, exist_ok=True)

    entries, summary = build_inventory(root)
    write_json(reports_dir / "markdown_inventory.json", summary, entries)
    write_inventory_md(reports_dir / "markdown_inventory.md", summary, entries)
    write_contradictions_md(reports_dir / "documentation_contradictions.md", summary, entries)

    print("SYSTEM3_MARKDOWN_INVENTORY_COMPLETE")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if summary["missing_required_active_docs"]:
        return 2
    # Contradictions are expected during cleanup; do not fail execution because the report itself is the proof.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
