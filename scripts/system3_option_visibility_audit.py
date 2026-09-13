#!/usr/bin/env python3
"""
System3 Option Visibility Audit.

Read-only verifier for signal -> option tradability -> PE/CE -> expiry -> strike -> token -> quote.

Outputs:
- reports/latest/option_strike_visibility.json
- reports/latest/option_strike_visibility.md
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

INDEX_UNDERLYINGS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"}
BROKER_ACCEPTANCE_REQUIRED = ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")
SUPPORTED_INDEX_UNIVERSE = BROKER_ACCEPTANCE_REQUIRED + ("SENSEX", "BANKEX")


@dataclass
class VisibilityRow:
    signal_ts_ist: str
    underlying: str
    symbol_type: str
    signal_score: Optional[float]
    signal_side: str
    option_side: str
    option_eligible: bool
    eligibility_source: str
    expiry: str
    strike: str
    instrument_token: str
    ltp: Optional[float]
    bid: Optional[float]
    ask: Optional[float]
    spread_pct: Optional[float]
    liquidity_status: str
    paper_trade_allowed: bool
    blocker_reason: str
    trading_symbol: str = ""
    source: str = "UNKNOWN"
    observed_at: str = ""
    source_timestamp: str = ""
    freshness_ms: Optional[float] = None
    market_session: str = "UNKNOWN"
    provenance_status: str = "UNKNOWN"
    quote_status: str = "BLOCKED"


def quote_proof(quote: Dict[str, Any], now: Optional[datetime] = None) -> Dict[str, Any]:
    """Validate broker evidence without inventing a price or source timestamp."""
    now = now or datetime.now(timezone.utc)
    source = str(quote.get("source") or "UNKNOWN").lower()
    stamp = str(quote.get("source_timestamp") or quote.get("source_observed_at") or "")
    reasons = []
    age = None
    try:
        observed = datetime.fromisoformat(stamp.replace('Z', '+00:00'))
        if observed.tzinfo is None:
            raise ValueError('timezone required')
        age = (now - observed).total_seconds() * 1000
        if not 0 <= age <= 60000:
            reasons.append('SOURCE_QUOTE_STALE_OR_FUTURE')
    except (ValueError, TypeError):
        reasons.append('SOURCE_TIMESTAMP_NOT_PROVEN')
    provenance = str(quote.get('provenance_status') or quote.get('verification_status') or 'UNKNOWN')
    if source not in {'dhan', 'dhan_option_chain_live'} or provenance != 'VERIFIED_DHAN':
        reasons.append('BROKER_PROVENANCE_NOT_PROVEN')
    values = tuple(as_float(quote.get(k)) for k in ('ltp', 'bid', 'ask'))
    if any(v is None or not math.isfinite(v) or v <= 0 for v in values):
        reasons.append('COMPLETE_POSITIVE_QUOTE_REQUIRED')
    elif values[2] < values[1]:
        reasons.append('CROSSED_QUOTE')
    if values == (125.0, 124.5, 125.5):
        reasons.append('KNOWN_SYNTHETIC_QUOTE_PATTERN')
    from core.utils.nse_holidays import HOLIDAYS_BY_YEAR, is_trading_day
    ist = now.astimezone(timezone(timedelta(hours=5, minutes=30)))
    regular = ist.year in HOLIDAYS_BY_YEAR and is_trading_day(ist.date())[0] and (9,15) <= (ist.hour,ist.minute) < (15,30)
    session = str(quote.get('market_session') or 'UNKNOWN')
    if not regular or session not in {'OPEN', 'LIVE_MARKET'}:
        reasons.append('MARKET_SESSION_NOT_OPEN')
    for key in ('security_id', 'trading_symbol', 'expiry', 'strike', 'option_type'):
        if not quote.get(key):
            reasons.append(key.upper() + '_NOT_PROVEN')
    try:
        if datetime.fromisoformat(str(quote.get('expiry'))[:10]).date() < ist.date():
            reasons.append('CONTRACT_EXPIRED')
    except ValueError:
        reasons.append('EXPIRY_INVALID')
    return dict(source=source, source_timestamp=stamp, freshness_ms=age,
                observed_at=str(quote.get('observed_at') or ''), market_session=session,
                provenance_status=provenance, quote_status='BLOCKED' if reasons else 'PASS',
                reasons=reasons)


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


def extract_signals_from_state(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    signals: List[Dict[str, Any]] = []
    for d in iter_dicts(state):
        symbol = d.get("symbol") or d.get("underlying") or d.get("name")
        score = d.get("score") or d.get("display_score") or d.get("confidence") or d.get("rank_score")
        status = str(d.get("status") or d.get("signal") or d.get("reason") or "").upper()
        if symbol and (score is not None or "TRADE" in status or "SIGNAL" in status or "PREDICT" in status):
            signals.append(d)
    # Deduplicate by normalized symbol while preserving first occurrence.
    out: List[Dict[str, Any]] = []
    seen = set()
    for s in signals:
        sym = norm_symbol(s.get("symbol") or s.get("underlying") or s.get("name"))
        if sym and sym not in seen:
            seen.add(sym)
            out.append(s)
    return out[:50]


def load_state_signals(root: Path, api_base: Optional[str]) -> Tuple[List[Dict[str, Any]], str]:
    if api_base:
        base = api_base.rstrip("/")
        state = fetch_json(base + "/api/state")
        if isinstance(state, dict):
            sig = extract_signals_from_state(state)
            if sig:
                return sig, f"api:{base}/api/state"
        gain = fetch_json(base + "/api/gain_rank", timeout=45)
        if isinstance(gain, dict):
            preds = (gain.get("latest") or {}).get("predictions") or gain.get("predictions") or []
            if isinstance(preds, list) and preds:
                mapped = []
                for p in preds[:20]:
                    if not isinstance(p, dict):
                        continue
                    mapped.append(
                        {
                            "symbol": p.get("underlying") or p.get("symbol"),
                            "underlying": p.get("underlying") or p.get("symbol"),
                            "score": p.get("gain_score") or p.get("confidence"),
                            "option_type": p.get("option_type"),
                            "strike": p.get("strike"),
                            "expiry": p.get("expiry") or p.get("expiry_date"),
                            "instrument_token": p.get("instrument_token") or p.get("security_id"),
                        }
                    )
                if mapped:
                    return mapped, f"api:{base}/api/gain_rank"
        scanner = fetch_json(base + "/api/scanner/top_contract_gainers", timeout=30)
        if isinstance(scanner, dict):
            items = scanner.get("gainers") or scanner.get("contracts") or scanner.get("items") or []
            if isinstance(items, list) and items:
                return items[:20], f"api:{base}/api/scanner/top_contract_gainers"
    candidates = [
        root / "state" / "gain_rank_history.json",
        root / "state" / "market_cache.json",
        root / "outputs" / "ai_signals.json",
        root / "outputs" / "signals.json",
        root / "reports" / "latest" / "gain_rank.json",
    ]
    for p in candidates:
        data = safe_json_file(p)
        if data is not None:
            sig = extract_signals_from_state(data if isinstance(data, dict) else {"items": data})
            if sig:
                return sig, str(p.relative_to(root))
    return [], "NO_SIGNAL_SOURCE"


def collect_option_master(root: Path) -> Tuple[Dict[str, List[Dict[str, str]]], str]:
    candidates = [
        root / "security_id_list.csv",
        root / "data" / "security_id_list.csv",
        root / "state" / "security_id_list.csv",
        root / "instruments.csv",
        root / "data" / "instruments.csv",
    ]
    rows_by_underlying: Dict[str, List[Dict[str, str]]] = {}
    used = "not-found"
    for p in candidates:
        if not p.exists():
            continue
        try:
            with p.open("r", encoding="utf-8", errors="replace", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    blob = " ".join(str(v) for v in row.values()).upper()
                    if not any(x in blob for x in ["OPT", "CE", "PE", "CALL", "PUT"]):
                        continue
                    underlying = ""
                    for idx in ["BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "BANKEX", "SENSEX", "NIFTY"]:
                        if idx in blob:
                            underlying = idx
                            break
                    if not underlying:
                        underlying = norm_symbol(
                            row.get("UNDERLYING_SYMBOL")
                            or row.get("underlying")
                            or row.get("SEM_CUSTOM_SYMBOL")
                            or row.get("SEM_TRADING_SYMBOL")
                            or row.get("symbol")
                            or row.get("SYMBOL_NAME")
                            or ""
                        )
                    if underlying:
                        rows_by_underlying.setdefault(underlying, []).append({str(k): str(v) for k, v in row.items()})
            used = str(p.relative_to(root))
            if rows_by_underlying:
                break
        except Exception:
            continue
    return rows_by_underlying, used


def infer_symbol_type(underlying: str) -> str:
    if underlying in INDEX_UNDERLYINGS:
        return "INDEX"
    if underlying:
        return "EQUITY"
    return "UNKNOWN"


def infer_option_side(signal: Dict[str, Any]) -> str:
    blob = " ".join(str(v) for v in signal.values()).upper()
    if "PUT" in blob or " PE" in blob or "_PE" in blob or "DOWN" in blob or "SHORT" in blob or "SELL" in blob:
        return "PE"
    if "CALL" in blob or " CE" in blob or "_CE" in blob or "UP" in blob or "LONG" in blob or "BUY" in blob:
        return "CE"
    return "UNKNOWN"


def pick_contract(
    rows: List[Dict[str, str]], option_side: str
) -> Tuple[str, str, str, Optional[float], Optional[float], Optional[float]]:
    if not rows:
        return "", "", "", None, None, None
    side_rows = []
    for r in rows:
        blob = " ".join(r.values()).upper()
        if option_side in {"CE", "PE"} and option_side not in blob and ("CALL" not in blob if option_side == "CE" else "PUT" not in blob):
            continue
        side_rows.append(r)
    if not side_rows or option_side not in {'CE', 'PE'}:
        return "", "", "", None, None, None
    selected = side_rows[0]
    expiry = (
        selected.get("SEM_EXPIRY_DATE")
        or selected.get("EXPIRY_DATE")
        or selected.get("expiry")
        or selected.get("SM_EXPIRY_DATE")
        or ""
    )
    strike = (
        selected.get("SEM_STRIKE_PRICE")
        or selected.get("STRIKE_PRICE")
        or selected.get("strike")
        or selected.get("SM_STRIKE_PRICE")
        or ""
    )
    token = (
        selected.get("SEM_SMST_SECURITY_ID")
        or selected.get("SECURITY_ID")
        or selected.get("security_id")
        or selected.get("token")
        or selected.get("instrument_token")
        or ""
    )
    ltp = as_float(selected.get("LTP") or selected.get("ltp") or selected.get("last_price"))
    bid = as_float(selected.get("BID") or selected.get("bid") or selected.get("best_bid"))
    ask = as_float(selected.get("ASK") or selected.get("ask") or selected.get("best_ask"))
    return str(expiry), str(strike), str(token), ltp, bid, ask


def make_rows(
    signals: List[Dict[str, Any]], master: Dict[str, List[Dict[str, str]]], master_source: str, signal_source: str
) -> List[VisibilityRow]:
    rows: List[VisibilityRow] = []
    for s in signals:
        underlying = norm_symbol(s.get("symbol") or s.get("underlying") or s.get("name"))
        score = as_float(s.get("score") or s.get("display_score") or s.get("confidence") or s.get("rank_score"))
        option_side = infer_option_side(s)
        symbol_type = infer_symbol_type(underlying)
        contracts = master.get(underlying, [])
        option_eligible = bool(contracts)
        expiry, strike, token, ltp, bid, ask = pick_contract(contracts, option_side)
        spread_pct = None
        if bid is not None and ask is not None and bid > 0 and ask >= bid:
            mid = (bid + ask) / 2
            spread_pct = ((ask - bid) / mid) * 100 if mid else None
        liquidity = "UNKNOWN"
        if spread_pct is not None:
            liquidity = "PASS" if spread_pct <= 5 else "WARN" if spread_pct <= 15 else "FAIL"
        blocker = []
        if not option_eligible:
            blocker.append("OPTION_ELIGIBILITY_NOT_PROVEN")
        if option_side == "UNKNOWN":
            blocker.append("CE_PE_SIDE_NOT_PROVEN")
        if not expiry:
            blocker.append("EXPIRY_NOT_FOUND")
        if not strike:
            blocker.append("STRIKE_NOT_FOUND")
        if not token:
            blocker.append("TOKEN_SECURITY_ID_NOT_FOUND")
        if ltp is None:
            blocker.append("LTP_NOT_AVAILABLE")
        if liquidity == "FAIL":
            blocker.append("SPREAD_LIQUIDITY_FAIL")
        # Instrument master identifies contracts; it does not prove live quotes.
        # Only the selected security's explicit quote may supply provenance.
        matching = next((r for r in contracts if str(r.get('security_id') or r.get('SEM_SMST_SECURITY_ID') or r.get('SECURITY_ID') or r.get('token') or r.get('instrument_token') or '') == token), {})
        evidence = dict(matching)
        evidence.update(security_id=token, expiry=expiry, strike=strike, option_type=option_side, ltp=ltp, bid=bid, ask=ask)
        proof = quote_proof(evidence)
        blocker.extend(proof.pop('reasons'))
        if liquidity != 'PASS':
            blocker.append('LIQUIDITY_NOT_PROVEN')
        paper_allowed = not blocker
        rows.append(
            VisibilityRow(
                signal_ts_ist=str(s.get("ts") or s.get("timestamp") or s.get("time") or "UNKNOWN"),
                underlying=underlying or "UNKNOWN",
                symbol_type=symbol_type,
                signal_score=score,
                signal_side=str(s.get("signal") or s.get("status") or s.get("direction") or "UNKNOWN"),
                option_side=option_side,
                option_eligible=option_eligible,
                eligibility_source=master_source if option_eligible else f"NOT_FOUND_IN_{master_source}",
                expiry=expiry,
                strike=strike,
                instrument_token=token,
                ltp=ltp,
                bid=bid,
                ask=ask,
                spread_pct=spread_pct,
                liquidity_status=liquidity,
                paper_trade_allowed=paper_allowed,
                blocker_reason=";".join(blocker) if blocker else "PASS",
                trading_symbol=str(evidence.get('trading_symbol') or ''),
                **proof,
            )
        )
    if not rows:
        rows.append(
            VisibilityRow(
                signal_ts_ist="UNKNOWN",
                underlying="NO_SIGNAL_FOUND",
                symbol_type="UNKNOWN",
                signal_score=None,
                signal_side="UNKNOWN",
                option_side="UNKNOWN",
                option_eligible=False,
                eligibility_source=signal_source,
                expiry="",
                strike="",
                instrument_token="",
                ltp=None,
                bid=None,
                ask=None,
                spread_pct=None,
                liquidity_status="UNKNOWN",
                paper_trade_allowed=False,
                blocker_reason="NO_SIGNAL_SOURCE_FOUND_OR_NO_SIGNAL_ROWS",
            )
        )
    return rows


def write_reports(root: Path, rows: List[VisibilityRow], signal_source: str, master_source: str) -> None:
    reports = root / "reports" / "latest"
    reports.mkdir(parents=True, exist_ok=True)
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "signal_source": signal_source,
        "option_master_source": master_source,
        "rows": len(rows),
        "paper_trade_allowed_count": sum(1 for r in rows if r.paper_trade_allowed),
        "blocked_count": sum(1 for r in rows if not r.paper_trade_allowed),
    }
    data = {"summary": summary, "rows": [asdict(r) for r in rows]}
    (reports / "option_strike_visibility.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    lines = [
        "# System3 Option Strike Visibility Audit",
        "",
        f"Generated UTC: `{summary['generated_at_utc']}`",
        "",
        "## Summary",
        "",
        f"- **Signal source**: `{signal_source}`",
        f"- **Option master source**: `{master_source}`",
        f"- **Rows**: `{summary['rows']}`",
        f"- **Paper trade allowed**: `{summary['paper_trade_allowed_count']}`",
        f"- **Blocked**: `{summary['blocked_count']}`",
        "",
        "## Visibility Rows",
        "",
        "| Underlying | Type | Score | CE/PE | Eligible | Expiry | Strike | Token | LTP | Spread % | Paper Allowed | Blocker Reason |",
        "|---|---|---:|---|---:|---|---|---|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| `{r.underlying}` | `{r.symbol_type}` | `{r.signal_score}` | `{r.option_side}` | `{r.option_eligible}` | `{r.expiry}` | `{r.strike}` | `{r.instrument_token}` | `{r.ltp}` | `{r.spread_pct}` | `{r.paper_trade_allowed}` | `{r.blocker_reason}` |"
        )
    lines.extend(
        [
            "",
            "## Verdict Rule",
            "",
            "No row is paper-trade-ready unless option eligibility, expiry, strike, token/security id, quote, and liquidity assumptions are proven.",
        ]
    )
    (reports / "option_strike_visibility.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="System3 option strike visibility audit")
    parser.add_argument("--root", default=None)
    parser.add_argument("--api-base", default=os.environ.get("SYSTEM3_API_BASE"))
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else repo_root_from_script()
    signals, signal_source = load_state_signals(root, args.api_base)
    master, master_source = collect_option_master(root)
    rows = make_rows(signals, master, master_source, signal_source)
    write_reports(root, rows, signal_source, master_source)
    print("SYSTEM3_OPTION_VISIBILITY_AUDIT_COMPLETE")
    print(
        json.dumps({"rows": len(rows), "signal_source": signal_source, "option_master_source": master_source}, indent=2)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
