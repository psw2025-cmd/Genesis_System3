#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick inspector that writes `SYSTEM3_QUICK_INSPECTION_REPORT.md` in project root.
Safe, read-only.
"""
from pathlib import Path
from datetime import datetime
import sys, csv, json

KEY_FILES = {
    "heartbeat_json": "storage/meta/system3_daily_heartbeat.json",
    "signals_curated_csv": "storage/live/angel_index_ai_signals_curated.csv",
    "signals_forward_csv": "storage/live/angel_index_ai_signals_with_forward.csv",
    "pnl_log_csv": "storage/live/angel_index_ai_pnl_log.csv",
    "autopilot_log_dir": "logs",
}

CSV_HEAD_ROWS = 5
LOG_TAIL_LINES = 40


def rel(path: Path, root: Path):
    try:
        return str(path.relative_to(root))
    except Exception:
        return str(path)


def read_csv_head(p: Path, n=CSV_HEAD_ROWS):
    rows = []
    try:
        with p.open("r", encoding="utf-8", newline="") as f:
            r = csv.reader(f)
            for i, row in enumerate(r):
                rows.append([str(x) for x in row])
                if i >= n:
                    break
    except Exception as e:
        rows.append([f"Error: {e}"])
    return rows


def tail_file(p: Path, n=LOG_TAIL_LINES):
    try:
        with p.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            return [l.rstrip("\n") for l in lines[-n:]]
    except Exception as e:
        return [f"Error reading file: {e}"]


def format_csv_table(rows):
    if not rows:
        return "(no rows)"
    out = []
    header = rows[0]
    out.append("| " + " | ".join(header) + " |")
    out.append("| " + " | ".join(["---"] * len(header)) + " |")
    for r in rows[1:]:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def main():
    root = Path(__file__).resolve().parent.parent
    report = root / "SYSTEM3_QUICK_INSPECTION_REPORT.md"
    now = datetime.now().isoformat()
    lines = []
    lines.append("# SYSTEM3 QUICK INSPECTION REPORT")
    lines.append("")
    lines.append(f"- Generated at: `{now}`")
    lines.append(f"- Project root: `{root}`")
    lines.append(f"- Python: `{sys.executable}` (version {sys.version.split()[0]})")
    lines.append("")

    lines.append("## Folder summary")
    dirs = [p.name for p in root.iterdir() if p.is_dir()]
    lines.append("")
    lines.append(f'- Subfolders: {", ".join(sorted(dirs))}')
    lines.append("")

    lines.append("## Key files")
    lines.append("")
    for k, relpath in KEY_FILES.items():
        p = root / relpath
        lines.append(f"### {k}")
        lines.append("")
        lines.append(f"- Path: `{rel(p,root)}`")
        lines.append(f"- Exists: `{p.exists()}`")
        if p.exists() and p.suffix.lower() == ".csv":
            head = read_csv_head(p, CSV_HEAD_ROWS)
            lines.append("")
            lines.append("**CSV head:**")
            lines.append("")
            lines.append(format_csv_table(head))
        if p.exists() and p.suffix.lower() == ".json":
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                lines.append("")
                lines.append("**JSON preview:**")
                lines.append("")
                if isinstance(data, dict):
                    for i, (kk, vv) in enumerate(data.items()):
                        if i >= 50:
                            break
                        lines.append(f"- `{kk}`: {repr(vv)[:120]}")
                else:
                    lines.append(f"({type(data).__name__})")
            except Exception as e:
                lines.append(f"_Error reading JSON: {e}_")
        lines.append("")

    # autopilot
    lines.append("## Autopilot tail")
    lines.append("")
    autopilot_dir = root / KEY_FILES.get("autopilot_log_dir", "logs")
    if autopilot_dir.exists():
        cand = list(autopilot_dir.glob("live_day_autopilot_*.log*"))
        if cand:
            latest = max(cand, key=lambda p: p.stat().st_mtime)
            lines.append(f"- Latest: `{rel(latest,root)}`")
            lines.append("")
            lines.append("```")
            lines.extend(tail_file(latest, LOG_TAIL_LINES))
            lines.append("```")
        else:
            lines.append("_No live_day_autopilot_*.log found._")
    else:
        lines.append("_Autopilot log dir not found._")

    try:
        report.write_text("\n".join(lines), encoding="utf-8")
        print(f"WROTE_REPORT::{report}")
    except Exception as e:
        print(f"ERROR_WRITING::{e}")


if __name__ == "__main__":
    main()
