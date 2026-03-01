import pandas as pd
from pathlib import Path

def inspect_training_data():
    csv_path = Path("storage/training/angel_index_options_training.csv")
    parquet_path = Path("storage/training/angel_ultra_training.parquet")
    
    for path in [csv_path, parquet_path]:
        if not path.exists():
            print(f"File not found: {path}")
            continue
            
        print(f"
{'='*20} Inspecting {path.name} {'='*20}")
        try:
            if path.suffix == ".csv":
                df = pd.read_csv(path)
            else:
                df = pd.read_parquet(path)
                
            print(f"Shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()[:10]} ...")
            
            if "underlying" in df.columns:
                print("
Samples per Underlying:")
                print(df["underlying"].value_counts())
                
                # Check labels for a few underlyings
                for u in df["underlying"].unique()[:5]:
                    df_u = df[df["underlying"] == u]
                    label_cols = [c for c in df.columns if 'label' in c]
                    if label_cols:
                        print(f"
Labels for {u} ({label_cols[0]}):")
                        print(df_u[label_cols[0]].value_counts(dropna=False))
                    else:
                        print(f"
No label columns found for {u}")
            else:
                print("No 'underlying' column found.")
                
            # Check for NaNs in first 20 features
            features = df.columns[:20]
            nan_counts = df[features].isna().sum()
            if nan_counts.sum() > 0:
                print("
NaN counts in features:")
                print(nan_counts[nan_counts > 0])
            else:
                print("
No NaNs found in first 20 features.")
                
        except Exception as e:
            print(f"Error reading {path.name}: {e}")

if __name__ == "__main__":
    inspect_training_data()
