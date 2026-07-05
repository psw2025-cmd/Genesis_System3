#!/usr/bin/env python3
"""Model-to-trade gap proof — links prediction accuracy to paper trade profitability."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "model_to_trade_gap"


def _read(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _spearman_days(root: Path) -> List[Dict[str, Any]]:
    mv = root / "state" / "market_validations"
    days: List[Dict[str, Any]] = []
    if not mv.exists():
        return days
    for p in sorted(mv.glob("*.json")):
        d = _read(p)
        if not d:
            continue
        rho = d.get("rank_correlation_spearman") or d.get("spearman_correlation")
        if rho is None:
            continue
        days.append({"date": d.get("date"), "rho": float(rho), "hit_rate": d.get("hit_rate")})
    return days


def build_report(root: Path = ROOT) -> Dict[str, Any]:
    friction = _read(root / "reports" / "latest" / "friction_expectancy" / "summary.json") or {}
    fev = friction.get("evidence") or {}
    days = _spearman_days(root)
    avg_hit = None
    hits = [d["hit_rate"] for d in days if d.get("hit_rate") is not None]
    if hits:
        avg_hit = sum(float(h) for h in hits) / len(hits)
    win_rate = fev.get("win_rate")
    expectancy = fev.get("net_expectancy_after_costs")
    trade_count = fev.get("trade_count") or 0

    gap_notes: List[str] = []
    if avg_hit is not None and win_rate is not None:
        gap = float(win_rate) - float(avg_hit)
        gap_notes.append(f"win_rate_minus_hit_rate={gap:.4f}")
    if expectancy is not None and float(expectancy) <= 0:
        gap_notes.append("negative_net_expectancy_after_costs")

    pass_gate = (
        trade_count >= 5
        and win_rate is not None
        and float(win_rate) >= 0.45
        and expectancy is not None
        and float(expectancy) > 0
        and avg_hit is not None
        and float(avg_hit) >= 0.40
    )

    return {
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "pass": pass_gate,
        "evidence": {
            "validation_days": len(days),
            "avg_prediction_hit_rate": round(avg_hit, 4) if avg_hit is not None else None,
            "paper_trade_win_rate": win_rate,
            "paper_trade_count": trade_count,
            "net_expectancy_after_costs": expectancy,
            "gap_notes": gap_notes,
            "note": "PASS requires prediction hit_rate≥0.40, trade win_rate≥0.45, positive expectancy, ≥5 trades",
        },
        "auto_action": "Improve ranker (auto_retrain) and paper entry filters until gap closes",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = build_report()
    (OUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (OUT / "summary.md").write_text(
        f"# Model-to-Trade Gap\n\nPass: **{report['pass']}**\n\n{json.dumps(report['evidence'], indent=2)}\n",
        encoding="utf-8",
    )
    print(json.dumps({"pass": report["pass"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
