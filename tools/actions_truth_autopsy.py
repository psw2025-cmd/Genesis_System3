#!/usr/bin/env python3
"""Summarize completed GitHub Actions proof runs.

This script reads downloaded workflow logs and artifacts, extracts PASS/FAIL,
BLOCKED_NOT_TRADE_READY, endpoint, browser, and chain blockers, writes a compact
sanitized report, then optionally removes raw downloaded files. It is read-only
against trading/runtime systems and does not call broker/order endpoints.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

SECRET_RE = re.compile(
    r"(?i)(token|secret|password|passwd|pwd|pin|totp|api[_-]?key|access[_-]?token|authorization|deploy[_-]?hook)"
)
LONG_VALUE_RE = re.compile(r"[A-Za-z0-9_\-]{32,}")
BLOCKER_RE = re.compile(
    r"(?i)(FAIL|FAILED|ERROR|BLOCKED|BLOCKER|EXCEPTION|401|403|404|500|NO_DHAN_DATA|NOT_TRADE_READY|CHAIN_NOT|UI_FAIL|API_FAIL|BROWSER_CONSOLE|PAGE_ERROR|REQUEST_FAILED)"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def redact_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if SECRET_RE.search(line):
            # Keep key name/context but never keep values.
            line = re.sub(r"([:=]\s*)[^\s]+", r"\1[REDACTED]", line)
        line = LONG_VALUE_RE.sub("[REDACTED]", line)
        lines.append(line)
    return "\n".join(lines)


def redact_obj(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for k, v in obj.items():
            if SECRET_RE.search(str(k)):
                if isinstance(v, bool) or str(k).lower().endswith(("_present", "present")):
                    out[k] = bool(v)
                else:
                    out[k] = "[REDACTED]"
            else:
                out[k] = redact_obj(v)
        return out
    if isinstance(obj, list):
        return [redact_obj(x) for x in obj[:500]]
    if isinstance(obj, str):
        return redact_text(obj)
    return obj


def iter_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    return (p for p in root.rglob("*") if p.is_file())


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def collect_summaries(root: Path) -> List[Dict[str, Any]]:
    summaries: List[Dict[str, Any]] = []
    for p in iter_files(root):
        rel = str(p.relative_to(root))
        if p.name.lower() == "summary.json":
            data = load_json(p)
            if isinstance(data, dict):
                summaries.append({"path": rel, "type": "summary_json", "data": redact_obj(data)})
        elif p.name.lower() == "summary.md":
            text = redact_text(p.read_text(encoding="utf-8", errors="replace"))[:12000]
            summaries.append({"path": rel, "type": "summary_md", "text": text})
    return summaries


def collect_blocker_lines(root: Path, limit: int = 300) -> List[Dict[str, str]]:
    hits: List[Dict[str, str]] = []
    for p in iter_files(root):
        if len(hits) >= limit:
            break
        if p.suffix.lower() not in {".txt", ".log", ".md", ".json"}:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for idx, line in enumerate(text.splitlines(), start=1):
            if BLOCKER_RE.search(line):
                hits.append({
                    "file": str(p.relative_to(root)),
                    "line": str(idx),
                    "text": redact_text(line)[:600],
                })
                if len(hits) >= limit:
                    break
    return hits


def infer_verdict(summaries: List[Dict[str, Any]], blocker_lines: List[Dict[str, str]]) -> str:
    verdicts: List[str] = []
    for item in summaries:
        data = item.get("data")
        if isinstance(data, dict):
            v = data.get("final_verdict") or data.get("verdict")
            if v:
                verdicts.append(str(v).upper())
        text = item.get("text")
        if isinstance(text, str):
            for m in re.finditer(r"(?i)(final verdict|verdict):\s*\*?\*?([A-Z_]+)", text):
                verdicts.append(m.group(2).upper())
    if any(v == "FAIL" for v in verdicts):
        return "FAIL"
    if any(v in {"BLOCKED", "BLOCKED_NOT_TRADE_READY"} for v in verdicts):
        return "BLOCKED_NOT_TRADE_READY"
    if verdicts and all(v in {"PASS", "OK", "WARN"} for v in verdicts):
        return "PASS"
    if blocker_lines:
        return "FAIL"
    return "UNKNOWN"


def write_report(out: Path, raw_root: Path, run_meta: Dict[str, Any], delete_raw: bool) -> None:
    out.mkdir(parents=True, exist_ok=True)
    summaries = collect_summaries(raw_root)
    blocker_lines = collect_blocker_lines(raw_root)
    verdict = infer_verdict(summaries, blocker_lines)

    report = {
        "generated_utc": utc_now(),
        "script": "tools/actions_truth_autopsy.py",
        "run": redact_obj(run_meta),
        "final_verdict": verdict,
        "summary_files_count": len(summaries),
        "blocker_lines_count": len(blocker_lines),
        "summaries": summaries,
        "blocker_lines": blocker_lines,
        "raw_deleted_after_analysis": bool(delete_raw),
        "safety": {
            "live_trading_enabled": False,
            "order_endpoints_called": False,
            "secrets_redacted": True,
        },
    }
    (out / "summary.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Actions Truth Autopsy",
        "",
        f"- Generated UTC: `{report['generated_utc']}`",
        f"- Workflow: `{run_meta.get('workflow_name', '-')}`",
        f"- Run ID: `{run_meta.get('run_id', '-')}`",
        f"- Conclusion: `{run_meta.get('conclusion', '-')}`",
        f"- Autopsy verdict: **{verdict}**",
        f"- Summary files found: `{len(summaries)}`",
        f"- Blocker lines found: `{len(blocker_lines)}`",
        f"- Raw downloaded files deleted after analysis: `{bool(delete_raw)}`",
        "",
        "## Top blocker lines",
    ]
    if blocker_lines:
        for hit in blocker_lines[:80]:
            lines.append(f"- `{hit['file']}:{hit['line']}` — {hit['text']}")
    else:
        lines.append("- None")
    lines.extend([
        "",
        "## Summary files",
    ])
    if summaries:
        for item in summaries[:40]:
            if item["type"] == "summary_json":
                data = item.get("data") or {}
                v = data.get("final_verdict") or data.get("verdict") or "-"
                lines.append(f"- `{item['path']}` type=json verdict=`{v}`")
            else:
                lines.append(f"- `{item['path']}` type=markdown")
    else:
        lines.append("- None")
    lines.extend([
        "",
        "## Safety",
        "- This autopsy only reads workflow logs/artifacts.",
        "- It does not call broker order placement, modification, cancellation, or live enablement endpoints.",
        "- Secret-looking keys/values are redacted before report upload.",
    ])
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if delete_raw and raw_root.exists():
        shutil.rmtree(raw_root, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", default="reports/latest/actions_truth_autopsy/raw")
    parser.add_argument("--out", default="reports/latest/actions_truth_autopsy")
    parser.add_argument("--delete-raw", action="store_true")
    parser.add_argument("--workflow-name", default=os.environ.get("SOURCE_WORKFLOW_NAME", ""))
    parser.add_argument("--run-id", default=os.environ.get("SOURCE_RUN_ID", ""))
    parser.add_argument("--conclusion", default=os.environ.get("SOURCE_RUN_CONCLUSION", ""))
    args = parser.parse_args()

    run_meta = {
        "workflow_name": args.workflow_name,
        "run_id": args.run_id,
        "conclusion": args.conclusion,
    }
    write_report(Path(args.out), Path(args.raw_root), run_meta, args.delete_raw)
    print((Path(args.out) / "summary.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
