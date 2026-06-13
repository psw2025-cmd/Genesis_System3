"""
System3 Phase 305 - Confidence Tier Tagger (High/Medium/Low)

Tags each past signal with a confidence tier based on score, edge, and context.
"""

import sys
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)

RECONCILED_CSV = STORAGE_LIVE / "dhan_index_ai_signals_reconciled.csv"
FALLBACK_CSV = STORAGE_LIVE / "dhan_index_ai_signals_with_forward.csv"

DECAY_303_JSON = STORAGE_META / "system3_edge_decay_profile_303.json"
REGIME_302_JSON = STORAGE_META / "system3_regime_performance_302.json"

LOG_DIR = PROJECT_ROOT / "logs" / "ml"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_confidence_tiering_305.md"
OUTPUT_CSV = STORAGE_LIVE / "dhan_index_ai_signals_confidence_tagged_305.csv"


def load_csv_robust(path: Path) -> pd.DataFrame:
    """Load CSV with robust error handling."""
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, engine="python", on_bad_lines="skip")
    except Exception:
        return pd.DataFrame()


def load_json_safe(path: Path) -> Dict:
    """Load JSON file safely."""
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def compute_confidence_score(row: pd.Series, decay_data: Dict, regime_data: Dict) -> float:
    """Compute confidence score for a signal row."""
    score = 0.0

    # Base score from final_score
    if "final_score" in row:
        abs_score = abs(float(row["final_score"]))
        score += abs_score * 0.4  # 40% weight

    # Regime strength (from Phase 302)
    if regime_data and "underlying_level" in regime_data:
        underlying = row.get("underlying", "")
        if underlying in regime_data["underlying_level"]:
            regime = regime_data["underlying_level"][underlying].get("regime", "UNKNOWN")
            if regime == "LOW":
                score += 0.1
            elif regime == "NORMAL":
                score += 0.2
            elif regime == "HIGH":
                score += 0.3

    # Edge profile (from Phase 303)
    if decay_data and "profiles" in decay_data:
        underlying = row.get("underlying", "")
        if underlying in decay_data["profiles"]:
            profile = decay_data["profiles"][underlying].get("edge_profile", "UNKNOWN")
            if profile == "LONG":
                score += 0.2
            elif profile == "MEDIUM":
                score += 0.15
            elif profile == "VERY_SHORT":
                score += 0.1

    # Forward return evidence (from Phase 301/221)
    has_forward = False
    for col in row.index:
        if "forward_return" in col.lower() or "fwd_ret" in col.lower():
            val = pd.to_numeric(row[col], errors="coerce")
            if not pd.isna(val):
                has_forward = True
                break

    if has_forward:
        score += 0.1

    return min(score, 1.0)  # Cap at 1.0


def tier_from_score(score: float) -> str:
    """Convert confidence score to tier."""
    if score >= 0.7:
        return "HIGH"
    elif score >= 0.4:
        return "MEDIUM"
    else:
        return "LOW"


def run_phase305(**kwargs) -> Dict[str, Any]:
    """Run Phase 305: Confidence Tier Tagger."""
    errors = []

    try:
        # Load signals
        df = load_csv_robust(RECONCILED_CSV)
        if df.empty:
            df = load_csv_robust(FALLBACK_CSV)

        if df.empty:
            return {
                "phase": 305,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"report_file": str(REPORT_PATH), "output_csv": str(OUTPUT_CSV)},
                "errors": [],
            }

        # Load supporting metadata
        decay_data = load_json_safe(DECAY_303_JSON)
        regime_data = load_json_safe(REGIME_302_JSON)

        # Compute confidence tier for each row
        confidence_scores = []
        confidence_tiers = []

        for idx, row in df.iterrows():
            score = compute_confidence_score(row, decay_data, regime_data)
            tier = tier_from_score(score)
            confidence_scores.append(score)
            confidence_tiers.append(tier)

        df["confidence_score"] = confidence_scores
        df["confidence_tier"] = confidence_tiers

        # Save enriched file
        df.to_csv(OUTPUT_CSV, index=False)

        # Generate report
        tier_counts = pd.Series(confidence_tiers).value_counts()

        report_lines = [
            "# System3 Confidence Tiering Report\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Rows Processed**: {len(df)}\n\n",
            "## Confidence Tier Distribution\n\n",
        ]

        for tier in ["HIGH", "MEDIUM", "LOW"]:
            count = tier_counts.get(tier, 0)
            pct = (count / len(df) * 100) if len(df) > 0 else 0.0
            report_lines.append(f"- **{tier}**: {count} ({pct:.1f}%)\n")

        # Examples
        report_lines.append("\n## Examples\n\n")

        high_examples = df[df["confidence_tier"] == "HIGH"].head(3)
        if not high_examples.empty:
            report_lines.append("### HIGH Confidence Examples\n\n")
            for idx, row in high_examples.iterrows():
                report_lines.append(
                    f"- {row.get('underlying', 'N/A')} | Score: {row.get('confidence_score', 0):.3f} | Final Score: {row.get('final_score', 0):.3f}\n"
                )

        low_examples = df[df["confidence_tier"] == "LOW"].head(3)
        if not low_examples.empty:
            report_lines.append("\n### LOW Confidence Examples\n\n")
            for idx, row in low_examples.iterrows():
                report_lines.append(
                    f"- {row.get('underlying', 'N/A')} | Score: {row.get('confidence_score', 0):.3f} | Final Score: {row.get('final_score', 0):.3f}\n"
                )

        # Per-underlying mix
        if "underlying" in df.columns:
            report_lines.append("\n## Confidence Mix by Underlying\n\n")
            report_lines.append("| Underlying | HIGH | MEDIUM | LOW |\n")
            report_lines.append("|------------|------|--------|-----|\n")

            for underlying in df["underlying"].unique():
                df_u = df[df["underlying"] == underlying]
                high_count = (df_u["confidence_tier"] == "HIGH").sum()
                med_count = (df_u["confidence_tier"] == "MEDIUM").sum()
                low_count = (df_u["confidence_tier"] == "LOW").sum()
                report_lines.append(f"| {underlying} | {high_count} | {med_count} | {low_count} |\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        return {
            "phase": 305,
            "status": "OK",
            "details": f"Tagged {len(df)} signals with confidence tiers",
            "outputs": {
                "rows_tagged": len(df),
                "high_count": int(tier_counts.get("HIGH", 0)),
                "medium_count": int(tier_counts.get("MEDIUM", 0)),
                "low_count": int(tier_counts.get("LOW", 0)),
                "report_file": str(REPORT_PATH),
                "output_csv": str(OUTPUT_CSV),
            },
            "errors": errors,
        }

    except Exception as e:
        errors.append(str(e))
        return {
            "phase": 305,
            "status": "ERROR",
            "details": f"Exception: {e}",
            "outputs": {"report_file": str(REPORT_PATH), "output_csv": str(OUTPUT_CSV)},
            "errors": errors,
        }
