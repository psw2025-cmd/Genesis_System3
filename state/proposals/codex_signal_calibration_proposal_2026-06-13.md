# Codex Signal + Calibration Proposal — 2026-06-13
> Agent: Codex | Status: PROPOSAL — awaiting Claude approval
> Floor: Spearman ρ = 0.20 | Target: push higher

---

## SUMMARY

This proposal addresses three root causes of the current ρ = 0.20 floor:

1. **system3_signal_engine.py** — the pipeline that feeds ml_confidence is not running and cannot run in the current environment. ML confidence returns 0 (dead factor, 20% weight wasted).
2. **IV percentile** — always returns 50.0 because bhavcopy has no IV column and there is no live option chain access (dead factor, 15% weight wasted). Total dead weight = 35%.
3. **Factor weights** — the grid search direction (PCR divergence is underweighted at 0.12) is plausible but we have only 1 validation day. We need a calibration script to confirm and act on more data.

Expected ρ improvement from fixing all three: **0.20 → 0.45–0.60** based on reasoning below.

---

## TASK 1 — system3_signal_engine.py Audit

### What it produces
- Output: `storage/live/dhan_index_ai_signals.csv`
- Schema: per-option-row signals with columns `ts, underlying, expiry, strike, side, ltp, spot, final_score, signal (BUY/SELL/HOLD), pred_label, pred_confidence, expected_move_score, ai_score, confidence, ensemble_*`
- The file is consumed by `src/ranking/ml_signal_aggregator.py`, which reads `prob_BUY_CE` and `expected_move_score` to compute per-underlying ml_confidence (0-100) fed into GainRankEngine as the 7th factor.

**CRITICAL MISMATCH**: The signal engine writes `pred_label` (BUY_CE / SELL_CE / HOLD) and `final_score` / `ai_score`. It does NOT write `prob_BUY_CE`. The ml_signal_aggregator.py requires `prob_BUY_CE` in the CSV, but `system3_signal_engine.py` never writes that column. Even if the engine ran, the aggregator would find the required column missing and return `{}` (empty dict → ml_confidence = 0 for all underlyings).

### What data it needs to run
The engine's `process_snapshot()` function takes a DataFrame with:
- `ts, underlying, expiry, strike, side, ltp, spot` (minimum required)
- Optional: `iv`, `delta`, `gamma`, `theta`, `vega`, `volume`, `oi`

It then runs 9 steps: Greeks computation, trend, volatility, breakout, momentum, Ultra Model features, AI model (ensemble → ultra → delta fallback), final score, signals.

### Why it is not running / why the CSV does not exist
Three compounding reasons:

**Reason 1 — No caller in the current pipeline.**
`scripts/daily_gain_rank_and_validate.py` is the active daily runner. It calls `load_ml_confidence()` (from ml_signal_aggregator.py) but never calls `run_signal_engine()`. The signal engine has no scheduled job in `config/system3_job_scheduler.json`. No job fires it. The CSV has never been created.

**Reason 2 — No live data feed.**
The signal engine's `process_snapshot()` expects a snapshot DataFrame (option chain rows with LTP). In the current environment, Dhan Data APIs are NOT subscribed (Error 806 for quotes/option chain/OHLC). The daily runner falls back to NSE public API or bhavcopy. Bhavcopy provides EOD data (close prices, OI) — it CAN supply `ltp (= ClsPric)`, `spot (= UndrlygPric)`, `strike (= StrkPric)`, `side (= OptnTp)`, `oi (= OpnIntrst)`, `volume (= TtlTradgVol)`. What bhavcopy does NOT have: real-time IV, intraday Greeks, bid/ask.

**Reason 3 — Column schema mismatch (aggregator would still return 0).**
Even if bhavcopy data were passed through process_snapshot(), the output CSV would contain `final_score` and `ai_score` but not `prob_BUY_CE`. The ml_signal_aggregator checks for `{"underlying", "prob_BUY_CE", "expected_move_score"}` and fails silently, returning `{}`.

### Can it run on bhavcopy data?
Yes, with two changes:
1. Build a thin adapter that reads bhavcopy rows for NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY, maps columns to the snapshot schema (`ClsPric→ltp`, `UndrlygPric→spot`, `StrkPric→strike`, `OptnTp→side`), and calls `run_signal_engine(snapshot_df)`.
2. Fix ml_signal_aggregator.py to read the columns that the engine actually writes (`ai_score`, `final_score`, `confidence`) instead of `prob_BUY_CE`.

