"""
Weekly Expiry Selector - Prioritizes weekly expiries over monthly
"""
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Optional, Tuple
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.brokers.angel_one.instruments import load_instruments
from core.utils.logger import logger


def classify_expiry_type(expiry_date: date, all_expiries: list[date]) -> str:
    """
    Classify expiry as weekly or monthly based on position in sorted expiry list.
    
    CRITICAL FIX: Weekly vs monthly cannot be detected by weekday alone.
    Logic:
    - Weekly expiry = the earliest expiry date (nearest) for that underlying
    - Monthly expiry = the LAST expiry date in that month
    
    Args:
        expiry_date: Date object to classify
        all_expiries: List of all expiry dates for the underlying (sorted)
    
    Returns:
        'weekly' or 'monthly'
    """
    if not all_expiries:
        return 'weekly'  # Default
    
    sorted_expiries = sorted(set(all_expiries))
    
    # Weekly = nearest expiry (first in sorted list)
    if expiry_date == sorted_expiries[0]:
        return 'weekly'
    
    # Monthly = last expiry in the same month
    same_month_expiries = [e for e in sorted_expiries if e.year == expiry_date.year and e.month == expiry_date.month]
    if same_month_expiries and expiry_date == same_month_expiries[-1]:
        return 'monthly'
    
    # Default: if it's not the first, assume weekly (intermediate weekly)
    return 'weekly'


def is_weekly_expiry(expiry_date: date, all_expiries: list[date] = None) -> bool:
    """
    Determine if an expiry date is a weekly expiry.
    
    Args:
        expiry_date: Date object
        all_expiries: Optional list of all expiry dates for context
    
    Returns:
        bool: True if weekly expiry, False if monthly
    """
    if all_expiries:
        return classify_expiry_type(expiry_date, all_expiries) == 'weekly'
    
    # Fallback: if no context, assume weekly (safer default)
    return True


