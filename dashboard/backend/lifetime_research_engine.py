"""Lifetime research engine for System3 paper/analyzer automation.

This engine is deliberately non-order-routing. It performs historical and
walk-forward evaluation, promotes a paper-only champion only when gates pass,
and writes proof artifacts. It never places broker orders and never claims live
readiness without out-of-sample evidence.
"""
from __future__ import annotations

import csv
import json
import math
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


DEFAULT_POLICY: Dict[str, Any] = {
    "min_train_rows": 30,
    "min_test_rows": 10,
    "min_walk_forward_windows": 3,
    "min_hit_rate": 0.55,
    "min_profit_factor": 1.15,
    "min_expectancy": 0.01,
    "max_drawdown_pct": 0.20,
    "min_avg_trade_return": 0.002,
    "paper_only": True,
    "live_trading_enabled_required_value": "0",
}


@dataclass
class OutcomeRow:
    ts: str
    symbol: str
    side: str
    strategy: str
    return_pct: float
    source: str


@dataclass
class CandidateMetrics:
    strategy: str
    symbol: str
    side: str
    samples: int
    hit_rate: float
    avg_return: float
    expectancy: float
    profit_factor: float
    max_drawdown_pct: float
    passed: bool
    blockers: List[str]


@dataclass
class ResearchDecision:
    status: str
    champion: Optional[Dict[str, Any]]
    candidates: List[Dict[str, Any]]
    blockers: List[str]
    generated_utc: str
    policy: Dict[str, Any]
    safety: Dict[str, Any]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _f(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, "", "--"):
            return default
        return float(value)
    except Exception:
        return default


def _norm(value: Any) -> str:
    return str(value or "").strip().upper()


def _safe_json(path: Path) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None
    return None


def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                rows.append(obj)
        except Exception:
            continue
    return rows