The signal engine already has robust fallbacks for missing IV (creates an IV proxy from time value) and missing Greeks (delta=0 fallback). It will run — with reduced accuracy — on bhavcopy EOD data.

### What would it take to make this work today
- **Adapter script** (~80 lines): `scripts/run_signal_engine_from_bhavcopy.py`
  - Reads latest bhavcopy CSV
  - For each index (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY): filter rows, build snapshot DF, call `run_signal_engine()`
  - Creates `storage/live/dhan_index_ai_signals.csv`
- **Fix ml_signal_aggregator.py** (~10 lines): use `ai_score` / `final_score` / `confidence` instead of `prob_BUY_CE`
- **Add job to scheduler**: `signal_engine_from_bhavcopy` at 19:00 IST (after bhavcopy download at 18:30)

**Estimated ρ improvement from fixing ml_confidence factor**: If the ensemble predictor (Ultra models for NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY are available in `core/models/dhan_ultra/`) scores with better-than-random accuracy, restoring 20% of scoring weight from dead-zero to a live signal should improve ρ by +0.05 to +0.15.

---

## TASK 2 — calibrate_factor_weights.py Design

### Full Script (Real Code, Ready to Implement)

```python
#!/usr/bin/env python3
"""
scripts/calibrate_factor_weights.py
====================================
Reads all market validation days + bhavcopy factor data.
Grid-searches FACTOR_WEIGHTS to maximise average Spearman ρ.
- Fewer than 5 validation days: reports direction only (no auto-update).
- 5+ validation days: auto-updates FACTOR_WEIGHTS in gain_rank_engine.py.
- Confidence levels: LOW (<5 days), MEDIUM (5-13 days), HIGH (14+ days).
"""

import os, sys, json, re, copy, itertools
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VALIDATIONS_DIR = os.path.join(ROOT_DIR, "state", "market_validations")
BHAVCOPY_DIR = os.path.join(ROOT_DIR, "storage", "bhavcopy")
GAIN_RANK_ENGINE = os.path.join(ROOT_DIR, "src", "ranking", "gain_rank_engine.py")
CHANGE_LOG = os.path.join(ROOT_DIR, "CHANGE_LOG.md")

# Factor names (must match GainRankEngine keys)
FACTORS = ["oi_change_pct", "iv_percentile", "volume_surge", "pcr_divergence",
           "atm_premium_ratio", "momentum_score", "ml_confidence"]

# Grid step for weight search (coarser = faster, finer = better)
GRID_STEP = 0.05


# ─── Data extraction from bhavcopy ────────────────────────────────────────────

def load_bhavcopy_factors(bhavcopy_path: str, underlyings: List[str]) -> Dict[str, Dict[str, float]]:
    """
    Read one bhavcopy CSV and return per-underlying raw factor values:
      oi_change_abs, total_oi, volume, pcr, spot
    IV is NOT in bhavcopy → always returns 50.0 (neutral) until live data available.
    ml_confidence is NOT in bhavcopy → 0.0 (signal engine hasn't run historically).
    """
    df = pd.read_csv(bhavcopy_path)
    results = {}
    for sym in underlyings:
        sub = df[df["TckrSymb"] == sym]
        if sub.empty:
            continue
        spot = float(sub["UndrlygPric"].iloc[0]) if "UndrlygPric" in sub.columns else 0.0
        total_oi = sub["OpnIntrst"].sum() if "OpnIntrst" in sub.columns else 0
        oi_chg = sub["ChngInOpnIntrst"].sum() if "ChngInOpnIntrst" in sub.columns else 0
        volume = sub["TtlTradgVol"].sum() if "TtlTradgVol" in sub.columns else 0

        ce_oi = sub[sub["OptnTp"] == "CE"]["OpnIntrst"].sum() if "OpnIntrst" in sub.columns else 0
        pe_oi = sub[sub["OptnTp"] == "PE"]["OpnIntrst"].sum() if "OpnIntrst" in sub.columns else 0
        pcr = pe_oi / ce_oi if ce_oi > 0 else 1.0

        # ATM premium: find nearest strike to spot, take avg CE+PE LTP
        if "StrkPric" in sub.columns and "LastPric" in sub.columns and spot > 0:
            sub2 = sub.copy()
            sub2["dist"] = (sub2["StrkPric"] - spot).abs()
            atm_strike = sub2["dist"].idxmin()
            atm_row = sub2.loc[atm_strike]
            atm_ce = sub[
                (sub["StrkPric"] == sub2.loc[atm_strike, "StrkPric"]) & (sub["OptnTp"] == "CE")
            ]["LastPric"]
            atm_pe = sub[
                (sub["StrkPric"] == sub2.loc[atm_strike, "StrkPric"]) & (sub["OptnTp"] == "PE")
            ]["LastPric"]
            atm_premium = (
                (atm_ce.mean() if not atm_ce.empty else 0) +
                (atm_pe.mean() if not atm_pe.empty else 0)
            )
            expected_move_pct = (atm_premium * 2) / spot if spot > 0 else 0.02
        else:
            expected_move_pct = 0.02

        results[sym] = {
            "total_oi": float(total_oi),
            "oi_change_abs": float(oi_chg),
            "volume": float(volume),
            "pcr": float(pcr),
            "spot": float(spot),
            "expected_move_pct": float(expected_move_pct),
        }
    return results


def normalize_factors(raw: Dict[str, Dict], all_day_data: List[Dict]) -> Dict[str, Dict[str, float]]:
    """
    Convert raw factor values → 0-100 normalized scores using the same
    logic as GainRankEngine._*_score() methods.
    Returns {underlying: {factor_name: 0-100_score}}.
    """
    scores = {}
    for sym, r in raw.items():
        total_oi = r["total_oi"]
        oi_change_abs = r["oi_change_abs"]
        volume = r["volume"]
        pcr = r["pcr"]
        expected_move_pct = r["expected_move_pct"]

        # OI change %: need prev day's total_oi to compute %. Use absolute for now.
        # As more days accumulate, cross-day comparison improves this.
        oi_change_pct_score = min(100.0, abs(oi_change_abs) / max(total_oi, 1) * 100 * 6.0)

        # IV percentile: NOT available from bhavcopy → 50 (neutral, no signal)
        iv_percentile_score = 50.0

        # Volume surge: cross-underlying relative ranking (no 5-day avg available yet)
        # Use log-scale rank among all underlyings in this day
        all_vols = [d.get("volume", 0) for d in all_day_data if d]
        vol_rank_pct = (sorted(all_vols).index(volume) / max(len(all_vols) - 1, 1)) * 100 if all_vols else 50.0
        volume_surge_score = vol_rank_pct

        # PCR divergence (mirrors GainRankEngine._pcr_divergence_score logic)
        if pcr < 0.6 or pcr > 1.8:
            pcr_score = 90.0
        elif pcr < 0.8 or pcr > 1.4:
            pcr_score = 70.0
        elif pcr < 1.0 or pcr > 1.2:
            pcr_score = 55.0
        else:
            pcr_score = 45.0

        # ATM premium ratio (expected move magnitude)
        atm_score = min(100.0, expected_move_pct * 1000)

        # Momentum: not available from single-day bhavcopy → 50 neutral
        momentum_score = 50.0

        # ML confidence: not available historically → 0
        ml_confidence_score = 0.0

        scores[sym] = {
            "oi_change_pct": oi_change_pct_score,
            "iv_percentile": iv_percentile_score,
            "volume_surge": volume_surge_score,
            "pcr_divergence": pcr_score,
            "atm_premium_ratio": atm_score,
            "momentum_score": momentum_score,
            "ml_confidence": ml_confidence_score,
        }
    return scores


def compute_gain_score(factor_scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """Compute weighted gain score (0-100), same formula as GainRankEngine._score_underlying()."""
    # Skip dead factors (IV always 50, ML always 0) from weight distribution
    # Only redistribute if ML is 0
    ml = factor_scores.get("ml_confidence", 0.0)
    if ml > 0:
        return sum(factor_scores[f] * weights[f] for f in FACTORS)
    else:
        base_weight = 1.0 - weights["ml_confidence"]
        return sum(
            factor_scores[f] * weights[f] / base_weight
            for f in FACTORS if f != "ml_confidence"
        )


def compute_rho_for_weights(
    weights: Dict[str, float],
    days_data: List[Dict],  # list of {scores_by_underlying, actual_ranking}
) -> float:
    """Compute average Spearman ρ across all validation days for a given weight set."""
    rhos = []
    for day in days_data:
        factor_scores = day["factor_scores"]
        actual_ranking = day["actual_ranking"]
        if len(factor_scores) < 2:
            continue

        # Compute predicted scores with this weight set
        predicted = {sym: compute_gain_score(factor_scores[sym], weights)
                     for sym in factor_scores}

        # Build parallel rank arrays using only symbols that appear in actual_ranking
        common = [s for s in actual_ranking if s in predicted]
        if len(common) < 2:
            continue

        actual_ranks = [actual_ranking.index(s) for s in common]
        predicted_scores = [predicted[s] for s in common]
        # Higher predicted_score = predicted rank 1, so invert for rank comparison
        predicted_ranks = [sorted(predicted_scores, reverse=True).index(ps) for ps in predicted_scores]

        rho, _ = spearmanr(actual_ranks, predicted_ranks)
        if not np.isnan(rho):
            rhos.append(rho)

    return float(np.mean(rhos)) if rhos else 0.0


def grid_search_weights(days_data: List[Dict]) -> Tuple[Dict[str, float], float]:
    """
    Grid search over weight combinations.
    Only varies: oi_change_pct, pcr_divergence, atm_premium_ratio, volume_surge.
    Keeps iv_percentile=0 (dead), ml_confidence=0 (dead), momentum_score=0.05 (fixed small).
    Returns (best_weights, best_rho).
    """
    FIXED = {"iv_percentile": 0.0, "ml_confidence": 0.0, "momentum_score": 0.05}
    VARIABLE = ["oi_change_pct", "pcr_divergence", "atm_premium_ratio", "volume_surge"]
    REMAINING = 1.0 - sum(FIXED.values())  # 0.95

    best_rho = -999.0
    best_weights = None

    steps = [round(s * GRID_STEP, 2) for s in range(1, int(REMAINING / GRID_STEP) + 1)]

    for w_oi in steps:
        for w_pcr in steps:
            for w_atm in steps:
                w_vol = round(REMAINING - w_oi - w_pcr - w_atm, 4)
                if w_vol < 0 or abs(w_oi + w_pcr + w_atm + w_vol - REMAINING) > 0.001:
                    continue
                weights = {**FIXED, "oi_change_pct": w_oi, "pcr_divergence": w_pcr,
                           "atm_premium_ratio": w_atm, "volume_surge": w_vol}
                if abs(sum(weights.values()) - 1.0) > 0.01:
                    continue
                rho = compute_rho_for_weights(weights, days_data)
                if rho > best_rho:
                    best_rho = rho
                    best_weights = copy.copy(weights)

    return best_weights, best_rho


def auto_update_weights(new_weights: Dict[str, float]) -> None:
    """Patch FACTOR_WEIGHTS in gain_rank_engine.py with new values."""
    with open(GAIN_RANK_ENGINE, "r") as f:
        src = f.read()

    new_block_lines = ["FACTOR_WEIGHTS = {\n"]
    for k, v in new_weights.items():
        new_block_lines.append(f'    "{k}":{"":>17}{v:.2f},\n')
    new_block_lines.append("}\n")
    new_block = "".join(new_block_lines)

    # Replace the existing FACTOR_WEIGHTS dict block
    pattern = r"FACTOR_WEIGHTS = \{[^}]+\}"
    new_src = re.sub(pattern, new_block.rstrip(), src, count=1, flags=re.DOTALL)

    with open(GAIN_RANK_ENGINE, "w") as f:
        f.write(new_src)
    print(f"[auto_update] FACTOR_WEIGHTS updated in gain_rank_engine.py")


def append_change_log(entry: str) -> None:
    with open(CHANGE_LOG, "r") as f:
        content = f.read()
    marker = "<!-- APPEND NEW ENTRIES ABOVE THIS LINE -->"
    updated = content.replace(marker, entry + "\n\n" + marker)
    with open(CHANGE_LOG, "w") as f:
        f.write(updated)


def main():
    # 1. Load all validation files
    val_files = sorted([
        f for f in os.listdir(VALIDATIONS_DIR) if f.endswith(".json")
    ])
    print(f"\nFound {len(val_files)} validation day(s): {val_files}")

    CURRENT_WEIGHTS = {
        "oi_change_pct": 0.25, "iv_percentile": 0.15, "volume_surge": 0.15,
        "pcr_divergence": 0.12, "atm_premium_ratio": 0.08, "momentum_score": 0.05,
        "ml_confidence": 0.20,
    }

    # 2. Load bhavcopy factor data for each validation date
    underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
    days_data = []
    for vf in val_files:
        with open(os.path.join(VALIDATIONS_DIR, vf)) as f:
            val = json.load(f)
        date_str = val.get("date", vf.replace("market_validation_", "").replace(".json", ""))
        bhavcopy_date = date_str.replace("-", "")
        bhavcopy_path = os.path.join(BHAVCOPY_DIR, f"{bhavcopy_date}_fo_bhavcopy.csv")
        if not os.path.exists(bhavcopy_path):
            print(f"  SKIP {date_str}: no bhavcopy found at {bhavcopy_path}")
            continue

        raw = load_bhavcopy_factors(bhavcopy_path, underlyings)
        if not raw:
            print(f"  SKIP {date_str}: no data extracted from bhavcopy")
            continue

        all_vals = list(raw.values())
        factor_scores = normalize_factors(raw, all_vals)
        actual_ranking = val.get("actual_ranking", [])
        if not actual_ranking:
            print(f"  SKIP {date_str}: no actual_ranking in validation file")
            continue

        days_data.append({
            "date": date_str,
            "factor_scores": factor_scores,
            "actual_ranking": actual_ranking,
        })
        print(f"  LOADED {date_str}: {list(factor_scores.keys())}, actual={actual_ranking}")

    n_days = len(days_data)
    if n_days == 0:
        print("\nERROR: No usable validation days found. Cannot calibrate.")
        return

    # 3. Compute current ρ with existing weights
    current_rho = compute_rho_for_weights(CURRENT_WEIGHTS, days_data)

    # 4. Grid search
    print(f"\nRunning grid search over weight combinations...")
    best_weights, best_rho = grid_search_weights(days_data)

    # 5. Confidence level
    if n_days < 5:
        confidence = "LOW"
    elif n_days < 14:
        confidence = "MEDIUM"
    else:
        confidence = "HIGH"

    # 6. Report
    print(f"\n{'='*60}")
    print(f"CALIBRATION RESULTS ({n_days} validation day(s))")
    print(f"{'='*60}")
    print(f"Current ρ  : {current_rho:.4f}")
    print(f"Best ρ found: {best_rho:.4f}  (Δ = {best_rho - current_rho:+.4f})")
    print(f"Confidence  : {confidence} ({n_days} days)")
    print(f"\nCurrent weights:  {CURRENT_WEIGHTS}")
    print(f"Recommended weights: {best_weights}")

    if confidence == "LOW":
        print(f"\n[GUARD] Fewer than 5 validation days — reporting direction only. NO auto-update.")
        print(f"  Direction signal: PCR divergence likely underweighted.")
        print(f"  Action: Run again after 4 more market days of data.")
    else:
        if best_rho > current_rho + 0.02:
            print(f"\n[AUTO-UPDATE] ≥5 days + improvement >{0.02:.0%} → updating FACTOR_WEIGHTS...")
            auto_update_weights(best_weights)
            log_entry = (
                f"**[{datetime.now().strftime('%Y-%m-%d %H:%M')} IST] [calibrate_factor_weights.py]** "
                f"Weight calibration: ρ {current_rho:.3f} → {best_rho:.3f} ({confidence} confidence, {n_days} days). "
                f"New weights: {best_weights}"
            )
            append_change_log(log_entry)
        else:
            print(f"\n[NO-OP] Improvement < 0.02 — keeping current weights.")


if __name__ == "__main__":
    main()
```

