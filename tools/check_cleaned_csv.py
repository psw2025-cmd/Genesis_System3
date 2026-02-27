from pathlib import Path
import sys

p = Path("storage/training/angel_index_options_training.csv")
if not p.exists():
    print("missing", p)
    sys.exit(1)
import pandas as pd

try:
    df = pd.read_csv(p)
    print("rows=", len(df))
    print("cols=", len(df.columns))
    print("columns=", df.columns.tolist()[:10])
except Exception as e:
    print("read failed:", e)
    sys.exit(2)
