"""Fail-closed auditor for System3 signal/plan CSVs (Gmail/export).

Reads only the supplied rows. Does not invent prices, PnL, or ρ, and never
authorizes LIVE trading or broker order actions.
"""

from __future__ import annotations

import csv
import io
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

REQUIRED_TRADE_COLUMNS = {"symbol", "entry", "stoploss", "target"}
SCANNER_COLUMNS = {"symbol", "ltp", "gain_pct"}
PLAN_SCHEMA_COLUMNS = {
    "issue_id",
    "proof_id",
    "query_id",
    "phase",
    "pending_action",
    "screenshot_reference",
    "category",
}
TINY_PREMIUM_MAX_LTP = 5.0
EXTREME_GAIN_PCT = 200.0
LIVE_OR_ORDER_RE = re.compile(
    r"\b(enable\s+live|live_trading|auto_execute|square[- ]off|place\s+order|"
    r"modify\s+order|cancel\s+order|buy\s+more\s+lots)\b",
    re.I,
)


def _f(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() in {"nan", "none", "null", "--"}:
        return None
    try:
        return float(text.replace(",", "").replace("%", ""))
    except ValueError:
        return None


def _geometry(entry: Optional[float], sl: Optional[float], target: Optional[float]) -> str:
    if entry is None or sl is None or target is None:
        return "UNKNOWN"
    if entry <= 0 or sl <= 0 or target <= 0:
        return "NON_POSITIVE"
    long_ok = sl < entry < target
    short_ok = target < entry < sl
    if long_ok and not short_ok:
        return "LONG"
    if short_ok and not long_ok:
        return "SHORT"
    return "INVALID"


def _rr(entry: Optional[float], sl: Optional[float], target: Optional[float], side: str) -> Optional[float]:
    if entry is None or sl is None or target is None or side not in {"LONG", "SHORT"}:
        return None
    risk = abs(entry - sl)
    reward = abs(target - entry)
    if risk <= 0:
        return None
    return round(reward / risk, 4)


def _iter_rows(raw_lines: Sequence[str]) -> tuple[List[str], List[Dict[str, str]]]:
    reader = csv.DictReader(io.StringIO("\n".join(raw_lines)))
    headers = [h.strip() for h in (reader.fieldnames or []) if h and str(h).strip()]
    rows: List[Dict[str, str]] = []
    for raw in reader:
        rows.append({str(k).strip(): "" if v is None else str(v).strip() for k, v in raw.items() if k})
    return headers, rows


def audit_signal_plan_texts(lines: Sequence[str]) -> Dict[str, Any]:
    headers, raw_rows = _iter_rows(lines)
    header_set = {h.lower() for h in headers}
    findings: List[Dict[str, Any]] = []
    parsed: List[Dict[str, Any]] = []
    is_trade = bool(headers) and REQUIRED_TRADE_COLUMNS.issubset(header_set)
    is_scanner = bool(headers) and SCANNER_COLUMNS.issubset(header_set)
    is_plan = bool(headers) and bool(header_set & PLAN_SCHEMA_COLUMNS)

    if headers and not (is_trade or is_scanner or is_plan or "recommendation" in header_set):
        missing = sorted(REQUIRED_TRADE_COLUMNS - header_set)
        if missing:
            findings.append(
                {
                    "code": "MISSING_COLUMNS",
                    "severity": "P0",
                    "detail": "required columns absent: " + ",".join(missing),
                }
            )

    valid = 0
    invalid = 0
    for idx, raw in enumerate(raw_rows, start=1):
        lowered = {k.lower(): v for k, v in raw.items()}
        symbol = lowered.get("symbol") or lowered.get("category") or f"row-{idx}"
        entry = _f(lowered.get("entry"))
        sl = _f(lowered.get("stoploss") or lowered.get("stop_loss") or lowered.get("sl"))
        target = _f(lowered.get("target") or lowered.get("target_exit"))
        pnl = _f(lowered.get("pnl") or lowered.get("entry_pnl"))
        change = _f(lowered.get("change"))
        rec = lowered.get("recommendation") or ""
        ltp = _f(lowered.get("ltp"))
        gain_pct = _f(lowered.get("gain_pct"))
        side = _geometry(entry, sl, target)
        rr = _rr(entry, sl, target, side)
        row_ok = True
        if is_scanner and ltp is not None and gain_pct is not None:
            if 0 < ltp < TINY_PREMIUM_MAX_LTP and gain_pct > EXTREME_GAIN_PCT:
                findings.append(
                    {
                        "code": "TINY_PREMIUM_EXTREME_GAIN",
                        "severity": "P0",
                        "row": idx,
                        "symbol": symbol,
                        "detail": (
                            f"ltp={ltp} gain_pct={gain_pct} is scanner-outlier quality, "
                            "not a trade signal"
                        ),
                    }
                )
        if "entry" in lowered or "stoploss" in lowered or "target" in lowered:
            if entry is not None and entry <= 0:
                row_ok = False
                findings.append(
                    {
                        "code": "NON_POSITIVE_PRICE",
                        "severity": "P0",
                        "row": idx,
                        "symbol": symbol,
                        "detail": "entry/sl/target must be > 0 when present",
                    }
                )
            elif side == "INVALID":
                row_ok = False
                findings.append(
                    {
                        "code": "INVALID_GEOMETRY",
                        "severity": "P0",
                        "row": idx,
                        "symbol": symbol,
                        "detail": "stoploss/entry/target are not a valid long or short ladder",
                    }
                )
            elif side == "NON_POSITIVE":
                row_ok = False
                findings.append(
                    {
                        "code": "NON_POSITIVE_PRICE",
                        "severity": "P0",
                        "row": idx,
                        "symbol": symbol,
                        "detail": "entry/sl/target must be > 0 when present",
                    }
                )
        if rec and LIVE_OR_ORDER_RE.search(rec):
            row_ok = False
            findings.append(
                {
                    "code": "LIVE_OR_ORDER_LANGUAGE",
                    "severity": "P0",
                    "row": idx,
                    "symbol": symbol,
                    "detail": "plan text requests LIVE/order action; ignored (ANALYZE/PAPER only)",
                }
            )
        if row_ok and (side in {"LONG", "SHORT"} or rec):
            valid += 1
        elif "entry" in lowered or rec:
            invalid += 1
        parsed.append(
            {
                "row": idx,
                "symbol": symbol,
                "entry": entry,
                "stoploss": sl,
                "target": target,
                "change": change,
                "pnl": pnl,
                "side": side,
                "reward_risk": rr,
                "recommendation": rec or None,
                "ltp": ltp,
                "gain_pct": gain_pct,
            }
        )

    return {
        "schema": "signal_plan_audit_v1",
        "ok": not any(f.get("severity") == "P0" and f.get("code") == "MISSING_COLUMNS" for f in findings),
        "error": None,
        "row_count": len(parsed),
        "headers": headers,
        "rows": parsed,
        "findings": findings,
        "invented_prices": False,
        "summary": {
            "valid_rows": valid,
            "invalid_rows": invalid,
            "finding_count": len(findings),
        },
        "safety": {
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "analyze_mode": True,
        },
    }


def audit_signal_plan_csv(path: Path | str) -> Dict[str, Any]:
    target = Path(path)
    if not target.is_file():
        return {
            "schema": "signal_plan_audit_v1",
            "ok": False,
            "error": "FILE_NOT_FOUND",
            "row_count": 0,
            "headers": [],
            "rows": [],
            "findings": [{"code": "FILE_NOT_FOUND", "severity": "P0", "detail": str(target)}],
            "invented_prices": False,
            "summary": {"valid_rows": 0, "invalid_rows": 0, "finding_count": 1},
            "safety": {
                "live_trading_enabled": False,
                "order_placement_allowed": False,
                "analyze_mode": True,
            },
        }
    text = target.read_text(encoding="utf-8-sig")
    return audit_signal_plan_texts(text.splitlines())


def audit_many(paths: Iterable[Path | str]) -> Dict[str, Any]:
    reports = [audit_signal_plan_csv(p) for p in paths]
    return {
        "schema": "signal_plan_audit_batch_v1",
        "file_count": len(reports),
        "reports": reports,
        "invented_prices": False,
        "safety": {"live_trading_enabled": False, "order_placement_allowed": False},
    }