def select_expiry_for_underlying(
    underlying_name: str,
    exchange: str = "NFO",
    prefer_weekly: bool = True
) -> Tuple[Optional[date], Optional[str], str]:
    """
    Select expiry for underlying, prioritizing weekly if prefer_weekly=True.
    
    Args:
        underlying_name: Underlying name (e.g., 'NIFTY', 'BANKNIFTY')
        exchange: Exchange code ('NFO' or 'BFO')
        prefer_weekly: If True, prefer weekly expiry; if False, use nearest
    
    Returns:
        Tuple of (expiry_date, expiry_string, selection_reason)
        Returns (None, None, reason) if no expiry found
    """
    df = load_instruments()
    if df is None:
        return None, None, "Failed to load instruments"
    
    # Find options for underlying
    cols = {c.lower(): c for c in df.columns}
    ex_col = cols.get("exch_seg", "exch_seg")
    name_col = cols.get("name", "name")
    inst_col = cols.get("instrumenttype", "instrumenttype")
    expiry_col = cols.get("expiry", "expiry")
    
    # Filter for options
    mask = (
        (df[ex_col] == exchange) &
        (df[name_col] == underlying_name) &
        (df[inst_col].astype(str).str.contains("OPT", case=False, na=False))
    )
    
    df_opts = df[mask].copy()
    if df_opts.empty:
        return None, None, f"No options found for {underlying_name} on {exchange}"
    
    # Parse expiry dates
    def _parse_expiry(x):
        x = str(x).strip()
        if not x:
            return None
        for fmt in ("%d%b%Y", "%d%b%y", "%d-%b-%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(x, fmt).date()
            except:
                continue
        return None
    
    df_opts["expiry_dt"] = df_opts[expiry_col].apply(_parse_expiry)
    df_opts = df_opts[df_opts["expiry_dt"].notna()]
    
    if df_opts.empty:
        return None, None, "No valid expiry dates found"
    
    today = date.today()
    future_expiries = df_opts[df_opts["expiry_dt"] >= today]
    
    if future_expiries.empty:
        future_expiries = df_opts  # Use all if no future
    
    # CRITICAL FIX: Classify expiries correctly
    all_expiry_dates = future_expiries["expiry_dt"].dropna().unique().tolist()
    future_expiries = future_expiries.copy()
    future_expiries["expiry_type"] = future_expiries["expiry_dt"].apply(
        lambda x: classify_expiry_type(x, all_expiry_dates) if pd.notna(x) else 'weekly'
    )
    
    if prefer_weekly:
        # Primary: nearest expiry (which is always weekly by definition)
        nearest = future_expiries["expiry_dt"].min()
        nearest_expiry_type = future_expiries[future_expiries["expiry_dt"] == nearest]["expiry_type"].iloc[0]
        expiry_str = future_expiries[future_expiries["expiry_dt"] == nearest][expiry_col].iloc[0]
        
        logger.info(f"{underlying_name}: Selected {nearest} ({nearest_expiry_type}) - {str(expiry_str)}")
        return nearest, str(expiry_str), f"{nearest_expiry_type.capitalize()} expiry selected (nearest)"
    else:
        # Monthly mode: find last expiry of current month
        today = date.today()
        current_month_expiries = future_expiries[
            (future_expiries["expiry_dt"].dt.year == today.year) &
            (future_expiries["expiry_dt"].dt.month == today.month)
        ]
        
        if not current_month_expiries.empty:
            monthly_expiry = current_month_expiries["expiry_dt"].max()
            expiry_str = current_month_expiries[current_month_expiries["expiry_dt"] == monthly_expiry][expiry_col].iloc[0]
            logger.info(f"{underlying_name}: Selected monthly expiry {monthly_expiry} - {str(expiry_str)}")
            return monthly_expiry, str(expiry_str), "Monthly expiry selected"
        else:
            # Fallback to nearest
            nearest = future_expiries["expiry_dt"].min()
            expiry_str = future_expiries[future_expiries["expiry_dt"] == nearest][expiry_col].iloc[0]
            logger.info(f"{underlying_name}: Selected nearest expiry {nearest} - {str(expiry_str)}")
            return nearest, str(expiry_str), "Nearest expiry selected (monthly not available)"


def get_expiry_for_all_indices(
    indices: list,
    prefer_weekly: bool = True
) -> dict:
    """
    Get expiry for all indices.
    
    Args:
        indices: List of dicts with 'name' and 'exchange' keys
        prefer_weekly: Prefer weekly expiries
    
    Returns:
        dict mapping underlying_name -> (expiry_date, expiry_string, reason)
    """
    results = {}
    for idx in indices:
        name = idx.get("name")
        exchange = idx.get("exchange", "NFO")
        expiry_date, expiry_str, reason = select_expiry_for_underlying(
            name, exchange, prefer_weekly
        )
        results[name] = {
            "expiry_date": expiry_date,
            "expiry_string": expiry_str,
            "reason": reason,
            "is_weekly": is_weekly_expiry(expiry_date) if expiry_date else False
        }
        logger.info(f"{name} ({exchange}): {expiry_str} - {reason}")
    
    return results


class ExpirySelector:
    """
    Expiry Selector class - Wrapper for expiry selection functions.
    Provides the interface expected by option_chain_automation_master.
    """
    
    def __init__(self, broker=None):
        """
        Initialize ExpirySelector.
        
        Args:
            broker: Optional broker instance (not used but kept for compatibility)
        """
        self.broker = broker
    
    def get_nearest_weekly_expiry(self, underlying_name: str, exchange: str = "NFO") -> Optional[str]:
        """
        Get nearest weekly expiry string for underlying.
        
        Args:
            underlying_name: Underlying name (e.g., 'NIFTY')
            exchange: Exchange code ('NFO' or 'BFO')
        
        Returns:
            Expiry string (e.g., '08FEB2026') or None if not found
        """
        expiry_date, expiry_str, reason = select_expiry_for_underlying(
            underlying_name, exchange, prefer_weekly=True
        )
        if expiry_str:
            logger.info(f"ExpirySelector: {underlying_name} -> {expiry_str} ({reason})")
        return expiry_str
    
    def get_expiry_date(self, underlying_name: str, exchange: str = "NFO") -> Optional[date]:
        """
        Get nearest weekly expiry date for underlying.
        
        Args:
            underlying_name: Underlying name
            exchange: Exchange code
        
        Returns:
            Expiry date object or None
        """
        expiry_date, expiry_str, reason = select_expiry_for_underlying(
            underlying_name, exchange, prefer_weekly=True
        )
        return expiry_date