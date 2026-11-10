"""Build /api/accuracy_trend from the same Spearman series as auto_gates.

Uses scripts.system3_gate_evaluator.load_spearman_days so local market_validations
and durable Firestore validation_day docs stay contract-aligned. Never fabricates
rho values or weakens ML gate thresholds.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def _enrich_from_local_validation(root: Path, day: str) -> Dict[str, Any]:
    path = root / "state" / "market_validations" / f"market_validation_{day}.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    out: Dict[str, Any] = {}
    if data.get("predicted_ranking") is not None:
        out["predicted"] = data.get("predicted_ranking")
    if data.get("actual_ranking") is not None:
        out["actual"] = data.get("actual_ranking")
    if data.get("status") is not None:
        out["status"] = data.get("status")
    if data.get("hit_rate") is not None and "hit_rate" not in out:
        out["hit_rate"] = data.get("hit_rate")
    return out


def build_accuracy_trend_payload(
    root: Path,
    *,
    retrain_needed: bool = False,
) -> Dict[str, Any]:
    """Return accuracy_trend payload aligned with gate evaluator Spearman days."""
    try:
        from scripts.system3_gate_evaluator import load_spearman_days
    except ImportError:
        return {
            "status": "error",
            "error": "gate_evaluator_unavailable",
            "trend": [],
            "avg_rho": None,
            "retrain_needed": retrain_needed,
            "days_available": 0,
            "source": "unavailable",
        }

    days, _passing, _latest = load_spearman_days(root)
    trend: List[Dict[str, Any]] = []
    for d in days:
        if not isinstance(d, dict):
            continue
        day = str(d.get("date") or "").strip()
        row: Dict[str, Any] = {
            "date": day,
            "rho": d.get("rho"),
            "hit_rate": d.get("hit_rate"),
            "status": d.get("status") or ("PASS" if d.get("pass") else "COLLECTING"),
            "predicted": [],
            "actual": [],
            "pass_threshold": bool(d.get("pass")),
        }
        row.update(_enrich_from_local_validation(root, day))
        trend.append(row)

    rhos = [float(e["rho"]) for e in trend if e.get("rho") is not None]
    avg_rho: Optional[float] = round(sum(rhos) / len(rhos), 4) if rhos else None
    return {
        "status": "ok" if trend else "no_data",
        "trend": trend,
        "avg_rho": avg_rho,
        "retrain_needed": retrain_needed,
        "days_available": len(trend),
        "source": "load_spearman_days",
        "aligned_with": "auto_gates.ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS",
    }
