"""
Dhan Index Options - Daily PnL Summary Tool

Reads PnL logs and produces a clean console summary for today's trading.
Works with both synthetic backtest logs and real live trading logs.
"""

import os
import pandas as pd
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LIVE_DIR = os.path.join(PROJECT_ROOT, "storage", "live")

PNL_LOG_CSV = os.path.join(LIVE_DIR, "dhan_index_ai_pnl_log.csv")  # from pnl simulator
EXEC_LOG_CSV = os.path.join(LIVE_DIR, "dhan_index_ai_trades_exec_log.csv")  # from trade executor
BACKTEST_DIR = os.path.join(PROJECT_ROOT, "storage", "backtests")
BACKTEST_CSV = os.path.join(BACKTEST_DIR, "dhan_backtest_trades_detailed.csv")  # from synthetic backtester


def _parse_date_safe(ts_str):
    """Parse timestamp string to datetime, handling various formats."""
    if not isinstance(ts_str, str) or not ts_str:
        return None
    try:
        # Handle ISO format with or without Z
        ts_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_str)
    except Exception:
        try:
            # Try parsing as simple datetime string
            return pd.to_datetime(ts_str)
        except Exception:
            return None


def load_pnl_log() -> pd.DataFrame:
    """Load PnL log from live trading."""
    if not os.path.exists(PNL_LOG_CSV):
        return pd.DataFrame()

    try:
        df = pd.read_csv(PNL_LOG_CSV)
        if df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        print(f"[PNL] Failed to read PnL log: {e}")
        return pd.DataFrame()


def load_backtest_log() -> pd.DataFrame:
    """Load backtest log from synthetic backtester."""
    if not os.path.exists(BACKTEST_CSV):
        return pd.DataFrame()

    try:
        df = pd.read_csv(BACKTEST_CSV)
        if df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        print(f"[PNL] Failed to read backtest log: {e}")
        return pd.DataFrame()


def filter_today(df: pd.DataFrame, strict: bool = False) -> tuple[pd.DataFrame, bool]:
    """
    Filter DataFrame to only include trades that exited today.

    Returns:
        (filtered_df, is_today) - DataFrame and whether it's strictly today's data
    """
    if df.empty:
        return df, False

    today = datetime.utcnow().date()

    # Try different timestamp column names (prefer exit timestamps)
    ts_col = None
    for col in ["exit_ts", "ts_exit", "ts_exec", "ts"]:
        if col in df.columns:
            ts_col = col
            break

    if ts_col is None:
        print(f"[PNL] No timestamp column found. Available columns: {list(df.columns)}")
        return pd.DataFrame(), False

    # Parse dates
    parsed = df[ts_col].apply(_parse_date_safe)
    df = df.assign(_exit_date=parsed.apply(lambda x: x.date() if x else None))

    # Filter for today
    df_today = df[df["_exit_date"] == today].copy()
    is_today = len(df_today) > 0

    if not is_today and not strict:
        # If no today's data, return all available data (for testing/backtesting)
        print(f"[PNL] No trades for today ({today}); showing all available trades.")
        df_today = df.copy()

    if "_exit_date" in df_today.columns:
        df_today = df_today.drop(columns=["_exit_date"])

    return df_today, is_today


def summarize_daily_pnl(df: pd.DataFrame, source: str = "live", is_today: bool = True) -> None:
    """Compute and print daily PnL summary."""
    if df.empty:
        print(f"[PNL] No trades available ({source}).")
        return

    # Detect PnL column name (handle both pnl_pct and pct_pnl)
    pnl_col = None
    for col in ["pnl_pct", "pct_pnl", "pnl"]:
        if col in df.columns:
            pnl_col = col
            break

    if pnl_col is None:
        print("[PNL] No PnL column found in log.")
        print(f"Columns: {list(df.columns)}")
        return

    df["is_win"] = df[pnl_col] > 0

    date_label = "TODAY" if is_today else "ALL AVAILABLE"
    print(f"=== DAILY PnL SUMMARY ({date_label}) - {source.upper()} ===")

    # Per underlying
    if "underlying" in df.columns:
        grp = df.groupby("underlying")[pnl_col]
        summary = grp.agg(["count", "mean", "max", "min"]).reset_index()
        summary.columns = ["underlying", "count", "mean", "max", "min"]
        summary["win_rate"] = df.groupby("underlying")["is_win"].mean().values

        print("\n--- By Underlying ---")
        for _, row in summary.iterrows():
            u = row["underlying"]
            n = int(row["count"])
            mean_p = row["mean"]
            max_p = row["max"]
            min_p = row["min"]
            win_r = row["win_rate"]

            print(
                f"{u}: trades={n}, win_rate={win_r*100:.1f}%, "
                f"avg_pnl={mean_p:.3f}%, max_pnl={max_p:.3f}%, min_pnl={min_p:.3f}%"
            )
    else:
        print("\n[PNL] No 'underlying' column found; skipping per-underlying summary.")

    # Overall
    total_trades = len(df)
    total_win_rate = df["is_win"].mean() if total_trades > 0 else 0.0
    overall_mean = df[pnl_col].mean()
    overall_sum = df[pnl_col].sum()

    print("\n--- Overall ---")
    print(f"Total trades: {total_trades}")
    print(f"Win rate   : {total_win_rate*100:.1f}%")
    print(f"Avg PnL    : {overall_mean:.3f}%")
    print(f"Total PnL  : {overall_sum:.3f}%")

    # Exit reason breakdown if available
    if "exit_reason" in df.columns or "result" in df.columns:
        reason_col = "exit_reason" if "exit_reason" in df.columns else "result"
        reason_counts = df[reason_col].value_counts()
        print(f"\n--- Exit Reasons ---")
        for reason, count in reason_counts.items():
            print(f"  {reason}: {count}")


def main() -> None:
    """Main entry point for daily PnL summary."""
    print("=== ANGEL ONE INDEX OPTIONS - DAILY PnL SUMMARY ===")

    # Try live PnL log first
    df_live = load_pnl_log()
    if not df_live.empty:
        df_live_today, is_today = filter_today(df_live, strict=False)
        if not df_live_today.empty:
            summarize_daily_pnl(df_live_today, source="live", is_today=is_today)
            return

    # Try backtest log
    df_backtest = load_backtest_log()
    if not df_backtest.empty:
        df_backtest_today, is_today = filter_today(df_backtest, strict=False)
        if not df_backtest_today.empty:
            summarize_daily_pnl(df_backtest_today, source="backtest", is_today=is_today)
            return

    # No data found
    print("[PNL] No PnL data found.")
    print(f"[PNL] Checked:")
    print(f"  - {PNL_LOG_CSV}")
    print(f"  - {BACKTEST_CSV}")


if __name__ == "__main__":
    main()