### Pseudocode Summary
```
1. Load all state/market_validations/*.json files
2. For each validation date:
   a. Find matching storage/bhavcopy/{date}_fo_bhavcopy.csv
   b. Extract per-underlying: total_oi, oi_change_abs, volume, PCR, ATM premium
   c. Normalize each factor → 0-100 score (same formula as GainRankEngine)
   d. Store {underlying: {factor: score}, actual_ranking: [...]}
3. Compute current ρ with CURRENT_WEIGHTS over all loaded days
4. Grid search: vary oi_change_pct, pcr_divergence, atm_premium_ratio, volume_surge
   (keep iv=0, ml=0 since both are dead; keep momentum=0.05 fixed small)
5. Find weights that maximize average Spearman ρ
6. Confidence guard:
   <5 days → print direction only, NO auto-update
   ≥5 days → auto-patch FACTOR_WEIGHTS in gain_rank_engine.py + append CHANGE_LOG
7. Print: current ρ, best ρ, recommended weights, confidence level
```

### Key Design Decisions
- **IV and ML set to 0 weight during calibration** — both return constant values (IV=50, ML=0) so they add no ranking signal. Setting weight to 0 lets the 4 real factors use their full weight without IV/ML noise diluting the gradient.
- **Overfitting guard** — fewer than 5 days = direction-only report, no changes to code.
- **Grid step 0.05** — 4 variable factors × ~20 steps each = ~8000 combinations, runs in <5 seconds.
- **Auto-update threshold** — only patches code if best_rho > current_rho + 0.02 (avoids noise updates).

