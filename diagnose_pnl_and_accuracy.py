import pandas as pd
import numpy as np
from pathlib import Path
import os

def diagnose():
    print("=" * 60)
    print("💎 GENESIS SYSTEM3: PNL & ACCURACY DIAGNOSTIC")
    print("=" * 60)
    
    signals_path = Path("storage/live/angel_index_ai_signals.csv")
    if not signals_path.exists():
        print(f"❌ Signals file not found: {signals_path}")
        return

    try:
        df = pd.read_csv(signals_path)
        print(f"📊 Loaded {len(df)} signals.")
        
        if df.empty:
            print("❌ Signals file is empty.")
            return

        # 1. Signal Distribution
        print("
[1] Signal Distribution:")
        if "signal" in df.columns:
            print(df["signal"].value_counts())
        else:
            print("❌ 'signal' column missing.")

        # 2. Score Statistics
        print("
[2] Final Score Stats:")
        if "final_score" in df.columns:
            print(df["final_score"].describe())
            zeros = (df["final_score"].abs() < 0.0001).sum()
            print(f"  Zeros: {zeros} ({zeros/len(df):.1%})")
        else:
            print("❌ 'final_score' column missing.")

        # 3. AI Score Statistics
        print("
[3] AI Score Stats:")
        if "ai_score" in df.columns:
            print(df["ai_score"].describe())
            unique_ai = df["ai_score"].nunique()
            print(f"  Unique AI values: {unique_ai}")
        else:
            print("❌ 'ai_score' column missing.")

        # 4. Profit Potential (Basic)
        print("
[4] Signal Quality (Moneyness vs Score):")
        if "spot" in df.columns and "strike" in df.columns and "side" in df.columns:
            df["moneyness"] = (df["spot"] - df["strike"]) / df["strike"]
            # Correct for PE
            df.loc[df["side"] == "PE", "moneyness"] *= -1
            
            corr = df["moneyness"].corr(df["final_score"])
            print(f"  Moneyness-Score Correlation: {corr:.4f}")
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")

if __name__ == "__main__":
    diagnose()
