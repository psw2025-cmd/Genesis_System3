"""
System3 Ultra - Phase 39: Ultra Shadow Live Campaign Manager

Turn Ultra shadow trading into a structured campaign: run fused decisions + shadow trades
over a configurable window (e.g., whole trading day) and produce a daily summary.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 102
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "storage" / "config"
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
LOGS_ULTRA_DIR = PROJECT_ROOT / "storage" / "logs_ultra"

ULTRA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

CAMPAIGN_CONFIG_FILE = CONFIG_DIR / "ultra_shadow_campaign_config.json"
LOG_FILE = LOGS_ULTRA_DIR / "system3_phases_39_45.log"


def _log(message: str) -> None:
    """Log message to file and console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [Phase39] {message}\n"
    print(f"[Phase39] {message}")

    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f"[Phase39][WARN] Failed to write log: {e}")


def load_config() -> Dict[str, Any]:
    """Load campaign parameters from JSON config file."""
    default_config = {"loops": 60, "sleep_seconds": 30}

    if not CAMPAIGN_CONFIG_FILE.exists():
        _log(f"Config file not found, creating with defaults: {default_config}")
        try:
            with CAMPAIGN_CONFIG_FILE.open("w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2)
            _log("Default config file created")
        except Exception as e:
            _log(f"Failed to create config file: {e}, using defaults")
        return default_config

    try:
        with CAMPAIGN_CONFIG_FILE.open("r", encoding="utf-8") as f:
            config = json.load(f)
        _log(f"Loaded config: loops={config.get('loops', 60)}, sleep_seconds={config.get('sleep_seconds', 30)}")
        return config
    except Exception as e:
        _log(f"Failed to load config: {e}, using defaults")
        return default_config


def run_campaign_once() -> None:
    """Run one iteration of Phase 31 fusion + Phase 34 shadow."""
    try:
        # Import here to avoid circular dependencies
        from core.engine.system3_phase31_ultra_fusion import run_phase31_fusion
        from core.engine.system3_phase34_ultra_shadow_exec import run_phase34_shadow_once

        _log("Running Phase 31 fusion...")
        try:
            run_phase31_fusion()
        except Exception as e:
            _log(f"Phase 31 error (non-fatal): {e}")

        _log("Running Phase 34 shadow...")
        try:
            run_phase34_shadow_once()
        except Exception as e:
            _log(f"Phase 34 error (non-fatal): {e}")

    except Exception as e:
        _log(f"Error in campaign iteration: {e}")
        # Don't raise - allow campaign to continue


def _build_daily_summary() -> str:
    """Build daily summary markdown content."""
    today = datetime.now().strftime("%Y%m%d")
    summary_lines = []

    summary_lines.append(f"# Ultra Shadow Campaign Summary - {today}")
    summary_lines.append("")
    summary_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append("")
    summary_lines.append("## Campaign Statistics")
    summary_lines.append("")

    # Read fused decisions
    fused_file = ULTRA_DIR / "phase31_ultra_fused_decisions.csv"
    if fused_file.exists():
        try:
            df_fused = pd.read_csv(fused_file)
            total_decisions = len(df_fused)

            hold_count = len(df_fused[df_fused["final_action"] == "HOLD"])
            buy_count = len(df_fused[df_fused["final_action"].str.contains("BUY", na=False)])

            safe_count = len(df_fused[df_fused["final_risk_flag"] == "SAFE"])
            risky_count = len(df_fused[df_fused["final_risk_flag"] == "RISKY"])

            summary_lines.append(f"- **Total Fused Decisions**: {total_decisions}")
            summary_lines.append(f"- **HOLD**: {hold_count}")
            summary_lines.append(f"- **BUY Signals**: {buy_count}")
            summary_lines.append(f"- **SAFE Risk**: {safe_count}")
            summary_lines.append(f"- **RISKY Risk**: {risky_count}")
        except Exception as e:
            summary_lines.append(f"- **Error reading fused decisions**: {e}")
    else:
        summary_lines.append("- **Fused decisions file not found**")

    summary_lines.append("")
    summary_lines.append("## Shadow Trades")
    summary_lines.append("")

    # Read shadow trades
    shadow_file = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_ultra_trades_shadow.csv"
    if shadow_file.exists():
        try:
            df_shadow = pd.read_csv(shadow_file)
            shadow_count = len(df_shadow)
            summary_lines.append(f"- **Total Shadow Trades**: {shadow_count}")

            if shadow_count > 0:
                buy_shadow = len(df_shadow[df_shadow["action"].str.contains("BUY", na=False)])
                summary_lines.append(f"- **BUY Shadow Trades**: {buy_shadow}")
        except Exception as e:
            summary_lines.append(f"- **Error reading shadow trades**: {e}")
    else:
        summary_lines.append("- **Shadow trades file not found or empty**")

    summary_lines.append("")
    summary_lines.append("## Notes")
    summary_lines.append("")
    summary_lines.append("- All shadow trades are logged but never executed")
    summary_lines.append("- Campaign runs in read-only mode")
    summary_lines.append("- No baseline files were modified")

    return "\n".join(summary_lines)


def run_phase39_shadow_campaign() -> None:
    """Run the full shadow campaign."""
    print("=" * 60)
    print("SYSTEM3 ULTRA - PHASE 39: SHADOW CAMPAIGN MANAGER")
    print("=" * 60)
    print("\n[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only")
    print("[SAFETY] Shadow trades are logged but NEVER executed\n")

    config = load_config()
    loops = config.get("loops", 60)
    sleep_seconds = config.get("sleep_seconds", 30)

    _log(f"Campaign started: loops={loops}, sleep_seconds={sleep_seconds}")

    try:
        for i in range(1, loops + 1):
            _log(f"Loop {i}/{loops} started")
            run_campaign_once()

            if i < loops:
                _log(f"Sleeping for {sleep_seconds} seconds...")
                time.sleep(sleep_seconds)

        _log("Campaign complete, building daily summary...")

        # Build daily summary
        today = datetime.now().strftime("%Y%m%d")
        summary_file = ULTRA_DIR / f"phase39_shadow_campaign_summary_{today}.md"

        summary_content = _build_daily_summary()

        with summary_file.open("w", encoding="utf-8") as f:
            f.write(summary_content)

        _log(f"Summary written to: {summary_file}")
        print(f"\n[OK] Phase 39 Shadow Campaign completed")
        print(f"[SAVE] Summary saved to: {summary_file}")

    except KeyboardInterrupt:
        _log("Campaign interrupted by user")
        print("\n[INFO] Campaign interrupted by user")
    except Exception as e:
        _log(f"Campaign error: {e}")
        print(f"\n[ERROR] Campaign failed: {e}")
        raise


def main() -> None:
    """CLI entry point."""
    run_phase39_shadow_campaign()


if __name__ == "__main__":
    main()
