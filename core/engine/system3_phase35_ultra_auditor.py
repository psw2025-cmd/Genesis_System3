"""
System3 Ultra - Phase 35: Ultra Decision Auditor

Audit Ultra fused decisions for:
- Over-aggression
- Regime mismatch
- Excessive size vs baseline risk limits

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 98
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
CONFIG_DIR = PROJECT_ROOT / "storage" / "config"

ULTRA_DIR.mkdir(parents=True, exist_ok=True)

# Safety limits (read-only from config or defaults)
MAX_POSITION_SIZE = 1.0  # Normalized max
MAX_TRADES_PER_DAY = 50
MAX_TRADES_PER_UNDERLYING = 10
DISALLOWED_REGIMES = ["CHAOTIC", "EXTREME_VOL"]


def _load_ultra_decisions() -> Optional[pd.DataFrame]:
    """Load Ultra fused decisions."""
    ultra_csv = ULTRA_DIR / "phase31_ultra_fused_decisions.csv"
    if not ultra_csv.exists():
        return None
    try:
        return pd.read_csv(ultra_csv)
    except Exception:
        return None


def _load_shadow_trades() -> Optional[pd.DataFrame]:
    """Load shadow Ultra trades."""
    shadow_csv = LIVE_DIR / "dhan_index_ai_ultra_trades_shadow.csv"
    if not shadow_csv.exists():
        return None
    try:
        return pd.read_csv(shadow_csv)
    except Exception:
        return None


def _load_baseline_limits() -> Dict[str, Any]:
    """Load baseline safety limits (read-only)."""
    # Try to load from config
    config_json = CONFIG_DIR / "thresholds_auto.json"
    if config_json.exists():
        try:
            import json

            with config_json.open("r", encoding="utf-8") as f:
                config = json.load(f)
                return {
                    "max_position_size": config.get("max_position_size", MAX_POSITION_SIZE),
                    "max_trades_per_day": config.get("max_trades_per_day", MAX_TRADES_PER_DAY),
                    "max_trades_per_underlying": config.get("max_trades_per_underlying", MAX_TRADES_PER_UNDERLYING),
                }
        except Exception:
            pass

    # Defaults
    return {
        "max_position_size": MAX_POSITION_SIZE,
        "max_trades_per_day": MAX_TRADES_PER_DAY,
        "max_trades_per_underlying": MAX_TRADES_PER_UNDERLYING,
    }


def _audit_decision(
    row: pd.Series,
    limits: Dict[str, Any],
    daily_trade_counts: Dict[str, int],
) -> Dict[str, Any]:
    """Audit a single Ultra decision."""
    audit_result = {
        "timestamp": row.get("timestamp", ""),
        "underlying": row.get("underlying", ""),
        "strike": row.get("strike", np.nan),
        "side": row.get("side", ""),
        "final_action": row.get("final_action", "HOLD"),
        "final_size": row.get("final_size", 0.0),
        "regime": row.get("regime", "UNKNOWN"),
        "risk_flag": row.get("final_risk_flag", "RISKY"),
        "status": "OK",
        "issues": [],
    }

    # Check 1: Position size
    final_size = float(row.get("final_size", 0.0))
    if final_size > limits["max_position_size"]:
        audit_result["status"] = "WARN"
        audit_result["issues"].append(f"Position size {final_size:.2f} exceeds limit {limits['max_position_size']:.2f}")

    # Check 2: Regime mismatch
    regime = str(row.get("regime", "UNKNOWN"))
    if regime in DISALLOWED_REGIMES:
        audit_result["status"] = "BLOCK"
        audit_result["issues"].append(f"Trade in disallowed regime: {regime}")

    # Check 3: Daily trade count per underlying
    underlying = row.get("underlying", "")
    if underlying in daily_trade_counts:
        if daily_trade_counts[underlying] >= limits["max_trades_per_underlying"]:
            audit_result["status"] = "BLOCK"
            audit_result["issues"].append(
                f"Daily trade limit reached for {underlying}: {daily_trade_counts[underlying]}"
            )

    # Check 4: Risk flag
    if audit_result["risk_flag"] == "BLOCKED":
        audit_result["status"] = "BLOCK"
        audit_result["issues"].append("Risk flag is BLOCKED")

    return audit_result


def run_phase35_audit() -> str:
    """
    Run Phase 35: Ultra Decision Auditor.

    Returns:
        Path to audit report MD file
    """
    print("=== SYSTEM3 ULTRA - PHASE 35: ULTRA DECISION AUDITOR ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Load data
    df_ultra = _load_ultra_decisions()
    df_shadow = _load_shadow_trades()
    limits = _load_baseline_limits()

    if df_ultra is None or df_ultra.empty:
        print("[PHASE 35][ERROR] No Ultra decisions found. Run Phase 31 first.")
        error_path = ULTRA_DIR / "phase35_error_no_decisions.md"
        with error_path.open("w", encoding="utf-8") as f:
            f.write("# Phase 35 Error\n\nNo Ultra decisions found. Run Phase 31 first.\n")
        return str(error_path)

    print(f"[LOAD] Loaded {len(df_ultra)} Ultra decisions")
    if df_shadow is not None:
        print(f"[LOAD] Loaded {len(df_shadow)} shadow trades")
    print(
        f"[LOAD] Safety limits: max_size={limits['max_position_size']}, max_trades/day={limits['max_trades_per_day']}"
    )

    # Count daily trades per underlying
    daily_trade_counts = {}
    if df_shadow is not None and not df_shadow.empty:
        for underlying in df_shadow.get("underlying", []):
            if pd.notna(underlying):
                daily_trade_counts[underlying] = daily_trade_counts.get(underlying, 0) + 1

    # Audit each decision
    audit_results = []
    for _, row in df_ultra.iterrows():
        audit_result = _audit_decision(row, limits, daily_trade_counts)
        audit_results.append(audit_result)

    df_audit = pd.DataFrame(audit_results)

    # Save audit CSV
    audit_csv = ULTRA_DIR / "phase35_decision_audit.csv"
    df_audit.to_csv(audit_csv, index=False)
    print(f"[SAVE] Audit CSV saved to: {audit_csv}")

    # Generate summary
    status_counts = df_audit["status"].value_counts()
    ok_count = status_counts.get("OK", 0)
    warn_count = status_counts.get("WARN", 0)
    block_count = status_counts.get("BLOCK", 0)

    print(f"\n=== AUDIT SUMMARY ===")
    print(f"Total decisions audited: {len(df_audit)}")
    print(f"OK: {ok_count}")
    print(f"WARN: {warn_count}")
    print(f"BLOCK: {block_count}")

    # Generate MD report
    report_md = ULTRA_DIR / "phase35_decision_audit_report.md"
    with report_md.open("w", encoding="utf-8") as f:
        f.write("# Ultra Decision Audit Report\n\n")
        f.write(f"Generated: {datetime.utcnow().isoformat()}\n\n")

        f.write("## Audit Summary\n\n")
        f.write("| Status | Count | Percentage |\n")
        f.write("|--------|-------|------------|\n")
        f.write(f"| OK | {ok_count} | {ok_count/len(df_audit)*100:.1f}% |\n")
        f.write(f"| WARN | {warn_count} | {warn_count/len(df_audit)*100:.1f}% |\n")
        f.write(f"| BLOCK | {block_count} | {block_count/len(df_audit)*100:.1f}% |\n\n")

        # Serious issues
        df_blocked = df_audit[df_audit["status"] == "BLOCK"]
        if not df_blocked.empty:
            f.write("## ⚠️ Serious Issues (BLOCKED)\n\n")
            for _, row in df_blocked.iterrows():
                f.write(f"### {row['underlying']} {row['strike']} {row['side']}\n\n")
                f.write(f"- **Action**: {row['final_action']}\n")
                f.write(f"- **Issues**: {', '.join(row['issues'])}\n\n")

        # Warnings
        df_warned = df_audit[df_audit["status"] == "WARN"]
        if not df_warned.empty:
            f.write("## ⚠️ Warnings\n\n")
            f.write(f"Total warnings: {len(df_warned)}\n\n")
            for _, row in df_warned.head(10).iterrows():  # Show first 10
                f.write(f"- {row['underlying']} {row['strike']} {row['side']}: {', '.join(row['issues'])}\n")
            if len(df_warned) > 10:
                f.write(f"\n... and {len(df_warned) - 10} more warnings\n")

        f.write("\n## Safety Notes\n\n")
        f.write("- This audit is read-only and does not modify any configs\n")
        f.write("- BLOCKED decisions should not be executed\n")
        f.write("- WARN decisions should be reviewed before execution\n")

    print(f"[SAVE] Audit report MD saved to: {report_md}")
    print("\n[OK] Phase 35 Ultra Decision Auditor completed")
    return str(report_md)


def main() -> None:
    """Main entry point for CLI use."""
    try:
        path = run_phase35_audit()
        print(f"\n[PHASE 35] Output written to: {path}")
    except Exception as e:
        print(f"[PHASE 35][ERROR] {e}")
        error_path = ULTRA_DIR / "phase35_error.md"
        with error_path.open("w", encoding="utf-8") as f:
            f.write(f"# Phase 35 Error\n\n{str(e)}\n")
        print(f"[PHASE 35] Error details saved to: {error_path}")


if __name__ == "__main__":
    main()
