"""
Factor Weight Calibration Script
=================================
Grid-searches FACTOR_WEIGHTS in GainRankEngine using all available
validation days + bhavcopy data.

Overfitting guard:
  < 5 validation days  → REPORT ONLY (print recommended weights, do not write)
  ≥ 5 validation days  → AUTO-UPDATE src/ranking/gain_rank_engine.py

Confidence levels:
  LOW    (<  5 days)
  MEDIUM (<  14 days)
  HIGH   (≥  14 days)

Usage:
  python scripts/calibrate_factor_weights.py           # auto mode
  python scripts/calibrate_factor_weights.py --dry-run # never writes
  python scripts/calibrate_factor_weights.py --force   # write even with <5 days (dev only)
"""

import argparse
import itertools
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

BHAVCOPY_DIR = ROOT_DIR / "storage" / "bhavcopy"
VALIDATION_DIR = ROOT_DIR / "state" / "market_validations"
GAIN_RANK_ENGINE = ROOT_DIR / "src" / "ranking" / "gain_rank_engine.py"

SYMBOLS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]

# Grid of candidate weights (will be normalized to sum=1.0)
WEIGHT_GRID = {
    "oi_change_pct":     [0.10, 0.15, 0.20, 0.25, 0.30],
    "iv_percentile":     [0.05, 0.10, 0.15, 0.20],
    "volume_surge":      [0.10, 0.15, 0.20],
    "pcr_divergence":    [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50],
    "atm_premium_ratio": [0.05, 0.10, 0.15],
    "momentum_score":    [0.03, 0.05, 0.08],
    # ml_confidence fixed at 0.0 — signal CSV not yet available
}


# ─────────────────────────────────────────────────────────────────────────────
# Factor extraction from bhavcopy
# ─────────────────────────────────────────────────────────────────────────────

def _iv_proxy(ce_ltp: float, pe_ltp: float, spot: float, days_to_expiry: int) -> float:
    """Simplified straddle-based IV proxy (annualised)."""
    T = max(days_to_expiry, 0.5) / 365
    straddle = ce_ltp + pe_ltp
    if spot <= 0 or straddle <= 0:
        return 0.0
    return straddle / spot / (T ** 0.5)


