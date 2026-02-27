import os
import sys
from datetime import datetime, date

import pandas as pd

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.utils.logger import logger
from core.brokers.angel_one.broker import AngelOneBroker
from core.brokers.angel_one.instruments import (
    load_instruments,
    find_options_for_underlying,
    find_index_by_name,
)


def _parse_expiry(df: pd.DataFrame) -> pd.DataFrame:
    """Add an expiry_dt column (datetime) parsed from 'expiry' strings."""
    df = df.copy()
    if "expiry" not in df.columns:
        df["expiry_dt"] = pd.NaT
        return df

    def _parse(x: str):
        x = str(x).strip()
        if not x:
            return pd.NaT
        # Angel expiry format looks like: 30JUN2026
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
        # No valid expiry parsing; just return original
        return df

    today = date.today()
    valid = df.dropna(subset=["expiry_dt"])
    future = valid[valid["expiry_dt"] >= today]
    if not future.empty:
        target = future["expiry_dt"].min()
    else:
        # Fallback: earliest expiry in history
        target = valid["expiry_dt"].min()

    return valid[valid["expiry_dt"] == target].copy()


def _normalize_strike(raw: str) -> float | None:
    """Convert Angel strike string to a usable float (handles *100 scaling)."""
    try:
        v = float(raw)
    except Exception:
        return None

    # Many strikes come as 2300000.0 for 23000.0 etc.
    if v > 100000:  # heuristic
        v = v / 100.0

    return v


def _fetch_ltp_safe(broker: AngelOneBroker, exchange: str, symbol: str, token: str):
    """Wrapper around broker.get_ltp with error handling."""
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
    For one underlying (e.g. NIFTY) return a list of dicts with:
    market, underlying, spot, expiry, strike, side, symbol, token, ltp
    """
    # 1) Find index instrument row and get spot LTP
    idx_row = find_index_by_name(name, index_exchange)
    if not idx_row:
        logger.warning(f"[{name}] No index row found; skipping.")
        return []

    idx_symbol = idx_row["symbol"]
    idx_token = idx_row["token"]

    spot = _fetch_ltp_safe(broker, index_exchange, idx_symbol, idx_token)
    if spot is None:
        logger.warning(f"[{name}] Could not fetch index LTP; skipping.")
        return []

    # 2) Get all option contracts for this underlying
    df_opts = find_options_for_underlying(name, options_exchange)
    if df_opts is None or df_opts.empty:
        logger.warning(f"[{name}] No options found in instruments; skipping.")
        return []

    # 3) Restrict to current (nearest) expiry
    current = _select_nearest_expiry(df_opts)
    if current.empty:
        logger.warning(f"[{name}] No options with valid expiry; skipping.")
        return []

    # 4) Normalize strikes and compute distance from spot
    current = current.copy()
    current["strike_val"] = current["strike"].apply(_normalize_strike)
    current = current.dropna(subset=["strike_val"])

    current["dist"] = (current["strike_val"] - spot).abs()

    # 5) Split CE / PE using symbol suffix
    sym_series = current["symbol"].astype(str)
    ce_df = current[sym_series.str.endswith("CE")]
    pe_df = current[sym_series.str.endswith("PE")]

    # If for some reason CE/PE not separated, just use whole df
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


def main():
    logger.info("=== Angel One Index Options Watch ===")
    print("Initializing AngelOne broker...")
    broker = AngelOneBroker(allow_data_only=True)  # Data fetching doesn't require live trading permission
    print("Login OK.\n")

    # Underlying configuration
    underlyings = [
        {"name": "NIFTY", "index_exch": "NSE", "opt_exch": "NFO"},
        {"name": "BANKNIFTY", "index_exch": "NSE", "opt_exch": "NFO"},
        {"name": "FINNIFTY", "index_exch": "NSE", "opt_exch": "NFO"},
        {"name": "MIDCPNIFTY", "index_exch": "NSE", "opt_exch": "NFO"},
        {"name": "SENSEX", "index_exch": "BSE", "opt_exch": "BFO"},
    ]

    all_rows = []
    for cfg in underlyings:
        name = cfg["name"]
        print(f"Building watch list for {name} ({cfg['opt_exch']}) ...")
        rows = _build_watch_for_underlying(
            broker,
            name=name,
            index_exchange=cfg["index_exch"],
            options_exchange=cfg["opt_exch"],
            num_strikes_each_side=3,
        )
        if not rows:
            print(f"  -> No rows collected for {name} (check instruments / index name).")
        else:
            print(f"  -> {len(rows)} option legs collected for {name}.")
        all_rows.extend(rows)

    if not all_rows:
        print("\nNo option data collected. Check logs for details.")
        logger.warning("Angel One options watch produced no rows.")
        return

    # Convert to DataFrame for pretty printing
    df = pd.DataFrame(all_rows)
    # Sort by underlying, expiry, strike, side
    df = df.sort_values(by=["underlying", "expiry", "strike", "side"], ascending=[True, True, True, True])

    print("\n=== INDEX OPTIONS WATCH (Angel One) ===")
    cols = [
        "underlying",
        "expiry",
        "strike",
        "side",
        "ltp",
        "spot",
        "opt_exch",
        "symbol",
        "token",
    ]
    # Keep only columns that exist
    cols = [c for c in cols if c in df.columns]
    print(df[cols].to_string(index=False))

    print("\nAngel One index options watch completed.")
    logger.info("=== Angel One Index Options Watch Completed ===")


if __name__ == "__main__":
    main()
