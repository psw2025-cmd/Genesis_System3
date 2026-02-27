"""
System3 - Overall Status Check Script

Run this to see the complete present state of System3.
"""

import os
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

print("=" * 70)
print("SYSTEM3 - OVERALL STATUS CHECK")
print("=" * 70)
print()

# Check key directories
print("=== DIRECTORY STRUCTURE ===")
dirs_to_check = [
    "core/engine",
    "core/models/angel_one",
    "storage/live",
    "storage/training",
    "storage/config",
    "storage/reports",
    "storage/learning",
    "storage/backtests",
]

for dir_path in dirs_to_check:
    full_path = ROOT_DIR / dir_path
    exists = "✅" if full_path.exists() else "❌"
    count = len(list(full_path.glob("*"))) if full_path.exists() else 0
    print(f"{exists} {dir_path}: {count} files")

print()

# Check key files
print("=== KEY FILES ===")
files_to_check = [
    "run_system3.py",
    "core/engine/angel_live_ai_signals.py",
    "core/engine/angel_trade_decision.py",
    "core/engine/angel_trade_executor.py",
    "core/engine/angel_pnl_simulator.py",
    "storage/training/angel_index_options_training.csv",
    "storage/live/angel_index_ai_signals.csv",
]

for file_path in files_to_check:
    full_path = ROOT_DIR / file_path
    exists = "✅" if full_path.exists() else "❌"
    size = full_path.stat().st_size if full_path.exists() else 0
    print(f"{exists} {file_path}: {size:,} bytes")

print()

# Check models
print("=== TRAINED MODELS ===")
models_dir = ROOT_DIR / "core" / "models" / "angel_one"
if models_dir.exists():
    models = list(models_dir.glob("*_model.pkl"))
    for model in models:
        size = model.stat().st_size
        print(f"✅ {model.name}: {size:,} bytes")
    if not models:
        print("❌ No models found")
else:
    print("❌ Models directory not found")

print()

# Check configuration
print("=== CONFIGURATION STATUS ===")
try:
    from core.engine.angel_trade_config import DEFAULT_THRESHOLDS
    print(f"✅ Trade Thresholds:")
    print(f"   min_confidence: {DEFAULT_THRESHOLDS.min_confidence}")
    print(f"   min_abs_score: {DEFAULT_THRESHOLDS.min_abs_score}")
    print(f"   target_pct: {DEFAULT_THRESHOLDS.target_pct}")
    print(f"   stoploss_pct: {DEFAULT_THRESHOLDS.stoploss_pct}")
except Exception as e:
    print(f"❌ Failed to load trade config: {e}")

try:
    from core.engine.angel_automation_config import AUTOMATION_CONFIG
    print(f"✅ Automation Config:")
    print(f"   auto_execute_trades: {AUTOMATION_CONFIG.auto_execute_trades}")
    print(f"   auto_simulate_pnl: {AUTOMATION_CONFIG.auto_simulate_pnl}")
except Exception as e:
    print(f"❌ Failed to load automation config: {e}")

print()

# Check data files
print("=== DATA FILES STATUS ===")
data_files = [
    ("Signals CSV", "storage/live/angel_index_ai_signals.csv"),
    ("Trade Plans CSV", "storage/live/angel_index_ai_trades_plan.csv"),
    ("Execution Log CSV", "storage/live/angel_index_ai_trades_exec_log.csv"),
    ("PnL Log CSV", "storage/live/angel_index_ai_pnl_log.csv"),
    ("Training CSV", "storage/training/angel_index_options_training.csv"),
    ("Outcomes CSV", "storage/learning/angel_real_outcomes.csv"),
]

for name, file_path in data_files:
    full_path = ROOT_DIR / file_path
    if full_path.exists():
        import pandas as pd
        try:
            df = pd.read_csv(full_path)
            rows = len(df)
            print(f"✅ {name}: {rows:,} rows")
        except Exception:
            print(f"⚠️  {name}: File exists but cannot read")
    else:
        print(f"❌ {name}: Not found")

print()

# Check menu system
print("=== MENU SYSTEM ===")
try:
    # Count menu options by reading run_system3.py
    with open(ROOT_DIR / "run_system3.py", "r", encoding="utf-8") as f:
        content = f.read()
        menu_count = content.count("elif choice ==")
        print(f"✅ Menu options detected: {menu_count}")
        print(f"✅ Menu file: run_system3.py")
except Exception as e:
    print(f"❌ Failed to check menu: {e}")

print()

# Check Ultra-Mode status
print("=== ULTRA-MODE STATUS ===")
try:
    from core.engine.angel_ultramode_prep import load_ultramode_config
    config = load_ultramode_config()
    print(f"✅ Live Execution: {'❌ DISABLED' if not config.live_execution_enabled else '⚠️ ENABLED'}")
    print(f"✅ Auto Trade: {'❌ DISABLED' if not config.auto_trade_execution else '⚠️ ENABLED'}")
    print(f"✅ Read-Only Mode: {'✅ ACTIVE' if config.read_only_mode else '❌ INACTIVE'}")
except Exception as e:
    print(f"⚠️  Ultra-Mode check failed: {e}")

print()

# Summary
print("=" * 70)
print("STATUS CHECK COMPLETE")
print("=" * 70)
print()
print("Next steps:")
print("1. Run: python run_system3.py (to see full menu)")
print("2. Run: python -m core.engine.angel_real_outcome_logger (test logger)")
print("3. Run: python -m core.engine.angel_ultramode_prep (check Ultra-Mode)")
print("4. Run: python -m core.engine.angel_daily_auto_reports (generate reports)")