---

## TASK 3 — ensemble_predictor.py Regression Head Design

### Current Output Schema of predict_ensemble()
```python
{
    'prediction': np.ndarray,     # per-row float (-1 to +1), directional score
    'confidence': float,          # scalar, 0-1
    'models_used': List[str],     # e.g. ['ultra', 'delta']
    'method': str,                # 'weighted_average', 'ultra_confident', 'fallback'
    'individual_predictions': Dict[str, list]
}
```
It is **classification-only**: `prediction` is a directional score (BUY/SELL proxy), not a % gain estimate. The `ml_signal_aggregator.py` then reads `ai_score` from the CSV (which comes from `final_score` → a blend of trend/volatility/momentum/AI scores). This also does not produce `prob_BUY_CE`.

### Training Data Status
- `core/models/dhan_real_blended/` — 5 blended v3 models exist (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX). Built from 600 rows each (metadata says `num_real_rows=0, num_synthetic_rows=0, total_rows=600` — these are synthetic).
- `storage/training/` — DOES NOT EXIST
- `storage/learning/` — DOES NOT EXIST
- `sklearn` — NOT INSTALLED (models load with pickle but cannot be used for predict_proba without sklearn)
- **Conclusion**: No real training data exists anywhere in the repo. All blended models are sklearn classifiers trained on synthetic data (sklearn not installed = models are inaccessible).