def extract_factors(bhavcopy_path: Path, symbol: str) -> dict | None:
    """
    Extract raw factor values for a single symbol from one bhavcopy file.
    Returns dict with keys: oi_total, oi_change_total, volume, pcr, iv_proxy, atm_premium
    Returns None if symbol not found.
    """
    df = pd.read_csv(bhavcopy_path)
    bhavcopy_date = datetime.strptime(bhavcopy_path.stem[:8], "%Y%m%d").date()

    sub = df[df["TckrSymb"].str.upper() == symbol.upper()]
    sub = sub[sub["OptnTp"].isin(["CE", "PE"])].copy()
    if sub.empty:
        return None

    spot = sub["UndrlygPric"].iloc[0]
    if spot <= 0:
        return None

    # OI totals
    ce_sub = sub[sub["OptnTp"] == "CE"]
    pe_sub = sub[sub["OptnTp"] == "PE"]
    ce_oi = ce_sub["OpnIntrst"].sum()
    pe_oi = pe_sub["OpnIntrst"].sum()
    oi_total = ce_oi + pe_oi
    oi_change_total = sub["ChngInOpnIntrst"].abs().sum()

    # Volume
    volume = sub["TtlTradgVol"].sum()

    # PCR
    pcr = pe_oi / ce_oi if ce_oi > 0 else 1.0

    # IV proxy from nearest expiry ATM straddle
    sub["XpryDt"] = pd.to_datetime(sub["XpryDt"])
    nearest_exp = sub["XpryDt"].min()
    days_to_exp = max((nearest_exp.date() - bhavcopy_date).days, 0)
    near = sub[sub["XpryDt"] == nearest_exp].copy()
    near["dist"] = (near["StrkPric"] - spot).abs()
    atm_strike = near.loc[near["dist"].idxmin(), "StrkPric"]

    atm_ce = near[(near["StrkPric"] == atm_strike) & (near["OptnTp"] == "CE")]
    atm_pe = near[(near["StrkPric"] == atm_strike) & (near["OptnTp"] == "PE")]
    ce_ltp = atm_ce["ClsPric"].values[0] if len(atm_ce) > 0 else 0.0
    pe_ltp = atm_pe["ClsPric"].values[0] if len(atm_pe) > 0 else 0.0

    # Skip expiry day straddle (intrinsic only = distorted IV)
    iv_prx = _iv_proxy(ce_ltp, pe_ltp, spot, days_to_exp) if days_to_exp > 0 else None
    atm_premium = (ce_ltp + pe_ltp) / 2 / spot if spot > 0 else 0.0

    return {
        "symbol": symbol,
        "spot": spot,
        "oi_total": oi_total,
        "oi_change_total": oi_change_total,
        "volume": volume,
        "pcr": pcr,
        "iv_proxy": iv_prx,
        "atm_premium": atm_premium,
        "days_to_exp": days_to_exp,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Factor → score normalisation (same logic as GainRankEngine, simplified)
# ─────────────────────────────────────────────────────────────────────────────

def _norm_minmax(values: list[float]) -> list[float]:
    lo, hi = min(values), max(values)
    if hi == lo:
        return [50.0] * len(values)
    return [(v - lo) / (hi - lo) * 100 for v in values]


def compute_scores(factor_rows: list[dict], iv_history: dict[str, list[float]]) -> pd.DataFrame:
    """
    Convert raw factor dicts for multiple symbols into normalised 0-100 scores.
    iv_history: {symbol: [list of past iv_proxy values]}
    """
    rows = []
    for r in factor_rows:
        sym = r["symbol"]

        # OI change score: % of total OI
        oi_chg_pct = r["oi_change_total"] / r["oi_total"] * 100 if r["oi_total"] > 0 else 0.0

        # IV percentile: rank current iv_proxy vs 5-day history
        iv_raw = r.get("iv_proxy")
        if iv_raw is not None and sym in iv_history and len(iv_history[sym]) > 0:
            hist = iv_history[sym]
            n_below = sum(1 for v in hist if v < iv_raw)
            iv_pctile = n_below / len(hist) * 100
        else:
            iv_pctile = None  # will be filled with cross-symbol median after loop

        rows.append({
            "symbol": sym,
            "oi_change_pct_raw": oi_chg_pct,
            "volume_raw": r["volume"],
            "pcr_raw": r["pcr"],
            "atm_premium_raw": r["atm_premium"],
            "iv_pctile": iv_pctile,
        })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # Fill missing IV percentile with median of known values
    known_iv = df["iv_pctile"].dropna()
    median_iv = known_iv.median() if not known_iv.empty else 50.0
    df["iv_pctile"] = df["iv_pctile"].fillna(median_iv)

    # Normalise cross-symbol min-max
    for col_raw, col_norm in [
        ("oi_change_pct_raw", "oi_score"),
        ("volume_raw", "vol_score"),
        ("atm_premium_raw", "atm_score"),
    ]:
        df[col_norm] = _norm_minmax(df[col_raw].tolist())

    # PCR: extreme PCR = high score (contrarian / big-move signal)
    def pcr_score(pcr: float) -> float:
        if pcr < 0.6 or pcr > 1.8:
            return 90.0
        elif pcr < 0.8 or pcr > 1.4:
            return 70.0
        elif pcr < 1.0 or pcr > 1.2:
            return 55.0
        return 45.0

    df["pcr_score"] = df["pcr_raw"].apply(pcr_score)
    df["iv_score"] = df["iv_pctile"].clip(0, 100)
    df["momentum_score"] = 50.0  # no intraday data from bhavcopy

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Grid search
# ─────────────────────────────────────────────────────────────────────────────

def weighted_gain_score(row: pd.Series, w: dict) -> float:
    base = (
        row["oi_score"]      * w["oi_change_pct"]
        + row["iv_score"]    * w["iv_percentile"]
        + row["vol_score"]   * w["volume_surge"]
        + row["pcr_score"]   * w["pcr_divergence"]
        + row["atm_score"]   * w["atm_premium_ratio"]
        + row["momentum_score"] * w["momentum_score"]
    )
    return base


def _normalise_weights(raw: dict) -> dict:
    total = sum(raw.values())
    return {k: round(v / total, 4) for k, v in raw.items()}


def run_grid_search(training_days: list[dict]) -> tuple[dict, float, list[dict]]:
    """
    training_days: list of {scores_df: DataFrame, actual_ranking: list[str]}
    Returns (best_weights, best_rho, top_k_results)
    """
    keys = list(WEIGHT_GRID.keys())
    ranges = [WEIGHT_GRID[k] for k in keys]

    results = []
    for combo in itertools.product(*ranges):
        raw_w = dict(zip(keys, combo))
        w = _normalise_weights(raw_w)

        rhos = []
        for day in training_days:
            df = day["scores_df"].copy()
            actual_order = day["actual_ranking"]

            df["gain_score"] = df.apply(lambda r: weighted_gain_score(r, w), axis=1)
            df = df.sort_values("gain_score", ascending=False).reset_index(drop=True)
            pred_order = df["symbol"].tolist()

            # Compute Spearman ρ
            actual_ranks = {sym: i + 1 for i, sym in enumerate(actual_order)}
            pred_ranks = {sym: i + 1 for i, sym in enumerate(pred_order)}
            common = [s for s in actual_order if s in pred_ranks]
            if len(common) < 2:
                continue
            a = [actual_ranks[s] for s in common]
            p = [pred_ranks[s] for s in common]
            rho, _ = spearmanr(a, p)
            rhos.append(rho if not np.isnan(rho) else 0.0)

        if not rhos:
            continue
        mean_rho = float(np.mean(rhos))
        results.append({"weights": w, "rho": mean_rho, "n_days": len(rhos)})

    if not results:
        return {}, 0.0, []

    results.sort(key=lambda x: x["rho"], reverse=True)
    best = results[0]
    return best["weights"], best["rho"], results[:10]


# ─────────────────────────────────────────────────────────────────────────────
# Load validation data
# ─────────────────────────────────────────────────────────────────────────────

def load_validation_days() -> list[dict]:
    """
    Returns list of {date, actual_ranking, bhavcopy_path} for days that have:
    - a market_validation JSON
    - a matching bhavcopy file
    """
    out = []
    if not VALIDATION_DIR.exists():
        return out
    for vfile in sorted(VALIDATION_DIR.glob("market_validation_*.json")):
        try:
            with open(vfile) as f:
                vdata = json.load(f)
        except Exception:
            continue

        date_str = vdata.get("date", "")
        actual = vdata.get("actual_ranking", [])
        if not actual or not date_str:
            continue

        # Find matching bhavcopy
        date_compact = date_str.replace("-", "")
        bhavcopy_path = BHAVCOPY_DIR / f"{date_compact}_fo_bhavcopy.csv"
        if not bhavcopy_path.exists():
            continue

        out.append({"date": date_str, "actual_ranking": actual, "bhavcopy_path": bhavcopy_path})
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Build IV history (rolling 5-day lookback)
# ─────────────────────────────────────────────────────────────────────────────

def build_iv_history(all_bhavcopy_files: list[Path], target_date: str) -> dict[str, list[float]]:
    """
    For a given target_date, build a dict of {symbol: [iv_proxy values from last 5 days]}
    using only files BEFORE target_date to avoid lookahead.
    """
    history: dict[str, list[float]] = {s: [] for s in SYMBOLS}
    target = datetime.strptime(target_date, "%Y-%m-%d").date()

    prior_files = sorted(
        [f for f in all_bhavcopy_files if datetime.strptime(f.stem[:8], "%Y%m%d").date() < target]
    )[-5:]  # last 5 trading days before target

    for f in prior_files:
        for sym in SYMBOLS:
            factors = extract_factors(f, sym)
            if factors and factors["iv_proxy"] is not None:
                history[sym].append(factors["iv_proxy"])
    return history


# ─────────────────────────────────────────────────────────────────────────────
# Patch gain_rank_engine.py
# ─────────────────────────────────────────────────────────────────────────────

def patch_engine_weights(new_weights: dict) -> bool:
    """Replace FACTOR_WEIGHTS block in gain_rank_engine.py."""
    text = GAIN_RANK_ENGINE.read_text()
    lines = [
        'FACTOR_WEIGHTS = {',
        f'    "oi_change_pct":      {new_weights["oi_change_pct"]},',
        f'    "iv_percentile":      {new_weights["iv_percentile"]},',
        f'    "volume_surge":       {new_weights["volume_surge"]},',
        f'    "pcr_divergence":     {new_weights["pcr_divergence"]},',
        f'    "atm_premium_ratio":  {new_weights["atm_premium_ratio"]},',
        f'    "momentum_score":     {new_weights["momentum_score"]},',
        f'    "ml_confidence":      {new_weights.get("ml_confidence", 0.20)},',
        '}',
    ]
    new_block = "\n".join(lines)
    patched = re.sub(
        r'FACTOR_WEIGHTS\s*=\s*\{[^}]+\}',
        new_block,
        text,
        flags=re.DOTALL,
    )
    if patched == text:
        print("  WARNING: Could not locate FACTOR_WEIGHTS block to patch.")
        return False
    GAIN_RANK_ENGINE.write_text(patched)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Calibrate GainRankEngine factor weights")
    parser.add_argument("--dry-run", action="store_true", help="Never write changes")
    parser.add_argument("--force",   action="store_true", help="Write even with <5 days (dev)")
    parser.add_argument("--verbose", action="store_true", help="Show top-10 weight combos")
    args = parser.parse_args()

    print("=" * 70)
    print("FACTOR WEIGHT CALIBRATION — Genesis System3")
    print(f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("=" * 70)

    # 1. Load validation days
    val_days = load_validation_days()
    n_days = len(val_days)
    print(f"\nValidation days found: {n_days}")

    if n_days < 2:
        confidence = "INSUFFICIENT"
    elif n_days < 5:
        confidence = "LOW"
    elif n_days < 14:
        confidence = "MEDIUM"
    else:
        confidence = "HIGH"

    print(f"Calibration confidence: {confidence}")
    for d in val_days:
        print(f"  {d['date']}: actual={d['actual_ranking']}")

    if n_days < 2:
        print("\nNeed at least 2 validation days to calibrate. Accumulate more data and re-run.")
        return

    # 2. Build training set
    all_bhavcopy = sorted(BHAVCOPY_DIR.glob("*.csv"))
    training_days = []

    for vday in val_days:
        print(f"\nExtracting factors for {vday['date']} ...")
        iv_history = build_iv_history(all_bhavcopy, vday["date"])
        factor_rows = []
        for sym in SYMBOLS:
            if sym not in vday["actual_ranking"]:
                continue
            factors = extract_factors(vday["bhavcopy_path"], sym)
            if factors:
                factor_rows.append(factors)

        if len(factor_rows) < 2:
            print(f"  Skipped {vday['date']}: not enough symbols in bhavcopy")
            continue

        scores_df = compute_scores(factor_rows, iv_history)
        if scores_df.empty:
            continue

        training_days.append({
            "date": vday["date"],
            "scores_df": scores_df,
            "actual_ranking": vday["actual_ranking"],
        })

    if not training_days:
        print("\nNo usable training days after factor extraction.")
        return

    # 3. Grid search
    print(f"\nRunning grid search over {sum(len(v) for v in WEIGHT_GRID.values())} parameter axes ...")
    best_weights, best_rho, top_results = run_grid_search(training_days)

    print(f"\n{'─'*70}")
    print(f"BEST RESULT: Spearman ρ = {best_rho:.4f} (over {len(training_days)} days)")
    print(f"Best weights (normalised to 1.0):")
    for k, v in best_weights.items():
        print(f"  {k:<22}: {v:.4f}")

    if args.verbose and top_results:
        print(f"\nTop 10 weight combinations:")
        for i, r in enumerate(top_results[:10], 1):
            w = r["weights"]
            print(f"  #{i} ρ={r['rho']:.4f}  OI={w['oi_change_pct']:.2f} IV={w['iv_percentile']:.2f} "
                  f"VOL={w['volume_surge']:.2f} PCR={w['pcr_divergence']:.2f} "
                  f"ATM={w['atm_premium_ratio']:.2f} MOM={w['momentum_score']:.2f}")

    # 4. Decision: write or report
    print(f"\n{'─'*70}")
    should_write = (n_days >= 5 or args.force) and not args.dry_run

    if confidence == "LOW" or n_days < 5:
        print(f"DECISION: REPORT ONLY (confidence={confidence}, n_days={n_days} < 5)")
        print("  Recommended weights printed above — not applied until 5+ validation days available.")
        print(f"  Current floor: ρ=0.20. Estimated new ρ with these weights: {best_rho:.4f}")
        if args.force:
            should_write = True
            print("  --force flag set: writing anyway.")
    else:
        print(f"DECISION: AUTO-UPDATE gain_rank_engine.py (confidence={confidence}, n_days={n_days})")

    if should_write and not args.dry_run:
        # Add ml_confidence back at 0.20, renormalise
        weights_with_ml = dict(best_weights)
        weights_with_ml["ml_confidence"] = 0.20
        weights_with_ml = _normalise_weights(weights_with_ml)
        ok = patch_engine_weights(weights_with_ml)
        if ok:
            print(f"  WRITTEN to {GAIN_RANK_ENGINE}")
        else:
            print("  ERROR: patch failed — check regex in patch_engine_weights()")
    elif args.dry_run:
        print("  --dry-run: no changes written.")

    # 5. Save calibration report
    report = {
        "run_at": datetime.now().isoformat(),
        "n_validation_days": n_days,
        "confidence": confidence,
        "best_rho": best_rho,
        "best_weights": best_weights,
        "training_dates": [d["date"] for d in training_days],
        "top_10": top_results[:10],
        "written": should_write and not args.dry_run,
    }
    report_path = ROOT_DIR / "state" / "calibration_report.json"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nCalibration report saved to: {report_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
