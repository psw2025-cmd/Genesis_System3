"""
Live Paper Trading Monitor - Real-time Dashboard
Shows streaming data fetch, paper trading activity, and performance metrics
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger


def clear_screen():
    """Clear terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def format_number(num, decimals=2):
    """Format number with commas."""
    if pd.isna(num) or num is None:
        return "N/A"
    try:
        return f"{float(num):,.{decimals}f}"
    except:
        return str(num)


def get_live_data_status():
    """Check if live data is being fetched."""
    # Check multiple possible locations
    csv_paths = [
        ROOT_DIR / "outputs" / "chain_raw_live.csv",
        ROOT_DIR / "storage" / "live" / "option_chain_ALL_INDICES.csv",
    ]

    csv_path = None
    for path in csv_paths:
        if path.exists():
            csv_path = path
            break

    if csv_path is None:
        return {
            "status": "NO_DATA",
            "message": "No data file found - waiting for first fetch... (checking every 5s)",
            "last_update": None,
            "contracts": 0,
        }

    try:
        # Check file modification time
        mod_time = datetime.fromtimestamp(csv_path.stat().st_mtime)
        ist = pytz.timezone("Asia/Kolkata")
        # Make mod_time timezone-aware for comparison
        if mod_time.tzinfo is None:
            mod_time = ist.localize(mod_time)
        now = datetime.now(ist)

        # Read last few rows to check timestamp
        df = pd.read_csv(csv_path)

        if len(df) == 0:
            return {"status": "EMPTY", "message": "Data file is empty", "last_update": None, "contracts": 0}

        # Get latest timestamp
        if "timestamp_ist" in df.columns:
            latest_timestamp = df["timestamp_ist"].iloc[-1] if df["timestamp_ist"].notna().any() else None
        else:
            latest_timestamp = None

        # Check how recent the data is (ensure both are timezone-aware)
        if mod_time.tzinfo is None:
            mod_time = ist.localize(mod_time)
        if now.tzinfo is None:
            now = datetime.now(ist)
        time_diff = (now - mod_time).total_seconds()

        if time_diff < 10:
            status = "LIVE"
            message = f"Data streaming LIVE (updated {int(time_diff)}s ago)"
        elif time_diff < 60:
            status = "RECENT"
            message = f"Data recent (updated {int(time_diff)}s ago)"
        else:
            status = "STALE"
            message = f"Data stale (updated {int(time_diff//60)}m ago)"

        return {
            "status": status,
            "message": message,
            "last_update": latest_timestamp or mod_time.strftime("%Y-%m-%d %H:%M:%S"),
            "contracts": len(df),
            "indices": df["underlying"].unique().tolist() if "underlying" in df.columns else [],
            "sample_data": df.iloc[-1].to_dict() if len(df) > 0 else None,
        }
    except Exception as e:
        return {"status": "ERROR", "message": f"Error reading data: {e}", "last_update": None, "contracts": 0}


def get_paper_trading_status():
    """Get paper trading activity."""
    trades_path = ROOT_DIR / "outputs" / "paper_trades.csv"
    pnl_path = ROOT_DIR / "outputs" / "pnl_summary.json"
    signals_path = ROOT_DIR / "outputs" / "top_trade_signal.json"

    result = {
        "total_trades": 0,
        "open_positions": 0,
        "total_pnl": 0.0,
        "winning_trades": 0,
        "losing_trades": 0,
        "win_rate": 0.0,
        "latest_signal": None,
        "latest_trade": None,
    }

    # Check trades
    if trades_path.exists():
        try:
            trades_df = pd.read_csv(trades_path)
            if len(trades_df) > 0:
                result["total_trades"] = len(trades_df)
                result["open_positions"] = len(trades_df[trades_df.get("status", "") == "OPEN"])

                # Calculate PnL
                if "pnl" in trades_df.columns:
                    result["total_pnl"] = trades_df["pnl"].sum()
                    result["winning_trades"] = len(trades_df[trades_df["pnl"] > 0])
                    result["losing_trades"] = len(trades_df[trades_df["pnl"] < 0])
                    if result["total_trades"] > 0:
                        result["win_rate"] = (result["winning_trades"] / result["total_trades"]) * 100

                # Latest trade
                result["latest_trade"] = trades_df.iloc[-1].to_dict() if len(trades_df) > 0 else None
        except Exception as e:
            result["error"] = f"Error reading trades: {e}"

    # Check PnL summary
    if pnl_path.exists():
        try:
            with open(pnl_path, "r") as f:
                pnl_data = json.load(f)
                result.update(
                    {
                        "total_pnl": pnl_data.get("total_pnl", result["total_pnl"]),
                        "win_rate": pnl_data.get("win_rate", result["win_rate"]),
                        "total_trades": pnl_data.get("total_trades", result["total_trades"]),
                    }
                )
        except:
            pass

    # Check latest signal
    if signals_path.exists():
        try:
            with open(signals_path, "r") as f:
                signal_data = json.load(f)
                result["latest_signal"] = signal_data
        except:
            pass

    return result