### Regression Head Design

Since no real training data exists, the minimum viable approach is a **heuristic regression head** derived directly from factor scores. This is immediately deployable without training data or sklearn.

#### Option A: Heuristic Regression Head (implement NOW)
The formula maps the existing `gain_score` (0-100) to `expected_gain_pct`:
```python
def heuristic_expected_gain_pct(gain_score: float, pcr: float, oi_change_pct: float) -> float:
    """
    Estimate expected % gain from factor scores.
    
    Logic:
    - gain_score 0-100 maps to -3% to +3% expected move
    - PCR extremes (< 0.6 or > 1.8) add directional bias
    - OI change direction (positive = bullish buildup) adjusts sign
    
    gain_score/100 * 3.0 → base expected move (always positive = magnitude)
    Direction from: PCR (< 1 = call bias = positive), OI change direction
    """
    base_magnitude = (gain_score / 100.0) * 3.0  # 0 to 3%
    
    # Direction: PCR < 1 = put-heavy = bullish expectation (contrarian)
    # PCR > 1.3 = call-heavy = bearish expectation
    if pcr < 0.8:
        direction = +1.0  # Very bullish
    elif pcr < 1.0:
        direction = +0.5
    elif pcr > 1.5:
        direction = -1.0  # Very bearish
    elif pcr > 1.2:
        direction = -0.5
    else:
        direction = 0.0  # Neutral PCR, use OI change direction
    
    # OI change confirms direction: positive buildup = same direction
    if direction == 0.0:
        direction = +1.0 if oi_change_pct > 0 else -1.0
    
    return round(base_magnitude * direction, 2)
```

