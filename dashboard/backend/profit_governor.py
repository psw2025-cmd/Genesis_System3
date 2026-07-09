"""Dhan-only paper profit governor.

Purpose:
- Select the best paper-trade candidate from real Dhan option quotes only.
- Block stale/non-Dhan/synthetic/CSV candidates.
- Use outcome history to prefer symbols/sides with positive out-of-sample expectancy.
- Produce deterministic entry/exit levels for the paper ledger.

This module does not place, modify, cancel, or route broker orders.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

BLOCK_NO_DHAN_QUOTE = "NO_REAL_DHAN_QUOTE"
BLOCK_EXPECTANCY = "EXPECTANCY_NOT_POSITIVE"
BLOCK_ACCURACY = "ACCURACY_GATE_NOT_MET"
BLOCK_LIQUIDITY = "LIQUIDITY_GATE_NOT_MET"
BLOCK_SPREAD = "SPREAD_TOO_WIDE"


@dataclass
class ProfitDecision:
    status: str
    selected: Optional[Dict[str, Any]]
    blocked: List[Dict[str, Any]]
    generated_utc: str
    gates: Dict[str, Any]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _f(x: Any, default: float = 0.0) -> float:
    try:
        if x in (None, "", "--"):
            return default
        return float(x)
    except Exception:
        return default


def _truthy_dhan_quote(row: Dict[str, Any]) -> bool:
    source = str(row.get("data_source") or row.get("source") or row.get("quote_data_source") or "").lower()
    priority = str(row.get("source_priority") or row.get("quote_source_priority") or "").lower()
    status = str(row.get("status") or "").upper()
    combined = f"{source} {priority} {status}"
    if any(bad in combined for bad in ("csv", "synthetic", "fallback", "stale", "bhavcopy", "yahoo", "mock", "fake")):
        return False
    if bool(row.get("stale")) or bool(row.get("chain_stale")):
        return False
    if "dhan" not in combined:
        return False
    return _f(row.get("ltp") or row.get("entry_price") or row.get("last_price")) > 0


def _key(symbol: str, side: str) -> str:
    return f"{str(symbol).upper()}::{str(side).upper()}"


def summarize_outcomes(rows: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """Build per symbol/side paper outcome statistics.

    Expected row fields: symbol/underlying, option_side, pnl_pct or pnl.
    """
    buckets: Dict[str, List[float]] = {}
    for r in rows:
        sym = str(r.get("underlying") or r.get("symbol") or "").upper()
        side = str(r.get("option_side") or r.get("side") or "").upper()
        if not sym or not side:
            continue
        pnl = r.get("pnl_pct")
        if pnl is None:
            pnl = r.get("return_pct")
        if pnl is None:
            pnl = r.get("pnl")
        value = _f(pnl, math.nan)
        if math.isnan(value):
            continue
        buckets.setdefault(_key(sym, side), []).append(value)

    stats: Dict[str, Dict[str, float]] = {}
    for k, vals in buckets.items():
        wins = [v for v in vals if v > 0]
        losses = [abs(v) for v in vals if v <= 0]
        hit_rate = len(wins) / len(vals) if vals else 0.0
        avg_win = sum(wins) / len(wins) if wins else 0.0
        avg_loss = sum(losses) / len(losses) if losses else 0.0
        expectancy = hit_rate * avg_win - (1 - hit_rate) * avg_loss
        stats[k] = {
            "samples": float(len(vals)),
            "hit_rate": hit_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "expectancy": expectancy,
        }
    return stats


def score_candidate(row: Dict[str, Any], history_stats: Dict[str, Dict[str, float]], gates: Dict[str, Any]) -> Tuple[float, Optional[str]]:
    if not _truthy_dhan_quote(row):
        return -1e9, BLOCK_NO_DHAN_QUOTE

    sym = str(row.get("underlying") or row.get("symbol") or "").upper()
    side = str(row.get("option_side") or row.get("option_type") or row.get("side") or "").upper()
    stats = history_stats.get(_key(sym, side), {})

    samples = int(stats.get("samples", 0))
    hit_rate = float(stats.get("hit_rate", gates.get("cold_start_hit_rate", 0.50)))
    expectancy = float(stats.get("expectancy", row.get("expected_move_pct") or row.get("expectancy") or 0.0))
    confidence = _f(row.get("confidence") or row.get("score") or row.get("display_score"))
    if confidence > 1.0:
        confidence = confidence / 100.0
    liquidity = _f(row.get("oi")) * 0.6 + _f(row.get("volume")) * 0.4
    bid = _f(row.get("top_bid_price") or row.get("bid"))
    ask = _f(row.get("top_ask_price") or row.get("ask"))
    ltp = _f(row.get("ltp") or row.get("entry_price") or row.get("last_price"))
    spread_pct = ((ask - bid) / ltp * 100.0) if ask > 0 and bid > 0 and ltp > 0 else 0.0

    if samples >= int(gates.get("min_samples", 10)) and hit_rate < float(gates.get("min_hit_rate", 0.55)):
        return -1e9, BLOCK_ACCURACY
    if expectancy <= float(gates.get("min_expectancy", 0.0)):
        return -1e9, BLOCK_EXPECTANCY
    if liquidity < float(gates.get("min_liquidity", 1.0)):
        return -1e9, BLOCK_LIQUIDITY
    if spread_pct > float(gates.get("max_spread_pct", 8.0)):
        return -1e9, BLOCK_SPREAD

    # Conservative score: expectancy dominates, then confidence, hit rate, liquidity.
    score = expectancy * 100.0 + confidence * 20.0 + hit_rate * 10.0 + math.log1p(max(liquidity, 0.0))
    return score, None


def entry_exit_plan(row: Dict[str, Any], gates: Dict[str, Any]) -> Dict[str, Any]:
    entry = _f(row.get("ltp") or row.get("entry_price") or row.get("last_price"))
    sl_pct = float(gates.get("stop_loss_pct", 0.22))
    tp_pct = float(gates.get("target_profit_pct", 0.35))
    trail_trigger_pct = float(gates.get("trail_trigger_pct", 0.25))
    trail_lock_pct = float(gates.get("trail_lock_pct", 0.15))
    return {
        "entry_price": entry,
        "stop_loss": round(entry * (1 - sl_pct), 2),
        "target": round(entry * (1 + tp_pct), 2),
        "trail_trigger": round(entry * (1 + trail_trigger_pct), 2),
        "trail_stop_after_trigger": round(entry * (1 + trail_lock_pct), 2),
        "max_hold_minutes": int(gates.get("max_hold_minutes", 45)),
        "exit_priority": ["hard_stop_loss", "target_or_trailing_profit", "time_exit", "market_close_exit"],
    }


def select_best_paper_trade(candidates: List[Dict[str, Any]], outcome_rows: List[Dict[str, Any]], gates: Optional[Dict[str, Any]] = None) -> ProfitDecision:
    gates = {
        "min_samples": 10,
        "min_hit_rate": 0.55,
        "cold_start_hit_rate": 0.50,
        "min_expectancy": 0.01,
        "min_liquidity": 1.0,
        "max_spread_pct": 8.0,
        "stop_loss_pct": 0.22,
        "target_profit_pct": 0.35,
        "trail_trigger_pct": 0.25,
        "trail_lock_pct": 0.15,
        "max_hold_minutes": 45,
        **(gates or {}),
    }
    history_stats = summarize_outcomes(outcome_rows)
    blocked: List[Dict[str, Any]] = []
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for row in candidates:
        score, reason = score_candidate(row, history_stats, gates)
        if reason:
            blocked.append({"underlying": row.get("underlying") or row.get("symbol"), "option_side": row.get("option_side") or row.get("option_type"), "reason": reason})
            continue
        candidate = dict(row)
        candidate["profit_score"] = round(score, 6)
        candidate["entry_exit"] = entry_exit_plan(candidate, gates)
        scored.append((score, candidate))

    if not scored:
        return ProfitDecision("BLOCKED", None, blocked, _now(), gates)
    scored.sort(key=lambda x: x[0], reverse=True)
    return ProfitDecision("SELECTED", scored[0][1], blocked, _now(), gates)


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


def run_profit_governor(root: Path | str) -> Dict[str, Any]:
    root = Path(root)
    base = root / "state" / "paper_pipeline_v8"
    paper_orders = read_jsonl(base / "paper_order_ledger.jsonl")
    candidates_path = root / "src" / "outputs" / "paper_trade_candidates.json"
    candidates = []
    if candidates_path.exists():
        obj = json.loads(candidates_path.read_text(encoding="utf-8"))
        candidates = obj.get("candidates", obj if isinstance(obj, list) else [])
    decision = select_best_paper_trade(candidates, paper_orders)
    out = asdict(decision)
    target = root / "reports" / "latest" / "profit_governor_decision.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    return out
