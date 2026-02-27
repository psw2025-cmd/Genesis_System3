"""Attempt to clean malformed CSV rows by using pandas with tolerant parsing.

This script will:
 - back up the original CSV to `*.bak`
 - attempt to read with `engine='python'` and `on_bad_lines='skip'`
 - write cleaned CSV back to the original path (and also to `*.cleaned.csv`)

Use with the repo venv:
.\venv\\Scripts\\python.exe tools\\clean_training_csv.py
"""

from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "storage" / "training" / "angel_index_options_training.csv"

if not CSV.exists():
    print("CSV not found:", CSV)
    sys.exit(1)

bak = CSV.with_suffix(".csv.bak")
cleaned = CSV.with_name(CSV.stem + ".cleaned.csv")

print("Backing up", CSV, "->", bak)
shutil.copy2(CSV, bak)

try:
    import pandas as pd
except Exception:
    print("pandas required. Install in venv: pip install pandas")
    sys.exit(1)

print("Reading with tolerant parser (python engine, skipping bad lines)")
try:
    df = pd.read_csv(CSV, engine="python", on_bad_lines="skip")
    print("Read rows:", len(df))
    print("Writing cleaned CSV to", cleaned)
    df.to_csv(cleaned, index=False)
    print("Replacing original with cleaned file")
    shutil.copy2(cleaned, CSV)
    print("Clean complete")
except Exception as e:
    print("Failed to clean CSV:", e)
    sys.exit(1)