def _iter_csv(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open(newline="", encoding="utf-8", errors="replace") as f:
            return [dict(r) for r in csv.DictReader(f)]
    except Exception:
        return []


def _row_from_any(row: Dict[str, Any], source: str) -> Optional[OutcomeRow]:
    symbol = _norm(row.get("underlying") or row.get("symbol") or row.get("scrip") or row.get("name"))
    side = _norm(row.get("option_side") or row.get("side") or row.get("option_type") or row.get("direction"))
    strategy = _norm(row.get("strategy") or row.get("source") or row.get("signal_source") or "SYSTEM3")
    ts = str(row.get("created_utc") or row.get("timestamp") or row.get("ts") or row.get("trade_date") or "")
    ret = row.get("return_pct")
    if ret is None:
        ret = row.get("pnl_pct")
    if ret is None:
        pnl = row.get("pnl") or row.get("realized_pnl") or row.get("unrealized_pnl")
        entry = row.get("entry_price") or row.get("capital") or row.get("notional")
        pnl_f = _f(pnl, math.nan)
        entry_f = abs(_f(entry, math.nan))
        ret = pnl_f / entry_f if entry_f and not math.isnan(pnl_f) else None
    ret_f = _f(ret, math.nan)
    if not symbol or not side or math.isnan(ret_f):
        return None
    if side in {"CALL", "BUY", "LONG", "UP"}:
        side = "CE"
    elif side in {"PUT", "SELL", "SHORT", "DOWN"}:
        side = "PE"
    return OutcomeRow(ts=ts, symbol=symbol, side=side, strategy=strategy, return_pct=ret_f, source=source)


def load_outcomes(root: Path | str) -> List[OutcomeRow]:
    """Load historical outcomes from local repo artifacts only."""
    root = Path(root)
    raw_rows: List[Tuple[Dict[str, Any], str]] = []
    candidates = [
        root / "state" / "paper_pipeline_v8" / "paper_order_ledger.jsonl",
        root / "state" / "paper_pipeline_v8" / "closed_paper_trade_ledger.jsonl",
        root / "src" / "outputs" / "paper_pnl.csv",
        root / "outputs" / "paper_pnl.csv",
    ]
    for p in candidates:
        if p.suffix.lower() == ".jsonl":
            raw_rows.extend((r, str(p.relative_to(root))) for r in _iter_jsonl(p))
        elif p.suffix.lower() == ".csv":
            raw_rows.extend((r, str(p.relative_to(root))) for r in _iter_csv(p))

    mv = root / "state" / "market_validations"
    if mv.exists():
        for p in sorted(mv.glob("*.json")):
            obj = _safe_json(p)
            if isinstance(obj, dict):
                for key in ("rows", "predicted", "predicted_ranking", "actual", "actual_ranking", "trades"):
                    vals = obj.get(key)
                    if isinstance(vals, list):
                        raw_rows.extend((x, str(p.relative_to(root))) for x in vals if isinstance(x, dict))
            elif isinstance(obj, list):
                raw_rows.extend((x, str(p.relative_to(root))) for x in obj if isinstance(x, dict))

    out: List[OutcomeRow] = []
    for r, src in raw_rows:
        row = _row_from_any(r, src)
        if row is not None:
            out.append(row)
    out.sort(key=lambda r: r.ts)
    return out


def max_drawdown(returns: Sequence[float]) -> float:
    equity = 1.0
    peak = 1.0
    max_dd = 0.0
    for r in returns:
        equity *= 1.0 + r
        peak = max(peak, equity)
        if peak > 0:
            max_dd = max(max_dd, (peak - equity) / peak)
    return max_dd


def compute_metrics(rows: Sequence[OutcomeRow], policy: Optional[Dict[str, Any]] = None) -> CandidateMetrics:
    policy = {**DEFAULT_POLICY, **(policy or {})}
    if not rows:
        return CandidateMetrics("UNKNOWN", "UNKNOWN", "UNKNOWN", 0, 0.0, 0.0, 0.0, 0.0, 0.0, False, ["NO_ROWS"])
    rets = [r.return_pct for r in rows]
    wins = [r for r in rets if r > 0]
    losses = [abs(r) for r in rets if r <= 0]
    hit_rate = len(wins) / len(rets) if rets else 0.0
    avg_win = mean(wins) if wins else 0.0
    avg_loss = mean(losses) if losses else 0.0
    expectancy = hit_rate * avg_win - (1 - hit_rate) * avg_loss
    gross_profit = sum(wins)
    gross_loss = sum(losses)
    pf = gross_profit / gross_loss if gross_loss > 0 else (999.0 if gross_profit > 0 else 0.0)
    dd = max_drawdown(rets)
    avg_return = mean(rets)
    blockers = []
    if len(rets) < int(policy["min_test_rows"]):
        blockers.append("INSUFFICIENT_TEST_ROWS")
    if hit_rate < float(policy["min_hit_rate"]):
        blockers.append("HIT_RATE_BELOW_GATE")
    if pf < float(policy["min_profit_factor"]):
        blockers.append("PROFIT_FACTOR_BELOW_GATE")
    if expectancy < float(policy["min_expectancy"]):
        blockers.append("EXPECTANCY_BELOW_GATE")
    if dd > float(policy["max_drawdown_pct"]):
        blockers.append("DRAWDOWN_ABOVE_GATE")
    if avg_return < float(policy["min_avg_trade_return"]):
        blockers.append("AVG_RETURN_BELOW_GATE")
    return CandidateMetrics(
        strategy=rows[0].strategy,
        symbol=rows[0].symbol,
        side=rows[0].side,
        samples=len(rets),
        hit_rate=hit_rate,
        avg_return=avg_return,
        expectancy=expectancy,
        profit_factor=pf,
        max_drawdown_pct=dd,
        passed=not blockers,
        blockers=blockers,
    )


def group_rows(rows: Sequence[OutcomeRow]) -> Dict[str, List[OutcomeRow]]:
    grouped: Dict[str, List[OutcomeRow]] = {}
    for r in rows:
        grouped.setdefault(f"{r.strategy}::{r.symbol}::{r.side}", []).append(r)
    return grouped


def walk_forward_windows(rows: Sequence[OutcomeRow], train_size: int, test_size: int) -> List[Tuple[List[OutcomeRow], List[OutcomeRow]]]:
    windows: List[Tuple[List[OutcomeRow], List[OutcomeRow]]] = []
    i = 0
    ordered = list(rows)
    while i + train_size + test_size <= len(ordered):
        train = ordered[i : i + train_size]
        test = ordered[i + train_size : i + train_size + test_size]
        if train and test:
            # Leakage guard: every test row must be after train row in the sorted sequence.
            windows.append((train, test))
        i += test_size
    return windows


def evaluate_walk_forward(rows: Sequence[OutcomeRow], policy: Optional[Dict[str, Any]] = None) -> List[CandidateMetrics]:
    policy = {**DEFAULT_POLICY, **(policy or {})}
    metrics: List[CandidateMetrics] = []
    for _key, bucket in group_rows(rows).items():
        wins = walk_forward_windows(bucket, int(policy["min_train_rows"]), int(policy["min_test_rows"]))
        if len(wins) < int(policy["min_walk_forward_windows"]):
            m = compute_metrics(bucket[-int(policy["min_test_rows"]):], policy)
            m.passed = False
            if "INSUFFICIENT_WALK_FORWARD_WINDOWS" not in m.blockers:
                m.blockers.append("INSUFFICIENT_WALK_FORWARD_WINDOWS")
            metrics.append(m)
            continue
        test_rows: List[OutcomeRow] = []
        for _train, test in wins:
            test_rows.extend(test)
        metrics.append(compute_metrics(test_rows, policy))
    return metrics


def safety_state() -> Dict[str, Any]:
    return {
        "live_trading_enabled": os.environ.get("LIVE_TRADING_ENABLED", "0"),
        "system3_live_trading_allowed": os.environ.get("SYSTEM3_LIVE_TRADING_ALLOWED", "0"),
        "analyze_mode": os.environ.get("ANALYZE_MODE", "1"),
        "paper_only_research_engine": True,
        "broker_order_path_used": False,
    }


def select_champion(metrics: Sequence[CandidateMetrics], policy: Optional[Dict[str, Any]] = None) -> ResearchDecision:
    policy = {**DEFAULT_POLICY, **(policy or {})}
    safety = safety_state()
    blockers: List[str] = []
    if str(safety["live_trading_enabled"]) != str(policy["live_trading_enabled_required_value"]):
        blockers.append("LIVE_TRADING_ENV_NOT_SAFE_FOR_RESEARCH")
    passed = [m for m in metrics if m.passed]
    if not passed:
        blockers.append("NO_CHAMPION_PASSED_WALK_FORWARD_GATES")
        return ResearchDecision("BLOCKED", None, [asdict(m) for m in metrics], blockers, _now(), policy, safety)
    passed.sort(key=lambda m: (m.expectancy, m.profit_factor, m.hit_rate, -m.max_drawdown_pct), reverse=True)
    champ = asdict(passed[0])
    return ResearchDecision("CHAMPION_SELECTED" if not blockers else "BLOCKED", champ if not blockers else None, [asdict(m) for m in metrics], blockers, _now(), policy, safety)


def run_lifetime_research(root: Path | str, policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    root = Path(root)
    policy_path = root / "config" / "lifetime_research_policy.json"
    file_policy = _safe_json(policy_path) if policy_path.exists() else None
    merged_policy = {**DEFAULT_POLICY, **(file_policy if isinstance(file_policy, dict) else {}), **(policy or {})}
    outcomes = load_outcomes(root)
    metrics = evaluate_walk_forward(outcomes, merged_policy)
    decision = select_champion(metrics, merged_policy)
    out = asdict(decision)
    out["outcome_rows_loaded"] = len(outcomes)
    out_dir = root / "reports" / "latest" / "lifetime_research_engine"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    lines = [
        "# Lifetime Research Engine",
        "",
        f"Status: **{out['status']}**",
        f"Generated UTC: `{out['generated_utc']}`",
        f"Outcome rows loaded: `{out['outcome_rows_loaded']}`",
        "",
        "## Champion",
        "",
        "```json",
        json.dumps(out.get("champion"), indent=2, default=str),
        "```",
        "",
        "## Blockers",
        "",
        *[f"- `{b}`" for b in out.get("blockers", [])],
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
