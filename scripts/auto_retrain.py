"""
Auto Retrain — Retrain Signal Consumer
=======================================
Reads state/retrain_signal.json emitted by MarketResultValidator when
Spearman ρ < 0.40 for 3 consecutive days.

If signal exists and data prerequisites are met:
  1. Backs up current models
  2. Calls train_blended_models() directly (no interactive prompt)
  3. Clears retrain_signal.json on success
  4. Logs outcome to CHANGE_LOG.md

Scheduled at 16:00 IST weekdays by system3_job_scheduler.

Usage:
  python scripts/auto_retrain.py
  python scripts/auto_retrain.py --force    # run even without signal file
  python scripts/auto_retrain.py --dry-run  # check signal, no actual training
"""

import argparse
import json
import os
import sys
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

RETRAIN_SIGNAL_FILE = os.path.join(ROOT_DIR, "state", "retrain_signal.json")
CHANGE_LOG_FILE = os.path.join(ROOT_DIR, "CHANGE_LOG.md")
SYSTEM_STATE_FILE = os.path.join(ROOT_DIR, "SYSTEM_STATE.md")


def _log_to_change_log(message: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n**[{ts}] [auto_retrain.py]** {message}\n"
    try:
        with open(CHANGE_LOG_FILE, "a") as f:
            f.write(entry)
    except Exception:
        pass


def _read_signal() -> dict:
    if not os.path.exists(RETRAIN_SIGNAL_FILE):
        return {}
    try:
        with open(RETRAIN_SIGNAL_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _clear_signal() -> None:
    try:
        os.remove(RETRAIN_SIGNAL_FILE)
        print("  Retrain signal cleared.")
    except FileNotFoundError:
        pass


def _check_prerequisites() -> tuple[bool, str]:
    """Returns (ready, reason)."""
    from pathlib import Path

    blended_csv = Path(ROOT_DIR) / "storage" / "training" / "dhan_blended_training_preview.csv"
    if not blended_csv.exists():
        return False, f"Blended training CSV missing: {blended_csv}"

    try:
        import pandas as pd
        df = pd.read_csv(blended_csv)
        if df.empty:
            return False, "Blended training CSV is empty — run dataset builder first"
        if len(df) < 500:
            return False, f"Too few training rows ({len(df)}) — need ≥ 500 for reliable training"
        return True, f"Prerequisites OK — {len(df)} training rows available"
    except Exception as e:
        return False, f"Could not read training CSV: {e}"


def run_retrain(dry_run: bool = False) -> dict:
    """Execute model retraining. Returns result dict."""
    print(f"\n{'='*60}")
    print(f"  AUTO RETRAIN — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    # Check prerequisites before importing heavy dependencies
    ok, reason = _check_prerequisites()
    if not ok:
        print(f"  SKIP: {reason}")
        _log_to_change_log(f"RETRAIN SKIPPED: {reason}")
        return {"status": "SKIPPED", "reason": reason}

    print(f"  {reason}")

    if dry_run:
        print("  DRY RUN — prerequisites OK, training would proceed")
        return {"status": "DRY_RUN", "reason": reason}

    try:
        from core.engine.dhan_blended_model_trainer_v2 import (
            train_blended_models,
            backup_existing_models,
        )
    except ImportError as e:
        msg = f"Cannot import trainer: {e}"
        print(f"  ERROR: {msg}")
        _log_to_change_log(f"RETRAIN FAILED: {msg}")
        return {"status": "ERROR", "reason": msg}

    print("  Backing up existing models...")
    try:
        backup_existing_models()
        print("  Backup complete.")
    except Exception as e:
        print(f"  WARNING: backup failed ({e}) — continuing with training")

    print("  Training models (this may take several minutes)...")
    started_at = datetime.now()

    try:
        result = train_blended_models()
    except Exception as e:
        msg = f"Training raised exception: {e}"
        print(f"  ERROR: {msg}")
        _log_to_change_log(f"RETRAIN FAILED: {msg}")
        return {"status": "ERROR", "reason": msg}

    elapsed = (datetime.now() - started_at).total_seconds()

    if result.get("status") == "SUCCESS":
        trained = [u for u, r in result.get("results", {}).items() if r.get("status") == "SUCCESS"]
        failed = [u for u, r in result.get("results", {}).items() if r.get("status") != "SUCCESS"]
        print(f"\n  RETRAIN COMPLETE ({elapsed:.0f}s):")
        for underlying, r in result.get("results", {}).items():
            acc = r.get("accuracy", 0)
            status = "OK" if r.get("status") == "SUCCESS" else "FAIL"
            print(f"    {underlying:14s}  [{status}]  accuracy={acc:.4f}")
        if failed:
            print(f"\n  WARNING: {len(failed)} underlying(s) failed: {failed}")

        _clear_signal()
        summary = f"RETRAIN SUCCESS in {elapsed:.0f}s: {trained} OK, {failed} failed"
        _log_to_change_log(summary)
        return {"status": "SUCCESS", "trained": trained, "failed": failed, "elapsed_s": elapsed}

    else:
        msg = result.get("message", "unknown error")
        print(f"  RETRAIN FAILED: {msg}")
        _log_to_change_log(f"RETRAIN FAILED: {msg}")
        return {"status": "ERROR", "reason": msg}


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto retrain trigger — reads retrain_signal.json")
    parser.add_argument("--force", action="store_true", help="Train even without retrain signal")
    parser.add_argument("--dry-run", action="store_true", help="Check prerequisites only, no training")
    args = parser.parse_args()

    signal = _read_signal()

    if not signal and not args.force:
        print("No retrain signal present — system accuracy is within threshold.")
        print("Use --force to retrain anyway.")
        return

    if signal:
        print(f"\nRetrain signal found:")
        print(f"  Triggered at : {signal.get('triggered_at', 'unknown')}")
        print(f"  Reason       : {signal.get('reason', 'unknown')}")
        print(f"  Action       : {signal.get('action', 'unknown')}")
    else:
        print("\nNo retrain signal — running because --force specified.")

    result = run_retrain(dry_run=args.dry_run)

    if result["status"] == "SUCCESS":
        print("\n  Next step: signal engine will use new models at next run (09:00 IST)")
    elif result["status"] == "SKIPPED":
        print("\n  Action required: build blended training dataset first")
        print("  Run: python core/engine/dhan_blended_data_builder.py")


if __name__ == "__main__":
    main()
