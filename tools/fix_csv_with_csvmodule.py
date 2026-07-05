"""Fix CSV by accumulating physical lines until csv.reader returns expected field count.

This is more robust than naive split(). It preserves quoting behavior.
"""

import csv
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "storage" / "training" / "dhan_index_options_training.csv"
if not CSV.exists():
    print("CSV missing", CSV)
    raise SystemExit(1)

bak = CSV.with_suffix(".csv.broken2.bak")
print("Backing up original to", bak)
shutil.copy2(CSV, bak)

text = CSV.read_text(encoding="utf-8", errors="replace")
lines = text.splitlines()
if not lines:
    print("empty file")
    raise SystemExit(1)

header = lines[0]
# determine expected fields using csv.reader on header
expected = len(next(csv.reader([header])))
print("Header fields expected:", expected)

out = [header]
N = len(lines)
i = 1
while i < N:
    chunk = lines[i]
    j = i
    parsed = None
    while True:
        try:
            parsed = next(csv.reader([chunk]))
            if len(parsed) == expected:
                out.append(chunk)
                i = j + 1
                break
            else:
                # need to append next physical line
                j += 1
                if j >= N:
                    # end of file, accept whatever
                    out.append(chunk)
                    i = j
                    break
                chunk = chunk + "\n" + lines[j]
        except Exception:
            # try appending next line
            j += 1
            if j >= N:
                out.append(chunk)
                i = j
                break
            chunk = chunk + "\n" + lines[j]

clean = CSV.with_suffix(".csv.fixed2.csv")
clean.write_text("\n".join(out), encoding="utf-8", newline="")
print("Wrote cleaned file to", clean)
shutil.copy2(clean, CSV)
print("Replaced original with cleaned file")
