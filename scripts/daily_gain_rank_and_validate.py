"""
Daily Gain Rank + Market Validation Runner
==========================================

Dhan-only analyzer job. It must never scrape NSE, read CSV fallback as live,
or create synthetic market rows. If verified Dhan rows are unavailable, it writes
an explicit BLOCKED proof instead of crashing or pretending the model is trained.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.data.datasource_manager import get_datasource_manager
from src.ranking.gain_rank_engine import GainRankEngine
from src.ranking.ml_signal_aggregator import load_ml_confidence
from src.validation.market_result_validator import MarketResultValidator

ENABLED_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
STATE_DIR = Path(ROOT_DIR) / "state"
REPORT_DIR = Path(ROOT_DIR) / "reports" / "latest" / "daily_gain_rank_and_validate"
OI_CACHE_FILE = STATE_DIR / "dhan_oi_cache.json"


def _now() -> str:
    return datetime.now().isoformat()


def _write_status(status: str, reason: str, extra: dict | None = None) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": _now(),
        "status": status,
        "reason": reason,
        "source": "dhan_only_no_fallback",
        "enabled_underlyings": ENABLED_UNDERLYINGS,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
    if extra:
        payload.update(extra)
    (REPORT_DIR / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    (REPORT_DIR / "summary.md").write_text(
        "\n".join([
            "# Daily Gain Rank + Validation",
            "",
            f"- Generated: `{payload['generated_at']}`",
            f"- Status: **{payload['status']}**",
            f"- Source: `{payload['source']}`",
            f"- Reason: {payload['reason']}",
            "- Live trading: `OFF`",
            "- Orders called: `false`",
        ]) + "\n",
        encoding="utf-8",
    )


def is_expiry_day(today: date | None = None) -> bool:
    """Conservative weekly-expiry guard for Indian index options."""
    d = today or date.today()
    return d.weekday() == 3


def load_oi_cache() -> Dict[str, int]:
    try:
        if OI_CACHE_FILE.exists():
            data = json.loads(OI_CACHE_FILE.read_text(encoding="utf-8"))
            return {str(k): int(v) for k, v in data.items() if int(v) > 0}
    except Exception:
        pass
    return {}


def save_oi_cache(snapshot: Dict[str, int]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = OI_CACHE_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, OI_CACHE_FILE)


def _oi_total(df: pd.DataFrame) -> int:
    col = next((c for c in df.columns if c.lower() == "oi" or ("oi" in c.lower() and "change" not in c.lower() and "prev" not in c.lower())), None)
    if not col:
        return 0
    try:
        return int(float(df[col].sum()))
    except Exception:
        return 0


def load_live_chain_data() -> Tuple[Dict[str, pd.DataFrame], Dict[str, float]]:
    """Load official Dhan option-chain rows only."""
    dsm = get_datasource_manager()
    all_data: Dict[str, pd.DataFrame] = {}
    spots: Dict[str, float] = {}
    blocked: Dict[str, str] = {}
    for idx, sym in enumerate(ENABLED_UNDERLYINGS):
        if idx:
            time.sleep(float(os.environ.get("DHAN_OPTION_CHAIN_SPACING_S", "3.25")))
        df, spot = dsm.fetch_option_chain(sym)
        if df is None or df.empty or float(spot or 0) <= 0:
            reason = dsm.last_error or "NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS"
            blocked[sym] = reason
            print(f"  {sym}: BLOCKED — {reason}")
            continue
        all_data[sym] = df
        spots[sym] = float(spot)
        print(f"  {sym}: Dhan official chain rows={len(df)} spot={float(spot):.2f}")
    if blocked:
        _write_status("PARTIAL" if all_data else "BLOCKED", "Some enabled Dhan chains unavailable", {"blocked_underlyings": blocked, "loaded_underlyings": sorted(all_data)})
    return all_data, spots


def run_ranking(top_n: int = 5) -> None:
    print(f"\n{'='*60}\n  DHAN-ONLY GAIN RANK — {_now()}\n{'='*60}")
    all_data, spots = load_live_chain_data()
    if not all_data:
        _write_status("BLOCKED", "No verified Dhan option-chain rows; ranking not generated")
        print("  BLOCKED: no verified Dhan rows")
        return

    if is_expiry_day():
        oi_history = {}
        print("  EXPIRY DAY: OI change disabled")
    else:
        prev = load_oi_cache()
        oi_history = {}
        for sym, df in all_data.items():
            curr = _oi_total(df)
            if prev.get(sym, 0) > 0 and curr > 0:
                oi_history[sym] = {"prev_oi": prev[sym], "curr_oi": curr}

    ml_confidence = load_ml_confidence()
    if not ml_confidence:
        print("  ML confidence missing: ranker runs with ML weight redistributed; model not proven trained")

    engine = GainRankEngine(top_n=top_n)
    ranked_df = engine.rank_all(all_data, spots, oi_history, ml_confidence=ml_confidence)
    if ranked_df.empty:
        _write_status("BLOCKED", "Rank engine produced no rows from verified Dhan chains")
        print("  BLOCKED: no ranked rows")
        return

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ranked_df.to_json(REPORT_DIR / "ranked.json", orient="records", indent=2)
    cols = [c for c in ["rank", "underlying", "gain_score", "ml_confidence_score", "oi_change_score", "expected_move_pct", "recommendation"] if c in ranked_df.columns]
    print(ranked_df[cols].to_string(index=False))
    _write_status("PASS", "Dhan-only ranking generated", {"ranked_rows": int(len(ranked_df)), "ranked_underlyings": ranked_df.get("underlying", pd.Series(dtype=str)).astype(str).tolist(), "ml_confidence_loaded": bool(ml_confidence)})


def run_validation() -> None:
    print(f"\n{'='*60}\n  MARKET RESULT VALIDATION — {_now()}\n{'='*60}")
    try:
        validator = MarketResultValidator()
        report = validator.run_daily_validation()
    except Exception as exc:
        _write_status("BLOCKED", f"Validation crashed: {type(exc).__name__}: {str(exc)[:200]}")
        print(f"  BLOCKED: validation crashed: {exc}")
        return
    if report.get("status") == "SKIPPED":
        _write_status("SKIPPED", str(report.get("reason") or "validation skipped"), {"validation": report})
        print(f"  Validation skipped: {report.get('reason')}")
        return
    _write_status("PASS", "Validation completed", {"validation": report})
    print(json.dumps(report, indent=2, default=str))


def run_trend() -> None:
    print(f"\n{'='*60}\n  ACCURACY TREND — {_now()}\n{'='*60}")
    try:
        validator = MarketResultValidator()
        trend = validator.get_accuracy_trend(last_n_days=14)
    except Exception as exc:
        _write_status("BLOCKED", f"Trend crashed: {type(exc).__name__}: {str(exc)[:200]}")
        print(f"  BLOCKED: trend crashed: {exc}")
        return
    _write_status("PASS" if trend else "SKIPPED", "Trend checked", {"trend": trend})
    print(json.dumps(trend, indent=2, default=str))


def run_post_market_pipeline() -> None:
    pipeline = os.path.join(ROOT_DIR, "scripts", "system3_post_market_auto_pipeline.py")
    if not os.path.isfile(pipeline):
        return
    try:
        import subprocess
        subprocess.run([sys.executable, pipeline], cwd=ROOT_DIR, timeout=900, check=False)
    except Exception as exc:
        print(f"  Post-market pipeline warning: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Dhan-only daily gain rank + validation")
    parser.add_argument("--mode", choices=["rank", "validate", "trend", "full"], default="full")
    parser.add_argument("--top-n", type=int, default=5)
    args = parser.parse_args()
    if args.mode in ("rank", "full"):
        run_ranking(top_n=args.top_n)
    if args.mode in ("validate", "full"):
        run_validation()
    if args.mode in ("trend", "full"):
        run_trend()
    if args.mode in ("validate", "trend", "full"):
        run_post_market_pipeline()


if __name__ == "__main__":
    main()
