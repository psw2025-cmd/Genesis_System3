"""
System3 Ultra Runtime Loops

Provides continuous runtime loops for:
- Live signal generation
- Decision auditing
- Snapshot generation
- Logging
- Health checks

All operations are shadow-only, read-only, with safety guards.
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

# Ensure project root is in path
ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.engine.ultra_safety import load_ultra_safety
from core.engine.angel_automation_config import AUTOMATION_CONFIG


def check_safety() -> bool:
    """Check if all safety mechanisms are in place."""
    safety = load_ultra_safety()
    if AUTOMATION_CONFIG.auto_execute_trades:
        print("[ERROR] Auto-execute is ENABLED. Disable before running loops.")
        return False
    if safety.get("AUTO_EXECUTE_TRADES", False):
        print("[ERROR] Ultra auto-execute is ENABLED. Disable before running loops.")
        return False
    return True


def live_signal_loop(interval_sec: int = 30, max_iterations: Optional[int] = None):
    """
    Continuous live signal generation loop.
    
    Args:
        interval_sec: Seconds between snapshots
        max_iterations: Maximum iterations (None for infinite)
    """
    if not check_safety():
        return
    
    print("=== SYSTEM3 ULTRA - LIVE SIGNAL LOOP ===")
    print(f"Interval: {interval_sec} seconds")
    print(f"Max iterations: {max_iterations or 'Infinite'}")
    print("[SAFETY] Shadow-only, no real trades\n")
    
    try:
        from core.brokers.angel_one.broker import AngelOneBroker
        from core.engine.angel_options_watch_loop import _build_full_snapshot
        from core.engine import angel_live_ai_signals
        
        broker = AngelOneBroker()
        print("Broker initialized.\n")
        
        iteration = 0
        while True:
            iteration += 1
            if max_iterations and iteration > max_iterations:
                break
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Snapshot #{iteration}...")
            try:
                df_snap = _build_full_snapshot(broker)
                if df_snap is not None and not df_snap.empty:
                    angel_live_ai_signals.run_once_with_snapshot(df_snap)
                    print(f"  -> Signals generated")
                else:
                    print("  -> No data")
            except Exception as e:
                print(f"  -> Error: {e}")
            
            if iteration < (max_iterations or float('inf')):
                time.sleep(interval_sec)
                
    except KeyboardInterrupt:
        print("\n[INFO] Loop interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] Loop failed: {e}")


def decision_audit_loop(interval_sec: int = 300, max_iterations: Optional[int] = None):
    """
    Continuous decision auditing loop.
    
    Args:
        interval_sec: Seconds between audits
        max_iterations: Maximum iterations (None for infinite)
    """
    if not check_safety():
        return
    
    print("=== SYSTEM3 ULTRA - DECISION AUDIT LOOP ===")
    print(f"Interval: {interval_sec} seconds")
    print(f"Max iterations: {max_iterations or 'Infinite'}")
    print("[SAFETY] Read-only, no changes\n")
    
    try:
        from core.engine.system3_phase35_ultra_auditor import run_phase35_audit
        
        iteration = 0
        while True:
            iteration += 1
            if max_iterations and iteration > max_iterations:
                break
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Audit #{iteration}...")
            try:
                run_phase35_audit()
                print("  -> Audit complete")
            except Exception as e:
                print(f"  -> Error: {e}")
            
            if iteration < (max_iterations or float('inf')):
                time.sleep(interval_sec)
                
    except KeyboardInterrupt:
        print("\n[INFO] Loop interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] Loop failed: {e}")


def snapshot_generation_loop(interval_sec: int = 3600, max_iterations: Optional[int] = None):
    """
    Periodic snapshot generation loop.
    
    Args:
        interval_sec: Seconds between snapshots
        max_iterations: Maximum iterations (None for infinite)
    """
    if not check_safety():
        return
    
    print("=== SYSTEM3 ULTRA - SNAPSHOT GENERATION LOOP ===")
    print(f"Interval: {interval_sec} seconds")
    print(f"Max iterations: {max_iterations or 'Infinite'}")
    print("[SAFETY] Snapshot directory only\n")
    
    try:
        from core.engine.system3_phase42_snapshot_manager import run_phase42_snapshot_create
        
        iteration = 0
        while True:
            iteration += 1
            if max_iterations and iteration > max_iterations:
                break
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Snapshot #{iteration}...")
            try:
                run_phase42_snapshot_create()
                print("  -> Snapshot created")
            except Exception as e:
                print(f"  -> Error: {e}")
            
            if iteration < (max_iterations or float('inf')):
                time.sleep(interval_sec)
                
    except KeyboardInterrupt:
        print("\n[INFO] Loop interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] Loop failed: {e}")


def health_check_loop(interval_sec: int = 600, max_iterations: Optional[int] = None):
    """
    Periodic health check loop.
    
    Args:
        interval_sec: Seconds between checks
        max_iterations: Maximum iterations (None for infinite)
    """
    if not check_safety():
        return
    
    print("=== SYSTEM3 ULTRA - HEALTH CHECK LOOP ===")
    print(f"Interval: {interval_sec} seconds")
    print(f"Max iterations: {max_iterations or 'Infinite'}")
    print("[SAFETY] Read-only, no changes\n")
    
    try:
        from core.engine.health_check import main as health_main
        
        iteration = 0
        while True:
            iteration += 1
            if max_iterations and iteration > max_iterations:
                break
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Health check #{iteration}...")
            try:
                health_main()
                print("  -> Health check complete")
            except Exception as e:
                print(f"  -> Error: {e}")
            
            if iteration < (max_iterations or float('inf')):
                time.sleep(interval_sec)
                
    except KeyboardInterrupt:
        print("\n[INFO] Loop interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] Loop failed: {e}")


def main():
    """Main entry point for runtime loops."""
    print("\n" + "="*70)
    print("SYSTEM3 ULTRA - RUNTIME LOOPS")
    print("="*70)
    print("\nSelect loop type:")
    print("1) Live Signal Loop (30s interval)")
    print("2) Decision Audit Loop (5min interval)")
    print("3) Snapshot Generation Loop (1hr interval)")
    print("4) Health Check Loop (10min interval)")
    print("0) Exit")
    
    choice = input("\nSelect: ").strip()
    
    if choice == "1":
        live_signal_loop()
    elif choice == "2":
        decision_audit_loop()
    elif choice == "3":
        snapshot_generation_loop()
    elif choice == "4":
        health_check_loop()
    elif choice == "0":
        print("Exiting.")
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()

