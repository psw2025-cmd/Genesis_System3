#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SYSTEM3 FULL INSPECTION SCRIPT
 
Place this file in the System3 project root (same level as system3/, storage/, logs/).
Run:  python system3_full_inspector.py
 
This script is READ-ONLY. It does NOT modify any existing files.
It generates a single markdown report:
    SYSTEM3_FULL_INSPECTION_REPORT.md
"""
 
import os
import re
import sys
import json
import csv
import traceback
from datetime import datetime
from pathlib import Path
from textwrap import indent
 
# -----------------------------
# CONFIG: tweak if needed
# -----------------------------
 
# Relative paths for known important files (if they exist)
KEY_FILES = {
    "heartbeat_json": "storage/meta/system3_daily_heartbeat.json",
    "signals_curated_csv": "storage/live/angel_index_ai_signals_curated.csv",
    "signals_forward_csv": "storage/live/angel_index_ai_signals_with_forward.csv",
    "pnl_log_csv": "storage/live/angel_index_ai_pnl_log.csv",
    "autopilot_log_dir": "logs",
    "phase_trace_dir": "logs/live_phase_trace",
}
 
PHASE_FILE_ROOTS = [
    "system3",      # main system code
]
 
# How many lines/rows to peek
CSV_HEAD_ROWS = 5
LOG_TAIL_LINES = 40
JSON_PREVIEW_KEYS = 50  # max keys to show flat
 
 
# -----------------------------
# Helpers
# -----------------------------
 
def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except Exception:
        return str(path)
 
 
def read_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None
 
 
def preview_json_flat(data, max_items=JSON_PREVIEW_KEYS):
    if not isinstance(data, dict):
        return f"(non-dict JSON, type={type(data).__name__})"
    items = []
    for i, (k, v) in enumerate(data.items()):
        if i >= max_items:
            items.append("... (truncated)")
            break
        items.append(f"{k!r}: {repr(v)[:120]}")
    return "\n".join(items)
 
 
def read_csv_head(path: Path, n=CSV_HEAD_ROWS):
    head_rows = []
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                head_rows.append(row)
                if i >= n:
                    break
    except Exception as e:
        head_rows.append([f"Error reading CSV: {e}"])
    return head_rows
 
 
def format_csv_table(rows):
    if not rows:
        return "(no rows)"
    # Simple markdown-like table
    out = []
    header = rows[0]
    out.append("| " + " | ".join(header) + " |")
    out.append("| " + " | ".join(["---"] * len(header)) + " |")
    for row in rows[1:]:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)
 
 
def tail_file(path: Path, n=LOG_TAIL_LINES):
    lines = []
    try:
        with path.open("rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            buf = bytearray()
            block = 1024
            while len(lines) <= n and size > 0:
                read_size = min(block, size)
                size -= read_size
                f.seek(size)
                buf.extend(f.read(read_size))
                lines = buf.splitlines()
            text_lines = [b.decode("utf-8", errors="replace") for b in lines[-n:]]
            return text_lines
    except Exception as e:
        return [f"Error reading log tail: {e}"]
 
 
def find_phase_functions(py_path: Path):
    """
    Scan a .py file for patterns:
        def run_phaseXXX(
    and phase numbers in filename:
        phaseXXX_*.py
    Returns list of dicts.
    """
    results = []
    txt = ""
    try:
        txt = py_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return results
 
    # Find phase numbers by run_phaseXXX
    for m in re.finditer(r"def\s+run_phase(\d+)\s*\(", txt):
        phase_num = int(m.group(1))
        fn_name = f"run_phase{phase_num}"
        results.append({
            "phase_number": phase_num,
            "function": fn_name,
            "from": "function_name",
        })
 
    # Also look at filename pattern
    fn = py_path.name
    m2 = re.search(r"phase(\d+)", fn)
    if m2:
        phase_num = int(m2.group(1))
        # Only add if not already present
        if not any(r["phase_number"] == phase_num for r in results):
            results.append({
                "phase_number": phase_num,
                "function": None,
                "from": "filename",
            })
 
    # Try to extract a simple title from top-of-file docstring or first comment
    title = None
    m3 = re.search(r'"""(.*?)"""', txt, re.DOTALL)
    if m3:
        first = m3.group(1).strip().splitlines()[0]
        if first:
            title = first.strip()
    if not title:
        m4 = re.search(r"#\s*(PHASE.*)", txt)
        if m4:
            title = m4.group(1).strip()
 
    for r in results:
        r["file"] = str(py_path)
        r["title"] = title
 
    return results
 
 
def walk_phase_files(root: Path):
    phase_entries = []
    for sub in PHASE_FILE_ROOTS:
        base = root / sub
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            phase_entries.extend(find_phase_functions(p))
    # sort by phase_number
    phase_entries.sort(key=lambda x: x["phase_number"])
    return phase_entries
 
 
def describe_file(path: Path, root: Path):
    if not path.exists():
        return {
            "exists": False,
            "rel": rel(path, root),
            "size": None,
            "mtime": None,
        }
    stat = path.stat()
    return {
        "exists": True,
        "rel": rel(path, root),
        "size": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }
 
 
def find_latest_file_glob(root: Path, pattern: str):
    matches = list(root.glob(pattern))
    if not matches:
        return None
    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0]
 
 
# -----------------------------
# Main inspection
# -----------------------------
 
def main():
    root = Path(__file__).resolve().parent
    report_path = root / "SYSTEM3_FULL_INSPECTION_REPORT.md"
 
    lines = []
    now = datetime.now().isoformat()
 
    lines.append(f"# SYSTEM3 FULL INSPECTION REPORT")
    lines.append("")
    lines.append(f"- Generated at: `{now}`")
    lines.append(f"- Project root: `{root}`")
    lines.append(f"- Python: `{sys.executable}` (version {sys.version.split()[0]})")
    lines.append("")
 
    # --- Section 1: Folder & environment summary ---
    lines.append("## 1. Folder & Environment Summary")
    subdirs = []
    for child in root.iterdir():
        if child.is_dir():
            subdirs.append(child.name)
    lines.append("")
    lines.append(f"- Subfolders in root: {', '.join(sorted(subdirs)) or '(none)'}")
    lines.append("")
 
    # --- Section 2: Phase discovery ---
    lines.append("## 2. Phase Discovery (run_phaseXXX + phaseXXX filenames)")
    phase_entries = walk_phase_files(root)
 
    if not phase_entries:
        lines.append("")
        lines.append("_No phase files detected (run_phaseXXX). Check PHASE_FILE_ROOTS configuration in the script._")
    else:
        lines.append("")
        lines.append("| Phase | Source | File | Function | Title |")
        lines.append("|-------|--------|------|----------|-------|")
        for e in phase_entries:
            lines.append(
                f"| {e['phase_number']} "
                f"| {e['from']} "
                f"| `{rel(Path(e['file']), root)}` "
                f"| `{e['function'] or ''}` "
                f"| {e['title'] or ''} |"
            )
    lines.append("")
 
    # --- Section 3: Key runtime files (CSV/JSON) ---
    lines.append("## 3. Key Runtime Files (CSV / JSON)")
    lines.append("")
    for key, relpath in KEY_FILES.items():
        p = root / relpath
        meta = describe_file(p, root)
        lines.append(f"### {key}")
        lines.append("")
        lines.append(f"- Path: `{meta['rel']}`")
        lines.append(f"- Exists: `{meta['exists']}`")
        lines.append(f"- Size: `{meta['size']}` bytes")
        lines.append(f"- Last modified: `{meta['mtime']}`")
        lines.append("")
 
        if not meta["exists"]:
            continue
 
        # CSV preview
        if p.suffix.lower() == ".csv":
            head_rows = read_csv_head(p, CSV_HEAD_ROWS)
            lines.append("**Head Preview (first rows):**")
            lines.append("")
            if head_rows:
                # cast all to str
                head_rows_str = [[str(x) for x in row] for row in head_rows]
                lines.append(format_csv_table(head_rows_str))
            else:
                lines.append("_No rows in file_")
            lines.append("")
 
        # JSON preview
        elif p.suffix.lower() == ".json":
            data = read_json(p)
            if data is None:
                lines.append("_Error reading JSON._")
            else:
                lines.append("**JSON Preview (flat):**")
                lines.append("")
                preview = preview_json_flat(data)
                lines.append("```")
                lines.append(preview)
                lines.append("```")
            lines.append("")
 
        # Directory special cases
        elif p.is_dir():
            # list a few files
            children = list(p.glob("*"))
            children = sorted(children, key=lambda c: c.stat().st_mtime if c.is_file() else 0, reverse=True)
            lines.append("**Directory contents (top 10 by mtime):**")
            lines.append("")
            for c in children[:10]:
                stat = c.stat()
                lines.append(
                    f"- `{rel(c, root)}` | size={stat.st_size} | mtime={datetime.fromtimestamp(stat.st_mtime).isoformat()}"
                )
            lines.append("")
 
    # --- Section 4: Autopilot log tail ---
    lines.append("## 4. Autopilot Log Tail")
    lines.append("")
    # try to find live_day_autopilot log
    autopilot_dir = root / KEY_FILES.get("autopilot_log_dir", "logs")
    if autopilot_dir.exists():
        latest_log = find_latest_file_glob(autopilot_dir, "live_day_autopilot_*.log*")
    else:
        latest_log = None
 
    if latest_log is None:
        lines.append("_No live_day_autopilot_*.log found._")
    else:
        lines.append(f"- Latest autopilot log: `{rel(latest_log, root)}`")
        lines.append("")
        tail = tail_file(latest_log, LOG_TAIL_LINES)
        lines.append("**Last lines:**")
        lines.append("")
        lines.append("```")
        lines.extend(tail)
        lines.append("```")
    lines.append("")
 
    # --- Section 5: Phase trace logs (if exist) ---
    lines.append("## 5. Phase Trace Logs (if Phases 314/315 implemented later)")
    lines.append("")
    trace_dir = root / KEY_FILES.get("phase_trace_dir", "logs/live_phase_trace")
    if not trace_dir.exists():
        lines.append("_Trace directory not found yet (logs/live_phase_trace). This is expected if Phase 314 is not implemented yet._")
    else:
        latest_trace = find_latest_file_glob(trace_dir, "phase_trace_*.jsonl")
        if latest_trace is None:
            lines.append("_No phase_trace_*.jsonl yet._")
   
 