def get_system_health():
    """Check system health metrics."""
    logs_path = ROOT_DIR / "logs" / "run.log"

    health = {"status": "UNKNOWN", "last_cycle": None, "errors": 0, "warnings": 0}

    if logs_path.exists():
        try:
            # Read last 100 lines of log
            with open(logs_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                last_lines = lines[-100:] if len(lines) > 100 else lines

                # Count errors and warnings
                health["errors"] = sum(1 for line in last_lines if "ERROR" in line or "error" in line.lower())
                health["warnings"] = sum(1 for line in last_lines if "WARNING" in line or "warning" in line.lower())

                # Find last cycle
                for line in reversed(last_lines):
                    if "CYCLE" in line:
                        health["last_cycle"] = line.strip()
                        break

                # Determine status
                if health["errors"] > 10:
                    health["status"] = "ERROR"
                elif health["warnings"] > 20:
                    health["status"] = "WARNING"
                else:
                    health["status"] = "HEALTHY"
        except:
            pass

    return health


def display_dashboard():
    """Display live monitoring dashboard."""
    clear_screen()

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    print("=" * 100)
    print("  LIVE PAPER TRADING MONITOR - REAL-TIME DASHBOARD".center(100))
    print("=" * 100)
    print(f"\nCurrent Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("=" * 100)

    # Section 1: Live Data Status
    print("\n[1] LIVE DATA FETCHING STATUS")
    print("-" * 100)
    data_status = get_live_data_status()

    status_icon = {"LIVE": "🟢", "RECENT": "🟡", "STALE": "🟠", "NO_DATA": "🔴", "EMPTY": "🔴", "ERROR": "🔴"}.get(
        data_status["status"], "⚪"
    )

    print(f"  Status: {status_icon} {data_status['status']}")
    print(f"  Message: {data_status['message']}")
    print(f"  Last Update: {data_status['last_update'] or 'N/A'}")
    print(f"  Contracts: {data_status['contracts']}")

    if data_status.get("indices"):
        print(f"  Indices: {', '.join(data_status['indices'])}")

    if data_status.get("sample_data"):
        sample = data_status["sample_data"]
        print(f"\n  Sample Data (Latest Contract):")
        print(f"    Symbol: {sample.get('symbol', 'N/A')}")
        print(f"    Strike: {sample.get('strike', 'N/A')}")
        print(f"    LTP: {format_number(sample.get('ltp'))}")
        print(f"    Volume: {format_number(sample.get('volume'), 0)}")
        print(f"    OI: {format_number(sample.get('oi'), 0)}")
        print(f"    Delta: {format_number(sample.get('delta'), 4)}")
        print(f"    IV: {format_number(sample.get('iv'), 4)}")

    # Section 2: Paper Trading Activity
    print("\n[2] PAPER TRADING ACTIVITY")
    print("-" * 100)
    trading_status = get_paper_trading_status()

    print(f"  Total Trades: {trading_status['total_trades']}")
    print(f"  Open Positions: {trading_status['open_positions']}")
    print(f"  Total PnL: Rs {format_number(trading_status['total_pnl'])}")
    print(f"  Winning Trades: {trading_status['winning_trades']}")
    print(f"  Losing Trades: {trading_status['losing_trades']}")
    print(f"  Win Rate: {format_number(trading_status['win_rate'], 1)}%")

    if trading_status.get("latest_trade"):
        trade = trading_status["latest_trade"]
        print(f"\n  Latest Trade:")
        print(f"    Symbol: {trade.get('symbol', 'N/A')}")
        print(f"    Action: {trade.get('action', 'N/A')}")
        print(f"    Entry: Rs {format_number(trade.get('entry_price'))}")
        print(f"    PnL: Rs {format_number(trade.get('pnl'))}")
        print(f"    Status: {trade.get('status', 'N/A')}")

    if trading_status.get("latest_signal"):
        signal = trading_status["latest_signal"]
        print(f"\n  Latest Signal:")
        print(f"    Action: {signal.get('action', 'N/A')}")
        print(f"    Underlying: {signal.get('underlying', 'N/A')}")
        print(f"    Strategy: {signal.get('strategy', 'N/A')}")
        print(f"    Confidence: {format_number(signal.get('confidence', 0), 1)}%")

    # Section 3: System Health
    print("\n[3] SYSTEM HEALTH")
    print("-" * 100)
    health = get_system_health()

    health_icon = {"HEALTHY": "🟢", "WARNING": "🟡", "ERROR": "🔴", "UNKNOWN": "⚪"}.get(health["status"], "⚪")

    print(f"  Status: {health_icon} {health['status']}")
    print(f"  Errors (last 100 lines): {health['errors']}")
    print(f"  Warnings (last 100 lines): {health['warnings']}")
    if health.get("last_cycle"):
        print(f"  Last Cycle: {health['last_cycle'][:80]}")

    # Section 4: Production Readiness
    print("\n[4] PRODUCTION READINESS CHECK")
    print("-" * 100)

    checks = []

    # Check 1: Data streaming
    if data_status["status"] == "LIVE":
        checks.append(("✅", "Data Streaming", "LIVE"))
    else:
        checks.append(("⚠️", "Data Streaming", data_status["status"]))

    # Check 2: Recent data
    if data_status["contracts"] > 0:
        checks.append(("✅", "Data Available", f"{data_status['contracts']} contracts"))
    else:
        checks.append(("❌", "Data Available", "No contracts"))

    # Check 3: Trading activity
    if trading_status["total_trades"] > 0:
        checks.append(("✅", "Trading Active", f"{trading_status['total_trades']} trades"))
    else:
        checks.append(("⚠️", "Trading Active", "No trades yet"))

    # Check 4: System health
    if health["status"] == "HEALTHY":
        checks.append(("✅", "System Health", "HEALTHY"))
    else:
        checks.append(("⚠️", "System Health", health["status"]))

    # Check 5: Profitability
    if trading_status["total_pnl"] > 0:
        checks.append(("✅", "Profitability", f"Rs {format_number(trading_status['total_pnl'])}"))
    elif trading_status["total_trades"] > 0:
        checks.append(("⚠️", "Profitability", f"Rs {format_number(trading_status['total_pnl'])} (negative)"))
    else:
        checks.append(("⚪", "Profitability", "No trades yet"))

    for icon, check, status in checks:
        print(f"  {icon} {check:20s}: {status}")

    # Overall status
    all_good = all(icon == "✅" for icon, _, _ in checks)
    if all_good:
        print(f"\n  🎯 OVERALL STATUS: ✅ PRODUCTION READY")
    else:
        print(f"\n  🎯 OVERALL STATUS: ⚠️  MONITORING - Some checks need attention")

    print("\n" + "=" * 100)
    print("  Press Ctrl+C to stop monitoring")
    print("  Auto-refresh: Every 5 seconds")
    print("=" * 100)


def main():
    """Main monitoring loop."""
    try:
        while True:
            display_dashboard()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\n[INFO] Monitoring stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
