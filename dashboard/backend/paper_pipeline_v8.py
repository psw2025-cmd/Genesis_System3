"""System3 Core Pipeline V8 — analyzer/paper ledger.

Paper-only pipeline. It never imports or calls broker place/modify/cancel paths.
It converts prediction/ranking artifacts into forecast rows and writes PAPER
ledgers only when a usable real Dhan option quote exists.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

INDEX_OPTION_UNDERLYINGS = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"}
BLOCK_FORECAST_ONLY_CASH = "FORECAST_ONLY_CASH_EQUITY"
BLOCK_NO_OPTION_CONTRACT = "NO_VALID_OPTION_CONTRACT"
BLOCK_NO_LIVE_QUOTE = "NO_LIVE_OPTION_QUOTE"
BLOCK_STALE_FORECAST = "STALE_OR_MISSING_FORECAST"


# ---------------------------------------------------------------------------
# Basic file helpers
# ---------------------------------------------------------------------------
def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ist_event_time(utc_timestamp: str) -> str:
    """Convert an immutable UTC event time to timezone-aware India time."""
    from zoneinfo import ZoneInfo

    parsed = datetime.fromisoformat(utc_timestamp.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("PAPER_EVENT_TIMESTAMP_MISSING_TIMEZONE")
    return parsed.astimezone(ZoneInfo("Asia/Kolkata")).isoformat()


def _today_ist() -> str:
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
    except Exception:
        return datetime.utcnow().strftime("%Y-%m-%d")


def _read_json(path: Path, default: Any = None) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _append_jsonl_once(path: Path, row: Dict[str, Any], key: str) -> bool:
    """Fail closed on corrupt ledgers, never silently append to unreadable history."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if key not in row or row[key] is None or str(row[key]) == "":
        raise ValueError("PAPER_LEDGER_MISSING_ID")
    existing = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)  # Corrupt history must stop paper writes.
            if not isinstance(item, dict) or key not in item:
                raise ValueError("PAPER_LEDGER_INVALID_HISTORY")
            existing.add(str(item[key]))
    if str(row[key]) in existing:
        return False
    serialized = json.dumps(row, default=str, allow_nan=False)
    with path.open("a", encoding="utf-8") as f:
        f.write(serialized + "\n")
    return True


