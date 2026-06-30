"""
Daily Prediction-vs-Actual Benchmark — GitHub Issue #26
==========================================================
Reads real prediction history (state/gain_rank_history.json) and real
validation reports (state/market_validations/*.json) already produced by
daily_gain_rank_and_validate.py + MarketResultValidator, and reshapes them
into the exact deliverables Issue #26 requires:

  reports/latest/prediction_benchmark/
    prediction_vs_actual.csv   — every prediction vs market result
    top_mover_match.csv        — did System3 predict actual movers?
    missed_opportunities.md    — what profitable moves were missed
    benchmark_summary.md       — daily scorecard

This script does NOT invent or simulate data. If no validation report
exists for a date, that date is skipped with an explicit note — never
backfilled with synthetic numbers. Designed to run unattended via the
job scheduler at 15:45 IST on trading days (after daily_gain_validate).

Usage:
    python scripts/daily_prediction_benchmark.py
    python scripts/daily_prediction_benchmark.py --days 30
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, date
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

RANK_HISTORY_FILE = ROOT_DIR / "state" / "gain_rank_history.json"
VALIDATION_DIR = ROOT_DIR / "state" / "market_validations"
OUT_DIR = ROOT_DIR / "reports" / "latest" / "prediction_benchmark"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def load_all_validations() -> list:
    """Load every market_validation_*.json report, sorted by date."""
    if not VALIDATION_DIR.exists():
        return []
    reports = []
    for f in sorted(VALIDATION_DIR.glob("market_validation_*.json")):
        data = load_json(f, None)
        if data and "date" in data:
            reports.append(data)
    reports.sort(key=lambda r: r["date"])
    return reports


def load_predictions_by_date() -> dict:
    """state/gain_rank_history.json -> {date: [predictions]}."""
    history = load_json(RANK_HISTORY_FILE, [])
    if not isinstance(history, list):
        return {}
    out = {}
    for entry in history:
        d = entry.get("date")
        preds = entry.get("predictions", [])
        if d and preds:
            out[d] = preds
    return out


def write_prediction_vs_actual_csv(validations: list, predictions_by_date: dict) -> int:
    """One row per (date, underlying): predicted rank/score vs actual rank."""
    out_path = OUT_DIR / "prediction_vs_actual.csv"
    rows = []
    for v in validations:
        d = v["date"]
        preds = predictions_by_date.get(d, [])
        pred_rank_map = {p["underlying"]: p for p in preds}
        actual_details = v.get("actual_details", [])
        for ad in actual_details:
            sym = ad.get("underlying")
            p = pred_rank_map.get(sym, {})
            rows.append({
                "date": d,
                "underlying": sym,
                "predicted_rank": p.get("rank", ""),
                "predicted_gain_score": p.get("gain_score", ""),
                "predicted_expected_move_pct": p.get("expected_move_pct", ""),
                "predicted_recommendation": p.get("recommendation", ""),
                "actual_rank": ad.get("actual_rank", ""),
                "actual_gain_score": ad.get("combined_gain_score", ""),
                "spearman_rho_for_day": v.get("spearman_correlation", ""),
                "hit_rate_for_day": v.get("hit_rate", ""),
                "status_for_day": v.get("status", ""),
            })
    with out_path.open("w", newline="", encoding="utf-8") as f:
        cols = ["date", "underlying", "predicted_rank", "predicted_gain_score",
                "predicted_expected_move_pct", "predicted_recommendation",
                "actual_rank", "actual_gain_score", "spearman_rho_for_day",
                "hit_rate_for_day", "status_for_day"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def write_top_mover_match_csv(validations: list) -> int:
    """One row per day: did predicted top-N overlap with actual top-N movers?"""
    out_path = OUT_DIR / "top_mover_match.csv"
    rows = []
    for v in validations:
        predicted_top = v.get("predicted_ranking", [])
        actual_top = v.get("actual_ranking", [])
        top_n = v.get("top_n_evaluated", 3)
        predicted_set = set(predicted_top[:top_n])
        actual_set = set(actual_top[:top_n])
        matched = predicted_set & actual_set
        missed = actual_set - predicted_set
        rows.append({
            "date": v["date"],
            "top_n": top_n,
            "predicted_top": " | ".join(predicted_top[:top_n]),
            "actual_top": " | ".join(actual_top[:top_n]),
            "matched_symbols": " | ".join(sorted(matched)) or "NONE",
            "missed_symbols": " | ".join(sorted(missed)) or "NONE",
            "match_count": len(matched),
            "match_rate_pct": round(100 * len(matched) / top_n, 1) if top_n else 0,
        })
    with out_path.open("w", newline="", encoding="utf-8") as f:
        cols = ["date", "top_n", "predicted_top", "actual_top",
                "matched_symbols", "missed_symbols", "match_count", "match_rate_pct"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def write_missed_opportunities_md(validations: list) -> int:
    """Days where an actual top mover was NOT in the predicted top-N."""
    out_path = OUT_DIR / "missed_opportunities.md"
    lines = ["# Missed Opportunities — Daily Top-Mover Misses\n",
             f"_Generated {datetime.now().isoformat()}_\n",
             "Symbols that were actual top movers on a given day but were "
             "NOT in System3's predicted top-N ranking for that day.\n"]
    miss_count = 0
    for v in validations:
        top_n = v.get("top_n_evaluated", 3)
        predicted_set = set(v.get("predicted_ranking", [])[:top_n])
        actual_top = v.get("actual_ranking", [])[:top_n]
        missed = [s for s in actual_top if s not in predicted_set]
        if missed:
            miss_count += 1
            lines.append(f"\n## {v['date']}")
            lines.append(f"- Predicted top-{top_n}: {', '.join(v.get('predicted_ranking', [])[:top_n])}")
            lines.append(f"- Actual top-{top_n}: {', '.join(actual_top)}")
            lines.append(f"- **Missed**: {', '.join(missed)}")
            lines.append(f"- ρ for day: {v.get('spearman_correlation', 'N/A')}")
    if miss_count == 0:
        lines.append("\nNo missed top movers in the analyzed window.")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return miss_count


def write_benchmark_summary_md(validations: list, predictions_by_date: dict) -> dict:
    """Daily scorecard + rolling stats."""
    out_path = OUT_DIR / "benchmark_summary.md"

    if not validations:
        out_path.write_text(
            "# Prediction Benchmark Summary\n\n"
            f"_Generated {datetime.now().isoformat()}_\n\n"
            "**No validation reports found in state/market_validations/.**\n\n"
            "This means the daily validation job has not produced any "
            "results yet. Once `daily_gain_rank_and_validate.py --mode "
            "validate` runs on a trading day, this file will populate "
            "with real data. No synthetic numbers are shown.\n",
            encoding="utf-8",
        )
        return {"days": 0, "avg_rho": None}

    rhos = [v.get("spearman_correlation") for v in validations if v.get("spearman_correlation") is not None]
    hit_rates = [v.get("hit_rate") for v in validations if v.get("hit_rate") is not None]
    avg_rho = sum(rhos) / len(rhos) if rhos else None
    avg_hit = sum(hit_rates) / len(hit_rates) if hit_rates else None
    retrain_days = sum(1 for v in validations if v.get("retrain_signal"))

    lines = [
        "# Prediction Benchmark Summary — Issue #26 Proof",
        f"\n_Generated {datetime.now().isoformat()}_\n",
        f"- Trading days with validation data: **{len(validations)}**",
        f"- Date range: {validations[0]['date']} → {validations[-1]['date']}",
        f"- Average Spearman ρ: **{avg_rho:.3f}**" if avg_rho is not None else "- Average Spearman ρ: N/A",
        f"- Average hit rate: **{avg_hit:.1%}**" if avg_hit is not None else "- Average hit rate: N/A",
        f"- Days that fired a retrain signal: {retrain_days}/{len(validations)}",
        "\n## Daily Scorecard\n",
        "| Date | Predicted Top | Actual Top | Spearman ρ | Hit Rate | Status |",
        "|------|---------------|------------|------------|----------|--------|",
    ]
    for v in validations[-30:]:
        pred_top = " ".join(v.get("predicted_ranking", [])[:3])
        act_top = " ".join(v.get("actual_ranking", [])[:3])
        rho = v.get("spearman_correlation")
        hit = v.get("hit_rate")
        lines.append(
            f"| {v['date']} | {pred_top} | {act_top} | "
            f"{rho:.3f} | {hit:.1%} | {v.get('status', '--')} |"
        )

    lines.append(
        "\n## Readiness Gate (per master roadmap)\n"
        f"- Threshold: Spearman ρ ≥ 0.70 required for live-trading readiness\n"
        f"- Current average: {avg_rho:.3f}" if avg_rho is not None else "N/A"
    )
    lines.append(
        "- **Verdict**: " +
        ("BELOW THRESHOLD — more trading days of data needed, or model retrain required"
         if (avg_rho is None or avg_rho < 0.70) else "THRESHOLD MET")
    )

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return {"days": len(validations), "avg_rho": avg_rho, "avg_hit_rate": avg_hit}


def main():
    parser = argparse.ArgumentParser(description="Daily Prediction-vs-Actual Benchmark (Issue #26)")
    parser.add_argument("--days", type=int, default=90, help="Max trading days to include")
    args = parser.parse_args()

    print("=" * 70)
    print("DAILY PREDICTION-VS-ACTUAL BENCHMARK — Issue #26")
    print("=" * 70)
    print(f"Run time: {datetime.now().isoformat()}")

    validations = load_all_validations()
    if args.days and len(validations) > args.days:
        validations = validations[-args.days:]
    predictions_by_date = load_predictions_by_date()

    print(f"Loaded {len(validations)} real validation reports from {VALIDATION_DIR}")
    print(f"Loaded {len(predictions_by_date)} days of predictions from {RANK_HISTORY_FILE}")

    n1 = write_prediction_vs_actual_csv(validations, predictions_by_date)
    print(f"  prediction_vs_actual.csv  — {n1} rows")

    n2 = write_top_mover_match_csv(validations)
    print(f"  top_mover_match.csv       — {n2} rows")

    n3 = write_missed_opportunities_md(validations)
    print(f"  missed_opportunities.md   — {n3} days with misses")

    summary = write_benchmark_summary_md(validations, predictions_by_date)
    print(f"  benchmark_summary.md      — {summary['days']} days summarized")

    if summary["days"] == 0:
        print("\n⚠️  No validation data yet. Files written with honest "
              "'no data' message. This is expected until the validate "
              "job has run on at least one trading day after this fix.")
    else:
        avg_rho = summary.get("avg_rho")
        print(f"\n✅ Benchmark complete. Avg Spearman ρ over {summary['days']} days: "
              f"{avg_rho:.3f}" if avg_rho is not None else "N/A")

    print(f"\nAll outputs written to: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
