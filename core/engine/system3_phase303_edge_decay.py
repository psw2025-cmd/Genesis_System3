"""
System3 Phase 303 - Intraday Edge Decay Analyzer

Understands how fast signal edge decays after it is generated.
"""

import sys
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)

SIGNALS_CSV = STORAGE_LIVE / "dhan_index_ai_signals_with_forward.csv"
LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_edge_decay_303.md"
DECAY_PROFILE_JSON = STORAGE_META / "system3_edge_decay_profile_303.json"

HORIZONS = [1, 3, 5]  # Default forward horizons


def load_signals_robust(path: Path) -> pd.DataFrame:
    """Load signals CSV with robust error handling."""
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, engine="python", on_bad_lines="skip")
    except Exception:
        return pd.DataFrame()


def get_last_trading_day(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to last trading day."""
    if df.empty or "ts" not in df.columns:
        return df
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    df = df.dropna(subset=["ts"]).sort_values("ts")
    if len(df) == 0:
        return df
    latest_date = df["ts"].max().date()
    cutoff = pd.Timestamp.combine(latest_date, pd.Timestamp.min.time())
    return df[df["ts"] >= cutoff].copy()


def classify_edge_profile(ev_by_horizon: Dict[int, float]) -> str:
    """Classify edge profile based on EV decay pattern."""
    if not ev_by_horizon:
        return "UNKNOWN"

    evs = [ev_by_horizon.get(h, 0.0) for h in sorted(ev_by_horizon.keys())]
    if len(evs) < 2:
        return "UNKNOWN"

    # VERY_SHORT: best EV at smallest horizon, then drops
    if evs[0] > evs[-1] and evs[0] > 0:
        return "VERY_SHORT"

    # LONG: EV grows with horizon
    if evs[-1] > evs[0] and evs[-1] > 0:
        return "LONG"

    # MEDIUM: EV stable
    if all(abs(ev - evs[0]) < 0.01 for ev in evs):
        return "MEDIUM"

    return "MEDIUM"  # Default


def run_phase303(**kwargs) -> Dict[str, Any]:
    """Run Phase 303: Intraday Edge Decay Analyzer."""
    errors = []

    try:
        df = load_signals_robust(SIGNALS_CSV)
        if df.empty:
            return {
                "phase": 303,
                "status": "WARN",
                "details": "Signals CSV not found or empty",
                "outputs": {"report_file": str(REPORT_PATH), "json_file": str(DECAY_PROFILE_JSON)},
                "errors": [],
            }

        df_recent = get_last_trading_day(df)
        df_signals = df_recent[df_recent["pred_label"].isin(["BUY", "SELL"])].copy()

        if len(df_signals) == 0:
            return {
                "phase": 303,
                "status": "WARN",
                "details": "No BUY/SELL signals in recent data",
                "outputs": {"report_file": str(REPORT_PATH), "json_file": str(DECAY_PROFILE_JSON)},
                "errors": [],
            }

        # Analyze edge decay per underlying
        profiles = {}
        underlyings = df_signals["underlying"].unique()

        for underlying in underlyings:
            df_underlying = df_signals[df_signals["underlying"] == underlying]

            ev_by_horizon = {}
            ev_by_horizon_label = {"BUY": {}, "SELL": {}}

            for h in HORIZONS:
                fwd_cols = [
                    col
                    for col in df_underlying.columns
                    if f"forward_return_{h}" in col.lower() or f"fwd_ret_{h}" in col.lower()
                ]
                if fwd_cols:
                    fwd_col = fwd_cols[0]
                    fwd_returns = pd.to_numeric(df_underlying[fwd_col], errors="coerce").dropna()
                    if len(fwd_returns) > 0:
                        ev_by_horizon[h] = float(fwd_returns.mean())

                # By label
                for label in ["BUY", "SELL"]:
                    df_label = df_underlying[df_underlying["pred_label"] == label]
                    if fwd_cols and len(df_label) > 0:
                        fwd_returns_label = pd.to_numeric(df_label[fwd_col], errors="coerce").dropna()
                        if len(fwd_returns_label) > 0:
                            ev_by_horizon_label[label][h] = float(fwd_returns_label.mean())

            edge_profile = classify_edge_profile(ev_by_horizon)
            best_horizon = max(ev_by_horizon.items(), key=lambda x: x[1])[0] if ev_by_horizon else 1

            profiles[underlying] = {
                "edge_profile": edge_profile,
                "best_horizon": best_horizon,
                "EV_by_horizon": ev_by_horizon,
                "EV_by_horizon_label": ev_by_horizon_label,
            }

        # Generate report
        report_lines = [
            "# System3 Edge Decay Analysis\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n",
            "## Edge Profile by Underlying\n\n",
            "| Underlying | Edge Profile | Best Horizon | EV (H1) | EV (H3) | EV (H5) |\n",
            "|------------|--------------|--------------|---------|---------|---------|\n",
        ]

        for underlying, profile in profiles.items():
            ev_h1 = profile["EV_by_horizon"].get(1, 0.0)
            ev_h3 = profile["EV_by_horizon"].get(3, 0.0)
            ev_h5 = profile["EV_by_horizon"].get(5, 0.0)
            report_lines.append(
                f"| {underlying} | {profile['edge_profile']} | {profile['best_horizon']} | "
                f"{ev_h1:.4f} | {ev_h3:.4f} | {ev_h5:.4f} |\n"
            )

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        # Save JSON
        json_data = {
            "computation_timestamp": datetime.now().isoformat(),
            "profiles": profiles,
        }

        with DECAY_PROFILE_JSON.open("w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        return {
            "phase": 303,
            "status": "OK",
            "details": f"Analyzed {len(profiles)} underlyings",
            "outputs": {
                "underlyings_analyzed": len(profiles),
                "report_file": str(REPORT_PATH),
                "json_file": str(DECAY_PROFILE_JSON),
            },
            "errors": errors,
        }

    except Exception as e:
        errors.append(str(e))
        return {
            "phase": 303,
            "status": "ERROR",
            "details": f"Exception: {e}",
            "outputs": {"report_file": str(REPORT_PATH), "json_file": str(DECAY_PROFILE_JSON)},
            "errors": errors,
        }
