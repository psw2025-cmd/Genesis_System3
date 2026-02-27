"""
System3 Ultra - Ultra PnL Analyzer

Advanced analysis of Ultra simulator PnL.
Shadow mode only.

Inputs:
- storage/ultra/angel_ultra_pnl_sim.csv

Outputs:
- storage/reports_ultra/ultra_pnl_report.csv

Menu Option: 82
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"

PNL_SIM_CSV = ULTRA_DIR / "angel_ultra_pnl_sim.csv"
PNL_REPORT_CSV = REPORTS_ULTRA_DIR / "ultra_pnl_report.csv"

REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def analyze_ultra_pnl() -> Dict[str, Any]:
    """
    Analyze Ultra simulator PnL.

    Returns:
        Dict with analysis results
    """
    print("=== SYSTEM3 ULTRA - PNL ANALYZER ===")
    print("[INFO] Advanced analysis of Ultra simulator PnL\n")
    print("[SAFETY] Shadow mode only - read-only analysis\n")

    # Load PnL simulation results
    if not PNL_SIM_CSV.exists():
        return {
            "status": "NO_DATA",
            "message": "PnL simulation CSV not found. Run Phase 18 first.",
        }

    try:
        df_pnl = pd.read_csv(PNL_SIM_CSV)
        print(f"[LOAD] PnL log: {len(df_pnl)} rows")
    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Failed to load PnL log: {e}",
        }

    if df_pnl.empty:
        return {
            "status": "EMPTY",
            "message": "PnL log is empty",
        }

    # Analysis
    report_rows = []

    # Overall summary
    total_trades = len(df_pnl)
    wins = (df_pnl["pnl_pct"] > 0).sum()
    losses = (df_pnl["pnl_pct"] < 0).sum()
    win_rate = wins / total_trades * 100 if total_trades > 0 else 0.0
    avg_pnl = df_pnl["pnl_pct"].mean()
    total_pnl = df_pnl["pnl_pct"].sum()
    max_win = df_pnl["pnl_pct"].max()
    max_loss = df_pnl["pnl_pct"].min()

    # Drawdown calculation
    cumulative = df_pnl["pnl_pct"].cumsum()
    running_max = cumulative.expanding().max()
    drawdown = cumulative - running_max
    max_drawdown = drawdown.min()

    report_rows.append(
        {
            "metric": "OVERALL",
            "underlying": "ALL",
            "value": None,
            "trades": total_trades,
            "wins": wins,
            "losses": losses,
            "win_rate": float(win_rate),
            "avg_pnl": float(avg_pnl),
            "total_pnl": float(total_pnl),
            "max_win": float(max_win),
            "max_loss": float(max_loss),
            "max_drawdown": float(max_drawdown),
        }
    )

    # Per-underlying breakdown
    for underlying in UNDERLYINGS:
        df_u = df_pnl[df_pnl["underlying"] == underlying]
        if df_u.empty:
            continue

        u_wins = (df_u["pnl_pct"] > 0).sum()
        u_losses = (df_u["pnl_pct"] < 0).sum()
        u_win_rate = u_wins / len(df_u) * 100 if len(df_u) > 0 else 0.0
        u_avg_pnl = df_u["pnl_pct"].mean()
        u_total_pnl = df_u["pnl_pct"].sum()
        u_max_win = df_u["pnl_pct"].max()
        u_max_loss = df_u["pnl_pct"].min()

        u_cumulative = df_u["pnl_pct"].cumsum()
        u_running_max = u_cumulative.expanding().max()
        u_drawdown = u_cumulative - u_running_max
        u_max_drawdown = u_drawdown.min()

        report_rows.append(
            {
                "metric": "PER_UNDERLYING",
                "underlying": underlying,
                "value": None,
                "trades": len(df_u),
                "wins": u_wins,
                "losses": u_losses,
                "win_rate": float(u_win_rate),
                "avg_pnl": float(u_avg_pnl),
                "total_pnl": float(u_total_pnl),
                "max_win": float(u_max_win),
                "max_loss": float(u_max_loss),
                "max_drawdown": float(u_max_drawdown),
            }
        )

    # Time-of-day performance (if timestamp available)
    if "entry_timestamp" in df_pnl.columns:
        try:
            df_pnl["hour"] = pd.to_datetime(df_pnl["entry_timestamp"], errors="coerce").dt.hour
            for hour in range(9, 16):  # 9 AM to 3 PM
                df_h = df_pnl[df_pnl["hour"] == hour]
                if not df_h.empty:
                    h_win_rate = (df_h["pnl_pct"] > 0).sum() / len(df_h) * 100
                    h_avg_pnl = df_h["pnl_pct"].mean()
                    report_rows.append(
                        {
                            "metric": "TIME_OF_DAY",
                            "underlying": "ALL",
                            "value": f"{hour}:00",
                            "trades": len(df_h),
                            "wins": (df_h["pnl_pct"] > 0).sum(),
                            "losses": (df_h["pnl_pct"] < 0).sum(),
                            "win_rate": float(h_win_rate),
                            "avg_pnl": float(h_avg_pnl),
                            "total_pnl": float(df_h["pnl_pct"].sum()),
                            "max_win": float(df_h["pnl_pct"].max()),
                            "max_loss": float(df_h["pnl_pct"].min()),
                            "max_drawdown": None,
                        }
                    )
        except Exception:
            pass

    # Save report
    df_report = pd.DataFrame(report_rows)
    df_report.to_csv(PNL_REPORT_CSV, index=False)
    print(f"[SAVE] PnL report: {PNL_REPORT_CSV}")

    return {
        "status": "SUCCESS",
        "total_trades": total_trades,
        "win_rate": float(win_rate),
        "avg_pnl": float(avg_pnl),
        "max_drawdown": float(max_drawdown),
        "report_rows": len(report_rows),
    }


def main() -> None:
    """Main entry point."""
    result = analyze_ultra_pnl()

    if result["status"] == "SUCCESS":
        print("\n=== PNL ANALYSIS SUMMARY ===")
        print(f"Total Trades: {result['total_trades']}")
        print(f"Win Rate: {result['win_rate']:.1f}%")
        print(f"Avg PnL: {result['avg_pnl']:.2f}%")
        print(f"Max Drawdown: {result['max_drawdown']:.2f}%")
        print(f"\n[SAVE] Full report: {PNL_REPORT_CSV}")
        print("[NOTE] Analysis only - no changes made")
    else:
        print(f"\n[INFO] {result.get('message', 'Analysis not completed')}")


if __name__ == "__main__":
    main()
