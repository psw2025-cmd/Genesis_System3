#!/usr/bin/env python3
"""
System3 Model Accuracy Tracker.

Read-only verifier for prediction-before-move and outcome proof availability.

Outputs:
- reports/latest/model_accuracy_report.json
- reports/latest/model_accuracy_report.md
- reports/history/model_accuracy_YYYYMMDD.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class AccuracyRow:
    prediction_ts_ist: str
    symbol: str
    symbol_type: str
    direction: str
    option_side: str
    confidence: Optional[float]
    selected_strike: str
    actual_5m: Optional[float]
    actual_15m: Optional[float]
    actual_30m: Optional[float]
    actual_eod: Optional[float]
    direction_correct: Optional[bool]
    option_profitable: Optional[bool]
    max_favorable_move: Optional[float]
    max_adverse_move: Optional[float]
    proof_status: str
    blocker_reason: str


INDEX_UNDERLYINGS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"}


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def safe_json_file(path: Path) -> Optional[Any]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def fetch_json(url: str, timeout: int = 8) -> Optional[Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception:
        return None


def norm_symbol(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"[^A-Z0-9]", "", str(value).upper())


def as_float(value: Any) -> Optional[float]:
    try:
        if value in (None, "", "-"):
            return None
        return float(value)
    except Exception:
        return None


def iter_dicts(obj: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from iter_dicts(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_dicts(item)


def symbol_type(symbol: str) -> str:
    if symbol in INDEX_UNDERLYINGS:
        return "INDEX"
    if symbol:
        return "EQUITY"
    return "UNKNOWN"


def infer_direction(d: Dict[str, Any]) -> str:
    blob = json.dumps(d, ensure_ascii=False).upper()
    explicit = str(d.get("direction") or d.get("signal_type") or d.get("signal") or "").upper()
    if explicit:
        blob = explicit + " " + blob
    if "PUT" in blob or "PE" in blob or "DOWN" in blob or "SHORT" in blob:
        return "DOWN"
    if "CALL" in blob or "CE" in blob or "UP" in blob or "LONG" in blob or "BUY" in blob:
        return "UP"
    return "UNKNOWN"


def infer_option_side(direction: str, d: Dict[str, Any]) -> str:
    blob = json.dumps(d, ensure_ascii=False).upper()
    if "PUT" in blob or "PE" in blob:
        return "PE"
    if "CALL" in blob or "CE" in blob:
        return "CE"
    if direction == "DOWN":
        return "PE"
    if direction == "UP":
        return "CE"
    return "UNKNOWN"


def extract_prediction_candidates(obj: Any) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for d in iter_dicts(obj):
        sym = d.get("symbol") or d.get("underlying") or d.get("name")
        score = d.get("score") or d.get("confidence") or d.get("display_score") or d.get("rank_score")
        ts = d.get("ts") or d.get("timestamp") or d.get("time") or d.get("prediction_ts")
        if sym and (score is not None or ts is not None or "signal" in {str(k).lower() for k in d.keys()}):
            rows.append(d)
    seen = set()
    out = []
    for r in rows:
        key = (
            norm_symbol(r.get("symbol") or r.get("underlying") or r.get("name")),
            str(r.get("ts") or r.get("timestamp") or r.get("time") or ""),
        )
        if key not in seen and key[0]:
            seen.add(key)
            out.append(r)
    return out[:200]


def load_prediction_sources(root: Path, api_base: Optional[str]) -> tuple[List[Dict[str, Any]], List[str]]:
    sources: List[str] = []
    all_rows: List[Dict[str, Any]] = []
    if api_base:
        for endpoint in ["/api/state", "/api/gain_rank", "/api/accuracy_trend"]:
            data = fetch_json(api_base.rstrip("/") + endpoint)
            if data is not None:
                rows = extract_prediction_candidates(data)
                if rows:
                    all_rows.extend(rows)
                    sources.append(f"api:{endpoint}")
    candidates = [
        root / "state" / "gain_rank_history.json",
        root / "state" / "market_validations" / "market_validation_2026-06-12.json",
        root / "reports" / "latest" / "option_strike_visibility.json",
        root / "outputs" / "signals.json",
        root / "outputs" / "ai_signals.json",
    ]
    for p in candidates:
        data = safe_json_file(p)
        if data is not None:
            rows = extract_prediction_candidates(data)
            if rows:
                all_rows.extend(rows)
                sources.append(str(p.relative_to(root)))
    # Also scan market_validations folder.
    mv = root / "state" / "market_validations"
    if mv.exists():
        for p in sorted(mv.glob("*.json"))[-10:]:
            data = safe_json_file(p)
            rows = extract_prediction_candidates(data) if data is not None else []
            if rows:
                all_rows.extend(rows)
                sources.append(str(p.relative_to(root)))
    # Deduplicate.
    seen = set()
    out = []
    for r in all_rows:
        key = json.dumps(
            {
                "sym": norm_symbol(r.get("symbol") or r.get("underlying") or r.get("name")),
                "ts": str(r.get("ts") or r.get("timestamp") or r.get("time") or r.get("prediction_ts") or ""),
                "score": str(
                    r.get("score") or r.get("confidence") or r.get("display_score") or r.get("rank_score") or ""
                ),
            },
            sort_keys=True,
        )
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out[:300], sources


def make_accuracy_rows(predictions: List[Dict[str, Any]]) -> List[AccuracyRow]:
    rows: List[AccuracyRow] = []
    for p in predictions:
        sym = norm_symbol(p.get("symbol") or p.get("underlying") or p.get("name")) or "UNKNOWN"
        direction = infer_direction(p)
        option_side = infer_option_side(direction, p)
        confidence = as_float(p.get("confidence") or p.get("score") or p.get("display_score") or p.get("rank_score"))
        strike = str(p.get("strike") or p.get("selected_strike") or p.get("option_strike") or "")
        actual_5m = as_float(p.get("actual_5m") or p.get("ret_5m") or p.get("return_5m"))
        actual_15m = as_float(p.get("actual_15m") or p.get("ret_15m") or p.get("return_15m"))
        actual_30m = as_float(p.get("actual_30m") or p.get("ret_30m") or p.get("return_30m"))
        actual_eod = as_float(p.get("actual_eod") or p.get("eod_return") or p.get("return_eod"))
        direction_correct = None
        outcome = (
            actual_30m
            if actual_30m is not None
            else actual_15m if actual_15m is not None else actual_5m if actual_5m is not None else actual_eod
        )
        if outcome is not None and direction in {"UP", "DOWN"}:
            direction_correct = outcome > 0 if direction == "UP" else outcome < 0
        option_profitable = None
        if direction_correct is not None and option_side in {"CE", "PE"}:
            option_profitable = bool(direction_correct)
        moves = [x for x in [actual_5m, actual_15m, actual_30m, actual_eod] if x is not None]
        max_fav = max(moves) if direction == "UP" and moves else min(moves) if direction == "DOWN" and moves else None
        max_adv = min(moves) if direction == "UP" and moves else max(moves) if direction == "DOWN" and moves else None
        blockers = []
        if str(p.get("ts") or p.get("timestamp") or p.get("time") or p.get("prediction_ts") or "") == "":
            blockers.append("PREDICTION_TIMESTAMP_MISSING")
        if direction == "UNKNOWN":
            blockers.append("DIRECTION_MISSING")
        if option_side == "UNKNOWN":
            blockers.append("OPTION_SIDE_UNKNOWN")
        if strike == "":
            blockers.append("STRIKE_NOT_LINKED")
        if outcome is None:
            blockers.append("ACTUAL_OUTCOME_WINDOW_MISSING")
        proof_status = "PASS" if not blockers and direction_correct is not None else "BLOCKED"
        rows.append(
            AccuracyRow(
                prediction_ts_ist=str(
                    p.get("ts") or p.get("timestamp") or p.get("time") or p.get("prediction_ts") or "UNKNOWN"
                ),
                symbol=sym,
                symbol_type=symbol_type(sym),
                direction=direction,
                option_side=option_side,
                confidence=confidence,
                selected_strike=strike,
                actual_5m=actual_5m,
                actual_15m=actual_15m,
                actual_30m=actual_30m,
                actual_eod=actual_eod,
                direction_correct=direction_correct,
                option_profitable=option_profitable,
                max_favorable_move=max_fav,
                max_adverse_move=max_adv,
                proof_status=proof_status,
                blocker_reason=";".join(blockers) if blockers else "PASS",
            )
        )
    if not rows:
        rows.append(
            AccuracyRow(
                prediction_ts_ist="UNKNOWN",
                symbol="NO_PREDICTION_FOUND",
                symbol_type="UNKNOWN",
                direction="UNKNOWN",
                option_side="UNKNOWN",
                confidence=None,
                selected_strike="",
                actual_5m=None,
                actual_15m=None,
                actual_30m=None,
                actual_eod=None,
                direction_correct=None,
                option_profitable=None,
                max_favorable_move=None,
                max_adverse_move=None,
                proof_status="BLOCKED",
                blocker_reason="NO_PREDICTION_SOURCE_FOUND",
            )
        )
    return rows


def write_reports(root: Path, rows: List[AccuracyRow], sources: List[str]) -> None:
    reports = root / "reports" / "latest"
    hist = root / "reports" / "history"
    reports.mkdir(parents=True, exist_ok=True)
    hist.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc)
    pass_rows = [r for r in rows if r.proof_status == "PASS"]
    direction_known = [r for r in rows if r.direction_correct is not None]
    summary = {
        "generated_at_utc": generated.isoformat(),
        "sources": sources,
        "rows": len(rows),
        "proof_pass_count": len(pass_rows),
        "blocked_count": len(rows) - len(pass_rows),
        "direction_known_count": len(direction_known),
        "direction_hit_rate": (
            (sum(1 for r in direction_known if r.direction_correct) / len(direction_known)) if direction_known else None
        ),
        "option_profitable_known_count": sum(1 for r in rows if r.option_profitable is not None),
    }
    data = {"summary": summary, "rows": [asdict(r) for r in rows]}
    json_text = json.dumps(data, indent=2, ensure_ascii=False)
    (reports / "model_accuracy_report.json").write_text(json_text, encoding="utf-8")
    (hist / f"model_accuracy_{generated.strftime('%Y%m%d')}.json").write_text(json_text, encoding="utf-8")
    lines = [
        "# System3 Model Accuracy Report",
        "",
        f"Generated UTC: `{summary['generated_at_utc']}`",
        "",
        "## Summary",
        "",
        f"- **Sources**: `{', '.join(sources) if sources else 'none'}`",
        f"- **Rows**: `{summary['rows']}`",
        f"- **Proof pass count**: `{summary['proof_pass_count']}`",
        f"- **Blocked count**: `{summary['blocked_count']}`",
        f"- **Direction known count**: `{summary['direction_known_count']}`",
        f"- **Direction hit rate**: `{summary['direction_hit_rate']}`",
        "",
        "## Accuracy Rows",
        "",
        "| Symbol | Type | Direction | CE/PE | Confidence | Strike | 5m | 15m | 30m | EOD | Direction Correct | Option Profitable | Proof | Blocker |",
        "|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| `{r.symbol}` | `{r.symbol_type}` | `{r.direction}` | `{r.option_side}` | `{r.confidence}` | `{r.selected_strike}` | `{r.actual_5m}` | `{r.actual_15m}` | `{r.actual_30m}` | `{r.actual_eod}` | `{r.direction_correct}` | `{r.option_profitable}` | `{r.proof_status}` | `{r.blocker_reason}` |"
        )
    lines.extend(
        [
            "",
            "## Pass Rule",
            "",
            "Model accuracy is not proven until 5+ market days include prediction-before-move timestamps, option-mapped strike/token proof, and actual 5m/15m/30m/EOD outcomes.",
        ]
    )
    (reports / "model_accuracy_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="System3 model accuracy tracker")
    parser.add_argument("--root", default=None)
    parser.add_argument("--api-base", default=os.environ.get("SYSTEM3_API_BASE"))
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else repo_root_from_script()
    predictions, sources = load_prediction_sources(root, args.api_base)
    rows = make_accuracy_rows(predictions)
    write_reports(root, rows, sources)
    print("SYSTEM3_MODEL_ACCURACY_TRACKER_COMPLETE")
    print(json.dumps({"rows": len(rows), "sources": sources}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
