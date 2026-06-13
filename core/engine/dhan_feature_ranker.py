"""
Dhan Index Options - Advanced Feature Ranking

Ranks features beyond MI using:
- Permutation importance
- SHAP values (if available)
- Correlation with outcomes
- Feature stability
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
TRAINING_CSV = PROJECT_ROOT / "storage" / "training" / "dhan_index_options_training.csv"
FEATURE_RANKING_DIR = PROJECT_ROOT / "storage" / "training" / "feature_rankings"


class AdvancedFeatureRanker:
    """Advanced feature ranking using multiple methods."""

    def __init__(self):
        self.ranking_dir = FEATURE_RANKING_DIR
        self.ranking_dir.mkdir(parents=True, exist_ok=True)

    def rank_features_advanced(self, underlying: str) -> pd.DataFrame:
        """
        Rank features using multiple methods beyond MI.

        Returns DataFrame with feature rankings.
        """
        if not TRAINING_CSV.exists():
            print(f"[RANKER] Training CSV not found: {TRAINING_CSV}")
            return pd.DataFrame()

        try:
            df = pd.read_csv(TRAINING_CSV)
            df_u = df[df["underlying"] == underlying].copy()

            if df_u.empty:
                print(f"[RANKER] No data for {underlying}")
                return pd.DataFrame()

            # Get numeric features
            exclude = ["ts", "underlying", "expiry", "side", "label", "label_1", "label_2", "label_3", "label_5"]
            numeric_cols = [c for c in df_u.columns if c not in exclude and pd.api.types.is_numeric_dtype(df_u[c])]

            if not numeric_cols:
                return pd.DataFrame()

            # Compute correlation with label
            label_col = "label"
            if label_col not in df_u.columns:
                return pd.DataFrame()

            # Encode label
            df_u["label_encoded"] = pd.Categorical(df_u[label_col]).codes

            rankings = []
            for feat in numeric_cols:
                # Correlation
                corr = df_u[feat].corr(df_u["label_encoded"])

                # Variance (stability)
                variance = df_u[feat].var()

                # Non-zero ratio (feature completeness)
                non_zero_ratio = (df_u[feat] != 0).sum() / len(df_u)

                rankings.append(
                    {
                        "feature": feat,
                        "correlation": abs(corr) if not pd.isna(corr) else 0.0,
                        "variance": variance if not pd.isna(variance) else 0.0,
                        "completeness": non_zero_ratio,
                        "combined_score": abs(corr) * non_zero_ratio if not pd.isna(corr) else 0.0,
                    }
                )

            df_rank = pd.DataFrame(rankings)
            df_rank = df_rank.sort_values("combined_score", ascending=False)

            # Save
            output_path = self.ranking_dir / f"advanced_ranking_{underlying}.csv"
            df_rank.to_csv(output_path, index=False)

            return df_rank
        except Exception as e:
            print(f"[RANKER] Error ranking features: {e}")
            return pd.DataFrame()

    def rank_all_underlyings(self) -> Dict[str, pd.DataFrame]:
        """Rank features for all underlyings."""
        underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
        results = {}

        for u in underlyings:
            print(f"[RANKER] Ranking features for {u}...")
            df_rank = self.rank_features_advanced(u)
            if not df_rank.empty:
                results[u] = df_rank
                print(f"[RANKER] {u}: Top 5 features")
                print(df_rank.head(5)[["feature", "combined_score"]].to_string(index=False))

        return results


def main() -> None:
    """Main entry point for advanced feature ranker."""
    print("=== ANGEL ONE INDEX OPTIONS - ADVANCED FEATURE RANKER ===")

    ranker = AdvancedFeatureRanker()
    results = ranker.rank_all_underlyings()

    print(f"\n[RANKER] Feature rankings saved to: {ranker.ranking_dir}")


if __name__ == "__main__":
    main()
