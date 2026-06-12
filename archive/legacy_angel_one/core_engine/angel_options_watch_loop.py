import os
import sys
import time
from datetime import datetime, date

import pandas as pd

# ---------------- Path setup ----------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.utils.logger import logger
from core.brokers.angel_one.broker import AngelOneBroker
from core.brokers.angel_one.instruments import (
    find_options_for_underlying,
    find_index_by_name,
)


def _parse_expiry(df: pd.DataFrame) -> pd.DataFrame:
    """Add an expiry_dt column (datetime.date) parsed from 'expiry' strings."""
    df = df.copy()
    if "expiry" not in df.columns:
        df["expiry_dt"] = pd.NaT
        return df

    def _parse(x: str):
        x = str(x).strip()
        if not x:
            return pd.NaT
        # Angel expiry format: 02DEC2025, 30JUN2026 etc.
        for fmt in ("%d%b%Y", "%d%b%y"):
            try:
                return datetime.strptime(x, fmt).date()
            except Exception:
                continue
        return pd.NaT

    df["expiry_dt"] = df["expiry"].apply(_parse)
    return df


def _select_nearest_expiry(df: pd.DataFrame) -> pd.DataFrame:
    """Return subset of df for the nearest (current) expiry."""
    if df.empty:
        return df

    df = _parse_expiry(df)
    if df["expiry_dt"].isna().all():
        return df

    today = date.today()
    valid = df.dropna(subset=["expiry_dt"])
    future = valid[valid["expiry_dt"] >= today]
    if not future.empty:
        target = future["expiry_dt"].min()
    else:
        target = valid["expiry_dt"].min()

    return valid[valid["expiry_dt"] == target].copy()


def _normalize_strike(raw: str) -> float | None:
    """Convert Angel strike string to useful float (handles *100 scaling)."""
    try:
        v = float(raw)
    except Exception:
        return None

    # Many strikes come as 2300000.0 for 23000.0 etc.
    if v > 100000:
        v = v / 100.0

    return v


def _fetch_ltp_safe(broker: AngelOneBroker, exchange: str, symbol: str, token: str):
    """Wrapper around broker.get_ltp with error handling, returns float or None."""
    data = broker.get_ltp(exchange, symbol, token)
    if not data or not data.get("status"):
        return None
    try:
        return float(data["data"]["ltp"])
    except Exception:
        return None


def _build_watch_for_underlying(
    broker: AngelOneBroker,
    name: str,
    index_exchange: str,
    options_exchange: str,
    num_strikes_each_side: int = 3,
):
    """
    For one underlying (e.g. NIFTY) return list of dicts:
    {
      underlying, index_exch, opt_exch, spot, expiry,
      strike, side, symbol, token, ltp
    }
    """
    # 1) Index instrument row + spot
    idx_row = find_index_by_name(name, index_exchange)
    if not idx_row:
        logger.warning(f"[{name}] No index row found; skipping.")
        return []

    idx_symbol = str(idx_row["symbol"])
    idx_token = str(idx_row["token"])

    spot = _fetch_ltp_safe(broker, index_exchange, idx_symbol, idx_token)
    if spot is None:
        logger.warning(f"[{name}] Could not fetch index LTP; skipping.")
        return []

    # 2) All option contracts
    df_opts = find_options_for_underlying(name, options_exchange)
    if df_opts is None or df_opts.empty:
        logger.warning(f"[{name}] No options found in instruments; skipping.")
        return []

    # 3) Nearest expiry only
    current = _select_nearest_expiry(df_opts)
    if current.empty:
        logger.warning(f"[{name}] No options with valid expiry; skipping.")
        return []

    # 4) Strikes and distance
    current = current.copy()
    current["strike_val"] = current["strike"].apply(_normalize_strike)
    current = current.dropna(subset=["strike_val"])
    current["dist"] = (current["strike_val"] - spot).abs()

    # 5) Split CE / PE via symbol suffix
    sym_series = current["symbol"].astype(str)
    ce_df = current[sym_series.str.endswith("CE")]
    pe_df = current[sym_series.str.endswith("PE")]

    if ce_df.empty:
        ce_df = current
    if pe_df.empty:
        pe_df = current

    ce_sel = ce_df.sort_values("dist").head(num_strikes_each_side)
    pe_sel = pe_df.sort_values("dist").head(num_strikes_each_side)

    rows = []

    def _collect(side_label: str, sub_df: pd.DataFrame):
        for _, r in sub_df.iterrows():
            sym = str(r["symbol"])
            tok = str(r["token"])
            strike_val = float(r["strike_val"])
            expiry_str = str(r.get("expiry", ""))

            opt_ltp = _fetch_ltp_safe(broker, options_exchange, sym, tok)

            rows.append(
                {
                    "underlying": name,
                    "index_exch": index_exchange,
                    "opt_exch": options_exchange,
                    "spot": spot,
                    "expiry": expiry_str,
                    "strike": strike_val,
                    "side": side_label,
                    "symbol": sym,
                    "token": tok,
                    "ltp": opt_ltp,
                }
            )

    _collect("CE", ce_sel)
    _collect("PE", pe_sel)

    return rows


