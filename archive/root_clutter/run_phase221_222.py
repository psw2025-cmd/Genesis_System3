#!/usr/bin/env python3
"""Run Phase 221 and 222 to generate forward returns and EV tables."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.system3_phase221_forward_returns import run_phase221
from core.engine.system3_phase222_signal_edge import run_phase222

print("=" * 80)
print("RUNNING PHASE 221: FORWARD RETURNS CALCULATOR")
print("=" * 80)
result221 = run_phase221()
print(f"Status: {result221['status']}")
print(f"Details: {result221['details']}")
if result221.get("outputs"):
    print(f"Output: {result221['outputs']['output_file']}")
    print(f"Rows processed: {result221['outputs']['rows_processed']}")
    if "rows_with_forward_returns" in result221["outputs"]:
        print(f"Rows with forward returns: {result221['outputs']['rows_with_forward_returns']}")

print("\n" + "=" * 80)
print("RUNNING PHASE 222: SIGNAL EDGE ESTIMATOR")
print("=" * 80)
result222 = run_phase222()
print(f"Status: {result222['status']}")
print(f"Details: {result222['details']}")
if result222.get("outputs"):
    print(f"Report: {result222['outputs']['report_path']}")
    print(f"EV Tables: {result222['outputs']['ev_tables_created']}")

print("\n" + "=" * 80)
print("COMPLETE")
print("=" * 80)

