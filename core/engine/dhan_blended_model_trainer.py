"""
Dhan Index Options - Blended Model Trainer

Trains models using both synthetic and real market data.
Blends training datasets for improved model performance.
"""

import os
import pandas as pd
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent
SYNTHETIC_CSV = PROJECT_ROOT / "storage" / "training" / "dhan_index_options_training.csv"
REAL_CSV = PROJECT_ROOT / "storage" / "training" / "dhan_index_options_real_training.csv"
BLENDED_CSV = PROJECT_ROOT / "storage" / "training" / "dhan_index_options_blended_training.csv"


class BlendedModelTrainer:
    """Trains models using blended synthetic + real data."""

    def __init__(self):
        self.synthetic_path = SYNTHETIC_CSV
        self.real_path = REAL_CSV
        self.blended_path = BLENDED_CSV

    def build_real_training_from_live(self) -> bool:
        """
        Build real training dataset from live signals and PnL data.

        This will be used after Monday to create real training data.
        """
        from core.engine.build_dhan_training_from_log import main as build_training_main

        try:
            # Use existing training builder
            build_training_main()
            return True
        except Exception as e:
            print(f"[BLENDED] Failed to build real training: {e}")
            return False

    def blend_datasets(self, synthetic_weight: float = 0.5, real_weight: float = 0.5) -> pd.DataFrame | None:
        """
        Blend synthetic and real training datasets.

        Args:
            synthetic_weight: Weight for synthetic data (0.0 to 1.0)
            real_weight: Weight for real data (0.0 to 1.0)
        """
        if not self.synthetic_path.exists():
            print(f"[BLENDED] Synthetic training not found: {self.synthetic_path}")
            return None

        # Load synthetic
        try:
            df_synthetic = pd.read_csv(self.synthetic_path)
        except Exception as e:
            print(f"[BLENDED] Failed to load synthetic: {e}")
            return None

        # Load real if available
        df_real = pd.DataFrame()
        if self.real_path.exists():
            try:
                df_real = pd.read_csv(self.real_path)
            except Exception as e:
                print(f"[BLENDED] Warning: Failed to load real data: {e}")

        # Blend datasets
        if df_real.empty:
            print("[BLENDED] No real data available, using synthetic only")
            df_blended = df_synthetic.copy()
        else:
            # Sample based on weights
            n_synthetic = int(len(df_synthetic) * synthetic_weight)
            n_real = int(len(df_real) * real_weight)

            df_syn_sample = df_synthetic.sample(min(n_synthetic, len(df_synthetic)), random_state=42)
            df_real_sample = df_real.sample(min(n_real, len(df_real)), random_state=42)

            df_blended = pd.concat([df_syn_sample, df_real_sample], ignore_index=True)
            print(
                f"[BLENDED] Blended dataset: {len(df_syn_sample)} synthetic + {len(df_real_sample)} real = {len(df_blended)} total"
            )

        # Save blended dataset
        self.blended_path.parent.mkdir(parents=True, exist_ok=True)
        df_blended.to_csv(self.blended_path, index=False)
        print(f"[BLENDED] Blended training dataset saved to: {self.blended_path}")

        return df_blended


def main() -> None:
    """Main entry point for blended model trainer."""
    print("=== ANGEL ONE INDEX OPTIONS - BLENDED MODEL TRAINER ===")
    print("[INFO] This will blend synthetic and real training data.\n")

    trainer = BlendedModelTrainer()

    # Check if real data exists
    if trainer.real_path.exists():
        print("[INFO] Real training data found. Blending datasets...")
        df_blended = trainer.blend_datasets(synthetic_weight=0.4, real_weight=0.6)
        if df_blended is not None:
            print("[INFO] Blended dataset ready. Run model training to use it.")
    else:
        print("[INFO] No real training data yet. Use synthetic data for now.")
        print("[INFO] After Monday, real data will be available for blending.")


if __name__ == "__main__":
    main()
