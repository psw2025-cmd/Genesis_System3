#!/usr/bin/env python3
"""Lock-safe CSV projection for System3 Continuous Closure issue evidence.

The CSV is deliberately operator-readable in Excel.  If Excel holds the CSV
open, new events are appended to a separate JSONL spool and merged on the next
successful invocation.  The spool is metadata-only and secret-like values are
redacted before either file is written.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "audit" / "live_agent_issue_ledger" / "SYSTEM3_LIVE_UNRESOLVED_ISSUES.csv"
FIELDS = (
    "issue_id", "first_seen_utc", "last_seen_utc", "last_seen_ist",
    "severity", "category", "keyword", "status", "source_type",
    "source_path", "command_or_surface", "message", "impact", "root_cause",
    "resolution_attempts", "evidence", "next_action", "user_input_required",
    "user_input_question", "owner", "branch", "commit_sha", "pr_url",
    "production_url", "occurrence_count", "resolution_utc",
    "resolution_evidence", "safe_to_ignore", "notes",
)
STATUSES = {"OPEN", "IN_PROGRESS", "WAITING", "BLOCKED", "RESOLVED", "INFORMATIONAL"}
SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}
PATTERN = re.compile(
    r"(?i)\b(error|exception|traceback|fail(?:ed|ure)?|warning|warn|blocked|"
    r"waiting|degraded|deprecated_endpoint|phone_registration_error|no data|"
    r"no timeseries data|storage|disk full|no space left|chromedriver_not_found)\b"
)
SECRET = re.compile(
    r"(?i)(access[_ -]?token|refresh[_ -]?token|client[_ -]?secret|api[_ -]?key|"
    r"authorization|private[_ -]?key|password)(\s*[:=]\s*)([^\s,;]+)"
)


def _now() -> tuple[str, str]:
    utc = datetime.now(timezone.utc)
    return utc.isoformat().replace("+00:00", "Z"), utc.astimezone(ZoneInfo("Asia/Kolkata")).isoformat()


def sanitize(value: Any, limit: int = 1200) -> str:
    text = str(value or "").replace("\x00", " ").replace("\r", " ").replace("\n", " ").strip()
    text = SECRET.sub(lambda m: f"{m.group(1)}{m.group(2)}[REDACTED]", text)
    return text[:limit]


def stable_issue_id(category: str, keyword: str, source: str, message: str) -> str:
    basis = "|".join(sanitize(v, 300).lower() for v in (category, keyword, source, message))
    return "SYS3-LIVE-" + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:12].upper()


def normalize(event: Dict[str, Any]) -> Dict[str, str]:
    utc, ist = _now()
    row = {field: sanitize(event.get(field, "")) for field in FIELDS}
    row["first_seen_utc"] = row["first_seen_utc"] or utc
    row["last_seen_utc"] = row["last_seen_utc"] or utc
    row["last_seen_ist"] = row["last_seen_ist"] or ist
    row["severity"] = row["severity"].upper() or "MEDIUM"
    row["status"] = row["status"].upper() or "OPEN"
    if row["severity"] not in SEVERITIES:
        raise ValueError(f"invalid severity: {row['severity']}")
    if row["status"] not in STATUSES:
        raise ValueError(f"invalid status: {row['status']}")
    row["user_input_required"] = "YES" if row["user_input_required"].upper() in {"1", "TRUE", "YES"} else "NO"
    row["safe_to_ignore"] = "YES" if row["safe_to_ignore"].upper() in {"1", "TRUE", "YES"} else "NO"
    row["occurrence_count"] = str(max(1, int(row["occurrence_count"] or "1")))
    row["issue_id"] = row["issue_id"] or stable_issue_id(
        row["category"], row["keyword"], row["source_path"], row["message"]
    )
    if row["user_input_required"] == "YES" and not row["user_input_question"]:
        raise ValueError("user_input_question is required when user_input_required=YES")
    if row["status"] == "RESOLVED" and not row["resolution_utc"]:
        row["resolution_utc"] = utc
    return row


def _read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _spool_path(path: Path) -> Path:
    return path.with_suffix(path.suffix + ".pending.jsonl")


def _read_spool(path: Path) -> List[Dict[str, str]]:
    spool = _spool_path(path)
    if not spool.exists():
        return []
    rows = []
    for line in spool.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rows.append(normalize(json.loads(line)))
        except (ValueError, json.JSONDecodeError, TypeError):
            continue
    return rows


def _merge(rows: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    merged: Dict[str, Dict[str, str]] = {}
    for raw in rows:
        row = normalize(raw)
        old = merged.get(row["issue_id"])
        if not old:
            merged[row["issue_id"]] = row
            continue
        count = int(old.get("occurrence_count") or "1") + int(row.get("occurrence_count") or "1")
        first = min(old["first_seen_utc"], row["first_seen_utc"])
        old.update({key: value for key, value in row.items() if value})
        old["first_seen_utc"] = first
        old["occurrence_count"] = str(count)
    return sorted(merged.values(), key=lambda r: (r["status"] in {"RESOLVED", "INFORMATIONAL"}, r["severity"], r["issue_id"]))


def write_events(path: Path, events: Iterable[Dict[str, Any]]) -> str:
    """Upsert events; return CSV_UPDATED or SPOOLED_FILE_LOCKED."""
    path.parent.mkdir(parents=True, exist_ok=True)
    new_rows = [normalize(dict(event)) for event in events]
    rows = _merge([*_read_csv(path), *_read_spool(path), *new_rows])
    temp = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    try:
        with temp.open("w", encoding="utf-8-sig", newline="") as handle:
            # LF keeps the tracked projection compatible with git diff --check;
            # Excel accepts UTF-8 BOM + LF on Windows.
            writer = csv.DictWriter(
                handle, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temp, path)
        spool = _spool_path(path)
        if spool.exists():
            spool.unlink()
        return "CSV_UPDATED"
    except PermissionError:
        if temp.exists():
            temp.unlink()
        spool = _spool_path(path)
        with spool.open("a", encoding="utf-8") as handle:
            for row in new_rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        return "SPOOLED_FILE_LOCKED"


def scan_files(paths: Iterable[Path], *, max_matches: int = 1000) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    for path in paths:
        if not path.is_file():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            match = PATTERN.search(line)
            if not match:
                continue
            keyword = match.group(1).upper().replace(" ", "_")
            message = sanitize(line)
            events.append({
                "severity": "MEDIUM" if keyword not in {"WARNING", "WARN", "WAITING"} else "LOW",
                "category": "LOG_SCAN",
                "keyword": keyword,
                "status": "OPEN",
                "source_type": "LOCAL_LOG",
                "source_path": str(path),
                "command_or_surface": f"line:{line_no}",
                "message": message,
                "impact": "Requires classification; keyword detection alone is not proof of product failure.",
                "next_action": "Reproduce from a current authoritative source, classify, then resolve or update this row.",
                "owner": "SYSTEM3_CONTINUOUS_CLOSURE",
            })
            if len(events) >= max_matches:
                return events
    return events


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    sub = parser.add_subparsers(dest="command", required=True)
    record = sub.add_parser("record")
    for name in FIELDS:
        if name not in {"first_seen_utc", "last_seen_utc", "last_seen_ist", "occurrence_count"}:
            record.add_argument("--" + name.replace("_", "-"), default="")
    scan = sub.add_parser("scan")
    scan.add_argument("paths", nargs="+", type=Path)
    scan.add_argument("--max-matches", type=int, default=1000)
    sub.add_parser("flush")
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "record":
        event = {field: getattr(args, field, "") for field in FIELDS}
        result = write_events(args.csv, [event])
    elif args.command == "scan":
        events = scan_files(args.paths, max_matches=max(1, args.max_matches))
        result = write_events(args.csv, events) if events else write_events(args.csv, [])
        print(f"MATCHES={len(events)}")
    else:
        result = write_events(args.csv, [])
    print(f"LIVE_ISSUE_LEDGER={result} CSV={args.csv} PENDING={_spool_path(args.csv)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
