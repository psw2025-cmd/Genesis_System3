"""
Dhan Token Watchdog Runner — standalone process entry point.
Imports and runs the watchdog loop from core/brokers/dhan/token_watchdog.py.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.brokers.dhan.token_watchdog import run_watchdog_loop
run_watchdog_loop()
