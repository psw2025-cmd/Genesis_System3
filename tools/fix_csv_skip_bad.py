"""Skip bad rows by using pandas with on_bad_lines='skip'."""

import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "storage" / "training" / "dhan_index_options_training.csv"
if not CSV.exists():
    print("CSV missing", CSV)
    raise SystemExit(1)

bak = CSV.with_suffix(".csv.bak3")
print("Backing up original to", bak)
shutil.copy2(CSV, bak)

print("Reading CSV with on_bad_lines=skip")
try:
    df = pd.read_csv(CSV, on_bad_lines="skip")
    print("Rows read:", len(df))
    print("Cols read:", len(df.columns))
except Exception as e:
    print("Failed:", e)
    raise SystemExit(1)

print("Writing cleaned CSV back")
df.to_csv(CSV, index=False, quoting=1)  # quoting=csv.QUOTE_ALL to be safe
print("Done")