def _read_jsonl(path: Path, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Never turn corrupt paper-trade evidence into a misleading empty ledger."""
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"PAPER_LEDGER_CORRUPT:{path.name}:line_{line_number}") from exc
        if not isinstance(item, dict):
            raise ValueError(f"PAPER_LEDGER_INVALID_ROW:{path.name}:line_{line_number}")
        rows.append(item)
    return rows[-limit:] if limit else rows


def _row_id(*parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _pipeline_paths(root: Path) -> Dict[str, Path]:
    base = root / "state" / "paper_pipeline_v8"
    return {
        "base": base,
        "forecast": base / "equity_forecast_ledger.jsonl",
        "orders": base / "paper_order_ledger.jsonl",
        "blocked": base / "blocked_trade_ledger.jsonl",
        "status": base / "status.json",
        "positions": root / "src" / "outputs" / "positions_live.json",
        "pnl_summary": root / "src" / "outputs" / "paper_pnl_summary.json",
        "pnl_csv": root / "src" / "outputs" / "paper_pnl.csv",
    }


# ---------------------------------------------------------------------------
# Prediction normalization
# ---------------------------------------------------------------------------
def _candidate_lists(obj: Any) -> Iterable[Any]:
    if obj is None:
        return []
    if isinstance(obj, list):
        return obj
    if not isinstance(obj, dict):
        return []
    keys = ["rankings", "predictions", "top5", "top", "candidates", "signals", "latest", "data"]
    for k in keys:
        v = obj.get(k)
        if isinstance(v, list):
            return v
        if isinstance(v, dict):
            nested = list(_candidate_lists(v))
            if nested:
                return nested
    return []


def _load_latest_gain_rank(root: Path) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]], str]:
    paths = [
        root / "state" / "gain_rank_history.json",
        root / "src" / "outputs" / "gain_rank_history.json",
        root / "outputs" / "gain_rank_history.json",
    ]
    for p in paths:
        data = _read_json(p)
        if data is None:
            continue
        latest = data[-1] if isinstance(data, list) and data else data if isinstance(data, dict) else None
        if latest:
            raw_items = list(_candidate_lists(latest))
            items = [_normalize_prediction(x) for x in raw_items]
            items = [x for x in items if x.get("underlying")]
            return latest, items, str(p)
    return None, [], "missing"


def _normalize_prediction(item: Any) -> Dict[str, Any]:
    if not isinstance(item, dict):
        return {}
    underlying = item.get("underlying") or item.get("symbol") or item.get("ticker") or item.get("name") or item.get("scrip") or ""
    underlying = str(underlying).upper().replace(".NS", "").replace("NSE:", "").strip()
    side_raw = str(item.get("signal_type") or item.get("side") or item.get("direction") or item.get("action") or "").upper()
    if "PUT" in side_raw or side_raw == "PE" or side_raw == "SELL":
        option_side = "PE"
    elif "CALL" in side_raw or side_raw == "CE" or side_raw == "BUY":
        option_side = "CE"
    else:
        option_side = "CE"
    score = item.get("display_score", item.get("score", item.get("confidence", item.get("gate_score", 0))))
    try:
        score = float(str(score).replace("%", ""))
        if score > 1.0:
            score = score / 100.0
    except Exception:
        score = 0.0
    spot = item.get("spot") or item.get("spot_price") or item.get("ltp") or item.get("price")
    try:
        spot = float(spot) if spot is not None else None
    except Exception:
        spot = None
    return {"underlying": underlying, "option_side": option_side, "confidence": score, "spot": spot, "raw": item}


# ---------------------------------------------------------------------------
# Instrument and quote selection
# ---------------------------------------------------------------------------
def _load_instruments_df():
    try:
        from core.data.instruments_cache import get_instruments_df

        return get_instruments_df()
    except Exception:
        return None


def _instrument_master_status(df: Any) -> Dict[str, Any]:
    try:
        if df is None or getattr(df, "empty", True):
            return {"status": "missing", "rows": 0}
        return {"status": "ok", "rows": int(len(df)), "columns": list(df.columns)[:30]}
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:200]}


def _select_option_contract(df: Any, underlying: str, side: str, spot: Optional[float]) -> Tuple[Optional[Dict[str, Any]], str]:
    if df is None or getattr(df, "empty", True):
        return None, "INSTRUMENT_MASTER_MISSING"
    try:
        work = df.copy()
        if "name" in work.columns:
            work = work[work["name"].astype(str).str.upper() == underlying.upper()]
        elif "symbol" in work.columns:
            work = work[work["symbol"].astype(str).str.upper().str.contains(underlying.upper(), na=False)]
        if work.empty:
            return None, BLOCK_NO_OPTION_CONTRACT if underlying.upper() in INDEX_OPTION_UNDERLYINGS else BLOCK_FORECAST_ONLY_CASH
        if "instrumenttype" in work.columns:
            work = work[work["instrumenttype"].astype(str).str.upper().str.contains("OPT", na=False)]
        if work.empty:
            return None, BLOCK_NO_OPTION_CONTRACT if underlying.upper() in INDEX_OPTION_UNDERLYINGS else BLOCK_FORECAST_ONLY_CASH
        if "symbol" in work.columns:
            side_filtered = work[work["symbol"].astype(str).str.upper().str.contains(side.upper(), na=False)]
            if not side_filtered.empty:
                work = side_filtered
        if "expiry" in work.columns:
            work = work.sort_values("expiry")
        if spot is not None and "strike" in work.columns:
            work = work.assign(_dist=(work["strike"].astype(float) - float(spot)).abs()).sort_values(["expiry", "_dist"] if "expiry" in work.columns else ["_dist"])
        return work.iloc[0].to_dict(), "OK"
    except Exception as exc:
        return None, f"OPTION_SELECT_ERROR:{str(exc)[:120]}"


def _is_real_dhan_chain_payload(data: Dict[str, Any]) -> bool:
    if not isinstance(data, dict):
        return False
    if bool(data.get("stale")):
        return False
    status = str(data.get("status") or "").upper()
    if any(bad in status for bad in ("STALE", "FALLBACK", "SYNTHETIC", "CSV")):
        return False
    data_source = str(data.get("data_source") or data.get("source") or "").lower()
    source_priority = str(data.get("source_priority") or "").lower()
    combined = f"{data_source} {source_priority}"
    if any(bad in combined for bad in ("csv", "fallback", "synthetic", "bhavcopy", "yahoo", "nse")):
        return False
    if data_source != "dhan":
        return False
    if status in ("MARKET_CLOSED", "CLOSED", "NO_DATA", "ERROR", "NOT_VERIFIED"):
        return False
    return True


def _contract_has_dhan_source(contract: Dict[str, Any]) -> bool:
    source = str(contract.get("source") or contract.get("data_source") or contract.get("quote_source") or "").lower()
    return source == "dhan"


def _load_chain_quote(root: Path, underlying: str, side: str, spot: Optional[float]) -> Tuple[Optional[Dict[str, Any]], str]:
    candidates = [
        root / "src" / "outputs" / f"chain_{underlying.upper()}.json",
        root / "outputs" / f"chain_{underlying.upper()}.json",
        root / "state" / f"chain_{underlying.upper()}.json",
    ]
    for p in candidates:
        data = _read_json(p)
        if not _is_real_dhan_chain_payload(data):
            continue
        contracts = data.get("contracts") or []
        if not isinstance(contracts, list) or not contracts:
            continue
        rows = []
        for c in contracts:
            if not isinstance(c, dict) or not _contract_has_dhan_source(c):
                continue
            opt_type = str(c.get("option_type") or c.get("side") or c.get("type") or c.get("instrument_type") or c.get("symbol") or "").upper()
            if side.upper() not in opt_type:
                continue
            ltp = c.get("ltp") or c.get("last_price") or c.get("price") or c.get("lastTradedPrice")
            try:
                ltp_f = float(ltp)
            except Exception:
                continue
            if not math.isfinite(ltp_f) or ltp_f <= 0:
                continue
            strike = c.get("strike") or c.get("strike_price")
            try:
                strike_f = float(strike) if strike is not None else None
            except Exception:
                strike_f = None
            if strike_f is not None and not math.isfinite(strike_f):
                continue
            rows.append((abs((strike_f or (spot or 0)) - (spot or (strike_f or 0))), c, ltp_f))
        if rows:
            rows.sort(key=lambda x: x[0])
            c = dict(rows[0][1])
            c["ltp"] = rows[0][2]
            c["quote_source_file"] = str(p)
            c["chain_data_source"] = data.get("data_source") or "dhan"
            c["chain_stale"] = False
            c["chain_source_priority"] = data.get("source_priority")
            return c, "OK"
    return None, BLOCK_NO_LIVE_QUOTE


def _safe_market_open() -> bool:
    try:
        from utils.market_hours import is_market_open

        open_now, _reason = is_market_open()
        return bool(open_now)
    except Exception:
        return False


def _paper_qty(contract: Dict[str, Any]) -> int:
    for k in ("lotsize", "lot_size", "lotSize", "SEM_LOT_UNITS"):
        try:
            v = int(float(contract.get(k)))
            if v > 0:
                return v
        except Exception:
            pass
    return 1


# ---------------------------------------------------------------------------
# Paper ledger write path
# ---------------------------------------------------------------------------
def _update_positions_and_pnl(root: Path, order: Dict[str, Any]) -> None:
    paths = _pipeline_paths(root)
    pos_file = paths["positions"]
    current = _read_json(pos_file, {"positions": [], "open_count": 0})
    positions = current.get("positions", []) if isinstance(current, dict) else []
    if not any(p.get("position_id") == order["position_id"] for p in positions):
        positions.append({
            "position_id": order["position_id"],
            "paper_order_id": order["paper_order_id"],
            "underlying": order["underlying"],
            "symbol": order["contract_symbol"],
            "qty": order["qty"],
            "entry_price": order["entry_price"],
            "current_price": order["entry_price"],
            "unrealized_pnl": 0.0,
            "status": "PAPER_OPEN",
            "entry_time": order["created_utc"],
            "entry_time_ist": order["created_ist"],
            "signal_source": "core_pipeline_v8",
            "provenance": "ANALYZER_PAPER_ONLY_NO_BROKER_ORDER_REAL_DHAN_QUOTE",
        })
    _write_json(pos_file, {"positions": positions, "open_count": len(positions), "timestamp": _utc_now(), "source": "core_pipeline_v8"})
    # Opening a PAPER position must not erase previously realized trade history.
    # When no independent close ledger exists, unknown results stay unknown.
    prior = _read_json(paths["pnl_summary"], {})
    prior = prior if isinstance(prior, dict) else {}
    realized_keys = ("total_trades", "winning_trades", "losing_trades",
                     "win_rate", "total_realized_pnl")
    summary = {key: prior.get(key) for key in realized_keys}
    summary.update({
        "total_unrealized_pnl": None,
        "total_pnl": None,
        "open_positions": sum(1 for p in positions if p.get("status") == "PAPER_OPEN"),
        "source": "core_pipeline_v8",
        "verification_status": "NOT_VERIFIED",
        "reason_if_unverified": "No independently reconciled closing fills or mark-to-market prices",
    })
    _write_json(paths["pnl_summary"], summary)
    paths["pnl_csv"].parent.mkdir(parents=True, exist_ok=True)
    if not paths["pnl_csv"].exists():
        with paths["pnl_csv"].open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["timestamp", "total_trades", "winning_trades", "losing_trades", "win_rate", "total_realized_pnl", "total_unrealized_pnl", "total_pnl", "open_positions"])
            w.writeheader()
            w.writerow({"timestamp": _utc_now(), **{k: summary[k] for k in w.fieldnames if k != "timestamp"}})


def run_pipeline_once(root: Path | str, outputs_dir: Optional[Path | str] = None, create_paper_orders: bool = True, source: str = "manual", max_candidates: int = 10) -> Dict[str, Any]:
    root = Path(root)
    paths = _pipeline_paths(root)
    paths["base"].mkdir(parents=True, exist_ok=True)
    latest, predictions, prediction_source = _load_latest_gain_rank(root)
    today = _today_ist()
    latest_date = str((latest or {}).get("date") or (latest or {}).get("trade_date") or "") if latest else ""
    fresh = bool(latest_date == today) if latest_date else False
    df = _load_instruments_df()
    instrument_status = _instrument_master_status(df)
    market_open = _safe_market_open()

    result: Dict[str, Any] = {
        "status": "ok",
        "pipeline": "core_pipeline_v8",
        "generated_utc": _utc_now(),
        "source": source,
        "market_open": market_open,
        "prediction_source": prediction_source,
        "latest_prediction_date": latest_date,
        "today_ist": today,
        "fresh_prediction": fresh,
        "instrument_master": instrument_status,
        "forecasts_seen": 0,
        "forecasts_written": 0,
        "paper_orders_written": 0,
        "blocked_written": 0,
        "blockers": [],
        "paper_orders": [],
    }

    if not predictions:
        result["status"] = "not_ready"
        result["blockers"].append(BLOCK_STALE_FORECAST)
        _write_json(paths["status"], result)
        return result

    for pred in predictions[:max_candidates]:
        underlying = pred.get("underlying")
        if not underlying:
            continue
        result["forecasts_seen"] += 1
        forecast_id = _row_id(today, underlying, pred.get("option_side"), prediction_source)
        forecast = {
            "forecast_id": forecast_id,
            "created_utc": _utc_now(),
            "trade_date": today,
            "underlying": underlying,
            "option_side": pred.get("option_side"),
            "confidence": pred.get("confidence"),
            "spot": pred.get("spot"),
            "horizons": ["1D", "5D", "10D", "20D"],
            "source": prediction_source,
            "raw": pred.get("raw"),
        }
        forecast["created_ist"] = _ist_event_time(forecast["created_utc"])
        if _append_jsonl_once(paths["forecast"], forecast, "forecast_id"):
            result["forecasts_written"] += 1

        # A forecast is still auditable outside trading hours, but must never
        # create a PAPER fill from yesterday's prediction or a closed market.
        if not fresh or not market_open:
            reason = BLOCK_STALE_FORECAST if not fresh else "MARKET_CLOSED_PAPER_ENTRY"
            blocked = {
                "block_id": _row_id(forecast_id, reason),
                "created_utc": _utc_now(),
                "forecast_id": forecast_id,
                "underlying": underlying,
                "reason": reason,
                "scope": "forecast_only_no_paper_entry",
            }
            if _append_jsonl_once(paths["blocked"], blocked, "block_id"):
                result["blocked_written"] += 1
            result["blockers"].append(blocked)
            continue

        contract, contract_status = _select_option_contract(df, underlying, pred.get("option_side") or "CE", pred.get("spot"))
        if not contract:
            blocked = {"block_id": _row_id(forecast_id, contract_status), "created_utc": _utc_now(), "forecast_id": forecast_id, "underlying": underlying, "reason": contract_status, "scope": "trade_only_forecast_kept"}
            if _append_jsonl_once(paths["blocked"], blocked, "block_id"):
                result["blocked_written"] += 1
            result["blockers"].append(blocked)
            continue

        quote, quote_status = _load_chain_quote(root, underlying, pred.get("option_side") or "CE", pred.get("spot"))
        if not quote:
            blocked = {"block_id": _row_id(forecast_id, quote_status), "created_utc": _utc_now(), "forecast_id": forecast_id, "underlying": underlying, "reason": quote_status, "contract_symbol": contract.get("symbol"), "scope": "trade_only_forecast_kept"}
            if _append_jsonl_once(paths["blocked"], blocked, "block_id"):
                result["blocked_written"] += 1
            result["blockers"].append(blocked)
            continue

        if not create_paper_orders:
            continue

        entry_price = float(quote.get("ltp") or 0)
        if entry_price <= 0:
            continue
        # Enforce capital on the ACTUAL paper pipeline, not only the toy simulator.
        # Fail closed on malformed configuration or invalid lot size.
        qty = _paper_qty(contract)
        try:
            capital_limit = float(os.environ.get("TRADING_CAPITAL_LIMIT_INR", "50000"))
        except (ValueError, TypeError):
            capital_limit = float("nan")
        order_value = entry_price * qty
        # A new order must fit alongside all existing open PAPER positions.
        # Corrupt position evidence must never be interpreted as zero exposure.
        try:
            if paths["positions"].exists():
                saved_positions = json.loads(paths["positions"].read_text(encoding="utf-8"))
                if not isinstance(saved_positions, dict) or not isinstance(saved_positions.get("positions"), list):
                    raise ValueError("PAPER_POSITIONS_INVALID")
                existing_positions = saved_positions["positions"]
            else:
                existing_positions = []
            open_exposure = 0.0
            for position in existing_positions:
                if not isinstance(position, dict):
                    raise ValueError("PAPER_POSITION_INVALID_ROW")
                if position.get("status") != "PAPER_OPEN":
                    continue
                held_qty = float(position["qty"])
                held_price = float(position["entry_price"])
                held_value = held_qty * held_price
                if (not math.isfinite(held_value) or held_qty <= 0
                        or held_price <= 0):
                    raise ValueError("PAPER_POSITION_INVALID_VALUE")
                open_exposure += held_value
            if not math.isfinite(open_exposure):
                raise ValueError("PAPER_EXPOSURE_INVALID")
        except (OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
            reason = "PAPER_EXPOSURE_UNVERIFIED"
            blocked = {"block_id": _row_id(forecast_id, reason),
                       "created_utc": _utc_now(), "forecast_id": forecast_id,
                       "underlying": underlying, "reason": reason,
                       "scope": "trade_only_forecast_kept"}
            if _append_jsonl_once(paths["blocked"], blocked, "block_id"):
                result["blocked_written"] += 1
            result["blockers"].append(blocked)
            continue
        if (not math.isfinite(capital_limit) or capital_limit <= 0
                or not isinstance(qty, (int, float))
                or not math.isfinite(float(qty)) or qty <= 0
                or not math.isfinite(order_value) or order_value + open_exposure > capital_limit):
            reason = "PAPER_CAPITAL_LIMIT_BLOCK"
            blocked = {"block_id": _row_id(forecast_id, reason),
                       "created_utc": _utc_now(), "forecast_id": forecast_id,
                       "underlying": underlying, "reason": reason,
                       "scope": "trade_only_forecast_kept"}
            if _append_jsonl_once(paths["blocked"], blocked, "block_id"):
                result["blocked_written"] += 1
            result["blockers"].append(blocked)
            continue
        paper_order_id = _row_id("PAPER", today, underlying, pred.get("option_side"), contract.get("symbol"), entry_price)
        order = {
            "paper_order_id": paper_order_id,
            "position_id": f"PV8-{paper_order_id[:12]}",
            "created_utc": _utc_now(),
            "trade_date": today,
            "forecast_id": forecast_id,
            "underlying": underlying,
            "option_side": pred.get("option_side"),
            "contract_symbol": contract.get("symbol") or quote.get("symbol") or underlying,
            "token": contract.get("token"),
            "expiry": contract.get("expiry"),
            "strike": contract.get("strike"),
            "qty": qty,
            "entry_price": entry_price,
            "status": "PAPER_OPEN",
            "order_mode": "ANALYZER_PAPER_ONLY_NO_BROKER_ORDER",
            "quote_source": quote.get("quote_source_file"),
            "quote_data_source": quote.get("chain_data_source"),
            "quote_source_priority": quote.get("chain_source_priority"),
            "source": "core_pipeline_v8",
        }
        order["created_ist"] = _ist_event_time(order["created_utc"])
        if _append_jsonl_once(paths["orders"], order, "paper_order_id"):
            result["paper_orders_written"] += 1
            result["paper_orders"].append(order)
            _update_positions_and_pnl(root, order)

    if result["paper_orders_written"]:
        result["status"] = "paper_orders_created"
    elif result["forecasts_seen"]:
        result["status"] = "forecast_only_or_blocked"
    _write_json(paths["status"], result)
    return result


def build_pipeline_status(root: Path | str, outputs_dir: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(root)
    paths = _pipeline_paths(root)
    status = _read_json(paths["status"], {})
    try:
        forecasts_all = _read_jsonl(paths["forecast"])
        orders_all = _read_jsonl(paths["orders"])
        blocked_all = _read_jsonl(paths["blocked"])
    except ValueError as exc:
        return {
            "status": "NOT_VERIFIED",
            "pipeline": "core_pipeline_v8",
            "generated_utc": _utc_now(),
            "verification_status": "NOT_VERIFIED",
            "ledger_integrity": "FAIL",
            "reason_if_unverified": str(exc),
            "ledger_counts": None,
            "recent_forecasts": [],
            "recent_paper_orders": [],
            "recent_blockers": [],
            "safety": {"broker_real_order_path": "not_used_by_core_pipeline_v8"},
            "next_action": "Quarantine and repair the corrupt paper ledger with audit evidence before resuming writes.",
        }
    forecasts = forecasts_all[-20:]
    orders = orders_all[-20:]
    blocked = blocked_all[-20:]
    validation_dir = root / "state" / "market_validations"
    validation_files = sorted(validation_dir.glob("market_validation_*.json")) if validation_dir.exists() else []
    return {
        "status": status.get("status", "not_ready"),
        "pipeline": "core_pipeline_v8",
        "generated_utc": _utc_now(),
        "safety": {
            "live_trading_enabled": os.environ.get("LIVE_TRADING_ENABLED", "0"),
            "system3_live_trading_allowed": os.environ.get("SYSTEM3_LIVE_TRADING_ALLOWED", "0"),
            "analyze_mode": os.environ.get("ANALYZE_MODE", "1"),
            "broker_real_order_path": "not_used_by_core_pipeline_v8",
        },
        "latest_run": status,
        "ledger_counts": {"forecasts": len(forecasts_all), "paper_orders": len(orders_all), "blocked_trades": len(blocked_all), "validation_days": len(validation_files)},
        "recent_forecasts": forecasts,
        "recent_paper_orders": orders,
        "recent_blockers": blocked,
        "next_action": "If forecasts exist but paper_orders=0, inspect recent_blockers. NO_LIVE_OPTION_QUOTE means the prediction is kept but no paper trade is allowed without a real Dhan option quote.",
    }


def run_self_test(proof_dir: Path | str) -> Dict[str, Any]:
    """Execute isolated PAPER safety probes, not pre-filled PASS assertions.

    This is a structural/offline self-test, NOT 30-day historical replay proof.
    """
    import tempfile

    proof_dir = Path(proof_dir)
    proof_dir.mkdir(parents=True, exist_ok=True)
    checks = []
    with tempfile.TemporaryDirectory(prefix="system3_paper_selftest_") as temp:
        root = Path(temp)
        try:
            contract, reason = _select_option_contract(None, "CASH_ONLY", "CE", 100)
            checks.append({"name": "missing_instrument_blocks_trade",
                           "passed": contract is None and reason == "INSTRUMENT_MASTER_MISSING",
                           "detail": reason})
        except Exception as exc:
            checks.append({"name": "missing_instrument_blocks_trade", "passed": False,
                           "detail": type(exc).__name__})
        try:
            quote, reason = _load_chain_quote(root, "NIFTY", "CE", 25000)
            checks.append({"name": "missing_dhan_quote_blocks_trade",
                           "passed": quote is None and reason == BLOCK_NO_LIVE_QUOTE,
                           "detail": reason})
        except Exception as exc:
            checks.append({"name": "missing_dhan_quote_blocks_trade", "passed": False,
                           "detail": type(exc).__name__})
        try:
            ledger = root / "paper_orders.jsonl"
            first = _append_jsonl_once(ledger, {"paper_order_id": "probe-1"}, "paper_order_id")
            duplicate = _append_jsonl_once(ledger, {"paper_order_id": "probe-1"}, "paper_order_id")
            checks.append({"name": "paper_ledger_idempotent",
                           "passed": first is True and duplicate is False and len(_read_jsonl(ledger)) == 1,
                           "detail": "Isolated temporary ledger; no production writes"})
        except Exception as exc:
            checks.append({"name": "paper_ledger_idempotent", "passed": False,
                           "detail": type(exc).__name__})

    gates = ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED",
             "LIVE_ORDER_AUTHORITY", "REAL_BROKER_ORDERS",
             "AUTO_EXECUTE_TRADES", "USE_LIVE_EXECUTION_ENGINE")
    unsafe = [name for name in gates if os.environ.get(name, "0").lower() not in ("0", "false", "")]
    checks.append({"name": "live_execution_environment_disabled",
                   "passed": not unsafe,
                   "detail": "All inspected execution flags disabled" if not unsafe else
                   "Unsafe environment flags: " + ",".join(unsafe)})

    passed = all(c["passed"] for c in checks)
    result = {
        "status": "PASS" if passed else "FAIL",
        "scope": "ISOLATED_OFFLINE_STRUCTURAL_ONLY",
        "full_market_replay_verified": False,
        "production_ui_verified": False,
        "model_training_verified": False,
        "real_broker_orders": 0,
        "checks": checks,
        "generated_utc": _utc_now(),
    }
    _write_json(proof_dir / "selftest.json", result)
    md = ["# Core Pipeline V8 Isolated Self-Test", "",
          f"Status: **{result['status']}** (offline checks only)", "",
          "Not proof of a 30-day historical replay, browser UI, or live market feed.",
          "", "| Check | Result | Detail |", "|---|---:|---|"]
    for c in checks:
        md.append(f"| {c['name']} | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |")
    (proof_dir / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return result
