"""
System3 Ultra - Phase 37: Ultra Policy & Risk Monitor

Create a single dashboard-style report summarizing:
- Thresholds
- Safety limits
- Trade caps
- Ultra shadow activity
- Any violations from Phase 35

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 100
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
CONFIG_DIR = PROJECT_ROOT / "storage" / "config"

ULTRA_DIR.mkdir(parents=True, exist_ok=True)


def _load_thresholds() -> Dict[str, Any]:
    """Load thresholds (read-only)."""
    thresholds_json = CONFIG_DIR / "thresholds_auto.json"
    if thresholds_json.exists():
        try:
            with thresholds_json.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _load_audit_results() -> Optional[pd.DataFrame]:
    """Load Phase 35 audit results."""
    audit_csv = ULTRA_DIR / "phase35_decision_audit.csv"
    if not audit_csv.exists():
        return None
    try:
        return pd.read_csv(audit_csv)
    except Exception:
        return None


def _load_shadow_trades() -> Optional[pd.DataFrame]:
    """Load shadow Ultra trades."""
    shadow_csv = LIVE_DIR / "angel_index_ai_ultra_trades_shadow.csv"
    if not shadow_csv.exists():
        return None
    try:
        return pd.read_csv(shadow_csv)
    except Exception:
        return None


def run_phase37_policy_risk_dashboard() -> str:
    """
    Run Phase 37: Ultra Policy & Risk Monitor Dashboard.

    Returns:
        Path to dashboard MD file
    """
    print("=== SYSTEM3 ULTRA - PHASE 37: POLICY & RISK MONITOR ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Load data
    thresholds = _load_thresholds()
    df_audit = _load_audit_results()
    df_shadow = _load_shadow_trades()

    print(f"[LOAD] Loaded thresholds (read-only)")
    if df_audit is not None:
        print(f"[LOAD] Loaded audit results: {len(df_audit)} decisions")
    if df_shadow is not None:
        print(f"[LOAD] Loaded shadow trades: {len(df_shadow)} trades")

    # Generate dashboard
    dashboard_md = ULTRA_DIR / "phase37_policy_risk_dashboard.md"
    with dashboard_md.open("w", encoding="utf-8") as f:
        f.write("# Ultra Policy & Risk Dashboard\n\n")
        f.write(f"Generated: {datetime.utcnow().isoformat()}\n\n")

        # Current Safety Settings
        f.write("## Current Safety Settings\n\n")
        f.write("| Setting | Value |\n")
        f.write("|---------|-------|\n")
        f.write(f"| Min Confidence | {thresholds.get('min_confidence', 'N/A')} |\n")
        f.write(f"| Min Score | {thresholds.get('min_abs_score', 'N/A')} |\n")
        f.write(f"| Max ATM Distance % | {thresholds.get('max_atm_dist_pct', 'N/A')} |\n")
        f.write(f"| Target % | {thresholds.get('target_pct', 'N/A')} |\n")
        f.write(f"| Stoploss % | {thresholds.get('stoploss_pct', 'N/A')} |\n")
        f.write("\n")

        # Ultra Shadow Activity
        f.write("## Ultra Shadow Activity\n\n")
        if df_shadow is not None and not df_shadow.empty:
            f.write(f"**Total Shadow Trades**: {len(df_shadow)}\n\n")
            if "underlying" in df_shadow.columns:
                shadow_by_underlying = df_shadow["underlying"].value_counts()
                f.write("| Underlying | Shadow Trades |\n")
                f.write("|------------|----------------|\n")
                for underlying, count in shadow_by_underlying.items():
                    f.write(f"| {underlying} | {count} |\n")
        else:
            f.write("**No shadow trades recorded yet.**\n")
        f.write("\n")

        # Audit Results Summary
        f.write("## Audit Results Summary (Phase 35)\n\n")
        if df_audit is not None and not df_audit.empty:
            status_counts = df_audit["status"].value_counts()
            f.write("| Status | Count |\n")
            f.write("|--------|-------|\n")
            for status, count in status_counts.items():
                f.write(f"| {status} | {count} |\n")
            f.write("\n")

            # WARN/BLOCK issues
            df_warn = df_audit[df_audit["status"] == "WARN"]
            df_block = df_audit[df_audit["status"] == "BLOCK"]

            if not df_block.empty:
                f.write("### ⚠️ BLOCKED Decisions\n\n")
                f.write(f"**Count**: {len(df_block)}\n\n")
                f.write("These decisions should NOT be executed.\n\n")

            if not df_warn.empty:
                f.write("### ⚠️ WARN Decisions\n\n")
                f.write(f"**Count**: {len(df_warn)}\n\n")
                f.write("These decisions should be reviewed before execution.\n\n")
        else:
            f.write("**No audit results available. Run Phase 35 first.**\n")
        f.write("\n")

        # Trade Caps
        f.write("## Trade Caps\n\n")
        f.write("| Cap Type | Limit |\n")
        f.write("|----------|-------|\n")
        f.write(f"| Max Position Size | {thresholds.get('max_position_size', 'N/A')} |\n")
        f.write(f"| Max Trades Per Day | {thresholds.get('max_trades_per_day', 'N/A')} |\n")
        f.write(f"| Max Trades Per Underlying | {thresholds.get('max_trades_per_underlying', 'N/A')} |\n")
        f.write("\n")

        # Safety Notes
        f.write("## Safety Notes\n\n")
        f.write("- All settings are read-only\n")
        f.write("- No configs have been modified\n")
        f.write("- Shadow trades are logged but never executed\n")
        f.write("- All Ultra operations are isolated from baseline\n")

    print(f"[SAVE] Dashboard saved to: {dashboard_md}")
    print("\n[OK] Phase 37 Policy & Risk Monitor completed")
    return str(dashboard_md)


def main() -> None:
    """Main entry point for CLI use."""
    try:
        path = run_phase37_policy_risk_dashboard()
        print(f"\n[PHASE 37] Output written to: {path}")
    except Exception as e:
        print(f"[PHASE 37][ERROR] {e}")
        error_path = ULTRA_DIR / "phase37_error.md"
        with error_path.open("w", encoding="utf-8") as f:
            f.write(f"# Phase 37 Error\n\n{str(e)}\n")
        print(f"[PHASE 37] Error details saved to: {error_path}")


if __name__ == "__main__":
    main()
