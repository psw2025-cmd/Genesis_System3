#!/usr/bin/env python3
"""
Friction-adjusted expectancy proof from paper trade ledger.

Outputs:
  reports/latest/friction_expectancy/summary.json
  reports/latest/friction_expectancy/summary.md
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "friction_expectancy"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from costed_walkforward_proof import compute_cost  # noqa: E402

CLOUD = os.environ.get(
    "SYSTEM3_API_BASE",
    "https://genesis-system3-backend.onrender.com",
).rstrip("/")

TRADE_SOURCES = [
    ROOT / "tests" / "fixtures" / "paper_closed_trades_feb2026.json",
    ROOT / "storage" / "live" / "paper_closed_trades.json",
    ROOT / "outputs" / "paper_closed_trades.json",
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _fetch_cloud_trades() -> List[Dict[str, Any]]:
    try:
        with urllib.request.urlopen(f"{CLOUD}/api/paper", timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
        trades = data.get("closed_trades") or data.get("trade_history") or data.get("trades") or []
        if isinstance(trades, list) and trades:
            return trades
    except Exception:
        pass
    return []


def _load_trades() -> tuple[List[Dict[str, Any]], str]:
    for path in TRADE_SOURCES:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            trades = data.get("trades") if isinstance(data, dict) else data
            if isinstance(trades, list) and trades:
                return trades, str(path.relative_to(ROOT))
        except Exception:
            continue
    cloud = _fetch_cloud_trades()
    if cloud:
        return cloud, f"api:{CLOUD}/api/paper"
    return [], "none"


def _cost_trade(t: Dict[str, Any]) -> Dict[str, Any]:
    underlying = str(t.get("underlying") or t.get("symbol") or "NIFTY").upper()
    entry = float(t.get("entry_price") or 0)
    exit_p = float(t.get("exit_price") or 0)
    qty = int(t.get("qty") or t.get("quantity") or 50)
    gross = float(t.get("realized_pnl") or (exit_p - entry) * qty)
    costs = compute_cost(entry, exit_p, underlying, qty)
    if t.get("realized_pnl") is not None and costs.get("gross_pnl") is not None:
        # Align gross with ledger when present
        gross = float(t["realized_pnl"])
        net = gross - float(costs.get("total_costs") or 0)
        costs["net_pnl"] = round(net, 2)
    return {
        "position_id": t.get("position_id") or t.get("trade_id"),
        "underlying": underlying,
        "trading_symbol": t.get("trading_symbol"),
        "gross_pnl": gross,
        "net_pnl": costs.get("net_pnl"),
        "total_costs": costs.get("total_costs"),
        "costs_detail": costs,
    }


def build_report() -> Dict[str, Any]:
    trades, source = _load_trades()
    rows = [_cost_trade(t) for t in trades]
    net_pnls = [float(r["net_pnl"]) for r in rows if r.get("net_pnl") is not None]
    gross_pnls = [float(r["gross_pnl"]) for r in rows if r.get("gross_pnl") is not None]
    wins = sum(1 for x in net_pnls if x > 0)
    trade_count = len(net_pnls)
    net_total = sum(net_pnls) if net_pnls else 0.0
    expectancy = (net_total / trade_count) if trade_count else None
    win_rate = (wins / trade_count) if trade_count else None
    pass_gate = trade_count >= 5 and expectancy is not None and expectancy > 0
    return {
        "generated_utc": _utc(),
        "pass": pass_gate,
        "source": source,
        "evidence": {
            "trade_count": trade_count,
            "wins": wins,
            "losses": trade_count - wins,
            "win_rate": round(win_rate, 4) if win_rate is not None else None,
            "gross_pnl_total": round(sum(gross_pnls), 2) if gross_pnls else None,
            "net_pnl_total": round(net_total, 2),
            "net_expectancy_after_costs": round(expectancy, 2) if expectancy is not None else None,
            "min_trades_required": 5,
            "note": (
                "PASS requires >=5 closed paper trades with positive per-trade net expectancy after "
                "brokerage, STT, exchange, GST, slippage (Dhan cost model)."
            ),
        },
        "trades": rows[:50],
        "blocker_if_fail": "POSITIVE_NET_EXPECTANCY_AFTER_COSTS",
        "auto_action_on_fail": "Accumulate more winning paper sessions or tune strategy; re-run after market-day trades",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = build_report()
    (OUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    ev = report["evidence"]
    md = [
        "# Friction Expectancy Proof",
        "",
        f"Generated: `{report['generated_utc']}`",
        f"Pass: **{report['pass']}**",
        f"Source: `{report['source']}`",
        "",
        f"- Trades: `{ev['trade_count']}`",
        f"- Win rate: `{ev['win_rate']}`",
        f"- Net expectancy/trade: `{ev['net_expectancy_after_costs']}` INR",
        f"- Net PnL total: `{ev['net_pnl_total']}` INR",
    ]
    (OUT / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("SYSTEM3_FRICTION_EXPECTANCY_COMPLETE")
    print(json.dumps({"pass": report["pass"], "expectancy": ev.get("net_expectancy_after_costs")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
