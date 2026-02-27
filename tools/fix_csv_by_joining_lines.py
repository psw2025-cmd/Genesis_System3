"""Attempt to fix CSV by joining subsequent physical lines until expected field count is reached.

This is a heuristic: it assumes rows were broken into multiple lines but fields do not contain unescaped newlines.
"""

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "storage" / "training" / "angel_index_options_training.csv"
if not CSV.exists():
    print("CSV missing", CSV)
    raise SystemExit(1)

bak = CSV.with_suffix(".csv.broken.bak")
print("Backing up original to", bak)
shutil.copy2(CSV, bak)

text = CSV.read_text(encoding="utf-8", errors="replace")
lines = text.splitlines()
if not lines:
    print("empty file")
    raise SystemExit(1)

header = lines[0]
expected = len(header.split(","))
print("Header fields expected:", expected)

out_lines = [header]
cur = ""
for ln in lines[1:]:
    if not cur:
        cur = ln
    else:
        # join without adding extra comma/newline; original wraps mid-field
        cur = cur + ln
    # check field count
    parts = cur.split(",")
    if len(parts) >= expected:
        out_lines.append(cur)
        cur = ""
# if leftover, append
if cur:
    out_lines.append(cur)

clean = CSV.with_suffix(".csv.fixed.csv")
clean.write_text("\n".join(out_lines), encoding="utf-8", newline="")
print("Wrote cleaned file to", clean)
# Replace original
shutil.copy2(clean, CSV)
print("Replaced original with cleaned file")