def _build_full_snapshot(broker: AngelOneBroker) -> pd.DataFrame | None:
    """
    Build one snapshot for all configured indices.
    Returns DataFrame or None if nothing fetched.
    """
    underlyings = [
        {"name": "NIFTY", "index_exch": "NSE", "opt_exch": "NFO"},
        {"name": "BANKNIFTY", "index_exch": "NSE", "opt_exch": "NFO"},
        {"name": "FINNIFTY", "index_exch": "NSE", "opt_exch": "NFO"},
        {"name": "MIDCPNIFTY", "index_exch": "NSE", "opt_exch": "NFO"},
        {"name": "SENSEX", "index_exch": "BSE", "opt_exch": "BFO"},
    ]

    all_rows = []
    for cfg in underlyings:
        rows = _build_watch_for_underlying(
            broker,
            name=cfg["name"],
            index_exchange=cfg["index_exch"],
            options_exchange=cfg["opt_exch"],
            num_strikes_each_side=3,
        )
        all_rows.extend(rows)

    if not all_rows:
        return None

    df = pd.DataFrame(all_rows)
    df = df.sort_values(
        by=["underlying", "expiry", "strike", "side"],
        ascending=[True, True, True, True],
    )

    return df


def main():
    logger.info("=== Angel One Index Options LIVE Watch Loop ===")
    print("Initializing AngelOne broker...")
    broker = AngelOneBroker(allow_data_only=True)  # Data fetching doesn't require live trading permission
    print("Login OK.\n")

    # Output CSV path
    live_dir = os.path.join(ROOT_DIR, "storage", "live")
    os.makedirs(live_dir, exist_ok=True)
    csv_path = os.path.join(live_dir, "angel_index_options_watch.csv")

    print(f"Live log file: {csv_path}")
    print("Press Ctrl + C to stop.\n")

    interval_sec = 30  # adjust if you want faster/slower polling
    iteration = 0

    try:
        while True:
            iteration += 1
            ts = datetime.now().isoformat(timespec="seconds")
            print(f"[{ts}] Snapshot #{iteration} ...")

            try:
                df = _build_full_snapshot(broker)
            except Exception as e:
                logger.exception("Error building Angel One options snapshot")
                print(f"  ERROR during snapshot: {e}")
                df = None

            if df is None or df.empty:
                print("  -> No data collected (check logs).")
            else:
                df = df.copy()
                df["ts"] = ts

                # Append to CSV
                write_header = not os.path.exists(csv_path)
                df.to_csv(csv_path, mode="a", header=write_header, index=False)

                # Small console summary: show one line per underlying ATM CE/PE
                summary = df.sort_values(["underlying", "expiry", "strike", "side"]).groupby("underlying").head(2)
                print(summary[["underlying", "expiry", "strike", "side", "ltp", "spot"]].to_string(index=False))

                print(f"  -> {len(df)} rows appended.")

            print(f"Sleeping for {interval_sec} seconds...\n")
            time.sleep(interval_sec)

    except KeyboardInterrupt:
        print("\nStopping Angel One index options live watch loop (Ctrl + C).")
        logger.info("Angel One index options live watch loop stopped by user.")


def load_latest_watch_snapshot():
    """
    Load the latest snapshot from the watch CSV file.
    Returns last 100 rows or None if file doesn't exist.
    """
    from pathlib import Path

    ROOT_DIR_PATH = Path(__file__).resolve().parents[2]
    csv_path = ROOT_DIR_PATH / "storage" / "live" / "angel_index_options_watch.csv"

    if not csv_path.exists():
        logger.warning(f"Watch CSV not found: {csv_path}")
        return None

    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            logger.warning("Watch CSV is empty")
            return None

        # Return last 100 rows (most recent data)
        return df.tail(100)
    except Exception as e:
        logger.error(f"Failed to load watch CSV: {e}")
        return None
