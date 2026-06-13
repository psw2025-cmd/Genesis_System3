"""Inspect lines around a problematic CSV row for debugging.

Usage:
  .\venv\Scripts\python.exe tools\inspect_training_csv.py --start 2988 --end 3005
"""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "storage" / "training" / "dhan_index_options_training.csv"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=2995)
    parser.add_argument("--end", type=int, default=3005)
    args = parser.parse_args()

    if not CSV.exists():
        print("CSV not found:", CSV)
        return
    with CSV.open("r", encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    start = max(0, args.start)
    end = min(len(lines), args.end)
    for i in range(start, end + 1):
        print(f"{i+1:6d}: {lines[i]}")


if __name__ == "__main__":
    main()