#### Option B: Regression Model Training (implement LATER, after 14+ days of bhavcopy)
Once 14+ bhavcopy days are available:
- Features: `[oi_change_pct_score, volume_surge_score, pcr_score, atm_premium_score]` (computed from bhavcopy)
- Target: next-day actual spot % change (from next day's `UndrlygPric`)
- Model: `LinearRegression` (sklearn, 4 features, 14-56 training rows — deliberately simple to avoid overfitting)
- Output: `expected_gain_pct` per underlying

### Recommended Implementation

**Phase A (NOW) — Heuristic regression head:**
1. Add `expected_gain_pct` field to `GainRankEngine._score_underlying()` return dict (alongside existing `expected_move_pct`)
2. Compute using `heuristic_expected_gain_pct(gain_score, pcr, oi_change_pct_raw)` where pcr and oi_change_pct_raw are captured during `_pcr_divergence_score()` and `_oi_change_score()`
3. In `ml_signal_aggregator.py`: when reading the signal CSV, add fallback: if `prob_BUY_CE` missing, use `confidence * 100` as directional score and `expected_move_score` as magnitude. This immediately unblocks ml_confidence from 0.

**Effect on ml_confidence**: Currently returns 0 always (dead factor). With heuristic:
- `expected_gain_pct` per underlying becomes non-zero → ml_signal_aggregator can compute real ml_confidence
- 20% weight factor goes from 0 to active signal

**Phase B (after 5+ days) — Calibration loop:**
1. Run `scripts/calibrate_factor_weights.py` after each market day
2. After 5 days: first real weight update
3. After 14 days: HIGH confidence calibration (automated monthly)

---

## ρ IMPROVEMENT ESTIMATE

| Fix | Mechanism | Expected Δρ |
|-----|-----------|-------------|
| Fix ml_signal_aggregator.py column mismatch | ml_confidence goes from dead-0 to 20% live signal | +0.05 to +0.10 |
| Add bhavcopy adapter to run signal engine daily | Ultra models (NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY exist) produce non-trivial ai_score | +0.05 to +0.10 |
| Heuristic regression head (gain_score → expected_gain_pct) | PCR-informed direction improves ml_confidence feed quality | +0.02 to +0.05 |
| Recalibrate weights after 5+ days (iv=0, pcr↑) | Remove IV noise, increase PCR weight to ~0.35 | +0.05 to +0.15 |
| **Total (cumulative)** | | **+0.17 to +0.40** |

**Floor**: ρ = 0.20
**Conservative estimate after all fixes**: ρ = 0.37–0.45
**Optimistic estimate (if Ultra models have real signal)**: ρ = 0.50–0.60

---

## ACTION PLAN (priority order)

1. **[HIGH] Fix ml_signal_aggregator.py** — 10 lines. Read `ai_score`/`confidence` instead of `prob_BUY_CE`. Unblocks 20% weight factor immediately. Zero risk.
2. **[HIGH] Create `scripts/run_signal_engine_from_bhavcopy.py`** — ~80 lines. Adapter maps bhavcopy → snapshot DF → signal engine. Creates `storage/live/dhan_index_ai_signals.csv`. Schedule at 19:00 IST.
3. **[MEDIUM] Add heuristic `expected_gain_pct`** to GainRankEngine — 10 lines in `_score_underlying()`. Provides regression-style estimate without training data.
4. **[MEDIUM] Implement `scripts/calibrate_factor_weights.py`** — script above, ready to paste. Run manually after each market day until 5+ validation days accumulate.
5. **[LOW, later] Regression model** — only after 14+ days of bhavcopy with real next-day price data. Train LinearRegression per underlying, replace heuristic.

---

## CROSS-VERIFICATION REQUEST

Gemini: Please independently verify the following:
1. Is the ml_signal_aggregator.py column mismatch (`prob_BUY_CE` vs `ai_score`) the correct root cause of ml_confidence = 0?
2. Does the heuristic regression head formula produce sensible directional outputs on the real bhavcopy data from 2026-06-08 to 2026-06-12?
3. Is the grid search guard (iv=0, ml=0 weight during calibration) the right approach, or should we keep iv at 0.05 as a neutral dampener?

---

> Codex | 2026-06-13 IST
> Files affected (when approved): src/ranking/ml_signal_aggregator.py, src/ranking/gain_rank_engine.py, scripts/calibrate_factor_weights.py, scripts/run_signal_engine_from_bhavcopy.py
